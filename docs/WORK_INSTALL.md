# Using SEALed-eval on a work machine

You do **not** need the Cursor Marketplace. SE is a normal git repo + CLI; Cursor skills are optional sugar.

## What to install where

| Piece | Where it lives | Public? |
| --- | --- | --- |
| Subject app | Your app repo | Whatever it already is |
| Control plane | Sibling `~/code/{app}-sealed-eval` (or private GH) | **Keep private** — holds `sealed/` + `SEAL_TOKEN` |
| Skills / plugin | Optional on the operator machine | Skills are public OSS; never put seal tokens in them |

## Fresh machine (operator)

```bash
# 1) Control plane from public SE (or your private fork)
git clone https://github.com/thebscolaro/sealed-eval.git
cd sealed-eval
./scripts/bootstrap.sh          # venv + SEAL_TOKEN (ownlock if available)

# 2) Pair with the work app
./scripts/bootstrap-sibling.sh /path/to/work-app
cd ../work-app-sealed-eval      # keep this repo private on GitHub

# 3) Optional Cursor skills (no marketplace)
./scripts/install-cursor-plugin-local.sh
# Developer: Reload Window — or open the sibling; it already has .cursor/skills/

# 4) UI grades
pip install -e ".[ui]" && playwright install chromium
```

Share the seal token with teammates via `./scripts/ownlock-team-bundle.sh` (passphrase out-of-band). Never commit `.env` or `sealed/*/`.

## Day-to-day flow

1. **Operator** (you / eval agent) in the **sibling** repo:  
   `survey-subject` → human OK Accept → `propose` → `show-draft` → `seal` → `publish`
2. **Coder** in the **app** repo: public task only; implement; start the app
3. **Operator**: `grade <suite> <url> $SEAL_TOKEN` → coder reads `scorecard` (aggregates only)

## Cursor: skill vs plugin vs marketplace

| Option | Needs Marketplace? | Notes |
| --- | --- | --- |
| Sibling `.cursor/skills/` (copied by bootstrap) | No | Enough for agents in that workspace |
| `./scripts/install-cursor-plugin-local.sh` → `~/.cursor/plugins/local/` | No | User-level skills on that machine |
| Official Marketplace listing | Yes (Cursor review) | Not required for work use |

## Ready for a work app?

Yes for a first private pilot if you: keep the sibling private, use ownlock for `SEAL_TOKEN`, human-OK Accept/show-draft, and seal real behaviors (not only `/health`). Start with HTTP + a few UI strings; add golden/invariant/db as you trust the loop.
