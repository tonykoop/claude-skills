"""
book_layout.audit
=================
Editorial quality audit — higher-level quality checks beyond structural validation.

Where `validator.py` checks structural integrity (page numbers, slot consistency,
aspect ratios), `audit.py` checks *editorial quality*: visual variety, chapter
balance, hero density, and spread grammar compliance.

Public API
----------
audit_book(book, theme)  -> EditorialAuditResult
audit_chapter(chapter)   -> list[AuditFinding]

AuditFinding
    severity    "info" | "warn" | "error"
    rule        machine-readable rule name (e.g. "chapter-balance")
    message     human-readable description
    context     which book/chapter/page triggered the finding

EditorialAuditResult
    ok          bool (True iff no "error" severity findings)
    findings    list[AuditFinding]
    errors      property → only "error" findings
    warnings    property → only "warn" findings
    infos       property → only "info" findings

Audit rules
-----------
chapter-balance
    All chapters should be within 50% of the average page count.
    Rationale: wildly uneven chapters break editorial flow.

template-variety
    No chapter should use the same template on >75% of its pages.
    Rationale: variety signals intentional composition, not lazy repetition.

hero-density
    At least 1 hero/full-bleed slot per 4 pages book-wide.
    Rationale: every section needs a visual anchor.

caption-coverage
    At least 50% of pages should have at least one text block with role CAPTION or BODY.
    Rationale: images without context lose editorial value.

chapter-arc (yearbook / design-chapter formats only)
    Each chapter should have at least one full-bleed or hero slot (strong opening)
    and at least one caption text block (explanatory closure).

minimum-pages
    A chapter should have at least 2 pages (1-page chapters feel underdeveloped).
    Exception: explicitly marked cover chapters.

Refs: claude-skills#210
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import List, Optional

from .schema import Book, BookFormat, Chapter, SlotRole, TextRole
from .themes import Theme, get_theme_for_format


# ── finding model ─────────────────────────────────────────────────────────────

@dataclass
class AuditFinding:
    severity: str       # "info" | "warn" | "error"
    rule: str           # machine-readable rule id
    message: str        # human-readable explanation
    context: str        # chapter title, page number, etc.

    def __repr__(self) -> str:
        return f"[{self.severity.upper()}:{self.rule}] {self.context}: {self.message}"


@dataclass
class EditorialAuditResult:
    findings: List[AuditFinding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(f.severity == "error" for f in self.findings)

    @property
    def errors(self) -> List[AuditFinding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> List[AuditFinding]:
        return [f for f in self.findings if f.severity == "warn"]

    @property
    def infos(self) -> List[AuditFinding]:
        return [f for f in self.findings if f.severity == "info"]

    def add(self, finding: AuditFinding) -> None:
        self.findings.append(finding)

    def _add(self, severity: str, rule: str, message: str, context: str) -> None:
        self.add(AuditFinding(severity=severity, rule=rule, message=message, context=context))

    def error(self, rule: str, message: str, context: str) -> None:
        self._add("error", rule, message, context)

    def warn(self, rule: str, message: str, context: str) -> None:
        self._add("warn", rule, message, context)

    def info(self, rule: str, message: str, context: str) -> None:
        self._add("info", rule, message, context)

    def __repr__(self) -> str:
        status = "PASS" if self.ok else "FAIL"
        return (
            f"EditorialAuditResult({status}, "
            f"errors={len(self.errors)}, "
            f"warnings={len(self.warnings)}, "
            f"infos={len(self.infos)})"
        )


# ── rule constants ────────────────────────────────────────────────────────────

CHAPTER_BALANCE_TOLERANCE = 0.50   # max deviation from mean page count
TEMPLATE_VARIETY_THRESHOLD = 0.75  # max fraction using the same template
HERO_DENSITY_PAGES_PER_HERO = 4    # at least 1 hero per N pages
CAPTION_COVERAGE_MIN = 0.50        # at least 50% of pages have a caption/body
MIN_PAGES_PER_CHAPTER = 2          # chapters shorter than this get a warning
COVER_TITLE_KEYWORDS = ("cover", "front matter", "frontmatter", "title page")


# ── rule implementations ──────────────────────────────────────────────────────

def _rule_chapter_balance(book: Book, result: EditorialAuditResult) -> None:
    if len(book.chapters) < 2:
        return
    page_counts = [c.page_count for c in book.chapters]
    mean = statistics.mean(page_counts)
    if mean == 0:
        return
    for chapter in book.chapters:
        deviation = abs(chapter.page_count - mean) / mean
        if deviation > CHAPTER_BALANCE_TOLERANCE:
            result.warn(
                rule="chapter-balance",
                message=(
                    f"Chapter has {chapter.page_count} pages vs mean {mean:.1f} "
                    f"({deviation:.0%} deviation — consider splitting or combining)"
                ),
                context=f"chapter '{chapter.title}'",
            )


def _rule_template_variety(book: Book, result: EditorialAuditResult) -> None:
    for chapter in book.chapters:
        if chapter.page_count < 3:
            continue  # too short to mandate variety
        from collections import Counter
        counts = Counter(p.template_name for p in chapter.pages)
        most_common, freq = counts.most_common(1)[0]
        fraction = freq / chapter.page_count
        if fraction > TEMPLATE_VARIETY_THRESHOLD:
            result.warn(
                rule="template-variety",
                message=(
                    f"Template '{most_common}' used on {freq}/{chapter.page_count} pages "
                    f"({fraction:.0%}). Consider mixing in a different template."
                ),
                context=f"chapter '{chapter.title}'",
            )


def _rule_hero_density(book: Book, result: EditorialAuditResult) -> None:
    total_pages = book.total_pages
    if total_pages == 0:
        return
    hero_roles = {SlotRole.HERO, SlotRole.FULL_BLEED}
    hero_count = sum(
        1
        for chapter in book.chapters
        for page in chapter.pages
        for slot in page.image_slots
        if slot.role in hero_roles
    )
    required = total_pages // HERO_DENSITY_PAGES_PER_HERO
    if hero_count < required:
        result.warn(
            rule="hero-density",
            message=(
                f"Book has {hero_count} hero/full-bleed slots across "
                f"{total_pages} pages; recommend at least "
                f"{required} (1 per {HERO_DENSITY_PAGES_PER_HERO} pages)."
            ),
            context="book",
        )
    else:
        result.info(
            rule="hero-density",
            message=f"Hero density OK: {hero_count} hero slots / {total_pages} pages.",
            context="book",
        )


def _rule_caption_coverage(book: Book, result: EditorialAuditResult) -> None:
    caption_roles = {TextRole.CAPTION, TextRole.BODY}
    total_pages = book.total_pages
    if total_pages == 0:
        return
    captioned = sum(
        1
        for chapter in book.chapters
        for page in chapter.pages
        if any(tb.role in caption_roles for tb in page.text_blocks)
    )
    coverage = captioned / total_pages
    if coverage < CAPTION_COVERAGE_MIN:
        result.warn(
            rule="caption-coverage",
            message=(
                f"Only {captioned}/{total_pages} pages ({coverage:.0%}) have a "
                f"caption or body text block. Aim for ≥{CAPTION_COVERAGE_MIN:.0%}."
            ),
            context="book",
        )


def _rule_chapter_arc(book: Book, result: EditorialAuditResult) -> None:
    """Yearbook/design-chapter books: each chapter should open strong and close with context."""
    arc_formats = {BookFormat.YEARBOOK, BookFormat.DESIGN_CHAPTER}
    if book.book_format not in arc_formats:
        return

    hero_roles = {SlotRole.HERO, SlotRole.FULL_BLEED}
    caption_roles = {TextRole.CAPTION, TextRole.BODY}

    for chapter in book.chapters:
        # Skip very short chapters and explicit cover chapters
        title_lower = chapter.title.lower()
        if chapter.page_count < 2 or any(kw in title_lower for kw in COVER_TITLE_KEYWORDS):
            continue

        # Check: at least one hero/full-bleed slot anywhere in the chapter
        has_hero = any(
            slot.role in hero_roles
            for page in chapter.pages
            for slot in page.image_slots
        )
        if not has_hero:
            result.warn(
                rule="chapter-arc",
                message=(
                    "Chapter has no hero or full-bleed slot. "
                    "Consider opening with a dominant visual."
                ),
                context=f"chapter '{chapter.title}'",
            )

        # Check: at least one caption/body text block anywhere
        has_caption = any(
            tb.role in caption_roles
            for page in chapter.pages
            for tb in page.text_blocks
        )
        if not has_caption:
            result.warn(
                rule="chapter-arc",
                message=(
                    "Chapter has no caption or body text block. "
                    "Add editorial context for the reader."
                ),
                context=f"chapter '{chapter.title}'",
            )


def _rule_minimum_pages(book: Book, result: EditorialAuditResult) -> None:
    for chapter in book.chapters:
        title_lower = chapter.title.lower()
        is_cover = any(kw in title_lower for kw in COVER_TITLE_KEYWORDS)
        is_index = "index" in title_lower
        if is_cover or is_index:
            continue
        if chapter.page_count < MIN_PAGES_PER_CHAPTER:
            result.warn(
                rule="minimum-pages",
                message=(
                    f"Chapter has only {chapter.page_count} page(s). "
                    f"Consider expanding to at least {MIN_PAGES_PER_CHAPTER}."
                ),
                context=f"chapter '{chapter.title}'",
            )


# ── main entry points ─────────────────────────────────────────────────────────

def audit_book(
    book: Book,
    theme: Optional[Theme] = None,
) -> EditorialAuditResult:
    """Run all editorial audit rules on `book`.

    Args:
        book:   the Book to audit
        theme:  optional Theme for theme-specific rules; inferred if None

    Returns:
        EditorialAuditResult.  `ok` is False only if "error" findings exist.
        Most editorial findings are "warn" (advisory).
    """
    result = EditorialAuditResult()

    if not book.chapters:
        result.error("no-chapters", "Book has no chapters — nothing to audit.", "book")
        return result

    _rule_chapter_balance(book, result)
    _rule_template_variety(book, result)
    _rule_hero_density(book, result)
    _rule_caption_coverage(book, result)
    _rule_chapter_arc(book, result)
    _rule_minimum_pages(book, result)

    if not result.findings:
        result.info("audit-clean", "All editorial rules passed.", "book")

    return result


def audit_chapter(chapter: Chapter) -> List[AuditFinding]:
    """Run per-chapter audit rules and return findings."""
    # Wrap in a minimal 1-chapter book to reuse book-level rules
    from .schema import Book, BookFormat, PageSize
    mock_book = Book(
        title="_audit_",
        book_format=BookFormat.DESIGN_CHAPTER,
        page_size=PageSize.LETTER,
        chapters=[chapter],
    )
    result = audit_book(mock_book)
    return result.findings
