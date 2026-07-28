---
name: sealed-eval-coder
description: >
  Coder boundary for SEALed-eval. Use when implementing a subject from a public
  task card or reading aggregate scorecards. Never seal or request seal tokens.
---

# SEALed-eval coder

## Do

1. Read the **public task** only (`sealed-eval publish` output or `/v1/public_task/{id}`)
2. Implement the subject app
3. Expose a reachable artifact URL for the operator
4. Soft unit tests OK for speed
5. Read `sealed-eval scorecard <suite>` (or `/v1/scorecard/{id}`) for buckets only

## Do not

- Ask for seal tokens or sealed case JSON
- Call `seal` / `grade` with a token
- Treat subject pytest as the SE gate
