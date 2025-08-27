#!/usr/bin/env bash
set -euo pipefail

log(){ echo "[$(date -Iseconds)] $*"; }

# Defaults
: "${TZ:=Europe/Amsterdam}"
: "${RUNTIME_DIR:=/config}"
: "${CRON_SCHEDULE:=0 0 * * *}"   # empty = run once
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

python - <<'PY'
import json, os, sys
cfg_path = '/app/config.json'
try:
    with open(cfg_path,'r',encoding='utf-8') as f:
        cfg = json.load(f)
except Exception:
    cfg = {}

# Ensure structure
cfg.setdefault('plex', {})
cfg.setdefault('simkl', {})
updated = []

plex_token = os.getenv('PLEX_ACCOUNT_TOKEN','').strip()
simkl_id   = os.getenv('SIMKL_CLIENT_ID','').strip()
simkl_sec  = os.getenv('SIMKL_CLIENT_SECRET','').strip()

if plex_token:
    cfg['plex']['account_token'] = plex_token
    updated.append('plex.account_token')
if simkl_id:
    cfg['simkl']['client_id'] = simkl_id
    updated.append('simkl.client_id')
if simkl_sec:
    cfg['simkl']['client_secret'] = simkl_sec
    updated.append('simkl.client_secret')

if updated:
    with open(cfg_path,'w',encoding='utf-8') as f:
        json.dump(cfg,f,indent=2)
    print("[ENTRYPOINT] Applied ENV → config.json for: " + ", ".join(updated))
PY
# --- END ENV overrides ---


# --- STATE FILE BOOTSTRAP ---
if [ ! -f "$RUNTIME_DIR/state.json" ]; then
  touch "$RUNTIME_DIR/state.json"
  chown "${PUID}:${PGID}" "$RUNTIME_DIR/state.json"
  log "[ENTRYPOINT] Created empty $RUNTIME_DIR/state.json"
fi

ln -sf "$RUNTIME_DIR/state.json" /app/state.json
log "[ENTRYPOINT] Linked $RUNTIME_DIR/state.json -> /app/state.json"

# --- FIRST-RUN / OAUTH CHECK ---
# Decide what to do based on config contents
# 1) If SIMKL access_token is present -> normal run
# 2) If SIMKL access_token is missing but required creds (Plex token + SIMKL client+secret) are missing,
#    print a clear instruction and exit so the user can fill config.json and restart.
# 3) Otherwise (creds present, no access_token) -> start OAuth helper.

# Helper to read which fields are missing (does not fail the script)
MISSING_FIELDS="$(python - <<'PY'
import json,sys
path = '/app/config.json'
missing = []
try:
    with open(path,'r',encoding='utf-8') as f:
        cfg = json.load(f)
except Exception:
    print('config.json:unreadable')
    sys.exit(0)

if not (cfg.get('plex') or {}).get('account_token'):
    missing.append('plex.account_token')
if not (cfg.get('simkl') or {}).get('client_id'):
    missing.append('simkl.client_id')
if not (cfg.get('simkl') or {}).get('client_secret'):
    missing.append('simkl.client_secret')

print(' '.join(missing))
PY
)"

# Check access_token
if python - <<'PY'
import json,sys
try:
    cfg=json.load(open('/app/config.json','r',encoding='utf-8'))
    tok=cfg.get('simkl',{}).get('access_token')
    sys.exit(0 if tok else 1)
except Exception:
    sys.exit(1)
PY
then
  log "[ENTRYPOINT] SIMKL access_token found → continue normal run"
else
  if [ -n "${MISSING_FIELDS}" ]; then
    log "[INIT] No SIMKL access_token AND missing required credentials → not starting OAuth"
    log "[INIT] Missing: ${MISSING_FIELDS}"
    log "[INIT] Please edit ${RUNTIME_DIR}/config.json to include your Plex token and SIMKL client credentials,"
    log "[INIT] then restart the container."
    log "[HINT] We created/linked: ${RUNTIME_DIR}/config.json → /app/config.json"
    log "[HINT] If you need a template, see /app/config.example.json"
    exit 0
  fi

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
