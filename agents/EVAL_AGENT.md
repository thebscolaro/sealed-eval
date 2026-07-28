# EVAL_AGENT.md

Principal: **eval-operator**. Not the coder swarm.

Prefer skill: `distribution/cursor-plugin/skills/sealed-eval-operator/SKILL.md`.

## Do

1. `sealed-eval capabilities`
2. `propose` → `show-draft` → human seal token (ownlock) → `seal`
3. `publish` public task
4. `grade` → share `scorecard` buckets only

## Do not

- Share seal token or sealed cases with coder sessions
- Invent pass/fail without harness scorecard JSON
