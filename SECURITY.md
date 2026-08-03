# Security Policy

## Reporting a vulnerability

If you discover a security vulnerability in SEALed-eval:

1. **Do not** open a public GitHub issue.
2. Open a [private security advisory](https://github.com/thebscolaro/sealed-eval/security/advisories/new) on GitHub.
3. Include a description, steps to reproduce, and whether seal tokens or hold-out data were exposed.
4. We will respond promptly and coordinate a fix.

CI / GitHub Actions hardening is documented in [docs/github-security.md](docs/github-security.md).

## Seal tokens and hold-outs

SEALed-eval's threat model assumes **seal tokens** and **sealed case payloads** stay with the eval-operator plane.

- Do **not** paste seal tokens into GitHub issues, PRs, chat logs, or public CI logs.
- Do **not** attach `cases.sealed.json` or private hold-outs to public issues.
- Scorecards should expose buckets and rates, not raw expected bodies.
- Prefer `ownlock` for local `SEAL_TOKEN` storage; never commit `.env` with live tokens.

If a seal token leaks, rotate it: re-seal the corpus with a new token and discard the old seal file.

## Supported versions

| Version | Supported |
| --- | --- |
| 0.3.x | Yes |
| 0.2.x | Best-effort |
| 0.1.x | Best-effort |

## Security model (short)

- Sealed store is local / operator-controlled; not nested inside subject repos.
- Grade adapters run against artifacts; they must not print secrets into scorecards.
- `json_probe` / `db` cases should reference env **names** and argv, not embed credentials.
- Public task and public scorecard APIs omit hold-out payloads.
