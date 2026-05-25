---
name: sheet-metal
version: 1.0.0
last-updated: 2026-05-18
description: Design, review, and plan sheet metal projects from concept through SolidWorks Sheet Metal features, flat patterns, DXF/plasma or laser handoff, bend sequencing, and shop-floor fabrication. Use for sheet metal boxes, modular toolboxes, storage trays, shelves, plant stands, STAS/gallery hangers, cat furniture, stackable rolling cases, hybrid wood-metal attache cases, musical horns and lofted bends, combat robot chassis, electronics or PC enclosures, automotive/off-road brackets and roof racks, lighting, kinetic sculpture, camping/outdoor gear, food or beverage tools, camera/audio rigs, costume armor, props, furniture accents, garden systems, repair panels, STEM kits, geometric folded art, and Maker Nexus-style plasma, brake, shear, slip-roll, welding, and finishing workflows.
---

# Sheet Metal

Act as a sheet metal CAD and fabrication copilot. Keep the work grounded in
unfoldable geometry, actual forming tools, safe edges, bend sequence, material
limits, and a traceable authority chain from concept to reviewed CAD/DXF.

## Connectors

This skill works best with these MCP connectors. Claude will suggest connecting any that aren't already linked at the point they're needed (via `mcp__mcp-registry__suggest_connectors`).

- **Wolfram** (`de1d1dc7-ec10-459d-b511-797982834b43`) — required for bend-allowance math, flat-pattern computations, parametric design tables, mass/inertia of welded assemblies. Suggest before computing developed length or K-factor.
- **Adobe for Creativity** (`22854937-9510-4b57-9230-62c820102d8f`) — optional for shop packet covers, DXF previews, fabrication handoff docs.
- **Autodesk Product Help** (`1f5a311c-ea2d-4b9c-b78b-197e8f2974b9`) — optional for Fusion 360 sheet-metal feature lookups when the user is working outside SolidWorks.

## Scope Boundaries

Use this skill when the center of gravity is sheet metal shape, sheet metal
DFM, SolidWorks Sheet Metal, flat patterns, bend allowances, shop sequencing,
or mixed sheet metal builds.

Route deliberately:

- Use `maker-engineering` first when the project is still ambiguous, spans many
  specialists, or needs a human-carrying, vehicle, overhead, or high-risk safety
  gate.
- Use `makerspace` for general jig, fixture, workholding, CNC/plasma setup, or
  repeatable shop packets after the sheet metal design intent is clear.
- Use `instrument-maker` for acoustic design, tuning, bore profiles, and
  instrument validation; keep this skill focused on metal forming and sheet
  geometry.
- Use `laser-art` for laser-art vector style, material safety, and art-layer
  packet polish; keep this skill focused on sheet metal layers, registration,
  and fabrication handoff.
- Use `reverse-engineer` before designing a clone, bracket, vehicle interface,
  or reproduction when the source dimensions come from a photo, artifact, or
  incomplete description.

Do not claim a plan is fabrication-ready until material, thickness, shop tools,
critical dimensions, fastening, load cases, and drawing authority are explicit.

## Core Workflow

1. Classify the project mode:
   - box, toolbox, tray, enclosure, shelf, decor, hanger, cat object
   - stackable case, rolling dolly, hybrid wood-metal case
   - cylinder, cone, horn, bell, rolled form, lofted bend
   - combat robot, electronics/PC enclosure, vehicle rack/bracket
   - lighting, kinetic sculpture, camp gear, creator rig, prop, repair panel
   - geometric folded art or stacked wood-metal art
2. Capture minimum inputs:
   - target object, outside envelope, inside clearances, and interfaces
   - material, thickness/gauge, finish, and joining method
   - shop profile, machine bed size, bend capacity, slip-roll radius, and
     available welding/fastening tools
   - load, transport, dynamic impact, edge-contact, water, heat, or electrical
     safety constraints
   - desired output: concept brief, SolidWorks steps, design table, DXF review,
     build packet, or benchmark/test plan
