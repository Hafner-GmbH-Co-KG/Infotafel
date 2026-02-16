#!/usr/bin/env bash
set -euo pipefail

python -m compileall -q .

python -m ruff check .
python -m ruff format --check .

python -m pytest -q
echo "OK: all gates green"
