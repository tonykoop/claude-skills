# Getting Started — instrument-maker-v4

This guide is for someone new to the skill. If you're Tony, skip to
[Five-minute install](#five-minute-install).

## What is this?

A Claude skill that lets the AI design real musical instruments
end-to-end. You ask it to size a flute, scale a marimba family, or
publish a build log — it picks the right physics model, applies
empirical corrections from 17 years of Tony's builds, generates the
spreadsheet/drawings/CNC setup plan/Wolfram package/BOM/deck/site, and
validates the output.

The skill assumes you have:

- Claude Desktop, Cowork mode, or Claude Code.
- A working folder where files can be created (the connector grants
  this).
- Python 3.10+ with `openpyxl`, `python-pptx`, `reportlab`, `pypdf`.

## Five-minute install

### Cowork / Claude Desktop (Windows)

1. Clone or download this folder.
2. Run from PowerShell:

   ```powershell
   $sourceDir = "C:\Users\$env:USERNAME\OneDrive\Documents\GitHub\instrument-maker-v4"
   $skillsDir = (Get-ChildItem "$env:APPDATA\Claude\local-agent-mode-sessions\skills-plugin" -Directory `
       | Sort-Object LastWriteTime -Descending `
       | Select-Object -First 1).FullName
   $installDir = (Get-ChildItem $skillsDir -Directory | Sort-Object LastWriteTime -Descending `
       | Select-Object -First 1).FullName
   $target = Join-Path $installDir "skills\instrument-maker-v4"
   New-Item -ItemType Directory -Force -Path $target | Out-Null
   Copy-Item -Path "$sourceDir\*" -Destination $target -Recurse -Force
   Write-Host "Installed to: $target"
   ```

3. Restart Claude Desktop. The skill should appear in
   `<available_skills>` in your next session, named
   `instrument-maker-v4`.
4. Install the Python deps:

   ```powershell
   pip install openpyxl python-pptx reportlab pypdf
   ```

### Cowork (macOS / Linux)

The skill folder for Mac/Linux Cowork installs is
`~/.claude/skills/` (or the equivalent under
`~/Library/Application Support/Claude/...` on macOS — check via
`/help` in Claude Desktop).

```bash
cp -r instrument-maker-v4 ~/.claude/skills/
pip3 install openpyxl python-pptx reportlab pypdf
```

### Claude Code

Place the folder under your project's `.claude/skills/` directory or
the global skills location reported by `claude config get
skills-path`.

## Smoke test

Open a new Claude session in the same workspace and try:

> *"Use instrument-maker-v4 to inspect Musical Instruments V2.xlsx and
> tell me how many sheets it has."*

Expected: Claude triggers the skill, runs
`scripts/inspect_instrument_workbook.py`, and reports the sheet count
(54 in the May 2026 baseline).

Then try a real design:

> *"Design a small ocarina-style vessel flute targeted at C5. Use the
> Helmholtz model. Generate dimensioned SVG drawings."*

Expected: Claude dispatches the acoustician specialist, picks the
Helmholtz model, sizes a chamber for ~523 Hz, emits a `family-spec.csv`,
runs `generate_drawings.py`, and produces an SVG with title block,
datums, and a dimensioned section view.

## How the skill thinks (mental model)

When you prompt, the skill:

1. **Reads `SKILL.md`** as the orchestrator.
2. **Decides which specialist to dispatch:**
   - Sizing / tuning → `acoustician`
   - Drawings / cut lists / CNC plans → `manufacturing-planner`
   - Decks / packets / sites / READMEs → `documentarian`
   - "Is this packet complete?" → `verifier`
   - "What could go wrong?" → `red-team`
3. **Loads the relevant `references/` doc** for the work — not all 16,
   just the ones that match.
4. **Runs scripts** for repetitive deterministic work (guided intake,
   drawings, CNC setup plans, Wolfram packages, deck, site, db build).
5. **Writes artifacts** into a `build-packets/<slug>/` folder.

You're never blocked by the skill — if it's missing context, it asks.

## Things you'll commonly do

### Design a single instrument

> *"Design a Native American style flute in G4, padauk wood, 0.875"
> bore."*

The skill will create a `build-packets/<date>-naf-g4-padauk/` folder
with `design.md`, `bom.csv`, `cut-list.csv`, drawings, deck, packet,
site.

### Start from a fuzzy idea

> *"I want a small Duntong in D minor pentatonic, probably cherry. Help
> me turn that into a real packet."*

The skill runs `design_input.py`, infers the closest workbook sheet, and
creates `design-intake.json` plus `design-input-row.csv` before it starts
specialist work.

### Plan CNC setup before CAM

> *"Generate the CNC operation plan for this packet before I open Fusion."*

The skill runs `generate_cnc_plan.py` and writes `cnc/cnc-plan.json`,
`cnc/operations.csv`, and `cnc/setup-sheet.md`. This is a pre-CAM plan,
not verified G-code.

### Generate the Wolfram package

> *"Make the Wolfram model package for this build packet."*

The skill runs `generate_wolfram_packet.py` and writes
`wolfram/instrument-model.wl` with formulas, `Manipulate` controls,
audio preview, and validation plot scaffolding.

### Design a family

> *"Design a tongue-drum family: small in D minor pentatonic, medium
> in A minor pentatonic, large in D minor."*

The skill emits a `family-spec.csv` and N packet folders, plus a
family-overview SVG.

### Record a measurement

> *"I just measured the small tongue drum. The A4 tongue reads
> 442.3 Hz on a Korg OT-120 in shop conditions, ~68F, ~45% RH."*

The skill runs `record_measurement.py`, updates `validation.csv`,
appends to the corrections database, and tells you which sibling
packets are affected.

### Audit a packet

> *"Audit my latest packet for risks before I commit to building it."*

The skill dispatches the red-team specialist and writes `risks.md`
with five categories of risks, each with a verification test.

### Migrate a v3 packet to v4 format

> *"I have a v3 packet at build-packets/2026-04-15-tng-001-tongue-drum.
> Migrate it to v4."*

The skill runs `migrate_packet.py`, scaffolds `risks.md`, regenerates
missing drawings, and emits the build-log site.

### Promote the catalog to a database

> *"Promote Instrument Workshop Master v3.xlsx to a SQLite database and
> tell me which open-pipe instruments don't have CAD files yet."*

The skill runs `build_catalog_db.py`, then queries the resulting
`catalog.sqlite` and reports.

## Where to learn more

- The skill's own `SKILL.md` is a good orientation read.
- `references/new-instruments-v4.md` enumerates the 12+ instrument
  families v4 added vs v3.
- The repo at github.com/tonykoop has 70+ public instrument repos;
  `tongue-drum`, `gemshorn`, `udu`, `ocarina`, and `transverse-flute`
  are the *done bar* — the canonical examples of what a finished
  instrument-maker output looks like.

## Getting help

If the skill produces something wrong, the fastest path is:

1. Tell Claude what was wrong specifically.
2. If it's a script bug, the script is in `scripts/<name>.py` —
   readable Python, no magic.
3. If it's a physics error, check the relevant section of
   `references/acoustic-models.md` — the formulas are spelled out and
   sourced.
4. If it's a workbook misread, check `references/workbook-integration.md`
   — the schemas are documented column-by-column.

Open an issue on the underlying repo; Tony reads them.
