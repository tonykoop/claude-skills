---
name: instrument-maker
version: 4.5.0
last-updated: 2026-06-13
description: >-
  (v4.5.0) Design, document, validate, and ship musical instruments end-to-end:
  woodwinds, strings, drums, percussion, idiophones, hybrid acoustic/electric,
  and brass/horn concepts. Covers acoustic physics, guided intake, parametric
  design tables, CAD/CNC/SolidWorks/OpenSCAD/Wolfram, DXF-first fabrication
  geometry, CNC setup plans, BOMs, sourcing/cut/validation packets, printable
  shop packets, slip-cast workflows, family-aware design, empirical learning,
  build-log sites, specialist sub-agents, and the Master Catalog. Trigger for
  instrument design, builds, BOMs, sourcing, capstone/print packets, CNC plans,
  Wolfram packets, OpenSCAD masters, DXF drawings, visual-output validation,
  and shop documentation.
---

# Instrument Maker v4.3

Design, document, validate, and ship musical instruments end-to-end:
acoustic physics → parametric design sheet → BOM/sourcing/cut list →
manufacturable drawings → CNC/laser/lathe plans → assembly manual →
tuning validation → capstone slide deck (.pptx) → printable shop packet (.pdf) →
public build-log site → measured-data feedback loop into the catalog database.

This skill is built for Cowork mode where Claude can produce real .xlsx, .docx,
.pptx, .pdf, .svg, and .sqlite files. When operating in a constrained environment
(Excel-only, web-only, no shell), gracefully degrade to Markdown/HTML/CSV
deliverables and explicitly mark which generators were skipped.

## What's new in v4.3 / v4.2 (vs v4.1)

v4.1 built the architecture: specialists, catalog database, family-aware
design, empirical learning, drawings, build-log site, migration, and
SolidWorks design tables. v4.2 tightens the remaining brainstorm ideas that
make the skill easier to drive from a fuzzy request and more useful before CAM
or Wolfram hand-work starts:

1. **Guided design intake.** `scripts/design_input.py` turns a rough prompt
   into `design-intake.json` and `design-input-row.csv`, with optional sheet
   inference against `Musical Instruments V2.xlsx`. Read
   `references/guided-design-intake.md` when the user has not supplied a
   Master Catalog row or a populated design sheet.
2. **CNC operation planning.** `scripts/generate_cnc_plan.py` emits
   `cnc/cnc-plan.json`, `cnc/operations.csv`, and `cnc/setup-sheet.md`. This
   is not G-code; it is the operation graph, datum plan, tooling, workholding,
   and release checks a human uses before CAM.
3. **Richer Wolfram package generation.** `scripts/generate_wolfram_packet.py`
   emits `wolfram/instrument-model.wl` with model-specific formulas,
   `Manipulate` controls, audio preview, validation plot scaffolding, and
   optional `wolframscript` execution when available.
4. **Photo pipeline wiring.** `photo-shotlist.md` remains a required packet
   scaffold, but v4.2 explicitly ties it to the repo-level
   `docs/photo-pipeline.md` rules and the build-log site image pickup.
5. **DXF-first visual pipeline.** String-family and flat-layout packets now
   declare `visual_output_targets`, emit DXF as fabrication geometry authority,
   treat SVG/PDF as derived previews, and may include image-gen-2 prompt
   scaffolds for non-dimensional concept imagery. See
   `references/drawing-and-visualization.md` and
   `scripts/validate_visual_outputs.py`.

## What's new in v4 (vs v3)

v3 was a true progressive-disclosure skill: 8 reference docs, 6 scripts, agent
configs, a worked tongue-drum example. v3's `validate_packet.py` docstring
captured the architecture in one line: *"the verifier-agent role formalized as a
script. Catches ~80% of what a human reviewer would otherwise file as a
follow-up issue."* v4 closes the remaining 20%, opens the skill to outside
makers/students/recruiters, and treats the multi-instrument catalog as an
asset that compounds over time.

The five v4 architecture shifts:

1. **Specialist sub-agents.** v4 splits the orchestrator into named roles:
   `acoustician` picks the model and applies empirical corrections;
   `manufacturing-planner` owns CAD/CNC/sourcing; `documentarian` produces
   deck/print packet/visual BOM/site; `verifier` enforces the quality gates
   (and now *iterates* — fixes what it can, escalates the rest); `red-team`
   intentionally tries to break the design with a structured `risks.md`.
   The orchestrator (this SKILL.md) decides which specialist to call when.
   See `agents/specialists/`.

