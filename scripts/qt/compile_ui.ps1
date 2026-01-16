param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.."))
)

$ErrorActionPreference = "Stop"

$uiDir = Join-Path $ProjectRoot "goh_mod_manager\res\ui"
$resourcesQrc = Join-Path $ProjectRoot "goh_mod_manager\res\resources.qrc"
$uiOutDir = Join-Path $ProjectRoot "goh_mod_manager\presentation\view\ui"
$resourcesOut = Join-Path $uiOutDir "resources_rc.py"

if (-not (Test-Path $uiDir))
{
    throw "UI directory not found: $uiDir"
}
if (-not (Test-Path $resourcesQrc))
{
    throw "resources.qrc not found: $resourcesQrc"
}

New-Item -ItemType Directory -Force -Path $uiOutDir | Out-Null

Write-Host "Generating resources -> $resourcesOut"
pyside6-rcc $resourcesQrc -o $resourcesOut

Write-Host "Generating UI modules from $uiDir"
Get-ChildItem -Path $uiDir -Filter *.ui | ForEach-Object {
    $outFile = Join-Path $uiOutDir ("{0}.py" -f $_.BaseName)
    Write-Host "  $_ -> $outFile"
    pyside6-uic --from-imports $_.FullName -o $outFile
}

Write-Host "Done."
