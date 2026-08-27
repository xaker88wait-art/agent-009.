# OCR runbook (Unlimited-OCR)

Runbook for running Baidu **Unlimited-OCR** on a machine with a CUDA GPU.

## 1. What you need
- A CUDA host (NVIDIA GPU). The sandbox here has no GPU, so this runs elsewhere.
- Model weights: downloaded automatically from HuggingFace (`baidu/Unlimited-OCR`) —
  they are **not** stored in the repo.
- Python 3.12 + CUDA toolchain. Repo deps are in `requirements.txt`.

## 2. Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Run (Transformers path)
```bash
# single image
python infer_transformers.py --image scan.jpg --output_dir ./out --config gundam

# a folder of images (multi-page, base config)
python infer_transformers.py --image ./scans --output_dir ./out

# a PDF (converts pages, multi-page, base config)
python infer_transformers.py --pdf doc.pdf --output_dir ./out

# validate the pipeline without a model (no GPU needed)
python infer_transformers.py --image scan.jpg --dry_run
```

## 4. Post-processing
Raw model output contains `<|det|>type [bbox]<|/det|>` markers. Clean them:
```python
from ocr_lib.postprocess import remove_det
clean_markdown = remove_det(raw_text)
```

## 5. SGLang path (batch / server)
```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install wheel/sglang-0.0.0.dev11416+g92e8bb79e-py3-none-any.whl kernels==0.11.7 pymupdf==1.27.2.2

python -m sglang.launch_server --model baidu/Unlimited-OCR \
  --served-model-name Unlimited-OCR --attention-backend fa3 --page-size 1 \
  --mem-fraction-static 0.8 --context-length 32768 --enable-custom-logit-processor \
  --disable-overlap-schedule --skip-server-warmup --host 0.0.0.0 --port 10000
```
Then run the batch client:
```bash
python infer.py --image_dir ./scans --output_dir ./out --concurrency 8 --image_mode gundam
```

## Recipes / configs
- Single image configs: `gundam` (base_size=1024, image_size=640, crop_mode=True)
  or `base` (base_size=1024, image_size=1024, crop_mode=False).
- Multi-page / PDF: **base only** (image_size=1024), `ngram_window=1024`.
- vLLM deployment recipe: https://recipes.vllm.ai/baidu/Unlimited-OCR

## Gotchas
- Use `--dry_run` to validate inputs before burning GPU time.
- Model weights are many GB — make sure disk is large enough and use
  `use_safetensors=True`.