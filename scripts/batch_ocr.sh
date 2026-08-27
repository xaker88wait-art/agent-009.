#!/usr/bin/env bash
# Batch OCR: run Unlimited-OCR over every PDF (or image folder) in a directory.
#
#   scripts/batch_ocr.sh --pdf-dir ./docs --output-dir ./ocr_out
#   scripts/batch_ocr.sh --img-dir ./scans --output-dir ./ocr_out --config base
#
# Each input produces its own output subfolder inside the output directory.
# Use --dry-run to print the plan without running (no GPU needed).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Resolve the OCR CLI like the wrapper does.
OCR_CLI=""
for candidate in \
  "${SCRIPT_DIR}/../infer_transformers.py" \
  "/workspace/project/infer_transformers.py"; do
  if [[ -f "$candidate" ]]; then OCR_CLI="$candidate"; break; fi
done
[[ -n "$OCR_CLI" ]] || { echo "ERROR: infer_transformers.py not found" >&2; exit 1; }

PDF_DIR=""
IMG_DIR=""
OUT_DIR="./ocr_out"
CONFIG="gundam"
DRY=0

usage() { sed -n '1,8p' "$0"; exit 0; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pdf-dir) PDF_DIR="$2"; shift 2;;
    --img-dir) IMG_DIR="$2"; shift 2;;
    --output-dir) OUT_DIR="$2"; shift 2;;
    --config) CONFIG="$2"; shift 2;;
    --dry-run) DRY=1; shift;;
    -h|--help) usage;;
    *) echo "Unknown option: $1" >&2; usage;;
  esac
done

if [[ -z "$PDF_DIR" && -z "$IMG_DIR" ]]; then
  echo "ERROR: provide --pdf-dir or --img-dir" >&2; usage;
fi

run_one() {  # $1=input path, $2=output folder
  local input="$1" out="$2"
  if [[ -n "$PDF_DIR" ]]; then
    ([[ $DRY -eq 1 ]] && python "$OCR_CLI" --pdf "$input" --output_dir "$out" --dry_run) \
      || python "$OCR_CLI" --pdf "$input" --output_dir "$out"
  else
    ([[ $DRY -eq 1 ]] && python "$OCR_CLI" --image "$input" --output_dir "$out" --config "$CONFIG" --dry_run) \
      || python "$OCR_CLI" --image "$input" --output_dir "$out" --config "$CONFIG"
  fi
}

mkdir -p "$OUT_DIR"

if [[ -n "$PDF_DIR" ]]; then
  echo "== Batch PDFs: $PDF_DIR =="
  for f in "$PDF_DIR"/*.pdf; do
    [[ -e "$f" ]] || continue
    base="$(basename "$f" .pdf)"
    echo "-> $base"
    run_one "$f" "$OUT_DIR/$base"
  done
else
  # Each subfolder of IMG_DIR becomes one job.
  echo "== Batch image dirs: $IMG_DIR =="
  for d in "$IMG_DIR"/*/; do
    [[ -d "$d" ]] || continue
    base="$(basename "$d")"
    echo "-> $base"
    run_one "$d" "$OUT_DIR/$base"
  done
fi

echo
echo "Done. Outputs in: $OUT_DIR"
[[ $DRY -eq 1 ]] && echo "(dry-run — nothing executed)"