# _statistics.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import json, time, threading

ROOT = Path(__file__).resolve().parent
CONFIG_BASE = Path("/config") if str(ROOT).startswith("/app") else ROOT
STATS_PATH = CONFIG_BASE / "statistics.json"

def _read_json(p: Path) -> Dict[str, Any]:
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _write_json_atomic(p: Path, data: Dict[str, Any]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(p)

class Stats:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path) if path else STATS_PATH
        self.lock = threading.Lock()
        self.data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        d = _read_json(self.path)
        if not isinstance(d, dict): d = {}
        d.setdefault("events", [])
        d.setdefault("samples", [])
        d.setdefault("current", {})
        self.data = d

    def _save(self) -> None:
        _write_json_atomic(self.path, self.data)

    @staticmethod
    def _union_keys(state: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        out: Dict[str, Dict[str, Any]] = {}
        plex = (state.get("plex", {}) or {}).get("items", {}) or {}
        simkl = (state.get("simkl", {}) or {}).get("items", {}) or {}
        keys: Set[str] = set(plex.keys()) | set(simkl.keys())
        for k in keys:
            p = plex.get(k) or {}
            s = simkl.get(k) or {}
            info = p or s
            src = "plex" if p and not s else ("simkl" if s and not p else "both")
            title = info.get("title") or info.get("name") or ""
            typ = (info.get("type") or "").lower()
            out[k] = {"src": src, "title": title, "type": typ}
        return out

    def refresh_from_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        now = int(time.time())
        with self.lock:
            prev = {k: dict(v) for k, v in (self.data.get("current") or {}).items()}
            cur = self._union_keys(state)
            prev_keys, cur_keys = set(prev.keys()), set(cur.keys())
            added, removed = sorted(cur_keys - prev_keys), sorted(prev_keys - cur_keys)

            ev = self.data.get("events") or []
            for k in added:
                m = cur.get(k) or {}
                ev.append({"ts": now, "action": "add", "key": k, "source": m.get("src",""), "title": m.get("title",""), "type": m.get("type","")})
            for k in removed:
                m = prev.get(k) or {}
                ev.append({"ts": now, "action": "remove", "key": k, "source": m.get("src",""), "title": m.get("title",""), "type": m.get("type","")})
            self.data["events"] = ev[-5000:]

            self.data["current"] = cur
            samples = self.data.get("samples") or []
            samples.append({"ts": now, "count": len(cur)})
            self.data["samples"] = samples[-4000:]

            self._save()
            return {"now": len(cur), "week": self._count_at(now - 7*86400), "month": self._count_at(now - 30*86400)}

    def record_event(self, *, action: str, key: str, source: str = "", title: str = "", typ: str = "") -> None:
        now = int(time.time())
        with self.lock:
            ev = self.data.get("events") or []
            ev.append({"ts": now, "action": action, "key": key, "source": source, "title": title, "type": typ})
            self.data["events"] = ev[-5000:]
            self._save()

    def _count_at(self, ts_floor: int) -> int:
        samples: List[Dict[str, Any]] = list(self.data.get("samples") or [])
        if not samples: return 0
        samples.sort(key=lambda r: int(r.get("ts") or 0))
        best = None
        for r in samples:
            t = int(r.get("ts") or 0)
            if t <= ts_floor: best = r
            else: break
        if best is None: best = samples[0]
        try: return int(best.get("count") or 0)
        except Exception: return 0

    def overview(self, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        now = int(time.time())
        with self.lock:
            now_count = len(self._union_keys(state).keys()) if state is not None else len(self.data.get("current") or {})
            return {"ok": True, "now": now_count, "week": self._count_at(now - 7*86400), "month": self._count_at(now - 30*86400)}
