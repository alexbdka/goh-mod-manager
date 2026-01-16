param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")),
    [string[]]$Languages = @("en", "fr", "ru", "zh", "de")
)

$ErrorActionPreference = "Stop"

$sourceRoot = Join-Path $ProjectRoot "goh_mod_manager"
$uiDir = Join-Path $sourceRoot "res\ui"
$excludeDirs = @(
    (Join-Path $sourceRoot "presentation\view\ui"),
    (Join-Path $sourceRoot "i18n"),
    (Join-Path $ProjectRoot ".venv")
)

if (-not (Test-Path $sourceRoot))
{
    throw "Source directory not found: $sourceRoot"
}

$pyFiles = Get-ChildItem -Path $sourceRoot -Recurse -Filter *.py | Where-Object {
    $full = $_.FullName
    foreach ($exclude in $excludeDirs)
    {
        if ( $full.StartsWith($exclude))
        {
            return $false
        }
    }
    return $true
} | ForEach-Object { $_.FullName }

$uiFiles = @()
if (Test-Path $uiDir)
{
    $uiFiles = Get-ChildItem -Path $uiDir -Filter *.ui | ForEach-Object { $_.FullName }
}

$inputFiles = @()
$inputFiles += $pyFiles
$inputFiles += $uiFiles

if (-not $inputFiles)
{
    throw "No translation input files found."
}

foreach ($language in $Languages)
{
    $tsPath = Join-Path $sourceRoot "i18n\goh_mod_manager_$language.ts"
    Write-Host "Updating translations: $tsPath"
    & pyside6-lupdate -extensions py,ui $inputFiles -ts $tsPath
}

Write-Host "Done."
