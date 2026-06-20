"""
Tests for book_layout.planner — pagination math, template selection,
chapter assembly, and full book assembly.

All tests are offline and deterministic.  No real images or person data.

Refs: claude-skills#210
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from book_layout.planner import (
    ChapterSpec, TemplateRules, paginate, plan_book, plan_chapter,
)
from book_layout.schema import BookFormat, PageSize


# ── paginate() ────────────────────────────────────────────────────────────────

class TestPaginate:
    def test_exact_fit(self):
        """4 items into 2 slots/page → 2 full pages."""
        result = paginate([1, 2, 3, 4], 2)
        assert result == [[1, 2], [3, 4]]

    def test_underfull_last_page(self):
        """5 items into 2 slots/page → 2 full + 1 half-full."""
        result = paginate([1, 2, 3, 4, 5], 2)
        assert result == [[1, 2], [3, 4], [5]]

    def test_single_page(self):
        result = paginate([1, 2], 4)
        assert result == [[1, 2]]   # underfull, 1 page

    def test_single_item(self):
        assert paginate([99], 3) == [[99]]

    def test_empty_list_returns_empty(self):
        assert paginate([], 3) == []

    def test_one_slot_per_page(self):
        items = list(range(5))
        result = paginate(items, 1)
        assert result == [[0], [1], [2], [3], [4]]

    def test_large_batch(self):
        items = list(range(100))
        result = paginate(items, 4)
        assert len(result) == 25
        assert result[0] == [0, 1, 2, 3]
        assert result[-1] == [96, 97, 98, 99]

    def test_page_count_math(self):
        """Verify ceiling-division page count for various sizes."""
        for n_items in range(1, 20):
            for slots in range(1, 6):
                pages = paginate(list(range(n_items)), slots)
                assert len(pages) == math.ceil(n_items / slots)

    def test_all_items_appear_exactly_once(self):
        items = list(range(17))
        pages = paginate(items, 3)
        flat = [item for page in pages for item in page]
        assert flat == items

    def test_zero_slots_raises(self):
        with pytest.raises(ValueError, match="slots_per_page must be > 0"):
            paginate([1, 2, 3], 0)

    def test_negative_slots_raises(self):
        with pytest.raises(ValueError):
            paginate([1, 2, 3], -1)

    def test_non_integer_items_preserved(self):
        items = ["a", "b", "c"]
        assert paginate(items, 2) == [["a", "b"], ["c"]]


# ── TemplateRules ─────────────────────────────────────────────────────────────

class TestTemplateRules:
    def _rules(self):
        return TemplateRules(
            thresholds=[(1, "full-bleed"), (3, "hero+caption"), (5, "collage")],
            default_template="grid-2x2",
        )

    def test_exact_threshold_match(self):
        rules = self._rules()
        assert rules.select(1) == "full-bleed"
        assert rules.select(3) == "hero+caption"
        assert rules.select(5) == "collage"

    def test_below_threshold_uses_first_match(self):
        rules = self._rules()
        # 0 items <= 1 → full-bleed
        assert rules.select(0) == "full-bleed"

    def test_above_all_thresholds_uses_default(self):
        rules = self._rules()
        assert rules.select(6) == "grid-2x2"
        assert rules.select(100) == "grid-2x2"

    def test_default_only(self):
        rules = TemplateRules(default_template="spread")
        assert rules.select(99) == "spread"

    def test_unsorted_thresholds_still_work(self):
        rules = TemplateRules(
            thresholds=[(5, "collage"), (1, "full-bleed"), (3, "hero+caption")],
            default_template="grid-2x2",
        )
        assert rules.select(2) == "hero+caption"


# ── ChapterSpec ───────────────────────────────────────────────────────────────

class TestChapterSpec:
    def test_basic_creation(self):
        spec = ChapterSpec(title="Intro", item_count=5, theme="blue")
        assert spec.title == "Intro"
        assert spec.item_count == 5
        assert spec.theme == "blue"

    def test_negative_item_count_raises(self):
        with pytest.raises(ValueError):
            ChapterSpec(title="Bad", item_count=-1)

    def test_zero_item_count_ok(self):
        spec = ChapterSpec(title="Empty", item_count=0)
        assert spec.item_count == 0


# ── plan_chapter() ────────────────────────────────────────────────────────────

class TestPlanChapter:
    def test_chapter_title_and_theme(self):
        spec = ChapterSpec(title="Opening", item_count=2, theme="classic")
        ch = plan_chapter(spec)
        assert ch.title == "Opening"
        assert ch.theme == "classic"

    def test_page_count_ceiling_division(self):
        """5 items with 2-slot template → 3 pages (ceil(5/2))."""
        rules = TemplateRules(default_template="hero+caption")  # 2 slots/page
        spec = ChapterSpec(title="Test", item_count=5)
        ch = plan_chapter(spec, rules=rules)
        assert ch.page_count == 3

    def test_start_page_respected(self):
        # full-bleed = 1 slot/page → 2 items → 2 pages, starting at 5
        rules = TemplateRules(default_template="full-bleed")
        spec = ChapterSpec(title="Ch2", item_count=2)
        ch = plan_chapter(spec, rules=rules, start_page=5)
        assert len(ch.pages) == 2
        assert ch.pages[0].page_number == 5
        assert ch.pages[1].page_number == 6

    def test_slots_filled_correctly(self):
        rules = TemplateRules(default_template="hero+caption")  # 2 slots/page
        spec = ChapterSpec(title="Fill Test", item_count=3)
        ch = plan_chapter(spec, rules=rules)
        # Page 1: 2 items → both slots filled
        p1 = ch.pages[0]
        assert p1.filled_slot_count == 2
        # Page 2: 1 item → slot 0 filled, slot 1 unfilled
        p2 = ch.pages[1]
        assert p2.filled_slot_count == 1
        assert p2.unfilled_slot_count == 1

    def test_zero_item_chapter_has_one_page(self):
        spec = ChapterSpec(title="Empty", item_count=0)
        ch = plan_chapter(spec)
        assert ch.page_count == 1   # one empty placeholder page

    def test_all_slots_on_full_pages_are_filled(self):
        rules = TemplateRules(default_template="grid-2x2")  # 4 slots/page
        spec = ChapterSpec(title="Grid", item_count=8)
        ch = plan_chapter(spec, rules=rules)
        # 8 items / 4 slots = 2 exact pages
        assert ch.page_count == 2
        for page in ch.pages:
            assert page.filled_slot_count == 4

    def test_template_name_recorded_on_page(self):
        rules = TemplateRules(default_template="spread")
        spec = ChapterSpec(title="Spread Chapter", item_count=3)
        ch = plan_chapter(spec, rules=rules)
        for page in ch.pages:
            assert page.template_name == "spread"

    def test_default_rules_applied_when_none(self):
        # Default rules: 1 item → full-bleed (1 slot), so 3 pages for 3 items
        spec = ChapterSpec(title="Default", item_count=3)
        ch = plan_chapter(spec, rules=None)
        # hero+caption has 2 slots → ceil(3/2) = 2 pages
        assert ch.page_count == 2


# ── plan_book() ───────────────────────────────────────────────────────────────

class TestPlanBook:
    def _specs(self):
        return [
            ChapterSpec(title="Front Matter", item_count=1),
            ChapterSpec(title="Chapter 1",    item_count=8),
            ChapterSpec(title="Chapter 2",    item_count=5),
        ]

    def test_book_title_and_format(self):
        book = plan_book(
            self._specs(),
            book_title="Test Yearbook",
            book_format=BookFormat.YEARBOOK,
        )
        assert book.title == "Test Yearbook"
        assert book.book_format == BookFormat.YEARBOOK

    def test_chapter_count(self):
        book = plan_book(self._specs())
        assert len(book.chapters) == 3

    def test_chapter_titles_preserved(self):
        book = plan_book(self._specs())
        titles = [c.title for c in book.chapters]
        assert titles == ["Front Matter", "Chapter 1", "Chapter 2"]

    def test_page_numbers_globally_sequential(self):
        rules = TemplateRules(default_template="full-bleed")  # 1 slot/page
        specs = [
            ChapterSpec(title="A", item_count=3),
            ChapterSpec(title="B", item_count=2),
        ]
        book = plan_book(specs, template_rules=rules)
        all_pages = [p for c in book.chapters for p in c.pages]
        expected = list(range(1, 6))
        actual = [p.page_number for p in all_pages]
        assert actual == expected

    def test_total_pages_math(self):
        rules = TemplateRules(default_template="grid-2x2")  # 4 slots/page
        specs = [
            ChapterSpec(title="A", item_count=4),    # 1 page
            ChapterSpec(title="B", item_count=9),    # ceil(9/4)=3 pages
        ]
        book = plan_book(specs, template_rules=rules)
        assert book.total_pages == 4

    def test_empty_specs_produces_empty_book(self):
        book = plan_book([])
        assert book.total_pages == 0
        assert len(book.chapters) == 0

    def test_page_size_propagated(self):
        book = plan_book(self._specs(), page_size=PageSize.A4)
        assert book.page_size == PageSize.A4

    def test_custom_template_rules_applied(self):
        rules = TemplateRules(default_template="collage")  # 5 slots/page
        specs = [ChapterSpec(title="C", item_count=10)]
        book = plan_book(specs, template_rules=rules)
        # 10 items / 5 slots = 2 pages exactly
        assert book.total_pages == 2

    def test_no_file_paths_in_serialized_book(self):
        """Privacy: serialized output must not contain file path markers."""
        book = plan_book(self._specs())
        json_str = book.model_dump_json()
        for forbidden in ["/home", "/tmp", "http://", "https://", ".jpg", ".png", ".tiff"]:
            assert forbidden not in json_str, f"Forbidden string in JSON: {forbidden!r}"

    def test_content_ref_values_are_local_page_indices(self):
        """Verify content_ref is a local index [0, slot_count), not a global id."""
        rules = TemplateRules(default_template="grid-2x2")  # 4 slots/page
        specs = [ChapterSpec(title="Index Check", item_count=8)]
        book = plan_book(specs, template_rules=rules)
        for chapter in book.chapters:
            for page in chapter.pages:
                for slot in page.image_slots:
                    if slot.filled:
                        assert slot.content_ref is not None
                        assert 0 <= slot.content_ref < page.slot_count
