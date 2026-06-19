# Changelog — houseplant

## v0.4.0 — 2026-06-19 (health-triage engine — #175)

Completes the CV plant-health "check-engine light" (#175), which shipped in
v0.3.0 as a reference doc only. The vision pass (the multimodal agent naming
symptoms from photos) now has a deterministic triage layer behind it.

### Added

- **`scripts/health_triage.py`** — pure-Python (no Blender). Maps observed
  symptoms to candidate flags, cross-references recent care events (a repot
  within ~14 days re-reads a sudden drop as transplant stress; a recent feed
  re-reads margin burn as fertilizer/salt), renders the `health_flag_added`
  event records with evidence + explicit confidence, and computes the
  structural-work risk escalation — any open **pest/rot** flag forces
  pruning/wiring/root work to **High** risk (per `bonsai-module.md`). Enforces
  the reference's posture: screen-not-diagnose, inspection-first, **never** a
  chemical recommendation; pest/rot candidates default to low confidence.
- **`tests/test_health_triage.py`** — 12 cases (symptom mapping, unknown-symptom
  surfacing, care cross-reference incl. the 14-day window, risk escalation,
  no-chemicals posture, rendering).

### Changed

- `references/health-diagnostics.md` and `SKILL.md` health routing now point the
  output step at `health_triage.py`.

## v0.3.0 — 2026-06-15 (v2 feature set — epic #209)

Implements the six modules deferred from v1 (the original BonsaiBot brainstorm), extending the existing skill in place. All new work shares the Blender MCP + Obsidian/Markdown plant-database context; the simulate-before-you-cut philosophy and the color semantics (red/amber/blue/green/pink/teal) carry through unchanged.

### Added — references

- `references/chrono-engine.md` (#172) — chrono-horticultural engine: turns species growth-speed class + season + indoor/outdoor + recent stressors into observation-driven **checks** rather than fixed timers, and computes **wire-removal inspection windows** scaled to species cambium-thickening rate. Pairs with `collection-records-and-care.md` reminder/record formats.
- `references/bud-bloom-tracker.md` (#173) — bud/bloom/flush tracking and bloom-window forecasting with **explicit confidence** (user's own logs first, species baseline as fallback), bud-drop cause logging, and the pink-marker workflow. Explicitly skips *Ficus benjamina* flowering (enclosed in the syconium). Reuses `cut_marker.py` (`SEMANTIC="bud"`) — no new script.
- `references/aerial-roots-nebari.md` (#174) — aerial-root and nebari development tracker with a `tip_promising → guided → reached_soil → thickening → fused` lifecycle, a health-and-warmth intervention gate, sphagnum/tube/humidity-tent techniques, and thickening-rate prediction. Expands the brief note in `bonsai-module.md`.
- `references/health-diagnostics.md` (#175) — computer-vision "check-engine light": screens the photos the skill already collects for chlorosis/leaf-drop patterns and common indoor pests, cross-references against recent care events, emits `health_flag_added` events, and **escalates structural-work risk** while open. Inspection / isolation / mechanical / cultural correction over chemicals.
- `references/grafting-sandbox.md` (#176) — simulation-only Blender boolean-union graft preview (approach/trunk/multi-tree fusion) with seam smoothing and pre/post silhouette renders; stays in `05_simulations/`, never mutates the canonical twin.
- `references/propagation.md` (#177) — propagation tracker: tip/stem cuttings vs. air-layering, `started → rooted → potted_up → independent` (or `failed`) lifecycle, parent/child `plant_id` lineage, and optimal-cutting-window timing via the chrono engine.

### Added — scripts

- `scripts/wire_window.py` (#172) — pure-Python helper returning the wire-removal inspection window (first-inspection date, recheck cadence, a 4-date ladder, and a calendar-ready guidance string) from `WIRED_DATE`, `GROWTH_CLASS` (fast/moderate/slow), and `ACTIVE_GROWTH`. No Blender required; unit-tested.
- `scripts/aerial_root_trace.py` (#174) — draws a teal, gently-drooping guided-root poly-curve from a branch tip to a substrate landing point and stamps lifecycle `STATE`. The drooping-path math (`droop_path_points`) is importable without bpy and unit-tested.
- `scripts/grafting_sim.py` (#176) — duplicates scion + stock into a dated `05_simulations/sim_graft_<label>_<date>` collection, applies a boolean UNION plus a corrective-smooth callus pass on the **copies**, and stamps graft metadata; leaves the canonical twin untouched and the fused result selected for rendering.

### Changed

- `SKILL.md` — bumped to v0.3.0 (`last-updated: 2026-06-15`); added six new routing entries to the Core Workflow and three new entries to Bundled Scripts.
- `references/collection-records-and-care.md` — added event types `cutting_potted_up`, `cutting_failed`, and the aerial-root lifecycle events (`aerial_root_observed/guided/reached_soil/thickening/fused`), with cross-links to the new references and a note on `parent_plant_id` lineage.
- `manifest.yaml` — bumped to v0.3.0; indexed all six new references and three new scripts (with inputs/outputs and `requires_blender`); converted the `deferred:` block to a `v2_features:` block mapping each story (#172–#177) to its delivered files.
- `tests/test_houseplant_scripts.py` — added `wire_window.py`, `aerial_root_trace.py`, `grafting_sim.py` to the expected-scripts set and added pure-math test classes for the wire-window ladder and the aerial-root droop path. 24 tests pass.

### Epic / stories

Closes the v2 feature set tracked under epic #209: #172 (chrono engine), #173 (bud/bloom tracker), #174 (aerial-root/nebari), #175 (CV health diagnostics), #176 (grafting sandbox), #177 (propagation tracker).

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
