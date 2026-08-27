#!/usr/bin/env bash
# Create a Python 3.12 venv and install the OCR requirements (for GPU hosts).
#
#   scripts/make_venv.sh                  # creates .venv in repo root
#   VENV_DIR=/opt/ocr scripts/make_venv.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$REPO_DIR/.venv}"

# Prefer python3.12; fall back to any python3.
PYBIN="$(command -v python3.12 || command -v python3 || true)"
[[ -n "$PYBIN" ]] || { echo "No python3 found" >&2; exit 1; }

"$PYBIN" -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip >/dev/null
if [[ -f "$REPO_DIR/requirements.txt" ]]; then
  "$VENV_DIR/bin/pip" install -r "$REPO_DIR/requirements.txt"
fi

echo "venv ready: $VENV_DIR"
echo "Activate:   source $VENV_DIR/bin/activate"