# SEALed-eval

![SEALed-eval wordmark](branding/wordmark.png)

**Agents will edit tests to pass. SEALed-eval keeps the grade outside their reach.**

SEALed-eval (SE) is a sealed evaluation control plane for coding agents. It lives in its **own repo/process**, drafts and seals hold-out cases, publishes a **public task** to coder agents, then grades a **running artifact** with black-box checks. Coders never see hold-out payloads.

## How it works (HTTP APIs today)

```text
intent-layer / AC / OpenAPI  -->  propose (draft)  -->  human seal
                                      |                     |
                                      v                     v
                              public task card        sealed cases
                                      |                     |
                                 coder agents               |
                                      |                     |
                                      v                     v
                              app running at URL  <--  grade (HTTP per case)
```

1. **Seeds are not grades.** Intent-layer (`AGENTS.md`), markdown AC, fixtures, or BYO JSON help *draft* cases. They do not auto-pass the app.
2. **Grading = HTTP calls.** Each sealed case with `check: contract` hits `artifact_base_url` + that case's method/path/body and asserts status/JSON. `/health` only runs if a case says so.
3. **No Playwright / DB probes in v0.1.** Soft tests inside the subject repo are optional and untrusted as the gate.
4. **Wrong fit today:** desktop/UI-only/CLI apps without an HTTP surface—wait for more check modes or wrap a small HTTP façade.

## Check modes

| Mode | What it does | Status |
| --- | --- | --- |
| `contract` | HTTP request + assert response | Works |
| `holdout_golden` | Compare to sealed expecteds (prefer hashes) | Specced |
| `differential` | Same input on reference vs candidate | Specced |
| `invariant` | Property must hold on I/O | Specced |

## Quick start

```bash
git clone <this-repo> && cd sealed-eval
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"   # or: uv pip install -e ".[dev]"

# one-shot dogfood (starts subject-demo, grades, exits 0 on pass)
./scripts/dogfood-pass.sh
./scripts/dogfood-fail.sh      # expect exit 1
./scripts/dogfood-markdown.sh  # propose from markdown AC
```

Manual loop:

```bash
# terminal A
uvicorn app:app --app-dir subject-demo --port 8080

# terminal B
TOKEN=$(sealed-eval new-token)
sealed-eval propose orders-v1 --fixture orders
sealed-eval seal orders-v1 "$TOKEN"
sealed-eval publish orders-v1
sealed-eval grade orders-v1 http://127.0.0.1:8080 "$TOKEN"
```

Operator API: `sealed-eval serve` (default `http://127.0.0.1:8787`).

## Docs

- [Runbook](docs/RUNBOOK.md) — operator/coder loops, dogfood, threat model, troubleshooting
- [SPEC.md](SPEC.md) — normative protocol
- [CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md) · [CHANGELOG.md](CHANGELOG.md)

## Layout

| Path | Role |
| --- | --- |
| `src/sealed_eval/` | Harness (Python) |
| `sealed/` | Local sealed store (runtime; gitignored) |
| `fixtures/` | Sample corpora (orders, sample AC) |
| `subject-demo/` | Tiny HTTP app for dogfood |
| `agents/` | Eval / coder / setup role docs |
| `scripts/` | Dogfood scripts |
| `distribution/` | Cursor / Claude / Pi client stubs |

## Profiles

- **eval-operator** — seal token; propose / seal / grade
- **coder** — public task + artifact URL only

MIT licensed. Keep seal tokens out of issues and CI logs.
