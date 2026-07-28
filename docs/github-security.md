# GitHub Actions and repository security

How **SEALed-eval** protects its CI/CD pipeline and what maintainers should verify in GitHub settings. Product threat model: [SECURITY.md](../SECURITY.md). Pattern mirrors [ownlock](https://github.com/thebscolaro/ownlock/blob/main/docs/github-security.md).

## Workflow design

The only workflow is [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

| Property | Setting |
|----------|---------|
| Triggers | `push` / `pull_request` to `main` |
| `pull_request_target` | **Not used** — avoids running untrusted fork code with write permissions |
| Default `permissions` | `contents: read` |
| Third-party actions | Pinned to full commit SHAs; Dependabot bumps the `github-actions` group weekly |

### Job permissions

| Job | Needs write? | Notes |
|-----|--------------|-------|
| `test` | No | pytest matrix 3.11 / 3.12 |
| `security` | No | bandit + pip-audit |
| `build` | No | sdist/wheel via `python -m build` |

Fork pull requests do **not** receive repository secrets. Do not approve workflow runs from first-time contributors without reviewing the workflow diff.

## Repository settings checklist

Apply on `thebscolaro/sealed-eval` (Settings → General / Code security):

- [x] **Branch protection** on `main`: require status checks (`test (3.11)`, `test (3.12)`, `security`, `build`), dismiss stale reviews, block force-push, enforce admins, require conversation resolution
- [x] **Secret scanning** + **push protection**
- [x] **Dependabot alerts** + security updates
- [x] **Private vulnerability reporting** (linked from SECURITY.md)
- [ ] **Actions permissions**: prefer verified creators / allowlist (confirm in UI)
- [x] **Fork PR workflows**: require approval for outside collaborators (`can_approve_pull_request_runs`)
- [x] Wiki / Projects disabled

## Supply-chain files

| File | Purpose |
|------|---------|
| `.github/dependabot.yml` | Weekly pip + github-actions update PRs |
| `.github/CODEOWNERS` | Review path for workflows, seal/grade code, SPEC/SECURITY |

## Reporting

Report workflow or CI vulnerabilities via [private security advisory](https://github.com/thebscolaro/sealed-eval/security/advisories/new).
