# SEALed-eval

![SEALed-eval wordmark](branding/wordmark.png)

**Agents will edit tests to pass. SEALed-eval keeps the grade outside their reach.**

SEALed-eval (SE) is a sealed evaluation control plane for coding agents. It lives in its **own repo/process**, drafts and seals hold-out cases, publishes a **public task** to coder agents, then grades a **running artifact**. Coders never see hold-out payloads.

Skills orchestrate; the harness judges.

![Architecture](docs/architecture.drawio.png)

![Operator loop](docs/operator-loop.drawio.png)

Editable sources: [architecture.drawio](docs/architecture.drawio), [operator-loop.drawio](docs/operator-loop.drawio).

1. **Seeds draft; seal grades.** Markdown AC / fixtures invent *draft* cases. A **seal token** (secret password for the judge, usually `SEAL_TOKEN` in ownlock) locks the suite so the coder cannot rewrite the grade.
2. **Check modes** hit the artifact (HTTP, golden, invariants, Playwright UI, JSON probes, read-only SQL).
3. **Coder sees** public task + aggregate scorecard — never sealed expects.
4. **Secrets:** prefer `ownlock run -- sealed-eval …` and bootstrap scripts. Keep sibling control planes **private**.
5. **Sibling control plane:** `bootstrap-sibling` next to the subject → `{name}-sealed-eval`.
6. **Containers:** `scripts/container-compose.sh` prefers Podman, falls back to Docker (same `Dockerfile` / compose names).

## How SE is meant to run

SE is a **long-lived sibling judge**, not a one-shot script and not an auto-updater on every commit.

| Cadence | Action |
| --- | --- |
| When AC matters | Survey → human OK → propose → show-draft → **seal** |
| Whenever you need a verdict | Running app URL → **grade** → scorecard |
| When requirements change | Reseal (human OK again) |

CI is optional (private job + seal token + preview URL). Not required for local/operator use. Details: [WORK_INSTALL.md](docs/WORK_INSTALL.md).

## Check modes

| Mode | What it does | Status |
| --- | --- | --- |
| `contract` | HTTP request + assert response | Works |
| `holdout_golden` | Sealed expected body / sha256 | Works |
| `invariant` | regex / never_contains / dotted jsonpath | Works |
| `ui` | Playwright text/selector | Works (`[ui]`) |
| `json_probe` | Sealed argv → JSON stdout asserts | Works |
| `db` | Read-only SQL via `DATABASE_URL` | Works (sqlite; psycopg optional) |
| `differential` / `cli` | Specced | Later |

## Quick start

**macOS / Linux**

```bash
git clone https://github.com/thebscolaro/sealed-eval && cd sealed-eval
./scripts/bootstrap.sh
./scripts/bootstrap-sibling.sh ~/code/my-app
```

**Windows (PowerShell — same shell as ownlock)**

```powershell
git clone https://github.com/thebscolaro/sealed-eval; cd sealed-eval
.\scripts\bootstrap.ps1
.\scripts\bootstrap-sibling.ps1 C:\path\to\my-app
```

Do not mix WSL and native Windows for ownlock/SE (if ownlock is on PowerShell PATH, use the `.ps1` scripts).

## Work laptop / another machine

Marketplace listing is **not** required. Full steps (lifecycle, Windows, skills): **[docs/WORK_INSTALL.md](docs/WORK_INSTALL.md)**.

Cursor skills: `distribution/cursor-plugin/skills/` (copied into the sibling as `.cursor/skills/`), or `install-cursor-plugin-local.ps1` / `.sh`.

## Docs

- [Work install](docs/WORK_INSTALL.md) · [Runbook](docs/RUNBOOK.md) · [SPEC.md](SPEC.md) · [AGENTS.md](AGENTS.md) · [CHANGELOG.md](CHANGELOG.md) · [github-security](docs/github-security.md)
- Dogfoods: [SPA](docs/dogfood-spa.md) · [fullstack](docs/dogfood-fullstack.md) · [mid-size](docs/dogfood-midsize.md) · [plugin + sandbox](docs/dogfood-plugin-sandbox.md)

MIT. Keep seal tokens out of issues and CI logs.
