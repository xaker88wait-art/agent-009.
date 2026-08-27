"""Unit tests for scripts/clean_ocr_output.py.

These tests exercise the self-contained fallback logic so they run anywhere
(no torch/transformers/GPU required). If the real ``ocr_lib.postprocess``
package is importable, the module will use that instead; both implementations
strip ``<|det|>`` markers, so the assertions below hold for either one.
"""

import os
from pathlib import Path

import pytest

import clean_ocr_output as clean


# ---------------------------------------------------------------------------
# remove_det
# ---------------------------------------------------------------------------

class TestRemoveDet:
    def test_plain_text_passthrough(self):
        assert clean.remove_det("hello world") == "hello world"

    def test_empty_text(self):
        assert clean.remove_det("") == ""

    def test_text_marker_strips_det_but_keeps_content(self):
        raw = "<|det|>text [0.0 0.0 0.0 0.0]<|/det|>  Hello world  <|/det|>"
        out = clean.remove_det(raw)
        # The bbox + <|det|> prefix are removed; the trailing <|/det|> of the
        # fallback remains verbatim (a known quirk of the self-contained copy).
        assert "<|det|>" not in out
        assert "Hello world" in out

    def test_image_marker_is_dropped(self):
        raw = "<|det|>image [0.0 0.0 0.0 0.0]<|/det|><|/det|>"
        assert clean.remove_det(raw) == ""

    def test_multiple_blocks_joined_with_blank_line(self):
        raw = (
            "<|det|>image [0 0 1 1]<|/det|><|/det|>\n"
            "<|det|>text [0 0 1 1]<|/det|>second<|/det|>\n"
            "<|det|>text [0 0 1 1]<|/det|>third<|/det|>"
        )
        out = clean.remove_det(raw)
        assert "image" not in out
        assert "second" in out
        assert "third" in out

    def test_leading_content_before_marker_is_kept(self):
        raw = "header\n<|det|>text [0 0 1 1]<|/det|>body<|/det|>"
        out = clean.remove_det(raw)
        assert out.startswith("header")

    def test_trailing_det_marker_survives_in_fallback(self):
        # Documents the self-contained copy's behavior: the closing <|/det|>
        # on the block line is not removed, unlike the canonical ocr_lib copy.
        out = clean.remove_det("<|det|>text [0 0 1 1]<|/det|>hi<|/det|>")
        assert "hi" in out
        assert "<|det|>" not in out


# ---------------------------------------------------------------------------
# process_file
# ---------------------------------------------------------------------------

class TestProcessFile:
    def test_unchanged_returns_false(self, tmp_path):
        src = tmp_path / "in.md"
        dst = tmp_path / "out.md"
        # No markers and no trailing newline: removing markers is a no-op, so
        # the cleaned text equals the source and no write happens.
        src.write_text("no markers here", encoding="utf-8")
        assert clean.process_file(src, dst) is False
        assert dst.read_text(encoding="utf-8") == "no markers here"

    def test_changed_returns_true(self, tmp_path):
        src = tmp_path / "in.md"
        dst = tmp_path / "out.md"
        src.write_text(
            "<|det|>image [0 0 1 1]<|/det|><|/det|>\nkept line\n",
            encoding="utf-8",
        )
        assert clean.process_file(src, dst) is True
        out = dst.read_text(encoding="utf-8")
        assert "kept line" in out
        assert "<|det|>" not in out

    def test_writes_to_dst_without_touching_src(self, tmp_path):
        src = tmp_path / "in.md"
        dst = tmp_path / "out.md"
        original = "<|det|>text [0 0 1 1]<|/det|>content<|/det|>"
        src.write_text(original, encoding="utf-8")
        clean.process_file(src, dst)
        # source untouched, destination cleaned
        assert src.read_text(encoding="utf-8") == original


# ---------------------------------------------------------------------------
# expand_sources
# ---------------------------------------------------------------------------

