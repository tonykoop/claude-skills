# Adobe Creative Cloud handoff

When the user wants a polished printable songsheet, hand off to the
Adobe Creative Cloud Claude connector (announced April 2026 — see
[anthropic.com/news/claude-for-creative-work](https://www.anthropic.com/news/claude-for-creative-work)).

The connector exposes 50+ tools across Photoshop, Illustrator, InDesign,
Premiere, and Express. The ones this skill uses are the document
rendering tools: `document_render_layout`, `document_render_vector`,
`document_convert_pdf`, plus image utilities for the title/illustration.

## When to use it

- The user explicitly asks for a "printable songsheet" or "print-ready
  PDF" that's nicer than ReportLab's output.
- The user wants the Heifer Zephyr brand applied (italic-serif wordmark,
  Fraunces headline, Inter body — the brand rules the user has
  documented in their memory).
- The user wants illustrations or photos integrated alongside the
  notation.

For everyday songbook PDFs (the `learn-to-play/` deposit), the local
ReportLab renderer is fine. Reach for Adobe when polish matters.

## What the skill produces for handoff

Before invoking the Adobe MCP tools, the skill stages the inputs:

```
adobe-staging/
├── tune.svg                # engraved notation as SVG (from LilyPond)
├── fingering.svg           # fingering chart as SVG
├── songsheet-spec.json     # layout instructions (title, sections, brand)
├── brand-assets/
│   ├── heifer-zephyr-wordmark.svg
│   └── bison-mark.svg
└── illustrations/          # optional decoration
```

`songsheet-spec.json` shape:

```json
{
  "title": "Twinkle Twinkle Little Star",
  "subtitle": "Arranged for A-tuned Native American Flute",
  "tempo": "♩ = 90",
  "key": "A minor pentatonic",
  "sections": [
    {"type": "notation", "src": "tune.svg"},
    {"type": "fingering-strip", "src": "fingering.svg"},
    {"type": "practice-tip", "text": "..."}
  ],
  "brand": {
    "wordmark": "brand-assets/heifer-zephyr-wordmark.svg",
    "headline_font": "Fraunces",
    "body_font": "Inter",
    "primary_color": "#2A2A2A"
  },
  "page_size": "letter"
}
```

## MCP call sequence

1. `adobe_mandatory_init` — call once per session.
2. `asset_initialize_file_upload` → `asset_finalize_file_upload` for
   each SVG asset; capture the returned asset ID.
3. `document_render_layout` with the layout spec referencing those
   asset IDs. The Adobe MCP returns a rendered PDF asset.
4. `document_convert_pdf` to download the PDF locally.

`scripts/build_songsheet_pdf.py` orchestrates this when invoked with
`--via adobe`. Without that flag, it uses ReportLab.

## Brand rules

Tony's Heifer Zephyr brand (already documented in his memory):

- **Wordmark** — italic-serif, this is the *only* place the curly
  italic-serif font appears.
- **Headlines** — Fraunces (a tight, contemporary serif).
- **Body** — Inter (clean sans-serif).
- **Code/numbers** — JetBrains Mono.
- **Never** use a serif body font. Never use the italic-serif anywhere
  but the wordmark.

The songsheet-spec.json `brand` block enforces this — set the fonts
explicitly per section, and the Adobe MCP applies them.

## Fallback (no Adobe connector)

If the Adobe MCP is unavailable, `build_songsheet_pdf.py` falls back to
ReportLab. The output is uglier (no wordmark, plain serif headers) but
correct. The fallback path is the default in `learn-to-play/` deposits.

## Examples

After Tony's Adobe MCP is available, this section will gain a
side-by-side: ReportLab output vs. Adobe-rendered. Until then, treat
this doc as the spec the connector implements.
