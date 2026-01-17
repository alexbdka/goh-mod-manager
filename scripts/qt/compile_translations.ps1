param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.."))
)

$ErrorActionPreference = "Stop"

$i18nDir = Join-Path $ProjectRoot "goh_mod_manager\i18n"

if (-not (Test-Path $i18nDir))
{
    throw "i18n directory not found: $i18nDir"
}

$tsFiles = Get-ChildItem -Path $i18nDir -Filter *.ts
if (-not $tsFiles)
{
    throw "No .ts files found in $i18nDir"
}

foreach ($tsFile in $tsFiles)
{
    Write-Host "Compiling $( $tsFile.Name )"
    & pyside6-lrelease $tsFile.FullName
}

Write-Host "Done."
