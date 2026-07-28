# SEALed-eval Specification (v0.1)

Normative protocol for a work-agnostic **sealed evaluation control plane**.
Display name: **SEALed-eval**. Mascot: harbor seal (`branding/`).

## Purpose

Grade coding-agent work against expected behavior that agents **cannot edit**.
Separate principals: **Eval Agent** drafts/grades/gates; **Coder swarm** implements.
The control plane is always its **own repo**, never nested inside the subject repo.

## Language / runtime

Harness and CLI are **Python 3.11+** (FastAPI). Client packages for Cursor, Claude Code,
and Pi are markdown/config that call this harness over HTTP (and MCP where supported).

## Trust boundaries

| Plane | Agent access | Contents |
|---|---|---|
| Subject workspace | Coders write | App code, optional soft checks |
| Public task card | Coders read | Goals without hold-out payloads |
| Sealed store | Eval-operator only | Hold-outs, seals, scorecards |
| Soft checks | Mutable | Fast feedback; never the merge gate |

## API surface (eval-operator)

1. `propose_eval` — draft task card + sealed cases from seeds, or import BYO corpus
2. `seal_corpus` — human/break-glass approve; requires out-of-band seal token
3. `publish_task` — write/return public task only
4. `submit_artifact` — register build artifact path/URL/image
5. `grade` — black-box run sealed checks; return bucketed scorecard (payloads withheld by default)
6. `gate` — pass / fail / retry from thresholds
7. `capabilities` — probe MCP/CLI availability (github, jira, intent-layer, context7, brains, …)

Coder profile may only: read public task, submit artifact ref, read aggregate scorecard.

## Check modes

- `holdout_golden` — sealed expected outputs (prefer hashed expecteds)
- `differential` — candidate vs reference system
- `contract` — HTTP/OpenAPI black-box
- `invariant` — property commands

## Seeds (authoring)

Priority when present: intent-layer AGENTS.md → existing corpus → ticket/AC paste →
OpenAPI/BDD → differential capture → DeepWiki/survey → Eval Agent interview → fixtures.

Context7 is **coder** docs assist, not a product-behavior seed.
Second brains enrich context; never become sealed expecteds.

## Anti-leak

- Out-of-band seal token (not forgeable subject-workspace sidecar)
- Hold-outs never in subject git history
- Grade artifacts, not in-repo soft tests
- Default scorecard: pass rate, visible−heldout gap, failure buckets — no raw fixtures
- Intent-layer / drafts are seed until `seal_corpus`

## Deploy profiles

1. Local `docker compose` (default)
2. VPS same compose
3. Pi package as eval operator (HTTP/CLI)
4. AgentCore host for Eval Agent (later)
5. Forgejo private sealed host (v2 notes only)

## Bootstrap

Eval-operator may offer `gh repo create … --private` for this control-plane repo after
**explicit confirm**. Never create sealed control plane inside the subject repo.
