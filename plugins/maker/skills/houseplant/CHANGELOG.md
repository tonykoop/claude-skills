# Changelog — houseplant

## v0.3.0 — 2026-06-13 (Chrono-horticultural calendar engine)

Lays the v2 houseplant foundation by adding the chrono-horticultural calendar engine. This shifts care routines from fixed timers to dynamic, observation-driven checks and auto-schedules wire-removal windows.

### Added

- `references/chrono-engine.md` — Core workflow for dynamic care windows and the V2 data-model schema extensions.
- `scripts/wire_window.py` — Computes recommended wire-inspection cadence based on species growth rate and date applied.
- Updated `SKILL.md` to route watering/fertilizing/wire-removal-schedule questions to the chrono-engine reference.

## v0.2.0 — 2026-05-17 (Blender MCP integration + bundled scripts)

First skill-creator iteration on top of Codex's initial draft. Focus: pruning + wire-coil-training workflow with real Blender MCP integration. Tested against three eval prompts grounded in the maintainer's Ficus benjamina specimen (lazy-susan capture, structural prune planning, sim-before-cutting).

### Added

- `references/capture-pipeline.md` — the four phone-capture modes (multi-angle photos with ruler, photogrammetry mesh, orbit video, lazy-susan stabilized video), required captures per mode, ruler-based scale-calibration workflow, ffmpeg frames helper, and an output contract for capture sessions.
- `scripts/scene_scaffold.py` — idempotently builds the `Plant_<plant_id>/` collection hierarchy (`00_source_scan/` through `99_exports/`) and stamps custom properties for cross-session recovery.
- `scripts/scale_from_ruler.py` — computes a uniform scale factor from two ruler endpoints in the imported scan and a known real distance, then applies it to a target collection.
- `scripts/wire_coil.py` — generates a helical wire-coil curve wrapped around a branch curve with metadata stamped for cross-session recovery (gauge, turns per meter, applied date).
- `scripts/cut_marker.py` — places a colored marker at a coordinate using the skill's color semantics (red cut, amber watch, blue wire, green preserve, pink bud, teal aerial root).
- `scripts/sim_collection.py` — clones the current-state twin into a dated `sim_<scenario>_<date>` collection under `05_simulations/`, leaving the canonical twin untouched.
- `assets/ficus-benjamina-starter.md` — starter plant profile for the maintainer's ficus with aerial-root nebari notes, fast-cambium wire-window guidance, and Ficus-specific care defaults.
- SKILL.md now lists every bundled script and `mcp__Blender__*` tool with usage order (orient → plan → execute → verify).
- Pushier description so the skill triggers reliably when users say things like "prune my plant" or "model my bonsai" without naming the skill.
- Per-skill `manifest.yaml` for structured discoverability (triggers, references with `load_when`, scripts with inputs/outputs/dry_run flags).
- `tests/` directory with smoke tests against the bundled scripts (script files parse, helper functions exist, scale-factor math is correct).
- This `CHANGELOG.md` and a `README.md` with folder layout and install notes.

### Changed

- `references/blender-digital-twin.md` — added the orient → plan → execute → verify rhythm, four concrete `bpy` patterns the model can adapt (scaffold, cut marker, wire helix, simulation collection), and a hybrid reconstruction recipe for `.obj`/`.ply`/`.glb` → editable twin.
- `references/bonsai-module.md` — added a pointer to the Ficus benjamina starter profile.
- SKILL.md core workflow rewritten with a capture-intake route in addition to the existing three.

### Deferred to GitHub issues

The original BonsaiBot brainstorm had six more modules. Filed as `houseplant` + `deferred-from-v1`:

- #172 chrono-horticultural calendar engine
- #173 bud/bloom chrono-tracker
- #174 aerial-root and nebari guidance tracker
- #175 computer-vision plant health diagnostics
- #176 virtual grafting sandbox
- #177 propagation tracker

### Iteration-1 benchmark

Workspace: `skills/houseplant-workspace/iteration-1/`

| Metric | Codex draft (old_skill) | v0.2.0 (with_skill) | Delta |
|---|---|---|---|
| Pass rate | 97% (24/25 assertions) | 94% (24/25 assertions) | -3% |
| Time | 127.1 s ± 73.6 s | 113.1 s ± 47.8 s | -14 s |
| Tokens | 44,115 ± 6,620 | 52,895 ± 10,931 | +8,780 |

The pass-rate delta is within run-to-run noise at n=1 per config per eval. Qualitatively the v0.2.0 outputs are substantially more concrete (the bundled scripts let the model produce parameterized, decisive plans instead of inline pseudo-code), which the human review flagged as significantly improved.

## v0.1.0 — 2026-05-17 (Codex initial draft)

First draft authored by Codex from the BonsaiBot brainstorm. Established the progressive-disclosure skeleton: `SKILL.md` orchestrator routing to `references/blender-digital-twin.md`, `references/bonsai-module.md`, and `references/collection-records-and-care.md`.

### Added

- `SKILL.md` with core workflow, scene contract, output contracts, decision rules, risk levels, and skill boundaries.
- `references/blender-digital-twin.md` — scene contract (`Plant_<plant_id>/` hierarchy), object naming conventions, digital-twin update steps, pruning and wiring simulation outlines.
- `references/bonsai-module.md` — bonsai intake, styling priorities, risk levels, pruning plan format, wiring and bending guidance, aerial-roots/nebari and bud/bloom tracking outlines.
- `references/collection-records-and-care.md` — source-of-truth conventions, minimal plant record schema, event log types, care scheduling principles, calendar-ready reminder format.
- `agents/openai.yaml` interface metadata.
