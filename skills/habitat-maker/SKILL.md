---
name: habitat-maker
version: 0.2.0
last-updated: 2026-05-10
description: >-
  Design wildlife habitat and garden infrastructure: birdhouses, bat houses,
  bee houses, bird baths, bird feeders, planters, pollinator habitat, garden
  signage, and plant supports. Use for species-specific habitat build packets,
  parametric laser/CNC/manual fabrication artifacts, welfare validation gates,
  and maker-friendly assembly documents.
---

# Habitat Maker

Use this skill when the user asks to design, document, or validate a habitat
or garden-support build: nest boxes, bat houses, solitary bee houses, bird
baths, feeders, pollinator structures, planters, trellises, moss poles, or
repurposed found cavities.

## Default Behavior

Start from the species or habitat welfare requirements, then choose a
fabrication method. A good packet is not merely buildable; it must be safe,
maintainable, and appropriate for the target organism.

For laser/CNC habitat packets, prefer generator-backed artifacts:

1. Define one parameter source for species constraints, material profile,
   finished dimensions, panel geometry, welfare checks, and validation tests.
2. Generate machine-readable geometry from that source instead of hand-copying
   numbers into SVG/DXF prose.
3. Ship both human-facing packet files and machine-facing artifacts:
   `geometry_params.json`, `panels.svg`, BOM, cut list, safety/welfare
   checklist, and an agent record.
4. Validate generated vectors when tooling is available. Use `jq` for JSON,
   Python/XML parsing for SVG syntax, and `rsvg-convert` or Inkscape for
   render checks.

## Owns

- Species-specific birdhouse, bat house, bee house, bath, feeder, planter,
  pollinator habitat, garden signage, and plant-support designs.
- Habitat build packets with BOMs, cut lists, geometry, assembly, mounting,
  maintenance, safety notes, and validation checklists.
- Laser/CNC/manual method profiles when the welfare constraints still drive
  the design.
- Public maker packets that are friendly to parent/grandparent plus child
  builds while keeping wildlife safety explicit.

## Boundaries

- Do not make beekeeping welfare decisions for observation-hive work without a
  dedicated bee-care source.
- Do not take over shop jig/workholding planning when the problem is primarily
  machine setup; route to `makerspace`.
- Do not take over instrument acoustics; route instruments to
  `instrument-maker` or `maker-engineering`.
- Do not treat decorative appearance as a substitute for habitat suitability.

## Load References On Demand

- `references/examples/chickadee-laser-birdhouse/`
  Canonical generator-backed laser nest-box packet. Load this when asked for
  birdhouses, generator-backed habitat packets, or laser/CNC geometry patterns.

## Canonical Generator Pattern

The chickadee example uses:

- `design_params.json` as the single parameter source.
- `scripts/generate_chickadee_laser_packet.py` to emit:
  - `geometry_params.json`
  - `panels.svg`

Run it from the repo root:

```bash
python3 skills/habitat-maker/scripts/generate_chickadee_laser_packet.py \
  --input skills/habitat-maker/references/examples/chickadee-laser-birdhouse/design_params.json \
  --outdir /tmp/habitat-maker-chickadee-check
```

Use this pattern for future laser/CNC habitat examples: first encode the
species gates, then derive geometry and validation artifacts from the same
source.
