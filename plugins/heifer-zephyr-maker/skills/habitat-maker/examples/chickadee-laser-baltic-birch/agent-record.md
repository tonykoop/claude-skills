# Agent Record — Canonical Chickadee Laser Packet

```yaml
packet: chickadee-laser-baltic-birch
skill: habitat-maker
skill_version: 0.2.0
created: 2026-05-10
provenance:
  origin: |
    Distilled from the Round 7 TwinGrid lane-alice blind run (Claude A) plus
    partner-peek synthesis with Codex B. The blind run produced a
    parametric chickadee birdhouse build packet; the partner peek added
    a generator-backed SVG, a JSON parameter file, an entrance guard, and
    cited NestWatch URLs.
  source_artifacts:
    - /tmp/twingrid-r7-claude-alice-laser-cut-chickadee-birdhouse/v2-generate.py
    - /tmp/twingrid-r7-claude-alice-laser-cut-chickadee-birdhouse/v2-chickadee-panels.svg
    - /tmp/twingrid-r7-claude-alice-laser-cut-chickadee-birdhouse/v2-geometry_params.json
    - /tmp/twingrid-r7-codex-alice-chickadee-birdhouse/geometry_params.json
species_data_source: Cornell Lab NestWatch (URLs in geometry_params.json → references[])
material_profile: primary  # 6 mm Baltic-birch; alternate cedar-lam noted in JSON

artifacts:
  hand_authored:
    - README.md
    - cut-list.md
    - BOM.md
    - validation-checklist.md
    - safety-notes.md
    - agent-record.md  # this file
  generated:
    - chickadee-panels.svg  # via scripts/generate_chickadee_packet.py
  source_of_truth:
    - geometry_params.json

regenerate_command: |
  python3 skills/habitat-maker/scripts/generate_chickadee_packet.py \
      --packet skills/habitat-maker/examples/chickadee-laser-baltic-birch

validation_run:
  - tool: jq -e .
    target: geometry_params.json
    result: pass
  - tool: python3 generate_chickadee_packet.py
    target: SVG generation
    result: pass
    detail: "wrote chickadee-panels.svg, ~10.8 KB"
  - tool: rsvg-convert
    target: chickadee-panels.svg → PNG
    result: pass
    detail: "renders to 2268 × 2873 PNG; 8 panels visible with cut + score layers"
  - tool: python3 -m unittest skills/habitat-maker/tests/test_habitat_maker.py
    target: smoke test
    result: pass

welfare_gates_satisfied:
  - G1 no_perch:           ENCODED in cut-list (no perch panel) and validation-checklist
  - G2 no_interior_finish: ENCODED in safety-notes and validation-checklist
  - G3 drainage:           ENCODED via 4 corner notches on P5 (geometry_params.json: drain_corner_notches_count=4)
  - G4 ventilation:        ENCODED via 3 vent slots per side on P3/P4 (vent_slots_per_side=3)
  - G5 fledgling_grip:     ENCODED via 5 score lines on P1 (fledgling_score_lines_count=5)
  - G6 predator_baffle:    ENCODED in BOM (predator baffle line item) and validation-checklist
  - G7 cleanout_access:    ENCODED via P4 cleanout door + 3 pilot holes

remaining_risks:
  - "Cavity volume (2.78 L) is borderline for NestWatch's chickadee comfort
     range. Acceptable but a future bump to 250 mm interior height puts it
     firmly inside the comfort window."
  - "Single-panel side-door pivot mechanism has no published field validation
     in this skill yet. First field season will tell."
  - "The cedar-lamination alternate material profile is described in
     geometry_params.json but not packaged as a parallel example folder.
     Future PR territory."
```
