#!/usr/bin/env python3
"""
Plex ⇄ SIMKL Watchlist Sync (v0.1)
==================================

Keep your Plex Watchlist and SIMKL “Plan to Watch” list in sync. This tool
adds and removes items so both services stay aligned.

How it works
------------
- Plex-first writes: All add/remove operations on Plex use `plexapi`.
- Read fallback (fetch only): If reading the Plex watchlist via `plexapi`
  fails due to upstream changes, the script temporarily reads it via Plex
  Discover HTTP. Writes still use `plexapi` only.

Sync modes
----------
- Mirror: Makes one side exactly match the other (adds + deletions) based on a
  chosen source of truth.
- Two-way:
  • First run: creates a local snapshot (`state.json`) and performs *adds only*
    (no deletions) to avoid accidental data loss.
  • Subsequent runs: compares current lists to the snapshot and propagates both
    *adds and deletions* in both directions.

SIMKL sign-in (OAuth)
---------------------
Run:
  --init-simkl redirect --bind <HOST>:8787 [--open]

Notes:
- `<HOST>` must be an address/hostname reachable by your browser (e.g., the
  server or container IP), **not** `0.0.0.0`.
- Add the exact callback URL `http://<HOST>:8787/callback` to your SIMKL app’s
  Redirect URIs.
- The command starts a tiny local web server to receive the SIMKL OAuth
  redirect. Open the printed authorization link and the script will store
  tokens in `config.json`.

Requirements
------------
- Python 3.8+.
- `requests` and `plexapi` installed in the same Python environment. Requires the latest plexapi
- A `config.json` next to the script (a starter file is created on first run).
"""

import argparse
import json
import re
import time
import requests
import sys
import urllib.parse
import webbrowser
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Tuple, List, Dict, Set, Optional

__VERSION__ = "0.1"

# Paths / constants
HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"
STATE_PATH  = HERE / "state.json"

UA = f"Plex-SIMKL-Watchlist-Sync/plexapi-first/{__VERSION__} (+https://simkl.com)"

ANSI_G = "\033[92m"
ANSI_R = "\033[91m"
ANSI_X = "\033[0m"

DISCOVER_HOST = "https://discover.provider.plex.tv"
PLEX_WATCHLIST_PATH = "/library/sections/watchlist/all"
PLEX_METADATA_PATH = "/library/metadata"

# Default config scaffold (Python dict comments are fine; JSON file has no comments)
DEFAULT_CONFIG = {
    "plex": {
        "account_token": ""
    },
    "simkl": {
        "client_id": "",
        "client_secret": "",
        "access_token": "",
        "refresh_token": "",
        "token_expires_at": 0
    },
    "sync": {
        "enable_add": True,
        "enable_remove": True,
        "verify_after_write": True,
        "bidirectional": {
            "enabled": True,
            "mode": "two-way",          # "two-way" (union) or "mirror"
            "source_of_truth": "plex"   # used only when mode="mirror": "simkl" or "plex"
        }
    },
    "runtime": {
        "debug": False
    }
}

# --------------------------- Config I/O --------------------------------------
def _read_text(p: Path) -> str:
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def _write_text(p: Path, s: str):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)

def load_config_file(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"[!] Missing config.json at {path}.")
    try:
        cfg = json.loads(_read_text(path))
    except Exception as e:
        sys.exit(f"[!] Could not parse {path} as JSON: {e}")
    # ensure essential sections exist
    for k, v in DEFAULT_CONFIG.items():
        if k not in cfg or not isinstance(cfg[k], dict):
            cfg[k] = v if isinstance(v, dict) else cfg.get(k, v)
    return cfg

def dump_config_file(path: Path, cfg: dict):
    _write_text(path, json.dumps(cfg, indent=2))

def ensure_config_exists(path: Path) -> bool:
    if path.exists():
        return False
    dump_config_file(path, DEFAULT_CONFIG)
    return True

# --------------------------- State I/O ---------------------------------------
def load_state(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(_read_text(path))
    except Exception:
        return None

def save_state(path: Path, data: dict):
    data = dict(data)
    data["version"] = 1
    data["last_sync_epoch"] = int(time.time())
    _write_text(path, json.dumps(data, indent=2))

def clear_state(path: Path):
    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass

# --------------------------- Banner -----------------------------------------
def print_banner():
    print(f"\nPlex ⇄ SIMKL Watchlist Sync Version {__VERSION__}")
    print("=======================================\n")

# --------------------------- SIMKL API --------------------------------------
SIMKL_BASE = "https://api.simkl.com"
SIMKL_OAUTH_TOKEN = f"{SIMKL_BASE}/oauth/token"
SIMKL_ALL_ITEMS = f"{SIMKL_BASE}/sync/all-items"
SIMKL_ADD_TO_LIST = f"{SIMKL_BASE}/sync/add-to-list"
SIMKL_HISTORY_REMOVE = f"{SIMKL_BASE}/sync/history/remove"
SIMKL_AUTH_URL = "https://simkl.com/oauth/authorize"

def simkl_headers(simkl_cfg: dict) -> dict:
    return {
        "User-Agent": UA,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {simkl_cfg.get('access_token','')}",
        "simkl-api-key": simkl_cfg.get("client_id",""),
    }

def token_expired(simkl_cfg: dict) -> bool:
    try:
        exp = float(simkl_cfg.get("token_expires_at", 0.0))
    except Exception:
        exp = 0.0
    return time.time() >= (exp - 60)

def simkl_refresh(cfg: dict, cfg_path: Path, debug: bool=False):
    s = cfg.get("simkl") or {}
    if not s.get("refresh_token"):
        if debug:
            print("[debug] No refresh_token; using current access_token as-is.")
        return cfg
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": s["refresh_token"],
        "client_id": s.get("client_id",""),
        "client_secret": s.get("client_secret",""),
    }
    r = requests.post(SIMKL_OAUTH_TOKEN, json=payload, headers={"User-Agent": UA}, timeout=30)
    if not r.ok:
        raise SystemExit(f"[!] SIMKL refresh failed: HTTP {r.status_code} {r.text}")
    tok = r.json()
    s["access_token"] = tok["access_token"]
    s["refresh_token"] = tok.get("refresh_token", s.get("refresh_token",""))
    s["token_expires_at"] = time.time() + int(tok.get("expires_in", 3600))
    cfg["simkl"] = s
    dump_config_file(cfg_path, cfg)
    if debug:
        print(f"[debug] SIMKL token refreshed and saved to {cfg_path}")
    return cfg

