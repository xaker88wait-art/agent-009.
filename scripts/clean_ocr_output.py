#!/usr/bin/env python3
"""Clean raw Unlimited-OCR output into Markdown.

Removes the inline ``<|det|>type [bbox]<|/det|>`` markers so the result is
readable Markdown. Can process one file, many files, or a whole directory.

Usage:
  python clean_ocr_output.py out.md                         # in-place
  python clean_ocr_output.py out.md --to clean.md           # write elsewhere
  python clean_ocr_output.py ./results --suffix .clean.md   # rewrite all .md

Importing ``ocr_lib`` requires it to be importable; the script falls back to a
local copy of the logic if the package cannot be found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:  # prefer the shared OCR repo helpers
    sys.path.insert(0, str(Path(__file__).resolve().parent / "../../project"))
    from ocr_lib.postprocess import remove_det
except Exception:  # self-contained fallback
    from typing import Iterable as _Iterable

    _DET_RE = re.compile(r"<\|det\|>([^<\s]+)(?:\s*\[[^\]]*\])?\s*<\|/det\|>(.*)", re.DOTALL)

    def remove_det(raw: str) -> str:
        blocks: list[str] = []
        current: list[str] | None = None
        for line in raw.splitlines():
            line = line.rstrip()
            if not line:
                continue
            m = _DET_RE.match(line)
            if m:
                cat, content = m.group(1).strip(), m.group(2).strip()
                if cat == "image":
                    continue
                if current is not None:
                    blocks.append("\n".join(current))
                current = [content] if content else []
                continue
            if current is None:
                current = []
            current.append(line)
        if current is not None:
            blocks.append("\n".join(current))
        return "\n\n".join(blocks).strip()


def process_file(src: Path, dst: Path) -> bool:
    text = src.read_text(encoding="utf-8")
    cleaned = remove_det(text)
    dst.write_text(cleaned, encoding="utf-8")
    return cleaned != text  # True if anything changed


def expand_sources(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            out.extend(sorted(path.glob("*.md")))
        elif path.is_file():
            out.append(path)
    return out


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="Files or directories (.md) to clean")
    ap.add_argument("--to", help="Write to this path (only valid with a single file)")
    ap.add_argument("--suffix", default=".clean",
                    help="For directories: append this suffix to rewritten filenames")
    ap.add_argument("--in-place", action="store_true",
                    help="Rewrite each file in place")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report what would change without writing")
    return ap.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    files = expand_sources(args.paths)
    if not files:
        raise SystemExit("No .md files found to clean.")

    if args.to and len(files) != 1:
        raise SystemExit("--to requires exactly one input file.")

    changed = unchanged = skipped = 0
    for src in files:
        if not args.to and not args.in_place and args.suffix:
            dst = src.with_suffix(src.suffix + args.suffix)
        else:
            dst = Path(args.to) if args.to else src

        if args.dry_run:
            text = src.read_text(encoding="utf-8")
            print(f"[dry-run] {src.name}: markers={text.count('<|det|>')} -> ")
            continue

        try:
            did_change = process_file(src, dst)
        except Exception as e:  # noqa: BLE001
            skipped += 1
            print(f"[skip] {src}: {e}")
            continue
        print(f"[{'changed' if did_change else 'unchanged'}] {src} -> {dst}")
        if did_change:
            changed += 1
        else:
            unchanged += 1

    print(f"\nCleaned {changed} changed, {unchanged} unchanged, {skipped} skipped.")


if __name__ == "__main__":
    main()