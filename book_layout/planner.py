"""
book_layout.planner
===================
Core layout-planning logic.

Public API
----------
paginate(items, slots_per_page) -> list[list]
    Pure-math pagination: distribute N items across pages of `slots_per_page`
    slots each.  Last page may be underfull.  Raises ValueError for
    slots_per_page <= 0.

plan_chapter(spec, rules, start_page) -> Chapter
    Build a Chapter from a ChapterSpec: select the best template, flow items
    across pages, fill slots with opaque content indices.

plan_book(chapter_specs, ...) -> Book
    Assemble a full Book: build chapters in order with globally sequential
    page numbers.

Supporting types
----------------
ChapterSpec     title, item_count, theme, book_format
TemplateRules   threshold list + default fallback for template selection

Privacy boundary
----------------
`content_ref` values assigned to ImageSlots are opaque integers (indices
into the caller's own item list).  No file paths, URLs, names, or
identifiable-person data enter this module.

Refs: claude-skills#210
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, List, Optional

from .schema import Book, BookFormat, Chapter, Page, PageSize
from .templates import get_template


# ── public data structures ────────────────────────────────────────────────────

@dataclass
class ChapterSpec:
    """Input spec for one chapter.

    `item_count` is the number of abstract content items (photos, renders,
    design spreads, …) to flow into this chapter.  No actual item objects
    are passed here; the planner uses the count to select templates and
    assigns opaque integer indices (0 … item_count-1) to slots.
    """
    title: str
    item_count: int
    theme: str = ""
    book_format: BookFormat = BookFormat.PHOTO_BOOK

    def __post_init__(self) -> None:
        if self.item_count < 0:
            raise ValueError(f"item_count must be >= 0, got {self.item_count}")


@dataclass
class TemplateRules:
    """Rules for selecting a template name given an item count.

    `thresholds` is a list of (max_items, template_name) pairs.  They are
    evaluated in ascending order; the first threshold >= item_count wins.
    If no threshold matches, `default_template` is used.

    Example::

        rules = TemplateRules(
            thresholds=[(1, "full-bleed"), (3, "hero+caption"), (5, "collage")],
            default_template="grid-2x2",
        )
        rules.select(1)   # -> "full-bleed"
        rules.select(4)   # -> "collage"
        rules.select(10)  # -> "grid-2x2"
    """
    thresholds: List[tuple] = field(default_factory=list)
    default_template: str = "hero+caption"

    def select(self, item_count: int) -> str:
        for threshold, tname in sorted(self.thresholds, key=lambda x: x[0]):
            if item_count <= threshold:
                return tname
        return self.default_template


# ── internal helpers ──────────────────────────────────────────────────────────

_DEFAULT_RULES = TemplateRules(
    thresholds=[
        (1, "full-bleed"),
        (3, "hero+caption"),
        (5, "collage"),
    ],
    default_template="grid-2x2",
)


def _effective_rules(rules: Optional[TemplateRules]) -> TemplateRules:
    return rules if rules is not None else _DEFAULT_RULES


def _build_page(
    page_number: int,
    template_name: str,
    chunk: List[Any],
) -> Page:
    """Instantiate a Page from a template, filling slots with chunk items.

    `chunk` items are opaque; only their position (index) is recorded as
    `content_ref` on each slot.  No actual item data is stored.
    """
    tmpl = get_template(template_name)
    slots = tmpl.make_slots(page_index=page_number)
    texts = tmpl.make_text_blocks(page_index=page_number)

    for local_idx, _item in enumerate(chunk):
        if local_idx < len(slots):
            slots[local_idx].fill(content_ref=local_idx)

    return Page(
        page_number=page_number,
        template_name=template_name,
        image_slots=slots,
        text_blocks=texts,
    )


# ── public API ────────────────────────────────────────────────────────────────

def paginate(items: List[Any], slots_per_page: int) -> List[List[Any]]:
    """Distribute `items` across pages of `slots_per_page` slots each.

    Returns a list-of-lists.  The last page may contain fewer items than
    `slots_per_page` (underfull page).  An empty `items` list returns [].

    Raises ValueError if `slots_per_page` <= 0.

    Examples::

        paginate([1,2,3,4,5], 2)  # -> [[1,2],[3,4],[5]]
        paginate([], 3)            # -> []
        paginate([1], 4)           # -> [[1]]   (underfull)
    """
    if slots_per_page <= 0:
        raise ValueError(f"slots_per_page must be > 0, got {slots_per_page!r}")
    if not items:
        return []
    page_count = math.ceil(len(items) / slots_per_page)
    return [
        items[i * slots_per_page : (i + 1) * slots_per_page]
        for i in range(page_count)
    ]


def plan_chapter(
    spec: ChapterSpec,
    rules: Optional[TemplateRules] = None,
    start_page: int = 1,
) -> Chapter:
    """Build a Chapter from a ChapterSpec.

    Selects the best-fit template via `rules`, then:
      1. Derives `slots_per_page` from the template's slot count.
      2. Paginates `spec.item_count` abstract items across pages.
      3. Fills each page's slots with opaque content-ref indices.

    Returns a fully-structured Chapter with globally-anchored page numbers
    starting at `start_page`.
    """
    effective = _effective_rules(rules)
    template_name = effective.select(spec.item_count)
    tmpl = get_template(template_name)
    slots_per_page = tmpl.slot_count

    # Abstract items are just integer indices — no real content.
    abstract_items: List[int] = list(range(spec.item_count))

    if not abstract_items:
        # Zero-item chapter: one empty placeholder page
        empty_page = _build_page(start_page, template_name, [])
        return Chapter(title=spec.title, theme=spec.theme, pages=[empty_page])

    chunks = paginate(abstract_items, slots_per_page)
    pages = [
        _build_page(start_page + i, template_name, chunk)
        for i, chunk in enumerate(chunks)
    ]
    return Chapter(title=spec.title, theme=spec.theme, pages=pages)


def plan_book(
    chapter_specs: List[ChapterSpec],
    book_title: str = "Untitled Book",
    book_format: BookFormat = BookFormat.PHOTO_BOOK,
    page_size: PageSize = PageSize.LETTER,
    template_rules: Optional[TemplateRules] = None,
) -> Book:
    """Assemble a full Book from a list of ChapterSpecs.

    Chapters are built in order.  Page numbers are globally sequential across
    all chapters (page 1 of chapter 2 follows the last page of chapter 1).

    Args:
        chapter_specs:    ordered list of ChapterSpec inputs
        book_title:       title for the assembled Book
        book_format:      BookFormat enum value
        page_size:        PageSize enum value
        template_rules:   optional TemplateRules; defaults apply if None

    Returns:
        A fully-structured Book with chapters, pages, and filled slots.
    """
    chapters: List[Chapter] = []
    current_page = 1

    for spec in chapter_specs:
        chapter = plan_chapter(spec, rules=template_rules, start_page=current_page)
        chapters.append(chapter)
        current_page += chapter.page_count

    return Book(
        title=book_title,
        book_format=book_format,
        page_size=page_size,
        chapters=chapters,
    )
