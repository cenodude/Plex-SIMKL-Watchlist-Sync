#!/usr/bin/env bash
set -euo pipefail

log(){ echo "[$(date -Iseconds)] $*"; }

# Defaults (cron-safe)
: "${RUNTIME_DIR:=/config}"
: "${SYNC_CMD:=python /app/plex_simkl_watchlist_sync.py --sync}"
: "${PATH:=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin}"

mkdir -p "$RUNTIME_DIR"

# --- TOKEN CHECK ---
MISSING="$(python - <<'PY'
import json,sys
missing=[]
try:
    cfg=json.load(open('/app/config.json','r',encoding='utf-8'))
    if not (cfg.get('plex',{}).get('account_token')):
        missing.append('plex.account_token')
    if not (cfg.get('simkl',{}).get('access_token')):
        missing.append('simkl.access_token')
except Exception:
    missing.append('config.json:unreadable')
print(' '.join(missing))
PY
)"

if [ -n "$MISSING" ]; then
  log "[SKIP] Missing required fields: $MISSING → aborting sync"
  exit 0
fi
# --- END TOKEN CHECK PBE---

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
