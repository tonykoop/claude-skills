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
from .templates import get_template, list_templates, PageTemplate, register_template
from .planner import paginate, plan_book, plan_chapter, ChapterSpec, TemplateRules
from .validator import validate_book, ValidationResult
from .themes import (
    Theme, ColourPalette, Typography, SpreadGrammar,
    get_theme, list_themes, register_theme, get_theme_for_format,
    YEARBOOK_CLASSIC, PHOTO_ALBUM_WARM, DESIGN_CHAPTER_TECHNICAL, MINIMAL_EDITORIAL,
)
from .export import (
    PageSizeConfig, BookManifest, PageManifest, SlotManifest,
    export_book, to_json, from_json, manifest_to_json, manifest_to_dict,
    get_page_size_config, PAGE_SIZE_CONFIGS,
)
from .album import (
    EraSpec, SourceLedger, SourceLedgerEntry, AlbumConfig, PrivacyTier,
    build_album, build_era_chapter, album_privacy_gate, ALBUM_TEMPLATE_RULES,
)
from .yearbook import (
    InstrumentChapterSpec, InstrumentContentSpec, YearbookConfig,
    GateStatus, GateError,
    build_instrument_chapter, build_yearbook, gate_check,
)

__all__ = [
    # schema
    "Book", "Chapter", "Page",
    "ImageSlot", "TextBlock",
    "SlotRole", "TextRole", "BookFormat", "PageSize",
    # templates
    "get_template", "list_templates", "PageTemplate", "register_template",
    # planner
    "paginate", "plan_book", "plan_chapter",
    "ChapterSpec", "TemplateRules",
    # validator
    "validate_book", "ValidationResult",
    # themes
    "Theme", "ColourPalette", "Typography", "SpreadGrammar",
    "get_theme", "list_themes", "register_theme", "get_theme_for_format",
    "YEARBOOK_CLASSIC", "PHOTO_ALBUM_WARM", "DESIGN_CHAPTER_TECHNICAL", "MINIMAL_EDITORIAL",
    # export
    "PageSizeConfig", "BookManifest", "PageManifest", "SlotManifest",
    "export_book", "to_json", "from_json", "manifest_to_json", "manifest_to_dict",
    "get_page_size_config", "PAGE_SIZE_CONFIGS",
    # album
    "EraSpec", "SourceLedger", "SourceLedgerEntry", "AlbumConfig", "PrivacyTier",
    "build_album", "build_era_chapter", "album_privacy_gate", "ALBUM_TEMPLATE_RULES",
    # yearbook
    "InstrumentChapterSpec", "InstrumentContentSpec", "YearbookConfig",
    "GateStatus", "GateError",
    "build_instrument_chapter", "build_yearbook", "gate_check",
]
