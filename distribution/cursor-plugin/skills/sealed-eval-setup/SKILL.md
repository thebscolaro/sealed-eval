---
name: sealed-eval-setup
description: >
  Bootstrap SEALed-eval control plane: venv, ownlock, capabilities, intent-layer.
  Use when installing SE from scratch or pairing secrets with a subject repo.
---

# SEALed-eval setup

1. Clone control plane (never nest sealed store inside subject)
2. Bootstrap in the **same shell** where `ownlock` is installed:
   - macOS/Linux: `./scripts/bootstrap.sh`
   - Windows PowerShell: `.\scripts\bootstrap.ps1` (do **not** use WSL if ownlock is Win-native)
3. Sibling: `bootstrap-sibling.sh` / `bootstrap-sibling.ps1`
4. Optional: `./scripts/ownlock-team-bundle.sh /path/to/subject KEYS…`
5. `sealed-eval capabilities` — note missing gh / ownlock / playwright / ctx7
6. Next: EVAL skill for propose → seal → grade

Confirm before `gh repo create` for a new private control plane.
