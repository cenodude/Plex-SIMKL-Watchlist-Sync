#!/usr/bin/env bash
set -euo pipefail

# ---------- tiny logger ----------
log() {
  echo "[$(date -Iseconds)] $*"
}

# ---------- defaults ----------
: "${TZ:=Europe/Amsterdam}"
: "${RUNTIME_DIR:=/config}"
: "${CRON_SCHEDULE:=0 * * * *}"   # empty => run once
: "${INIT_TIMEOUT:=600}"          # seconds to wait for OAuth success
: "${PUID:=1000}"
: "${PGID:=1000}"

# Auto-detect container IP:port if BIND_ADDR not provided
if [ -z "${BIND_ADDR:-}" ]; then
  ip="$(hostname -i | awk '{print $1}')"
  BIND_ADDR="${ip}:8787"
fi

# ---------- timezone ----------
ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime
echo "$TZ" > /etc/timezone

# ---------- user/group (LinuxServer-style) ----------
if ! getent group appgroup >/dev/null 2>&1; then
  groupadd -g "$PGID" appgroup
fi
if ! id -u appuser >/dev/null 2>&1; then
  useradd -u "$PUID" -g "$PGID" -s /bin/bash -m appuser
fi

mkdir -p "$RUNTIME_DIR"
chown -R "$PUID:$PGID" "$RUNTIME_DIR"

CFG="$RUNTIME_DIR/config.json"
export CFG

# ---------- ensure minimal config.json ----------
if [ ! -f "$CFG" ]; then
  cat >"$CFG" <<'JSON'
{
  "plex": { "account_token": "" },
  "simkl": {
    "client_id": "",
    "client_secret": "",
    "access_token": "",
    "refresh_token": "",
    "token_expires_at": 0
  },
  "sync": {
    "enable_add": true,
    "enable_remove": true,
    "bidirectional": { "enabled": true, "mode": "two-way", "source_of_truth": "plex" },
    "activity": { "use_activity": true, "types": ["watchlist"] }
  },
  "runtime": { "debug": false }
}
JSON
  chown "$PUID:$PGID" "$CFG"
  log "[ENTRYPOINT] Created default config at $CFG"
fi

# ---------- prefill from env (optional) ----------
python - <<'PY' || true
import json, os
p=os.environ["CFG"]
with open(p,"r",encoding="utf-8") as f: cfg=json.load(f)
simkl=cfg.get("simkl") or {}; plex=cfg.get("plex") or {}
cid=os.environ.get("SIMKL_CLIENT_ID","").strip()
csec=os.environ.get("SIMKL_CLIENT_SECRET","").strip()
ptok=os.environ.get("PLEX_TOKEN","").strip()
changed=False
if cid and not simkl.get("client_id"): simkl["client_id"]=cid; changed=True
if csec and not simkl.get("client_secret"): simkl["client_secret"]=csec; changed=True
if ptok and not plex.get("account_token"): plex["account_token"]=ptok; changed=True
cfg["simkl"]=simkl; cfg["plex"]=plex
if changed:
    with open(p,"w",encoding="utf-8") as f: json.dump(cfg,f,indent=2)
PY

# ---------- check SIMKL status ----------
simkl_status="$(python - <<'PY'
import json, os
p=os.environ["CFG"]
try:
    d=json.load(open(p,"r",encoding="utf-8"))
    s=d.get("simkl") or {}
    ok=bool(s.get("client_id") and s.get("client_secret") and s.get("access_token"))
    print("OK" if ok else "NEEDS_INIT")
except Exception:
    print("NEEDS_INIT")
PY
)"

# ---------- OAuth init if needed ----------
if [ "$simkl_status" = "NEEDS_INIT" ]; then
  log "[ENTRYPOINT] SIMKL tokens missing → starting OAuth helper on ${BIND_ADDR}"

  container_ip="${BIND_ADDR%:*}"; container_port="${BIND_ADDR##*:}"
  if [ "$container_ip" = "0.0.0.0" ] || [ "$container_ip" = "::" ]; then
    container_ip="$(hostname -i | awk '{print $1}')"
  fi
  log "Callback (container internal):  http://${container_ip}:${container_port}/callback"
  log "If published (-p ${container_port}:${container_port}), open in your browser:"
  log "  http://<docker-host-ip>:${container_port}/callback"
  log "Make sure this exact URL is in your SIMKL Redirect URIs."

  # Run helper as appuser in background
  gosu appuser sh -c "python /app/plex_simkl_watchlist_sync.py --init-simkl redirect --bind ${BIND_ADDR}" &
  helper_pid=$!

  log "Waiting (timeout ${INIT_TIMEOUT}s) for tokens to appear in $CFG ..."
  secs=0; status="WAIT"
  while [ $secs -lt "$INIT_TIMEOUT" ]; do
    status="$(python - <<'PY'
import json, os
p=os.environ["CFG"]
try:
    d=json.load(open(p,"r",encoding="utf-8"))
    s=d.get("simkl") or {}
    print("OK" if s.get("access_token") else "WAIT")
except Exception:
    print("WAIT")
PY
)"
    if [ "$status" = "OK" ]; then
      log "SIMKL tokens detected. OAuth init complete."
      break
    fi
    sleep 2; secs=$((secs+2))
  done

  if ps -p $helper_pid >/dev/null 2>&1; then
    kill $helper_pid || true
  fi

  if [ "$status" != "OK" ]; then
    log "[ENTRYPOINT] ERROR: OAuth init timed out after ${INIT_TIMEOUT}s."
    log "Check logs and Redirect URI configuration."
    exit 1
  fi
fi

# ---------- run-once mode ----------
if [ -z "${CRON_SCHEDULE}" ]; then
  log "[ENTRYPOINT] CRON_SCHEDULE empty → running once."
  exec gosu appuser /usr/local/bin/run-sync.sh
fi

# ---------- cron setup ----------
echo "${CRON_SCHEDULE} gosu appuser /usr/local/bin/run-sync.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/plex-simkl
chmod 0644 /etc/cron.d/plex-simkl
crontab /etc/cron.d/plex-simkl

log "[ENTRYPOINT] Cron scheduled: ${CRON_SCHEDULE}"
exec cron -f
