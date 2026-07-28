#!/usr/bin/env bash
# Optional: share named secrets between subject and SE control plane via ownlock team bundle.
set -euo pipefail
SUBJECT="${1:-}"
SE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "$SUBJECT" ]]; then
  echo "usage: $0 /path/to/subject-repo [KEY...]" >&2
  exit 1
fi
shift || true
KEYS=("$@")
if [[ ${#KEYS[@]} -eq 0 ]]; then
  KEYS=(SEAL_TOKEN DATABASE_URL)
fi

cd "$SE_ROOT"
if ! command -v ownlock >/dev/null 2>&1; then
  echo "ownlock required" >&2
  exit 1
fi
ownlock share "${KEYS[@]}" --team
echo "Wrote $SE_ROOT/.ownlock/team.olbundle — copy to subject and run: ownlock import-share .ownlock/team.olbundle"
echo "Subject path noted: $SUBJECT"
