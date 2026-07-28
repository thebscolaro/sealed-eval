# SEALed-eval runbook

Operational guide for eval-operators and anyone dogfooding the project.

## Mental model

SE does **not** run the subject repo's pytest suite as the gate. It grades a **running HTTP artifact** using sealed cases the coder swarm cannot edit.

- **Intent-layer / AC / OpenAPI** → seed drafts
- **Human seal** → cases become authoritative
- **Public task** → what coders may see
- **Grade** → HTTP `contract` calls per case (v0.1)

## Operator loop

1. Install and activate the venv (`pip install -e ".[dev]"` or `uv pip install -e ".[dev]"`).
2. Draft cases:
   - `sealed-eval propose <suite> --fixture orders`
   - or `sealed-eval propose <suite> --markdown-file fixtures/sample-ac.md --title "..."`  
   - or BYO JSON via API `import_path` / CLI `--import-path`
3. Create a seal token: `TOKEN=$(sealed-eval new-token)` — store it like a secret.
4. Seal: `sealed-eval seal <suite> "$TOKEN"`
5. Publish public task: `sealed-eval publish <suite>` (hand to coders; no hold-outs).
6. Ensure the subject API is reachable at a base URL.
7. Optional: register artifact via API `POST /v1/submit_artifact`.
8. Grade: `sealed-eval grade <suite> http://127.0.0.1:8080 "$TOKEN"`
9. Gate is embedded in the scorecard (`pass` / `fail` / `retry`) and available at `POST /v1/gate`.

Exit code of `grade`: `0` = pass, `1` = fail/retry.

## Coder loop

1. Read the **public task** only.
2. Implement the subject app.
3. Expose a base URL the operator can reach.
4. Do not request seal tokens or sealed JSON.
5. Soft/unit tests in-repo are fine for speed; they are not the SE gate.

## Dogfood A — break subject-demo and watch fail

```bash
./scripts/dogfood-fail.sh
```

This starts a healthy subject, seals the orders fixture, then stops the subject (or breaks it) and grades. Expect **exit 1** and failing buckets. The script restores nothing permanent to `subject-demo` source if it only stops the process; see script comments.

Manual variant:

```bash
./scripts/dogfood-pass.sh   # proves green
# stop uvicorn / break a handler
sealed-eval grade orders-v1 http://127.0.0.1:8080 "$TOKEN"   # expect fail
```

## Dogfood B — markdown AC (no orders fixture)

```bash
./scripts/dogfood-markdown.sh
```

Proposes from `fixtures/sample-ac.md`, seals, grades against a running subject. The sample AC includes a visible `/health` contract case so a stock `subject-demo` can pass.

## Threat model (short)

| Asset | Rule |
| --- | --- |
| Seal token | Out-of-band; never in subject git or public issues |
| Sealed cases | Only in SE sealed store / eval-operator disk |
| Public task | Safe to share with coder agents |
| Scorecard | Buckets + rates; no raw hold-out bodies by default |

If a token leaks, re-seal with a new token and discard the old seal file.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `seal token mismatch` | Same `$TOKEN` used for seal and grade; suite id matches |
| Connection errors in buckets | Subject up? Correct base URL/port? |
| `suite not sealed` | Run `seal` before `grade`; `load_cases` requires sealed file |
| Fixture not found | Run from repo root so `fixtures/` resolves |
| Ports in use | Change script ports or kill old `uvicorn` |
| Capabilities | `sealed-eval capabilities` — gh / docker / intent-layer / ctx7 probes |

API health: `curl -s http://127.0.0.1:8787/health` after `sealed-eval serve`.

## Related

- [README.md](../README.md) — product story
- [SPEC.md](../SPEC.md) — normative protocol
- [agents/EVAL_AGENT.md](../agents/EVAL_AGENT.md) · [CODER_BOUNDARY.md](../agents/CODER_BOUNDARY.md)
