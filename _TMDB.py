# _TMDb.py
# TMDb helpers (no external deps). Caches posters and metadata on disk.

from pathlib import Path
from typing import Tuple, Dict, Any, List
import json
import urllib.request

TMDB_IMG = "https://image.tmdb.org/t/p"
TMDB_API = "https://api.themoviedb.org/3"

def _urlopen(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read()

def get_meta(api_key: str, typ: str, tmdb_id: int, cache_dir: Path) -> Dict[str, Any]:
    meta_file = cache_dir / "tmdb_meta" / f"{typ}-{tmdb_id}.json"
    meta_file.parent.mkdir(parents=True, exist_ok=True)
    if meta_file.exists():
        try:
            return json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    url = f"{TMDB_API}/{typ}/{tmdb_id}?language=en-US&api_key={api_key}"
    data = _urlopen(url)
    j = json.loads(data.decode("utf-8"))
    genres: List[str] = [g.get("name","") for g in (j.get("genres") or []) if g.get("name")]
    out = {
        "id": tmdb_id,
        "type": typ,
        "title": j.get("title") or j.get("name") or "",
        "overview": j.get("overview") or "",
        "year": (j.get("release_date") or j.get("first_air_date") or "0000")[:4],
        "poster_path": j.get("poster_path"),
        "genres": genres,
    }
    meta_file.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out

def get_poster_file(api_key: str, typ: str, tmdb_id: int, size: str, cache_dir: Path) -> Tuple[Path, str]:
    meta = get_meta(api_key, typ, tmdb_id, cache_dir)
    poster_path = meta.get("poster_path")
    if not poster_path:
        raise RuntimeError("no poster")
    safe_size = size if size.startswith("w") or size == "original" else "w342"
    local = cache_dir / "tmdb" / typ / str(tmdb_id) / f"{safe_size}.jpg"
    local.parent.mkdir(parents=True, exist_ok=True)
    if not local.exists():
        url = f"{TMDB_IMG}/{safe_size}{poster_path}"
        data = _urlopen(url)
        local.write_bytes(data)
    return local, "image/jpeg"
