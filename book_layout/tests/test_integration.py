"""
End-to-end integration tests for the book_layout engine.

These tests exercise the full pipeline: plan → validate → export → audit →
CLI round-trip.  They prove all modules compose correctly.

All tests are offline and deterministic.  No real images.

Refs: claude-skills#210
"""
import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import book_layout as bl
from book_layout.album import (
    AlbumConfig, EraSpec, PrivacyTier, SourceLedger, SourceLedgerEntry,
    album_privacy_gate, build_album,
)
from book_layout.audit import audit_book
from book_layout.cli import main as cli_main
from book_layout.export import export_book, from_json, manifest_to_json, to_json
from book_layout.planner import ChapterSpec, TemplateRules, plan_book
from book_layout.schema import BookFormat, PageSize
from book_layout.spreads import (
    SpreadConfig, chapter_spread_summary, plan_spread_book, spread_summary,
    spreads_for_book,
)
from book_layout.validator import validate_book
from book_layout.yearbook import (
    GateStatus, InstrumentChapterSpec, InstrumentContentSpec,
    YearbookConfig, build_yearbook,
)


# ── end-to-end: photo album pipeline ─────────────────────────────────────────

class TestAlbumPipeline:
    def _build(self):
        eras = [
            EraSpec("Early Days",    item_count=8,  privacy_tier=PrivacyTier.FAMILY_ONLY,
                    approximate_years="2000–2005"),
            EraSpec("Road Trips",    item_count=15, privacy_tier=PrivacyTier.FAMILY_ONLY,
                    approximate_years="2006–2012"),
            EraSpec("Family Events", item_count=6,  privacy_tier=PrivacyTier.FAMILY_ONLY,
                    approximate_years="2013–2020"),
        ]
        config = AlbumConfig(
            album_title="20 Years of Adventures",
            audience="family-and-friends",
            page_size=PageSize.SQUARE,
        )
        return build_album(eras, config=config), eras, config

    def test_album_builds_successfully(self):
        book, _, _ = self._build()
        assert book.total_pages > 0
        assert book.book_format == BookFormat.PHOTO_BOOK

    def test_album_validates(self):
        book, _, _ = self._build()
        result = validate_book(book)
        assert result.ok, f"Validation errors: {result.errors}"

    def test_album_exports_to_manifest(self):
        book, _, _ = self._build()
        manifest = export_book(book)
        assert manifest.total_pages == book.total_pages
        assert manifest.theme_name == "photo-album-warm"
        assert manifest.fill_rate > 0

    def test_album_json_round_trip(self):
        book, _, _ = self._build()
        restored = from_json(to_json(book))
        assert restored.title == book.title
        assert restored.total_pages == book.total_pages
        assert restored.book_format == book.book_format

    def test_album_audits_ok(self):
        book, _, _ = self._build()
        result = audit_book(book)
        assert result.ok

    def test_album_privacy_gate_passes(self):
        _, eras, config = self._build()
        ok, issues = album_privacy_gate(eras, config)
        assert ok, f"Privacy gate issues: {issues}"

    def test_source_ledger_does_not_contaminate_book(self):
        book, _, _ = self._build()
        ledger = SourceLedger()
        ledger.add(SourceLedgerEntry(
            era_title="Early Days",
            source_path="/private/family/archive/2000-2005",
            item_count=8,
        ))
        # Source path must not appear anywhere in the book's JSON
        book_json = to_json(book)
        assert "/private/family/archive/2000-2005" not in book_json

    def test_album_spreads(self):
        book, _, _ = self._build()
        smap = spreads_for_book(book)
        assert len(smap) == len(book.chapters)
        for chapter_title, spreads in smap.items():
            summ = spread_summary(spreads)
            assert summ.total_spreads > 0


# ── end-to-end: yearbook pipeline ─────────────────────────────────────────────