2. **Catalog as a database.** The Master Catalog and related tables in
   `Instrument Workshop Master v3.xlsx` get promoted to a queryable SQLite
   database (`scripts/build_catalog_db.py`). The xlsx becomes a *view*, not
   the source of truth. This is what enables cross-instrument queries
   ("every open-pipe instrument with measured-vs-predicted error >5 cents")
   and feeds the empirical-learning loop. See
   `references/catalog-database.md`.

3. **Family-aware design.** v3 produced family-aware *packets* (S/M/L/XL
   members of one design). v4 lets the user say "design a new vessel-flute
   family" and proposes the family scaling law, generates members at
   acoustically-reasonable size ratios, and produces a `family-spec.csv` that
   feeds N packet generations. See `references/family-aware-design.md`.

4. **Empirical-learning loop.** v3 has `validation.csv` with target columns
   but no path from "I measured this with a tuner" back into the design
   sheet. v4 ships `scripts/record_measurement.py` and a
   per-family corrections database. New measurements update K2, K-constant,
   and end-correction tables; future packets in the same family read the
   updated values automatically. See `references/empirical-learning-loop.md`.

5. **Public build-log site.** The capstone deck is for recruiters, the print
   packet is for the shop. v4 adds a third recruiter-grade artifact: a static
   site per packet (`scripts/generate_site.py`) so other makers can follow a
   build online. This is also what makes v4 *shareable* — the static site is
   how an outside reader encounters Tony's work. See
   `references/build-log-site.md`.

Plus — and this is the one that matters most for triggering reliability:
the SKILL frontmatter description was rewritten to be more "pushy" so the
agent invokes the skill on family-only or sub-task prompts, not just on
"design a [named instrument]" prompts.

## Output shape: two valid modes

The skill produces deliverables in **one of two folder shapes**, not both. Pick
the right one based on what the user has set up:

**Mode A — Project-repo at root** (use when the user starts a fresh single-instrument repo, e.g. `drone-flutes/`, `gemshorn/`, `tongue-drum/`). Files land at the top level of the repo: `README.md`, `risks.md`, `Drone-Flutes-Design.xlsx`, `Drone-Flutes-BOM-Build-Method.docx`, `inlay-patterns/`, `sw-reference/`, `LICENSE`, `.gitignore`, `images/`, `drawings/`, `site/`. This shape matches the *done bar* reference repos (tongue-drum, gemshorn, udu, ocarina, transverse-flute). Use Mode A when the user names the project as a folder ("design drone flutes in `drone-flutes/`") or works inside an existing single-instrument repo.

**Mode B — Build-packet folder** (use inside a multi-instrument workspace where many packets coexist). Files land in `build-packets/<date>-<instrument-id>-<slug>/` with the structured set: `design.md`, `bom.csv`, `sourcing.csv`, `cut-list.csv`, `validation.csv`, `assembly-manual.md`, `supplier-rfq.md`, `visual-bom-brief.md`, `drawing-brief.md`, `wolfram-starter.wl`, `risks.md`, `photo-shotlist.md`, `README.md` (per-packet), `drawings/`, `cad/`, `cnc/`, `images/`, `data/`, `wolfram/`, `site/`. Use Mode B when the user is generating a packet from the Master Catalog ("create a build packet for TNG-001"), when they're already in a folder with sibling `build-packets/...` folders, or when the prompt explicitly mentions "build packet."

Both modes ship the same v4.2 obligations: guided intake when needed,
parametric design surface (xlsx or design.md), BOM, sourcing, cut list,
validation, drawings, CNC operation/setup plan, Wolfram package, deck, print
packet, site, risks, photo-shotlist, and the README. The container differs.

If the user's intent is ambiguous, ask. A wrong-mode delivery wastes work — single-instrument repos with `build-packets/<slug>/` deeply nested feel awkward; multi-instrument folders with files at root collide.

## Operating Principles (carry forward from v3)

- Start from user artifacts before designing from memory: workbooks,
  CAD/PDF drawings, photos, sketches, build logs, supplier specs, measured
  prototypes, prior repo files.
- Keep calculations parametric. In spreadsheets, write formulas that
  reference input cells. Do not paste static computed dimensions unless the
  user asks for a snapshot.
