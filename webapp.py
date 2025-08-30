#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web UI backend (FastAPI) for Plex ⇄ SIMKL Watchlist Sync
"""

import json
import re
import secrets
import socket
import subprocess
import sys
import threading
import time
import os
import shutil
import urllib.request
import urllib.error
import urllib.parse
from _watchlist import build_watchlist, delete_watchlist_item

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Body, FastAPI, Request, Path as FPath, Query
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    StreamingResponse,
    PlainTextResponse,
    Response,
    FileResponse,
)

from _auth_helper import (
    plex_request_pin,
    plex_wait_for_token,
    simkl_build_authorize_url,
    simkl_exchange_code,
)
from _TMDB import get_poster_file, get_meta
from _FastAPI import get_index_html
from _secheduling import SyncScheduler  # your scheduler module

ROOT = Path(__file__).resolve().parent


# --- Favicon (SVG) ---
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<defs><linearGradient id="g" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#2de2ff"/><stop offset="0.5" stop-color="#7c5cff"/><stop offset="1" stop-color="#ff7ae0"/></linearGradient></defs>
<rect width="64" height="64" rx="14" fill="#0b0b0f"/>
<rect x="10" y="16" width="44" height="28" rx="6" fill="none" stroke="url(#g)" stroke-width="3"/>
<rect x="24" y="46" width="16" height="3" rx="1.5" fill="url(#g)"/>
<circle cx="20" cy="30" r="2.5" fill="url(#g)"/>
<circle cx="32" cy="26" r="2.5" fill="url(#g)"/>
<circle cx="44" cy="22" r="2.5" fill="url(#g)"/>
<path d="M20 30 L32 26 L44 22" fill="none" stroke="url(#g)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


# ---------- Paths (Docker-aware) ----------
# If running from /app (typical inside a container), store config, cache, and reports under /config.
CONFIG_BASE = Path("/config") if str(ROOT).startswith("/app") else ROOT
JSON_PATH   = CONFIG_BASE / "config.json"
CONFIG_PATH = JSON_PATH  # always JSON

REPORT_DIR = CONFIG_BASE / "sync_reports"; REPORT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = CONFIG_BASE / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
STATE_PATHS = [CONFIG_BASE / "state.json", ROOT / "state.json"]

# ---------- Globals ----------
SYNC_PROC_LOCK = threading.Lock()
RUNNING_PROCS: Dict[str, subprocess.Popen] = {}
MAX_LOG_LINES = 3000
LOG_BUFFERS: Dict[str, List[str]] = {"SYNC": [], "PLEX": [], "SIMKL": [], "TRBL": []}

SIMKL_STATE: Dict[str, Any] = {}

DEFAULT_CFG: Dict[str, Any] = {
    "plex": {"account_token": ""},
    "simkl": {
        "client_id": "YOUR_SIMKL_CLIENT_ID",
        "client_secret": "YOUR_SIMKL_CLIENT_SECRET",
        "access_token": "",
        "refresh_token": "",
        "token_expires_at": 0,
    },
    "tmdb": {"api_key": ""},
    "sync": {
        "enable_add": True,
        "enable_remove": True,
        "verify_after_write": True,
        "bidirectional": {"enabled": True, "mode": "two-way", "source_of_truth": "plex"},
    },
    "runtime": {"debug": False},
}

# ---------- Config read/write (JSON only) ----------
def _read_json(p: Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def _write_json(p: Path, data: Dict[str, Any]) -> None:
    tmp = p.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(p)

def load_config() -> Dict[str, Any]:
    if JSON_PATH.exists():
        try:
            return _read_json(JSON_PATH)
        except Exception:
            pass
    cfg = DEFAULT_CFG.copy()
    save_config(cfg)
    return cfg

def save_config(cfg: Dict[str, Any]) -> None:
    _write_json(JSON_PATH, cfg)

def _is_placeholder(val: str, placeholder: str) -> bool:
    return (val or "").strip().upper() == placeholder.upper()

# ---------- ANSI → HTML & logs ----------
ANSI_RE = re.compile(r"\x1b\[(\d{1,3})(?:;\d{1,3})*m")
ANSI_CLASS = {"90":"c90","91":"c91","92":"c92","93":"c93","94":"c94","95":"c95","96":"c96","97":"c97","0":"c0"}
ANSI_STRIP = re.compile(r"\x1b\[[0-9;]*m")
def _escape_html(s: str) -> str:
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def strip_ansi(s: str) -> str:
    return ANSI_STRIP.sub("", s)
def ansi_to_html(line: str) -> str:
    parts, open_span, pos = [], False, 0
    for m in ANSI_RE.finditer(line):
        if m.start() > pos: parts.append(_escape_html(line[pos:m.start()]))
        code = m.group(1)
        if open_span: parts.append("</span>"); open_span = False
        cls = ANSI_CLASS.get(code)
        if cls and cls != "c0": parts.append(f'<span class="{cls}">'); open_span = True
        pos = m.end()
    if pos < len(line): parts.append(_escape_html(line[pos:]))
    if open_span: parts.append("</span>")
    return "".join(parts)
def _append_log(tag: str, raw_line: str) -> None:
    html = ansi_to_html(raw_line.rstrip("\n"))
    buf = LOG_BUFFERS.setdefault(tag, [])
    buf.append(html)
    if len(buf) > MAX_LOG_LINES:
        LOG_BUFFERS[tag] = buf[-MAX_LOG_LINES:]

# ---------- Sync Summary ----------
SUMMARY_LOCK = threading.Lock()
SUMMARY: Dict[str, Any] = {}
def _summary_reset() -> None:
    with SUMMARY_LOCK:
        SUMMARY.clear()
        SUMMARY.update({
            "running": False,
            "started_at": None,
            "finished_at": None,
            "duration_sec": None,
            "cmd": "",
            "version": "",
            "plex_pre": None,
            "simkl_pre": None,
            "plex_post": None,  # Ensure Plex Post-sync is initialized
            "simkl_post": None,  # Ensure SIMKL Post-sync is initialized
            "result": "",
            "exit_code": None,
            "timeline": {"start": False, "pre": False, "post": False, "done": False},
            "raw_started_ts": None,
        })
def _summary_set(k: str, v: Any) -> None:
    with SUMMARY_LOCK:
        SUMMARY[k] = v

def _summary_set_timeline(flag: str, value: bool = True) -> None:
    with SUMMARY_LOCK:
        SUMMARY["timeline"][flag] = value

def _summary_snapshot() -> Dict[str, Any]:
    with SUMMARY_LOCK:
        # Return the summary with Post-sync counts included
        return dict(SUMMARY)
    
def _parse_sync_line(line: str) -> None:
    s = strip_ansi(line).strip()

    # Match sync start
    m = re.match(r"^> SYNC start:\s+(?P<cmd>.+)$", s)
    if m:
        if not SUMMARY.get("running"):
            _summary_set("running", True)
            SUMMARY["raw_started_ts"] = time.time()
            _summary_set("started_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        _summary_set("cmd", m.group("cmd"))
        _summary_set_timeline("start", True)
        return

    # Match version
    m = re.search(r"Version\s+(?P<ver>[0-9][0-9A-Za-z\.\-\+_]*)", s)
    if m:
        _summary_set("version", m.group("ver"))
        return

    # Match Pre-sync counts (if necessary)
    m = re.search(r"Pre-sync counts:\s+Plex=(?P<pp>\d+)\s+vs\s+SIMKL=(?P<sp>\d+)\s+\((?P<rel>[^)]+)\)", s)
    if m:
        _summary_set("plex_pre", int(m.group("pp")))
        _summary_set("simkl_pre", int(m.group("sp")))
        _summary_set_timeline("pre", True)
        return

    # Match Post-sync counts
    m = re.search(r"Post-sync:\s+Plex=(?P<pa>\d+)\s+vs\s+SIMKL=(?P<sa>\d+)\s*(?:→|->)\s*(?P<res>[A-Z]+)", s)
    if m:
        _summary_set("plex_post", int(m.group("pa")))  # Store Post-sync Plex count
        _summary_set("simkl_post", int(m.group("sa")))  # Store Post-sync SIMKL count
        _summary_set("result", m.group("res"))  # Store the result (EQUAL or others)
        _summary_set_timeline("post", True)
        return

    # Match exit code
    m = re.search(r"\[SYNC\]\s+exit code:\s+(?P<code>\d+)", s)
    if m:
        code = int(m.group("code"))
        _summary_set("exit_code", code)
        started = SUMMARY.get("raw_started_ts")
        if started:
            dur = max(0.0, time.time() - float(started))
            _summary_set("duration_sec", round(dur, 2))
        _summary_set("finished_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        _summary_set("running", False)
        _summary_set_timeline("done", True)

        # Save the summary to a file
        try:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            path = REPORT_DIR / f"sync-{ts}.json"
            with path.open("w", encoding="utf-8") as f:
                json.dump(_summary_snapshot(), f, indent=2)
        except Exception:
            pass

def _stream_proc(cmd: List[str], tag: str) -> None:
    try:
        if tag == "SYNC":
            _summary_reset(); _summary_set("running", True)
            SUMMARY["raw_started_ts"] = time.time(); _summary_set("started_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
            _summary_set_timeline("start", True)
        _append_log(tag, f"> {tag} start: {' '.join(cmd)}")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, cwd=str(ROOT))
        RUNNING_PROCS[tag] = proc
        assert proc.stdout is not None
        for line in proc.stdout:
            _append_log(tag, line)
            if tag == "SYNC": _parse_sync_line(line)
        rc = proc.wait(); _append_log(tag, f"[{tag}] exit code: {rc}")
        if tag == "SYNC" and _summary_snapshot().get("exit_code") is None:
            _summary_set("exit_code", rc)
            started = _summary_snapshot().get("raw_started_ts")
            if started:
                dur = max(0.0, time.time()-float(started)); _summary_set("duration_sec", round(dur,2))
            _summary_set("finished_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")); _summary_set("running", False); _summary_set_timeline("done", True)
            try:
                ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"); path = REPORT_DIR / f"sync-{ts}.json"
                with path.open("w", encoding="utf-8") as f: json.dump(_summary_snapshot(), f, indent=2)
            except Exception: pass
    except Exception as e:
        _append_log(tag, f"[{tag}] ERROR: {e}")
    finally:
        RUNNING_PROCS.pop(tag, None)

def start_proc_detached(cmd: List[str], tag: str) -> None:
    threading.Thread(target=_stream_proc, args=(cmd, tag), daemon=True).start()

# Add refresh_wall() function here
def _load_hide_set() -> set:
    # Stub: return an empty set, or implement loading from file if needed
    return set()

def refresh_wall():
    # Reload the state and hidden items list
    state = _load_state()
    hidden_set = _load_hide_set()

    # Re-render the posters, marking those in the hidden set as 'deleted'
    posters = _wall_items_from_state()
    return posters  # Return the posters list directly or implement rendering logic here

# ---------- Misc helpers ----------
def get_primary_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80)); return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

# ---------- state.json helpers ----------
def _find_state_path() -> Optional[Path]:
    for p in STATE_PATHS:
        if p.exists(): return p
    return None

def _load_state() -> Dict[str, Any]:
    sp = _find_state_path()
    if not sp: return {}
    try:
        return json.loads(sp.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _parse_epoch(v: Any) -> int:
    """Accept integer seconds, float, or ISO 8601 strings (returns epoch seconds)."""
    if v is None: return 0
    try:
        if isinstance(v, (int, float)): return int(v)
        s = str(v).strip()
        if s.isdigit(): return int(s)
        s = s.replace("Z","+00:00")
        try:
            dt = datetime.fromisoformat(s)
            return int(dt.timestamp())
        except Exception:
            return 0
    except Exception:
        return 0

def _pick_added(d: Dict[str, Any]) -> Optional[str]:
    """Find a plausible 'added at' timestamp in various shapes and normalize to UTC Z."""
    if not isinstance(d, dict):
        return None
    for k in ("added", "added_at", "addedAt", "date_added", "created_at", "createdAt"):
        v = d.get(k)
        if v:
            try:
                if isinstance(v, (int, float)):
                    return datetime.fromtimestamp(int(v), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                return str(v)
            except Exception:
                return str(v)
    dates = d.get("dates") or d.get("meta") or d.get("attributes") or {}
    if isinstance(dates, dict):
        for k in ("added", "added_at", "created", "created_at"):
            v = dates.get(k)
            if v:
                try:
                    if isinstance(v, (int, float)):
                        return datetime.fromtimestamp(int(v), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    return str(v)
                except Exception:
                    return str(v)
    return None

def _tmdb_genres(api_key: str, typ: str, tmdb_id: int, ttl_days: int = 14) -> List[str]:
    """Fetch & cache TMDb genres for movie/tv. Safe fallback to []."""
    try:
        meta_dir = CACHE_DIR / "tmdb_meta"
        meta_dir.mkdir(parents=True, exist_ok=True)
        fpath = meta_dir / f"{typ}-{tmdb_id}.json"

        fresh = False
        if fpath.exists():
            age = time.time() - fpath.stat().st_mtime
            if age < ttl_days * 86400:
                fresh = True

        data = None
        if fresh:
            try:
                data = json.loads(fpath.read_text(encoding="utf-8"))
            except Exception:
                data = None

        if data is None:
            url = f"https://api.themoviedb.org/3/{'tv' if typ=='tv' else 'movie'}/{tmdb_id}?api_key={api_key}&language=en-US"
            with urllib.request.urlopen(url, timeout=8) as resp:
                raw = resp.read()
            fpath.write_bytes(raw)
            data = json.loads(raw.decode("utf-8", errors="ignore"))

        genres = []
        for g in (data.get("genres") or []):
            name = g.get("name")
            if isinstance(name, str) and name.strip():
                genres.append(name.strip())
        return genres[:8]
    except Exception:
        return []

def _wall_items_from_state() -> List[Dict[str, Any]]:
    """Build watchlist preview items from state.json, newest-first."""
    st = _load_state()
    plex_items = (st.get("plex", {}) or {}).get("items", {}) or {}
    simkl_items = (st.get("simkl", {}) or {}).get("items", {}) or {}

    cfg = load_config()
    api_key = (cfg.get("tmdb", {}) or {}).get("api_key") or ""

    out: List[Dict[str, Any]] = []
    all_keys = set(plex_items.keys()) | set(simkl_items.keys())

    def iso_to_epoch(iso: Optional[str]) -> int:
        if iso is None: return 0
        try:
            s = str(iso).strip()
            if s.isdigit(): return int(s)
            s = s.replace("Z", "+00:00")
            return int(datetime.fromisoformat(s).timestamp())
        except Exception:
            return 0

    for key in all_keys:
        p = plex_items.get(key) or {}
        s = simkl_items.get(key) or {}
        info = p or s
        if not info:
            continue

        typ_raw = (info.get("type") or "").lower()
        typ = "tv" if typ_raw in ("tv", "show") else "movie"

        title = info.get("title") or info.get("name") or ""
        year = info.get("year") or info.get("release_year")
        tmdb_id = (info.get("ids", {}) or {}).get("tmdb") or info.get("tmdb")

        p_when = _pick_added(p)
        s_when = _pick_added(s)
        p_ep = iso_to_epoch(p_when)
        s_ep = iso_to_epoch(s_when)

        if p_ep >= s_ep:
            added_when = p_when
            added_epoch = p_ep
            added_src = "plex" if p else ("simkl" if s else "")
        else:
            added_when = s_when
            added_epoch = s_ep
            added_src = "simkl" if s else ("plex" if p else "")

        status = "both" if key in plex_items and key in simkl_items else ("plex_only" if key in plex_items else "simkl_only")

        categories: List[str] = []
        if api_key and tmdb_id:
            try:
                categories = _tmdb_genres(api_key, typ, int(tmdb_id))
            except Exception:
                categories = []

        out.append({
            "key": key,
            "type": typ,
            "title": title,
            "year": year,
            "tmdb": tmdb_id,
            "status": status,
            "added_epoch": added_epoch,
            "added_when": added_when,
            "added_src": added_src,
            "categories": categories,
        })

    out.sort(key=lambda x: (x.get("added_epoch") or 0, x.get("year") or 0), reverse=True)
    return out

# ---------- Probes (cached) ----------
_PROBE_CACHE: Dict[str, Tuple[float, bool]] = {"plex": (0.0, False), "simkl": (0.0, False)}
def _http_get(url: str, headers: Dict[str, str], timeout: int = 8) -> Tuple[int, bytes]:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() if e.fp else b""
    except Exception:
        return 0, b""

def probe_plex(cfg: Dict[str, Any], max_age_sec: int = 30) -> bool:
    ts, ok = _PROBE_CACHE["plex"]
    now = time.time()
    if now - ts < max_age_sec:
        return ok
    token = (cfg.get("plex", {}) or {}).get("account_token") or ""
    if not token:
        _PROBE_CACHE["plex"] = (now, False); return False
    headers = {
        "X-Plex-Token": token,
        "X-Plex-Client-Identifier": "plex-simkl-sync-webui",
        "X-Plex-Product": "PlexSimklSync",
        "X-Plex-Version": "1.0",
        "Accept": "application/xml",
        "User-Agent": "Mozilla/5.0",
    }
    code, _ = _http_get("https://plex.tv/users/account", headers=headers, timeout=8)
    ok = (code == 200)
    _PROBE_CACHE["plex"] = (now, ok)
    return ok

def probe_simkl(cfg: Dict[str, Any], max_age_sec: int = 30) -> bool:
    ts, ok = _PROBE_CACHE["simkl"]
    now = time.time()
    if now - ts < max_age_sec:
        return ok
    simkl = cfg.get("simkl", {}) or {}
    cid = (simkl.get("client_id") or "").strip()
    tok = (simkl.get("access_token") or "").strip()
    if not cid or not tok:
        _PROBE_CACHE["simkl"] = (now, False); return False
    headers = {
        "Authorization": f"Bearer {tok}",
        "simkl-api-key": cid,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    }
    code, _ = _http_get("https://api.simkl.com/users/settings", headers=headers, timeout=8)
    ok = (code == 200)
    _PROBE_CACHE["simkl"] = (now, ok)
    return ok

def connected_status(cfg: Dict[str, Any]) -> Tuple[bool, bool, bool]:
    plex_ok = probe_plex(cfg)
    simkl_ok = probe_simkl(cfg)
    debug = bool(cfg.get("runtime", {}).get("debug"))
    return plex_ok, simkl_ok, debug

# ---------- FastAPI ----------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        scheduler.ensure_defaults()
        sch = (load_config().get("scheduling") or {})
        if sch.get("enabled"):
            scheduler.start()
    except Exception:
        pass
    try:
        yield
    finally:
        try:
            scheduler.stop()
        except Exception:
            pass

app = FastAPI(lifespan=lifespan)

# --- Watchlist API (grid page) ---
@app.get("/api/watchlist")
def api_watchlist() -> JSONResponse:
    cfg = load_config()
    st = _load_state()
    api_key = (cfg.get("tmdb", {}) or {}).get("api_key") or ""

    # If no state at all: return ok:false but HTTP 200 (frontend expects JSON, not 404)
    if not st:
        return JSONResponse(
            {"ok": False, "error": "No state.json found or empty.", "missing_tmdb_key": not bool(api_key)},
            status_code=200,
        )
    try:
        items = build_watchlist(st, tmdb_api_key_present=bool(api_key))
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e), "missing_tmdb_key": not bool(api_key)}, status_code=200)

    if not items:
        return JSONResponse(
            {"ok": False, "error": "No state data found.", "missing_tmdb_key": not bool(api_key)},
            status_code=200,
        )

    return JSONResponse(
        {
            "ok": True,
            "items": items,
            "missing_tmdb_key": not bool(api_key),
            "last_sync_epoch": st.get("last_sync_epoch"),
        },
        status_code=200,
    )


@app.delete("/api/watchlist/{key}")
def api_watchlist_delete(key: str = FPath(...)) -> JSONResponse:
    sp = _find_state_path() or (CONFIG_BASE / "state.json")
    # key may arrive URL-encoded from the browser
    try:
        if "%" in (key or ""):
            key = urllib.parse.unquote(key)

        result = delete_watchlist_item(
            key=key,
            state_path=sp,
            cfg=load_config(),
            log=_append_log,  # optional logger
        )
        # Always return JSON, never 404
        if not isinstance(result, dict) or "ok" not in result:
            result = {"ok": False, "error": "unexpected server response"}

        status = 200 if result.get("ok") else 400
        return JSONResponse(result, status_code=status)
    except Exception as e:
        _append_log("TRBL", f"[WATCHLIST] ERROR: {e}")
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/favicon.svg", include_in_schema=False)
def favicon_svg():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")

@app.get("/favicon.ico", include_in_schema=False)
def favicon_ico():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")

# -------- Scheduler wiring --------
def _is_sync_running() -> bool:
    p = RUNNING_PROCS.get("SYNC")
    try:
        return p is not None and (p.poll() is None)
    except Exception:
        return False

def _start_sync_from_scheduler() -> bool:
    if _is_sync_running():
        return False
    sync_script = ROOT / "plex_simkl_watchlist_sync.py"
    if not sync_script.exists():
        return False
    cmd = [sys.executable, str(sync_script), "--sync"]
    start_proc_detached(cmd, tag="SYNC")
    return True

# Instantiate scheduler
scheduler = SyncScheduler(load_config, save_config, run_sync_fn=_start_sync_from_scheduler, is_sync_running_fn=_is_sync_running)

INDEX_HTML = get_index_html()

@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)

@app.get("/api/status")
def api_status() -> Dict[str, Any]:
    cfg = load_config()
    plex_ok, simkl_ok, debug = connected_status(cfg)
    can_run = plex_ok and simkl_ok
    return {"plex_connected": plex_ok, "simkl_connected": simkl_ok, "can_run": can_run, "debug": debug}

@app.get("/api/config")
def api_config() -> JSONResponse:
    return JSONResponse(load_config())

@app.post("/api/config")
def api_config_save(cfg: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    save_config(cfg)
    _PROBE_CACHE["plex"] = (0.0, False)
    _PROBE_CACHE["simkl"] = (0.0, False)
    return {"ok": True}

# ---- PLEX auth ----
@app.post("/api/plex/pin/new")
def api_plex_pin_new() -> Dict[str, Any]:
    try:
        info = plex_request_pin()
        pin_id = info["id"]; code = info["code"]; exp_epoch = int(info["expires_epoch"]); headers = info["headers"]
        def waiter(_pin_id: int, _headers: Dict[str, str]):
            token = plex_wait_for_token(_pin_id, headers=_headers, timeout_sec=360, interval=1.0)
            if token:
                cfg = load_config(); cfg.setdefault("plex", {})["account_token"] = token; save_config(cfg)
                _append_log("PLEX", "\x1b[92m[PLEX]\x1b[0m Token acquired and saved.")
                _PROBE_CACHE["plex"] = (0.0, False)
            else:
                _append_log("PLEX", "\x1b[91m[PLEX]\x1b[0m PIN expired or not authorized.")
        threading.Thread(target=waiter, args=(pin_id, headers), daemon=True).start()
        expires_in = max(0, exp_epoch - int(time.time()))
        return {"ok": True, "code": code, "pin_id": pin_id, "expiresIn": expires_in}
    except Exception as e:
        _append_log("PLEX", f"[PLEX] ERROR: {e}")
        return {"ok": False, "error": str(e)}

# ---- SIMKL OAuth ----
@app.post("/api/simkl/authorize")
def api_simkl_authorize(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    try:
        origin = (payload or {}).get("origin") or ""
        if not origin:
            return {"ok": False, "error": "origin missing"}
        cfg = load_config(); simkl = cfg.get("simkl", {}) or {}
        client_id = (simkl.get("client_id") or "").strip(); client_secret = (simkl.get("client_secret") or "").strip()
        bad_cid = (not client_id) or _is_placeholder(client_id, "YOUR_SIMKL_CLIENT_ID")
        bad_sec = (not client_secret) or _is_placeholder(client_secret, "YOUR_SIMKL_CLIENT_SECRET")
        if bad_cid or bad_sec:
            return {"ok": False, "error": "SIMKL client_id and client_secret must be set in settings first"}
        state = secrets.token_urlsafe(24); redirect_uri = f"{origin}/callback"
        SIMKL_STATE["state"] = state; SIMKL_STATE["redirect_uri"] = redirect_uri
        url = simkl_build_authorize_url(client_id, redirect_uri, state)
        return {"ok": True, "authorize_url": url}
    except Exception as e:
        _append_log("SIMKL", f"[SIMKL] ERROR: {e}")
        return {"ok": False, "error": str(e)}

@app.get("/callback")
def oauth_simkl_callback(request: Request) -> PlainTextResponse:
    try:
        params = dict(request.query_params); code = params.get("code"); state = params.get("state")
        if not code or not state: return PlainTextResponse("Missing code or state.", status_code=400)
        if state != SIMKL_STATE.get("state"): return PlainTextResponse("State mismatch.", status_code=400)
        redirect_uri = str(SIMKL_STATE.get("redirect_uri") or f"{request.base_url}callback")
        cfg = load_config(); simkl_cfg = cfg.setdefault("simkl", {})
        client_id = (simkl_cfg.get("client_id") or "").strip(); client_secret = (simkl_cfg.get("client_secret") or "").strip()
        bad_cid = (not client_id) or _is_placeholder(client_id, "YOUR_SIMKL_CLIENT_ID")
        bad_sec = (not client_secret) or _is_placeholder(client_secret, "YOUR_SIMKL_CLIENT_SECRET")
        if bad_cid or bad_sec: return PlainTextResponse("SIMKL client_id/secret missing or placeholders in config.", status_code=400)
        tokens = simkl_exchange_code(client_id, client_secret, code, redirect_uri)
        if not tokens or "access_token" not in tokens: return PlainTextResponse("SIMKL token exchange failed.", status_code=400)
        simkl_cfg["access_token"] = tokens["access_token"]
        if tokens.get("refresh_token"): simkl_cfg["refresh_token"] = tokens["refresh_token"]
        if tokens.get("expires_in"): simkl_cfg["token_expires_at"] = int(time.time()) + int(tokens["expires_in"])
        save_config(cfg); _append_log("SIMKL", "\x1b[92m[SIMKL]\x1b[0m Access token saved.")
        _PROBE_CACHE["simkl"] = (0.0, False)
        return PlainTextResponse("SIMKL authorized. You can close this tab and return to the app.", status_code=200)
    except Exception as e:
        _append_log("SIMKL", f"[SIMKL] ERROR: {e}")
        return PlainTextResponse(f"Error: {e}", status_code=500)

# ---- Run & Summary ----
@app.post("/api/run")
def api_run_sync() -> Dict[str, Any]:
    sync_script = ROOT / "plex_simkl_watchlist_sync.py"
    if not sync_script.exists():
        return {"ok": False, "error": "plex_simkl_watchlist_sync.py not found"}

    with SYNC_PROC_LOCK:
        if "SYNC" in RUNNING_PROCS and RUNNING_PROCS["SYNC"].poll() is None:
            return {"ok": False, "error": "Sync already running"}
        
        # Start the sync process
        cmd = [sys.executable, str(sync_script), "--sync"]
        start_proc_detached(cmd, tag="SYNC")
        
        # Notify frontend to refresh the Watchlist Preview
        # This could be done by setting a flag or calling a function to refresh the UI.
        refresh_watchlist_preview()  # This is where you can trigger the refresh

        return {"ok": True}

def refresh_watchlist_preview():
    # Trigger a refresh of the Watchlist Preview on the frontend
    # This could send a response to the frontend, or you can call a JavaScript function via SSE/WebSocket
    # Example: Notify frontend to reload the watchlist grid
    print("Triggering refresh of the watchlist preview")


@app.get("/api/run/summary")
def api_run_summary() -> JSONResponse:
    return JSONResponse(_summary_snapshot())

@app.get("/api/run/summary/file")
def api_run_summary_file() -> Response:
    js = json.dumps(_summary_snapshot(), indent=2)
    return Response(content=js, media_type="application/json", headers={"Content-Disposition": 'attachment; filename="last_sync.json"'})

@app.get("/api/run/summary/stream")
def api_run_summary_stream() -> StreamingResponse:
    def gen():
        last_key = None
        while True:
            time.sleep(0.25)
            snap = _summary_snapshot()
            key = (snap.get("running"), snap.get("exit_code"), snap.get("plex_post"), snap.get("simkl_post"),
                   snap.get("result"), snap.get("duration_sec"), (snap.get("timeline", {}) or {}).get("done"))
            if key != last_key:
                last_key = key
                yield f"data: {json.dumps(snap, separators=(',',':'))}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")

# ---- Logs SSE ----
@app.get("/api/logs/stream")
def api_logs_stream(tag: str) -> StreamingResponse:
    tag = (tag or "").upper()
    if tag not in LOG_BUFFERS:
        def empty():
            while True:
                time.sleep(1); yield "data: \n\n"
        return StreamingResponse(empty(), media_type="text/event-stream")
    def event_gen():
        for line in LOG_BUFFERS.get(tag, []): yield f"data: {line}\n\n"
        last_len = len(LOG_BUFFERS.get(tag, []))
        while True:
            time.sleep(0.25)
            buf = LOG_BUFFERS.get(tag, [])
            if len(buf) > last_len:
                for line in buf[last_len:]: yield f"data: {line}\n\n"
                last_len = len(buf)
    return StreamingResponse(event_gen(), media_type="text/event-stream")

# ---- TMDb & wall ----
@app.get("/api/state/wall")
def api_state_wall() -> Dict[str, Any]:
    cfg = load_config()
    api_key = (cfg.get("tmdb", {}) or {}).get("api_key") or ""
    st = _load_state()
    items = _wall_items_from_state()
    if not items:
        return {"ok": False, "error": "No state.json found or empty.", "missing_tmdb_key": not bool(api_key)}
    return {
        "ok": True,
        "items": items,
        "missing_tmdb_key": not bool(api_key),
        "last_sync_epoch": st.get("last_sync_epoch"),
    }

@app.get("/art/tmdb/{typ}/{tmdb_id}")
def api_tmdb_art(typ: str = FPath(...), tmdb_id: int = FPath(...), size: str = Query("w342")):
    typ = typ.lower()
    if typ == "show": typ = "tv"
    if typ not in {"movie", "tv"}:
        return PlainTextResponse("Bad type", status_code=400)
    cfg = load_config(); api_key = (cfg.get("tmdb", {}) or {}).get("api_key") or ""
    if not api_key:
        return PlainTextResponse("TMDb key missing", status_code=404)
    try:
        local_path, mime = get_poster_file(api_key, typ, tmdb_id, size, CACHE_DIR)
        return FileResponse(path=str(local_path), media_type=mime)
    except Exception as e:
        return PlainTextResponse(f"Poster not available: {e}", status_code=404)

@app.get("/api/tmdb/meta/{typ}/{tmdb_id}")
def api_tmdb_meta(typ: str = FPath(...), tmdb_id: int = FPath(...)) -> Dict[str, Any]:
    typ = typ.lower()
    if typ == "show": typ = "tv"
    cfg = load_config(); api_key = (cfg.get("tmdb", {}) or {}).get("api_key") or ""
    if not api_key:
        return {"ok": False, "error": "TMDb key missing"}
    try:
        meta = get_meta(api_key, typ, tmdb_id, CACHE_DIR)
        return {"ok": True, **meta}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# --- Scheduling API ---
@app.get("/api/scheduling")
def api_sched_get():
    cfg = load_config()
    return (cfg.get("scheduling") or {})

@app.post("/api/scheduling")
def api_sched_post(payload: dict = Body(...)):
    cfg = load_config()
    cfg["scheduling"] = (payload or {})
    save_config(cfg)
    if (cfg["scheduling"] or {}).get("enabled"):
        scheduler.start(); scheduler.refresh()
    else:
        scheduler.stop()
    st = scheduler.status()
    return {"ok": True, "next_run_at": st.get("next_run_at", 0)}

@app.get("/api/scheduling/status")
def api_sched_status():
    return scheduler.status()

# --- Troubleshoot API ---
def _safe_remove_path(p: Path) -> bool:
    try:
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        elif p.exists():
            p.unlink(missing_ok=True)
        return True
    except Exception:
        return False

@app.post("/api/troubleshoot/clear-cache")
def api_trbl_clear_cache() -> Dict[str, Any]:
    """Delete contents of CACHE_DIR but keep the directory."""
    deleted_files = 0
    deleted_dirs = 0
    if CACHE_DIR.exists():
        for entry in CACHE_DIR.iterdir():
            try:
                if entry.is_dir():
                    shutil.rmtree(entry, ignore_errors=True)
                    deleted_dirs += 1
                else:
                    entry.unlink(missing_ok=True)
                    deleted_files += 1
            except Exception:
                pass
    _append_log("TRBL", "\x1b[91m[TROUBLESHOOT]\x1b[0m Cleared cache folder.")
    return {"ok": True, "deleted_files": deleted_files, "deleted_dirs": deleted_dirs}

@app.post("/api/troubleshoot/reset-state")
def api_trbl_reset_state() -> Dict[str, Any]:
    """Ask the sync script to rebuild state.json asynchronously (logged under TRBL)."""
    sync_script = ROOT / "plex_simkl_watchlist_sync.py"
    if not sync_script.exists():
        return {"ok": False, "error": "plex_simkl_watchlist_sync.py not found"}
    cmd = [sys.executable, str(sync_script), "--reset-state"]
    start_proc_detached(cmd, tag="TRBL")
    return {"ok": True, "started": True}

# ---- Main ----
def main(host: str = "0.0.0.0", port: int = 8787) -> None:
    ip = get_primary_ip()
    print("\nPlex ⇄ SIMKL Web UI running:")
    print(f"  Local:   http://127.0.0.1:{port}")
    print(f"  Docker:  http://{ip}:{port}")
    print(f"  Bind:    {host}:{port}")
    print(f"  Config:  {CONFIG_PATH} (JSON)")
    print(f"  Cache:   {CACHE_DIR}")
    print(f"  Reports: {REPORT_DIR}\n")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
