# scripts/

Reusable CLI utilities kept under version control.

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