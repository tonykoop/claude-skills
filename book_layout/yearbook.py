"""
book_layout.yearbook
====================
High-level builder for **yearbook-style instrument design-book chapters**
(stories #92 and #100).

Each public instrument repo that has passed its quality gate gets one
polished design-book chapter.  This module models that editorial process:

  InstrumentContentSpec  How many items each section of the chapter contains
  GateStatus             Whether the instrument has passed its repo quality gate
  InstrumentChapterSpec  Full spec for one instrument chapter
  YearbookConfig         Yearbook-wide configuration
  build_instrument_chapter()   Build one instrument's Chapter
  build_yearbook()             Assemble a full yearbook Book from many instruments
  gate_check()                 Validate that all instruments have passed their gate

Chapter structure (per instrument)
-----------------------------------
Each chapter follows a fixed 4-section editorial arc (minimum viable chapter):

  1. Cover spread        — 1 hero item (3D isometric / concept render placeholder)
  2. Build gallery       — N process photos / CAD screenshots
  3. Experiment lab      — N Wolfram / parameter-sweep items
  4. Detail shots        — N close-up / dimensioned-drawing items

Sections map to pages via the standard template system; the chapter is
assembled by calling plan_chapter() for each section and concatenating.

Gate enforcement
----------------
`gate_check()` returns a list of issues for ungated instruments.
`build_instrument_chapter()` raises GateError if the instrument has not
passed its gate, unless `force=True` is explicitly set.

Privacy boundary
----------------
Item counts are abstract.  No file paths, real photos, or identifiable-person
data are stored in any schema object.

Refs: claude-skills#210 (#92, #100)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

from .schema import Book, BookFormat, Chapter, Page, PageSize
from .planner import ChapterSpec, TemplateRules, plan_chapter, plan_book
from .themes import YEARBOOK_CLASSIC, DESIGN_CHAPTER_TECHNICAL, Theme


# ── gate ──────────────────────────────────────────────────────────────────────

class GateStatus(str, Enum):
    PASSED = "passed"
    PENDING = "pending"
    FAILED = "failed"


class GateError(RuntimeError):
    """Raised when trying to build a chapter for an ungated instrument."""


# ── content spec ──────────────────────────────────────────────────────────────

@dataclass
class InstrumentContentSpec:
    """Item counts for each editorial section of an instrument chapter.

    All counts are abstract (no real photos).  Defaults match the minimum
    viable chapter described in the yearbook production workflow doc.
    """
    cover_items: int = 1          # hero: concept render / 3D isometric
    build_gallery_items: int = 6  # process photos / CAD screenshots
    experiment_lab_items: int = 3 # Wolfram / parameter-sweep visuals
    detail_shot_items: int = 4    # close-ups / dimensioned drawings

    def __post_init__(self) -> None:
        for attr in ("cover_items", "build_gallery_items",
                     "experiment_lab_items", "detail_shot_items"):
            if getattr(self, attr) < 0:
                raise ValueError(f"{attr} must be >= 0")

    @property
    def total_items(self) -> int:
        return (self.cover_items + self.build_gallery_items
                + self.experiment_lab_items + self.detail_shot_items)


# ── instrument chapter spec ───────────────────────────────────────────────────

@dataclass
class InstrumentChapterSpec:
    """Full specification for one instrument's design-book chapter."""
    repo_name: str                  # e.g. "handpan-resonance-model"
    display_name: str               # e.g. "Handpan — Resonance Model"
    gate_status: GateStatus = GateStatus.PASSED
    content: InstrumentContentSpec = field(default_factory=InstrumentContentSpec)
    theme_override: Optional[str] = None   # override the yearbook's default theme
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.repo_name:
            raise ValueError("repo_name must not be empty")
        if not self.display_name:
            self.display_name = self.repo_name


# ── yearbook config ───────────────────────────────────────────────────────────

@dataclass
class YearbookConfig:
    """Configuration for a full yearbook build."""
    title: str = "Instrument Design Yearbook"
    edition: str = ""               # e.g. "2026 Edition"
    page_size: PageSize = PageSize.LETTER
    include_index: bool = True      # placeholder index chapter at end
    # Template rules per section type
    cover_rules: Optional[TemplateRules] = None
    gallery_rules: Optional[TemplateRules] = None
    lab_rules: Optional[TemplateRules] = None
    detail_rules: Optional[TemplateRules] = None

    def full_title(self) -> str:
        if self.edition:
            return f"{self.title} — {self.edition}"
        return self.title


# ── section template rules ────────────────────────────────────────────────────

_COVER_RULES = TemplateRules(
    thresholds=[(1, "full-bleed")],
    default_template="full-bleed",
)

_GALLERY_RULES = TemplateRules(
    thresholds=[
        (2, "hero+caption"),
        (5, "collage"),
    ],
    default_template="grid-2x2",
)

_LAB_RULES = TemplateRules(
    thresholds=[
        (1, "full-bleed"),
        (3, "hero+caption"),
    ],
    default_template="collage",
)

_DETAIL_RULES = TemplateRules(
    thresholds=[
        (2, "hero+caption"),
        (5, "collage"),
    ],
    default_template="grid-2x2",
)


# ── gate check ────────────────────────────────────────────────────────────────

