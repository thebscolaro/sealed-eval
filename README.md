# SEALed-eval

![SEALed-eval wordmark](branding/wordmark.png)

**Agents will edit tests to pass. SEALed-eval keeps the grade outside their reach.**

SEALed-eval (SE) is a sealed evaluation control plane for coding agents. It lives in its **own repo/process**, drafts and seals hold-out cases, publishes a **public task** to coder agents, then grades a **running artifact**. Coders never see hold-out payloads.

Skills orchestrate; the harness judges. See [docs/architecture.drawio](docs/architecture.drawio).

## How it works

```text
AC / fixtures / OpenAPI  -->  propose (draft)  -->  human seal (ownlock SEAL_TOKEN)
                                      |                     |
                                      v                     v
                              public task card        sealed cases
                                      |                     |
                                 coder agents               |
                                      |                     |
                                      v                     v
                         running artifact URL  <--  grade (check adapters)
                                      |
                                      v
                         scorecard buckets (coder-safe)
```

1. **Seeds draft; seal grades.** Markdown AC / fixtures invent *draft* cases. Only a human seal token makes them authoritative.
2. **Check modes** hit the artifact (HTTP, golden body, invariants, Playwright UI, JSON CLI probes, read-only SQL).
3. **Coder sees** public task + aggregate scorecard — never sealed expects.
4. **Secrets:** prefer `ownlock run -- sealed-eval …` and `./scripts/bootstrap.sh`.

## Check modes

| Mode | What it does | Status |
| --- | --- | --- |
| `contract` | HTTP request + assert response | Works |
| `holdout_golden` | Sealed expected body / sha256 | Works |
| `invariant` | regex / never_contains / jsonpath | Works |
| `ui` | Playwright text/selector | Works (extra `[ui]`) |
| `json_probe` | Sealed argv → JSON stdout asserts | Works |
| `db` | Read-only SQL via `DATABASE_URL` | Works (sqlite stdlib; psycopg optional) |
| `differential` / `cli` | Specced | Later |

## Quick start

```bash
git clone https://github.com/thebscolaro/sealed-eval && cd sealed-eval
./scripts/bootstrap.sh
./scripts/dogfood-install-path.sh   # propose → show-draft → seal → grade → scorecard
./scripts/dogfood-multimode.sh
./scripts/dogfood-probe-db.sh
```

Manual loop:

```bash
uvicorn app:app --app-dir subject-demo --port 8080
TOKEN=$(sealed-eval new-token)   # or: ownlock run -- printenv SEAL_TOKEN
sealed-eval propose orders-v1 --fixture orders
sealed-eval show-draft orders-v1
sealed-eval seal orders-v1 "$TOKEN"
sealed-eval publish orders-v1
sealed-eval grade orders-v1 http://127.0.0.1:8080 "$TOKEN"
sealed-eval scorecard orders-v1   # coder-safe
```

Cursor skills: `distribution/cursor-plugin/skills/` (operator / coder / setup).

## Docs

- [Runbook](docs/RUNBOOK.md) · [SPEC.md](SPEC.md) · [AGENTS.md](AGENTS.md) · [CHANGELOG.md](CHANGELOG.md)

MIT. Keep seal tokens out of issues and CI logs.
