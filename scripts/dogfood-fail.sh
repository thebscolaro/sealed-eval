#!/usr/bin/env bash
# Dogfood: seal against healthy app, then grade with subject down -> expect exit 1
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/sealed-eval ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -e ".[dev]" -q
fi
# shellcheck disable=SC1091
source .venv/bin/activate

PORT="${SE_SUBJECT_PORT:-8081}"
SUITE="${SE_SUITE:-orders-fail}"
pkill -f "uvicorn app:app --app-dir subject-demo --port ${PORT}" 2>/dev/null || true
rm -rf "sealed/${SUITE}"

uvicorn app:app --app-dir subject-demo --port "$PORT" --log-level warning &
PID=$!

for _ in $(seq 1 50); do
  if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null; then
    break
  fi
  sleep 0.05
done

TOKEN="$(sealed-eval new-token)"
sealed-eval propose "$SUITE" --fixture orders
sealed-eval seal "$SUITE" "$TOKEN" >/dev/null

# Break: stop the subject so contract checks cannot connect
kill "$PID" 2>/dev/null || true
wait "$PID" 2>/dev/null || true
sleep 0.2

set +e
sealed-eval grade "$SUITE" "http://127.0.0.1:${PORT}" "$TOKEN"
EC=$?
set -e
if [[ "$EC" -eq 0 ]]; then
  echo "dogfood-fail: expected non-zero exit, got 0" >&2
  exit 1
fi
echo "dogfood-fail: OK (grade failed as expected, exit=$EC)"
