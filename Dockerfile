# ./Dockerfile
FROM python:3.12-slim

# deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends cron tzdata gosu \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# python deps
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir plexapi requests

# scripts
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY docker/run-sync.sh   /usr/local/bin/run-sync.sh
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/run-sync.sh \
 && touch /var/log/cron.log

# runtime env (override at run time if needed)
ENV TZ="Europe/Amsterdam" \
    RUNTIME_DIR="/config" \
    CRON_SCHEDULE="0 * * * *" \
    PUID="1000" \
    PGID="1000" \
    SYNC_CMD="python /app/plex_simkl_watchlist_sync.py --sync" \
    INIT_CMD="python /app/plex_simkl_watchlist_sync.py --init-simkl redirect --bind 0.0.0.0:8787"

# first-run OAuth needs this
EXPOSE 8787

# persist config/state
VOLUME ["/config"]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["cron", "-f"]
