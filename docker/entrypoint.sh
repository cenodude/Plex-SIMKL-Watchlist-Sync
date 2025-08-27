#!/usr/bin/env bash
set -euo pipefail

log(){ echo "[$(date -Iseconds)] $*"; }

# Defaults
: "${TZ:=Europe/Amsterdam}"
: "${RUNTIME_DIR:=/config}"
: "${CRON_SCHEDULE:=0 * * * *}"   # empty = run once
: "${PUID:=1000}"
: "${PGID:=1000}"
: "${SYNC_CMD:=python /app/plex_simkl_watchlist_sync.py --sync}"
: "${INIT_CMD:=python /app/plex_simkl_watchlist_sync.py --init-simkl redirect --bind 0.0.0.0:8787}"

mkdir -p "$RUNTIME_DIR" /var/log
touch /var/log/cron.log

# Timezone
if [ -f "/usr/share/zoneinfo/${TZ}" ]; then
  ln -snf "/usr/share/zoneinfo/${TZ}" /etc/localtime && echo "${TZ}" > /etc/timezone
fi

# User/group
getent group "${PGID}" >/dev/null 2>&1 || groupadd -g "${PGID}" appgroup || true
id -u "${PUID}"    >/dev/null 2>&1 || useradd -u "${PUID}" -g "${PGID}" -M -s /usr/sbin/nologin appuser || true
chown -R "${PUID}:${PGID}" "$RUNTIME_DIR" /var/log/cron.log

# --- CONFIG BOOTSTRAP ---
# If /config/config.json is missing, copy example
if [ ! -f "$RUNTIME_DIR/config.json" ] && [ -f "/app/config.example.json" ]; then
  cp /app/config.example.json "$RUNTIME_DIR/config.json"
  chown "${PUID}:${PGID}" "$RUNTIME_DIR/config.json"
  log "[ENTRYPOINT] Created $RUNTIME_DIR/config.json from template"
fi

# Always symlink into /app for the script
ln -sf "$RUNTIME_DIR/config.json" /app/config.json
log "[ENTRYPOINT] Linked $RUNTIME_DIR/config.json -> /app/config.json"

# --- FIRST-RUN / OAUTH CHECK ---
if python - <<'PY'
import json,sys
try:
    cfg=json.load(open('/app/config.json'))
    tok=cfg.get("simkl",{}).get("access_token")
    sys.exit(0 if tok else 1)
except Exception:
    sys.exit(1)
PY
then
  log "[ENTRYPOINT] SIMKL access_token found → continue normal run"
else
  log "[INIT] No SIMKL access_token; starting OAuth flow"
  log "[INIT] Map port 8787 on first run (-p 8787:8787)"
  cd "$RUNTIME_DIR"
  exec gosu appuser sh -lc "${INIT_CMD} && echo '[INIT] Done. Restart container to start normal syncs.'"
fi
# --- END FIRST-RUN / OAUTH CHECK ---

# Run-once mode
if [ -z "${CRON_SCHEDULE}" ]; then
  log "[ENTRYPOINT] Run once"
  exec gosu appuser /usr/local/bin/run-sync.sh
fi

# Cron mode
echo "${CRON_SCHEDULE} gosu appuser /usr/local/bin/run-sync.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/plex-simkl
chmod 0644 /etc/cron.d/plex-simkl
crontab /etc/cron.d/plex-simkl
log "[ENTRYPOINT] Cron scheduled: ${CRON_SCHEDULE}"
exec cron -f
