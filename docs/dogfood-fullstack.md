# Fullstack dogfood (2026-07-28)

## Deploy model (what this proves)

| Piece | Used here? |
| --- | --- |
| `bootstrap-sibling.sh` control plane | Yes — sealed store outside the subject |
| Bundled Cursor plugin skills in sibling `.cursor/skills/` | Yes — operator loop content |
| Marketplace plugin install provenance | No (still later) |
| Cursor sandbox | No (still later) |

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

## Status
HITL Accept + grade results go here after human OK on Accept and show-draft.
