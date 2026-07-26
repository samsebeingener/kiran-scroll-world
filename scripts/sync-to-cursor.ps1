# Sync scroll-world plugin source -> Cursor local install.
# Cursor rejects junctions outside ~/.cursor/plugins/local — use copy, not symlink.

$ErrorActionPreference = "Stop"

$Source = $PSScriptRoot | Split-Path -Parent
$Target = Join-Path $env:USERPROFILE ".cursor\plugins\local\scroll-world"

if (-not (Test-Path $Source)) {
    throw "Source not found: $Source"
}

New-Item -ItemType Directory -Force -Path (Split-Path $Target -Parent) | Out-Null

Write-Host "Sync: $Source"
Write-Host "  -> $Target"

robocopy $Source $Target /MIR /XD .git projects /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null

if ($LASTEXITCODE -ge 8) {
    throw "robocopy failed with exit code $LASTEXITCODE"
}

Write-Host "Done. Reload Cursor: Developer -> Reload Window"
