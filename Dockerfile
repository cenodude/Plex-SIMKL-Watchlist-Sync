# ./Dockerfile
FROM python:3.12-slim

# Install dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends cron tzdata \
 && rm -rf /var/lib/apt/lists/*

# Python runtime flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy application files
COPY plex_simkl_watchlist_sync.py /app/
COPY config.example.json /app/
COPY plex_token_helper.py /app/
COPY webapp.py /app/
COPY _auth_helper.py /app/
COPY _FastAPI.py /app/
COPY _secheduling.py /app/
COPY _TMDB.py /app/
COPY _watchlist.py /app/

# Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir plexapi requests fastapi uvicorn pydantic pillow

# Copy scripts
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY docker/run-sync.sh /usr/local/bin/run-sync.sh

# Set executable permissions for scripts
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/run-sync.sh \
 && touch /var/log/cron.log

# Runtime environment variables
ENV TZ="Europe/Amsterdam" \
    RUNTIME_DIR="/config" \
    CRON_SCHEDULE="0 0 * * *" \
    PUID="1000" \
    PGID="1000" \
    SYNC_CMD="python /app/plex_simkl_watchlist_sync.py --sync" \
    INIT_CMD="python /app/plex_simkl_watchlist_sync.py --init-simkl redirect --bind 0.0.0.0:8787" \
    WEBINTERFACE="yes"

# First-run OAuth environment variables
ENV PLEX_ACCOUNT_TOKEN="" \
    SIMKL_CLIENT_ID="" \
    SIMKL_CLIENT_SECRET=""

# Expose web interface port
EXPOSE 8787

# Persist config/state
VOLUME ["/config"]

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["cron", "-f"]
