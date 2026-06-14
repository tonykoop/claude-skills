---
name: houseplant
version: 0.3.0
last-updated: 2026-06-13
description: Manage houseplant and bonsai collection digital twins plus care workflows, with first-class Blender MCP support. Use this skill whenever the user mentions a houseplant or bonsai specimen, pruning plans, wire-coil bending or training, mobile phone scans (photogrammetry, LiDAR, orbit video, lazy-susan video), multi-angle plant photos, bonsai aerial roots or nebari, bud/bloom tracking, plant care checklists, watering or fertilizing schedules, propagation logs, ruler-based scale calibration of a 3D scan, or any task that updates an Obsidian/Markdown/spreadsheet plant database. Use this skill even when the user only mentions "my plant" plus an action (prune, wire, train, repot, scan, model) — it owns that workflow.
---

# Houseplant

Use this skill to treat each houseplant as a living record plus a digital twin. Start with the user's collection database, update or simulate the plant's Blender state when available, then produce practical care outputs: annotated photos, decisive pruning or wiring plans with risk levels, calendar-ready follow-ups, and checklists.

The killer app this skill enables is **simulate before you cut**: build a parametric Blender twin from phone captures, try the prune and wire-coil scenarios in `05_simulations/`, then commit the version you like to the physical plant.

## Core Workflow

1. **Identify the specimen.** Prefer a stable `plant_id` from Obsidian, Markdown, or a spreadsheet; create a provisional id only when none exists. If the user has a starter profile in `assets/`, load it.
2. **Gather minimum useful context.** Species or likely species, current date and location, indoor/outdoor placement, last water/fertilizer/repot/prune/wire events, health concerns, intended outcome.
3. **Gather media and model inputs.** For 2D-only work, prefer front, back, left, right, top-down, trunk/root close-up, and target-branch close-up photos with a ruler or other scale reference visible in at least one shot. For digital twins, also ask for or inspect `.blend`, `.obj`, `.ply`, `.glb`, texture, or scan folders, and a known-scale object (ruler, AprilTag, pot diameter).
4. **Route to the right reference.** Read only what the current task actually needs:
   - **Capture intake** (the user has photos/video/scan and wants them turned into a Blender-usable twin): [`references/capture-pipeline.md`](references/capture-pipeline.md).
   - **Blender or MCP digital twin work** (scene contract, MCP tool order, bpy patterns, pruning/wiring sims): [`references/blender-digital-twin.md`](references/blender-digital-twin.md).
   - **Bonsai pruning, wiring, aerial roots, branch styling, ficus-specific guidance**: [`references/bonsai-module.md`](references/bonsai-module.md).
   - **Obsidian/spreadsheet records, care checklists, reminder drafts**: [`references/collection-records-and-care.md`](references/collection-records-and-care.md).
   - **Dynamic care scheduling, watering/fertilizing windows, wire-removal checks**: [`references/chrono-engine.md`](references/chrono-engine.md).
5. **Recommend decisively.** Include risk level, evidence, assumptions, and a quick pre-action verification step for irreversible physical actions. Be explicit about what was simulated vs. what was observed.
6. **Sync results back.** Blender scene changes, annotated images, plant record updates, calendar-ready reminders, care checklists.

## Blender MCP Tools

When Blender MCP is connected, prefer its tools over guessing:

- `mcp__Blender__get_blendfile_summary_*` — orient yourself in an unfamiliar `.blend`.
- `mcp__Blender__get_objects_summary` and `get_object_detail_summary` — inspect the scene before writing. Don't assume object names.
- `mcp__Blender__execute_blender_code` — write or run `bpy` Python. The patterns in `scripts/` are designed to be pasted or imported here.
- `mcp__Blender__get_screenshot_of_window_as_image` — capture viewport state for the user or for grounding the next step.
- `mcp__Blender__render_viewport_to_path` / `render_thumbnail_to_path` — produce exportable comparison images.
- `mcp__Blender__search_api_docs` / `search_manual_docs` / `get_python_api_docs` — resolve uncertainty about a `bpy` symbol before guessing.

Inspect first, then write. Idempotency matters: check for existing collections and objects by name before creating duplicates.

## Bundled Scripts

`scripts/` contains adaptable `bpy` modules for the most common moves. Read or paste them rather than re-deriving:

- `scripts/scene_scaffold.py` — builds the `Plant_<plant_id>/` collection hierarchy and stamps custom properties.
- `scripts/scale_from_ruler.py` — calibrates scene units from a measured ruler segment in the scan.
- `scripts/wire_coil.py` — generates a helical copper-colored curve around a branch curve for wire-bending preview.
- `scripts/cut_marker.py` — places a colored empty/sphere marker at a coordinate with the skill's color semantics.
- `scripts/sim_collection.py` — clones the current-state twin into a dated `05_simulations/sim_<scenario>` collection for non-destructive what-if.

`assets/` holds starter profiles for specific specimens (e.g. `assets/ficus-benjamina-starter.md`). Use them as a baseline plant record when the user hasn't created their own.

## Output Contracts

For a **Blender scene update**, report the scene file or target scene, changed collections or objects, assumptions about scale/orientation, simulation objects created, custom properties updated, exports produced, and unresolved uncertainties.

For a **bonsai pruning or wiring plan**, include branch ids or visual references, recommended action, reason, risk level, "verify before cutting/bending" check, aftercare, and follow-up date.

For **annotated photos**, use consistent color semantics: red for cut/remove, amber for watch/uncertain, blue for wire/bend, green for preserve/encourage, pink for bud/bloom event, and teal for aerial-root/root-work guidance. Keep labels short enough to remain readable on mobile.

For **calendar reminders**, provide exact dates or recurrence rules in plain language, the trigger evidence, priority, and a checklist. Create live calendar events only when the user asks and a calendar connector/tool is available; otherwise draft calendar-ready entries.

For **care checklists**, make them action-oriented and specimen-specific. Avoid generic "water every N days" rules unless the user explicitly wants a fixed cadence; prefer observation windows and tests such as soil moisture, pot weight, leaf turgor, growth stage, and recent weather.

## Decision Rules

- Prefer simulation before irreversible physical action. In Blender, create a separate simulation collection instead of overwriting the current-state twin.
- Preserve raw evidence. Do not destructively edit original scans, photos, or plant records; append dated logs and create derived artifacts.
- Be explicit about uncertainty. If species, scale, branch identity, seasonality, or health status is uncertain, state how that uncertainty affects the recommendation.
- Use risk levels:
  - `Low`: maintenance trimming, checklist updates, marker placement, reversible Blender-only changes.
  - `Medium`: structural pruning on a healthy plant, moderate wiring, care schedule changes after clear evidence.
  - `High`: major branch removal, trunk/root work, heavy bending, out-of-season interventions, weak or pest-stressed plants, or action based on poor media.
- Avoid restricted pesticide or hazardous treatment instructions. Prefer inspection, isolation, mechanical removal, cultural correction, and label-compliant local guidance.

## Skill Boundaries

This skill owns houseplant collection state, care workflows, Blender digital twins, and bonsai-oriented styling workflows. It may hand off to `reverse-engineer` when reconstructing a physical object or unknown mechanism from sparse photos, and to `makerspace` when the user wants fabrication plans for plant stands, jigs, fixtures, shelves, or watering hardware.

Do not turn every request into a full digital twin project. For a simple care question, use the collection record and produce a concise checklist. For a Blender request, assume Blender MCP is installed and operational, inspect the live scene before changing it, and leave the user with clear scene changes and next actions.
