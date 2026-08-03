#!/usr/bin/env bash
# Install SEALed-eval Cursor plugin into ~/.cursor/plugins/local for local proof.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/distribution/cursor-plugin"
DEST="${HOME}/.cursor/plugins/local/sealed-eval"

if [[ ! -f "$SRC/.cursor-plugin/plugin.json" ]]; then
  echo "install-cursor-plugin-local: missing $SRC/.cursor-plugin/plugin.json" >&2
  exit 1
fi

mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
# Copy plugin tree (skills + manifest). Prefer rsync when available.
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete "$SRC/" "$DEST/"
else
  cp -R "$SRC" "$DEST"
fi

echo "install-cursor-plugin-local: OK → $DEST"
echo "Reload Cursor window (Developer: Reload Window) to pick up skills."
python3 - <<'PY'
import json
from pathlib import Path
p = Path.home() / ".cursor/plugins/local/sealed-eval/.cursor-plugin/plugin.json"
print(json.dumps(json.loads(p.read_text()), indent=2))
skills = sorted((Path.home() / ".cursor/plugins/local/sealed-eval/skills").iterdir())
print("skills:", [s.name for s in skills if s.is_dir()])
PY
