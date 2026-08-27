#!/usr/bin/env bash
# Pre-flight check for running OCR (Unlimited-OCR) before spending GPU time.
# Verifies Python version, GPU availability, and the required Python packages.
# Exit code 0 = ready; non-zero = something is missing.
set -uo pipefail

echo "== Python =="
python3 --version 2>&1 || { echo "python3 not found"; exit 1; }

echo "== GPU =="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null \
    || nvidia-smi -L
  echo "GPU detected ✓"
else
  echo "nvidia-smi not found — no NVIDIA GPU/CUDA driver."
  echo "OCR inference needs a CUDA GPU. (Dry-runs still work via --dry_run.)"
  exit 1
fi

echo "== Python packages =="
python3 - <<'PY' 2>&1
import importlib.util
required = [
    "torch", "torchvision", "transformers", "PIL", "einops",
    "addict", "easydict", "fitz", "psutil", "matplotlib",
]
missing = [m for m in required if importlib.util.find_spec(m) is None]
if missing:
    print("MISSING:", ", ".join(missing))
    raise SystemExit(1)
try:
    import torch
    print("CUDA available in torch:", torch.cuda.is_available())
except ImportError:
    pass
print("All required OCR packages present ✓")
PY
code=$?
if [ $code -ne 0 ]; then
  echo "Run: pip install -r requirements.txt"
  exit $code
fi

echo
echo "Pre-flight OK — ready to OCR."