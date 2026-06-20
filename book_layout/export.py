"""
book_layout.export
==================
Export and serialization layer for the book layout engine.

Produces a **BookManifest** — a print-ready descriptor that a downstream
renderer (image-gen-2 pipeline, InDesign script, PDF engine) can consume.
The manifest describes pages, slots, dimensions, and spread metadata as
plain data.  It contains no real images.

Public API
----------
export_book(book, page_size_config, theme)  -> BookManifest
to_json(book)                               -> str   (compact JSON)
from_json(json_str)                         -> Book  (round-trip)
manifest_to_json(manifest)                  -> str

PageSizeConfig
    Physical dimensions for a PageSize enum value (width_mm, height_mm,
    bleed_mm, margin_mm).  Built-in configs for letter, a4, square, spread.

BookManifest
    Flat, renderer-friendly view of the book.
    - metadata: title, format, page_size, total_pages, theme_name
    - page_manifests: one PageManifest per page
    - slot_manifests: denormalised list of all slots (for quick iteration)

Refs: claude-skills#210 (#93, #101)
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from .schema import Book, BookFormat, Chapter, Page, PageSize
from .themes import Theme, get_theme_for_format


# ── physical page dimensions ──────────────────────────────────────────────────

@dataclass
class PageSizeConfig:
    """Physical page dimensions in millimetres."""
    width_mm: float
    height_mm: float
    bleed_mm: float = 3.0
    margin_mm: float = 12.0

    @property
    def printable_width_mm(self) -> float:
        return self.width_mm - 2 * self.margin_mm

    @property
    def printable_height_mm(self) -> float:
        return self.height_mm - 2 * self.margin_mm

    @property
    def total_width_mm(self) -> float:
        """Including bleed."""
        return self.width_mm + 2 * self.bleed_mm

    @property
    def total_height_mm(self) -> float:
        return self.height_mm + 2 * self.bleed_mm


# Standard page-size configs
PAGE_SIZE_CONFIGS: Dict[str, PageSizeConfig] = {
    PageSize.LETTER: PageSizeConfig(width_mm=215.9, height_mm=279.4),
    PageSize.A4:     PageSizeConfig(width_mm=210.0, height_mm=297.0),
    PageSize.SQUARE: PageSizeConfig(width_mm=304.8, height_mm=304.8),
    PageSize.SPREAD: PageSizeConfig(width_mm=431.8, height_mm=279.4),  # 2× letter width
}


def get_page_size_config(page_size: PageSize) -> PageSizeConfig:
    return PAGE_SIZE_CONFIGS[page_size]


# ── manifest data structures ──────────────────────────────────────────────────

@dataclass
class SlotManifest:
    """Renderer-ready descriptor for one image slot."""
    slot_id: str
    page_number: int
    chapter_title: str
    role: str
    aspect_ratio: float
    filled: bool
    content_ref: Optional[int]
    # Advisory geometry (approximate — final layout is the renderer's job)
    approx_width_mm: float = 0.0
    approx_height_mm: float = 0.0


@dataclass
class PageManifest:
    """Renderer-ready descriptor for one page."""
    page_number: int
    chapter_title: str
    template_name: str
    slot_count: int
    filled_slot_count: int
    unfilled_slot_count: int
    text_block_count: int
    slots: List[SlotManifest] = field(default_factory=list)


@dataclass
class BookManifest:
    """Flat, renderer-friendly view of an entire book."""
    # metadata
    title: str
    book_format: str
    page_size: str
    total_pages: int
    total_slots: int
    filled_slots: int
    chapter_count: int
    theme_name: str
    # per-page descriptors
    page_manifests: List[PageManifest] = field(default_factory=list)
    # denormalised slot list (for quick iteration across the whole book)
    all_slots: List[SlotManifest] = field(default_factory=list)

    @property
    def unfilled_slots(self) -> int:
        return self.total_slots - self.filled_slots

    @property
    def fill_rate(self) -> float:
        if self.total_slots == 0:
            return 1.0
        return self.filled_slots / self.total_slots


# ── geometry helpers ──────────────────────────────────────────────────────────

def _approx_slot_geometry(
    aspect_ratio: float,
    printable_width_mm: float,
    printable_height_mm: float,
    slot_count: int,
) -> tuple[float, float]:
    """Rough slot dimensions assuming equal-area grid layout."""
    if slot_count <= 0:
        return (printable_width_mm, printable_height_mm)
    # Approximate: divide printable area evenly
    cols = max(1, round(slot_count ** 0.5))
    rows = (slot_count + cols - 1) // cols
    cell_w = printable_width_mm / cols
    cell_h = printable_height_mm / rows
    # Fit aspect ratio within cell
    if cell_w / cell_h > aspect_ratio:
        w = cell_h * aspect_ratio
        h = cell_h
    else:
        w = cell_w
        h = cell_w / aspect_ratio
    return round(w, 1), round(h, 1)


# ── export ────────────────────────────────────────────────────────────────────

def export_book(
    book: Book,
    page_size_config: Optional[PageSizeConfig] = None,
    theme: Optional[Theme] = None,
) -> BookManifest:
    """Produce a BookManifest from a Book.

    Args:
        book:             the Book to export
        page_size_config: physical dimensions; defaults to built-in for book.page_size
        theme:            design theme; defaults to the best match for book.book_format
    """
    if page_size_config is None:
        page_size_config = get_page_size_config(book.page_size)
    if theme is None:
        theme = get_theme_for_format(book.book_format.value)

    pw = page_size_config.printable_width_mm
    ph = page_size_config.printable_height_mm

    page_manifests: List[PageManifest] = []
    all_slots: List[SlotManifest] = []

    for chapter in book.chapters:
        for page in chapter.pages:
            slot_manifests: List[SlotManifest] = []
            for slot in page.image_slots:
                approx_w, approx_h = _approx_slot_geometry(
                    slot.aspect_ratio, pw, ph, page.slot_count
                )
                sm = SlotManifest(
                    slot_id=slot.slot_id,
                    page_number=page.page_number,
                    chapter_title=chapter.title,
                    role=slot.role.value,
                    aspect_ratio=slot.aspect_ratio,
                    filled=slot.filled,
                    content_ref=slot.content_ref,
                    approx_width_mm=approx_w,
                    approx_height_mm=approx_h,
                )
                slot_manifests.append(sm)
                all_slots.append(sm)

            pm = PageManifest(
                page_number=page.page_number,
                chapter_title=chapter.title,
                template_name=page.template_name,
                slot_count=page.slot_count,
                filled_slot_count=page.filled_slot_count,
                unfilled_slot_count=page.unfilled_slot_count,
                text_block_count=len(page.text_blocks),
                slots=slot_manifests,
            )
            page_manifests.append(pm)

    return BookManifest(
        title=book.title,
        book_format=book.book_format.value,
        page_size=book.page_size.value,
        total_pages=book.total_pages,
        total_slots=book.total_slots,
        filled_slots=book.filled_slots,
        chapter_count=len(book.chapters),
        theme_name=theme.name,
        page_manifests=page_manifests,
        all_slots=all_slots,
    )


# ── serialization ─────────────────────────────────────────────────────────────

def to_json(book: Book, indent: Optional[int] = None) -> str:
    """Serialise a Book to JSON string."""
    return book.model_dump_json(indent=indent)


def from_json(json_str: str) -> Book:
    """Deserialise a Book from a JSON string (round-trip)."""
    return Book.model_validate_json(json_str)


def manifest_to_json(manifest: BookManifest, indent: Optional[int] = 2) -> str:
    """Serialise a BookManifest to JSON string."""
    return json.dumps(asdict(manifest), indent=indent)


def manifest_to_dict(manifest: BookManifest) -> Dict[str, Any]:
    return asdict(manifest)
