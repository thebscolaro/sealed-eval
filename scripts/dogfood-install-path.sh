#!/usr/bin/env bash
# Prove cold install path: propose → show-draft → seal → grade → coder scorecard.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/sealed-eval ]]; then
  ./scripts/bootstrap.sh
fi
# shellcheck disable=SC1091
source .venv/bin/activate

PORT="${SE_SUBJECT_PORT:-8088}"
SUITE="${SE_SUITE:-install-path-demo}"
rm -rf "sealed/${SUITE}"

pkill -f "uvicorn app:app --app-dir subject-demo --port ${PORT}" 2>/dev/null || true
uvicorn app:app --app-dir subject-demo --port "$PORT" --log-level warning &
PID=$!
cleanup() { kill "$PID" 2>/dev/null || true; }
trap cleanup EXIT

for _ in $(seq 1 50); do
  curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null && break
  sleep 0.05
done

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  set -a; source .env; set +a
fi

if command -v ownlock >/dev/null 2>&1 && grep -q 'vault(' .env 2>/dev/null; then
  TOKEN="$(ownlock run -- printenv SEAL_TOKEN)"
else
  TOKEN="${SEAL_TOKEN:-$(sealed-eval new-token)}"
fi

sealed-eval propose "$SUITE" --markdown-file fixtures/sample-ac.md --title "Install path"
echo "--- draft ---"
sealed-eval show-draft "$SUITE" | head -n 40
sealed-eval seal "$SUITE" "$TOKEN" >/dev/null
sealed-eval publish "$SUITE" >/dev/null
sealed-eval grade "$SUITE" "http://127.0.0.1:${PORT}" "$TOKEN"
echo "--- coder scorecard (no token) ---"
sealed-eval scorecard "$SUITE"
echo "dogfood-install-path: OK"
