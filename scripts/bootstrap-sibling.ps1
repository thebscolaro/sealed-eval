# Create a sibling *-sealed-eval control plane next to a subject app (Windows PowerShell).
# Usage: .\scripts\bootstrap-sibling.ps1 C:\path\to\subject [optional-name]
$ErrorActionPreference = "Stop"
if ($args.Count -lt 1) {
    throw "Usage: .\scripts\bootstrap-sibling.ps1 <subject-path> [repo-name]"
}

$Subject = (Resolve-Path $args[0]).Path
$Name = if ($args.Count -ge 2 -and $args[1]) { $args[1] } else { "$(Split-Path $Subject -Leaf)-sealed-eval" }
$Parent = Split-Path $Subject -Parent
$Dest = Join-Path $Parent $Name
$SeSrc = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (Test-Path $Dest) {
    throw "bootstrap-sibling: $Dest already exists"
}

Write-Host "bootstrap-sibling: copying SE template → $Dest"
New-Item -ItemType Directory -Path $Dest | Out-Null

# Prefer robocopy (built-in); excludes match bootstrap-sibling.sh
$xd = @(".venv", ".git", ".pytest_cache", "__pycache__", "sealed")
$rcArgs = @($SeSrc, $Dest, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NC", "/NS", "/NP")
foreach ($d in $xd) { $rcArgs += @("/XD", $d) }
& robocopy @rcArgs | Out-Null
# robocopy: 0–7 == success with/without files copied
if ($LASTEXITCODE -ge 8) {
    throw "bootstrap-sibling: robocopy failed (exit $LASTEXITCODE)"
}

# Empty sealed store placeholder
$sealedDir = Join-Path $Dest "sealed"
New-Item -ItemType Directory -Force -Path $sealedDir | Out-Null
New-Item -ItemType File -Force -Path (Join-Path $sealedDir ".gitkeep") | Out-Null

Set-Location $Dest
if (Test-Path ".git") { Remove-Item -Recurse -Force ".git" }
git init -q
git add -A
git commit -qm "Bootstrap sealed-eval control plane for $(Split-Path $Subject -Leaf)."

& (Join-Path $Dest "scripts\bootstrap.ps1")

$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    $owner = ""
    try { $owner = (& gh api user -q .login 2>$null | Out-String).Trim() } catch { $owner = "" }
    if ($owner) {
        & gh repo create "$owner/$Name" --private --source=. --remote=origin --push `
            --description "SEALed-eval control plane for $(Split-Path $Subject -Leaf)"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "bootstrap-sibling: gh repo create failed (create manually)"
        }
    } else {
        Write-Host "bootstrap-sibling: gh not logged in; create repo manually when ready"
    }
}

$pointer = Join-Path $Subject "SEALED_EVAL.md"
@"
# SEALed-eval

This subject is graded by a **sibling** control plane (not this repo).

- Control plane path: ``$Dest``
- Coders: read public task + scorecard only — never seal tokens

Operator loop: see control plane ``docs/RUNBOOK.md`` / ``docs/WORK_INSTALL.md``.
"@ | Set-Content -Path $pointer -Encoding utf8

Write-Host "bootstrap-sibling: wrote $pointer"
Write-Host "bootstrap-sibling: OK → $Dest"
