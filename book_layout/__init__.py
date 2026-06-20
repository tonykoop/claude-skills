"""
book_layout
===========
Photo-book / yearbook / design-chapter layout & composition engine.

This package is the **composition model only** — page structure, slot geometry,
template assignment, and chapter flow.  It contains:

  schema      Pydantic data-models (Book, Chapter, Page, ImageSlot, TextBlock)
  templates   Reusable page-template definitions and a template registry
  planner     paginate() + plan_book() layout planner
  validator   Integrity checks (unfilled slots, numbering, aspect-ratio sanity)

Privacy boundary
----------------
All image slots are ABSTRACT PLACEHOLDERS (slot_id, aspect_ratio, role).
No file paths, URLs, real photos, or identifiable-person data are stored
anywhere in this package.  Consent handling, real-photo ingestion, and
identifiable-content governance are out of scope and live elsewhere.

Refs: claude-skills#210
"""
from .schema import (
    Book, Chapter, Page,
    ImageSlot, TextBlock,
    SlotRole, TextRole, BookFormat, PageSize,
)
from .templates import get_template, list_templates, PageTemplate
from .planner import paginate, plan_book, plan_chapter, ChapterSpec, TemplateRules
from .validator import validate_book, ValidationResult

__all__ = [
    "Book", "Chapter", "Page",
    "ImageSlot", "TextBlock",
    "SlotRole", "TextRole", "BookFormat", "PageSize",
    "get_template", "list_templates", "PageTemplate",
    "paginate", "plan_book", "plan_chapter",
    "ChapterSpec", "TemplateRules",
    "validate_book", "ValidationResult",
]
