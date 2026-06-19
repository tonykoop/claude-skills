# Instrument Design-Book Chapter — Yearbook Production Workflow

Issue: https://github.com/tonykoop/claude-skills/issues/100

The yearbook-staff editorial workflow for producing a polished design-book
chapter for a public instrument repo that has passed its gate. This doc covers
the **how** (editorial process, spread structure, image-gen-2 prompting
discipline, proof review). The **what** (asset contract, chapter structure,
authority-vs-concept distinction) lives in the template:

`plugins/maker/skills/idea-incubator/references/image-gen-2-chapter-template.md`

The **which** (gate status per repo) lives in:

`docs/image-gen-2/instrument-chapter-readiness.md` (Refs #92)

## The Yearbook Lens

A high-school yearbook's editorial strengths are exactly what separates a
good instrument chapter from a good README:

- **Strong spreads** — a spread has a dominant visual, a supporting visual,
  and supporting text. The dominant visual earns its place; the rest serves it.
- **Captions that carry weight** — captions are the reader's handle on what
  they're looking at. "3D isometric view of the handpan shell" is not a
  caption. "The shell's 2.4 mm dimpled steel — formed on a pneu-hydro press
  from a 600-mm disk — holds ≥190 Hz resonance without additional relief cuts
  (measured, commit `a7f3b1c`)." is a caption.
- **Build-story arc** — the reader goes from "what is this?" to "how was it
  made?" to "how does it work?" in a legible arc. No chapter should be a
  gallery of unrelated visuals.
- **Editorial consistency** — every chapter in the series shares type scale,
  spread grammar, and color discipline so a reader can move between instruments
  and immediately orient.

## Pre-production checklist (before any image-gen-2 call)

- [ ] Repo has passed all gate criteria (see `instrument-chapter-readiness.md`).
- [ ] Read the full README and every file in `docs/` of the target repo.
- [ ] Pull the parameter CSV (or build-spec table) and extract 3–5 key numbers
  that will appear in captions and the build section.
- [ ] Identify the dimensioned drawing (CAD, DXF, STEP): what does it show?
  What measurements are legible? These are your authority artifacts.
- [ ] Confirm the BOM is present. At least one materials-selection decision
  from the BOM should appear in the chapter as editorial content.
- [ ] Note any Wolfram interactive content: which parameter is it exploring?
  This defines the "experiment lab" section.
- [ ] Identify what visual evidence already exists (build photos, renders,
  SolidWorks screenshots). These inform the image-gen-2 brief — you're filling
  gaps, not replacing originals.

## Spread structure

Each chapter is 4–6 spreads. Minimum viable chapter is 4:

### Spread 1 — Cover + Opening Statement

**Left page:** hero image (image-gen-2 concept render of the assembled
instrument or a decisive detail — e.g. the handpan's tuned field, the
barrel organ's rank of pipes). Bleed to edge.

**Right page:**
- Instrument name, large
- One-line identity ("A tunable steel tongue drum — 9 notes, 54 cm,
  designed for concert hall acoustics at bedroom-workshop scale.")
- Packet status block: `VALIDATED` (green, if L2+ earned) or
  `PROVISIONAL — build status unverified` (amber). No chapter hides this.
- Brief build-origin note: materials, process, year.

### Spread 2 — The Build, Honestly

**Left page:** dimensioned drawing or CAD view, full width. Caption: what the
drawing shows, the governing dimension, the material. Cite the CAD commit.

**Right page:**
- Parameter table extracted from the CSV: 6–10 rows, the numbers that matter.
  Label units. No decoration.
- BOM highlight: 1–2 materials-selection calls with brief rationale ("2024-T3
  Al sheet: 4× better yield-to-weight than 3003; confirmed resonance retention
  at 22°C per tuning log.").
- Build process note: 2–3 sentences. What process produced these parts? What
  was the hardest constraint to meet?

### Spread 3 — The Instrument, Felt

**Left page:** 3D isometric concept render (image-gen-2). Alt text must state
`derivative: true` — this is mood, not measurement. Caption may include a
real number *only if* it is repeated from the authority artifact on spread 2.

**Right page:** 2 supporting visuals:
- A detail concept render (e.g., joint close-up, tuning mass detail, mounting
  bracket) with `derivative: true` sidecar.
- A scale reference or human-use context (instrument in hand, instrument at
  performance height), also `derivative: true`.

### Spread 4 — Experiment Lab and Wolfram Content

**Left page:** A reproduction or screenshot of the Wolfram interactive content,
plus a plain-English paragraph explaining what it explores and what parameter
range is interesting.

**Right page:**
- Lab result summary: what was measured, what range was tested, what the
  result tells a builder about the design space.
- If measurement evidence exists (frequency response, structural test, play
  session notes): cite the commit. If not: "Not yet measured. The Wolfram
  model projects [X]; empirical validation is a build-readiness gate for L3."

### Optional Spread 5 — Build Log Excerpts

If the repo contains a build log (Markdown, notes, photos), pull the
3 most decision-revealing moments:
- A choice point (material substitution, dimension adjustment, constraint
  discovered late).
- A failure or near-failure (and what it taught).
- The moment the instrument first worked (first resonance, first note, first
  test pass).

### Optional Spread 6 — Context and Related Work

Cross-links to instruments in the series that share a mechanism, material,
or acoustic family. This spread activates if the Cross-Pollination Agent
(#247) has found connections; otherwise omit.

## image-gen-2 prompt discipline

Every image-gen-2 call for an instrument chapter follows this form:

```
[STYLE] [SUBJECT] [DOMINANT MATERIAL] [LIGHTING] [COMPOSITION] [CONSTRAINT]
```

Example:
```
Technical illustration style. Assembled handpan, 600 mm diameter,
2.4 mm dimpled 430 stainless steel shell, 9 tone fields. Natural
side-light from a high workshop window. Three-quarter isometric view,
full shell visible, no cropping. Not a photograph — concept render only.
```

Constraints to always include in instrument renders:
- "Not a photograph — concept render only." (prevents derivative from being
  read as build evidence)
- Name the material explicitly (prevents material hallucination)
- Name the measurement if scale matters ("600 mm diameter") — but repeat
  it from the authority artifact, do not invent

Constraints to always include in the sidecar:
- `derivative: true`
- `non_dimensional: true` (unless the render has no visible dimensions)
- `prompt: "<exact string used>"`

## Proof review before chapter merge

No chapter merges to its target repo without:

1. **Authority review**: every number in captions and the build section traced
   to its source artifact (parameter CSV row, drawing dimension, BOM line, test
   log entry). Any number that cannot be traced is removed.
2. **Derivative review**: every image-gen-2 asset confirmed to carry a
   `derivative: true` sidecar. No asset relabeled as a photograph or build
   evidence.
3. **Packet status review**: the cover's packet-status block matches the repo's
   actual gate state on the day of merge. If the repo's gate status changes
   between chapter draft and merge, the cover is updated.
4. **Alt text review**: every image has meaningful alt text. Concept renders say
   "Concept render of [instrument]: [brief description]. Not a photograph; not
   build evidence." in their alt text.

## First chapter selection

When the readiness matrix (Refs #92) produces a first gated repo, start with
the instrument whose authority artifacts are the most complete:
- Most columns of the parameter CSV filled in
- Dimensioned drawing showing the governing geometry
- At least one measurement log entry

A chapter built from strong authority artifacts is faster to produce and
safer to review than one that leans heavily on image-gen-2 fill.
