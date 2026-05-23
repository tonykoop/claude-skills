# Blender Digital Twin Workflow

Read this reference when the user wants Blender MCP, `bpy`, mobile photogrammetry, LiDAR scans, procedural foliage, scene updates, pruning simulations, wiring simulations, or digital-twin sync.

## Scene Contract

Use a stable parent collection per specimen:

```text
Plant_<plant_id>/
  00_source_scan/
  01_reference_photos/
  02_skeleton_curves/
  03_procedural_geometry/
  04_markers/
  05_simulations/
  99_exports/
```

Name objects so they can be referenced in plant records and future sessions:

```text
<plant_id>_source_scan_<YYYYMMDD>
<plant_id>_trunk_curve
<plant_id>_branch_L01
<plant_id>_branch_R02
<plant_id>_cut_marker_L01_A
<plant_id>_wire_sim_R02_<YYYYMMDD>
<plant_id>_bud_marker_<YYYYMMDD>_01
```

Set custom properties on parent collections or key objects when possible:

- `plant_id`
- `scientific_name`
- `common_name`
- `source_record`
- `capture_date`
- `scale_units`
- `front_axis`
- `confidence`
- `last_synced`
- `notes`

## Digital Twin Update Steps

1. Inspect the existing Blender scene through MCP before editing. Record relevant object names, collections, modifiers, and units.
2. Preserve raw scans. Import `.obj`, `.ply`, `.glb`, or scan assets into `00_source_scan/`; duplicate meshes for cleanup or segmentation.
3. Establish scale and orientation. Use a ruler, pot diameter, known planter size, AprilTag/marker, or user-provided measurement. Define the chosen front and axes in custom properties.
4. Separate evidence from interpretation. Keep the scan/photo-derived current state distinct from procedural branches, leaf instances, and simulation geometry.
5. Build a branch skeleton. Prefer one curve per meaningful decision unit: trunk line, primary branches, major secondary branches, aerial roots, and wires. Branch ids should remain stable across future pruning plans.
6. Replace messy foliage only when useful. Photogrammetry often turns leaves into noisy green mass; keep high-quality trunk/root scans, then add procedural or instanced foliage tied to terminal branch curves.
7. Add markers for decisions and events. Use small named objects or empties for cut points, wire anchors, buds, bloom sites, aerial-root tips, disease flags, and follow-up inspections.
8. Create simulations in `05_simulations/`. Do not mutate the current-state twin when previewing pruning, bending, grafting, root development, or future growth.
9. Export useful artifacts: viewport screenshot, render, GLB, annotated still, or a short change log. Update the collection record with paths and changed object ids.

## Blender MCP Implementation Guidance

- Use `bpy` to inspect before writing; do not assume object names from memory.
- Make operations idempotent where possible: find existing collections/objects by name before creating duplicates.
- Prefer curves, bevel depths, instances, and modifiers for editable plant structures. Use Geometry Nodes when they clearly improve editability; fall back to curves and instanced meshes when node-tree API work would be brittle.
- Store simulation alternatives as separate collections with clear names such as `sim_prune_apex_2026-05-17` or `sim_wire_R02_down_30deg`.
- Use material colors consistently with `SKILL.md`: red cut/remove, amber watch, blue wire/bend, green preserve/encourage, pink bud/bloom, teal aerial root.
- Keep physical advice separate from viewport operations. A Blender cut marker is a recommendation, not confirmation that the physical plant was cut.

## Pruning Simulation

For each candidate cut:

1. Identify the branch curve or mesh segment and assign a stable branch id.
2. Create a cut marker at the proposed node/internode.
3. In simulation, hide, shorten, or ghost the removed section rather than deleting the current-state object.
4. Add a projected silhouette or comparison render when useful.
5. Record the risk level and aftercare in the plant record or response.

## Wiring Simulation

For each target branch:

1. Estimate branch diameter from scan scale or user measurement.
2. Create a blue wire curve around the branch path. Approximate a helical wrap; exact coil physics are not required for planning.
3. Store wire material, gauge, application date, target bend, and inspection/removal window.
4. Bend via the branch skeleton or a duplicated simulation curve. Avoid destructive mesh deformation on the current-state twin.
5. Add follow-up reminders for bite-in inspection during active growth.

## Digital Twin Sync Log

Every scene update should leave a compact sync note:

```markdown
### Digital twin sync - YYYY-MM-DD
- Scene/file:
- Inputs:
- Changed objects:
- Simulations created:
- Exported artifacts:
- Care or styling decisions:
- Follow-ups:
- Uncertainties:
```
