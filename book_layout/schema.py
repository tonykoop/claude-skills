"""
book_layout.schema
==================
Pure-data models for the photo-book / yearbook / design-chapter layout engine.

Privacy boundary
----------------
ImageSlot objects are ABSTRACT PLACEHOLDERS.

  - `slot_id`      machine label (e.g. "p3-hero-0")
  - `aspect_ratio` composition geometry only (width / height float)
  - `role`         visual role enum (hero, supporting, accent, …)
  - `filled`       True once the planner assigns content to this slot
  - `content_ref`  opaque integer index into the caller's item list — never a
                   file path, URL, name, face, or any identifiable-person data

Real photos, real people, consent records, and identifiable content are out of
scope and governed elsewhere.  See README.md § Privacy boundary.

Refs: claude-skills#210
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ── enumerations ──────────────────────────────────────────────────────────────

class SlotRole(str, Enum):
    """Visual role of one image slot on a page."""
    HERO = "hero"
    SUPPORTING = "supporting"
    ACCENT = "accent"
    FULL_BLEED = "full-bleed"
    COLLAGE_TILE = "collage-tile"


class TextRole(str, Enum):
    """Semantic role of one text block on a page."""
    TITLE = "title"
    CAPTION = "caption"
    BODY = "body"
    HEADLINE = "headline"
    SUBTITLE = "subtitle"
    BYLINE = "byline"


class BookFormat(str, Enum):
    YEARBOOK = "yearbook"
    PHOTO_BOOK = "photo-book"
    DESIGN_CHAPTER = "design-chapter"


class PageSize(str, Enum):
    LETTER = "letter"        # 8.5 × 11 in
    A4 = "a4"                # 210 × 297 mm
    SQUARE = "square"        # 12 × 12 in
    SPREAD = "spread"        # 2-page spread (2× width)


# ── leaf models ───────────────────────────────────────────────────────────────

class ImageSlot(BaseModel):
    """Abstract placeholder for one image position on a page.

    Contains NO real image data.  A slot is 'filled' once the planner
    assigns a content-item index (`content_ref`) to it.

    `content_ref` is an opaque integer (index into the caller's own item
    list) — it is NOT a file path, URL, or any identifiable information.
    """
    slot_id: str
    aspect_ratio: float = Field(gt=0.0, description="width / height ratio, e.g. 1.5 = 3:2")
    role: SlotRole
    filled: bool = False
    content_ref: Optional[int] = None   # opaque index; no paths or PII

    model_config = {"frozen": False}

    def fill(self, content_ref: int) -> None:
        """Mark this slot as filled and record the content reference index."""
        if content_ref < 0:
            raise ValueError(f"content_ref must be >= 0, got {content_ref}")
        self.filled = True
        self.content_ref = content_ref

    def clear(self) -> None:
        """Reset slot to unfilled state."""
        self.filled = False
        self.content_ref = None


class TextBlock(BaseModel):
    """One text region on a page.  `content` is optional plain text."""
    block_id: str
    role: TextRole
    max_chars: int = Field(gt=0, default=500)
    content: Optional[str] = None

    model_config = {"frozen": False}

    @field_validator("content", mode="before")
    @classmethod
    def _check_length(cls, v):
        # length validation happens after the model is fully built (see model_validator)
        return v

    @model_validator(mode="after")
    def _content_fits(self) -> "TextBlock":
        if self.content is not None and len(self.content) > self.max_chars:
            raise ValueError(
                f"content length {len(self.content)} exceeds max_chars {self.max_chars}"
            )
        return self


# ── composite models ──────────────────────────────────────────────────────────

class Page(BaseModel):
    """One physical page in a chapter."""
    page_number: int = Field(ge=1)
    template_name: str
    image_slots: List[ImageSlot] = Field(default_factory=list)
    text_blocks: List[TextBlock] = Field(default_factory=list)

    model_config = {"frozen": False}

    @property
    def slot_count(self) -> int:
        return len(self.image_slots)

    @property
    def filled_slot_count(self) -> int:
        return sum(1 for s in self.image_slots if s.filled)

    @property
    def unfilled_slot_count(self) -> int:
        return self.slot_count - self.filled_slot_count

    @property
    def is_overfull(self) -> bool:
        """True when more content was assigned than slots exist (impossible via
        fill() but useful for external validation of hand-crafted pages)."""
        return any(s.content_ref is not None and s.content_ref >= self.slot_count
                   for s in self.image_slots)


class Chapter(BaseModel):
    """A named section of a book, containing an ordered list of Pages."""
    title: str
    theme: str = ""
    pages: List[Page] = Field(default_factory=list)

    model_config = {"frozen": False}

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def total_slots(self) -> int:
        return sum(p.slot_count for p in self.pages)

    @property
    def filled_slots(self) -> int:
        return sum(p.filled_slot_count for p in self.pages)

    @property
    def unfilled_slots(self) -> int:
        return self.total_slots - self.filled_slots


class Book(BaseModel):
    """Top-level container for a photo-book, yearbook, or design-chapter book."""
    title: str
    book_format: BookFormat
    page_size: PageSize = PageSize.LETTER
    chapters: List[Chapter] = Field(default_factory=list)

    model_config = {"frozen": False}

    @property
    def total_pages(self) -> int:
        return sum(c.page_count for c in self.chapters)

    @property
    def total_slots(self) -> int:
        return sum(c.total_slots for c in self.chapters)

    @property
    def filled_slots(self) -> int:
        return sum(c.filled_slots for c in self.chapters)
