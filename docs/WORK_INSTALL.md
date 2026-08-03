# Using SEALed-eval on a work machine

You do **not** need the Cursor Marketplace. SE is a normal git repo + CLI; Cursor skills are optional sugar.

## Lifecycle (whole picture)

SE is a **long-lived sibling judge**, not a one-shot script.

| Cadence | What happens |
| --- | --- |
| Once (or when AC changes) | Survey → human OK Accept → propose → show-draft → **seal** |
| Often | App is running → **grade** → coder reads scorecard |
| Rarely | Reseal when requirements change |

Cases do **not** auto-update from every code change. CI is optional (private runner + seal token + preview URL) — not shipped as a default GitHub Action.

```text
[subject app repo]          [sibling *-sealed-eval — keep private]
 coder implements    <---    public task
 running URL         --->    grade → scorecard
```

## What to install where

| Piece | Where it lives | Public? |
| --- | --- | --- |
| Subject app | Your app repo | Whatever it already is |
| Control plane | Sibling `{app}-sealed-eval` (or private GH) | **Keep private** — holds `sealed/` + `SEAL_TOKEN` |
| Skills / plugin | Optional on the operator machine | Skills are public OSS; never put seal tokens in them |

## Fresh machine — macOS / Linux

```bash
git clone https://github.com/thebscolaro/sealed-eval.git
cd sealed-eval
./scripts/bootstrap.sh
./scripts/bootstrap-sibling.sh /path/to/work-app
cd ../work-app-sealed-eval   # keep private
./scripts/install-cursor-plugin-local.sh   # optional
pip install -e ".[ui]" && playwright install chromium   # if UI grades
```

## Fresh machine — Windows (PowerShell)

**Stay in native PowerShell.** If ownlock was installed for Windows/PowerShell, do **not** bootstrap or grade inside WSL — WSL will not see that `ownlock` on PATH and agents may “helpfully” jump to bash.

```powershell
git clone https://github.com/thebscolaro/sealed-eval.git
cd sealed-eval
.\scripts\bootstrap.ps1
.\scripts\bootstrap-sibling.ps1 C:\path\to\work-app
cd ..\work-app-sealed-eval
.\scripts\install-cursor-plugin-local.ps1   # optional
.\.venv\Scripts\pip install -e ".[ui]"
.\.venv\Scripts\playwright install chromium
```

Day-to-day (same PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
ownlock run -- sealed-eval survey-subject C:\path\to\work-app --out fixtures\survey-candidates.md
# human OK Accept → propose → show-draft → seal
ownlock run -- sealed-eval grade <suite> http://127.0.0.1:PORT
```

If Cursor’s agent opens a WSL terminal: switch the terminal profile to **PowerShell**, or set the workspace default terminal to PowerShell so `ownlock` and `.venv\Scripts\sealed-eval.exe` match.

Share the seal token with teammates via `ownlock` team bundle (passphrase out-of-band). Never commit `.env` or `sealed/*/`.

## Day-to-day flow

1. **Operator** in the **sibling** repo:  
   `survey-subject` → human OK Accept → `propose` → `show-draft` → `seal` → `publish`
2. **Coder** in the **app** repo: public task only; implement; start the app
3. **Operator**: `grade <suite> <url>` with seal token → coder reads `scorecard`

## Cursor: skill vs plugin vs marketplace

| Option | Needs Marketplace? | Notes |
| --- | --- | --- |
| Sibling `.cursor/skills/` (copied by bootstrap) | No | Enough for agents in that workspace |
| `install-cursor-plugin-local` → `~/.cursor/plugins/local/` | No | User-level skills on that machine |
| Official Marketplace listing | Yes (Cursor review) | Not required for work use |

## Ready for a work app?

Yes for a first private pilot if you: keep the sibling private, use ownlock for `SEAL_TOKEN`, human-OK Accept/show-draft, and seal real behaviors (not only `/health`). Start with HTTP + a few UI strings; add golden/invariant/db as you trust the loop.
