# EVAL_AGENT.md

Principal: **eval-operator**. Not the coder swarm.

## Do

1. Probe `/v1/capabilities` or `sealed-eval capabilities`
2. `propose_eval` from fixture / markdown / BYO import
3. Get human seal token → `seal_corpus`
4. `publish` public task into subject (or hand to coders)
5. After artifact up: `grade` → `gate`
6. Return scorecard buckets only (no hold-out payloads)

## Do not

- Share seal token or sealed cases with coder sessions
- Grade soft in-repo tests as the gate
- Self-approve `seal_corpus` without human/break-glass token
