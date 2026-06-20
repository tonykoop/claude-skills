# `book_layout` — Photo-Book / Yearbook / Design-Chapter Layout Engine

> **Refs:** claude-skills#210 — _image-gen-2: photo books, yearbooks & design chapters_

`book_layout` is the **page/chapter composition model** for the claude-skills
image-gen-2 epic.  It handles layout structure, template assignment, slot flow,
spread planning, editorial audit, and export manifest generation — nothing more.

---

## Privacy boundary

> **ImageSlot objects are ABSTRACT PLACEHOLDERS.**
>
> No file paths, URLs, real photos, faces, names, or identifiable-person data
> exist anywhere in this package.  `ImageSlot.content_ref` is an opaque
> integer — an index into the *caller's* item list.  What that index points to
> is entirely the caller's concern.
>
> `SourceLedger` (album module) stores source paths as plain strings for
> provenance purposes, but **ledger data never enters the Book/Chapter/Page
> schema** — it lives alongside the layout model, not inside it.
>
> **Real photo ingestion, identifiable-person handling, consent records, and
> privacy/GDPR governance are OUT OF SCOPE for this module** and must be
> implemented in a separate layer by the caller.
>
> Enforced by `test_no_real_image_data_in_serialization` and
> `test_source_ledger_does_not_contaminate_book`.

---

## Module overview

| Module | Role |
|---|---|
| `schema.py` | Pydantic models: `Book`, `Chapter`, `Page`, `ImageSlot`, `TextBlock`; enums |
| `templates.py` | 5 built-in page templates + global registry |
| `planner.py` | `paginate()`, `plan_chapter()`, `plan_book()`, `TemplateRules` |
| `validator.py` | `validate_book()` → structural integrity checks |
| `themes.py` | 4 built-in design themes + registry; `get_theme_for_format()` |
| `export.py` | `export_book()` → `BookManifest`; `to_json()` / `from_json()` |
| `album.py` | Family/friends album builder (`EraSpec`, `build_album()`, `SourceLedger`) |
| `yearbook.py` | Instrument design-book builder (`InstrumentChapterSpec`, `build_yearbook()`) |
| `spreads.py` | 2-page spread planner (`pair_into_spreads()`, `plan_spread_book()`) |
| `audit.py` | Editorial quality audit (`audit_book()`, `EditorialAuditResult`) |
| `cli.py` | `python -m book_layout` CLI |

---

## Quick start

### Generic book
```python
from book_layout import plan_book, ChapterSpec, validate_book, export_book
from book_layout import BookFormat, PageSize

specs = [
    ChapterSpec(title="Front Matter",  item_count=1),
    ChapterSpec(title="Build Gallery", item_count=12),
    ChapterSpec(title="Detail Shots",  item_count=5),
]
book = plan_book(specs, book_title="My Design Book",
                 book_format=BookFormat.DESIGN_CHAPTER,
                 page_size=PageSize.LETTER)

result = validate_book(book)    # ValidationResult(PASS, errors=0, warnings=3)
manifest = export_book(book)    # BookManifest ready for renderer
```

### Family photo album (#93 / #101)
```python
from book_layout.album import EraSpec, AlbumConfig, build_album

eras = [
    EraSpec("Early 2000s",  item_count=8),
    EraSpec("Road Trips",   item_count=15),
    EraSpec("Family Years", item_count=10),
]
config = AlbumConfig(album_title="20 Years of Adventures", page_size=PageSize.SQUARE)
book = build_album(eras, config=config)
```

### Instrument design-book / yearbook (#92 / #100)
```python
from book_layout.yearbook import (
    InstrumentChapterSpec, InstrumentContentSpec, YearbookConfig,
    GateStatus, build_yearbook,
)

instruments = [
    InstrumentChapterSpec(
        repo_name="handpan-resonance-model",
        display_name="Handpan — Resonance Model",
        gate_status=GateStatus.PASSED,
        content=InstrumentContentSpec(
            cover_items=1, build_gallery_items=6,
            experiment_lab_items=3, detail_shot_items=4,
        ),
    ),
]
config = YearbookConfig(title="Instrument Design Yearbook", edition="2026")
book = build_yearbook(instruments, config=config)
```

