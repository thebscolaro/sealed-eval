# Open questions / skill follow-ups

Captured while executing Phases A–C. Do not forget these.

## From intent-layer

1. **Root context file:** We created `AGENTS.md` only (intent-layer asks CLAUDE.md vs AGENTS.md). Prefer keeping a single root file — confirm if you want CLAUDE.md instead or a symlink policy.
2. **Child nodes:** intent-layer may want `src/sealed_eval/AGENTS.md` once that package grows past ~20k tokens — revisit after more adapters.

## From drawio-skill

3. **draw.io desktop CLI** was not on PATH (`drawio` / `/Applications/draw.io.app/...`). Architecture lives at `docs/architecture.drawio` (editable). Install with `brew install --cask drawio` then export PNG if you want README embeds.
4. Optional Graphviz autolayout not used (diagram is small).

## From superpowers / executing-plans

5. **Worktrees:** skill prefers git worktrees for plan execution; we worked on `main` because you asked for a GH repo + commits on this project directly.
6. **Subagent-driven-development** was suggested over executing-plans when subagents exist — we used parallel Task agents for explore earlier; implementation stayed in-parent for speed (ponytail).

## From context7

7. **`ctx7` CLI not on PATH** in this shell. Recommend finishing Context7 login (`npx ctx7 setup`) if you want live FastAPI/Playwright/httpx docs during future adapter work.

## From ownlock / product

8. **Team bundle passphrase UX:** `ownlock-team-bundle.sh` writes `.ownlock/team.olbundle` but does not automate passphrase distribution to the subject repo — confirm preferred channel (1Password / separate DM).
9. **Postgres:** `db` mode uses sqlite stdlib; psycopg is optional and not a declared extra yet — add `[db]` extra when you want first-class Postgres.
10. **AWS json_probe:** cases store argv only; real AWS dogfood needs credentials via ownlock and a fixture you approve (no live AWS calls in CI by default).

## From code-review (run after commits)

11. Review findings will be appended below after the post-push review pass.
