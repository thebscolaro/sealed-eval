# SEALed-eval runbook

## Mental model

Skills tell agents **when** to call SE. The harness **seals and grades**. Markdown AC drafts cases; human seal makes them authoritative; coder gets public task + aggregate scorecard only.

## Cold install

```bash
git clone https://github.com/thebscolaro/sealed-eval && cd sealed-eval
./scripts/bootstrap.sh
./scripts/dogfood-install-path.sh
```

`bootstrap.sh` creates a venv, installs the package, and writes `.env` with `SEAL_TOKEN` (vault-ref if ownlock works).

## Operator loop

1. `sealed-eval propose <suite> --markdown-file fixtures/sample-ac.md` (or `--fixture` / `--import-path`)
2. `sealed-eval show-draft <suite>` — review modes/paths
3. `TOKEN` from `.env` / ownlock → `sealed-eval seal <suite> "$TOKEN"`
4. `sealed-eval publish <suite>` → hand to coder
5. Subject up → `sealed-eval grade <suite> <url> "$TOKEN"`
6. Coder reads `sealed-eval scorecard <suite>` (no token)

Optional UI: `pip install -e ".[ui]" && playwright install chromium` then propose from `fixtures/sample-ac-ui.md`.

Optional cross-repo secrets: `./scripts/ownlock-team-bundle.sh /path/to/subject SEAL_TOKEN DATABASE_URL`

## Coder loop

1. Public task only
2. Implement subject; expose URL
3. Soft tests OK; not the gate
4. Read scorecard buckets only

## Dogfood scripts

| Script | Expect |
| --- | --- |
| `dogfood-pass.sh` / `fail.sh` | orders fixture green / red |
| `dogfood-markdown.sh` | AC → grade |
| `dogfood-install-path.sh` | full cold path + scorecard |
| `dogfood-multimode.sh` | contract + invariant + golden |
| `dogfood-probe-db.sh` | json_probe + sqlite db |
| `dogfood-ownauth.sh` | OwnAuth Express API only (not Tauri desktop IPC) |

## Threat model

| Asset | Rule |
| --- | --- |
| Seal token | ownlock / `.env` gitignored; never in subject git |
| Sealed cases | SE `sealed/` only |
| Scorecard public | Aggregates; no hold-out bodies |
| DB / AWS probes | Creds via ownlock env; cases store key **names** and argv, not secrets |

## Troubleshooting

| Symptom | Check |
| --- | --- |
| seal token mismatch | Same token for seal and grade |
| playwright_missing | Install `[ui]` extra + browsers |
| missing_env:DATABASE_URL | `ownlock run -- …` or export DSN |
| psycopg_missing | Use sqlite DSN or `pip install psycopg` |
