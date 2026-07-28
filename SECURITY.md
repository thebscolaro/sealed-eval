# Security Policy

## Seal tokens and hold-outs

SEALed-eval's threat model assumes **seal tokens** and **sealed case payloads** stay with the eval-operator plane.

- Do **not** paste seal tokens into GitHub issues, PRs, chat logs, or public CI logs.
- Do **not** attach `cases.sealed.json` or fixture hold-outs from a private deployment to public issues.
- Scorecards should expose buckets and rates, not raw expected bodies.

If a seal token leaks, rotate it: re-seal the corpus with a new token and revoke the old one (delete old `sealed/<suite>/seal` and re-run `seal`).

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |

## Reporting a vulnerability

Prefer GitHub Security Advisories once the repository is public. Until then, contact the repository owner privately. Please include steps to reproduce and whether hold-out data was exposed.