- Separate concept imagery from manufacturable documentation. AI-generated
  images are useful for ideation, BOM plates, ergonomics, and visual
  communication; critical dimensions must come from formulas, CAD, measured
  artifacts, or explicitly marked assumptions.
- Use inches by default for Tony's shop and workbooks, with metric
  equivalents where sourcing, traditional references, or Wolfram models
  benefit from SI.
- Prefer traceable design packages: design table, drawing, BOM, build
  method, validation checklist, and source/provenance notes.
- For sourcing, distinguish stable specifications from time-sensitive
  supplier facts. Verify current prices, availability, lead time, and
  shipping when the user asks for purchasing recommendations.
- Mark unknown or guessed dimensions as `TBD`, `assumption`, or
  `derived estimate`; ask for confirmation when an unknown affects safety,
  fit, tuning, or machining.

## Core Workflow (orchestrator view)

You — the orchestrator — read this SKILL.md, look at the prompt, and decide
which specialist to dispatch.

1. **Define the deliverable.** Design sheet? Build packet? Family roll-out?
   Drawing? Tuning analysis? Catalog query? Migration of a v3 packet to v4?
2. **Run guided intake if the request is fuzzy.** If the user has not supplied
   a Master Catalog row, design sheet, or concrete packet target, run
   `scripts/design_input.py` and read `references/guided-design-intake.md`.
3. **Look up the instrument.** Read `references/repo-relationships.yaml` to
   find the family, pipeline, status, and the *done bar* reference repo to
   model on. New instruments not in the registry get a row added during
   the work.
4. **Dispatch to the right specialist.**
   - Acoustic physics, scale tables, end corrections → `acoustician`
   - Drawings, CAD/CNC/laser/lathe plans, sourcing, cut lists →
     `manufacturing-planner`
   - Capstone deck, print packet, visual BOM, build-log site →
     `documentarian`
   - Quality-gate enforcement, packet completeness, tuning predictions vs
     measured → `verifier`
   - Failure-mode walk-through, ergonomic minimums, structural minimums,
     glue-joint risk → `red-team`
5. **Produce the artifact at the right fidelity.** Match the *done bar* of
   the reference repo, not the auto-generator's defaults.
6. **Validate.** Run the verifier specialist before declaring complete.
   v4 verifier *iterates* — it fixes what it can (placeholder fallbacks,
   missing TBDs the design sheet can answer, missing slides) for up to two
   passes, then escalates remaining findings to the human.
7. **Close the loop.** If the user provides measured data, write it through
   `scripts/record_measurement.py` so the empirical-learning loop updates
   the per-family corrections.

## Reference Map (load on demand)

Read the reference that matches the work, not all of them. v4's references:

- `references/guided-design-intake.md` — *new in v4.2*. How to turn fuzzy
  prompts into `design-intake.json` and `design-input-row.csv`, infer likely
  workbook sheets, and keep unknowns visible before specialists start.
- `references/acoustic-models.md` — formulas, tuning, validation checks for
  pipes, beams, strings, resonators, membranes, hybrid instruments. Includes
  Tony's NAF K2 corrections, scale offset tables, instrument-specific
  empirical corrections, and material K-constant tables for cantilever and
  free-free beams. **Read the "Empirical-correction guard rules" section
  before applying any K-constant or K2 correction** — they only apply to
  specific physical models, and misapplying them will produce wrong
  predictions.
- `references/new-instruments-v4.md` — additions covering the 12+
  instrument families that exist in `Musical Instruments V2.xlsx` but
  weren't called out in v3: Handpan, Steel Pan, Tubular Bells, Cajón,
  Glockenspiel, Rainstick, Steel Tongue Drum, Wood Shell Tongue Drum,
  Ceramic Tongue Drum, Ceramic Electric Violin, Great Highland Bagpipe,
  Duntong. Each has the governing model, scale conventions, key formulas,
  and the workbook sheet to consult.
- `references/workbook-integration.md` — *rewritten in v4* with the actual
  schema of `Musical Instruments V2.xlsx` (54 sheets) and
  `Instrument Workshop Master v3.xlsx` (16 sheets including the new DoE
  Studies sheet). Documents the Master Catalog table (`Table_2`, 24
  columns) and the 9 other named tables that drive the catalog. **This is
  the canonical schema doc for the workbook → database promotion in v4.**
