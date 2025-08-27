#!/usr/bin/env bash
set -euo pipefail

# Set timezone
if [ -n "${TZ:-}" ]; then
  ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime
  echo "$TZ" > /etc/timezone
fi

# Create user/group according to PUID/PGID
if ! getent group appgroup >/dev/null; then
  groupadd -g "$PGID" appgroup
fi
if ! id -u appuser >/dev/null 2>&1; then
  useradd -u "$PUID" -g "$PGID" -s /bin/bash -m appuser
fi

# Fix ownership of /config
chown -R "$PUID":"$PGID" /config

# If no CRON_SCHEDULE → run once and keep container alive
if [ -z "${CRON_SCHEDULE:-}" ]; then
  echo "[ENTRYPOINT] CRON_SCHEDULE empty → run once."
  gosu appuser /usr/local/bin/run-sync.sh
  exec tail -f /dev/null
fi

# Setup cron job 
echo "${CRON_SCHEDULE} gosu appuser /usr/local/bin/run-sync.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/plex-simkl
chmod 0644 /etc/cron.d/plex-simkl
crontab /etc/cron.d/plex-simkl

echo "[ENTRYPOINT] Cron scheduled: ${CRON_SCHEDULE}"
exec "$@"
