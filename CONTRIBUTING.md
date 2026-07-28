# Contributing to SEALed-eval

Thanks for helping. Keep changes small and testable.

## Setup

```bash
git clone <this-repo>
cd sealed-eval
python3 -m venv .venv && source .venv/bin/activate
# preferred if you have uv:
# uv pip install -e ".[dev]"
pip install -e ".[dev]"
pytest -q
```

## Before a PR

1. Run `pytest -q` (and dogfood scripts if you touch grading).
2. Do not commit seal tokens, `sealed/*/cases.sealed.json`, or hold-out payloads in issues/PRs.
3. Match the mental model in `README.md` and `docs/RUNBOOK.md`: grade is outside the subject repo.
4. Prefer extending check modes or docs over adding a UI.

## Scope

- Harness code: `src/sealed_eval/`
- Spec: `SPEC.md`
- Demo subject: `subject-demo/` (HTTP contract dogfood only)

Open an issue before large refactors.
