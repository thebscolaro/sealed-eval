---
name: sealed-eval-setup
description: >
  Bootstrap SEALed-eval control plane: venv, ownlock, capabilities, intent-layer.
  Use when installing SE from scratch or pairing secrets with a subject repo.
---

# SEALed-eval setup

1. Clone control plane (never nest sealed store inside subject)
2. `./scripts/bootstrap.sh`
3. Optional: `./scripts/ownlock-team-bundle.sh /path/to/subject KEYS…`
4. `sealed-eval capabilities` — note missing gh / ownlock / playwright / ctx7
5. Next: EVAL skill for propose → seal → grade

Confirm before `gh repo create` for a new private control plane.
