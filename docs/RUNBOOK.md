# SEALed-eval runbook

## Mental model

Skills tell agents **when** to call SE. The harness **seals and grades**. Intent-layer (`AGENTS.md` on the subject) helps agents understand the app; SE is a **sibling** judge repo.

## Cold install

```bash
git clone https://github.com/thebscolaro/sealed-eval && cd sealed-eval
./scripts/bootstrap.sh
./scripts/dogfood-install-path.sh
```

## Sibling control plane (real subject)

```bash
./scripts/bootstrap-sibling.sh /path/to/subject [optional-name]
# creates ../{name}-sealed-eval, private GH repo, subject SEALED_EVAL.md pointer
```

Team secrets: `./scripts/ownlock-team-bundle.sh /path/to/subject SEAL_TOKEN` — you enter the bundle passphrase when prompted (1Password / out-of-band; never commit it).

## Operator loop

1. `sealed-eval propose <suite> --markdown-file …` (or `--fixture` / `--import-path`)
2. `sealed-eval show-draft <suite>`
3. Seal with ownlock/`SEAL_TOKEN`
4. `publish` → coder
5. Subject up → `grade` → coder reads `scorecard`

Optional UI: `pip install -e ".[ui]" && playwright install chromium`.

## OwnAuth note

`dogfood-ownauth.sh` grades the **Express browser-dev API** only — not the Tauri desktop IPC app.

## Dogfood scripts

| Script | Expect |
| --- | --- |
| `dogfood-pass.sh` / `fail.sh` | orders fixture |
| `dogfood-markdown.sh` / `install-path.sh` | AC → grade → scorecard |
| `dogfood-multimode.sh` | contract + invariant + golden |
| `dogfood-probe-db.sh` | json_probe + sqlite |
| `dogfood-ui.sh` | Playwright |
| `dogfood-ownauth.sh` | OwnAuth Express (not Tauri) |

## Check notes

- `jsonpath_equals` uses **dotted** paths (`a.b[0]`), not full JSONPath.
- Postgres: install `psycopg` when needed; sqlite works with stdlib.
- AWS: use `json_probe` under `ownlock run` locally — not live AWS in public CI.
