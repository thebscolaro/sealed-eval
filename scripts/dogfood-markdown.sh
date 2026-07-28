#!/usr/bin/env bash
# Dogfood: propose from markdown AC (health-only) -> expect grade exit 0
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/sealed-eval ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -e ".[dev]" -q
fi
# shellcheck disable=SC1091
source .venv/bin/activate

PORT="${SE_SUBJECT_PORT:-8082}"
SUITE="${SE_SUITE:-markdown-ac}"
pkill -f "uvicorn app:app --app-dir subject-demo --port ${PORT}" 2>/dev/null || true
rm -rf "sealed/${SUITE}"

uvicorn app:app --app-dir subject-demo --port "$PORT" --log-level warning &
PID=$!
cleanup() { kill "$PID" 2>/dev/null || true; }
trap cleanup EXIT

for _ in $(seq 1 50); do
  if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null; then
    break
  fi
  sleep 0.05
done

TOKEN="$(sealed-eval new-token)"
sealed-eval propose "$SUITE" --title "Markdown AC" --markdown-file fixtures/sample-ac.md
sealed-eval seal "$SUITE" "$TOKEN" >/dev/null
sealed-eval publish "$SUITE" >/dev/null
set +e
sealed-eval grade "$SUITE" "http://127.0.0.1:${PORT}" "$TOKEN"
EC=$?
set -e
if [[ "$EC" -ne 0 ]]; then
  echo "dogfood-markdown: expected exit 0, got $EC" >&2
  exit 1
fi
echo "dogfood-markdown: OK"