### Spread-aware layout
```python
from book_layout.spreads import plan_spread_book, spread_summary, spreads_for_book

book, spread_map = plan_spread_book(specs, book_format=BookFormat.YEARBOOK)
for chapter_title, spreads in spread_map.items():
    summ = spread_summary(spreads)
    print(f"{chapter_title}: {summ}")
```

### Editorial audit
```python
from book_layout.audit import audit_book

result = audit_book(book)
print(result)         # EditorialAuditResult(PASS, errors=0, warnings=2, infos=1)
for f in result.warnings:
    print(f)
```

---

## Data model

```
Book
 ├─ title, book_format, page_size
 └─ chapters: list[Chapter]
     ├─ title, theme
     └─ pages: list[Page]
         ├─ page_number, template_name
         ├─ image_slots: list[ImageSlot]   ← abstract placeholders
         └─ text_blocks: list[TextBlock]
```

### ImageSlot (abstract placeholder)
```python
ImageSlot(
    slot_id      = "p3-hero-0",    # page-scoped machine label
    aspect_ratio = 1.5,            # float: width / height
    role         = SlotRole.HERO,  # hero | supporting | accent | full-bleed | collage-tile
    filled       = True,           # True once planner assigns content
    content_ref  = 2,              # opaque int index; NOT a file path
)
```

---

## Built-in page templates

| Name | Slots | Roles |
|---|---|---|
| `full-bleed` | 1 | full-bleed |
| `grid-2x2` | 4 | collage-tile × 4 |
| `hero+caption` | 2 | hero + supporting |
| `collage` | 5 | collage-tile × 5 |
| `spread` | 3 | full-bleed + supporting × 2 |

Register custom templates with `register_template(PageTemplate(...))`.

---

## Built-in design themes

| Name | Best for |
|---|---|
| `yearbook-classic` | `yearbook` format |
| `photo-album-warm` | `photo-book` format |
| `design-chapter-technical` | `design-chapter` format |
| `minimal-editorial` | any format |

`get_theme_for_format(book_format)` auto-selects the right default.
Themes carry `ColourPalette`, `Typography`, `SpreadGrammar`, and
`art_direction_hints` — advisory metadata for downstream renderers.

---

## Export layer

```python
from book_layout.export import export_book, to_json, from_json, manifest_to_json

# Renderer-ready manifest (with physical mm dimensions)
manifest = export_book(book)
print(manifest.fill_rate)       # 0.875 (87.5% of slots filled)
print(manifest.all_slots[0])    # SlotManifest(slot_id=..., approx_width_mm=95.7, ...)

# JSON round-trip
json_str = to_json(book)
book2 = from_json(json_str)
assert book2.total_pages == book.total_pages
```

Physical page sizes: Letter (215.9 × 279.4 mm), A4 (210 × 297 mm),
Square (304.8 × 304.8 mm), Spread (431.8 × 279.4 mm).

---

## Spread planner

```python
from book_layout.spreads import pair_into_spreads, spread_summary

spreads = pair_into_spreads(chapter.pages, chapter_title=chapter.title)
for s in spreads:
    print(f"Spread {s.spread_number}: "
          f"pp.{s.left_page_number}–{s.right_page_number or 'solo'} "
          f"dominant={s.dominant_side}")
```

`plan_spread_book()` builds an entire book using spread-aware template
assignment and returns `(Book, spread_map)`.

---

## Editorial audit rules

