"""
Tests for book_layout.cli — all CLI sub-commands, offline and deterministic.

These tests call main() directly with argv lists; no subprocess needed.

Refs: claude-skills#210
"""
import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from book_layout.cli import main


# ── helpers ───────────────────────────────────────────────────────────────────

def run_cli(*args: str) -> int:
    """Run CLI with the given args, return exit code."""
    return main(list(args))


def run_cli_to_file(*args: str) -> tuple[int, Path]:
    """Run CLI writing output to a temp file, return (exit_code, path)."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name
    code = main(list(args) + ["--out", out])
    return code, Path(out)


# ── plan ──────────────────────────────────────────────────────────────────────

class TestCLIPlan:
    def test_plan_writes_valid_json(self):
        code, path = run_cli_to_file("plan", "--chapters", "4,8,3")
        assert code == 0
        data = json.loads(path.read_text())
        assert data["title"] == "Untitled Book"
        assert len(data["chapters"]) == 3

    def test_plan_with_title(self):
        code, path = run_cli_to_file("plan", "--chapters", "4", "--title", "My Book")
        assert code == 0
        data = json.loads(path.read_text())
        assert data["title"] == "My Book"

    def test_plan_format_yearbook(self):
        code, path = run_cli_to_file(
            "plan", "--chapters", "4", "--format", "yearbook"
        )
        assert code == 0
        data = json.loads(path.read_text())
        assert data["book_format"] == "yearbook"

    def test_plan_size_a4(self):
        code, path = run_cli_to_file(
            "plan", "--chapters", "4", "--size", "a4"
        )
        assert code == 0
        data = json.loads(path.read_text())
        assert data["page_size"] == "a4"

    def test_plan_single_chapter(self):
        code, path = run_cli_to_file("plan", "--chapters", "10")
        assert code == 0
        data = json.loads(path.read_text())
        assert len(data["chapters"]) == 1


# ── album ─────────────────────────────────────────────────────────────────────

class TestCLIAlbum:
    def test_album_basic(self):
        code, path = run_cli_to_file(
            "album", "--eras", "2000s:8,2010s:12,2020s:5"
        )
        assert code == 0
        data = json.loads(path.read_text())
        assert data["book_format"] == "photo-book"
        # 3 eras + 1 cover chapter
        assert len(data["chapters"]) == 4

    def test_album_no_cover(self):
        code, path = run_cli_to_file(
            "album", "--eras", "2000s:8,2010s:12", "--no-cover"
        )
        assert code == 0
        data = json.loads(path.read_text())
        assert len(data["chapters"]) == 2

    def test_album_title(self):
        code, path = run_cli_to_file(
            "album", "--eras", "Trips:10", "--title", "Adventure Album"
        )
        assert code == 0
        data = json.loads(path.read_text())
        assert "Adventure Album" in data["title"]

    def test_album_era_without_count_uses_default(self):
        code, path = run_cli_to_file("album", "--eras", "AgeOfAdventure", "--no-cover")
        assert code == 0
        data = json.loads(path.read_text())
        assert len(data["chapters"]) == 1


# ── year ──────────────────────────────────────────────────────────────────────

class TestCLIYear:
    def test_year_basic(self):
        code, path = run_cli_to_file(
            "year", "--instruments", "handpan:14,barrel-organ:10"
        )
        assert code == 0
        data = json.loads(path.read_text())
        assert data["book_format"] == "design-chapter"

    def test_year_title_and_edition(self):
        code, path = run_cli_to_file(
            "year", "--instruments", "handpan:14",
            "--title", "Design Book", "--edition", "2026"
        )
        assert code == 0
        data = json.loads(path.read_text())
        assert "2026" in data["title"]

    def test_year_without_count_uses_default(self):
        code, path = run_cli_to_file("year", "--instruments", "handpan")
        assert code == 0
        data = json.loads(path.read_text())
        assert len(data["chapters"]) >= 1


# ── validate ──────────────────────────────────────────────────────────────────

class TestCLIValidate:
    def test_validate_valid_book_returns_0(self):
        # First plan a book
        _, book_path = run_cli_to_file("plan", "--chapters", "4,8")
        code = run_cli("validate", str(book_path))
        assert code == 0

    def test_validate_bad_json_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            f.write('{"not": "a book"}')
            bad_path = f.name
        with pytest.raises(Exception):
            run_cli("validate", bad_path)


# ── export ────────────────────────────────────────────────────────────────────

class TestCLIExport:
    def test_export_produces_manifest(self):
        _, book_path = run_cli_to_file("plan", "--chapters", "4,8")
        manifest_path = str(book_path).replace(".json", "-manifest.json")
        code = run_cli("export", str(book_path), "--manifest-out", manifest_path)
        assert code == 0
        data = json.loads(Path(manifest_path).read_text())
        assert "page_manifests" in data
        assert "all_slots" in data
        assert data["total_pages"] > 0


# ── themes / templates ────────────────────────────────────────────────────────

class TestCLIListCommands:
    def test_themes_returns_0(self, capsys):
        code = run_cli("themes")
        assert code == 0
        out = capsys.readouterr().out
        assert "yearbook-classic" in out
        assert "photo-album-warm" in out

    def test_templates_returns_0(self, capsys):
        code = run_cli("templates")
        assert code == 0
        out = capsys.readouterr().out
        assert "full-bleed" in out
        assert "grid-2x2" in out
        assert "hero+caption" in out
