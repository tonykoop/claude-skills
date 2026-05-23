# Blender Digital Twin Workflow

Read this reference when the user wants Blender MCP, `bpy`, mobile photogrammetry, LiDAR scans, procedural foliage, scene updates, pruning simulations, wiring simulations, or digital-twin sync.

If the user is at the capture stage (still has raw photos/video/scan that hasn't entered Blender yet), read [`capture-pipeline.md`](capture-pipeline.md) first.

## Blender MCP Tool Order

Almost every Blender MCP session follows the same orient → plan → execute → verify rhythm. Skipping the orient step is the most common cause of brittle code that breaks when the user's scene differs from what Claude assumed.

1. **Orient.** Call `mcp__Blender__get_blendfile_summary_path_info`, `get_blendfile_summary_datablocks`, and `get_objects_summary` to learn the file. If a `Plant_<plant_id>/` collection already exists, inspect it via `get_object_detail_summary` before touching anything.
2. **Plan.** Decide which scene contract directory each change goes into (`02_skeleton_curves`, `04_markers`, `05_simulations`, etc.). Plan idempotently: every object you create should have a deterministic name you can find again next session.
3. **Execute.** Run `mcp__Blender__execute_blender_code` with a focused script. Prefer importing or pasting bundled scripts from `../scripts/` rather than reinventing patterns. Errors loop back to you — use them to self-correct.
4. **Verify.** Call `get_screenshot_of_window_as_image` or `render_thumbnail_to_path` and look at the result before reporting success. If the user asked for "the apex marker on the front-left branch," check the screenshot says so.
5. **Document.** Append a digital-twin sync note to the plant record (template at the bottom of this file).

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
- Make operations idempotent: find existing collections/objects by name before creating duplicates. The bundled scripts in `../scripts/` are written this way — prefer them over ad-hoc snippets.
- Prefer curves, bevel depths, instances, and modifiers for editable plant structures. Use Geometry Nodes when they clearly improve editability; fall back to curves and instanced meshes when node-tree API work would be brittle.
- Store simulation alternatives as separate collections with clear names such as `sim_prune_apex_2026-05-17` or `sim_wire_R02_down_30deg`. `scripts/sim_collection.py` does this in one call.
- Use material colors consistently with `SKILL.md`: red cut/remove, amber watch, blue wire/bend, green preserve/encourage, pink bud/bloom, teal aerial root.
- Keep physical advice separate from viewport operations. A Blender cut marker is a recommendation, not confirmation that the physical plant was cut.

## Concrete bpy Patterns

These are starting points to adapt — paste into `mcp__Blender__execute_blender_code` after `get_objects_summary` has confirmed your assumptions about the scene. Full versions live in `../scripts/`.

### Scaffolding the scene contract for a new specimen

```python
import bpy

PLANT_ID = "ficus-benjamina-01"
CHILDREN = [
    "00_source_scan", "01_reference_photos", "02_skeleton_curves",
    "03_procedural_geometry", "04_markers", "05_simulations", "99_exports",
]

def ensure_collection(name, parent):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        parent.children.link(coll)
    return coll

root = ensure_collection(f"Plant_{PLANT_ID}", bpy.context.scene.collection)
for child in CHILDREN:
    ensure_collection(f"{PLANT_ID}__{child}", root)

# Stamp custom properties so future sessions can recover context.
root["plant_id"] = PLANT_ID
root["last_synced"] = "YYYY-MM-DD"
```

### Placing a cut marker at a coordinate

```python
import bpy

def cut_marker(plant_id, branch_id, suffix, location, color=(1, 0.1, 0.1, 1)):
    name = f"{plant_id}_cut_marker_{branch_id}_{suffix}"
    obj = bpy.data.objects.get(name)
    if obj is None:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.005, location=location)
        obj = bpy.context.active_object
        obj.name = name
    mat = bpy.data.materials.get(f"mat_cut_red") or bpy.data.materials.new("mat_cut_red")
    mat.diffuse_color = color
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return obj
```

### Wire-coil helix wrapped around a branch curve

The simplest reliable approach is a parametric helix curve generated as a poly curve, then bevel-depthed to give it copper-wire thickness. This avoids the brittleness of trying to drive a Screw modifier on a non-axis-aligned branch curve.

```python
import bpy, math
from mathutils import Vector

def wire_coil(branch_obj, plant_id, branch_id, turns_per_meter=18,
              wire_radius=0.0015, coil_radius=None, name_suffix=""):
    # Sample the branch curve to get a poly-line backbone.
    if branch_obj.type != "CURVE":
        raise TypeError("Pass the branch curve, not its instance.")
    spline = branch_obj.data.splines[0]
    points = [Vector(p.co.xyz) for p in spline.bezier_points] if spline.bezier_points else \
             [Vector(p.co.xyz) for p in spline.points]
    # Walk the backbone, building a helical offset around each segment's tangent frame.
    helix_points = []
    arc_len = 0.0
    for i in range(len(points) - 1):
        a, b = points[i], points[i + 1]
        seg = b - a
        seg_len = seg.length
        tangent = seg.normalized()
        # Pick a stable "up" that isn't parallel to tangent.
        up = Vector((0, 0, 1)) if abs(tangent.z) < 0.9 else Vector((1, 0, 0))
        side = tangent.cross(up).normalized()
        up = side.cross(tangent).normalized()
        radius = coil_radius if coil_radius else max(0.005, wire_radius * 3)
        steps = max(8, int(seg_len * turns_per_meter * 8))
        for s in range(steps + 1):
            t = s / steps
            angle = (arc_len + t * seg_len) * turns_per_meter * 2 * math.pi
            offset = side * math.cos(angle) * radius + up * math.sin(angle) * radius
            helix_points.append(a + tangent * (t * seg_len) + offset)
        arc_len += seg_len
    # Build the curve datablock.
    coil_name = f"{plant_id}_wire_sim_{branch_id}_{name_suffix}".rstrip("_")
    curve_data = bpy.data.curves.new(coil_name, type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = wire_radius
    spl = curve_data.splines.new("POLY")
    spl.points.add(len(helix_points) - 1)
    for i, p in enumerate(helix_points):
        spl.points[i].co = (p.x, p.y, p.z, 1.0)
    obj = bpy.data.objects.new(coil_name, curve_data)
    bpy.context.scene.collection.objects.link(obj)
    return obj
```

For the user's first session, default to ~18 turns/meter — that's a wraps-loose-enough-to-not-bite-in starting point. Tighter wraps come later when bend force needs to be higher.

### Creating a simulation collection without mutating the twin

```python
import bpy, datetime

def make_sim_collection(plant_id, scenario):
    today = datetime.date.today().isoformat()
    sim_name = f"sim_{scenario}_{today}"
    parent = bpy.data.collections.get(f"{plant_id}__05_simulations")
    sim = bpy.data.collections.get(sim_name) or bpy.data.collections.new(sim_name)
    if sim.name not in parent.children:
        parent.children.link(sim)
    # Caller adds simulated geometry into `sim`. Current-state twin stays untouched.
    return sim
```

## Hybrid Reconstruction Recipe (Phone Scan → Editable Twin)

When the user imports a photogrammetry mesh:

1. Import the `.obj`/`.ply`/`.glb` into `00_source_scan/` and leave it there as evidence.
2. Run `scripts/scale_from_ruler.py` (or the inline math) using the ruler in the scan to set scene scale.
3. Duplicate the source mesh into `02_skeleton_curves/` as a working copy. Skeletonize: identify the trunk and primary branch axes either by hand (placing curve handles along visible branches in the duplicate) or by running a Laplacian-style contraction script. The deliverable of this step is one Bezier curve per "decision unit": trunk, primary branches, major secondaries.
4. In `03_procedural_geometry/`, keep the cleanest trunk faces from the scan as the visible trunk shell, but discard the melted foliage faces. Instance simple leaf meshes along the terminal portions of the skeleton curves using a Geometry Nodes modifier or instance-on-points setup.
5. Place markers in `04_markers/` for any decisions the user wants to remember between sessions.
6. Run pruning/wiring simulations in `05_simulations/` only.

If the scan quality is too poor for skeletonization, fall back to a curve-only stylized twin built directly from measurements off the multi-angle photos — make this fallback explicit in the sync log.

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