def _cb() -> str:
    return str(int(time.time() * 1000))

def _http_get_json(url: str, headers: dict, debug: bool=False):
    u = f"{url}?_cb={_cb()}"
    if debug:
        print(f"[debug] SIMKL GET: {u}")
    r = requests.get(u, headers=headers, timeout=45)
    if not r.ok:
        raise SystemExit(f"[!] SIMKL GET {u} failed: HTTP {r.status_code} {r.text}")
    try:
        return r.json()
    except Exception:
        return None

def simkl_get_ptw(simkl_cfg: dict, debug: bool=False) -> Tuple[List[dict], List[dict]]:
    hdrs = simkl_headers(simkl_cfg)
    shows_js = _http_get_json(f"{SIMKL_ALL_ITEMS}/shows/plantowatch", hdrs, debug)
    shows_items = (shows_js or {}).get("shows", []) if isinstance(shows_js, dict) else []
    movies_js = _http_get_json(f"{SIMKL_ALL_ITEMS}/movies/plantowatch", hdrs, debug)
    movies_items = (movies_js or {}).get("movies", []) if isinstance(movies_js, dict) else []
    return shows_items, movies_items

def ids_from_simkl_item(it: dict) -> dict:
    node = None
    for k in ("movie", "show", "anime", "ids"):
        if isinstance(it.get(k), dict):
            node = it[k]
            break
    if node is None:
        return {}
    ids_block = node.get("ids", node) if "ids" in node or node is it else node
    ids = {}
    for k in ("simkl", "imdb", "tmdb", "tvdb", "slug"):
        v = ids_block.get(k)
        if v is not None:
            ids[k] = v
    if "title" in node:
        ids["title"] = node.get("title")
    if "year" in node:
        try:
            ids["year"] = int(node.get("year"))
        except Exception:
            ids["year"] = node.get("year")
    for k in ("tmdb", "tvdb", "year"):
        if k in ids and ids[k] is not None:
            try:
                ids[k] = int(ids[k])
            except Exception:
                pass
    return ids

def combine_ids(ids: dict) -> dict:
    out = {}
    for k in ("imdb", "tmdb", "tvdb", "slug", "title", "year"):
        if k in ids and ids[k] is not None:
            out[k] = ids[k]
    return out

def idset_from_ids(ids: dict) -> Set[Tuple[str, str]]:
    out: Set[Tuple[str, str]] = set()
    for k in ("imdb", "tmdb", "tvdb", "slug"):
        if k in ids and ids[k] is not None:
            out.add((k, str(ids[k])))
    return out

def canonical_identity(ids: dict) -> Optional[Tuple[str, str]]:
    for k in ("imdb", "tmdb", "tvdb", "slug"):
        v = ids.get(k)
        if v is not None:
            return (k, str(v))
    return None

def identity_key(pair: Tuple[str, str]) -> str:
    return f"{pair[0]}:{pair[1]}"

# --------------------------- SIMKL OAuth helper ------------------------------
def detect_local_ip(fallback: str="localhost") -> str:
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    return fallback

def build_simkl_authorize_url(client_id: str, redirect_uri: str, state: str = "", scope: str | None = None) -> str:
    params = {"response_type": "code", "client_id": client_id, "redirect_uri": redirect_uri}
    if state:
        params["state"] = state
    if scope:
        params["scope"] = scope
    return f"{SIMKL_AUTH_URL}?{urllib.parse.urlencode(params)}"

def simkl_exchange_code_for_tokens(code: str, redirect_uri: str, simkl_cfg: dict, cfg_path: Path, debug: bool=False):
    payload = {
        "grant_type": "authorization_code",
        "code": code.strip(),
        "redirect_uri": redirect_uri,
        "client_id": simkl_cfg.get("client_id", ""),
        "client_secret": simkl_cfg.get("client_secret", ""),
    }
    r = requests.post(SIMKL_OAUTH_TOKEN, json=payload, headers={"User-Agent": UA}, timeout=30)
    if not r.ok:
        raise SystemExit(f"[!] SIMKL token exchange failed: HTTP {r.status_code} {r.text}")
    tok = r.json()
    simkl_cfg["access_token"] = tok["access_token"]
    simkl_cfg["refresh_token"] = tok.get("refresh_token", simkl_cfg.get("refresh_token", ""))
    simkl_cfg["token_expires_at"] = time.time() + int(tok.get("expires_in", 3600))
    full_cfg = load_config_file(cfg_path)
    full_cfg["simkl"] = simkl_cfg
    dump_config_file(cfg_path, full_cfg)
    if debug:
        print("[debug] SIMKL token exchange success; tokens saved to", cfg_path)
    return tok

class _RedirectHandler(BaseHTTPRequestHandler):
    def _html(self, body: str, status: int=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, fmt, *args):
        if getattr(self.server, "debug", False):
            super().log_message(fmt, *args)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            return self._html("<h3>Not Found</h3>", 404)
        qs = urllib.parse.parse_qs(parsed.query or "")
        code = (qs.get("code") or [""])[0].strip()
        state = (qs.get("state") or [""])[0].strip()
        if not code:
            return self._html("<h3>Missing ?code</h3>", 400)
        if self.server.expected_state and state and state != self.server.expected_state:
            return self._html("<h3>State mismatch</h3>", 400)
        try:
            simkl_exchange_code_for_tokens(
                code, self.server.redirect_uri, self.server.simkl_cfg, self.server.cfg_path, debug=self.server.debug
            )
            return self._html("<h3>Success!</h3><p>Tokens saved. You can close this tab.</p>")
        except SystemExit as e:
            return self._html(f"<h3>Exchange failed</h3><pre>{e}</pre>", 500)
        except Exception as e:
            return self._html(f"<h3>Unexpected error</h3><pre>{e}</pre>", 500)

