$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$server = Join-Path $PSScriptRoot "multi_ai_platform\server.py"

if (Get-Command python -ErrorAction SilentlyContinue) {
    python $server @args
    exit $LASTEXITCODE
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 $server @args
    exit $LASTEXITCODE
}

$candidates = @()
$candidates += Get-ChildItem "$env:LocalAppData\Programs\Python" -Filter python.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
$candidates += Get-ChildItem "C:\Program Files" -Filter python.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
$python = $candidates | Select-Object -First 1

if (-not $python) {
    throw "No Python interpreter was found. Install Python 3 to run the prototype."
}

& $python $server @args
exit $LASTEXITCODE
