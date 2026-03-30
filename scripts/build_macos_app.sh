#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
PYINSTALLER_BIN="$ROOT_DIR/.venv/bin/pyinstaller"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Missing virtual environment at .venv/. Create it first and install requirements."
  exit 1
fi

if [[ ! -x "$PYINSTALLER_BIN" ]]; then
  "$PYTHON_BIN" -m pip install pyinstaller pywebview
fi

rm -rf build dist

"$PYINSTALLER_BIN" \
  --noconfirm \
  --windowed \
  --name Silode \
  --add-data "app/static:app/static" \
  --hidden-import uvicorn.logging \
  --hidden-import uvicorn.loops.auto \
  --hidden-import uvicorn.protocols.http.auto \
  --hidden-import uvicorn.protocols.websockets.auto \
  desktop.py

echo "Built macOS app at: $ROOT_DIR/dist/Silode.app"
