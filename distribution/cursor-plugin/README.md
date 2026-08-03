# SEALed-eval (Cursor plugin)

Bundles operator / coder / setup skills. Harness still lives in the sibling control plane (`sealed-eval` CLI); skills only orchestrate.

## Local install (pre-marketplace)

```bash
# from sealed-eval repo root
./scripts/install-cursor-plugin-local.sh
# then: Developer → Reload Window
```

Verify: Customize → Plugins (or skills list) shows `sealed-eval-operator`, `sealed-eval-coder`, `sealed-eval-setup`.

## Marketplace

Official listing requires Cursor review: https://cursor.com/marketplace/publish  
Repo to submit: `https://github.com/thebscolaro/sealed-eval` (plugin root `distribution/cursor-plugin/`).

Until listed, use local install or team marketplace import of this repo.

## Harness

```bash
sealed-eval serve --port 8787
```

Coder sessions: install nothing that can `seal_corpus`.
