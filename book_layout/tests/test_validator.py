"""
Tests for book_layout.validator — overfull/underfull detection, page-number
sequencing errors, aspect-ratio bounds, and consistency checks.

All tests are offline and deterministic.

Refs: claude-skills#210
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from book_layout.planner import ChapterSpec, TemplateRules, plan_book, plan_chapter
from book_layout.schema import (
    Book, BookFormat, Chapter, ImageSlot, Page, PageSize, SlotRole,
)
from book_layout.validator import (
    ASPECT_RATIO_MAX, ASPECT_RATIO_MIN, ValidationResult, validate_book,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_valid_book(item_counts=(4,)) -> Book:
    """Build a minimal valid Book with given item counts per chapter."""
    rules = TemplateRules(default_template="grid-2x2")  # 4 slots/page
    specs = [
        ChapterSpec(title=f"Chapter {i + 1}", item_count=n)
        for i, n in enumerate(item_counts)
    ]
    return plan_book(specs, template_rules=rules)


def _make_slot(filled: bool = True, aspect_ratio: float = 1.5) -> ImageSlot:
    slot = ImageSlot(slot_id="test-slot", aspect_ratio=aspect_ratio, role=SlotRole.HERO)
    if filled:
        slot.fill(0)
    return slot


def _make_page(page_number: int = 1, slots=None) -> Page:
    if slots is None:
        slots = [_make_slot(filled=True)]
    return Page(page_number=page_number, template_name="test", image_slots=slots)


# ── ValidationResult ──────────────────────────────────────────────────────────

class TestValidationResult:
    def test_default_is_ok(self):
        r = ValidationResult()
        assert r.ok is True
        assert r.errors == []
        assert r.warnings == []

    def test_add_error_sets_ok_false(self):
        r = ValidationResult()
        r.add_error("something broke")
        assert r.ok is False
        assert "something broke" in r.errors

    def test_add_warning_does_not_change_ok(self):
        r = ValidationResult()
        r.add_warning("heads up")
        assert r.ok is True   # warnings are non-fatal
        assert "heads up" in r.warnings

    def test_multiple_errors_accumulated(self):
        r = ValidationResult()
        r.add_error("err1")
        r.add_error("err2")
        assert len(r.errors) == 2
        assert r.ok is False


# ── valid book passes ─────────────────────────────────────────────────────────

class TestValidBook:
    def test_fully_filled_book_passes(self):
        book = _make_valid_book(item_counts=(4, 8))
        result = validate_book(book)
        assert result.ok, f"Expected PASS but got errors: {result.errors}"
        assert result.errors == []

    def test_single_chapter_single_page_passes(self):
        book = _make_valid_book(item_counts=(1,))
        result = validate_book(book)
        assert result.ok

    def test_no_errors_on_clean_book(self):
        book = _make_valid_book(item_counts=(4,))
        result = validate_book(book)
        assert len(result.errors) == 0


# ── empty / missing structure ────────────────────────────────────────────────

class TestEmptyStructure:
    def test_book_with_no_chapters_fails(self):
        book = Book(title="Empty", book_format=BookFormat.PHOTO_BOOK)
        result = validate_book(book)
        assert not result.ok
        assert any("no chapters" in e for e in result.errors)

    def test_chapter_with_no_pages_fails(self):
        empty_chapter = Chapter(title="Empty", pages=[])
        book = Book(
            title="T", book_format=BookFormat.YEARBOOK,
            chapters=[empty_chapter]
        )
        result = validate_book(book)
        assert not result.ok
        assert any("no pages" in e for e in result.errors)


# ── unfilled slots (warnings) ────────────────────────────────────────────────

class TestUnfilledSlots:
    def test_underfull_last_page_generates_warning(self):
        """5 items into 4-slot pages → last page has 1 filled + 3 unfilled."""
        rules = TemplateRules(default_template="grid-2x2")  # 4 slots
        book = plan_book(
            [ChapterSpec(title="C", item_count=5)],
            template_rules=rules,
        )
        result = validate_book(book)
        assert result.ok  # warnings only, not errors
        # There should be 3 unfilled-slot warnings on page 2
        unfilled_warnings = [w for w in result.warnings if "unfilled" in w]
        assert len(unfilled_warnings) == 3

    def test_fully_empty_page_generates_warning_not_error(self):
        """A page with all slots unfilled is a warning, not a fatal error."""
        slot = _make_slot(filled=False)
        page = _make_page(slots=[slot])
        chapter = Chapter(title="C", pages=[page])
        book = Book(title="T", book_format=BookFormat.PHOTO_BOOK, chapters=[chapter])
        result = validate_book(book)
        assert result.ok  # unfilled = warning, not error
        assert any("unfilled" in w for w in result.warnings)


# ── aspect-ratio bounds ───────────────────────────────────────────────────────

class TestAspectRatioBounds:
    def test_slot_too_narrow_fails(self):
        """aspect_ratio below ASPECT_RATIO_MIN is an error."""
        slot = ImageSlot(
            slot_id="narrow", aspect_ratio=ASPECT_RATIO_MIN - 0.01, role=SlotRole.HERO
        )
        slot.fill(0)
        page = _make_page(slots=[slot])
        chapter = Chapter(title="C", pages=[page])
        book = Book(title="T", book_format=BookFormat.PHOTO_BOOK, chapters=[chapter])
        result = validate_book(book)
        assert not result.ok
        assert any("aspect_ratio" in e for e in result.errors)

    def test_slot_too_wide_fails(self):
        """aspect_ratio above ASPECT_RATIO_MAX is an error."""
        slot = ImageSlot(
            slot_id="wide", aspect_ratio=ASPECT_RATIO_MAX + 0.01, role=SlotRole.HERO
        )
        slot.fill(0)
        page = _make_page(slots=[slot])
        chapter = Chapter(title="C", pages=[page])
        book = Book(title="T", book_format=BookFormat.PHOTO_BOOK, chapters=[chapter])
        result = validate_book(book)
        assert not result.ok
        assert any("aspect_ratio" in e for e in result.errors)

    def test_boundary_aspect_ratios_pass(self):
        """Exactly at the bounds is valid."""
        for ar in [ASPECT_RATIO_MIN, ASPECT_RATIO_MAX]:
            slot = ImageSlot(slot_id="edge", aspect_ratio=ar, role=SlotRole.HERO)
            slot.fill(0)
            page = _make_page(slots=[slot])
            chapter = Chapter(title="C", pages=[page])
            book = Book(title="T", book_format=BookFormat.PHOTO_BOOK, chapters=[chapter])
            result = validate_book(book)
            ar_errors = [e for e in result.errors if "aspect_ratio" in e]
            assert len(ar_errors) == 0, f"Boundary ratio {ar} should be valid"

    def test_typical_aspect_ratios_pass(self):
        """Common real-world ratios (3:2, 16:9, 4:3, 1:1) must all pass."""
        for ar in [1.0, 1.333, 1.5, 1.778]:  # 1:1, 4:3, 3:2, 16:9
            slot = ImageSlot(slot_id=f"s-{ar}", aspect_ratio=ar, role=SlotRole.SUPPORTING)
            slot.fill(0)
            page = _make_page(slots=[slot])
            chapter = Chapter(title="C", pages=[page])
            book = Book(title="T", book_format=BookFormat.PHOTO_BOOK, chapters=[chapter])
            result = validate_book(book)
            ar_errors = [e for e in result.errors if "aspect_ratio" in e]
            assert len(ar_errors) == 0, f"Ratio {ar} should be valid but got errors: {ar_errors}"


# ── slot consistency ──────────────────────────────────────────────────────────

class TestSlotConsistency:
    def test_filled_without_content_ref_fails(self):
        """filled=True but content_ref=None is a structural error."""
        slot = ImageSlot(slot_id="s", aspect_ratio=1.5, role=SlotRole.HERO)
        slot.filled = True        # manually corrupt — content_ref stays None
        page = _make_page(slots=[slot])
        chapter = Chapter(title="C", pages=[page])
        book = Book(title="T", book_format=BookFormat.PHOTO_BOOK, chapters=[chapter])
        result = validate_book(book)
        assert not result.ok
        assert any("content_ref" in e for e in result.errors)

    def test_content_ref_without_filled_fails(self):
        """content_ref set but filled=False is a structural error."""
        slot = ImageSlot(slot_id="s", aspect_ratio=1.5, role=SlotRole.HERO)
        slot.content_ref = 0      # manually corrupt — filled stays False
        page = _make_page(slots=[slot])
        chapter = Chapter(title="C", pages=[page])
        book = Book(title="T", book_format=BookFormat.PHOTO_BOOK, chapters=[chapter])
        result = validate_book(book)
        assert not result.ok
        assert any("content_ref" in e for e in result.errors)


# ── page numbering ────────────────────────────────────────────────────────────

class TestPageNumbering:
    def test_non_sequential_page_numbers_fail(self):
        slot1 = _make_slot()
        slot2 = _make_slot()
        p1 = _make_page(page_number=1, slots=[slot1])
        p3 = _make_page(page_number=3, slots=[slot2])  # gap: page 2 missing
        chapter = Chapter(title="C", pages=[p1, p3])
        book = Book(title="T", book_format=BookFormat.PHOTO_BOOK, chapters=[chapter])
        result = validate_book(book)
        assert not result.ok
        assert any("expected sequential" in e for e in result.errors)

    def test_duplicate_page_numbers_fail(self):
        slot1 = _make_slot()
        slot2 = _make_slot()
        p1 = _make_page(page_number=1, slots=[slot1])
        p1dup = _make_page(page_number=1, slots=[slot2])   # duplicate 1
        chapter = Chapter(title="C", pages=[p1, p1dup])
        book = Book(title="T", book_format=BookFormat.PHOTO_BOOK, chapters=[chapter])
        result = validate_book(book)
        assert not result.ok

    def test_page_numbers_across_chapters_sequential(self):
        """Pages must be globally sequential across chapter boundaries."""
        rules = TemplateRules(default_template="full-bleed")
        book = plan_book(
            [ChapterSpec(title="A", item_count=3),
             ChapterSpec(title="B", item_count=2)],
            template_rules=rules,
        )
        result = validate_book(book)
        assert result.ok
        all_pages = [p for c in book.chapters for p in c.pages]
        nums = [p.page_number for p in all_pages]
        assert nums == list(range(1, 6))

    def test_plan_book_always_produces_valid_page_numbers(self):
        """plan_book() should always produce a numbering-valid book."""
        for item_counts in [(4,), (4, 8), (1, 1, 1), (7, 3, 5)]:
            book = _make_valid_book(item_counts)
            result = validate_book(book)
            numbering_errors = [
                e for e in result.errors if "sequential" in e
            ]
            assert numbering_errors == [], (
                f"item_counts={item_counts} produced numbering errors: {numbering_errors}"
            )
