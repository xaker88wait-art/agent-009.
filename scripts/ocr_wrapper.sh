#!/usr/bin/env bash
# Convenience wrapper around the OCR Transformers CLI.
# Usage:
#   scripts/ocr_wrapper.sh single <image> [extra args...]
#   scripts/ocr_wrapper.sh pdf <file.pdf> [extra args...]
#   scripts/ocr_wrapper.sh scan --dry-run     # no GPU needed
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OCR_CLI="${SCRIPT_DIR}/../infer_transformers.py"
DEFAULT_OUT="${OCR_OUTPUT_DIR:-./outputs}"

if [[ ! -f "$OCR_CLI" ]]; then
  # The wrapper can also live next to the OCR repo clone. Try common path.
  if [[ -f "/workspace/project/infer_transformers.py" ]]; then
    OCR_CLI="/workspace/project/infer_transformers.py"
  else
    echo "ERROR: infer_transformers.py not found (${OCR_CLI})" >&2
    exit 1
  fi
fi

cmd="${1:-}"
shift || true

case "$cmd" in
  single)
    input="$1"; shift || true
    python "$OCR_CLI" --image "$input" --output_dir "$DEFAULT_OUT" "$@";;
  pdf)
    input="$1"; shift || true
    python "$OCR_CLI" --pdf "$input" --output_dir "$DEFAULT_OUT" "$@";;
  scan)
    input="$1"; shift || true
    python "$OCR_CLI" --image "$input" --output_dir "$DEFAULT_OUT" --dry_run "$@";;
  help|--help|-h|"")
    tail -n +1 "$0" | head -20
    exit 0;;
  *)
    echo "Unknown command: $cmd" >&2
    echo "Usage: $0 {single|pdf|scan} <input> [extra args...]" >&2
    exit 1;;
esac