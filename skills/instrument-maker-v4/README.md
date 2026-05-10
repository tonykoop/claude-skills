# instrument-maker-v4

A Claude skill for designing, prototyping, validating, and shipping
musical instruments end-to-end. Built by Tony Koop on 17+ years of
instrument-making experience and 70+ public repos at
[github.com/tonykoop](https://github.com/tonykoop).

This is **v4.3** — the version with specialist sub-agents, guided design
intake, CNC operation/setup planning, richer Wolfram package generation,
a queryable catalog database, family-aware design, an empirical-learning
loop, public build-log site generation, root/nested validation, close-ready
repo triage, and lightweight public-readiness adjuncts for resources and jig
decisions. The audience widened in v4: where v3 was for Tony and an agent
collaborator, v4 is intended to be drivable by another maker, a student, or a
recruiter exploring the work.

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

into real artifacts: parametric design tables, dimensioned SVG drawings,
sourcing packets, CNC setup sheets, Wolfram model packages, capstone
slide decks (.pptx), printable shop packets (.pdf), build-log static
sites, OpenSCAD masters, and a SQLite catalog.

The skill is heavily progressive-disclosure — `SKILL.md` is the
orchestrator; everything else loads on demand.

## What this skill does NOT do

- **Run tools for you.** It generates inputs and operation plans for SolidWorks,
  Wolfram/Mathematica, OpenSCAD, and CNC machines — it does not operate those
  tools itself.
- **Guarantee acoustic accuracy.** First-order bore, tongue, and shell models
  are sanity checks. Physical prototyping and measured tuning still determine
  the real instrument.
- **Substitute for shop time.** Validator-clean does not mean shop-proven.
  CAD rebuilds, supplier confirmations, prototype measurements, and photo
  review remain human steps.
- **Advise on cultural or IP ownership.** Traditional-instrument repos with
  cultural or provenance sensitivity must be reviewed by a human before going
  public.

## Known limitations (v4.3)

- `validate_packet.py --mode root` checks file presence and structure; it
  does not verify acoustic correctness or build feasibility.
- `resources.md` and `jig-decision.md` are recommended adjuncts, not hard
  validator gates — they become gating items in v5.
- Handpan and empirical metal-forming instruments treat acoustic formulas as
  first-order estimates only; final tuning requires physical iteration.
- Multi-part SolidWorks assemblies are not yet fully supported in
  `ingest_dimension_csv.py`; see `references/solidworks-integration.md §6`.
- Private/IP-sensitive repos (e.g., `wooden-hang`) are excluded from
  public-ready sprint reports unless explicitly included by Tony.

## Folder layout

```
instrument-maker-v4/
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
│   ├── golden-examples.md            # public-safe done-bar examples
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
│   ├── solidworks-integration.md        # family-spec → SW design table handoff
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
│   ├── generate_drawings.py          # NEW v4
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
- **Inkscape** — to inspect the generated SVG drawings.

## Installing the skill into Claude Desktop / Cowork

The skill installs by being copied into the Claude Desktop skills folder:

```
C:\Users\<you>\AppData\Roaming\Claude\local-agent-mode-sessions\
  skills-plugin\<plugin-id>\<install-id>\skills\instrument-maker-v4\
```

For Tony's environment, see the PowerShell snippet in
`getting-started.md`.

## What v4 changed from v3

v4.3 adds the remaining "make it easier to drive" layer from the brainstorm:

- **Root/nested validation** — `validate_packet.py --mode auto` handles both
  root-mode repos and nested `build/packet` layouts.
- **Close-ready triage** — `scripts/report_close_ready.py` dry-runs open
  build-packet issues against local repos and suggests next issue comments.
- **Root-mode scaffolding** — `templates/instrument-repo-root-mode/` and
  `scripts/new_instrument_repo.py` create public-safe Mode A repo starters.
- **Resources and jig decisions** — v4.3 scaffolds `resources.md`,
  `jig-decision.md`, and `jigs/` as public-readiness adjuncts before their
  fuller v5 automation.
- **Challenge-tested packets** — rainstick, kora, and handpan validated
  root-mode generation across empirical/noise, string/resonator, and
  high-uncertainty tuned-metal cases.

- **Guided intake** — `design_input.py` turns fuzzy prompts into
  `design-intake.json` and `design-input-row.csv`.
- **CNC operation plans** — `generate_cnc_plan.py` emits pre-CAM setup
  sheets, operation CSVs, and a machine-readable CNC plan.
- **Wolfram package generator** — `generate_wolfram_packet.py` emits a
  richer `.wl` source package with model explorers, audio preview, and
  validation scaffolding.
- **Photo pipeline wiring** — shotlists now explicitly route into the
  repo-level photo-pipeline rules and build-log site image pickup.

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
- **Public-ready examples** — `references/golden-examples.md` links to safe
  packet examples and names what future agents should copy from each.
- **Migration script** — `migrate_packet.py` upgrades v3 packets in
  place.
- **Manifest** — `manifest.yaml` lists every reference, specialist,
  and script with structured metadata for fast discovery.

## See also

- `references/solidworks-integration.md` — complete family-spec → SW design
  table handoff: header normalization, global variable rules, import steps,
  troubleshooting, and quality gates.
- `references/golden-examples.md` — public-safe done-bar repos annotated with
  what future agents should copy from each.
- `docs/v4.3-release-notes.md` — what's new, smoke test, and known boundaries.
- `getting-started.md` — install and first-run guide for outside makers.

## License

Same as the underlying instrument-maker repo (MIT). Build something
beautiful with it.
