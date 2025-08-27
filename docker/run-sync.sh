#!/usr/bin/env bash
set -euo pipefail

# tiny logger
log() {
  echo "[$(date -Iseconds)] $*"
}

RUNTIME_DIR="${RUNTIME_DIR:-/config}"
mkdir -p "$RUNTIME_DIR"

log "[RUN] cd $RUNTIME_DIR && ${SYNC_CMD}"
cd "$RUNTIME_DIR"
sh -c "${SYNC_CMD}"
log "[RUN] done."

