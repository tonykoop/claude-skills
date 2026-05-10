# Build-Log Site — v4 (Tier 5 #18)

The capstone deck is for recruiters. The print packet is for the shop.
v4 adds the third recruiter-grade artifact: a static-site build log
that speaks to *another maker* who wants to follow along and build the
instrument themselves.

This is the brainstorm's "publishable build-log site, every instrument
links to its build" — and answers the strategic question of what v4's
recruiter test is.

## Design constraints

The site must be:

- **Single-folder** — one `site/` folder per packet. Self-contained,
  no global dependencies.
- **Build-step-free** — no `npm`, no compiler. Just HTML, CSS, and a
  small embedded JS for the optional scroll/anchor behaviors. Generated
  by `scripts/generate_site.py` directly.
- **GitHub Pages compatible** — drop the `site/` folder into a repo's
  `docs/` and Pages serves it as-is. No router config needed.
- **Mobile-readable** — recruiters and other makers will load this on
  phones in messy contexts. Single-column responsive layout, large
  type, avoid CSS that breaks below 380px.
- **Asset-stable** — image paths resolve relatively (no `file:///`
  paths from Tony's local Documents folder leaking in).

## Page structure (per packet)

### `site/index.html` — the main page

Sections, in order:

1. **Hero** — full-width hero image, instrument name, family,
   one-sentence intent.
2. **What this is** — 2-3 paragraphs. What instrument, why it's
   interesting, what playing it sounds like (link to audio if
   available).
3. **The design** — embedded SVG of the family-overview drawing (or
   the single-instrument drawing if not a family); a paragraph
   explaining the governing physics in plain language.
4. **The build** — step-by-step build summary, drawn from
   `assembly-manual.md` but rewritten for outside readers (less
   imperative, more narrative). Embedded process photos when
   available.
5. **The numbers** — BOM table (HTML, from `bom.csv`), with prices
   and sources. Cut list table (HTML, from `cut-list.csv`).
6. **Tuning & validation** — measured-vs-predicted chart (HTML/SVG)
   from `validation.csv`. Honest about cents error.
7. **Known risks** — short summary of `risks.md` for the curious
   reader.
8. **Family overview** *(if family-aware)* — links to sibling members.
9. **Resources** — link to GitHub repo, link to capstone deck, link
   to print packet PDF, link to Tony's broader instrument-maker
   portfolio.
10. **Footer** — Tony's name, contact, license, attribution.

### `site/family/index.html` — for family-aware packets

A roll-up across N members. Hero image (group shot if available).
Member grid with thumbnail + key + link to each member's page.
Family-level governing physics (the scaling law from
`family-aware-design.md`). Cross-link to members.

### `site/assets/` — bundled images and CSS

- `assets/style.css` — single CSS file.
- `assets/hero.jpg`, `assets/process-1.jpg`, etc. — symlinked or
  copied from the packet's `images/` folder.
- `assets/drawings/*.svg` — symlinked or copied from `drawings/`.

The generator copies files (not symlinks) for portability; the cost
is duplicate disk space, but the resulting `site/` folder is
self-contained and movable.

## Data sources

The generator reads the packet's structured files:

- `design.md` — for the *What this is* and *The design* sections.
- `bom.csv` and `cut-list.csv` — for the *The numbers* section.
- `validation.csv` — for *Tuning & validation*.
- `assembly-manual.md` — for *The build*.
- `risks.md` — for *Known risks*.
- `images/` — for hero, process, finished-detail shots.
- `family-spec.csv` — for the *Family overview* (if family-aware).
- `capstone-manifest.json` — for cross-links to the deck and PDF.
- The `repo-relationships.yaml` registry — for the *Resources*
  section.

## Rendering style

- **Typography:** A serif body (Charter / Iowan / system serif) and
  a sans-serif heading (Inter / system sans). Type sizes scale from
  16px body on phones to 18px on desktop. Wide measure (~70 chars).
- **Color:** Single-color theme — the instrument family's color
  family (warm wood tones for wood instruments, cool for metal,
  earth for ceramic). Generator picks from a fixed palette by family.
- **Tables:** Striped rows for BOM and cut-list. Right-align numbers.
- **Photos:** Full-width hero. Process shots in a 2-column grid on
  desktop, single column on mobile.
- **Drawings:** Inline SVG, scaled to fit content width. Pinch-zoom
  works on mobile because it's an inline SVG, not an image.

## Generator usage

```bash
python3 scripts/generate_site.py \
  ./build-packets/2026-05-02-tng-001-tongue-drum \
  --output ./build-packets/2026-05-02-tng-001-tongue-drum/site \
  [--theme warm-wood] \
  [--dry-run]
```

Outputs:

- `site/index.html`
- `site/assets/style.css`
- `site/assets/hero.jpg` (copy from `images/hero.jpg` if present)
- `site/assets/process-N.jpg` (copies from `images/`)
- `site/assets/drawings/*.svg` (copies from `drawings/`)
- `site/family/index.html` (if `family-spec.csv` has >1 row)
- `site/family/<member-id>.html` (if family-aware)

## Quality gates

- [ ] `site/index.html` opens in a browser and renders without
      JavaScript errors in the console.
- [ ] All `<img src=>` and `<link href=>` paths resolve relative to
      `site/`.
- [ ] No absolute paths leak (no `file:///`, no
      `C:\Users\Tony\...`).
- [ ] On a 380px viewport, no horizontal scroll.
- [ ] All tables in BOM/cut-list/validation render correctly with
      striped rows.
- [ ] At least one hero image exists, or a "shotlist placeholder"
      banner is shown.
- [ ] Family pages link bidirectionally (member page → family page,
      family page → each member).
- [ ] License and attribution are present in the footer.

## Publishing

Two paths the generator supports:

1. **GitHub Pages:** Move/copy `site/` to the instrument's repo
   `docs/` folder; enable GitHub Pages on the repo's Settings →
   Pages → "Deploy from a branch" → `docs/`. Tony does this manually;
   the script doesn't push to GitHub.
2. **Standalone:** Send the `site/` folder as a .zip to anyone; they
   open `index.html` locally. No internet required.

## What this site is not

- It is not a CMS. There's no admin UI, no comments, no analytics.
- It is not a dynamic site. No backend, no DB.
- It is not the capstone deck. The deck has speaker notes; the site
  doesn't. The deck is for a 30-second flip-through; the site is for
  a 10-minute read.
- It is not the print packet. The packet is a paper thing for the
  shop; the site is a digital thing for a network of makers.
