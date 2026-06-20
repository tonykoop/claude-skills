"""
book_layout.album
=================
High-level builder for **family / friends photo album books** (stories #93 and #101).

This module adds album-specific concepts on top of the core planner:

  EraSpec          A named time period (decade, trip, event) with an item count
                   and optional notes.  No actual photos here.
  SourceLedger     Privacy-preserving record of where source photos live and
                   what consent / privacy tier applies.  Stores PATHS in the
                   caller's system — but the ledger itself holds no image data.
  AlbumConfig      Album-wide configuration: audience, privacy tier, print target.
  build_album()    Wraps plan_book() with album-specific defaults:
                   - one Chapter per era
                   - photo-album-warm theme
                   - cover-page prepended (full-bleed, single item)
                   - letter / square page size
  build_era_chapter()  Build one era's Chapter from an EraSpec.

Privacy rules
-------------
- SourceLedger entries record source PATHS (strings) so the ledger can describe
  where originals live; these strings are never passed into ImageSlot / Page /
  Book objects.  The layout engine sees only item counts.
- `PrivacyTier` distinguishes public vs. family-only vs. archive-only content.
- Nothing in this module generates, processes, or stores actual image data.

Refs: claude-skills#210 (#93, #101)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .schema import Book, BookFormat, Chapter, Page, PageSize
from .planner import ChapterSpec, TemplateRules, plan_book, plan_chapter
from .themes import PHOTO_ALBUM_WARM, Theme


# ── privacy tier ──────────────────────────────────────────────────────────────

class PrivacyTier(str, Enum):
    """How widely a source collection may be shared."""
    PUBLIC = "public"           # Safe for any audience
    FAMILY_ONLY = "family-only" # Share only with family / close friends
    ARCHIVE_ONLY = "archive-only"  # Never publish; personal archive use only


# ── album data structures ─────────────────────────────────────────────────────

@dataclass
class EraSpec:
    """One named time period in the album.

    `item_count` is the number of abstract content items (photos, collages,
    etc.) to flow into this era's chapter.  No actual files are referenced.
    """
    title: str
    item_count: int
    notes: str = ""
    privacy_tier: PrivacyTier = PrivacyTier.FAMILY_ONLY
    approximate_years: str = ""   # e.g. "2004–2009" — advisory metadata only

    def __post_init__(self) -> None:
        if self.item_count < 0:
            raise ValueError(f"EraSpec item_count must be >= 0, got {self.item_count}")

    def to_chapter_spec(self) -> ChapterSpec:
        return ChapterSpec(
            title=self.title,
            item_count=self.item_count,
            theme=self.notes,
            book_format=BookFormat.PHOTO_BOOK,
        )


@dataclass
class SourceLedgerEntry:
    """One entry in the source ledger — describes where source photos live.

    The `source_path` is a string describing the location in the *caller's*
    storage system (e.g. a drive label, folder name, or cloud album ID).
    It is NOT passed to ImageSlot / Page — it stays in the ledger only.
    """
    era_title: str
    source_path: str    # caller's reference; never enters layout slots
    item_count: int
    privacy_tier: PrivacyTier = PrivacyTier.FAMILY_ONLY
    notes: str = ""

    def __post_init__(self) -> None:
        if self.item_count < 0:
            raise ValueError("item_count must be >= 0")


@dataclass
class SourceLedger:
    """Collection of source-ledger entries for an album project.

    The ledger is a planning/provenance artifact that records which real
    collections feed which eras.  It is never serialised into the Book
    object — it lives alongside, not inside, the layout model.
    """
    entries: List[SourceLedgerEntry] = field(default_factory=list)

    def add(self, entry: SourceLedgerEntry) -> None:
        self.entries.append(entry)

    def total_items(self) -> int:
        return sum(e.item_count for e in self.entries)

    def entries_for_era(self, era_title: str) -> List[SourceLedgerEntry]:
        return [e for e in self.entries if e.era_title == era_title]

    def privacy_summary(self) -> dict:
        summary: dict = {tier.value: 0 for tier in PrivacyTier}
        for entry in self.entries:
            summary[entry.privacy_tier.value] += entry.item_count
        return summary


@dataclass
class AlbumConfig:
    """Configuration for an album build."""
    album_title: str
    audience: str = "family-and-friends"    # advisory: who this is for
    print_target: str = "home-print"        # advisory: home-print / professional / digital-only
    page_size: PageSize = PageSize.SQUARE   # square is common for photo books
    include_cover: bool = True
    cover_title: str = ""                   # defaults to album_title if empty
    privacy_tier: PrivacyTier = PrivacyTier.FAMILY_ONLY

    def __post_init__(self) -> None:
        if not self.cover_title:
            self.cover_title = self.album_title


# ── album template rules ──────────────────────────────────────────────────────

# Photo-album default: collage for 4+ items, hero+caption for 2–3, full-bleed for 1
ALBUM_TEMPLATE_RULES = TemplateRules(
    thresholds=[
        (1, "full-bleed"),
        (3, "hero+caption"),
        (7, "collage"),
    ],
    default_template="grid-2x2",
)


# ── builders ──────────────────────────────────────────────────────────────────

def build_era_chapter(
    era: EraSpec,
    rules: Optional[TemplateRules] = None,
    start_page: int = 1,
) -> Chapter:
    """Build one Chapter for a single era."""
    effective_rules = rules or ALBUM_TEMPLATE_RULES
    spec = era.to_chapter_spec()
    return plan_chapter(spec, rules=effective_rules, start_page=start_page)


def build_album(
    eras: List[EraSpec],
    config: Optional[AlbumConfig] = None,
    template_rules: Optional[TemplateRules] = None,
) -> Book:
    """Build a photo-album Book from a list of EraSpecs.

    - One Chapter per era, plus an optional cover chapter.
    - Photo-album-warm theme defaults.
    - Page numbers are globally sequential.

    Args:
        eras:             ordered list of EraSpecs (each becomes a chapter)
        config:           AlbumConfig; defaults applied if None
        template_rules:   template selection; ALBUM_TEMPLATE_RULES if None

    Returns:
        Fully-planned Book (no real image data).
    """
    if config is None:
        config = AlbumConfig(album_title="Photo Album")

    effective_rules = template_rules or ALBUM_TEMPLATE_RULES

    chapter_specs: List[ChapterSpec] = []

    # Optional cover chapter (1-item, full-bleed)
    if config.include_cover:
        chapter_specs.append(
            ChapterSpec(
                title=f"Cover — {config.cover_title}",
                item_count=1,
                theme="cover",
                book_format=BookFormat.PHOTO_BOOK,
            )
        )

    # One chapter per era
    for era in eras:
        chapter_specs.append(era.to_chapter_spec())

    return plan_book(
        chapter_specs=chapter_specs,
        book_title=config.album_title,
        book_format=BookFormat.PHOTO_BOOK,
        page_size=config.page_size,
        template_rules=effective_rules,
    )


def album_privacy_gate(
    eras: List[EraSpec],
    config: AlbumConfig,
) -> tuple[bool, List[str]]:
    """Check that all eras are compatible with the album's privacy tier.

    Returns (passed: bool, issues: list[str]).
    Issues is empty if passed.

    Rule: no era may have a *more public* privacy tier than the album config.
    e.g. if the album is FAMILY_ONLY, PUBLIC eras are fine; ARCHIVE_ONLY eras
    should be flagged for human review before including.
    """
    tier_rank = {
        PrivacyTier.PUBLIC: 0,
        PrivacyTier.FAMILY_ONLY: 1,
        PrivacyTier.ARCHIVE_ONLY: 2,
    }
    album_rank = tier_rank[config.privacy_tier]
    issues: List[str] = []
    for era in eras:
        era_rank = tier_rank[era.privacy_tier]
        if era_rank > album_rank:
            issues.append(
                f"Era '{era.title}' has privacy tier '{era.privacy_tier.value}' "
                f"which is more restrictive than album tier '{config.privacy_tier.value}'. "
                f"Review before including in a {config.audience} album."
            )
    return (len(issues) == 0), issues
