#!/usr/bin/env bash
set -euo pipefail

log(){ echo "[$(date -Iseconds)] $*"; }

# Defaults (cron-safe)
: "${RUNTIME_DIR:=/config}"
: "${SYNC_CMD:=python /app/plex_simkl_watchlist_sync.py --sync}"
: "${PATH:=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin}"

mkdir -p "$RUNTIME_DIR"

# --- TOKEN CHECK ---
if ! python - <<'PY'
import json,sys
try:
    cfg=json.load(open("/app/config.json"))
    plex_ok = bool(cfg.get("plex",{}).get("account_token"))
    simkl_ok = bool(cfg.get("simkl",{}).get("access_token"))
    sys.exit(0 if (plex_ok and simkl_ok) else 1)
except Exception:
    sys.exit(1)
PY
then
  log "[SKIP] Missing Plex or SIMKL tokens → aborting sync"
  exit 0
fi
# --- END TOKEN CHECK ---

# Simple lock to prevent overlapping runs
LOCKDIR="$RUNTIME_DIR/.sync.lock"
if mkdir "$LOCKDIR" 2>/dev/null; then
  trap 'rmdir "$LOCKDIR"' EXIT INT TERM
else
  log "[SKIP] Another run is in progress (lock: $LOCKDIR)"
  exit 0
fi

log "[RUN] cd $RUNTIME_DIR && ${SYNC_CMD}"
cd "$RUNTIME_DIR"
# Use sh -c to allow complex SYNC_CMD strings
sh -c "${SYNC_CMD}"
log "[RUN] done."
