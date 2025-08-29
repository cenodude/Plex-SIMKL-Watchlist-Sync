# ./Dockerfile
FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends cron tzdata \
 && rm -rf /var/lib/apt/lists/*

# Python runtime flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY plex_simkl_watchlist_sync.py /app/
COPY config.example.json /app/
COPY plex_token_helper.py /app/

# Python deps
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir plexapi requests

# Scripts
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY docker/run-sync.sh   /usr/local/bin/run-sync.sh
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/run-sync.sh \
 && touch /var/log/cron.log

# Runtime env
ENV TZ="Europe/Amsterdam" \
    RUNTIME_DIR="/config" \
    CRON_SCHEDULE="0 0 * * *" \
    PUID="1000" \
    PGID="1000" \
    SYNC_CMD="python /app/plex_simkl_watchlist_sync.py --sync" \
    INIT_CMD="python /app/plex_simkl_watchlist_sync.py --init-simkl redirect --bind 0.0.0.0:8787"

# First-run OAuth env
ENV PLEX_ACCOUNT_TOKEN="" \
    SIMKL_CLIENT_ID="" \
    SIMKL_CLIENT_SECRET=""

EXPOSE 8787

# Persist config/state
VOLUME ["/config"]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["cron", "-f"]
