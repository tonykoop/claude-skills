# Public Quickstart - Instrument Maker v4.3

This quickstart is for makers, students, recruiters, and agent developers who
want to try `instrument-maker-v4` outside Tony's personal desktop setup.

The skill designs and documents musical instruments end-to-end: acoustic model,
parametric packet, BOM, sourcing, cut list, drawings, CNC setup plan, Wolfram
starter, deck, print packet, validation plan, and build-log site.

## 1. Get The Skill Folder

Use this folder as the skill package:

```text
instrument-maker/skills/v4/instrument-maker-v4/
```

It must contain `SKILL.md`, `manifest.yaml`, `references/`, `agents/`,
`scripts/`, and `assets/`.

## 2. Install Python Dependencies

From the skill folder or from a project repo:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install openpyxl python-pptx reportlab pypdf
```

On Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install openpyxl python-pptx reportlab pypdf
```

These packages enable `.xlsx`, `.pptx`, `.pdf`, and packet validation. If a
runtime cannot install them, the skill should still degrade to Markdown, CSV,
HTML, SVG, and OpenSCAD outputs.

## 3. Run From Codex CLI

Start in the target instrument repo, then launch Codex:

```bash
cd /path/to/your/instrument-repo
codex
```

In WSL, Windows paths are mounted under `/mnt/c`. For example:

```bash
cd /mnt/c/Users/Tony/Documents/GitHub/wooden-hang
codex
```

Prompt:

```text
Use the installed instrument-maker-v4 skill. Create a Mode A build packet for
this repo. Start from the files already here, mark uncertain dimensions as
assumptions, generate the packet docs/drawings/CNC/Wolfram/site, then run the
available validator and summarize remaining risks.
```

## 4. Run From Claude Desktop Or Cowork

Copy the folder into the skills location used by your Claude Desktop/Cowork
session, restart Claude, then check that `instrument-maker-v4` appears in the
available skills list.

Prompt:

```text
Use instrument-maker-v4 to design a small vessel flute in C5. Generate a build
packet, dimensioned SVG drawings, a CNC setup plan, a Wolfram starter, a
capstone deck, a printable packet, and a validation plan.
```

## 5. Smoke-Test The Scripts Directly

The scripts are plain Python and can be run without an agent.

Validate a root-mode packet:

```bash
python3 scripts/validate_packet.py /path/to/instrument-repo --mode root --strict
```

Validate either root-mode or nested `build/packet` layout and emit
machine-readable output:

```bash
python3 scripts/validate_packet.py /path/to/instrument-repo --mode auto --json
```

Generate capstone and print files:

```bash
python3 scripts/generate_capstone_docs.py /path/to/instrument-repo
```

For a post-reorg packet whose docs live in `build/packet` and drawings live in
`build/drawings`:

```bash
python3 scripts/generate_capstone_docs.py /path/to/repo/build/packet \
  --drawings-dir /path/to/repo/build/drawings \
  --images-dir /path/to/repo/assets/images
```

Generate a SolidWorks design table from readable family headers:

```bash
python3 scripts/generate_sw_design_table.py /path/to/instrument-repo --dry-run
```

Generate an OpenSCAD starter, letting the script detect the model:

```bash
python3 scripts/generate_openscad_starter.py /path/to/instrument-repo
```

If the detected model and requested model conflict, the script stops unless
you intentionally pass `--force-model`.

From the `instrument-maker` repo root, create a new root-mode scaffold:

```bash
python3 scripts/new_instrument_repo.py frame-drum \
  --repo-root /path/to/github \
  --display-name "Frame Drum" \
  --governing-model membrane \
  --manufacturing-path "bent or segmented shell"
```

Report which open build-packet issues are likely close-ready:

```bash
python3 scripts/report_close_ready.py \
  --repo-root /path/to/github \
  --github-repo tonykoop/instrument-maker
```

## 6. What Good Output Looks Like

A complete Mode A repo usually has:

```text
README.md
design.md
family-spec.csv
bom.csv
sourcing.csv
cut-list.csv
validation.csv
assembly-manual.md
supplier-rfq.md
drawing-brief.md
visual-bom-brief.md
risks.md
photo-shotlist.md
resources.md
jig-decision.md
wolfram-starter.wl
capstone-deck.md
capstone-deck.pptx
capstone-manifest.json
print-packet.md
print-packet.html
print-packet.pdf
cad/
cnc/
drawings/
images/
jigs/
site/
```

Some binary outputs are optional in constrained environments. The agent should
say which were skipped and why.

See `references/golden-examples.md` for public-safe examples of completed or
near-complete packet shapes.

## 7. Known Boundaries

- The skill emits manufacturable starting points, not final certified CAD.
- Supplier prices and availability are time-sensitive; verify before buying.
- AI-generated images are concept placeholders unless explicitly replaced with
  owned shop photos or measured CAD renders.
- Acoustic formulas are first-order until prototype measurements are recorded.
- The validator catches common packet regressions, not every possible physics
  or shop-safety problem.

## 8. Best First Test

Use a simple instrument repo with a clear governing model:

```text
Use instrument-maker-v4 to create a root-mode packet for a one-octave wooden
tongue drum in D minor pentatonic. Use derived estimates where measurements
are missing, generate drawings and a validation plan, then run the validator.
```

If that works, try a harder hybrid packet such as a ceramic-electric violin,
wooden handpan concept, or slip-cast open-pipe flute.
