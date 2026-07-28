# SEALed-eval runbook

## Mental model

Skills tell agents **when** to call SE. The harness **seals and grades**. Intent-layer (`AGENTS.md` on the subject) helps agents understand the app; SE is a **sibling** judge repo.

## Cold install

```bash
git clone https://github.com/thebscolaro/sealed-eval && cd sealed-eval
./scripts/bootstrap.sh
./scripts/dogfood-install-path.sh
```

`bootstrap.sh` creates a venv, installs the package, and writes `.env` with `SEAL_TOKEN` (vault-ref if ownlock works).

## Sibling control plane (real subject)

```bash
./scripts/bootstrap-sibling.sh /path/to/subject [optional-name]
# creates ../{name}-sealed-eval, optional private GH repo, subject SEALED_EVAL.md
```

Team secrets: `./scripts/ownlock-team-bundle.sh /path/to/subject SEAL_TOKEN` — enter the bundle passphrase when prompted (1Password / out-of-band; never commit it).

## Operator loop

1. `sealed-eval propose <suite> --markdown-file …` (or `--fixture` / `--import-path`)
2. `sealed-eval show-draft <suite>` — **required** human review before seal (heuristics invent drafts)
3. Seal with ownlock/`SEAL_TOKEN`
4. `publish` → coder
5. Subject up → `grade` → coder reads `scorecard`

Optional UI: `pip install -e ".[ui]" && playwright install chromium`.

## Coder loop

1. Public task only
2. Implement subject; expose URL
3. Soft tests OK; not the gate
4. Read scorecard buckets only

## Dogfood scripts

| Script | Expect |
| --- | --- |
| `dogfood-pass.sh` / `fail.sh` | orders fixture |
| `dogfood-markdown.sh` / `install-path.sh` | AC → grade → scorecard |
| `dogfood-multimode.sh` | contract + invariant + golden |
| `dogfood-probe-db.sh` | json_probe + sqlite |
| `dogfood-ui.sh` | Playwright |
| `dogfood-ownauth.sh` | OwnAuth Express only (not Tauri IPC) |

## Threat model

| Asset | Rule |
| --- | --- |
| Seal token | ownlock / `.env` gitignored; never in subject git |
| Sealed cases | SE `sealed/` only |
| Scorecard public | Aggregates; no hold-out bodies |
| DB / AWS probes | Creds via ownlock env; cases store key **names** and argv, not secrets |

## Check notes

- `jsonpath_equals` uses **dotted** paths (`a.b[0]`), not full JSONPath.
- Postgres: install `psycopg` when needed; sqlite works with stdlib.
- AWS: use `json_probe` under `ownlock run` locally — not live AWS in public CI.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| seal token mismatch | Same token for seal and grade |
| playwright_missing | Install `[ui]` extra + browsers |
| missing_env:DATABASE_URL | `ownlock run -- …` or export DSN |
| psycopg_missing | Use sqlite DSN or `pip install psycopg` |
