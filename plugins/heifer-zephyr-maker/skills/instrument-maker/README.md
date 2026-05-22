# instrument-maker

A Claude skill for designing, prototyping, validating, and shipping
musical instruments end-to-end. Built by Tony Koop on 17+ years of
instrument-making experience and 70+ public repos at
[github.com/tonykoop](https://github.com/tonykoop).

This is **v4.3** — the version with
specialist sub-agents, guided design intake, CNC operation/setup planning,
richer Wolfram package generation, a DXF-first visual-output contract,
a queryable catalog database, family-aware design, an empirical-learning
loop, and public build-log site generation. The audience widened in v4: where v3
was for Tony and an agent collaborator, v4 is intended to be drivable by
another maker, a student, or a recruiter exploring the work.

## What this skill does

When loaded into a Claude session that has access to its file tools
(Cowork, Claude Desktop with the skills plugin, or Claude Code), this
skill turns prompts like:

- *"Design an A4 NAF in cherry"*
- *"Make me a vessel-flute family in C major: tonic, fifth, octave"*
- *"What miter angle for a 16-segment ashiko?"*
- *"Record a measurement: A4 tongue reads 442.3 Hz"*
- *"Promote the Master Catalog to a database and tell me which cherry
  tongue drums are now mistuned"*

into real artifacts: parametric design tables, DXF-first fabrication drawings,
derived SVG/PDF previews,
sourcing packets, CNC setup sheets, Wolfram model packages, capstone
slide decks (.pptx), printable shop packets (.pdf), build-log static
sites, OpenSCAD masters, and a SQLite catalog.

The skill is heavily progressive-disclosure — `SKILL.md` is the
orchestrator; everything else loads on demand.

## Folder layout

```
instrument-maker/
├── SKILL.md                          # the orchestrator
├── manifest.yaml                     # v4.3 structured discoverability
├── README.md                         # this file
├── getting-started.md                # for outside makers
├── agents/
│   ├── claude.yaml                   # Claude triggers and deliverables
│   ├── openai.yaml                   # OpenAI agent triggers
│   └── specialists/                  # v4 sub-agents
│       ├── acoustician.md
│       ├── manufacturing-planner.md
│       ├── documentarian.md
│       ├── verifier.md
│       └── red-team.md
├── references/                       # progressive-disclosure docs
│   ├── acoustic-models.md
│   ├── guided-design-intake.md       # NEW v4.2
│   ├── new-instruments-v4.md         # 12 v4 additions
│   ├── workbook-integration.md       # rewritten with actual schema
│   ├── catalog-database.md           # NEW v4
│   ├── family-aware-design.md        # NEW v4
│   ├── empirical-learning-loop.md    # NEW v4
│   ├── doe-integration.md            # NEW v4
│   ├── build-log-site.md             # NEW v4
│   ├── repo-relationships.yaml
│   ├── drawing-and-visualization.md
│   ├── manufacturing-and-cnc.md
│   ├── queued-instruments.md
│   ├── presentation-and-print-packets.md
│   ├── sourcing-and-production.md
│   ├── wolfram-workflow.md
│   └── techniques/
│       └── headstock-driven-deep-bore-drilling.md
├── scripts/
│   ├── inspect_instrument_workbook.py
│   ├── inspect_pdf_geometry.py
│   ├── design_input.py               # NEW v4.2
│   ├── generate_cnc_plan.py          # NEW v4.2
│   ├── generate_wolfram_packet.py    # NEW v4.2
│   ├── generate_build_packet.py
│   ├── generate_capstone_docs.py
│   ├── generate_openscad_starter.py
│   ├── validate_packet.py            # extended with --fix mode (v4)
│   ├── build_catalog_db.py           # NEW v4
│   ├── generate_drawings.py          # NEW v4; DXF-first visual update
│   ├── validate_visual_outputs.py    # NEW issue #148 visual contract gate
│   ├── generate_site.py              # NEW v4
│   ├── record_measurement.py         # NEW v4
│   └── migrate_packet.py             # NEW v4
└── assets/
    └── templates/
        ├── instrument-drawing-brief.md
        └── wolfram-notebook-starter.wl
```

## Required tools

Python 3.10+ with these packages:

```
openpyxl       # for .xlsx I/O (workbook inspectors, catalog db)
python-pptx    # for the capstone deck generator
reportlab      # for the print-packet PDF
pypdf          # for the PDF inspector
```

Install in a virtual environment to avoid polluting your global Python:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\Activate.ps1         # Windows PowerShell
pip install openpyxl python-pptx reportlab pypdf
```

Optional but recommended:

- **OpenSCAD** — to render `cad/<slug>_master.scad` into 3D previews.
- **Wolfram Engine / Mathematica** — to run the generated
  `wolfram/instrument-model.wl`.
- **LibreCAD/QCAD/Fusion/Rhino** — to inspect generated DXF drawings.
- **Inkscape** — to inspect derived SVG previews.

## Installing the skill into Claude Desktop / Cowork

The skill installs by being copied into the Claude Desktop skills folder:

```
C:\Users\<you>\AppData\Roaming\Claude\local-agent-mode-sessions\
  skills-plugin\<plugin-id>\<install-id>\skills\instrument-maker\
```

For Tony's environment, see the PowerShell snippet in
`getting-started.md`.

## What v4 changed from v3

v4.3 adds the DXF-first visual-pipeline update on top of the v4.2
"make it easier to drive" layer:

- **Guided intake** — `design_input.py` turns fuzzy prompts into
  `design-intake.json` and `design-input-row.csv`.
- **CNC operation plans** — `generate_cnc_plan.py` emits pre-CAM setup
  sheets, operation CSVs, and a machine-readable CNC plan.
- **Wolfram package generator** — `generate_wolfram_packet.py` emits a
  richer `.wl` source package with model explorers, audio preview, and
  validation scaffolding.
- **Photo pipeline wiring** — shotlists now explicitly route into the
  repo-level photo-pipeline rules and build-log site image pickup.
- **DXF-first visual contract** — string-family and flat-layout packets
  now use DXF as fabrication geometry authority, SVG/PDF as derived previews,
  and optional image-gen-2 prompt scaffolds as non-dimensional concept imagery.
  `validate_visual_outputs.py` checks DXF units, layers, authority paths,
  preview paths, and prompt labels.

- **Specialist sub-agents** — split the orchestrator into
  acoustician / manufacturing-planner / documentarian / verifier /
  red-team. Each is a focused reference loaded on dispatch.
- **Catalog as a database** — Master Catalog promoted from xlsx to
  SQLite via `build_catalog_db.py`.
- **Family-aware design** — propose a family scaling law and emit
  one family-spec.csv that drives N packets.
- **Empirical-learning loop** — `record_measurement.py` ingests tuner
  readings and updates per-family corrections.
- **Build-log site** — `generate_site.py` emits a recruiter-grade
  static site per packet.
- **Iterating verifier** — `validate_packet.py --fix` repairs the
  85% → 100% gap automatically.
- **12 new instrument families** documented in `new-instruments-v4.md`
  (handpan, steel pan, tubular bells, cajón, glockenspiel, rainstick,
  steel/wood-shell/ceramic tongue drums, ceramic electric violin,
  Great Highland bagpipe, duntong).
- **Migration script** — `migrate_packet.py` upgrades v3 packets in
  place.
- **Manifest** — `manifest.yaml` lists every reference, specialist,
  and script with structured metadata for fast discovery.

## License

Same as the underlying instrument-maker repo (MIT). Build something
beautiful with it.
