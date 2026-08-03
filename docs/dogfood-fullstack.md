# Fullstack dogfood (2026-07-28)

## Deploy model (what this proves)

| Piece | Used here? |
| --- | --- |
| `bootstrap-sibling.sh` control plane | Yes — sealed store outside the subject |
| Bundled Cursor plugin skills in sibling `.cursor/skills/` | Yes — operator loop content |
| Local Cursor plugin (`~/.cursor/plugins/local`) | See [dogfood-plugin-sandbox.md](dogfood-plugin-sandbox.md) |
| Official marketplace listing | Submit path documented; listing needs Cursor review |
| Cursor sandbox grade | See [dogfood-plugin-sandbox.md](dogfood-plugin-sandbox.md) |

## Subject (public clone)
- [DwonnG/qa-automation-lab](https://github.com/DwonnG/qa-automation-lab) → `~/code/qa-automation-lab-se`
- React UI (`web/`) + FastAPI (`demo-app/`)
- Existing health: `GET /api/health` → `{"status":"ok"}` (`pytest-api/tests/test_health.py`)
- Login UI copy: `Enter the 6-digit demo PIN to continue.` (PIN `000000`)
- Pointer: `~/code/qa-automation-lab-se/SEALED_EVAL.md`

## Control plane
- Sibling: `~/code/qa-automation-lab-se-sealed-eval`
- GitHub (private): https://github.com/thebscolaro/qa-automation-lab-se-sealed-eval
- Created via `./scripts/bootstrap-sibling.sh`

## HITL + grade that ran
1. Early Accept (suite `lab`): health + login UI string → gate pass
2. Expanded suite **`lab-full`** (11 cases, all working modes) → **gate pass** 11/11:
   - `contract`: health, openapi, wrong PIN → 401, items without auth → 401
   - `holdout_golden`: health body; login `000000` issues a `token`
   - `invariant`: health never contains traceback / DEMO_PIN
   - `ui`: PIN prompt + label
   - `json_probe` + `db` (sqlite): local side checks
3. SUT: `demo-app` `:5050` + `web` `:5173` (proxies `/api`); `DATABASE_URL` set for db case
4. Fixture: sibling `fixtures/lab-full.json`

## What this proves
- Sibling control plane grades a third-party public app with **HTTP + UI** buckets
- Accept came from existing pytest health + visible login copy (not a random SPA h1)
- Vite proxy base URL works for combined contract+ui grade
