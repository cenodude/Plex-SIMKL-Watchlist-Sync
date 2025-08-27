#!/usr/bin/env bash
set -euo pipefail
log(){ echo "[$(date -Iseconds)] $*"; }

: "${TZ:=Europe/Amsterdam}"
: "${RUNTIME_DIR:=/config}"
: "${CRON_SCHEDULE:=0 * * * *}"   # empty = run once
: "${PUID:=1000}"
: "${PGID:=1000}"
: "${SYNC_CMD:=python /app/plex_simkl_watchlist_sync.py --sync}"
: "${INIT_CMD:=python /app/plex_simkl_watchlist_sync.py --init-simkl redirect --bind 0.0.0.0:8787}"

mkdir -p "$RUNTIME_DIR" /var/log
touch /var/log/cron.log

if [ -f "/usr/share/zoneinfo/${TZ}" ]; then
  ln -snf "/usr/share/zoneinfo/${TZ}" /etc/localtime && echo "${TZ}" > /etc/timezone
fi

getent group "${PGID}" >/dev/null 2>&1 || groupadd -g "${PGID}" appgroup || true
id -u "${PUID}" >/dev/null 2>&1 || useradd -u "${PUID}" -g "${PGID}" -M -s /usr/sbin/nologin appuser || true
chown -R "${PUID}:${PGID}" "$RUNTIME_DIR" /var/log/cron.log

if [ ! -f "$RUNTIME_DIR/config.yml" ]; then
  log "[INIT] No config.yml in ${RUNTIME_DIR}"
  log "[INIT] Map port 8787 on first run (-p 8787:8787)"
  cd "$RUNTIME_DIR"
  exec gosu appuser sh -lc "${INIT_CMD} && echo '[INIT] Done. Restart to start normal syncs.'"
fi

cat >/usr/local/bin/run-sync.sh <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
log(){ echo "[$(date -Iseconds)] $*"; }
: "${RUNTIME_DIR:=/config}"
: "${SYNC_CMD:=python /app/plex_simkl_watchlist_sync.py --sync}"
: "${PATH:=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin}"
mkdir -p "$RUNTIME_DIR"
LOCKDIR="$RUNTIME_DIR/.sync.lock"
if mkdir "$LOCKDIR" 2>/dev/null; then trap 'rmdir "$LOCKDIR"' EXIT INT TERM; else log "[SKIP] another run in progress"; exit 0; fi
log "[RUN] cd $RUNTIME_DIR && ${SYNC_CMD}"
cd "$RUNTIME_DIR"
sh -c "${SYNC_CMD}"
log "[RUN] done."
EOS
chmod +x /usr/local/bin/run-sync.sh
chown "${PUID}:${PGID}" /usr/local/bin/run-sync.sh

if [ -z "${CRON_SCHEDULE}" ]; then
  log "[ENTRYPOINT] Run once"
  exec gosu appuser /usr/local/bin/run-sync.sh
fi

echo "${CRON_SCHEDULE} gosu appuser /usr/local/bin/run-sync.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/plex-simkl
chmod 0644 /etc/cron.d/plex-simkl
crontab /etc/cron.d/plex-simkl
log "[ENTRYPOINT] Cron scheduled: ${CRON_SCHEDULE}"
exec cron -f