class TestYearbookPipeline:
    def _instruments(self):
        return [
            InstrumentChapterSpec(
                repo_name="handpan-resonance-model",
                display_name="Handpan — Resonance Model",
                gate_status=GateStatus.PASSED,
                content=InstrumentContentSpec(
                    cover_items=1, build_gallery_items=6,
                    experiment_lab_items=3, detail_shot_items=4,
                ),
            ),
            InstrumentChapterSpec(
                repo_name="barrel-organ-v2",
                display_name="Barrel Organ v2",
                gate_status=GateStatus.PASSED,
                content=InstrumentContentSpec(
                    cover_items=1, build_gallery_items=8,
                    experiment_lab_items=2, detail_shot_items=5,
                ),
            ),
            InstrumentChapterSpec(
                repo_name="steelpan-tuning",
                display_name="Steel Pan — Tuning",
                gate_status=GateStatus.PASSED,
                content=InstrumentContentSpec(
                    cover_items=1, build_gallery_items=4,
                    experiment_lab_items=3, detail_shot_items=3,
                ),
            ),
        ]

    def _config(self):
        return YearbookConfig(
            title="Instrument Design Yearbook",
            edition="2026",
            include_index=True,
        )

    def test_yearbook_builds_successfully(self):
        book = build_yearbook(self._instruments(), config=self._config())
        assert book.total_pages > 0
        assert book.book_format == BookFormat.DESIGN_CHAPTER

    def test_yearbook_validates(self):
        book = build_yearbook(self._instruments(), config=self._config())
        result = validate_book(book)
        assert result.ok, f"Validation errors: {result.errors}"

    def test_yearbook_exports_to_manifest(self):
        book = build_yearbook(self._instruments(), config=self._config())
        manifest = export_book(book)
        assert manifest.theme_name == "design-chapter-technical"
        assert len(manifest.all_slots) == book.total_slots

    def test_yearbook_json_round_trip(self):
        book = build_yearbook(self._instruments(), config=self._config())
        restored = from_json(to_json(book))
        assert restored.title == book.title
        assert restored.total_pages == book.total_pages
        assert len(restored.chapters) == len(book.chapters)

    def test_yearbook_audits_ok(self):
        book = build_yearbook(self._instruments(), config=self._config())
        result = audit_book(book)
        assert result.ok

    def test_yearbook_spread_planning(self):
        book = build_yearbook(self._instruments(), config=YearbookConfig(include_index=False))
        smap = spreads_for_book(book)
        chapter_summ = chapter_spread_summary(book)
        for title in [spec.display_name for spec in self._instruments()]:
            assert title in smap
            assert title in chapter_summ

    def test_index_chapter_present(self):
        book = build_yearbook(self._instruments(), config=self._config())
        titles = [c.title for c in book.chapters]
        assert "Index" in titles

    def test_edition_in_book_title(self):
        book = build_yearbook(self._instruments(), config=self._config())
        assert "2026" in book.title

    def test_page_numbering_globally_sequential(self):
        book = build_yearbook(self._instruments(), config=self._config())
        all_pages = [p for c in book.chapters for p in c.pages]
        nums = [p.page_number for p in all_pages]
        assert nums == list(range(1, book.total_pages + 1))

    def test_no_pii_in_manifest(self):
        book = build_yearbook(self._instruments(), config=self._config())
        manifest = export_book(book)
        mj = manifest_to_json(manifest)
        for forbidden in ["/home", "/tmp", "http://", ".jpg", ".png", ".tiff", "@"]:
            assert forbidden not in mj


# ── end-to-end: spread-first book ────────────────────────────────────────────

class TestSpreadFirstBook:
    def test_spread_book_pipeline(self):
        specs = [
            ChapterSpec(title="Opening",    item_count=6),
            ChapterSpec(title="Main Story", item_count=9),
            ChapterSpec(title="Closing",    item_count=3),
        ]
        book, smap = plan_spread_book(
            specs,
            book_title="Spread Test Book",
            book_format=BookFormat.YEARBOOK,
        )
        # Validate
        v = validate_book(book)
        assert v.ok, f"Validation errors: {v.errors}"
        # Export
        manifest = export_book(book)
        assert manifest.total_pages == book.total_pages
        # Audit
        a = audit_book(book)
        assert a.ok
        # Spreads exist for every chapter
        assert set(smap.keys()) == {"Opening", "Main Story", "Closing"}