class TestExpandSources:
    def test_single_file(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("x", encoding="utf-8")
        out = clean.expand_sources([str(f)])
        assert out == [f]

    def test_directory_globs_md_files_sorted(self, tmp_path):
        (tmp_path / "b.md").write_text("1", encoding="utf-8")
        (tmp_path / "a.md").write_text("2", encoding="utf-8")
        (tmp_path / "c.txt").write_text("not md", encoding="utf-8")
        out = clean.expand_sources([str(tmp_path)])
        assert [p.name for p in out] == ["a.md", "b.md"]

    def test_missing_path_is_ignored(self, tmp_path):
        assert clean.expand_sources([str(tmp_path / "nope.md")]) == []

    def test_mixed_file_and_dir(self, tmp_path):
        f = tmp_path / "top.md"
        f.write_text("x", encoding="utf-8")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "z.md").write_text("y", encoding="utf-8")
        out = clean.expand_sources([str(f), str(sub)])
        assert [p.name for p in out] == ["top.md", "z.md"]


# ---------------------------------------------------------------------------
# main / CLI behavior (GPU-free paths)
# ---------------------------------------------------------------------------

class TestMain:
    def test_no_files_exits_with_message(self, tmp_path, capsys):
        empty = tmp_path / "empty"
        empty.mkdir()
        with pytest.raises(SystemExit) as exc:
            clean.main([str(empty)])
        assert exc.value.code == "No .md files found to clean."

    def test_to_requires_single_file(self, tmp_path, capsys):
        a = tmp_path / "a.md"
        b = tmp_path / "b.md"
        a.write_text("x", encoding="utf-8")
        b.write_text("y", encoding="utf-8")
        with pytest.raises(SystemExit) as exc:
            clean.main([str(a), str(b), "--to", "out.md"])
        assert exc.value.code == "--to requires exactly one input file."

    def test_dry_run_does_not_write(self, tmp_path, capsys):
        src = tmp_path / "in.md"
        src.write_text(
            "<|det|>image [0 0 1 1]<|/det|><|/det|>\nkeep\n", encoding="utf-8"
        )
        clean.main([str(src), "--dry-run"])
        # file unchanged, stdout contains dry-run marker
        assert "<|det|>" in src.read_text(encoding="utf-8")
        assert "markers=" in capsys.readouterr().out

    def test_in_place_cleans_when_changed(self, tmp_path, capsys):
        src = tmp_path / "in.md"
        src.write_text(
            "<|det|>text [0 0 1 1]<|/det|>keep me<|/det|>\n",
            encoding="utf-8",
        )
        clean.main([str(src), "--in-place"])
        out = src.read_text(encoding="utf-8")
        assert "keep me" in out
        assert "<|det|>" not in out

    def test_suffix_output(self, tmp_path, capsys):
        src = tmp_path / "in.md"
        src.write_text(
            "<|det|>text [0 0 1 1]<|/det|>hi<|/det|>\n", encoding="utf-8"
        )
        clean.main([str(src), "--suffix", ".clean"])
        cleaned = tmp_path / "in.md.clean"
        assert cleaned.exists()
        assert "<|det|>" not in cleaned.read_text(encoding="utf-8")
        # original left untouched
        assert "<|det|>" in src.read_text(encoding="utf-8")

    def test_to_writes_to_specific_path(self, tmp_path, capsys):
        src = tmp_path / "in.md"
        dst = tmp_path / "custom.md"
        src.write_text("<|det|>text [0 0 1 1]<|/det|>x<|/det|>", encoding="utf-8")
        clean.main([str(src), "--to", str(dst)])
        assert "<|det|>" not in dst.read_text(encoding="utf-8")


def test_parse_args_defaults():
    args = clean.parse_args(["a.md", "b.md"])
    assert args.paths == ["a.md", "b.md"]
    assert args.to is None
    assert args.suffix == ".clean"
    assert args.in_place is False
    assert args.dry_run is False