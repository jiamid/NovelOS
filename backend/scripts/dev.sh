#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate

# Only watch app/ source; avoid reload on db/data changes.
# Set NOVELOS_RELOAD=0 to disable hot reload for maximum stability.
if [ "${NOVELOS_RELOAD:-1}" = "1" ]; then
  exec uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --reload \
    --reload-dir app
else
  exec uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8000
fi
