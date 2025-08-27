#!/usr/bin/env bash
set -euo pipefail
log(){ echo "[$(date -Iseconds)] $*"; }

: "${RUNTIME_DIR:=/config}"
: "${SYNC_CMD:=python /app/plex_simkl_watchlist_sync.py --sync}"
: "${PATH:=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin}"

mkdir -p "$RUNTIME_DIR"

LOCKDIR="$RUNTIME_DIR/.sync.lock"
if mkdir "$LOCKDIR" 2>/dev/null; then
  trap 'rmdir "$LOCKDIR"' EXIT INT TERM
else
  log "[SKIP] another run is in progress (lock: $LOCKDIR)"
  exit 0
fi

log "[RUN] cd $RUNTIME_DIR && ${SYNC_CMD}"
cd "$RUNTIME_DIR"
sh -c "${SYNC_CMD}"
log "[RUN] done."
