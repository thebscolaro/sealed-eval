#!/usr/bin/env bash
# UI check mode dogfood (requires [ui] + chromium).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate
if ! python -c "import playwright" 2>/dev/null; then
  pip install -e ".[ui]" -q
  playwright install chromium
fi
PORT="${SE_SUBJECT_PORT:-8091}"
SUITE="ui-demo"
rm -rf "sealed/${SUITE}"
uvicorn app:app --app-dir subject-demo --port "$PORT" --log-level warning &
PID=$!
cleanup() { kill "$PID" 2>/dev/null || true; }
trap cleanup EXIT
for _ in $(seq 1 50); do curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null && break; sleep 0.05; done
TOKEN="$(sealed-eval new-token)"
cat > /tmp/se-ui.json <<EOF
{
  "task_card": {"id": "$SUITE", "title": "ui", "summary": "ui", "public_acceptance": ["Orders page"]},
  "cases": [{
    "id": "home",
    "check": "ui",
    "bucket": "ui",
    "request": {"path": "/"},
    "expect": {"text": "Orders", "selector": "#status", "selector_text": "demo ready"},
    "visible": true
  }]
}
EOF
sealed-eval propose "$SUITE" --import-path /tmp/se-ui.json
sealed-eval seal "$SUITE" "$TOKEN" >/dev/null
sealed-eval grade "$SUITE" "http://127.0.0.1:${PORT}" "$TOKEN"
echo "dogfood-ui: OK"
