# Sheet Metal Round 1 Eval

Date: 2026-05-18
Skill path: `skills/sheet-metal`
Version: `0.1.0`

## Scope

Initial cross-platform skill creation from the captured brainstorming session
at `Second_Brain/Clippings/brainstorming sheet metal skill.md`, with shape
borrowed from the local maker skill family under `claude-skills/skills`.

## Structural Validation

Run after edits:

```bash
python3 /mnt/c/Users/Tony/.codex/skills/.system/skill-creator/scripts/quick_validate.py /mnt/c/Users/Tony/Documents/GitHub/claude-skills/skills/sheet-metal
```

Observed result:

```text
Skill is valid!
```

## Script Smoke Tests

Run after edits:

```bash
python3 scripts/sheet_metal_math.py bend-allowance --angle-deg 90 --radius 0.06 --thickness 0.06 --k-factor 0.44
python3 scripts/sheet_metal_math.py cylinder-blank --diameter 6 --height 12 --trim-margin 1.5
python3 scripts/sheet_metal_math.py weight --material aluminum --area 120 --thickness 0.063
python3 scripts/sheet_metal_math.py combat-budget --class beetleweight
```

Observed result: all commands exited 0 and printed deterministic planning
estimates:

- 90 degree bend allowance at R=0.060, T=0.060, K=0.44: `0.135717`
- 6 inch diameter cylinder with 1.5 inch trim per end: `21.849556` inch
  developed width
- 120 in2 of 0.063 inch aluminum: `0.74088` lb / `336.057515` g
- beetleweight budget: `3.0 lb / 1360 g` total, `300 to 400 g` target chassis

## Prompt Benchmarks

### 1. Modular Toolbox

Prompt:

```text
Use sheet-metal to design a 20 x 10 x 8 inch modular toolbox for bike spares:
rim tape, tubes, grease, small lights, brushes, and stems. I want drop-in trays
and a clamshell lid.
```

Pass criteria:

- Uses the modular toolbox platform and storage archetypes.
- Names provisional material/thickness assumptions.
- Produces parameters, SolidWorks feature plan, tray architecture, safe rim/hem
  plan, bend order, DXF checks, and missing measurements.

### 2. Horn Segment

Prompt:

```text
Use sheet-metal to plan the flat pattern and shop workflow for a rolled brass
bugle bell segment. I care about SolidWorks Lofted Bend and avoiding a lumpy
seam.
```

Pass criteria:

- Routes acoustic design to `instrument-maker`.
- Covers lofted bend, seam marks, rolling, annealing, joining, planishing, and
  station validation.

### 3. Beetleweight Chassis

Prompt:

```text
Use sheet-metal for a 3 lb beetleweight wedge chassis with folded aluminum
armor, guarded wheels, and fast service access.
```

Pass criteria:

- Uses combat robotics and micro-budget guidance.
- Includes weight budget, material/bend warning, sloped armor, wheel guards,
  service fastening, and electronics shock isolation.

### 4. Electronics Enclosure

Prompt:

```text
Use sheet-metal to design a Mini-ITX cyberdeck enclosure with ventilation,
grounding, and plasma-cut panels.
```

Pass criteria:

- Requires exact component models before fabrication-ready hole patterns.
- Includes ventilation web width, grounding, service access, cable edge
  protection, and DXF layer discipline.

### 5. Vehicle Rack Safety Boundary

Prompt:

```text
Use sheet-metal to plan a flat roof rack for a 2024 Toyota RAV4 Prime so I can
carry a ShiftPod and lumber.
```

Pass criteria:

- Treats the project as safety-sensitive.
- Routes final safety gate to `maker-engineering`.
- Gives provisional sheet metal geometry guidance without claiming road-ready
  certification.

### 6. Stacked Wood-Metal Art

Prompt:

```text
Use sheet-metal to make a Gabriel Schama-inspired stacked wood and brass wall
piece with registration pins.
```

Pass criteria:

- Keeps vector and material safety partnership with `laser-art`.
- Includes registration holes, layer offsets, material stack, authority ladder,
  and test-coupon guidance.

## Residual Risks

- Shop tool limits came from a brainstorming transcript and must be verified
  before fabrication.
- SolidWorks API macros are not included in v0.1.0; this skill provides
  workflow and DFM guidance plus helper math.
- Vehicle, overhead, animal-facing, and combat robot work needs real safety
  validation before use.
