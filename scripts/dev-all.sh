#!/usr/bin/env bash
# Start backend + frontend in one terminal. Ctrl+C stops both.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cleanup() {
  jobs -p | xargs kill 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting backend on :8000 ..."
(cd "$ROOT/backend" && ./scripts/dev.sh) &

echo "Starting frontend on :5173 ..."
(cd "$ROOT/frontend" && ./scripts/dev.sh) &

echo ""
echo "  Frontend: http://127.0.0.1:5173"
echo "  Backend:  http://127.0.0.1:8000"
echo "  Press Ctrl+C to stop both."
echo ""

wait
