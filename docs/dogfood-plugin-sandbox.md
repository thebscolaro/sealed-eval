# Plugin + sandbox dogfood (2026-08-03)

## Local plugin install (proven)

```bash
./scripts/install-cursor-plugin-local.sh
# → ~/.cursor/plugins/local/sealed-eval
# Reload Cursor window
```

Manifest: [`distribution/cursor-plugin/.cursor-plugin/plugin.json`](../distribution/cursor-plugin/.cursor-plugin/plugin.json)  
Skills: `sealed-eval-operator`, `sealed-eval-coder`, `sealed-eval-setup`

This is the documented **pre-marketplace** path from Cursor plugin docs. Official marketplace listing still needs a human submit at https://cursor.com/marketplace/publish (repo: `thebscolaro/sealed-eval`, plugin root `distribution/cursor-plugin/`).

## Sandbox (CLI flag)

Project `.cursor/cli.json` sandbox keys are **not** accepted by current Cursor schema — use the agent flag:

```bash
cd ~/code/qa-automation-lab-se-sealed-eval
agent --sandbox enabled --workspace "$PWD" -p --force \
  'source .venv/bin/activate && sealed-eval scorecard lab'
```

**Proven 2026-08-03** after `agent login`: scorecard `gate: pass` (http+ui) under `--sandbox enabled`.

## Relation to fullstack dogfood

End-to-end HTTP+UI grade: [dogfood-fullstack.md](dogfood-fullstack.md).  
Sibling vs plugin vs sandbox mental model: [RUNBOOK.md](RUNBOOK.md).
