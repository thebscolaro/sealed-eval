#!/usr/bin/env bash
# Dogfood: OwnAuth Express dev API graded by SEALed-eval (separate sealed store).
# Grades the browser-dev HTTP surface only — not the Tauri desktop app.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OWNAUTH="${OWNAUTH_ROOT:-$HOME/code/ownauth}"
cd "$ROOT"

if [[ ! -d "$OWNAUTH" ]]; then
  echo "dogfood-ownauth: OwnAuth not found at $OWNAUTH (set OWNAUTH_ROOT)" >&2
  exit 1
fi

if [[ ! -x .venv/bin/sealed-eval ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -e ".[dev]" -q
fi
# shellcheck disable=SC1091
source .venv/bin/activate

PORT="${SE_OWNAUTH_PORT:-3017}"
SUITE="${SE_SUITE:-ownauth-dev-api}"
TOKEN_VALUE="se-ownauth-dogfood"
DATA_DIR="$(mktemp -d /tmp/ownauth-se-XXXXXX)"

rm -rf "sealed/${SUITE}"
if curl -sf "http://127.0.0.1:${PORT}/api/health" >/dev/null 2>&1 \
  || curl -sf -H "Authorization: Bearer ${TOKEN_VALUE}" \
    "http://127.0.0.1:${PORT}/api/health" >/dev/null 2>&1; then
  echo "dogfood-ownauth: port ${PORT} already in use; set SE_OWNAUTH_PORT" >&2
  exit 1
fi

cleanup() {
  if [[ -n "${PID:-}" ]]; then
    kill "$PID" 2>/dev/null || true
  fi
  rm -rf "$DATA_DIR"
}
trap cleanup EXIT

(
  cd "$OWNAUTH"
  OWNAUTH_DEV_MODE=1 \
  OWNAUTH_DEV_API_TOKEN="$TOKEN_VALUE" \
  OWNAUTH_DATA_DIR="$DATA_DIR" \
  OWNAUTH_MASTER_KEY="se-dogfood-master-key-32b!!" \
  PORT="$PORT" \
  node src/server.js
) &
PID=$!

for _ in $(seq 1 80); do
  if curl -sf -H "Authorization: Bearer ${TOKEN_VALUE}" \
    "http://127.0.0.1:${PORT}/api/health" >/dev/null; then
    break
  fi
  sleep 0.05
done

if ! curl -sf -H "Authorization: Bearer ${TOKEN_VALUE}" \
  "http://127.0.0.1:${PORT}/api/health" >/dev/null; then
  echo "dogfood-ownauth: OwnAuth failed to become ready on :${PORT}" >&2
  exit 1
fi

SEAL="$(sealed-eval new-token)"
sealed-eval propose "$SUITE" --fixture ownauth
sealed-eval seal "$SUITE" "$SEAL" >/dev/null
sealed-eval publish "$SUITE" >/dev/null
echo "--- public task card (what a coder would see) ---"
sealed-eval publish "$SUITE"
echo "--- grade (sealed HTTP contracts vs running OwnAuth) ---"
set +e
sealed-eval grade "$SUITE" "http://127.0.0.1:${PORT}" "$SEAL"
EC=$?
set -e
if [[ "$EC" -ne 0 ]]; then
  echo "dogfood-ownauth: expected exit 0, got $EC" >&2
  exit 1
fi
echo "dogfood-ownauth: OK (OwnAuth Express API passed sealed contracts)"