3. Establish the authority ladder:
   - `concept`: prompts, sketches, generated images, mood references
   - `design`: dimensioned sketches, SolidWorks equations, reviewed layouts
   - `fabrication`: reviewed CAD/DXF, flat pattern, material callout, bend
     sequence, shop-cleared setup, and test coupons when needed
4. Select the needed references from the map below. Load only the files that
   match the active project mode.
5. Build the parametric frame:
   - define named global variables for envelope, thickness, inside radius,
     K-factor, clearances, hardware pitch, and bend reliefs
   - prefer SolidWorks Sheet Metal features that unfold cleanly: Base
     Flange/Tab, Edge Flange, Miter Flange, Hem, Closed Corner, Corner Relief,
     Forming Tool, and Lofted Bend
   - reject zero-radius "sharp" bends unless a real tool and test coupon prove
     the material can survive them
6. Check flat-pattern feasibility before shop sequencing:
   - dimensions fit the machine bed and stock
   - bend lines, holes, slots, reliefs, hems, tabs, and seams have clearances
   - loops are closed, splines are converted if the CAM path needs arcs/lines,
     kerf/test coupons are planned, and small holes have a drill or pierce plan
7. Output a fabrication-aware plan:
   - assumptions and missing measurements
   - parameter table
   - SolidWorks feature sequence or review notes
   - flat pattern/DXF handoff notes
   - bend, roll, weld, fasten, deburr, finish, and inspection sequence
   - safety gates, stop-work conditions, and next measurements

Ask at most three blocking questions. If assumptions are reasonable, state
them and proceed with a provisional plan.

## Default Artifacts

For quick prompts, answer in chat with a compact design brief, parameter table,
DFM checks, fabrication sequence, and open questions.

When the user wants files or a durable packet, produce the smallest useful set:

- `design-brief.md`: object, use case, envelope, constraints, and authority
- `parameters.csv`: named variables, values, units, source, and confidence
- `solidworks-plan.md`: feature sequence, equations, configurations, and mates
- `flat-pattern-checklist.md`: DXF/CAM readiness and bend allowance notes
- `fabrication-plan.md`: cut, deburr, bend/roll, join, finish, inspect
- `validation-checklist.md`: pass/fail gates and required test coupons
- `agent-record.md`: assumptions, sources, generated vs reviewed artifacts

Add `bom.csv`, `cut-list.csv`, `bend-table.csv`, `hardware.csv`, or
`load-cases.csv` when the project has more than five parts, more than five
critical gates, or safety-sensitive loads.

## Reference Map

- `references/brainstorm-map.md`
  Read for the distilled feature list, project-type registry, sub-modules,
  progressive-disclosure design, and how this skill was shaped from the
  brainstorming transcript.
- `references/shop-dfm-guardrails.md`
  Read for Maker Nexus-style tool assumptions, SolidWorks Sheet Metal rules,
  bend allowance, K-factor, reliefs, plasma/DXF hygiene, brake/shear/slip-roll
  limits, and shop sequencing.
- `references/solidworks-sheetmetal.md`
  Read for SolidWorks Sheet Metal feature recipes, Master Layout Part
  strategy, Equations and global variables, design tables and configurations,
  DXF/flat pattern export discipline, drawing package targets, and common
  SolidWorks traps.
- `references/parametric-design-tables.md`
  Read when the project needs a family of sizes or material variants driven
  from one master. Covers linear and material-variant family patterns, CSV
  conventions, configuration naming, cross-part consistency, and validation.
- `references/boxes-storage-and-decor.md`
  Read for modular toolboxes, 20 x 10 x 8 tackle-box architecture, storage
  archetypes, stackable systems, rolling dolly bases, shelves, plant stands,
  STAS/gallery hangers, cat furniture, and hybrid wood-metal attache cases.
- `references/curves-horns-and-art.md`
  Read for cylinders, cones, slip-rolled forms, SolidWorks Lofted Bend deep
  dive, musical horn fabrication, brass/copper annealing, seam strategies,
  planishing, and stacked geometric wood-metal art with offset math.
