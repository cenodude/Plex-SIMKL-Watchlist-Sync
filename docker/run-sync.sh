#!/usr/bin/env bash
set -euo pipefail

log(){ echo "[$(date -Iseconds)] $*"; }

# Defaults (cron-safe)
: "${RUNTIME_DIR:=/config}"
: "${SYNC_CMD:=python /app/plex_simkl_watchlist_sync.py --sync}"
: "${WEBINTERFACE:=yes}"  # Default to 'yes', can be overridden in Dockerfile or when running the container
: "${PATH:=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin}"

mkdir -p "$RUNTIME_DIR"

# --- TOKEN CHECK ---
MISSING="$(python - <<'PY'
import json,sys
missing=[]
try:
    cfg=json.load(open('/app/config.json','r',encoding='utf-8'))
    if not (cfg.get('plex',{}).get('account_token')):  # Check for Plex token
        missing.append('plex.account_token')
    if not (cfg.get('simkl',{}).get('access_token')):  # Check for SIMKL token
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
# --- END TOKEN CHECK PBE ---

# Simple lock to prevent overlapping runs
LOCKDIR="$RUNTIME_DIR/.sync.lock"
if mkdir "$LOCKDIR" 2>/dev/null; then
  trap 'rmdir "$LOCKDIR"' EXIT INT TERM
else
  log "[SKIP] Another run is in progress (lock: $LOCKDIR)"
  exit 0
fi

# Check if WEBINTERFACE is enabled and start the web interface if 'yes'
if [[ "$WEBINTERFACE" == "yes" ]]; then
    log "[RUN] Web interface is enabled. Skipping sync and starting webapp.py..."
    # Start the web interface (FastAPI app)
    exec python /app/webapp.py
else
    log "[RUN] cd $RUNTIME_DIR && ${SYNC_CMD}"
    cd "$RUNTIME_DIR"
    # Use sh -c to allow complex SYNC_CMD strings
    sh -c "${SYNC_CMD}"
    log "[RUN] done."
fi
