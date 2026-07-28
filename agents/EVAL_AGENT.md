# EVAL_AGENT.md

Principal: **eval-operator**. Prefer skill: `distribution/cursor-plugin/skills/sealed-eval-operator/SKILL.md`.

## Do

1. `sealed-eval survey-subject <subject>` (all sources) → **human edits/OKs AC** (incl. novel)
2. `propose` → `show-draft` → **human confirms** → seal (ownlock)
3. `publish` → `grade` → share `scorecard` buckets only

## Do not

- Seal without human OK on AC and show-draft
- Share seal token / sealed cases with coder sessions
- Invent pass/fail without harness scorecard JSON
