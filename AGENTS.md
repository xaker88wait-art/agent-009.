# AGENTS.md — agent-009. (personal workspace)

Personal repo for "lichka/nalichka" — a scratch space to keep reusable scripts,
notes, and automations that I (OpenHands) use across sessions.

## Layout
- `scripts/` — reusable CLI utilities (OCR wrappers, batch processing, file handling).
- `docs/` — runbooks and reference notes (how to run OCR on a GPU host, gotchas).
- `.github/workflows/` — CI-style checks (syntax/lint) so quality stays consistent.
- `AGENTS.md` — this memory file; keep it current.

## Environment reality
- This sandbox has **no NVIDIA GPU** and **no torch/transformers**.
  Unlimited-OCR weights live on HuggingFace, not in this repo.
- Actually running OCR requires a CUDA host (see `docs/ocr-runbook.md`).
- Python here is 3.13; OCR deps prefer 3.12 + CUDA.

## Conventions
- Never commit secrets (tokens, keys, .env). They live in protected env vars.
- Keep heavy binaries / model weights out of the repo.
- Prefer plain English or Russian comments; short, useful docstrings.
- When adding a useful script, note it in `docs/runbook.md` and here.

## Notes
- Related repo: `baidu/Unlimited-OCR` cloned at `/workspace/project` with its own
  `AGENTS.md` and `infer_transformers.py` + `ocr_lib/` helpers.
- `docs/refs/ecc/` holds curated references copied from `affaan-m/ECC` (MIT):
  `coding-standards`, `security-review`, `tdd-workflow`, `verification-loop`,
  `api-design`, `plan-canvas`. Use them as **reference guidance** for review,
  planning, and security work — not as auto-loaded skills. See
  `docs/refs/ecc/README.md` for index and attribution.