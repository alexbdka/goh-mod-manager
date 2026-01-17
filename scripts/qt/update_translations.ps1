param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")),
    [Alias("Language")]
    [string[]]$Languages = @()
)

$ErrorActionPreference = "Stop"

$sourceRoot = Join-Path $ProjectRoot "goh_mod_manager"
$uiDir = Join-Path $sourceRoot "res\ui"
$i18nDir = Join-Path $sourceRoot "i18n"
$excludeDirs = @(
    (Join-Path $sourceRoot "presentation\view\ui"),
    (Join-Path $sourceRoot "i18n"),
    (Join-Path $ProjectRoot ".venv")
)

if (-not (Test-Path $sourceRoot))
{
    throw "Source directory not found: $sourceRoot"
}

$resolvedLanguages = @()
if ($Languages -and $Languages.Count -gt 0)
{
    $resolvedLanguages = $Languages
}
else
{
    if (Test-Path $i18nDir)
    {
        $existingTs = Get-ChildItem -Path $i18nDir -Filter "goh_mod_manager_*.ts" -ErrorAction SilentlyContinue
        foreach ($file in $existingTs)
        {
            if ($file.Name -match "^goh_mod_manager_(.+)\.ts$")
            {
                $resolvedLanguages += $Matches[1]
            }
        }
    }
}

if (-not $resolvedLanguages -or $resolvedLanguages.Count -eq 0)
{
    throw "No languages specified and no existing .ts files found. Use -Language fr or -Languages fr, de."
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

if (-not (Test-Path $i18nDir))
{
    New-Item -ItemType Directory -Force -Path $i18nDir | Out-Null
}

foreach ($language in $resolvedLanguages)
{
    $tsPath = Join-Path $i18nDir "goh_mod_manager_$language.ts"
    Write-Host "Updating translations: $tsPath"
    & pyside6-lupdate -extensions py,ui $inputFiles -ts $tsPath
}

Write-Host "Done."
