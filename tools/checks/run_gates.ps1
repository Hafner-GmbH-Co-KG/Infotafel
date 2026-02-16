$ErrorActionPreference = "Stop"

python -m compileall -q .

python -m ruff check .
python -m ruff format --check .

python -m pytest -q

Write-Host "OK: all gates green"
