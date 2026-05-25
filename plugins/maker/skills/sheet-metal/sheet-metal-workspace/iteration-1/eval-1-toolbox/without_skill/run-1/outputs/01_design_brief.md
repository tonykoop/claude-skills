# Stackable Modular Toolbox System - Design Brief

## Project Overview
Parametric, top-down SolidWorks assembly for a stackable sheet metal toolbox system with a companion dolly capable of transporting 3-4 boxes simultaneously. Inspired by modular toolbox systems (Milwaukee Packout, DeWalt ToughSystem, Festool Systainer).

## First Size (Reference Configuration)
- **Width (W):** 20 in (508 mm)
- **Height (H):** 8 in (203 mm)
- **Depth (D):** 10 in (254 mm)
- **Material:** 18 gauge (0.048 in / 1.2 mm) cold-rolled steel sheet
- **Estimated empty weight:** ~12-15 lb per box
- **Target payload:** 50 lb per box

## Design Goals
1. **Top-down parametric control** - One master sketch / global variables drive the entire assembly. Change `BoxWidth`, `BoxHeight`, `BoxDepth`, and all child parts/features rebuild correctly.
2. **Stackability** - Positive male/female interlock between top of one box and bottom of the next. Boxes must auto-align when stacked.
3. **Family of sizes** - Support a family table (Small / Medium / Large; full / half / quarter height) all sharing the same parametric backbone.
4. **Dolly compatibility** - Dolly base accepts stack of 3-4 boxes, has casters, and integrates with the same interlock pattern so the bottom box locks to the dolly.
5. **Sheet-metal manufacturable** - All parts must produce valid flat patterns (uniform thickness, K-factor controlled, no impossible geometry).
6. **Stamp/laser/brake friendly** - Bends are 90 degree where possible; minimum flange lengths respected; hole-to-bend distances respected.

## Non-Goals (v1)
- Drawer slides, lid latches beyond simple draw latches, soft-close mechanisms.
- IP-rated weather sealing (gaskets are a v2 add-on).
- Powered/tracked tool integration.

## Constraints
- Single material thickness throughout (simpler BOM, single coil stock).
- All exterior corners rounded for safety (min 0.125 in / 3 mm radius).
- Mass-produceable on a 4 ft x 8 ft laser/punch and an 8 ft press brake.
- Caster bolt pattern standard 3 in x 3 in square (4-hole) for off-the-shelf 3 in casters.

## Deliverables in This Package
- `01_design_brief.md` - this file
- `02_global_variables.txt` - SolidWorks Equations / Global Variables list
- `03_parameters_family_table.csv` - design table / family of sizes
- `04_assembly_structure.md` - top-down assembly tree and feature plan
- `05_sheet_metal_parameters.md` - thickness, K-factor, bend radius, relief
- `06_interlock_design.md` - stacking interlock geometry and engagement
- `07_dolly_design.md` - dolly part and assembly
- `08_modeling_plan.md` - step-by-step build sequence in SolidWorks
- `09_drawing_list.md` - drawing package required for fabrication
- `10_bom.csv` - bill of materials (purchased + fabricated)
- `11_validation_checklist.md` - design and manufacturability review checklist
- `12_naming_conventions.md` - file/feature naming for the project