| Rule | Severity | Trigger |
|---|---|---|
| `chapter-balance` | warn | Chapter deviates > 50% from mean page count |
| `template-variety` | warn | Same template on > 75% of a chapter's pages |
| `hero-density` | warn | < 1 hero/full-bleed slot per 4 pages |
| `caption-coverage` | warn | < 50% of pages have a caption or body block |
| `chapter-arc` | warn | Yearbook/design-chapter chapter has no hero slot or no caption |
| `minimum-pages` | warn | Non-cover chapter has < 2 pages |

---

## CLI

```bash
# Plan a generic book
python -m book_layout plan --chapters 4,12,8 --title "My Book" --out book.json

# Build a family photo album
python -m book_layout album --eras "2000s:10,2010s:15,2020s:8" --title "Family Album" --out album.json

# Build an instrument yearbook
python -m book_layout year --instruments "handpan:14,barrel-organ:10" --edition "2026"

# Validate a serialised book
python -m book_layout validate book.json

# Export to renderer manifest
python -m book_layout export book.json --manifest-out manifest.json

# List themes / templates
python -m book_layout themes
python -m book_layout templates
```

---

## Tests

```bash
pytest book_layout/tests/ -v
```

**324 tests, all offline and deterministic.  No real images.**

| Test file | Coverage |
|---|---|
| `test_schema.py` | Field validation, fill/clear, JSON round-trips, privacy invariant |
| `test_templates.py` | Slot counts, roles, page-scoped IDs, registry, custom templates |
| `test_planner.py` | Pagination math, TemplateRules, full book assembly |
| `test_validator.py` | Structural errors, unfilled slots, aspect-ratio bounds, numbering |
| `test_themes.py` | Registry, built-ins, format matching, dataclass helpers |
| `test_export.py` | PageSizeConfig, BookManifest, geometry, JSON round-trip |
| `test_album.py` | EraSpec, SourceLedger, build_album, privacy gate |
| `test_yearbook.py` | InstrumentChapterSpec, gate_check, build_instrument_chapter, build_yearbook |
| `test_spreads.py` | pair_into_spreads, dominant-side alternation, plan_spread_book |
| `test_audit.py` | All 6 editorial rules, EditorialAuditResult |
| `test_cli.py` | All CLI sub-commands (plan, album, year, validate, export, themes, templates) |
| `test_integration.py` | Full pipelines: album, yearbook, spread-first, CLI chain, public API surface |

---

## Relationship to existing image-gen-2 skill

The `studiopipeline:image-gen-2` skill handles **image-generation briefs,
editorial workflows, and spread production**.

`book_layout` is a **complementary composition model** — the structural
skeleton (which pages exist, how many slots, which templates, what spread
pairings, which editorial rules apply) that a downstream rendering or
image-gen step would fill.  It does not replace or duplicate any existing
image-gen-2 skill logic.

---

## Directory

```
book_layout/
├── __init__.py          public re-exports
├── __main__.py          python -m book_layout entry point
├── schema.py            Pydantic models (Book, Chapter, Page, ImageSlot, TextBlock)
├── templates.py         template registry + 5 built-in templates
├── planner.py           paginate(), plan_chapter(), plan_book()
├── validator.py         validate_book() + ValidationResult
├── themes.py            4 built-in themes + registry
├── export.py            export_book() + BookManifest + JSON round-trip
├── album.py             family/friends album builder (EraSpec, SourceLedger)
├── yearbook.py          instrument design-book builder (InstrumentChapterSpec, gate)
├── spreads.py           2-page spread planner
├── audit.py             editorial quality audit (6 rules)
├── cli.py               CLI sub-commands
├── README.md            this file
└── tests/
    ├── test_schema.py
    ├── test_templates.py
    ├── test_planner.py
    ├── test_validator.py
    ├── test_themes.py
    ├── test_export.py
    ├── test_album.py
    ├── test_yearbook.py
    ├── test_spreads.py
    ├── test_audit.py
    ├── test_cli.py
    └── test_integration.py
```
