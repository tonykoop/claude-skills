"""
Tests for book_layout.yearbook — InstrumentChapterSpec, gate_check,
build_instrument_chapter(), build_yearbook().

All tests offline and deterministic.  No real images.

Refs: claude-skills#210 (#92, #100)
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from book_layout.yearbook import (
    GateError, GateStatus, InstrumentChapterSpec, InstrumentContentSpec,
    YearbookConfig, build_instrument_chapter, build_yearbook, gate_check,
)
from book_layout.schema import BookFormat, PageSize
from book_layout.validator import validate_book


# ── InstrumentContentSpec ─────────────────────────────────────────────────────

class TestInstrumentContentSpec:
    def test_defaults(self):
        spec = InstrumentContentSpec()
        assert spec.cover_items == 1
        assert spec.build_gallery_items == 6
        assert spec.experiment_lab_items == 3
        assert spec.detail_shot_items == 4

    def test_total_items(self):
        spec = InstrumentContentSpec(
            cover_items=1, build_gallery_items=6,
            experiment_lab_items=3, detail_shot_items=4,
        )
        assert spec.total_items == 14

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            InstrumentContentSpec(cover_items=-1)

    def test_zero_section_ok(self):
        spec = InstrumentContentSpec(experiment_lab_items=0)
        assert spec.experiment_lab_items == 0


# ── InstrumentChapterSpec ─────────────────────────────────────────────────────

class TestInstrumentChapterSpec:
    def test_basic_creation(self):
        spec = InstrumentChapterSpec(
            repo_name="handpan-resonance-model",
            display_name="Handpan — Resonance Model",
        )
        assert spec.repo_name == "handpan-resonance-model"
        assert spec.display_name == "Handpan — Resonance Model"

    def test_display_name_defaults_to_repo_name(self):
        spec = InstrumentChapterSpec(repo_name="barrel-organ", display_name="")
        assert spec.display_name == "barrel-organ"

    def test_empty_repo_name_raises(self):
        with pytest.raises(ValueError):
            InstrumentChapterSpec(repo_name="", display_name="X")

    def test_default_gate_status_passed(self):
        spec = InstrumentChapterSpec(repo_name="r", display_name="R")
        assert spec.gate_status == GateStatus.PASSED


# ── gate_check() ──────────────────────────────────────────────────────────────

class TestGateCheck:
    def _spec(self, gate: GateStatus = GateStatus.PASSED) -> InstrumentChapterSpec:
        return InstrumentChapterSpec(repo_name="test-r", display_name="T", gate_status=gate)

    def test_all_passed(self):
        specs = [self._spec(GateStatus.PASSED), self._spec(GateStatus.PASSED)]
        ok, issues = gate_check(specs)
        assert ok
        assert issues == []

    def test_pending_flagged(self):
        specs = [self._spec(GateStatus.PENDING)]
        ok, issues = gate_check(specs)
        assert not ok
        assert "pending" in issues[0]

    def test_failed_flagged(self):
        specs = [self._spec(GateStatus.FAILED)]
        ok, issues = gate_check(specs)
        assert not ok
        assert "failed" in issues[0]

    def test_mixed_accumulates_issues(self):
        specs = [
            self._spec(GateStatus.PASSED),
            self._spec(GateStatus.PENDING),
            self._spec(GateStatus.FAILED),
        ]
        ok, issues = gate_check(specs)
        assert not ok
        assert len(issues) == 2

    def test_empty_list_passes(self):
        ok, issues = gate_check([])
        assert ok
        assert issues == []


# ── build_instrument_chapter() ────────────────────────────────────────────────

class TestBuildInstrumentChapter:
    def _spec(self) -> InstrumentChapterSpec:
        return InstrumentChapterSpec(
            repo_name="handpan",
            display_name="Handpan",
            gate_status=GateStatus.PASSED,
            content=InstrumentContentSpec(
                cover_items=1,
                build_gallery_items=4,
                experiment_lab_items=2,
                detail_shot_items=3,
            ),
        )

    def test_chapter_title_is_display_name(self):
        ch = build_instrument_chapter(self._spec())
        assert ch.title == "Handpan"

    def test_chapter_has_pages(self):
        ch = build_instrument_chapter(self._spec())
        assert ch.page_count > 0

    def test_start_page_respected(self):
        ch = build_instrument_chapter(self._spec(), start_page=5)
        assert ch.pages[0].page_number == 5

    def test_gate_error_without_force(self):
        spec = InstrumentChapterSpec(
            repo_name="r", display_name="R",
            gate_status=GateStatus.PENDING,
        )
        with pytest.raises(GateError):
            build_instrument_chapter(spec)

    def test_force_bypasses_gate(self):
        spec = InstrumentChapterSpec(
            repo_name="r", display_name="R",
            gate_status=GateStatus.PENDING,
        )
        ch = build_instrument_chapter(spec, force=True)
        assert ch.page_count > 0

    def test_zero_section_items_skipped(self):
        spec = InstrumentChapterSpec(
            repo_name="r", display_name="R",
            content=InstrumentContentSpec(
                cover_items=1, build_gallery_items=0,
                experiment_lab_items=0, detail_shot_items=0,
            ),
        )
        ch = build_instrument_chapter(spec)
        # Only cover section → 1 page (full-bleed, 1 item)
        assert ch.page_count == 1

    def test_page_numbers_sequential(self):
        ch = build_instrument_chapter(self._spec(), start_page=3)
        nums = [p.page_number for p in ch.pages]
        assert nums == list(range(3, 3 + ch.page_count))

    def test_theme_applied(self):
        ch = build_instrument_chapter(self._spec())
        assert "technical" in ch.theme or "design" in ch.theme

    def test_no_real_image_data_in_pages(self):
        ch = build_instrument_chapter(self._spec())
        import json
        ch_dict = {
            "pages": [
                {
                    "slots": [
                        {"slot_id": s.slot_id, "content_ref": s.content_ref}
                        for s in p.image_slots
                    ]
                }
                for p in ch.pages
            ]
        }
        j = json.dumps(ch_dict)
        for forbidden in ["/home", "/tmp", "http://", ".jpg", ".png"]:
            assert forbidden not in j


# ── build_yearbook() ──────────────────────────────────────────────────────────

class TestBuildYearbook:
    def _specs(self):
        return [
            InstrumentChapterSpec(
                repo_name="handpan", display_name="Handpan",
                gate_status=GateStatus.PASSED,
                content=InstrumentContentSpec(
                    cover_items=1, build_gallery_items=4,
                    experiment_lab_items=2, detail_shot_items=3,
                ),
            ),
            InstrumentChapterSpec(
                repo_name="barrel-organ", display_name="Barrel Organ",
                gate_status=GateStatus.PASSED,
                content=InstrumentContentSpec(
                    cover_items=1, build_gallery_items=6,
                    experiment_lab_items=3, detail_shot_items=4,
                ),
            ),
        ]

    def test_book_format_is_design_chapter(self):
        book = build_yearbook(self._specs())
        assert book.book_format == BookFormat.DESIGN_CHAPTER

    def test_instrument_chapters_present(self):
        book = build_yearbook(self._specs())
        titles = [c.title for c in book.chapters]
        assert "Handpan" in titles
        assert "Barrel Organ" in titles

    def test_index_chapter_appended(self):
        config = YearbookConfig(include_index=True)
        book = build_yearbook(self._specs(), config=config)
        assert book.chapters[-1].title == "Index"

    def test_no_index_chapter_when_disabled(self):
        config = YearbookConfig(include_index=False)
        book = build_yearbook(self._specs(), config=config)
        assert book.chapters[-1].title != "Index"

    def test_gate_error_on_ungated_instrument(self):
        specs = [
            InstrumentChapterSpec(
                repo_name="r", display_name="R",
                gate_status=GateStatus.PENDING,
            )
        ]
        with pytest.raises(GateError):
            build_yearbook(specs)

    def test_force_bypasses_gate(self):
        specs = [
            InstrumentChapterSpec(
                repo_name="r", display_name="R",
                gate_status=GateStatus.PENDING,
            )
        ]
        book = build_yearbook(specs, force=True)
        assert book.total_pages > 0

    def test_page_numbers_globally_sequential(self):
        book = build_yearbook(self._specs())
        result = validate_book(book)
        numbering_errors = [e for e in result.errors if "sequential" in e]
        assert numbering_errors == []

    def test_edition_in_title(self):
        config = YearbookConfig(title="Instrument Design Yearbook", edition="2026")
        book = build_yearbook(self._specs(), config=config)
        assert "2026" in book.title

    def test_single_instrument(self):
        book = build_yearbook([self._specs()[0]])
        assert book.total_pages > 0
        instrument_chapters = [c for c in book.chapters if c.title != "Index"]
        assert len(instrument_chapters) == 1

    def test_full_book_validates_clean(self):
        book = build_yearbook(self._specs(), config=YearbookConfig(include_index=False))
        result = validate_book(book)
        # No structural errors — warnings for underfull last pages are OK
        structural_errors = [e for e in result.errors
                             if "sequential" in e or "no chapters" in e or "no pages" in e]
        assert structural_errors == []