def simkl_oauth_redirect(cfg_path: Path, bind_host: str="0.0.0.0", bind_port: int=8787, open_browser: bool=False, debug: bool=False):
    cfg = load_config_file(cfg_path)
    s = cfg.get("simkl") or {}
    if not s.get("client_id") or not s.get("client_secret"):
        raise SystemExit("[!] Please set simkl.client_id and simkl.client_secret in config.json first.")

    shown_host = detect_local_ip() if bind_host in ("0.0.0.0", "::") else bind_host
    redirect_uri = f"http://{shown_host}:{bind_port}/callback"
    state = secrets.token_urlsafe(16)
    auth_url = build_simkl_authorize_url(s["client_id"], redirect_uri, state=state)

    srv = HTTPServer((bind_host, bind_port), _RedirectHandler)
    srv.simkl_cfg = s
    srv.cfg_path = cfg_path
    srv.redirect_uri = redirect_uri
    srv.expected_state = state
    srv.debug = debug

    print("[i] Redirect helper is running")
    print(f"    Callback URL: {redirect_uri}")
    print("[i] IMPORTANT: Ensure this exact redirect is configured in your SIMKL app settings.")
    print("[i] Open this authorization URL from any device that can reach this server:")
    print(f"    {auth_url}")

    if open_browser:
        try:
            webbrowser.open(auth_url)
        except Exception:
            pass

    print("[i] Waiting for SIMKL to redirect back with ?code=...")
    try:
        srv.handle_request()  # handle a single request then exit
        print("[✓] Code handled; tokens saved if the exchange succeeded.")
    except KeyboardInterrupt:
        print("\n[!] Redirect helper stopped before completing.")

# --------------------------- Plex (plexapi + read fallback) ------------------
try:
    import plexapi
    from plexapi.myplex import MyPlexAccount  # type: ignore
    from plexapi.exceptions import NotFound as PlexNotFound  # type: ignore
except Exception:
    py = Path(sys.executable)
    pip = py.with_name("pip")
    print(ANSI_R + "[!] plexapi is not installed in this Python environment." + ANSI_X)
    print("    Install it first, then rerun:")
    print(f"      {pip} install -U plexapi")
    print("    or")
    print(f"      {py} -m pip install -U plexapi")
    sys.exit(1)

_PAT_IMDB = re.compile(r"(?:com\.plexapp\.agents\.imdb|imdb)://(tt\d+)", re.I)
_PAT_TMDB = re.compile(r"(?:com\.plexapp\.agents\.tmdb|tmdb)://(\d+)", re.I)
_PAT_TVDB = re.compile(r"(?:com\.plexapp\.agents\.thetvdb|tvdb)://(\d+)", re.I)

def _extract_ids_from_guid_strings(guid_values: List[str]) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    imdb = tmdb = tvdb = None
    for s in guid_values or []:
        s = str(s)
        m = _PAT_IMDB.search(s)
        if m and not imdb:
            imdb = m.group(1)
        m = _PAT_TMDB.search(s)
        if m and not tmdb:
            try:
                tmdb = int(m.group(1))
            except Exception:
                pass
        m = _PAT_TVDB.search(s)
        if m and not tvdb:
            try:
                tvdb = int(m.group(1))
            except Exception:
                pass
    return imdb, tmdb, tvdb

def _plexapi_upgrade_hint(where: str, exc: Exception | None, debug: bool):
    v = getattr(plexapi, "__version__", "?")
    pip_bin = Path(sys.executable).with_name("pip")
    python_bin = Path(sys.executable)
    print("")
    print(ANSI_R + "[!] Plex API call failed" + ANSI_X)
    print(f"    While: {where}")
    print(f"    Detected plexapi version: {v}")
    print("    Your installed plexapi likely lacks support for the current Plex Discover")
    print("    search or watchlist write endpoints required by this script.")
    print("")
    print("    Please upgrade plexapi in the SAME environment:")
    print(f"      {pip_bin} install -U plexapi")
    print("    or")
    print(f"      {python_bin} -m pip install -U plexapi")
    print("")
    print("    After upgrading, rerun:")
    print("      ./plex_simkl_watchlist_sync.py --sync")
    if debug and exc is not None:
        print("")
        print(f"    [debug] Underlying error: {repr(exc)}")
    sys.exit(1)

# Read via plexapi (preferred)
def plex_fetch_watchlist_items_via_plexapi(acct: MyPlexAccount, debug: bool=False) -> Optional[List[object]]:
    try:
        movies = acct.watchlist(libtype="movie")
        shows = acct.watchlist(libtype="show")
        items = (movies or []) + (shows or [])
        if debug:
            print(f"[debug] plexapi watchlist fetched: {len(items)} items")
        return items
    except Exception as e:
        if debug:
            print(f"[debug] plexapi watchlist fetch failed: {e}")
        return None

# Read fallback via Discover HTTP (read-only)
def _plex_headers(token: str) -> dict:
    return {
        "X-Plex-Token": token,
        "Accept": "application/json",
        "X-Plex-Product": "PlexWatchlistSync",
        "X-Plex-Version": __VERSION__,
        "X-Plex-Client-Identifier": "plex-simkl-bridge",
        "X-Plex-Device": "Python",
        "X-Plex-Device-Name": "plex-simkl-bridge",
        "X-Plex-Platform": "Python",
        "User-Agent": UA,
    }

def _discover_get(path: str, token: str, params: dict, timeout: int=20) -> Optional[dict]:
    url = f"{DISCOVER_HOST}{path}"
    try:
        r = requests.get(url, headers=_plex_headers(token), params=params, timeout=timeout)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return None

def _discover_metadata_by_ratingkey(token: str, rating_key: str, debug: bool=False) -> Optional[dict]:
    params = {"includeExternalMedia": "1"}
    data = _discover_get(f"{PLEX_METADATA_PATH}/{rating_key}", token, params, timeout=12)
    if not data:
        return None
    md = (data.get("MediaContainer", {}).get("Metadata") or [])
    return md[0] if md else None

