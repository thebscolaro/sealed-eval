# SETUP_AGENT.md

Bootstrap the control plane (never inside the subject repo).

Prefer skill: `distribution/cursor-plugin/skills/sealed-eval-setup/SKILL.md`.

1. `./scripts/bootstrap.sh`
2. Optional ownlock team bundle: `./scripts/ownlock-team-bundle.sh <subject> KEYS…`
3. Confirm before `gh repo create` for a new private control plane
4. Intent-layer: root `AGENTS.md` already present in this repo
