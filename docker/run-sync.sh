#!/usr/bin/env bash
set -euo pipefail

RUNTIME_DIR="${RUNTIME_DIR:-/config}"
mkdir -p "$RUNTIME_DIR"

echo "[RUN] $(date -Iseconds) → cd $RUNTIME_DIR && ${SYNC_CMD}"
cd "$RUNTIME_DIR"
sh -c "${SYNC_CMD}"
echo "[RUN] done."