def plex_fetch_watchlist_items_via_discover(token: str, page_size: int=100, debug: bool=False) -> List[dict]:
    params_base = {"includeCollections": "1", "includeExternalMedia": "1"}
    start = 0
    items: List[dict] = []
    while True:
        params = dict(params_base)
        params["X-Plex-Container-Start"] = start
        params["X-Plex-Container-Size"] = page_size
        data = _discover_get(PLEX_WATCHLIST_PATH, token, params, timeout=20)
        if not data:
            if debug:
                print("[debug] discover watchlist: no data")
            break
        mc = data.get("MediaContainer", {}) or {}
        md = mc.get("Metadata", []) or []
        if debug:
            total = mc.get("totalSize")
            try:
                total = int(total) if total is not None else None
            except Exception:
                total = None
            print(f"[debug] discover page start={start} got={len(md)} total={total}")
        for it in md:
            title = it.get("title") or it.get("name")
            rating_key = str(it.get("ratingKey") or "") or ""
            mtype = it.get("type") or it.get("metadataType")
            mtype = "show" if (isinstance(mtype, str) and mtype.startswith("show")) or mtype == 2 else "movie"

            guid_values: List[str] = []
            if isinstance(it.get("guid"), str):
                guid_values.append(it["guid"])
            if isinstance(it.get("Guid"), list):
                for gg in it["Guid"]:
                    if isinstance(gg, dict) and "id" in gg:
                        guid_values.append(gg["id"])

            imdb, tmdb, tvdb = _extract_ids_from_guid_strings(guid_values)
            if not any([imdb, tmdb, tvdb]) and rating_key:
                enriched = _discover_metadata_by_ratingkey(token, rating_key, debug=debug)
                if enriched:
                    e_guids = []
                    if isinstance(enriched.get("Guid"), list):
                        for gg in enriched["Guid"]:
                            if isinstance(gg, dict) and "id" in gg:
                                e_guids.append(gg["id"])
                    if isinstance(enriched.get("guid"), str):
                        e_guids.append(enriched["guid"])
                    imdb, tmdb, tvdb = _extract_ids_from_guid_strings(e_guids)
                    if debug:
                        allg = list(dict.fromkeys(guid_values + e_guids))
                        print(f"[debug] Enriched '{title}' (rk={rating_key}) GUIDs: {allg}")

            ids = {}
            if imdb:
                ids["imdb"] = imdb
            if tmdb is not None:
                ids["tmdb"] = tmdb
            if tvdb is not None:
                ids["tvdb"] = tvdb

            items.append({"type": mtype, "title": title, "ids": ids})

        size = int(mc.get("size", len(md)))
        if not md or size < page_size:
            break
        start += size if size else page_size
    return items

# Mixed fetch: plexapi first, then Discover HTTP (read-only) if needed
def plex_fetch_watchlist_items(acct: MyPlexAccount, plex_token: str, debug: bool=False) -> List[object | dict]:
    items = plex_fetch_watchlist_items_via_plexapi(acct, debug=debug)
    if items is not None:
        return items
    if debug:
        print("[debug] Falling back to Discover HTTP for watchlist read")
    return plex_fetch_watchlist_items_via_discover(plex_token, page_size=100, debug=debug)

def plex_item_to_ids(item) -> dict:
    """Extract provider IDs from either a plexapi Discover item or a fallback dict row."""
    if isinstance(item, dict):
        ids = item.get("ids") or {}
        title = item.get("title")
        year = item.get("year")
        out = {"title": title, "year": year}
        out.update({k: v for k, v in ids.items() if v is not None})
        return {k: v for k, v in out.items() if v is not None}

    title = getattr(item, "title", None)
    year = getattr(item, "year", None)
    guid_values: List[str] = []
    try:
        for g in (getattr(item, "guids", []) or []):
            gid = getattr(g, "id", None)
            if isinstance(gid, str):
                guid_values.append(gid)
    except Exception:
        pass
    gsingle = getattr(item, "guid", None)
    if isinstance(gsingle, str):
        guid_values.append(gsingle)
    imdb, tmdb, tvdb = _extract_ids_from_guid_strings(guid_values)
    out = {"title": title, "year": year, "imdb": imdb, "tmdb": tmdb, "tvdb": tvdb}
    return {k: v for k, v in out.items() if v}

def item_libtype(item) -> str:
    if isinstance(item, dict):
        return "show" if item.get("type") == "show" else "movie"
    t = getattr(item, "type", "movie")
    return "show" if t == "show" else "movie"

# plexapi search + add/remove (no HTTP fallbacks)
def resolve_discover_item(acct: MyPlexAccount, ids: dict, libtype: str, debug: bool=False):
    queries: List[str] = []
    if ids.get("imdb"):
        queries.append(ids["imdb"])
    if ids.get("tmdb"):
        queries.append(str(ids["tmdb"]))
    if ids.get("tvdb"):
        queries.append(str(ids["tvdb"]))
    if ids.get("title"):
        queries.append(ids["title"])

    for q in queries:
        try:
            hits = acct.searchDiscover(q, libtype=libtype) or []
        except TypeError as e:
            _plexapi_upgrade_hint("MyPlexAccount.searchDiscover(libtype=...)", e, debug)
        except PlexNotFound as e:
            _plexapi_upgrade_hint("Searching Discover via plexapi", e, debug)
        except Exception as e:
            if debug:
                print(f"[debug] searchDiscover error for {q}: {e}")
            hits = []

        for md in hits:
            md_ids = plex_item_to_ids(md)
            if ids.get("imdb") and md_ids.get("imdb") == ids.get("imdb"):
                return md
            if ids.get("tmdb") and md_ids.get("tmdb") == ids.get("tmdb"):
                return md
            if ids.get("tvdb") and md_ids.get("tvdb") == ids.get("tvdb"):
                return md
            if ids.get("title") and ids.get("year"):
                try:
                    if (str(md_ids.get("title", "")).strip().lower() == str(ids["title"]).strip().lower() and
                        int(md_ids.get("year", 0)) == int(ids["year"])):
                        return md
                except Exception:
                    pass
    return None

def plex_add_by_ids(acct: MyPlexAccount, ids: dict, libtype: str, debug: bool=False) -> bool:
    it = resolve_discover_item(acct, ids, libtype, debug=debug)
    if not it:
        if debug:
            print(f"[debug] plexapi add: could not resolve {ids}")
        return False
    try:
        it.addToWatchlist(account=acct)
        if debug:
            print(f"[debug] plexapi add OK: {getattr(it, 'title', ids)}")
        return True
    except TypeError as e:
        _plexapi_upgrade_hint("addToWatchlist(account=...)", e, debug)
    except Exception as e:
        if debug:
            print(f"[debug] plexapi add failed: {e}")
        return False

