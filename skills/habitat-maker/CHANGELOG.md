# habitat-maker — CHANGELOG

## 0.3.0 — 2026-05-10

- Added bird-bath and balcony/renter support to `SKILL.md`, including
  maintenance-first welfare gates and deployment requirements.
- Added `references/bird-bath-balcony.md` with shallow-depth, textured
  footing, escape, dump/scrub, mosquito, material-safety, heat/evaporation,
  stability, no-drill, drip, window-strike, and travel-dry checks.
- Added a bird-bath material safety matrix and optional fill-depth gauge
  template for compact balcony packets.
- Added smoke-test coverage for the new bird-bath reference and skill routing.

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
