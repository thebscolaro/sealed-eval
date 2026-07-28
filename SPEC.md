# SEALed-eval Specification (v0.3)

Normative protocol for a work-agnostic **sealed evaluation control plane**.

## Purpose

Grade coding-agent work against expected behavior that agents **cannot edit**.
**Skills orchestrate; the harness judges.** Specs/ACs are the collaboration language.

## Trust boundaries

| Plane | Agent access | Contents |
|---|---|---|
| Subject workspace | Coders write | App code, optional soft checks |
| Public task card | Coders read | Goals without hold-out payloads |
| Public scorecard | Coders read | Buckets, rates, gap, gate |
| Sealed store | Eval-operator only | Hold-outs, seals |
| Soft checks | Mutable | Fast feedback; never the merge gate |
| ownlock | Operator inject | SEAL_TOKEN, DB/AWS creds — not a substitute for seal |

## API surface

1. `propose_eval` — draft task + cases
2. `show draft` / `GET /v1/draft/{id}`
3. `seal_corpus` — human token
4. `publish_task` — public card
5. `submit_artifact` — register URL
6. `grade` — run adapters; persist scorecard
7. `GET /v1/scorecard/{id}` — coder-safe aggregates
8. `gate` — pass / fail / retry
9. `capabilities` — gh, ownlock, playwright, intent-layer, ctx7, docker

Coder profile: public task, submit artifact ref, read aggregate scorecard.

## Check modes

- `contract` — HTTP black-box
- `holdout_golden` — sealed expected / sha256
- `invariant` — property predicates on I/O (`regex`, `never_contains`, **dotted** `jsonpath_equals` — not full JSONPath)
- `ui` — Playwright text / selector / optional `screenshot_sha256`
- `json_probe` — sealed argv → JSON asserts (AWS CLI etc. under ownlock)
- `db` — read-only SQL via env DSN (sqlite stdlib; optional psycopg)
- `differential` / `cli` — later

## Seeds

Intent-layer / AC / fixtures / BYO JSON **draft** only until `seal_corpus`.

## Anti-leak

- Out-of-band seal token (ownlock recommended)
- Hold-outs never in subject git
- Grade artifacts, not in-repo soft tests
- Scorecard: rates, buckets, visible−heldout gap — no raw fixtures
