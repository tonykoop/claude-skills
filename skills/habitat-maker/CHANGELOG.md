# habitat-maker — CHANGELOG

## Unreleased

- Added observation-camera mode contract with explicit enum values:
  `none`, `interior_view`, `exterior_approach`, and
  `interior_plus_exterior_approach`.
- Added `references/observation-camera-modes.md` with welfare gates for
  electronics isolation, heat, light, moisture, cable routing, service
  independence, and non-disturbance.
- Added `examples/chickadee-camera-observation-contract/` as a short
  machine-readable example for primary interior-view camera mode plus optional
  exterior approach camera mode.
- Added `scripts/validate_camera_modes.py` and tests for camera-mode contract
  validation and manifest expectations.
- Clarified that a four-chamber bat-house layout is suitable for a canonical
  skill-package example, but is not an implicit requirement for every
  `bat-houses` scaffold.
- Added a machine-readable observation-hive preflight gate contract that keeps
  public packets concept/preflight-only, requires all six observation-hive
  gate ids, preserves evidence fields, and routes live colony decisions out of
  `habitat-maker` content.
- Added smoke-test coverage for the observation-hive preflight contract.

## 0.4.0 — 2026-05-11

- Tightened bat-house welfare guidance for clear drop space, venting/moisture,
  no-mesh roost surfaces, discouraged tree mounts, climate/site records,
  mount type, seasonal disturbance windows, and service calendars.
- Added bat house, native bee house, observation-hive preflight, and
  camera/electronics welfare routing to `SKILL.md`.
- Added `references/bat-bee-observation-hive-welfare.md` with pass/fail gates
  for bat roosting surfaces, chamber spacing, heat, predator exclusion,
  native bee tunnel media, parasite/mold management, observation-hive
  containment, qualified review, and electronics caveats.
- Added a compact reusable gate record shape for future packet JSON,
  generated checklists, and `habitat-reference` imports.
- Moved `SKILL.md` version metadata to top-level frontmatter fields so
  `skills-meta` can read the canonical version and update date.
- Added smoke-test coverage for the new reference and routing strings.
- Added `references/welfare-gate-schema.md`, a shared pass/fail record shape
  for welfare gates and the future `habitat-reference` import workflow.
- Updated `SKILL.md` and the chickadee validation checklist to route reusable
  welfare gates through the shared schema without changing fabrication
  geometry.
- Added concrete starter gate families for bat houses, native bee houses,
  observation-hive preflight, and camera/electronics welfare review.
- Added smoke-test coverage for the shared welfare-gate schema reference.

## 0.3.0 — 2026-05-10

- Added bird-bath and balcony/renter support to `SKILL.md`, including
  maintenance-first welfare gates and deployment requirements.
- Added `references/bird-bath-balcony.md` with shallow-depth, textured
  footing, escape, dump/scrub, mosquito, material-safety, heat/evaporation,
  stability, no-drill, drip, window-strike, and travel-dry checks.
- Added a bird-bath material safety matrix and optional fill-depth gauge
  template for compact balcony packets.
- Added smoke-test coverage for the new bird-bath reference and skill routing.
- Added `examples/temperate-na-four-chamber-bat-house/`: a canonical
  builder-facing bat-house packet with `geometry_params.json`, human shop
  packet docs, climate/site presets, mounting worksheet, bat-specific welfare
  gates, validation-report schema, and example validation report.
- Added `scripts/generate_bat_house_packet.py`: reads the bat-house parameter
  file and emits `four-chamber-bat-house-layout.svg` plus
  `generated-cut-list.csv` deterministically.
- SKILL.md: documented bat-house-specific gates for four chambers, roost gap,
  roughened landing, venting, clear drop space, no mesh, no interior finish,
  no treated interior lumber, tree-mount discouragement, and maintenance
  timing.
- Extended smoke tests to cover the bat-house packet, generator, generated SVG
  groups, validation-report JSON shape, and required packet files.
- Provenance: distilled from the Round 9 TwinGrid Frank blind run,
  Partner Peek pass, and issue `tonykoop/claude-skills#102`.


## 0.2.0 — 2026-05-10

- First working canonical example landed: `examples/chickadee-laser-baltic-birch/`.
  Generator-backed laser-cut chickadee birdhouse, mirroring
  `instrument-maker-v4` packet conventions.
- Added `scripts/generate_chickadee_packet.py`: reads
  `examples/chickadee-laser-baltic-birch/geometry_params.json` and emits
  `chickadee-panels.svg` deterministically. Re-run to refresh.
- SKILL.md: declared the v0.2 build-packet contract (single source-of-truth
  parameter file, generator-backed artifacts for laser/CNC, welfare-integrated
  validation gates, cut list, BOM, safety notes, agent record).
- SKILL.md: instructed agents to prefer generator-backed artifacts over
  hand-edited SVGs whenever the build method is laser, CNC, or plotter-cut
  vinyl.
- Added smoke test `tests/test_habitat_maker.py` for generator + welfare
  checks.
- Provenance: distilled from the Round 7 TwinGrid lane-alice blind run
  + partner-peek pass. See PR description for source artifacts.

## 0.1.0 — 2026-05-09

- Initial scaffold (placeholder skill, no implementation).
