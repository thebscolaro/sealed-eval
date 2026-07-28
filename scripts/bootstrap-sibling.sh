#!/usr/bin/env bash
# Create a sibling *-sealed-eval control plane next to a subject app.
# Usage: ./scripts/bootstrap-sibling.sh /path/to/subject [repo-name]
set -euo pipefail
SUBJECT="$(cd "${1:?subject path required}" && pwd)"
NAME="${2:-$(basename "$SUBJECT")-sealed-eval}"
PARENT="$(dirname "$SUBJECT")"
DEST="$PARENT/$NAME"
SE_SRC="$(cd "$(dirname "$0")/.." && pwd)"

if [[ -e "$DEST" ]]; then
  echo "bootstrap-sibling: $DEST already exists" >&2
  exit 1
fi

echo "bootstrap-sibling: copying SE template → $DEST"
mkdir -p "$DEST"
# Lightweight control plane: package + fixtures + scripts + skills (not full .git history)
rsync -a --exclude '.venv' --exclude '.git' --exclude 'sealed/*/' --exclude '.pytest_cache' \
  --exclude 'docs/*.drawio.png' \
  "$SE_SRC/" "$DEST/"
# keep diagrams sources; pngs optional
rsync -a "$SE_SRC/docs/"*.drawio "$DEST/docs/" 2>/dev/null || true
rsync -a "$SE_SRC/docs/"*.drawio.png "$DEST/docs/" 2>/dev/null || true

cd "$DEST"
rm -rf .git
git init -q
git add -A
git commit -qm "Bootstrap sealed-eval control plane for $(basename "$SUBJECT")."

./scripts/bootstrap.sh

if command -v gh >/dev/null 2>&1; then
  OWNER="$(gh api user -q .login 2>/dev/null || true)"
  if [[ -n "$OWNER" ]]; then
    gh repo create "$OWNER/$NAME" --private --source=. --remote=origin --push \
      --description "SEALed-eval control plane for $(basename "$SUBJECT")" \
      || echo "bootstrap-sibling: gh repo create failed (create manually: gh repo create $OWNER/$NAME --private --source=. --push)"
  else
    echo "bootstrap-sibling: gh not logged in; create repo manually when ready"
  fi
fi

POINTER="$SUBJECT/SEALED_EVAL.md"
cat > "$POINTER" <<EOF
# SEALed-eval

This subject is graded by a **sibling** control plane (not this repo).

- Control plane path: \`$DEST\`
- Coders: read public task + scorecard only — never seal tokens

Operator loop: see control plane \`docs/RUNBOOK.md\`.
EOF

echo "bootstrap-sibling: wrote $POINTER"
echo "bootstrap-sibling: OK → $DEST"
