# scripts/

Reusable CLI utilities kept under version control.

## Tools
- `ocr_wrapper.sh` — friendly wrapper (single / pdf / scan dry-run).
- `batch_ocr.sh` — run OCR over every PDF or image subfolder in a directory.
  `--pdf-dir DIR --output-dir OUT` or `--img-dir DIR --output-dir OUT`,
  plus `--config`, `--dry-run`.
- `preflight.sh` — checks Python/GPU/packages before burning GPU time.
- `clean_ocr_output.py` — strip `<|det|>` markers to Markdown (single/many/dir).
- `make_venv.sh` — create a Python 3.12 venv and install `requirements.txt`.

All support `--dry-run`/safe modes so they can be tested without a GPU.

## `ocr_wrapper.sh`
Friendly wrapper around the Unlimited-OCR Transformers CLI.

```bash
scripts/ocr_wrapper.sh single scan.jpg        # single image, ./outputs
scripts/ocr_wrapper.sh pdf doc.pdf            # PDF, ./outputs
scripts/ocr_wrapper.sh single scan.jpg --config base
scripts/ocr_wrapper.sh scan --dry-run         # validate, no GPU
```

Set `OCR_OUTPUT_DIR` to change the output folder.

> The wrapper expects `infer_transformers.py` next to it (in the OCR repo clone)
> or at `/workspace/project/infer_transformers.py`.