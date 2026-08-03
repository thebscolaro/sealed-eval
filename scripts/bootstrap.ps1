# Cold-start bootstrap for SEALed-eval on Windows (native PowerShell).
# Use this shell for ownlock + sealed-eval — do not mix with WSL.
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

function Get-PythonCmd {
    foreach ($name in @("py", "python", "python3")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd }
    }
    throw "Python 3.11+ required on PATH (py launcher or python)."
}

$py = Get-PythonCmd
if (-not (Test-Path ".venv")) {
    if ($py.Name -eq "py.exe" -or $py.Name -eq "py") {
        & $py.Source -3 -m venv .venv
    } else {
        & $py.Source -m venv .venv
    }
}

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "venv missing Scripts\python.exe — recreate .venv with Windows Python (not WSL)."
}
& $venvPython -m pip install -e ".[dev]" -q

$sealedEval = Join-Path $Root ".venv\Scripts\sealed-eval.exe"
$ownlock = Get-Command ownlock -ErrorAction SilentlyContinue

if ($ownlock) {
    if (-not (Test-Path ".ownlock")) {
        & ownlock init --yes 2>$null
        if ($LASTEXITCODE -ne 0) { & ownlock init }
    }
    if (-not (Test-Path ".env")) {
        $token = & $sealedEval new-token
        $token = ($token | Out-String).Trim()
        & ownlock set "SEAL_TOKEN=$token" --yes 2>$null
        if ($LASTEXITCODE -eq 0) {
            Set-Content -Path ".env" -Value 'SEAL_TOKEN=vault("SEAL_TOKEN")' -Encoding utf8
            Write-Host "bootstrap: SEAL_TOKEN stored in ownlock; .env uses vault()"
        } else {
            & ownlock set "SEAL_TOKEN=$token" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Set-Content -Path ".env" -Value 'SEAL_TOKEN=vault("SEAL_TOKEN")' -Encoding utf8
                Write-Host "bootstrap: SEAL_TOKEN stored in ownlock; .env uses vault()"
            } else {
                Set-Content -Path ".env" -Value "SEAL_TOKEN=$token" -Encoding utf8
                Write-Host "bootstrap: wrote plaintext SEAL_TOKEN to .env (ownlock set failed; rotate later)"
            }
        }
    }
} else {
    if (-not (Test-Path ".env")) {
        $token = & $sealedEval new-token
        $token = ($token | Out-String).Trim()
        Set-Content -Path ".env" -Value "SEAL_TOKEN=$token" -Encoding utf8
        Write-Host "bootstrap: ownlock not on this PowerShell PATH; wrote .env (install Win ownlock or add to PATH)"
    }
}

& $sealedEval capabilities
Write-Host "bootstrap: OK — stay in PowerShell; ownlock run -- sealed-eval …"
Write-Host "bootstrap: if Cursor opens WSL terminals, prefer a PowerShell terminal so ownlock matches."
