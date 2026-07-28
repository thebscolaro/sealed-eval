# Open questions / skill follow-ups

## Decisions (2026-07-28)

1. **AGENTS.md only** at SE root (no CLAUDE.md). Intent-layer + SE compose; different jobs.
2. **draw.io** installed via Homebrew; PNGs exported for README.
3. **Context7:** install/verify CLI separately if MCP missing — does not block dogfood.
4. **Team-bundle passphrase:** human enters when prompted; out-of-band / 1Password; never commit.
5. **`[db]` / AWS:** deferred packaging; sqlite + local ownlock probes documented.
6. **Gaps:** addressed in 0.3 (richer propose, sibling bootstrap, skills load, screenshot hook).

## Still later

- Child `src/sealed_eval/AGENTS.md` if package grows
- Full JSONPath library; Postgres `[db]` extra; live AWS fixture
- Marketplace plugin; Tauri IPC grade mode
- Propose: refuse unquoted bullets instead of CapWord/`App` guesses (ponytail)
- Prove `screenshot_sha256` with a mint helper + test, or remove until needed
- Cold dogfood against a real public clone + `vite preview` (not only create-vite + `dev`)

## Review notes (2026-07-28)

- Ponytail: RUNBOOK threat model restored; org hardcode removed from sibling bootstrap
- Standards: 0 hard; judgement on propose keyword cascade / untested screenshot hook
- Spec: SPA dogfood used scaffolded Vite Vue (reliable); stranger-clone still a follow-up