# ── end-to-end: CLI pipeline ─────────────────────────────────────────────────

class TestCLIPipeline:
    def test_plan_validate_export_chain(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            book_path = f"{tmpdir}/book.json"
            manifest_path = f"{tmpdir}/manifest.json"

            # Step 1: plan
            code = cli_main(["plan", "--chapters", "4,8,6", "--title", "E2E Test", "--out", book_path])
            assert code == 0

            # Step 2: validate
            code = cli_main(["validate", book_path])
            assert code == 0

            # Step 3: export manifest
            code = cli_main(["export", book_path, "--manifest-out", manifest_path])
            assert code == 0

            # Verify manifest
            manifest_data = json.loads(Path(manifest_path).read_text())
            assert manifest_data["title"] == "E2E Test"
            assert manifest_data["total_pages"] > 0
            assert "page_manifests" in manifest_data

    def test_album_cli_pipeline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            book_path = f"{tmpdir}/album.json"
            manifest_path = f"{tmpdir}/album-manifest.json"

            code = cli_main([
                "album", "--eras", "2000s:10,2010s:15,2020s:8",
                "--title", "Family Album", "--out", book_path,
            ])
            assert code == 0

            code = cli_main(["validate", book_path])
            assert code == 0

            code = cli_main(["export", book_path, "--manifest-out", manifest_path])
            assert code == 0

    def test_yearbook_cli_pipeline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            book_path = f"{tmpdir}/yearbook.json"

            code = cli_main([
                "year",
                "--instruments", "handpan:14,barrel-organ:10",
                "--title", "Design Yearbook",
                "--edition", "2026",
                "--out", book_path,
            ])
            assert code == 0

            code = cli_main(["validate", book_path])
            assert code == 0

    def test_themes_and_templates_are_listed(self, capsys):
        code = cli_main(["themes"])
        assert code == 0
        out = capsys.readouterr().out
        assert "yearbook-classic" in out

        code = cli_main(["templates"])
        assert code == 0
        out = capsys.readouterr().out
        assert "spread" in out


# ── end-to-end: public API surface ───────────────────────────────────────────

class TestPublicAPISurface:
    """Verify the public __init__.py re-exports are all importable and functional."""

    def test_all_key_exports_importable(self):
        # schema
        assert bl.Book is not None
        assert bl.Chapter is not None
        assert bl.Page is not None
        assert bl.ImageSlot is not None
        assert bl.TextBlock is not None
        # templates
        assert bl.get_template is not None
        assert bl.list_templates is not None
        # planner
        assert bl.paginate is not None
        assert bl.plan_book is not None
        assert bl.plan_chapter is not None
        # validator
        assert bl.validate_book is not None
        # themes
        assert bl.get_theme is not None
        assert bl.YEARBOOK_CLASSIC is not None
        # export
        assert bl.export_book is not None
        assert bl.to_json is not None
        assert bl.from_json is not None
        # album
        assert bl.build_album is not None
        assert bl.EraSpec is not None
        # yearbook
        assert bl.build_yearbook is not None
        assert bl.InstrumentChapterSpec is not None

    def test_quick_book_build_and_validate(self):
        specs = [bl.ChapterSpec(title="One", item_count=4)]
        book = bl.plan_book(specs, book_format=bl.BookFormat.PHOTO_BOOK)
        result = bl.validate_book(book)
        assert result.ok

    def test_quick_export_and_round_trip(self):
        specs = [bl.ChapterSpec(title="One", item_count=4)]
        book = bl.plan_book(specs, book_format=bl.BookFormat.YEARBOOK)
        j = bl.to_json(book)
        restored = bl.from_json(j)
        assert restored.total_pages == book.total_pages
