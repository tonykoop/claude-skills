"""
Tests for book_layout.spreads — pair_into_spreads(), plan_spread_book(),
SpreadSummary, dominant-visual assignment.

All tests offline and deterministic.

Refs: claude-skills#210
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from book_layout.planner import ChapterSpec, TemplateRules, plan_book, plan_chapter
from book_layout.schema import BookFormat, Page, PageSize
from book_layout.spreads import (
    Spread, SpreadConfig, SpreadSummary,
    chapter_spread_summary, pair_into_spreads, plan_spread_book,
    plan_spread_chapter, spread_summary, spreads_for_book, spreads_for_chapter,
)
from book_layout.validator import validate_book


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_pages(n: int, template: str = "full-bleed") -> list:
    """Make n filled pages via the planner."""
    rules = TemplateRules(default_template=template)
    ch = plan_chapter(
        ChapterSpec(title="T", item_count=n),
        rules=rules,
        start_page=1,
    )
    return ch.pages


# ── pair_into_spreads() ───────────────────────────────────────────────────────

class TestPairIntoSpreads:
    def test_even_pages_all_full_spreads(self):
        pages = _make_pages(4)
        spreads = pair_into_spreads(pages)
        assert len(spreads) == 2
        assert all(not s.is_solo for s in spreads)

    def test_odd_pages_last_is_solo(self):
        pages = _make_pages(5)
        spreads = pair_into_spreads(pages)
        assert len(spreads) == 3
        assert spreads[-1].is_solo
        assert spreads[-1].right_page is None
        assert not any(s.is_solo for s in spreads[:-1])

    def test_single_page_solo_spread(self):
        pages = _make_pages(1)
        spreads = pair_into_spreads(pages)
        assert len(spreads) == 1
        assert spreads[0].is_solo

    def test_empty_returns_empty(self):
        assert pair_into_spreads([]) == []

    def test_two_pages_one_spread(self):
        pages = _make_pages(2)
        spreads = pair_into_spreads(pages)
        assert len(spreads) == 1
        assert not spreads[0].is_solo

    def test_spread_number_1_based(self):
        spreads = pair_into_spreads(_make_pages(6))
        assert [s.spread_number for s in spreads] == [1, 2, 3]

    def test_chapter_title_propagated(self):
        pages = _make_pages(2)
        spreads = pair_into_spreads(pages, chapter_title="My Chapter")
        assert all(s.chapter_title == "My Chapter" for s in spreads)

    def test_left_right_page_assignment(self):
        pages = _make_pages(4)
        spreads = pair_into_spreads(pages)
        assert spreads[0].left_page.page_number == 1
        assert spreads[0].right_page.page_number == 2
        assert spreads[1].left_page.page_number == 3
        assert spreads[1].right_page.page_number == 4

    def test_dominant_side_alternates_by_default(self):
        pages = _make_pages(6)
        spreads = pair_into_spreads(pages, config=SpreadConfig(alternate_dominant=True))
        sides = [s.dominant_side for s in spreads]
        assert sides == ["left", "right", "left"]

    def test_fixed_dominant_side(self):
        pages = _make_pages(4)
        cfg = SpreadConfig(dominant_side="right", alternate_dominant=False)
        spreads = pair_into_spreads(pages, config=cfg)
        assert all(s.dominant_side == "right" for s in spreads)


# ── Spread properties ─────────────────────────────────────────────────────────

class TestSpreadProperties:
    def _spread(self, n_pages: int = 2) -> Spread:
        pages = _make_pages(n_pages)
        return pair_into_spreads(pages)[0]

    def test_total_slots_full_spread(self):
        s = self._spread(2)
        assert s.total_slots == s.left_page.slot_count + s.right_page.slot_count

    def test_filled_slots(self):
        s = self._spread(2)
        # full-bleed template: 1 slot / page, both filled
        assert s.filled_slots == 2

    def test_dominant_page_left_default(self):
        s = self._spread(2)
        # spread_number=1 → dominant_side="left" with alternation
        assert s.dominant_page is s.left_page

    def test_dominant_page_right(self):
        pages = _make_pages(2)
        s = pair_into_spreads(pages, config=SpreadConfig(dominant_side="right", alternate_dominant=False))[0]
        assert s.dominant_page is s.right_page

    def test_solo_dominant_page_is_left(self):
        pages = _make_pages(1)
        s = pair_into_spreads(pages)[0]
        assert s.is_solo
        assert s.dominant_page is s.left_page

    def test_page_numbers(self):
        pages = _make_pages(2)
        s = pair_into_spreads(pages)[0]
        assert s.left_page_number == 1
        assert s.right_page_number == 2

    def test_solo_right_page_number_none(self):
        pages = _make_pages(1)
        s = pair_into_spreads(pages)[0]
        assert s.right_page_number is None


# ── spreads_for_chapter() ─────────────────────────────────────────────────────

class TestSpreadsForChapter:
    def test_even_chapter(self):
        rules = TemplateRules(default_template="full-bleed")
        ch = plan_chapter(ChapterSpec(title="C", item_count=4), rules=rules)
        spreads = spreads_for_chapter(ch)
        assert len(spreads) == 2
        assert ch.title == spreads[0].chapter_title

    def test_odd_chapter(self):
        rules = TemplateRules(default_template="full-bleed")
        ch = plan_chapter(ChapterSpec(title="C", item_count=3), rules=rules)
        spreads = spreads_for_chapter(ch)
        assert len(spreads) == 2
        assert spreads[-1].is_solo


# ── spreads_for_book() ────────────────────────────────────────────────────────

class TestSpreadsForBook:
    def test_spread_map_keys_are_chapter_titles(self):
        rules = TemplateRules(default_template="full-bleed")
        book = plan_book(
            [ChapterSpec(title="A", item_count=2),
             ChapterSpec(title="B", item_count=4)],
            template_rules=rules,
        )
        smap = spreads_for_book(book)
        assert set(smap.keys()) == {"A", "B"}

    def test_spread_count_per_chapter(self):
        rules = TemplateRules(default_template="full-bleed")
        book = plan_book(
            [ChapterSpec(title="A", item_count=4)],
            template_rules=rules,
        )
        smap = spreads_for_book(book)
        assert len(smap["A"]) == 2   # 4 pages → 2 spreads


# ── plan_spread_chapter() ─────────────────────────────────────────────────────

class TestPlanSpreadChapter:
    def test_returns_chapter_and_spreads(self):
        spec = ChapterSpec(title="S", item_count=3)
        ch, spreads = plan_spread_chapter(spec)
        assert ch.title == "S"
        assert len(spreads) > 0

    def test_spread_template_used(self):
        spec = ChapterSpec(title="S", item_count=6)
        ch, _ = plan_spread_chapter(spec)
        # default_multi_template="spread" → 3 slots/page
        assert all(p.template_name == "spread" for p in ch.pages)

    def test_start_page_propagated(self):
        spec = ChapterSpec(title="S", item_count=3)
        ch, _ = plan_spread_chapter(spec, start_page=7)
        assert ch.pages[0].page_number == 7


# ── plan_spread_book() ────────────────────────────────────────────────────────

class TestPlanSpreadBook:
    def test_returns_book_and_map(self):
        specs = [ChapterSpec(title="A", item_count=6),
                 ChapterSpec(title="B", item_count=3)]
        book, smap = plan_spread_book(specs)
        assert book.total_pages > 0
        assert set(smap.keys()) == {"A", "B"}

    def test_page_numbers_sequential(self):
        specs = [ChapterSpec(title="A", item_count=6),
                 ChapterSpec(title="B", item_count=3)]
        book, _ = plan_spread_book(specs)
        result = validate_book(book)
        assert not any("sequential" in e for e in result.errors)

    def test_book_format_default_yearbook(self):
        book, _ = plan_spread_book([ChapterSpec(title="A", item_count=3)])
        assert book.book_format == BookFormat.YEARBOOK


# ── spread_summary() ─────────────────────────────────────────────────────────

class TestSpreadSummary:
    def test_summary_counts(self):
        pages = _make_pages(5)
        spreads = pair_into_spreads(pages)
        summ = spread_summary(spreads)
        assert summ.total_spreads == 3
        assert summ.solo_spreads == 1
        assert summ.full_spreads == 2

    def test_fill_rate_all_filled(self):
        pages = _make_pages(4)
        spreads = pair_into_spreads(pages)
        summ = spread_summary(spreads)
        assert summ.fill_rate == pytest.approx(1.0)

    def test_empty_spread_list(self):
        summ = spread_summary([])
        assert summ.total_spreads == 0
        assert summ.fill_rate == pytest.approx(1.0)   # vacuously full

    def test_repr_contains_key_info(self):
        pages = _make_pages(4)
        spreads = pair_into_spreads(pages)
        r = repr(spread_summary(spreads))
        assert "spreads=2" in r
        assert "fill=" in r


# ── chapter_spread_summary() ─────────────────────────────────────────────────

class TestChapterSpreadSummary:
    def test_summary_dict_has_expected_keys(self):
        rules = TemplateRules(default_template="full-bleed")
        book = plan_book(
            [ChapterSpec(title="Ch1", item_count=4)],
            template_rules=rules,
        )
        result = chapter_spread_summary(book)
        assert "Ch1" in result
        ch_data = result["Ch1"]
        for key in ("page_count", "spread_count", "solo_spreads",
                    "total_slots", "filled_slots"):
            assert key in ch_data

    def test_spread_count_is_ceil_half_pages(self):
        import math
        rules = TemplateRules(default_template="full-bleed")
        for n in range(1, 8):
            book = plan_book(
                [ChapterSpec(title="C", item_count=n)], template_rules=rules
            )
            result = chapter_spread_summary(book)
            expected_pages = book.chapters[0].page_count
            expected_spreads = math.ceil(expected_pages / 2)
            assert result["C"]["spread_count"] == expected_spreads
