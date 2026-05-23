# Presentation and print packets

Tier 3 deliverables: the slide deck (`deck.pptx`) and the printable
shop packet (`print-packet.pdf`). Both are recruiter-facing artifacts.

## Slide deck — `deck.pptx`

Use the `pptx` skill to produce this. Standard 16:9 widescreen, a
neutral title slide, body slides with a consistent template.

### Canonical 13-slide structure

1. **Title** — project name, your name, makerspace name + city, date.
2. **Project intent** — one sentence: what this is, who it's for, why
   it matters. Then 2-3 bullets of context.
3. **Final artifact** — hero photo full-bleed (or render placeholder),
   one-line caption.
4. **File map** — annotated screenshot of the repo root showing what
   each file is. This is "I'm organized" in slide form.
5. **Build workflow overview** — high-level flow / Gantt of design →
   plan → build → finish → ship.
6. **Design summary** — key parameters and the formulas that derive
   them. Show the parametric nature.
7. **BOM and sourcing** — top 5-10 items with cost; total at the
   bottom. Brief, not exhaustive.
8. **Drawings / CAD / CNC** — one slide per critical view (typically
   2-3 slides total in this section).
9. **Visual BOM** — full-page assembly showing all parts called out.
10. **Assembly** — the 3-5 most pivotal assembly steps with photos.
11. **Validation** — what checks we run and what passed.
12. **Open risks** — top 3-5 from `risks.md` with the mitigation plan.
    *Showing risks* (and how you handle them) is more impressive than
    pretending there are none.
13. **Next actions** — what's left to ship, what a v2 would change.

### Slide design conventions

- **Title slide** — name + date, single hero image, no body text.
- **Body slides** — slide title at top, content area below. Avoid
  walls of text — if a slide has more than 5 bullets it should be
  two slides.
- **Speaker notes** — every slide gets at least 2-3 sentences of
  speaker notes. The verifier flags slides without notes.
- **Image placeholders** — TBD images get a clear placeholder rect
  with the filename it's expecting. Don't ship broken-image
  thumbnails.

### When to skip a slide

- Skip slide 8 (Drawings) if the project has no manufactured-drawing
  equivalent (e.g., a sewn fabric piece). Replace with a process
  diagram or pattern layout.
- Skip slide 9 (Visual BOM) if the project has fewer than 5 parts.
- Skip slide 11 (Validation) if Tier 1 — but never if Tier 3.

Don't skip slides 1, 2, 3, 12, or 13. Those are the narrative spine.

## Print packet — `print-packet.pdf`

Letter-size (8.5×11") portrait, single column, generated from the
same content as the deck but laid out for shop-floor reading.

### Canonical 12-section structure

1. Cover / summary (1 page)
2. Quick start + file map (1 page)
3. Design intent + key parameters (1-2 pages)
4. BOM (1-2 pages, table form)
5. Sourcing list with vendor URLs (1 page)
6. Cut list with sheet layouts (1-2 pages)
7. Drawing brief or full drawings (variable)
8. Assembly manual (variable)
9. Validation/tuning sheet (1 page, with check boxes for in-shop use)
10. Supplier RFQ (1 page, only when needed)
11. Visual BOM brief (1 page)
12. Appendix (variable — anything else)

### Print packet design conventions

- **Sans-serif body** — readable on a shop-floor clipboard at arm's
  length. Inter is a readable default; substitute your preferred sans-serif if Inter isn't
  available.
- **Headings differentiate by size, not by color** — print packets
  may be photocopied or printed grayscale.
- **Page numbers** — bottom-center, "Page N of M" format.
- **Section header on every page** — top-right, lets the user flip
  to a section without consulting a TOC.
- **Generous margins** — at least 0.75" all around, more on the bound
  edge if the user plans to bind.

### Generation

If `scripts/build_print_packet.py` exists, use it. Otherwise compose
in the `pdf` skill or via LaTeX/typst as your tooling allows.

## Build-log site — `site/index.html`

Single-file HTML, no build step, no framework. Designed to render
when opened from local disk *or* served via GitHub Pages.

### Sections (in order)

- `<header>` — project title + hero image
- `<section id="intent">` — what this is and why
- `<section id="space">` — where it was built (link to space profile)
- `<section id="workflow">` — build steps with in-shop photos
- `<section id="finished">` — final detail shots
- `<section id="links">` — link to GitHub repo, deck, print packet
- `<footer>` — license, attribution

### Style conventions

- Inline `<style>` block — no external CSS file.
- Image references relative to `site/` — assumes `site/images/`.
- Mobile-first responsive layout.
- Keep total file size under 100 KB excluding images. The page should
  load fast even on a phone connection in a noisy coffee shop.

### What the site is *not*

- It's not a blog. One page per project, not a multi-post site.
- It's not a portfolio. Link to it from your portfolio, but don't
  make this site the portfolio.
- It's not a documentation hub. Link to GitHub for that.

The site exists because a recruiter has 30 seconds to decide if
they're interested. A PDF or pptx is a hurdle; a URL is one click.
