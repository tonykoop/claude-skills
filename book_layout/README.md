# `book_layout` — Photo-Book / Yearbook / Design-Chapter Layout Engine

> **Refs:** claude-skills#210 — _image-gen-2: photo books, yearbooks & design chapters_

`book_layout` is the **page/chapter composition model** for the claude-skills
image-gen-2 epic.  It handles layout structure, template assignment, slot
flow, and validation — nothing more.

---

## What this module does

| Layer | Description |
|---|---|
| **Schema** (`schema.py`) | Pydantic models: `Book`, `Chapter`, `Page`, `ImageSlot`, `TextBlock` |
| **Templates** (`templates.py`) | Five reusable page-layout templates with a global registry |
| **Planner** (`planner.py`) | `paginate()` + `plan_chapter()` + `plan_book()` — assigns templates, flows items across pages |
| **Validator** (`validator.py`) | Structural integrity checks: filled/unfilled slots, page numbering, aspect-ratio bounds |

---

## Quick start

```python
from book_layout import plan_book, ChapterSpec, TemplateRules, validate_book
from book_layout import BookFormat, PageSize

specs = [
    ChapterSpec(title="Front Matter",  item_count=1,  theme="opening"),
    ChapterSpec(title="Build Gallery", item_count=12, theme="process"),
    ChapterSpec(title="Detail Shots",  item_count=5,  theme="closeup"),
]

book = plan_book(
    specs,
    book_title="Handpan Build — 2026 Edition",
    book_format=BookFormat.DESIGN_CHAPTER,
    page_size=PageSize.LETTER,
)

result = validate_book(book)
print(result)           # ValidationResult(PASS, errors=0, warnings=3)
print(book.total_pages) # 7
```

---

## Data model

```
Book
 └─ chapters: list[Chapter]
     └─ pages: list[Page]
         ├─ image_slots: list[ImageSlot]   ← abstract placeholders
         └─ text_blocks: list[TextBlock]
```

### ImageSlot

```python
ImageSlot(
    slot_id    = "p3-hero-0",   # machine label — page-scoped
    aspect_ratio = 1.5,         # float: width / height  (e.g. 1.5 = 3:2)
    role       = SlotRole.HERO, # enum: hero / supporting / accent / full-bleed / collage-tile
    filled     = True,          # set by planner after content assignment
    content_ref = 2,            # opaque int index into caller's item list
)
```

**`content_ref` is an opaque integer.  It is not a file path, URL, or any
identifiable-person reference.**

---

## Built-in templates

| Name | Slots | Slot roles | Text blocks |
|---|---|---|---|
| `full-bleed` | 1 | full-bleed | caption |
| `grid-2x2` | 4 | collage-tile × 4 | headline |
| `hero+caption` | 2 | hero + supporting | caption + body |
| `collage` | 5 | collage-tile × 5 | title |
| `spread` | 3 | full-bleed + supporting × 2 | headline + caption |

Register custom templates:

```python
from book_layout.templates import PageTemplate, register_template
from book_layout.schema import SlotRole, TextRole

custom = PageTemplate(
    name="sidebar",
    slot_prototypes=[
        {"slot_id": "main",    "aspect_ratio": 1.333, "role": SlotRole.HERO},
        {"slot_id": "sidebar", "aspect_ratio": 0.75,  "role": SlotRole.ACCENT},
    ],
    text_prototypes=[
        {"block_id": "cap", "role": TextRole.CAPTION, "max_chars": 250},
    ],
)
register_template(custom)
```

---

## Planner

### `paginate(items, slots_per_page) -> list[list]`

Pure-math helper — no templates, no schema.  Distributes any list across
pages with `slots_per_page` slots each.  The last page may be underfull.

```python
from book_layout import paginate
paginate(list(range(10)), 4)
# [[0,1,2,3], [4,5,6,7], [8,9]]
```

### `TemplateRules`

Controls which template is chosen for a chapter with a given `item_count`:

```python
from book_layout import TemplateRules

rules = TemplateRules(
    thresholds=[
        (1, "full-bleed"),      # 1 item  → full-bleed
        (3, "hero+caption"),    # 2–3 items → hero+caption
        (5, "collage"),         # 4–5 items → collage
    ],
    default_template="grid-2x2",  # 6+ items
)
```

If `template_rules=None` is passed to `plan_book()`, built-in defaults apply.

---

## Validation

```python
from book_layout import validate_book

result = validate_book(book)

result.ok        # bool — False if any errors
result.errors    # list[str] — fatal structural issues
result.warnings  # list[str] — non-fatal notices (unfilled slots, etc.)
```

**Errors** (fatal — `ok = False`):
- Book has no chapters
- Chapter has no pages
- Page numbering is not globally sequential (gaps, duplicates)
- `ImageSlot.aspect_ratio` outside `[0.3, 4.0]`
- `filled` / `content_ref` inconsistency on a slot

**Warnings** (non-fatal — `ok` unchanged):
- Unfilled image slot (underfull last page is normal)
- Page with no image slots

---

## Tests

```bash
pytest book_layout/tests/ -v
```

113 tests, all offline and deterministic.  No real images, no network calls.

Test coverage:

| File | What is tested |
|---|---|
| `test_schema.py` | Field validation, fill/clear, JSON round-trips, privacy invariant |
| `test_templates.py` | Slot counts, role enums, page-scoped IDs, registry, custom templates |
| `test_planner.py` | Pagination math, ceiling division, TemplateRules selection, full book assembly |
| `test_validator.py` | Valid books pass; empty book/chapter, unfilled slots, bad aspect ratios, bad numbering |

---

## Privacy boundary

**This module is composition logic only.**

> `book_layout` stores no real photos, no file paths, no URLs, no names, no
> faces, and no identifiable-person data anywhere in its data model.
>
> `ImageSlot.content_ref` is an opaque integer — an index into the caller's
> own item list.  What that index points to is entirely the caller's concern.
>
> **Real photo ingestion, identifiable-person handling, consent records, and
> privacy/GDPR governance are OUT OF SCOPE for this module and must be
> implemented in a separate layer by the caller.**

This boundary is enforced by the test `test_no_real_image_data_in_serialization`
in `test_schema.py` (checks that serialized JSON contains no path markers or
image-file extensions).

---

## Relationship to existing image-gen-2 skill

The `studiopipeline:image-gen-2` skill
(`plugins/maker/skills/idea-incubator/references/image-gen-2-chapter-template.md`)
handles **image generation briefs, editorial workflows, and spread production**.

`book_layout` is a **complementary composition model** — it defines the
structural skeleton (which pages exist, how many slots, which templates) that
a downstream rendering or image-gen step would fill.  It does not replace or
duplicate any existing image-gen-2 skill logic.

---

## Directory

```
book_layout/
├── __init__.py          public re-exports
├── schema.py            Pydantic models
├── templates.py         template registry + 5 built-in templates
├── planner.py           paginate(), plan_chapter(), plan_book()
├── validator.py         validate_book() + ValidationResult
├── README.md            this file
└── tests/
    ├── __init__.py
    ├── test_schema.py
    ├── test_templates.py
    ├── test_planner.py
    └── test_validator.py
```
