#!/usr/bin/env bash
# Cold-start bootstrap for SEALed-eval control plane.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -e ".[dev]" -q

if command -v ownlock >/dev/null 2>&1; then
  if [[ ! -d .ownlock ]]; then
    ownlock init --yes 2>/dev/null || ownlock init || true
  fi
  if [[ ! -f .env ]]; then
    TOKEN="$(sealed-eval new-token)"
    # Prefer vault refs when ownlock can store the token non-interactively.
    if ownlock set SEAL_TOKEN="$TOKEN" --yes 2>/dev/null || ownlock set SEAL_TOKEN="$TOKEN" 2>/dev/null; then
      printf 'SEAL_TOKEN=vault("SEAL_TOKEN")\n' > .env
      echo "bootstrap: SEAL_TOKEN stored in ownlock; .env uses vault()"
    else
      printf 'SEAL_TOKEN=%s\n' "$TOKEN" > .env
      echo "bootstrap: wrote plaintext SEAL_TOKEN to .env (ownlock set failed; rotate later)"
    fi
  fi
else
  if [[ ! -f .env ]]; then
    TOKEN="$(sealed-eval new-token)"
    printf 'SEAL_TOKEN=%s\n' "$TOKEN" > .env
    echo "bootstrap: ownlock missing; wrote .env with SEAL_TOKEN (install ownlock for vault)"
  fi
fi

sealed-eval capabilities
echo "bootstrap: OK — run ./scripts/dogfood-install-path.sh next"
