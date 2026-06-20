"""
Tests for book_layout.themes — registry, built-ins, format matching.

All tests offline and deterministic.

Refs: claude-skills#210
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from book_layout.themes import (
    ColourPalette, SpreadGrammar, Theme, Typography,
    DESIGN_CHAPTER_TECHNICAL, MINIMAL_EDITORIAL, PHOTO_ALBUM_WARM, YEARBOOK_CLASSIC,
    get_theme, get_theme_for_format, list_themes, register_theme,
)

BUILTIN_THEMES = [
    "design-chapter-technical",
    "minimal-editorial",
    "photo-album-warm",
    "yearbook-classic",
]


class TestRegistry:
    def test_list_contains_builtins(self):
        available = list_themes()
        for name in BUILTIN_THEMES:
            assert name in available

    def test_get_known_theme(self):
        for name in BUILTIN_THEMES:
            t = get_theme(name)
            assert t.name == name

    def test_get_unknown_raises(self):
        with pytest.raises(KeyError, match="Unknown theme"):
            get_theme("does-not-exist-xyzzy")

    def test_register_custom(self):
        custom = Theme(name="custom-test-abc", description="Test theme")
        register_theme(custom)
        assert "custom-test-abc" in list_themes()
        assert get_theme("custom-test-abc") is custom


class TestBuiltinThemes:
    def test_yearbook_classic_has_spread_grammar(self):
        t = YEARBOOK_CLASSIC
        assert t.spread_grammar is not None
        assert t.spread_grammar.dominant_position in ("left", "right")

    def test_photo_album_warm_compatible_with_photo_book(self):
        assert "photo-book" in PHOTO_ALBUM_WARM.compatible_formats

    def test_design_chapter_technical_compatible_with_design_chapter(self):
        assert "design-chapter" in DESIGN_CHAPTER_TECHNICAL.compatible_formats

    def test_minimal_editorial_compatible_with_all(self):
        for fmt in ["yearbook", "photo-book", "design-chapter"]:
            assert fmt in MINIMAL_EDITORIAL.compatible_formats

    def test_art_direction_hints_nonempty(self):
        for t in [YEARBOOK_CLASSIC, PHOTO_ALBUM_WARM, DESIGN_CHAPTER_TECHNICAL]:
            assert len(t.art_direction_hints) > 0

    def test_all_themes_have_description(self):
        for name in BUILTIN_THEMES:
            t = get_theme(name)
            assert t.description.strip() != ""

    def test_summarise_returns_string(self):
        for name in BUILTIN_THEMES:
            s = get_theme(name).summarise()
            assert isinstance(s, str)
            assert name in s


class TestGetThemeForFormat:
    def test_yearbook_format_returns_yearbook_classic(self):
        t = get_theme_for_format("yearbook")
        assert t.name == "yearbook-classic"

    def test_photo_book_returns_warm(self):
        t = get_theme_for_format("photo-book")
        assert t.name == "photo-album-warm"

    def test_design_chapter_returns_technical(self):
        t = get_theme_for_format("design-chapter")
        assert t.name == "design-chapter-technical"

    def test_unknown_format_returns_minimal(self):
        t = get_theme_for_format("unknown-format")
        assert t.name == "minimal-editorial"


class TestDataclasses:
    def test_colour_palette_describe(self):
        p = ColourPalette(background="white", primary_text="black")
        desc = p.describe()
        assert "white" in desc
        assert "black" in desc

    def test_typography_describe(self):
        ty = Typography(headline_family="serif", base_size_hint="12pt")
        desc = ty.describe()
        assert "serif" in desc
        assert "12pt" in desc

    def test_spread_grammar_notes(self):
        sg = SpreadGrammar(notes="Test note")
        assert sg.notes == "Test note"
