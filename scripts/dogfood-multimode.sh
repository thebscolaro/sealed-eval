#!/usr/bin/env bash
# Multi-mode fixture dogfood (contract + invariant + golden).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate

PORT="${SE_SUBJECT_PORT:-8089}"
SUITE="orders-multimode"
rm -rf "sealed/${SUITE}"
uvicorn app:app --app-dir subject-demo --port "$PORT" --log-level warning &
PID=$!
cleanup() { kill "$PID" 2>/dev/null || true; }
trap cleanup EXIT
for _ in $(seq 1 50); do curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null && break; sleep 0.05; done
TOKEN="$(sealed-eval new-token)"
sealed-eval propose "$SUITE" --fixture orders-multimode
sealed-eval seal "$SUITE" "$TOKEN" >/dev/null
sealed-eval grade "$SUITE" "http://127.0.0.1:${PORT}" "$TOKEN"
sealed-eval scorecard "$SUITE" >/dev/null
echo "dogfood-multimode: OK"
