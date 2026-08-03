# Install SEALed-eval Cursor plugin into %USERPROFILE%\.cursor\plugins\local (Windows).
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Src = Join-Path $Root "distribution\cursor-plugin"
$Dest = Join-Path $env:USERPROFILE ".cursor\plugins\local\sealed-eval"

if (-not (Test-Path (Join-Path $Src ".cursor-plugin\plugin.json"))) {
    throw "install-cursor-plugin-local: missing plugin.json under distribution\cursor-plugin"
}

New-Item -ItemType Directory -Force -Path (Split-Path $Dest -Parent) | Out-Null
if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
Copy-Item -Recurse -Force $Src $Dest

Write-Host "install-cursor-plugin-local: OK → $Dest"
Write-Host "Reload Cursor window (Developer: Reload Window) to pick up skills."
Get-ChildItem (Join-Path $Dest "skills") -Directory | ForEach-Object { Write-Host ("  skill: " + $_.Name) }