def gate_check(
    specs: List[InstrumentChapterSpec],
) -> Tuple[bool, List[str]]:
    """Verify all instruments have passed their gate.

    Returns (all_passed: bool, issues: list[str]).
    """
    issues: List[str] = []
    for spec in specs:
        if spec.gate_status != GateStatus.PASSED:
            issues.append(
                f"'{spec.repo_name}' gate status is '{spec.gate_status.value}' — "
                f"chapters should only be created for PASSED instruments."
            )
    return (len(issues) == 0), issues


# ── chapter builder ───────────────────────────────────────────────────────────

def build_instrument_chapter(
    spec: InstrumentChapterSpec,
    start_page: int = 1,
    config: Optional[YearbookConfig] = None,
    force: bool = False,
) -> Chapter:
    """Build one instrument's design-book Chapter from its InstrumentChapterSpec.

    The chapter has 4 sub-sections, each planned independently and assembled
    into a single Chapter with globally-anchored page numbers.

    Args:
        spec:       InstrumentChapterSpec
        start_page: first page number for this chapter (for global sequencing)
        config:     YearbookConfig (for template-rule overrides); defaults if None
        force:      if True, build even if gate_status != PASSED (for drafts)

    Raises:
        GateError: if gate_status != PASSED and force is False
    """
    if spec.gate_status != GateStatus.PASSED and not force:
        raise GateError(
            f"Instrument '{spec.repo_name}' has gate status "
            f"'{spec.gate_status.value}'. "
            f"Pass force=True to build a draft chapter anyway."
        )

    cfg = config or YearbookConfig()
    content = spec.content
    current_page = start_page
    all_pages: List[Page] = []

    # Section 1: Cover spread
    if content.cover_items > 0:
        cover_rules = cfg.cover_rules or _COVER_RULES
        cover_ch = plan_chapter(
            ChapterSpec(
                title=f"{spec.display_name} — Cover",
                item_count=content.cover_items,
                book_format=BookFormat.DESIGN_CHAPTER,
            ),
            rules=cover_rules,
            start_page=current_page,
        )
        all_pages.extend(cover_ch.pages)
        current_page += cover_ch.page_count

    # Section 2: Build gallery
    if content.build_gallery_items > 0:
        gallery_rules = cfg.gallery_rules or _GALLERY_RULES
        gallery_ch = plan_chapter(
            ChapterSpec(
                title=f"{spec.display_name} — Build Gallery",
                item_count=content.build_gallery_items,
                book_format=BookFormat.DESIGN_CHAPTER,
            ),
            rules=gallery_rules,
            start_page=current_page,
        )
        all_pages.extend(gallery_ch.pages)
        current_page += gallery_ch.page_count

    # Section 3: Experiment lab
    if content.experiment_lab_items > 0:
        lab_rules = cfg.lab_rules or _LAB_RULES
        lab_ch = plan_chapter(
            ChapterSpec(
                title=f"{spec.display_name} — Experiment Lab",
                item_count=content.experiment_lab_items,
                book_format=BookFormat.DESIGN_CHAPTER,
            ),
            rules=lab_rules,
            start_page=current_page,
        )
        all_pages.extend(lab_ch.pages)
        current_page += lab_ch.page_count

    # Section 4: Detail shots
    if content.detail_shot_items > 0:
        detail_rules = cfg.detail_rules or _DETAIL_RULES
        detail_ch = plan_chapter(
            ChapterSpec(
                title=f"{spec.display_name} — Detail Shots",
                item_count=content.detail_shot_items,
                book_format=BookFormat.DESIGN_CHAPTER,
            ),
            rules=detail_rules,
            start_page=current_page,
        )
        all_pages.extend(detail_ch.pages)

    return Chapter(
        title=spec.display_name,
        theme=spec.theme_override or "design-chapter-technical",
        pages=all_pages,
    )


# ── yearbook builder ──────────────────────────────────────────────────────────

def build_yearbook(
    instrument_specs: List[InstrumentChapterSpec],
    config: Optional[YearbookConfig] = None,
    force: bool = False,
) -> Book:
    """Assemble a full yearbook Book from many InstrumentChapterSpecs.

    Instruments are laid out in order; page numbers are globally sequential.
    An optional index chapter is appended if config.include_index is True.

    Args:
        instrument_specs:   ordered list of InstrumentChapterSpec objects
        config:             YearbookConfig; defaults if None
        force:              pass-through to build_instrument_chapter (draft mode)

    Returns:
        Fully-planned Book.

    Raises:
        GateError: if any instrument has not passed its gate and force=False
    """
    cfg = config or YearbookConfig()

    if not force:
        ok, issues = gate_check(instrument_specs)
        if not ok:
            raise GateError(
                f"{len(issues)} instrument(s) have not passed their gate:\n"
                + "\n".join(f"  • {i}" for i in issues)
            )

    chapters: List[Chapter] = []
    current_page = 1

    for spec in instrument_specs:
        chapter = build_instrument_chapter(
            spec=spec,
            start_page=current_page,
            config=cfg,
            force=force,
        )
        chapters.append(chapter)
        current_page += chapter.page_count

    # Optional index chapter (1 item placeholder per instrument)
    if cfg.include_index:
        index_spec = ChapterSpec(
            title="Index",
            item_count=len(instrument_specs),
            book_format=BookFormat.DESIGN_CHAPTER,
        )
        index_ch = plan_chapter(index_spec, start_page=current_page)
        chapters.append(index_ch)

    return Book(
        title=cfg.full_title(),
        book_format=BookFormat.DESIGN_CHAPTER,
        page_size=cfg.page_size,
        chapters=chapters,
    )
