# Mid-size subject dogfood (full-stack-fastapi-template)

## Subject
- [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) → `~/code/full-stack-fastapi-se` (~2.8M checkout, backend+frontend+compose)
- Sibling: `~/code/full-stack-fastapi-se-sealed-eval` (private GH)

## What ran
1. `survey-subject` over the real tree (issues/PRs + package heuristics)
2. HITL-style Accept from known template surfaces:
   - `GET /api/v1/utils/health-check/`
   - Login at `/login` shows `"Login to your account"` (propose supports `at /path`)
3. propose → seal → grade **pass** (http+ui)

## Honest limit
Full template wants **Python ≥3.14** + Postgres compose stack. This dogfood graded the **sealed suite** against a tiny local stub that implements those two surfaces — proves SE on a large-subject control plane, not a full Traefik/Postgres bring-up. Real stack: use `./scripts/container-compose.sh` in the subject once their runtime is available.

## Also green
- `./scripts/dogfood-multimode.sh` (in-repo subject-demo) gate pass
- qa-automation-lab real SUT grade (see dogfood-fullstack.md)
- `agent --sandbox enabled` scorecard pass