def plex_remove_by_ids(acct: MyPlexAccount, ids: dict, libtype: str, debug: bool=False) -> bool:
    it = resolve_discover_item(acct, ids, libtype, debug=debug)
    if not it:
        if debug:
            print(f"[debug] plexapi remove: could not resolve {ids}")
        return False
    try:
        it.removeFromWatchlist(account=acct)
        if debug:
            print(f"[debug] plexapi remove OK: {getattr(it, 'title', ids)}")
        return True
    except TypeError as e:
        _plexapi_upgrade_hint("removeFromWatchlist(account=...)", e, debug)
    except Exception as e:
        if debug:
            print(f"[debug] plexapi remove failed: {e}")
        return False

# --------------------------- Sync helpers ------------------------------------
def neutral_precheck_msg(plex_total: int, simkl_total: int):
    if plex_total == simkl_total:
        print(f"[i] Pre-sync counts: Plex={plex_total} vs SIMKL={simkl_total} (already equal)")
    else:
        print(f"[i] Pre-sync counts: Plex={plex_total} vs SIMKL={simkl_total} (differences → will sync)")

def colored_postcheck(plex_total: int, simkl_total: int):
    ok = plex_total == simkl_total
    msg = "EQUAL" if ok else "NOT EQUAL"
    color = ANSI_G if ok else ANSI_R
    print(f"[i] Post-sync (counts): Plex={plex_total} vs SIMKL={simkl_total} ? {color}{msg}{ANSI_X}")

