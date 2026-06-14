# Changelog

All notable changes to the `sheet-metal` skill are documented here. The format
follows Keep a Changelog and the version numbers follow Semantic Versioning.

## [1.0.0] - 2026-05-18

First complete release. Brings the skill to parity with `instrument-maker`,
`makerspace`, and other peer skills in this repo.

### Added

- `CHANGELOG.md` (this file).
- `agents/specialists/` with five sub-agent briefs:
  - `dfm-reviewer.md`: catches sheet metal DFM violations before fabrication.
  - `safety-gate.md`: gates vehicle, overhead, animal-facing, combat, electrical,
    food-contact, and hot-work projects.
  - `parametric-equations.md`: writes SolidWorks equations, design tables, and
    family-of-sizes scaffolding.
  - `manufacturing-planner.md`: orders cut, deburr, bend, roll, weld, fasten,
    and finish steps and flags machine clearance traps.
  - `red-team.md`: stress-tests a design for what will actually go wrong.
- `examples/` directory with an index pointing at real deliverables built with
  this skill (currently the stackable-sheet-metal-toolbox).
- `references/solidworks-sheetmetal.md`: dedicated reference for SolidWorks
  Sheet Metal feature recipes, Master Layout Part strategy, equations, design
  tables, configurations, and DXF export discipline.
- `references/parametric-design-tables.md`: patterns for driving a family of
  sizes from one master, including the toolbox/dolly family and horn segment
  family seeded in this skill.
- `evals/evals.json`: machine-readable benchmark file used by the iteration
  loop; covers toolbox, horn, beetleweight, electronics, vehicle rack, and
  stacked art prompts.
- `scripts/generate_design_table.py`: emits a SolidWorks-compatible design
  table CSV for the seed parametric box family.
- `scripts/generate_dxf_layer_template.py`: emits standard layer naming for
  plasma/laser DXF handoff (cut, mark, etch, bend-centerline, construction,
  registration).
- `scripts/validate_packet.py`: lints a sheet-metal deliverable folder for the
  expected default artifacts and CSV column shapes.

### Changed

- Expanded `references/curves-horns-and-art.md` with deeper lofted bend math,
  slip-roll feed mechanics, segmented horn fabrication, planishing details, and
  Schama-style stacked-layer offset math.
- Hardened `references/enclosures-bots-and-vehicles.md` vehicle-rack section
  with explicit non-certification language and a per-load-case worksheet.
- Tightened `SKILL.md` reference map and added pointers to the new references,
  specialists, and scripts.
- Bumped `manifest.yaml` to `1.0.0` and added `examples/` and `CHANGELOG.md`
  to the artifacts list.

### Notes

- v1.0.0 is not "ship-to-production for safety-critical work"; it is "this
  skill now has the full shape of a peer skill in this repo and is ready for
  serious use, with the same boundaries the rest of the family enforces."

## [0.2.0] - 2026-05-18

### Added

- `references/creative-maker-expansion.md` covering lighting, kinetic
  sculpture, shop infrastructure, camping, food/beverage, creator rigs,
  costume, furniture, garden, repair, STEM, and percussion modules.
- `evals/round-2-creative-expansion.md` with benchmark prompts for the new
  modules.

### Changed

- Updated `SKILL.md` to include the creative-maker-expansion reference and
  expanded the triggering description so the skill is recognized for the new
  domains.

## [0.1.0] - 2026-05-18

### Added

- First coherent cross-platform sheet metal skill.
- `SKILL.md` with scope boundaries, workflow, default artifacts, reference
  map, and final checks.
- `references/brainstorm-map.md`, `references/shop-dfm-guardrails.md`,
  `references/boxes-storage-and-decor.md`, `references/curves-horns-and-art.md`,
  `references/enclosures-bots-and-vehicles.md`, and
  `references/benchmarks-and-versioning.md`.
- `scripts/sheet_metal_math.py` with bend-allowance, cylinder-blank, weight,
  and combat-budget subcommands.
- `agents/openai.yaml` Codex display metadata.
- `manifest.yaml` at version `0.1.0`.
- `evals/round-1-eval.md` with initial benchmark prompts.