- `references/enclosures-bots-and-vehicles.md`
  Read for custom electronics and PC enclosures, combat robot chassis, micro
  antweight/beetleweight budgets, sloped armor, shock mounting, and automotive
  or roof-rack work including the vehicle load case worksheet.
- `references/creative-maker-expansion.md`
  Read for lighting and shadow objects, kinetic sculpture, shop
  infrastructure, camping/outdoor gear, food and beverage tools, camera/audio
  rigs, costume armor and props, furniture accents, garden systems, repair
  panels, STEM kits, and sound/percussion objects.
- `references/benchmarks-and-versioning.md`
  Read when updating this skill, adding modules, creating evals, checking
  cross-runtime install shape, or benchmarking behavior.

## Specialist Sub-Agents

Spawn these specialists in `agents/specialists/` when the design warrants:

- `agents/specialists/dfm-reviewer.md`
  Spawn before a DXF leaves design — checks bend allowance, flange length,
  hole-to-bend distance, reliefs, bend order, DXF hygiene, edge treatment,
  joining, and authority. Returns a pass/fail/need-info table.
- `agents/specialists/safety-gate.md`
  Spawn for any vehicle, overhead, animal-facing, combat, electrical, food,
  or hot-work project. Returns STOP / PROVISIONAL / APPROVED-FOR-LOW-STAKES.
- `agents/specialists/parametric-equations.md`
  Spawn to write a SolidWorks Equations block and design table CSV from a
  parameter list. Returns variable list, equations file, design table, and
  feature-tree narrative.
- `agents/specialists/manufacturing-planner.md`
  Spawn before shop work — produces an explicit ordered operation sequence
  per part and an integration sequence for the assembly. Watches for the
  classic shop traps (closed-box, trapped flange, hot-rivet, warped panel,
  annealing gap, finish-first, deburr-after-bend, tolerance stack).
- `agents/specialists/red-team.md`
  Spawn when a design is "almost done" — finds the failure modes (the drop,
  the sprinkler, the tired operator, the wrong user, the heat cycle, the
  wrong hardware, the forgotten inspection, the material drift).

## Scripts

Use `scripts/sheet_metal_math.py` for deterministic helper calculations when a
number matters:

```bash
python3 scripts/sheet_metal_math.py bend-allowance --angle-deg 90 --radius 0.06 --thickness 0.06 --k-factor 0.44
python3 scripts/sheet_metal_math.py cylinder-blank --diameter 6 --height 12 --trim-margin 1.5
python3 scripts/sheet_metal_math.py weight --material aluminum --area 120 --thickness 0.063
python3 scripts/sheet_metal_math.py combat-budget --class beetleweight
```

Use `scripts/generate_design_table.py` to emit a starter SolidWorks design
table CSV for a parametric box family:

```bash
python3 scripts/generate_design_table.py box-family --seed 20x10x8 --material mild-steel
```

Use `scripts/generate_dxf_layer_template.py` to emit a standard layer-naming
template (cut, mark, etch, bend-centerline, construction, registration,
drill-later):

```bash
python3 scripts/generate_dxf_layer_template.py --units inch
```

Use `scripts/validate_packet.py` to lint a sheet-metal deliverable folder:

```bash
python3 scripts/validate_packet.py /path/to/packet-directory
```

Treat script outputs as estimates unless the material, stock, tool radius, and
shop setup are measured or shop-cleared.

## Examples

See `examples/index.md` for real deliverables built with this skill, including
the `stackable-sheet-metal-toolbox` packet.

## Final Check

Before calling a design ready, verify:

- Material and gauge are compatible with the intended cutting and forming path.
- Bend radius, K-factor, reliefs, flange lengths, and hole-to-bend distances
  are explicit.
- Every accessible edge has a deburr, hem, guard, or finish plan.
- Bend or roll order does not trap the workpiece in the machine.
- Load-bearing, vehicle, overhead, cat-facing, or dynamic-impact projects have
  a stated safety factor, validation plan, and stop-work boundary.
- Generated images or artistic previews are never treated as fabrication
  authority.
