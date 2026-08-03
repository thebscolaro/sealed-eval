# Cold SPA dogfood (2026-07-28)

## Subject (public clone)
- Cloned [lecoueyl/vue3-template](https://github.com/lecoueyl/vue3-template) → `~/code/vue3-template-se`
- Real landing copy: **Vue.js starter template** (`src/pages/index.vue`)
- Preview: `npm run serve` → `vite preview` (not `preview`)
- Pointer: `~/code/vue3-template-se/SEALED_EVAL.md`

## Control plane
- Sibling: `~/code/vue3-template-se-sealed-eval`
- GitHub (private): https://github.com/thebscolaro/vue3-template-se-sealed-eval
- Created via `./scripts/bootstrap-sibling.sh`

## HITL flow that ran
1. `sealed-eval survey-subject` — auto-scanned README / gh PRs / package heuristics / pages
2. Human OK on Accept (survey noise discarded; quoted UI string kept):
   - `Landing page shows "Vue.js starter template"`
3. `propose` → `show-draft` (1 `ui` case) → `seal` (ownlock `SEAL_TOKEN`) → `publish`
4. `npm i && VITE_BASE_PUBLIC_PATH=/ npm run build && npm run serve -- --host 127.0.0.1 --port 4173`
5. `grade` → `scorecard`
6. Result: **gate pass**, 1/1 ui bucket

## Earlier scaffold dogfood
- Vite + Vue create-vite stand-in at `~/code/se-spa-vite-vue` (sibling `se-spa-vite-vue-sealed-eval`) still documents cold-start scaffolding; prefer the public-clone path above for “real subject” proof.

## What this proves
- Survey HITL + refuse-unquoted UI propose works on a third-party public SPA.
- Sibling control plane + ownlock bootstrap works off a real clone.
- Production preview (`vite preview`) grades cleanly (not only `vite` dev).

## Gaps still real
- Survey still surfaces README feature bullets / dep-bump PRs — human must trim.
- No HTTP API on this SPA (UI-only grade).
- Subject had no prior SE AC; Accept was operator-chosen from page text.
