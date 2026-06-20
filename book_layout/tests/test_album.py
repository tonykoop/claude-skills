"""
Tests for book_layout.album — EraSpec, SourceLedger, AlbumConfig,
build_album(), build_era_chapter(), privacy gate.

All tests offline and deterministic.  No real images or person data.

Refs: claude-skills#210 (#93, #101)
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from book_layout.album import (
    ALBUM_TEMPLATE_RULES, AlbumConfig, EraSpec, PrivacyTier,
    SourceLedger, SourceLedgerEntry,
    album_privacy_gate, build_album, build_era_chapter,
)
from book_layout.schema import BookFormat, PageSize
from book_layout.validator import validate_book


# ── EraSpec ───────────────────────────────────────────────────────────────────

class TestEraSpec:
    def test_basic_creation(self):
        era = EraSpec(title="2000s Adventures", item_count=12)
        assert era.title == "2000s Adventures"
        assert era.item_count == 12

    def test_negative_item_count_raises(self):
        with pytest.raises(ValueError):
            EraSpec(title="Bad", item_count=-1)

    def test_zero_item_count_ok(self):
        era = EraSpec(title="Empty Era", item_count=0)
        assert era.item_count == 0

    def test_privacy_tier_default(self):
        era = EraSpec(title="E", item_count=5)
        assert era.privacy_tier == PrivacyTier.FAMILY_ONLY

    def test_to_chapter_spec(self):
        era = EraSpec(title="Trip to Scotland", item_count=10, notes="2006 summer")
        spec = era.to_chapter_spec()
        assert spec.title == "Trip to Scotland"
        assert spec.item_count == 10
        assert spec.book_format == BookFormat.PHOTO_BOOK


# ── SourceLedger ──────────────────────────────────────────────────────────────

class TestSourceLedger:
    def _make_ledger(self) -> SourceLedger:
        ledger = SourceLedger()
        ledger.add(SourceLedgerEntry(
            era_title="2000s", source_path="drive-A/2000s/", item_count=50,
            privacy_tier=PrivacyTier.FAMILY_ONLY,
        ))
        ledger.add(SourceLedgerEntry(
            era_title="2010s", source_path="drive-A/2010s/", item_count=80,
            privacy_tier=PrivacyTier.FAMILY_ONLY,
        ))
        return ledger

    def test_total_items(self):
        ledger = self._make_ledger()
        assert ledger.total_items() == 130

    def test_entries_for_era(self):
        ledger = self._make_ledger()
        entries = ledger.entries_for_era("2000s")
        assert len(entries) == 1
        assert entries[0].era_title == "2000s"

    def test_entries_for_unknown_era(self):
        ledger = self._make_ledger()
        assert ledger.entries_for_era("1990s") == []

    def test_privacy_summary(self):
        ledger = self._make_ledger()
        summary = ledger.privacy_summary()
        assert summary["family-only"] == 130
        assert summary["public"] == 0

    def test_source_paths_stay_in_ledger(self):
        """Source paths must NOT appear in any Book/Chapter/Page object."""
        ledger = SourceLedger()
        ledger.add(SourceLedgerEntry(
            era_title="2000s", source_path="/secret/family/photos/2000s",
            item_count=10,
        ))
        # Build an album — source_path must not leak into the book JSON
        era = EraSpec(title="2000s", item_count=10)
        book = build_album([era])
        book_json = book.model_dump_json()
        assert "/secret/family/photos/2000s" not in book_json

    def test_negative_item_count_raises(self):
        with pytest.raises(ValueError):
            SourceLedgerEntry(era_title="X", source_path="path", item_count=-1)


# ── build_era_chapter() ───────────────────────────────────────────────────────

class TestBuildEraChapter:
    def test_chapter_title_from_era(self):
        era = EraSpec(title="Hawaii 2008", item_count=6)
        ch = build_era_chapter(era)
        assert ch.title == "Hawaii 2008"

    def test_chapter_has_pages(self):
        era = EraSpec(title="E", item_count=5)
        ch = build_era_chapter(era)
        assert ch.page_count > 0

    def test_start_page_respected(self):
        era = EraSpec(title="E", item_count=5)
        ch = build_era_chapter(era, start_page=10)
        assert ch.pages[0].page_number == 10


# ── build_album() ─────────────────────────────────────────────────────────────

class TestBuildAlbum:
    def _eras(self):
        return [
            EraSpec(title="Early 2000s", item_count=8),
            EraSpec(title="Road Trips", item_count=15),
            EraSpec(title="Family Events", item_count=6),
        ]

    def test_book_format_is_photo_book(self):
        book = build_album(self._eras())
        assert book.book_format == BookFormat.PHOTO_BOOK

    def test_chapter_count_includes_cover(self):
        eras = self._eras()
        book = build_album(eras)
        assert len(book.chapters) == len(eras) + 1   # +1 for cover

    def test_chapter_count_no_cover(self):
        eras = self._eras()
        config = AlbumConfig(album_title="T", include_cover=False)
        book = build_album(eras, config=config)
        assert len(book.chapters) == len(eras)

    def test_era_titles_preserved_in_chapters(self):
        eras = self._eras()
        config = AlbumConfig(album_title="T", include_cover=False)
        book = build_album(eras, config=config)
        titles = [c.title for c in book.chapters]
        for era in eras:
            assert era.title in titles

    def test_cover_chapter_is_first(self):
        eras = self._eras()
        book = build_album(eras)
        assert "Cover" in book.chapters[0].title

    def test_page_numbers_globally_sequential(self):
        book = build_album(self._eras())
        from book_layout.validator import validate_book
        result = validate_book(book)
        numbering_errors = [e for e in result.errors if "sequential" in e]
        assert numbering_errors == []

    def test_album_title_propagated(self):
        config = AlbumConfig(album_title="Family Adventures 2000–2020")
        book = build_album(self._eras(), config=config)
        assert "Family Adventures" in book.title

    def test_page_size_from_config(self):
        config = AlbumConfig(album_title="T", page_size=PageSize.SQUARE)
        book = build_album(self._eras(), config=config)
        assert book.page_size == PageSize.SQUARE

    def test_empty_eras_list_no_cover(self):
        config = AlbumConfig(album_title="T", include_cover=False)
        book = build_album([], config=config)
        assert book.total_pages == 0

    def test_valid_book_structure(self):
        book = build_album(self._eras())
        result = validate_book(book)
        # Should have no structural errors (unfilled last-page slots are fine)
        structural_errors = [e for e in result.errors if "no chapters" not in e
                             and "no pages" not in e]
        assert structural_errors == []

    def test_no_real_image_data_in_output(self):
        book = build_album(self._eras())
        j = book.model_dump_json()
        for forbidden in ["/home", "/tmp", "http://", ".jpg", ".png", ".tiff"]:
            assert forbidden not in j


# ── album_privacy_gate() ──────────────────────────────────────────────────────

class TestAlbumPrivacyGate:
    def test_all_same_tier_passes(self):
        eras = [
            EraSpec("E1", 5, privacy_tier=PrivacyTier.FAMILY_ONLY),
            EraSpec("E2", 5, privacy_tier=PrivacyTier.FAMILY_ONLY),
        ]
        config = AlbumConfig(album_title="T", privacy_tier=PrivacyTier.FAMILY_ONLY)
        ok, issues = album_privacy_gate(eras, config)
        assert ok
        assert issues == []

    def test_more_public_era_is_fine(self):
        """A PUBLIC era is less restrictive than FAMILY_ONLY — no issue."""
        eras = [EraSpec("E1", 5, privacy_tier=PrivacyTier.PUBLIC)]
        config = AlbumConfig(album_title="T", privacy_tier=PrivacyTier.FAMILY_ONLY)
        ok, issues = album_privacy_gate(eras, config)
        assert ok

    def test_more_restrictive_era_flagged(self):
        """ARCHIVE_ONLY era in a FAMILY_ONLY album → issue."""
        eras = [EraSpec("E1", 5, privacy_tier=PrivacyTier.ARCHIVE_ONLY)]
        config = AlbumConfig(album_title="T", privacy_tier=PrivacyTier.FAMILY_ONLY)
        ok, issues = album_privacy_gate(eras, config)
        assert not ok
        assert len(issues) == 1
        assert "archive-only" in issues[0].lower()

    def test_multiple_issues_accumulated(self):
        eras = [
            EraSpec("E1", 5, privacy_tier=PrivacyTier.ARCHIVE_ONLY),
            EraSpec("E2", 5, privacy_tier=PrivacyTier.ARCHIVE_ONLY),
        ]
        config = AlbumConfig(album_title="T", privacy_tier=PrivacyTier.FAMILY_ONLY)
        ok, issues = album_privacy_gate(eras, config)
        assert not ok
        assert len(issues) == 2