- `references/catalog-database.md` — *new in v4*. SQLite schema generated
  from the Master Catalog tables, query patterns ("every cherry tongue drum
  with measured tuning error >5 cents"), and the script that builds the
  database from the xlsx. The xlsx remains the human-edit surface; the db
  is the read API.
- `references/family-aware-design.md` — *new in v4*. How to propose a
  family scaling law (vessel-flute Helmholtz scaling, marimba-bar
  cantilever scaling, drum-bowl segmented scaling) and emit a
  `family-spec.csv` that drives N packet generations in one shot.
- `references/empirical-learning-loop.md` — *new in v4*. The
  `record_measurement.py` flow, the per-family corrections database, and
  how new measurements propagate to existing packet predictions in the
  same family.
- `references/doe-integration.md` — *new in v4*. Wires the new DoE Studies
  sheet in `Instrument Workshop Master v3.xlsx` to the protocol/data
  paths in each instrument's GitHub repo. When a user mentions a DoE,
  this is how the skill finds the protocol and writes results back.
- `references/build-log-site.md` — *new in v4*. Static-site format spec
  (Astro-style, but emitted as plain HTML for portability), per-packet
  page structure, and the `generate_site.py` flow.
- `references/repo-relationships.yaml` — sister-repo registry mapping
  every instrument slug to its acoustic family, shop pipeline, status, and
  related repos. Used by the deck/README/site generators to auto-link
  cross-references. **Look up an instrument here before generating a
  packet — it tells you the family it belongs to and the right "done bar"
  reference repo to model on.**
- `references/drawing-and-visualization.md` — Strat blueprint quality bar,
  technical drawing standards, BOM-with-images layouts, 3D views,
  ergonomic/player renderings. **In v4**, this is the spec
  `scripts/generate_drawings.py` reads when emitting per-family-member
  SVGs.
- `references/manufacturing-and-cnc.md` — CNC router, laser, lathe,
  segmented construction, steam bending, tooling, fixtures,
  design-for-manufacture checks. Includes Maker Nexus tool list,
  standard CNC bits, and the v4.2 CNC operation-plan contract.
- `references/queued-instruments.md` — research dimensions for Kora,
  Ngoni, Stave Lute/Oud, and other roadmap instruments.
- `references/presentation-and-print-packets.md` — capstone slide deck
  structure, printable packet structure, file maps, screenshots/previews,
  export guidance, cowork-mode .pptx and .pdf production.
- `references/sourcing-and-production.md` — procurement, supplier RFQs,
  cut lists, validation sheets, assembly manuals, visual BOM production
  guidance.
- `references/wolfram-workflow.md` — Wolfram Desktop/Cloud notebook
  patterns, file outputs, notebook ideas tied to instrument physics,
  and the v4.2 `generate_wolfram_packet.py` source/notebook flow.
- `references/solidworks-integration.md` — *new in v4.1*. The three
  pillars of Tony's SW workflow: global equations, design tables,
  master-sketch convention. Naming/units conventions across Excel, SW,
  and the macro CSV. The `Extract_Dimensions.swp` macro schema. The
  two SW scripts (`ingest_dimension_csv.py`,
  `generate_sw_design_table.py`). **Read this when the user mentions
  SolidWorks, design tables, equations, global variables, or
  extracting dimensions from CAD.**
- `references/techniques/headstock-driven-deep-bore-drilling.md` — niche
  technique reference; cite from packets that need it.

## The "Done Bar" — Reference Repos

Before generating a packet, read at least one repo from this list. They are
the canonical examples of what a finished instrument-maker output looks
like. Match their fidelity, not the auto-generator's defaults:

- **[tongue-drum](https://github.com/tonykoop/tongue-drum)** — *newest*
  v3-style packet. Custom README with hero image, magazine-baseline
  attribution, three-drum study plan, DoE protocol, skill index.
  Auto-generated capstone deck + print packet sit alongside hand-written
  content. **Use as the README template for every new instrument.**
- **[gemshorn](https://github.com/tonykoop/gemshorn)** — slip-cast
  horn-flute family. Closest match for any vessel-flute work. Has
  authentic-horn-build-plan, hole schedules (historical + modern),
  family-spec.csv, mold-and-slip-casting-plan, OpenSCAD master generator.
  **Use for slip-cast vessel-flute work.**
- **[transverse-flute](https://github.com/tonykoop/transverse-flute)** —
  slip-cast transverse flute family. Full mold-workflow, supplier-rfq,
  doe-plan, dimensioned SVG drawings per family member. **Use for
  slip-cast bore + family-aware drawings.**
- **[ocarina](https://github.com/tonykoop/ocarina)** — slip-cast vessel
  flute, single-instrument packet. v2 baseline output (auto-generated)
  plus hand-curated CAD/drawings/images. **Use for single-instrument
  slip-cast Helmholtz packets.**
- **[udu](https://github.com/tonykoop/udu)** — slip-cast vessel drum,
  family-aware packet. Dual-Helmholtz physics, S/M/L/XL family,
  family-aware OpenSCAD master. **Use for family-aware slip-cast packets
  and dual-port physics.**

When the user names an instrument that isn't in this list, look up its
`family` and `pipeline` in `references/repo-relationships.yaml`, then read
the matching reference repo above. A new vessel flute models on gemshorn
or ocarina; a new drum models on udu or djembe; a new wooden idiophone
models on tongue-drum.

## Specialists (when to call which)

The orchestrator dispatches; the specialists do the work. Each specialist
is a focused reference with its own loading priorities, quality gates, and
output conventions.

- `agents/specialists/acoustician.md` — picks the governing model, applies
  empirical corrections, writes the design.md governing-model section,
  emits frequency formulas and scale tables. Call when the user asks
  "what's the bore length for an A4 NAF" or "size the marimba bar in
  Padauk" or "tune this tongue drum to D minor pentatonic."
- `agents/specialists/manufacturing-planner.md` — owns CAD/CNC/laser/lathe
  and sourcing. Reads the design sheet, emits cut lists, tool lists,
  workholding plans, segmented construction math, and dimensioned
  DXF-first drawings via `scripts/generate_drawings.py`. Call when the user asks
  "what bits do I need" or "plan the CNC operations" or "draw the title
  block" or "what miter angle for a 16-segment ashiko."
- `agents/specialists/documentarian.md` — produces the deck (.pptx),
  print packet (.pdf), visual BOM, README, and build-log site. Reads the
  design.md and the reference repos to match the *done bar*. Call when
  the user asks "make me a capstone deck" or "produce the print packet"
  or "publish a build-log page" or "draft the README for this packet."
- `agents/specialists/verifier.md` — runs the v4 iterating verifier:
  validate_packet.py with --fix mode, two passes max, then escalate.
  Call when the user asks "is this packet complete" or "ship it" or
  after any specialist completes work.
- `agents/specialists/red-team.md` — walks the design looking for
  failure modes: stock clearance, glue-joint humidity tolerance, wall
  thickness vs wood modulus, hand-reach for 5th-percentile player.
  Emits a structured `risks.md` with a *test* attached to every risk.
  Call when the user asks "what could go wrong" or "audit this design"
  or before a packet ships.

## Deliverables (Capstone Standard)

Every serious project should produce, at minimum:

1. **Parametric design sheet** — Excel or Wolfram, formulas not values,
   blue inputs.
2. **Build packet folder** — `design.md`, `bom.csv`, `sourcing.csv`,
   `cut-list.csv`, `validation.csv`, `assembly-manual.md`,
   `supplier-rfq.md`, `visual-bom-brief.md`, `drawing-brief.md`,
   `wolfram-starter.wl`, `risks.md` *(new in v4 — emitted by red-team)*,
   plus placeholder `cad/`, `cnc/`, `drawings/`, `images/`, `data/` paths.
3. **Manufacturing drawings** — DXF-first flat geometry plus derived SVG/PDF
   previews. Title block, units, scale, datums, all critical dimensions,
   section/detail views, tolerances, material/finish notes, tool/access notes,
   revision/date. Emitted by `scripts/generate_drawings.py`; checked by
   `scripts/validate_visual_outputs.py`.
4. **CNC operation/setup plan** — *new in v4.2*. `cnc/cnc-plan.json`,
   `cnc/operations.csv`, and `cnc/setup-sheet.md`: operation order,
   datums, tools, workholding, checks, and explicit pre-CAM assumptions.
5. **Visual BOM** — assembly name, quote date, hero image, part rows with
   pictures, quantities, units, cost each, total, sourcing notes.
6. **Capstone slide deck (.pptx)** — title, project intent, file map,
   build workflow, design sheet summary, BOM/sourcing, drawings/CAD/CNC,
   visual BOM, assembly, validation, open risks, next actions.
7. **Printable shop packet (.pdf)** — cover/summary, quick start and file
   map, design intent, BOM, sourcing list, cut list, drawing brief,
   assembly manual, validation/tuning sheet, supplier RFQ, visual BOM
   brief, appendix.
8. **Wolfram package** — `.wl` source with parameters at top,
   `Manipulate`/plots/audio/3D, validation examples. In v4.2 this is
   generated by `scripts/generate_wolfram_packet.py`.
9. **Build-log site** *(new in v4)* — static HTML page per packet at
   `site/index.html`, generated by `scripts/generate_site.py`. Hero
   image, design intent, family overview, drawings, BOM, build steps with
   in-shop process shots, finished detail, link to GitHub repo. This is
   the *outside maker / recruiter* artifact.

The capstone deck, printable packet, and build-log site are the
recruiter-facing artifacts: they prove the design is documented well
enough that someone else could build it.

## Source Artifacts To Prefer

Local artifacts when present:

- `C:\Users\Tony\Documents\Claude\Projects\Career\flutes-staging\Flutes-AI.xlsx`
- `C:\Users\Tony\Documents\Claude\Projects\Career\Instrument Workshop Master v3.xlsx`
- `C:\Users\Tony\OneDrive\Documents\GitHub\Musical Instruments V2.xlsx`
- `C:\Users\Tony\Documents\GitHub\laser-cut\docs\Fender62stratocaster-blueprint.pdf`
- `C:\Users\Tony\Documents\GitHub\ashiko-drum-workshop\images\figure-bom-v2.png`
- `C:\Users\Tony\Documents\GitHub\instrument-maker\docs\wolfram-notebooks-roadmap.md`
- `C:\Users\Tony\Documents\GitHub\instrument-maker\docs\photo-pipeline.md`
- Repo examples: `flutes/`, `fujara/`, `tongue-drum/`, `ashiko-drum-workshop/`,
  `djembe/`, `dundun/`, `conga/`, `laser-cut/`, `gemshorn/`, `udu/`,
  `transverse-flute/`, `ocarina/`.

## Scripts

Run scripts from the skill folder. In Cowork bash, the skill folder is
`/sessions/.../mnt/<skill-folder>/`.

All v4 scripts accept `--dry-run` (preview-only, no files written) per
brainstorm Tier 4 #11.

### Inspect

```bash
python3 scripts/inspect_instrument_workbook.py "/path/to/Flutes-AI.xlsx" \
  --tables --formulas 6 --samples 6
python3 scripts/inspect_pdf_geometry.py "/path/to/blueprint.pdf"
```

### Guided design intake (new in v4.2)

Use before packet generation when the user starts from an idea instead of a
catalog row:

```bash
python3 scripts/design_input.py \
  --instrument-type "Duntong" \
  --family "cylindrical tongue drum" \
  --key-scale "D minor pentatonic" \
  --primary-material "Cherry" \
  --infer-sheet "Duntong" \
  --output-dir ./build-packets/<slug>/data
```

Emits `design-intake.json` and `design-input-row.csv`. Use
`--list-sheets` to inspect `Musical Instruments V2.xlsx` and
`--interactive` only when a terminal is available. See
`references/guided-design-intake.md`.

### SolidWorks (new in v4.1)

Read `references/solidworks-integration.md` first. Two scripts:

```bash
# Validate SW dimensions vs Excel design table
python3 scripts/ingest_dimension_csv.py \
  --csv /path/to/Extract_Dimensions-output.csv \
  --workbook /path/to/Drone-Flutes-Design.xlsx \
  --design-sheet Master_Inputs \
  --tolerance-percent 0.5 \
  --report findings.md

# Emit a SolidWorks design-table xlsx from family-spec.csv
python3 scripts/generate_sw_design_table.py \
  ./build-packets/<slug> \
  --output ./build-packets/<slug>/cad/sw-design-table.xlsx \
  --part-name TNG-001_TongueDrum
```

Sample SW assets ship in `assets/solidworks/`: the
`Extract_Dimensions.swp` macro binary, an example dimension-extract CSV,
and an example SW design table xlsx.

### Catalog database (new in v4)

Promote the Master Catalog from xlsx to SQLite:

```bash
python3 scripts/build_catalog_db.py \
  "/path/to/Instrument Workshop Master v3.xlsx" \
  --output ./catalog.sqlite
```

The db has tables for `master_catalog`, `design_sheets`, `cad_cnc_library`,
`production_log`, `materials_inventory`, `bom_budget`,
`suppliers_resources`, `training_plan`, `roadmap`, `doe_studies`. See
`references/catalog-database.md` for the schema and query patterns.

### Generate a build packet

```bash
python3 scripts/generate_build_packet.py \
  --master-workbook "/path/to/Instrument Workshop Master v3.xlsx" \
  --instrument-id TNG-001 \
  --design-workbook "/path/to/Musical Instruments V2.xlsx" \
  --design-sheet "Tongue Drum" \
  --output-root ./build-packets
```

### Generate DXF-first drawings and previews

```bash
python3 scripts/generate_drawings.py \
  ./build-packets/2026-05-02-tng-001-tongue-drum \
  --visual-output-targets dxf,preview-svg,image-prompts
```

Reads `family-spec.csv` (or the family table in `design.md`) and emits one
DXF per family member into `drawings/`, plus derived SVG previews when
requested. It also writes `visual-output-contract.json` and optional
`images/image-gen-2-prompts.md`. DXF is the fabrication-facing authority;
SVG/PDF are documentation previews. See `references/drawing-and-visualization.md`
for the spec and `scripts/generate_drawings.py --help` for options.

### Generate CNC operation/setup plan (new in v4.2)

```bash
python3 scripts/generate_cnc_plan.py \
  ./build-packets/2026-05-02-tng-001-tongue-drum
```

Emits `cnc/cnc-plan.json`, `cnc/operations.csv`, and
`cnc/setup-sheet.md`. This is a pre-CAM plan: operation graph, datum
strategy, tooling, workholding, checks, and release gates. It deliberately
does not emit unverified G-code.

### Capstone deck + print packet

```bash
python3 scripts/generate_capstone_docs.py \
  ./build-packets/2026-05-02-tng-001-tongue-drum \
  --title "Tongue Drum Capstone"
```

### Build-log static site (new in v4)

```bash
python3 scripts/generate_site.py \
  ./build-packets/2026-05-02-tng-001-tongue-drum \
  --output ./build-packets/2026-05-02-tng-001-tongue-drum/site
```

Emits a single-folder static site (HTML+CSS, no build step). Open
`site/index.html` in a browser, or copy to GitHub Pages for publishing.
See `references/build-log-site.md` for the page structure.

### OpenSCAD master starter

```bash
python3 scripts/generate_openscad_starter.py \
  ./build-packets/2026-05-02-tng-001-tongue-drum
```

### Wolfram model package (new in v4.2)

```bash
python3 scripts/generate_wolfram_packet.py \
  ./build-packets/2026-05-02-tng-001-tongue-drum
```

Emits `wolfram/instrument-model.wl` with formulas, `Manipulate` controls,
audio preview, validation plot scaffolding, and a `CreateDocument` notebook
entry point. Pass `--execute` only when `wolframscript` is installed and
local Wolfram execution is appropriate.

### Validate (with v4 iterate-fix mode)

```bash
python3 scripts/validate_packet.py \
  ./build-packets/2026-05-02-tng-001-tongue-drum --fix
```

`--fix` runs the iterating verifier: at most two passes, fixes what it
can (placeholder fallbacks, missing TBDs the design sheet can answer,
missing slides the deck generator can re-render), escalates the rest.

For visual-output contracts specifically:

```bash
python3 scripts/validate_visual_outputs.py \
  ./build-packets/2026-05-02-tng-001-tongue-drum --strict
```

This checks DXF units, required layers, geometry-authority entries, derived
preview paths, and non-dimensional image-gen-2 prompt labels.
`--strict` exits 1 on any remaining finding.

### Record a measurement (new in v4 — closes the empirical loop)

```bash
python3 scripts/record_measurement.py \
  --packet ./build-packets/2026-05-02-tng-001-tongue-drum \
  --note-id A4 \
  --measured-hz 442.3 \
  --tuner "Korg OT-120" \
  --environment "shop, 68F, 45% RH"
```

Updates the packet's `validation.csv`, computes cents error vs predicted,
appends to the per-family corrections database, and flags any sibling
packets in the same family whose predictions just shifted by more than
2 cents. See `references/empirical-learning-loop.md`.

### Migrate a v3 packet to v4 format (new in v4)

```bash
python3 scripts/migrate_packet.py \
  ./build-packets/2026-05-02-tng-001-tongue-drum
```

Adds `risks.md` skeleton, generates the missing SVG drawings, and (if
none exists) scaffolds the `site/` folder. Idempotent — safe to re-run.

## Quality Gates

- Physics model matches the instrument boundary conditions and excitation.
- A4 = 440 Hz and at least one known instrument dimension sanity-check
  correctly.
- Units, named inputs, and formula references are consistent.
- Critical dimensions are visible in drawings and map back to formulas or
  measured references.
- CNC/laser/lathe operations fit available tooling, stock, machine travel,
  workholding.
- Images clearly show the actual instrument/parts, not vague mood boards.
- BOM, drawing, CAD, and workbook IDs agree with the master catalog where
  applicable.
- Design notes identify assumptions, risks, next measurements, tuning/DoE
  validation.
- Capstone deck answers one practical question per slide; uses
  screenshots/previews instead of dense bullets.
- Printable packet is black-on-white, page-broken between major sections,
  with checkboxes/blanks for shop notes.
- *(v4 addition)* `risks.md` exists with at least one entry per risk
  category (acoustic, structural, ergonomic, supply, fit/finish), each
  with a verification test attached.
- *(v4 addition)* `site/index.html` renders cleanly and links to all
  packet artifacts; cross-links to the GitHub repo and to sibling family
  members are present.
- *(v4 addition)* If measured data exists, `validation.csv` includes
  cents error vs predicted, and the per-family corrections database has
  been updated.
- *(v4.2 addition)* If the user starts from a fuzzy idea, `data/design-intake.json`
  and `data/design-input-row.csv` exist and all unknowns remain explicit
  `TBD` values.
- *(v4.2 addition)* `cnc/cnc-plan.json` and `cnc/setup-sheet.md` exist
  before CAM/G-code work begins, and every operation has datum,
  workholding, tool, inputs, outputs, and release checks.
- *(v4.2 addition)* `wolfram/instrument-model.wl` exists for serious
  physics/validation work, or the packet explicitly states why Wolfram was
  skipped.
- *(v4.3 visual-pipeline addition)* When `visual_output_targets` requests
  DXF, `visual-output-contract.json` exists, DXF files are the geometry
  authority, SVG/PDF files are derived previews, DXF units/layers validate,
  and image-gen-2 prompts are labeled non-dimensional.

## Change history

See [`docs/skill-evolution/timeline.md`](../../../docs/skill-evolution/timeline.md) for the full version log. Recent entries:

- **v4.3 visual pipeline (2026-05-10)** — DXF-first visual output contract for string-family/flat-layout packets; SVG/PDF are derived previews; optional image-gen-2 prompt scaffolds are non-dimensional; `validate_visual_outputs.py` checks units, layers, authority paths, previews, and prompt labels.
- **v4.2 (in development, 2026-05-06)** — Path-separator normalization in `validate_packet.py:check_referenced_files_exist()` so Windows-authored decks (`drawings\foo.svg`) validate cleanly on Linux/Cowork. Closes the v4.1 ocarina-run finding (10 → 0 spurious findings after `risks.md` scaffold). Plus the previously-landed v4.2 surface: guided design intake, CNC operation/setup plans, Wolfram model packet generator.
- **v4.1 (2026-05-05)** — SolidWorks design-table integration (generator + ingest + round-trip verification scripts).
- **v4** — Specialist sub-agents, Master Catalog database, family-aware design, empirical-learning loop, dimensioned SVG drawings, build-log site generator.

## Connectors

This skill works best with these MCP connectors. Claude will suggest connecting any that aren't already linked at the point they're needed (via `mcp__mcp-registry__suggest_connectors`).

- **Wolfram** (`de1d1dc7-ec10-459d-b511-797982834b43`) — required for live acoustic-law evaluation, parametric design tables, tube/bore/string math, intervals. Suggest at first acoustic computation if not connected.
- **Adobe for Creativity** (`22854937-9510-4b57-9230-62c820102d8f`) — optional for visual register exports, capstone deck images, shop packet covers, photo shotlist editing.
- **Blender** (local stdio MCP — no registry UUID, requires the Blender MCP add-on) — optional for 3D concept renders and parametric mesh experiments. Skip `suggest_connectors`; direct the user to install the add-on.

