# Cold SPA dogfood (2026-07-28)

## Subject
- Scaffolded Vite + Vue app at `~/code/se-spa-vite-vue` (official `create-vite` vue template — stand-in for a “random” SPA with a reliable cold start).
- Pointer: `~/code/se-spa-vite-vue/SEALED_EVAL.md`

## Control plane
- Sibling: `~/code/se-spa-vite-vue-sealed-eval`
- GitHub (private): https://github.com/thebscolaro/se-spa-vite-vue-sealed-eval
- Created via `./scripts/bootstrap-sibling.sh`

## Flow that ran
1. Survey AC from visible UI strings → `fixtures/survey-ac.md`
2. `propose` → 3 `ui` cases (“Get started”, “Documentation”, “Vite”) — **not** stub `/health`
3. `show-draft` → `seal` (ownlock `SEAL_TOKEN`) → `publish`
4. `npm run dev` on `:5173` → `grade` → `scorecard`
5. Result: **gate pass**, 3/3 ui buckets

## What this proves
- Sibling control plane + ownlock bootstrap works for a non-demo subject.
- Markdown propose is SPA-friendly (UI modes).
- Skills/docs path matches cold install mental model.

## Gaps still real
- Subject had no prior AC/intent-layer; survey was operator-written from page text.
- No HTTP API on this SPA (UI-only grade).
- Context7 CLI still needed for live framework docs polish.
