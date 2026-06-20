"""
book_layout.spreads
===================
2-page spread planner — pairs consecutive pages into editorial spread units.

A *spread* is the fundamental visual unit of print design: two facing pages
that are seen together and composed as a single visual statement.  This module
models spreads as first-class objects and provides:

  Spread              A left+right page pair with dominant-visual metadata
  SpreadConfig        Configuration for spread planning (dominant side, gap policy)
  pair_into_spreads() Pair a page list into Spread objects
  plan_spread_book()  Plan an entire book where every chapter uses spread-aware
                      layout (chapters have even page counts; the 'spread' template
                      is the default for multi-item chapters)
  spread_summary()    Human-readable summary of spread counts and fill rates

Dominant-visual assignment
--------------------------
Each spread has a `dominant_side` ("left" or "right") that controls which page
carries the hero/full-bleed slot.  This follows the theme's spread_grammar.

Odd-page handling
-----------------
When a chapter has an odd number of pages, the final page is a "solo" page with
no facing partner.  It is represented as a Spread with `right_page=None`.

Privacy boundary
----------------
No real image data.  Slot content_ref values are opaque ints.

Refs: claude-skills#210
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional

from .schema import Book, BookFormat, Chapter, Page, PageSize
from .planner import ChapterSpec, TemplateRules, plan_book, plan_chapter
from .themes import Theme, get_theme_for_format


# ── spread config ─────────────────────────────────────────────────────────────

@dataclass
class SpreadConfig:
    """Configuration for spread-level layout planning."""
    dominant_side: str = "left"           # "left" | "right"
    solo_page_template: str = "full-bleed"
    default_multi_template: str = "spread"  # the 3-slot spread template
    alternate_dominant: bool = True       # flip dominant_side on every spread
    chapter_template_rules: Optional[TemplateRules] = None


# ── spread model ──────────────────────────────────────────────────────────────

@dataclass
class Spread:
    """One 2-page spread: left + right pages as an editorial unit.

    `right_page` is None when the chapter has an odd page count (solo page).
    """
    spread_number: int            # 1-based within the chapter
    left_page: Page
    right_page: Optional[Page]
    dominant_side: str = "left"   # which side holds the hero/full-bleed slot
    chapter_title: str = ""

    @property
    def left_page_number(self) -> int:
        return self.left_page.page_number

    @property
    def right_page_number(self) -> Optional[int]:
        return self.right_page.page_number if self.right_page else None

    @property
    def is_solo(self) -> bool:
        return self.right_page is None

    @property
    def total_slots(self) -> int:
        right_slots = self.right_page.slot_count if self.right_page else 0
        return self.left_page.slot_count + right_slots

    @property
    def filled_slots(self) -> int:
        right_filled = self.right_page.filled_slot_count if self.right_page else 0
        return self.left_page.filled_slot_count + right_filled

    @property
    def unfilled_slots(self) -> int:
        return self.total_slots - self.filled_slots

    @property
    def dominant_page(self) -> Page:
        if self.dominant_side == "right" and self.right_page is not None:
            return self.right_page
        return self.left_page

    @property
    def supporting_page(self) -> Optional[Page]:
        if self.dominant_side == "right":
            return self.left_page
        return self.right_page


# ── core functions ────────────────────────────────────────────────────────────

def pair_into_spreads(
    pages: List[Page],
    chapter_title: str = "",
    config: Optional[SpreadConfig] = None,
) -> List[Spread]:
    """Pair consecutive pages into Spread objects.

    Odd-numbered final pages become solo spreads (right_page=None).

    Args:
        pages:          ordered page list (page_number may be anything)
        chapter_title:  advisory label for the spreads
        config:         SpreadConfig; defaults applied if None

    Returns:
        List of Spread objects, len == ceil(len(pages) / 2).
    """
    cfg = config or SpreadConfig()
    spreads: List[Spread] = []

    for i in range(0, len(pages), 2):
        spread_number = i // 2 + 1
        left = pages[i]
        right = pages[i + 1] if (i + 1) < len(pages) else None

        # Alternate dominant side if configured
        if cfg.alternate_dominant:
            dominant = "left" if (spread_number % 2 == 1) else "right"
        else:
            dominant = cfg.dominant_side

        spreads.append(Spread(
            spread_number=spread_number,
            left_page=left,
            right_page=right,
            dominant_side=dominant,
            chapter_title=chapter_title,
        ))

    return spreads


def spreads_for_chapter(
    chapter: Chapter,
    config: Optional[SpreadConfig] = None,
) -> List[Spread]:
    """Produce spreads for an existing Chapter."""
    return pair_into_spreads(
        pages=chapter.pages,
        chapter_title=chapter.title,
        config=config,
    )


def spreads_for_book(
    book: Book,
    config: Optional[SpreadConfig] = None,
) -> dict[str, List[Spread]]:
    """Return a mapping of chapter_title → [Spread] for the whole book."""
    result: dict[str, List[Spread]] = {}
    for chapter in book.chapters:
        result[chapter.title] = spreads_for_chapter(chapter, config)
    return result


def plan_spread_chapter(
    spec: ChapterSpec,
    start_page: int = 1,
    config: Optional[SpreadConfig] = None,
) -> tuple[Chapter, List[Spread]]:
    """Plan a chapter with spread-aware layout and return (Chapter, spreads).

    For items that pair naturally into spreads (even counts), uses the
    'spread' template (3 slots: 1 full-bleed hero + 2 supporting).
    For a single item or odd totals, the last page uses solo_page_template.

    Returns:
        (Chapter, list[Spread]) — chapter ready to insert into a Book, plus
        the spread pairing for editorial review.
    """
    cfg = config or SpreadConfig()
    rules = cfg.chapter_template_rules or TemplateRules(
        thresholds=[(1, cfg.solo_page_template)],
        default_template=cfg.default_multi_template,
    )
    chapter = plan_chapter(spec, rules=rules, start_page=start_page)
    spreads = spreads_for_chapter(chapter, config=cfg)
    return chapter, spreads


def plan_spread_book(
    chapter_specs: List[ChapterSpec],
    book_title: str = "Untitled Book",
    book_format: BookFormat = BookFormat.YEARBOOK,
    page_size: PageSize = PageSize.SPREAD,
    config: Optional[SpreadConfig] = None,
) -> tuple[Book, dict[str, List[Spread]]]:
    """Plan a Book where all chapters use spread-aware layout.

    Returns:
        (Book, spread_map) where spread_map is chapter_title → [Spread].
    """
    cfg = config or SpreadConfig()
    rules = cfg.chapter_template_rules or TemplateRules(
        thresholds=[(1, cfg.solo_page_template)],
        default_template=cfg.default_multi_template,
    )

    book = plan_book(
        chapter_specs,
        book_title=book_title,
        book_format=book_format,
        page_size=page_size,
        template_rules=rules,
    )
    spread_map = spreads_for_book(book, config=cfg)
    return book, spread_map


# ── summary helpers ───────────────────────────────────────────────────────────

@dataclass
class SpreadSummary:
    total_spreads: int
    solo_spreads: int
    full_spreads: int
    total_slots: int
    filled_slots: int
    fill_rate: float

    def __repr__(self) -> str:
        return (
            f"SpreadSummary("
            f"spreads={self.total_spreads} "
            f"[{self.full_spreads} full + {self.solo_spreads} solo], "
            f"slots={self.filled_slots}/{self.total_slots} "
            f"fill={self.fill_rate:.0%})"
        )


def spread_summary(spreads: List[Spread]) -> SpreadSummary:
    """Compute aggregate statistics for a list of Spread objects."""
    total = len(spreads)
    solos = sum(1 for s in spreads if s.is_solo)
    total_slots = sum(s.total_slots for s in spreads)
    filled_slots = sum(s.filled_slots for s in spreads)
    fill_rate = filled_slots / total_slots if total_slots > 0 else 1.0
    return SpreadSummary(
        total_spreads=total,
        solo_spreads=solos,
        full_spreads=total - solos,
        total_slots=total_slots,
        filled_slots=filled_slots,
        fill_rate=fill_rate,
    )


def chapter_spread_summary(book: Book, config: Optional[SpreadConfig] = None) -> dict:
    """Return a per-chapter spread summary dict for reporting."""
    result = {}
    for chapter in book.chapters:
        spreads = spreads_for_chapter(chapter, config=config)
        result[chapter.title] = {
            "page_count": chapter.page_count,
            "spread_count": len(spreads),
            "solo_spreads": sum(1 for s in spreads if s.is_solo),
            "total_slots": chapter.total_slots,
            "filled_slots": chapter.filled_slots,
        }
    return result
