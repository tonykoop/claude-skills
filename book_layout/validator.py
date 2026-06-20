"""
book_layout.validator
=====================
Integrity checks for Book, Chapter, and Page objects.

`validate_book(book)` runs all checks and returns a `ValidationResult`.

Checks
------
- Book has at least one chapter
- Each chapter has at least one page
- Page numbers are globally sequential (1-based, no gaps or duplicates)
- Each image slot has a valid aspect ratio in [ASPECT_RATIO_MIN, ASPECT_RATIO_MAX]
- Unfilled slots are reported as warnings (not errors) — an underfull last page
  is normal; a completely unfilled slot in the middle of a chapter is notable
- `content_ref` consistency: if a slot is marked filled, content_ref must be set
  (and vice versa)

ValidationResult
----------------
    ok        bool        True iff no errors (warnings are non-fatal)
    errors    list[str]   fatal structural problems
    warnings  list[str]   advisory notices (unfilled slots, etc.)

Refs: claude-skills#210
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .schema import Book, Chapter, ImageSlot, Page


# ── aspect-ratio bounds ───────────────────────────────────────────────────────
# 0.3 ≈ tall portrait (1:3), 4.0 = very wide panoramic strip
ASPECT_RATIO_MIN: float = 0.3
ASPECT_RATIO_MAX: float = 4.0


# ── result container ──────────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    ok: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.ok = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def __repr__(self) -> str:
        status = "PASS" if self.ok else "FAIL"
        return (
            f"ValidationResult({status}, "
            f"errors={len(self.errors)}, warnings={len(self.warnings)})"
        )


# ── per-element checks ────────────────────────────────────────────────────────

def _check_slot(slot: ImageSlot, ctx: str, result: ValidationResult) -> None:
    # Aspect-ratio bounds
    if not (ASPECT_RATIO_MIN <= slot.aspect_ratio <= ASPECT_RATIO_MAX):
        result.add_error(
            f"{ctx} slot '{slot.slot_id}': aspect_ratio {slot.aspect_ratio:.3f} "
            f"out of valid range [{ASPECT_RATIO_MIN}, {ASPECT_RATIO_MAX}]"
        )
    # Filled / content_ref consistency
    if slot.filled and slot.content_ref is None:
        result.add_error(
            f"{ctx} slot '{slot.slot_id}': marked filled but content_ref is None"
        )
    if not slot.filled and slot.content_ref is not None:
        result.add_error(
            f"{ctx} slot '{slot.slot_id}': content_ref set but slot not marked filled"
        )
    # Unfilled warning
    if not slot.filled:
        result.add_warning(f"{ctx} slot '{slot.slot_id}': unfilled (no content assigned)")


def _check_page(page: Page, ctx: str, result: ValidationResult) -> None:
    pctx = f"{ctx} > page {page.page_number}"
    if not page.image_slots:
        result.add_warning(f"{pctx}: has no image slots")
        return
    for slot in page.image_slots:
        _check_slot(slot, pctx, result)


def _check_chapter(chapter: Chapter, result: ValidationResult) -> None:
    ctx = f"chapter '{chapter.title}'"
    if not chapter.pages:
        result.add_error(f"{ctx}: has no pages")
        return
    for page in chapter.pages:
        _check_page(page, ctx, result)


def _check_page_numbering(book: Book, result: ValidationResult) -> None:
    """Verify globally sequential page numbers (1-based, no gaps or duplicates)."""
    expected = 1
    for chapter in book.chapters:
        for page in chapter.pages:
            if page.page_number != expected:
                result.add_error(
                    f"chapter '{chapter.title}' page {page.page_number}: "
                    f"expected sequential page number {expected}"
                )
            expected += 1


# ── main entry point ──────────────────────────────────────────────────────────

def validate_book(book: Book) -> ValidationResult:
    """Run all integrity checks on `book`.

    Returns a ValidationResult.  `ok` is True iff no errors were found.
    Warnings are informational; they do not set ok=False.
    """
    result = ValidationResult()

    if not book.chapters:
        result.add_error("book has no chapters")
        return result

    for chapter in book.chapters:
        _check_chapter(chapter, result)

    _check_page_numbering(book, result)

    return result
