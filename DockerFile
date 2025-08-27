# ./Dockerfile
FROM python:3.12-slim

# Install cron, timezone data, and gosu
RUN apt-get update \
 && apt-get install -y --no-install-recommends cron tzdata gosu \
 && rm -rf /var/lib/apt/lists/*

# Working directory for your app code
WORKDIR /app
COPY . /app

# Install Python dependencies for your script
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir plexapi requests

# Copy helper scripts
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY docker/run-sync.sh   /usr/local/bin/run-sync.sh
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/run-sync.sh \
 && touch /var/log/cron.log

# Default environment variables (override at runtime)
ENV TZ="Europe/Amsterdam" \
    CRON_SCHEDULE="0 * * * *" \
    SYNC_CMD="python /app/plex_simkl_watchlist_sync.py --sync" \
    RUNTIME_DIR="/config" \
    PUID="1000" \
    PGID="1000"

# Persist config/state
VOLUME ["/config"]

# Start via entrypoint; cron stays in foreground
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["cron", "-f"]
