#!/usr/bin/env bash
set -euo pipefail

log(){ echo "[$(date -Iseconds)] $*"; }

# ---------- Defaults ----------
: "${TZ:=Europe/Amsterdam}"
: "${RUNTIME_DIR:=/config}"
: "${CRON_SCHEDULE:=0 0 * * *}"   # empty = run once
: "${PUID:=1000}"
: "${PGID:=1000}"
: "${SYNC_CMD:=python /app/plex_simkl_watchlist_sync.py --sync}"
: "${INIT_CMD:=python /app/plex_simkl_watchlist_sync.py --init-simkl redirect --bind 0.0.0.0:8787}"
: "${LOCK_FILE:=/var/lock/plex-simkl.lock}"

# ---------- Sanity on PUID/PGID ----------
case "$PUID" in (*[!0-9]*|'') PUID=1000;; esac
case "$PGID" in (*[!0-9]*|'') PGID=1000;; esac

# ---------- FS prep ----------
mkdir -p "$RUNTIME_DIR" /var/log /var/lock
: > /var/log/cron.log

# ---------- Timezone ----------
if [ -f "/usr/share/zoneinfo/${TZ}" ]; then
  ln -snf "/usr/share/zoneinfo/${TZ}" /etc/localtime
  echo "${TZ}" > /etc/timezone
fi

# ---------- User/group ----------
if ! getent group "${PGID}" >/dev/null 2>&1; then
  groupadd -g "${PGID}" appgroup
fi
if ! id -u "${PUID}" >/dev/null 2>&1; then
  useradd -u "${PUID}" -g "${PGID}" -M -s /usr/sbin/nologin appuser
fi
chown -R "${PUID}:${PGID}" "$RUNTIME_DIR" /var/log/cron.log /var/lock

# ---------- CONFIG BOOTSTRAP ----------
if [ ! -f "$RUNTIME_DIR/config.json" ] && [ -f "/app/config.example.json" ]; then
  cp /app/config.example.json "$RUNTIME_DIR/config.json"
  chown "${PUID}:${PGID}" "$RUNTIME_DIR/config.json"
  log "[ENTRYPOINT] Created $RUNTIME_DIR/config.json from template"
fi

ln -sf "$RUNTIME_DIR/config.json" /app/config.json
log "[ENTRYPOINT] Linked $RUNTIME_DIR/config.json -> /app/config.json"

# Merge ENV config.json (safe if file missing/invalid)
python - <<'PY'
import json, os, sys
cfg_path = '/app/config.json'
try:
    with open(cfg_path,'r',encoding='utf-8') as f:
        cfg = json.load(f)
except Exception:
    cfg = {}

cfg.setdefault('plex', {})
cfg.setdefault('simkl', {})
updated = []

def set_if(env, path):
    v = os.getenv(env, '').strip()
    if not v: return
    d = cfg
    *parents, key = path.split('.')
    for p in parents:
        d = d.setdefault(p, {})
    d[key] = v
    updated.append(path)

set_if('PLEX_ACCOUNT_TOKEN', 'plex.account_token')
set_if('SIMKL_CLIENT_ID',     'simkl.client_id')
set_if('SIMKL_CLIENT_SECRET', 'simkl.client_secret')

if updated:
    with open(cfg_path,'w',encoding='utf-8') as f:
        json.dump(cfg,f,indent=2)
    print("[ENTRYPOINT] Applied ENV → config.json for: " + ", ".join(updated))
PY

# ---------- STATE FILE ----------
if [ ! -f "$RUNTIME_DIR/state.json" ]; then
  : > "$RUNTIME_DIR/state.json"
  chown "${PUID}:${PGID}" "$RUNTIME_DIR/state.json"
  log "[ENTRYPOINT] Created empty $RUNTIME_DIR/state.json"
fi
ln -sf "$RUNTIME_DIR/state.json" /app/state.json
log "[ENTRYPOINT] Linked $RUNTIME_DIR/state.json -> /app/state.json"

# ---------- FIRST-RUN / OAUTH CHECK ----------
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
    log "[INIT] Please edit ${RUNTIME_DIR}/config.json to include Plex token and SIMKL client credentials,"
    log "[INIT] then restart the container."
    log "[HINT] We created/linked: ${RUNTIME_DIR}/config.json → /app/config.json"
    log "[HINT] If you need a template, see /app/config.example.json"
    exit 0
  fi

  log "[INIT] No SIMKL access_token; starting OAuth flow"
  log "[INIT] Map port 8787 on first run (-p 8787:8787)"
  cd "$RUNTIME_DIR"
  exec su -s /bin/sh -c "${INIT_CMD} && echo '[INIT] Done. Restart container to start normal syncs.'" appuser
fi

# ---------- RUN-ONCE MODE ----------
if [ -z "${CRON_SCHEDULE}" ]; then
  log "[ENTRYPOINT] Run once"
  exec su -s /bin/sh -c "flock -n ${LOCK_FILE} -c '/usr/local/bin/run-sync.sh'" appuser
fi

# ---------- CRON MODE ----------
# Prepare cron.d file with PATH/SHELL and user field 
{
  echo 'SHELL=/bin/sh'
  echo 'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
  # flock to avoid overlaps if job runs longer than schedule
  echo "${CRON_SCHEDULE} appuser flock -n ${LOCK_FILE} -c '/usr/local/bin/run-sync.sh' >> /var/log/cron.log 2>&1"
} > /etc/cron.d/plex-simkl

chmod 0644 /etc/cron.d/plex-simkl

log "[ENTRYPOINT] Cron scheduled: ${CRON_SCHEDULE}"
exec cron -f
