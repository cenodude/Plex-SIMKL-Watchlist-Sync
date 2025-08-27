#!/usr/bin/env bash
set -euo pipefail

log(){ echo "[$(date -Iseconds)] $*"; }

# Defaults
: "${TZ:=Europe/Amsterdam}"
: "${RUNTIME_DIR:=/config}"
: "${CRON_SCHEDULE:=0 * * * *}"   # leeg = run-once
: "${PUID:=1000}"
: "${PGID:=1000}"
: "${SYNC_CMD:=python /app/plex_simkl_watchlist_sync.py --sync}"

mkdir -p "$RUNTIME_DIR" /var/log
touch /var/log/cron.log

# Timezone
if [ -f "/usr/share/zoneinfo/${TZ}" ]; then
  ln -snf "/usr/share/zoneinfo/${TZ}" /etc/localtime && echo "${TZ}" > /etc/timezone
fi

# Drop privileges user/group
if ! getent group "${PGID}" >/dev/null 2>&1; then
  groupadd -g "${PGID}" appgroup || true
fi
if ! id -u "${PUID}" >/dev/null 2>&1; then
  useradd -u "${PUID}" -g "${PGID}" -M -s /usr/sbin/nologin appuser || true
fi
chown -R "${PUID}:${PGID}" "$RUNTIME_DIR" /var/log/cron.log

# Helper die één sync uitvoert
cat >/usr/local/bin/run-sync.sh <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
log(){ echo "[$(date -Iseconds)] $*"; }
: "${RUNTIME_DIR:=/config}"
: "${SYNC_CMD:=python /app/plex_simkl_watchlist_sync.py --sync}"
mkdir -p "$RUNTIME_DIR"
log "[RUN] cd $RUNTIME_DIR && ${SYNC_CMD}"
cd "$RUNTIME_DIR"
sh -c "${SYNC_CMD}"
log "[RUN] done."
EOS
chmod +x /usr/local/bin/run-sync.sh

# Run-once modus als CRON_SCHEDULE leeg is
if [ -z "${CRON_SCHEDULE}" ]; then
  log "[ENTRYPOINT] CRON_SCHEDULE leeg → éénmalig draaien."
  exec gosu appuser /usr/local/bin/run-sync.sh
fi

# Cron job installeren
echo "${CRON_SCHEDULE} gosu appuser /usr/local/bin/run-sync.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/plex-simkl
chmod 0644 /etc/cron.d/plex-simkl
crontab /etc/cron.d/plex-simkl
log "[ENTRYPOINT] Cron gepland: ${CRON_SCHEDULE}"
exec cron -f