def gather_plex_sets(items: List[object | dict]) -> Tuple[List[dict], Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    parsed: List[dict] = []
    plex_movies_set: Set[Tuple[str, str]] = set()
    plex_shows_set: Set[Tuple[str, str]] = set()
    for it in items:
        libtype = item_libtype(it)
        ids_full = plex_item_to_ids(it)
        ids = {k: v for k, v in ids_full.items() if k in ("imdb", "tmdb", "tvdb", "slug") and v}
        row = {"type": libtype, "title": ids_full.get("title"), "year": ids_full.get("year"), "ids": ids}
        parsed.append(row)
        if ids:
            idset = idset_from_ids(ids)
            if libtype == "movie":
                plex_movies_set |= idset
            else:
                plex_shows_set |= idset
    return parsed, plex_movies_set, plex_shows_set

def plan_differences(
    plex_rows: List[dict],
    plex_movies_set: Set[Tuple[str, str]],
    plex_shows_set: Set[Tuple[str, str]],
    simkl_movies: List[dict],
    simkl_shows: List[dict]
):
    simkl_movies_set = set().union(*(idset_from_ids(i["ids"]) for i in simkl_movies)) if simkl_movies else set()
    simkl_shows_set = set().union(*(idset_from_ids(i["ids"]) for i in simkl_shows)) if simkl_shows else set()

    plex_only_movies, plex_only_shows, simkl_only_movies, simkl_only_shows = [], [], [], []

    for p in plex_rows:
        if not p.get("ids"):
            continue
        pidset = idset_from_ids(p["ids"])
        if p["type"] == "movie":
            if not (pidset & simkl_movies_set):
                plex_only_movies.append(p)
        else:
            if not (pidset & simkl_shows_set):
                plex_only_shows.append(p)

    for it in simkl_movies:
        sidset = idset_from_ids(it["ids"])
        if not (sidset & plex_movies_set):
            simkl_only_movies.append(it)
    for it in simkl_shows:
        sidset = idset_from_ids(it["ids"])
        if not (sidset & plex_shows_set):
            simkl_only_shows.append(it)

    return plex_only_movies, plex_only_shows, simkl_only_movies, simkl_only_shows

def build_index(rows_movies: List[dict], rows_shows: List[dict]):
    """
    Build per-side index: identity_key -> record {ids, type, title, year}
    """
    idx: Dict[str, dict] = {}

    for r in rows_movies:
        ids = combine_ids(r["ids"])
        pair = canonical_identity(ids)
        if not pair:
            continue
        idx[identity_key(pair)] = {
            "type": "movie",
            "ids": ids,
            "title": r.get("title"),
            "year": r.get("year"),
        }
    for r in rows_shows:
        ids = combine_ids(r["ids"])
        pair = canonical_identity(ids)
        if not pair:
            continue
        idx[identity_key(pair)] = {
            "type": "show",
            "ids": ids,
            "title": r.get("title"),
            "year": r.get("year"),
        }
    return idx

def build_index_from_simkl(simkl_movies: List[dict], simkl_shows: List[dict]):
    idx: Dict[str, dict] = {}
    for m in simkl_movies:
        ids = combine_ids(m["ids"])
        pair = canonical_identity(ids)
        if not pair:
            continue
        idx[identity_key(pair)] = {"type": "movie", "ids": ids, "title": m.get("title"), "year": ids.get("year")}
    for s in simkl_shows:
        ids = combine_ids(s["ids"])
        pair = canonical_identity(ids)
        if not pair:
            continue
        idx[identity_key(pair)] = {"type": "show", "ids": ids, "title": s.get("title"), "year": ids.get("year")}
    return idx

def snapshot_for_state(plex_idx: Dict[str, dict], simkl_idx: Dict[str, dict]) -> dict:
    return {
        "plex": {"items": plex_idx},
        "simkl": {"items": simkl_idx},
    }

# --------------------------- CLI / Main --------------------------------------
def build_parser() -> argparse.ArgumentParser:
    epilog = """examples:
  Initialize SIMKL tokens (redirect helper on port 8787):
    ./plex_simkl_watchlist_sync.py --init-simkl redirect --bind 0.0.0.0:8787 --open

  Run a sync (banner first, then [i] logs):
    ./plex_simkl_watchlist_sync.py --sync

  Override Plex token just for this run:
    ./plex_simkl_watchlist_sync.py --sync --plex-account-token <TOKEN>

  Reset the local state snapshot (safe re-seed on next run):
    ./plex_simkl_watchlist_sync.py --reset-state
"""
    ap = argparse.ArgumentParser(
        prog="plex_simkl_watchlist_sync.py",
        description="Sync your Plex Watchlist with SIMKL Plan-to-Watch (plexapi-first, Discover HTTP fallback for read only).",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )
    ap.add_argument("--sync", action="store_true", help="Run synchronization using values from config.json")
    ap.add_argument("--init-simkl", choices=["redirect"], help="Initialize SIMKL tokens via local HTTP redirect helper")
    ap.add_argument("--bind", default="0.0.0.0:8787", help="Bind host:port for redirect helper (default 0.0.0.0:8787)")
    ap.add_argument("--open", action="store_true", help="With --init-simkl redirect, also try to open the auth URL locally")
    ap.add_argument("--plex-account-token", help="Override Plex token from config.json for this run only")
    ap.add_argument("--debug", action="store_true", help="Verbose logging")
    ap.add_argument("--version", action="store_true", help="Print script and plexapi versions")
    ap.add_argument("--reset-state", action="store_true", help="Delete local state.json so next --sync re-seeds")
    return ap

def main():
    ap = build_parser()

    # Show help when no flags are provided.
    if len(sys.argv) == 1:
        ap.print_help()
        return

    args = ap.parse_args()

    if args.version:
        import plexapi
        print(f"Script version: {__VERSION__}")
        print(f"plexapi version: {getattr(plexapi, '__version__', '?')}")
        return

    if args.reset_state:
        clear_state(STATE_PATH)
        print("[✓] Cleared local state.json (next --sync will safely re-seed).")
        return

    # Create starter config if missing.
    created = ensure_config_exists(CONFIG_PATH)
    if created:
        print("[i] Created starter config.json next to the script.")
        print("    Fill in:")
        print("      - simkl.client_id and simkl.client_secret")
        print("      - plex.account_token")
        print("    Then initialize SIMKL tokens:")
        print("      ./plex_simkl_watchlist_sync.py --init-simkl redirect --bind 0.0.0.0:8787")
        return

    # SIMKL OAuth helper
    if args.init_simkl:
        host, port = "0.0.0.0", 8787
        if ":" in args.bind:
            host, p = args.bind.rsplit(":", 1)
            try:
                port = int(p)
            except Exception:
                pass
        simkl_oauth_redirect(CONFIG_PATH, bind_host=host, bind_port=port, open_browser=bool(args.open), debug=True)
        return

    if not args.sync:
        ap.print_help()
        return

    # Sync flow
    print_banner()

    cfg = load_config_file(CONFIG_PATH)
    plex_cfg = cfg.get("plex") or {}
    simkl_cfg = cfg.get("simkl") or {}
    sync_cfg = cfg.get("sync") or {}
    run_cfg = cfg.get("runtime") or {}
    bidi_cfg = (sync_cfg.get("bidirectional") or {})

    debug = bool(args.debug or run_cfg.get("debug", False))

    plex_token = args.plex_account_token or plex_cfg.get("account_token", "")
    if not plex_token:
        print("[!] Missing Plex token. Please add it under 'plex.account_token' in config.json")
        return

    # SIMKL credentials
    if not simkl_cfg.get("client_id") or not simkl_cfg.get("client_secret"):
        print("[!] Missing SIMKL client credentials. Set 'simkl.client_id' and 'simkl.client_secret' in config.json.")
        print("    Then run: ./plex_simkl_watchlist_sync.py --init-simkl redirect --bind 0.0.0.0:8787")
        return
    if not simkl_cfg.get("access_token"):
        print("[!] No SIMKL access_token found. Initialize tokens first:")
        print("    ./plex_simkl_watchlist_sync.py --init-simkl redirect --bind 0.0.0.0:8787")
        return

    if token_expired(simkl_cfg):
        cfg = simkl_refresh(cfg, CONFIG_PATH, debug=debug)
        simkl_cfg = cfg.get("simkl") or {}

    # Plex account
    try:
        acct = MyPlexAccount(token=plex_token)
    except Exception as e:
        print(ANSI_R + "[!] Could not authenticate to Plex with provided token." + ANSI_X)
        print(f"    {e}")
        return

    # 1) Pull both sides
    plex_items_mixed = plex_fetch_watchlist_items(acct, plex_token, debug=debug)
    print(f"[i] Plex items: {len(plex_items_mixed)}")

    plex_rows, plex_movies_set, plex_shows_set = gather_plex_sets(plex_items_mixed)

    print("[i] Fetching SIMKL Plan to Watch (movies & shows)")
    shows_items, movies_items = simkl_get_ptw(simkl_cfg, debug=debug)

    simkl_movies = [{"ids": ids_from_simkl_item(it), "title": (it.get("movie") or {}).get("title")} for it in movies_items]
    simkl_shows = [{"ids": ids_from_simkl_item(it), "title": (it.get("show") or {}).get("title")} for it in shows_items]

    # For indexing & state
    plex_movies_rows = [r for r in plex_rows if r["type"] == "movie"]
    plex_shows_rows  = [r for r in plex_rows if r["type"] == "show"]
    plex_idx         = build_index(plex_movies_rows, plex_shows_rows)
    simkl_idx        = build_index_from_simkl(simkl_movies, simkl_shows)

    plex_total, simkl_total = len(plex_rows), (len(simkl_movies) + len(simkl_shows))
    neutral_precheck_msg(plex_total, simkl_total)

    # 2) Plan differences for union/mirror helpers
    plex_only_movies, plex_only_shows, simkl_only_movies, simkl_only_shows = plan_differences(
        plex_rows, plex_movies_set, plex_shows_set, simkl_movies, simkl_shows
    )

    enable_add = bool(sync_cfg.get("enable_add", True))
    enable_remove = bool(sync_cfg.get("enable_remove", True))
    bidi_enabled = bool(bidi_cfg.get("enabled", True))
    mode = str(bidi_cfg.get("mode", "two-way")).lower()
    source_of_truth = str(bidi_cfg.get("source_of_truth", "plex")).lower()

    if debug:
        print(f"[debug] plan: PLEX-only movies={len(plex_only_movies)} shows={len(plex_only_shows)}")
        print(f"[debug] plan: SIMKL-only movies={len(simkl_only_movies)} shows={len(simkl_only_shows)}")
        print(f"[debug] mode={mode} source_of_truth={source_of_truth} add={enable_add} remove={enable_remove}")

    hdrs_simkl = simkl_headers(simkl_cfg)

    # Load previous state (for true two-way with deletions)
    prev_state = load_state(STATE_PATH)

    # Track failures; if any write fails, we won't save state to avoid losing deltas
    any_failure = False
    added_simkl = removed_simkl = added_plex = removed_plex = 0

    if bidi_enabled and mode == "two-way":
        if prev_state is None:
            # First run: safe seeding (adds only)
            if enable_add:
                simkl_add_payload = {}
                if plex_only_movies:
                    simkl_add_payload["movies"] = [{"to": "plantowatch", "ids": combine_ids(p["ids"])} for p in plex_only_movies]
                if plex_only_shows:
                    simkl_add_payload["shows"] = [{"to": "plantowatch", "ids": combine_ids(p["ids"])} for p in plex_only_shows]
                if simkl_add_payload:
                    if debug:
                        print(f"[debug] SIMKL add payload (first-run seed):\n{json.dumps(simkl_add_payload, indent=2)}")
                    r = requests.post(SIMKL_ADD_TO_LIST, headers=hdrs_simkl, json=simkl_add_payload, timeout=45)
                    if not r.ok:
                        print(ANSI_R + f"[!] SIMKL add-to-list failed: HTTP {r.status_code} {r.text}" + ANSI_X)
                        any_failure = True
                    else:
                        added_simkl = len(simkl_add_payload.get("movies", [])) + len(simkl_add_payload.get("shows", []))
                        if added_simkl:
                            print(f"[✓] Added Plex→SIMKL items: {added_simkl}")
                if enable_add:
                    for it in simkl_only_movies:
                        if plex_add_by_ids(acct, it["ids"], "movie", debug=debug):
                            added_plex += 1
                        else:
                            any_failure = True
                    for it in simkl_only_shows:
                        if plex_add_by_ids(acct, it["ids"], "show", debug=debug):
                            added_plex += 1
                        else:
                            any_failure = True
                    if added_plex:
                        print(f"[✓] Added SIMKL→Plex items: {added_plex}")

            # Save initial snapshot even if some adds failed? Safer to only save on clean run.
            if any_failure:
                print(ANSI_R + "[!] Some actions failed; NOT saving state so the changes will retry on the next run." + ANSI_X)
            else:
                save_state(STATE_PATH, snapshot_for_state(plex_idx, simkl_idx))
                if debug:
                    print("[debug] First-run seed complete; state saved.")
        else:
            # True two-way with deletions based on deltas vs last state
            prev_plex_idx  = (prev_state.get("plex") or {}).get("items") or {}
            prev_simkl_idx = (prev_state.get("simkl") or {}).get("items") or {}

            new_plex_keys  = set(plex_idx.keys())
            old_plex_keys  = set(prev_plex_idx.keys())
            new_simkl_keys = set(simkl_idx.keys())
            old_simkl_keys = set(prev_simkl_idx.keys())

            plex_added_keys   = new_plex_keys - old_plex_keys
            plex_removed_keys = old_plex_keys - new_plex_keys
            simkl_added_keys  = new_simkl_keys - old_simkl_keys
            simkl_removed_keys= old_simkl_keys - new_simkl_keys

            if debug:
                print(f"[debug] deltas: plex_added={len(plex_added_keys)} plex_removed={len(plex_removed_keys)} "
                      f"simkl_added={len(simkl_added_keys)} simkl_removed={len(simkl_removed_keys)}")

            # Propagate Plex deltas -> SIMKL
            if enable_add and plex_added_keys:
                payload = {"movies": [], "shows": []}
                for k in plex_added_keys:
                    rec = plex_idx.get(k)
                    if not rec:
                        continue
                    to = "movies" if rec["type"] == "movie" else "shows"
                    payload[to].append({"to": "plantowatch", "ids": combine_ids(rec["ids"])})
                # prune empties
                payload = {k: v for k, v in payload.items() if v}
                if payload:
                    if debug:
                        print(f"[debug] SIMKL add payload (plex→simkl via deltas):\n{json.dumps(payload, indent=2)}")
                    r = requests.post(SIMKL_ADD_TO_LIST, headers=hdrs_simkl, json=payload, timeout=45)
                    if not r.ok:
                        print(ANSI_R + f"[!] SIMKL add-to-list failed: HTTP {r.status_code} {r.text}" + ANSI_X)
                        any_failure = True
                    else:
                        added_simkl += sum(len(v) for v in payload.values())

            if enable_remove and plex_removed_keys:
                payload = {"movies": [], "shows": []}
                for k in plex_removed_keys:
                    rec = prev_plex_idx.get(k)  # use old snapshot to retrieve ids
                    if not rec:
                        continue
                    to = "movies" if rec["type"] == "movie" else "shows"
                    payload[to].append({"ids": combine_ids(rec["ids"])})
                payload = {k: v for k, v in payload.items() if v}
                if payload:
                    if debug:
                        print(f"[debug] SIMKL remove payload (plex→simkl via deltas):\n{json.dumps(payload, indent=2)}")
                    r = requests.post(SIMKL_HISTORY_REMOVE, headers=hdrs_simkl, json=payload, timeout=45)
                    if not r.ok:
                        print(ANSI_R + f"[!] SIMKL history/remove failed: HTTP {r.status_code} {r.text}" + ANSI_X)
                        any_failure = True
                    else:
                        removed_simkl += sum(len(v) for v in payload.values())

            # Propagate SIMKL deltas -> Plex
            if enable_add and simkl_added_keys:
                for k in simkl_added_keys:
                    rec = simkl_idx.get(k)
                    if not rec:
                        continue
                    ok = plex_add_by_ids(acct, rec["ids"], rec["type"], debug=debug)
                    if ok:
                        added_plex += 1
                    else:
                        any_failure = True

            if enable_remove and simkl_removed_keys:
                for k in simkl_removed_keys:
                    rec = prev_simkl_idx.get(k)  # use old snapshot to retrieve ids
                    if not rec:
                        continue
                    ok = plex_remove_by_ids(acct, rec["ids"], rec["type"], debug=debug)
                    if ok:
                        removed_plex += 1
                    else:
                        any_failure = True

            # Save updated snapshot only if all actions succeeded
            if any_failure:
                print(ANSI_R + "[!] Some actions failed; NOT saving state so the changes will retry on the next run." + ANSI_X)
            else:
                save_state(STATE_PATH, snapshot_for_state(plex_idx, simkl_idx))
                if debug:
                    print("[debug] State updated after successful two-way delta sync.")

            # Summary lines (optional)
            if added_simkl:
                print(f"[✓] PLEX→SIMKL adds applied: {added_simkl}")
            if removed_simkl:
                print(f"[✓] PLEX→SIMKL removals applied: {removed_simkl}")
            if added_plex or removed_plex:
                print(f"[✓] SIMKL→PLEX applied: +{added_plex} / -{removed_plex}")

    elif bidi_enabled and mode == "mirror":
        if source_of_truth == "plex":
            # Make SIMKL match Plex.
            simkl_add_payload = {}
            if enable_add and plex_only_movies:
                simkl_add_payload["movies"] = [{"to": "plantowatch", "ids": combine_ids(p["ids"])} for p in plex_only_movies]
            if enable_add and plex_only_shows:
                simkl_add_payload["shows"] = [{"to": "plantowatch", "ids": combine_ids(p["ids"])} for p in plex_only_shows]
            if simkl_add_payload:
                if debug:
                    print(f"[debug] SIMKL add payload (mirror/plex):\n{json.dumps(simkl_add_payload, indent=2)}")
                r = requests.post(SIMKL_ADD_TO_LIST, headers=hdrs_simkl, json=simkl_add_payload, timeout=45)
                if not r.ok:
                    print(ANSI_R + f"[!] SIMKL add-to-list failed: HTTP {r.status_code} {r.text}" + ANSI_X)
                    any_failure = True
                else:
                    total_added = len(simkl_add_payload.get("movies", [])) + len(simkl_add_payload.get("shows", []))
                    if total_added:
                        print(f"[✓] MIRROR(plex): added {total_added} to SIMKL")

            simkl_rm_payload = {}
            if enable_remove and simkl_only_movies:
                simkl_rm_payload["movies"] = [{"ids": combine_ids(m["ids"])} for m in simkl_only_movies]
            if enable_remove and simkl_only_shows:
                simkl_rm_payload["shows"] = [{"ids": combine_ids(s["ids"])} for s in simkl_only_shows]
            if simkl_rm_payload:
                if debug:
                    print(f"[debug] SIMKL remove payload (mirror/plex):\n{json.dumps(simkl_rm_payload, indent=2)}")
                r = requests.post(SIMKL_HISTORY_REMOVE, headers=hdrs_simkl, json=simkl_rm_payload, timeout=45)
                if not r.ok:
                    print(ANSI_R + f"[!] SIMKL history/remove failed: HTTP {r.status_code} {r.text}" + ANSI_X)
                    any_failure = True
                else:
                    total_removed = len(simkl_rm_payload.get("movies", [])) + len(simkl_rm_payload.get("shows", []))
                    if total_removed:
                        print(f"[✓] MIRROR(plex): removed {total_removed} from SIMKL")

        else:
            # Make Plex match SIMKL.
            added = removed = 0
            if enable_add:
                for it in simkl_only_movies:
                    if plex_add_by_ids(acct, it["ids"], "movie", debug=debug):
                        added += 1
                    else:
                        any_failure = True
                for it in simkl_only_shows:
                    if plex_add_by_ids(acct, it["ids"], "show", debug=debug):
                        added += 1
                    else:
                        any_failure = True
            if enable_remove:
                for p in plex_only_movies:
                    if plex_remove_by_ids(acct, p["ids"], "movie", debug=debug):
                        removed += 1
                    else:
                        any_failure = True
                for p in plex_only_shows:
                    if plex_remove_by_ids(acct, p["ids"], "show", debug=debug):
                        removed += 1
                    else:
                        any_failure = True
            if added or removed:
                print(f"[✓] MIRROR(simkl): added {added} to Plex; removed {removed} from Plex.")

        # Update state snapshot after mirror if all ok
        if not any_failure:
            save_state(STATE_PATH, snapshot_for_state(plex_idx, simkl_idx))
        else:
            print(ANSI_R + "[!] Some actions failed; NOT saving state so the changes will retry on the next run." + ANSI_X)

    else:
        # One-way: Plex -> SIMKL
        simkl_add_payload = {}
        if enable_add and (plex_only_movies or plex_only_shows):
            if plex_only_movies:
                simkl_add_payload["movies"] = [{"to": "plantowatch", "ids": combine_ids(p["ids"])} for p in plex_only_movies]
            if plex_only_shows:
                simkl_add_payload["shows"] = [{"to": "plantowatch", "ids": combine_ids(p["ids"])} for p in plex_only_shows]
            if debug:
                print(f"[debug] SIMKL add payload (one-way):\n{json.dumps(simkl_add_payload, indent=2)}")
            r = requests.post(SIMKL_ADD_TO_LIST, headers=hdrs_simkl, json=simkl_add_payload, timeout=45)
            if not r.ok:
                print(ANSI_R + f"[!] SIMKL add-to-list failed: HTTP {r.status_code} {r.text}" + ANSI_X)
                any_failure = True
            else:
                total_added = len(simkl_add_payload.get("movies", [])) + len(simkl_add_payload.get("shows", []))
                if total_added:
                    print(f"[✓] Added missing Plex items to SIMKL: {total_added}")

        if enable_remove and (simkl_only_movies or simkl_only_shows):
            rm_payload = {}
            if simkl_only_movies:
                rm_payload["movies"] = [{"ids": combine_ids(m["ids"])} for m in simkl_only_movies]
            if simkl_only_shows:
                rm_payload["shows"] = [{"ids": combine_ids(s["ids"])} for s in simkl_only_shows]
            if debug:
                print(f"[debug] SIMKL remove payload (one-way):\n{json.dumps(rm_payload, indent=2)}")
            r = requests.post(SIMKL_HISTORY_REMOVE, headers=hdrs_simkl, json=rm_payload, timeout=45)
            if not r.ok:
                print(ANSI_R + f"[!] SIMKL history/remove failed: HTTP {r.status_code} {r.text}" + ANSI_X)
                any_failure = True
            else:
                total_removed = len(rm_payload.get("movies", [])) + len(rm_payload.get("shows", []))
                if total_removed:
                    print(f"[✓] Removed SIMKL-only items: {total_removed}")

        # Update state snapshot after one-way if all ok
        if not any_failure:
            save_state(STATE_PATH, snapshot_for_state(plex_idx, simkl_idx))
        else:
            print(ANSI_R + "[!] Some actions failed; NOT saving state so the changes will retry on the next run." + ANSI_X)

    # 4) Post-check
    plex_items_after = plex_fetch_watchlist_items(acct, plex_token, debug=debug)
    shows2, movies2 = simkl_get_ptw(simkl_cfg, debug=debug)
    colored_postcheck(len(plex_items_after), len(shows2) + len(movies2))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Aborted")
