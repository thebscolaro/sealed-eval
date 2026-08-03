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

## Sandbox (project CLI config)

[`.cursor/cli.json`](../.cursor/cli.json) enables Cursor CLI sandbox for this repo with localhost + GitHub allowlisted. Project overrides apply to Cursor CLI agent sessions in this tree; they do not rewrite `~/.cursor/cli-config.json`.

Grade itself is still the harness CLI (`sealed-eval grade …`). Sandbox wraps **agent** shell/network in CLI sessions that call that harness — not a second grader.

Project config is committed. Headless proof command (needs `agent login` or `CURSOR_API_KEY`):

```bash
cd ~/code/qa-automation-lab-se-sealed-eval
agent --sandbox enabled --workspace "$PWD" -p --force \
  'source .venv/bin/activate && sealed-eval scorecard lab'
```

This session could not complete that headless run (CLI auth missing). Local plugin install **did** complete; sandbox is enabled via project `.cursor/cli.json` + `--sandbox enabled` flag for when CLI auth is available.

## Relation to fullstack dogfood

End-to-end HTTP+UI grade: [dogfood-fullstack.md](dogfood-fullstack.md).  
Sibling vs plugin vs sandbox mental model: [RUNBOOK.md](RUNBOOK.md).
