# AGENTS.md

READ THIS FIRST before changing SEALed-eval.

## What this repo owns

- Sealed evaluation **control plane** (propose → seal → grade → scorecard)
- Check adapters: `contract`, `holdout_golden`, `invariant`, `ui`, `json_probe`, `db`
- Thin Cursor skills under `distribution/cursor-plugin/skills/` (orchestrate CLI; do not reimplement grade)

## Out of scope

- Subject application code (lives in a separate repo)
- Using in-repo soft tests as the merge gate
- Storing seal tokens or hold-outs in the subject git history

## Invariants

- Hold-out cases require seal token to grade
- Public task and public scorecard never include sealed expects/payloads
- Coder skill must not seal
- Grade running artifacts, not mutable subject tests

## Layout

- `src/sealed_eval/` — harness
- `sealed/` — local sealed store (gitignored suites)
- `fixtures/` — draft seeds only
- `subject-demo/` — HTTP(+UI) demo subject
- `docs/RUNBOOK.md` — operator loop

## Patterns

- Prefer extending `checks.run_case` dispatch over new top-level scripts
- Secrets via ownlock (`ownlock run -- …`)
- Keep commits to one sentence
