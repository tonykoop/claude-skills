# Pruning + wiring simulation: ficus-benjamina-01

Good instinct simulating first. L03 is structural-removal territory (Medium-to-High risk) and R02 down-bending with wire is a Medium-risk staged bend on a fast-cambium species, so seeing both in the twin before you reach for the shears is worth ten minutes of Blender time.

I will not touch `Plant_ficus-benjamina-01__02_skeleton_curves` or `__03_procedural_geometry`. Everything lands in a fresh dated sim collection under `__05_simulations/`, plus markers in `__04_markers/`.

## MCP tool call order

1. `mcp__Blender__get_blendfile_summary_path_info` — confirm the .blend path so the sync log records it.
2. `mcp__Blender__get_objects_summary` — confirm the seven branch curves and the trunk curve exist under `Plant_ficus-benjamina-01` and that the `__05_simulations` collection is present (if not, I scaffold it).
3. `mcp__Blender__get_object_detail_summary` on `ficus-benjamina-01_branch_L03` and `_R02` — read their world matrix, spline endpoints, and current users_collection so I can compute the L03 base point (cut location) and the R02 tip (current vs. target end position for the bend).
4. `mcp__Blender__execute_blender_code` — run **Pass 1: scaffold + sim collection** (block A below).
5. `mcp__Blender__execute_blender_code` — run **Pass 2: prune L03** (block B). Makes L03 single-user inside the sim, hides + ghosts it, and drops a red cut marker at its base.
6. `mcp__Blender__execute_blender_code` — run **Pass 3: bend R02 + wire coil** (block C). Single-users R02's curve, rotates a control point about the R02 base to drop the tip ~25 degrees, places a blue wire-anchor marker at the base, then runs `wire_coil.py` against the simulated curve.
7. `mcp__Blender__execute_blender_code` — run **Pass 4: framing** (block D). Sets the active camera or viewport to the recorded front axis, frames the `Plant_ficus-benjamina-01` collection, and isolates the current-state twin + the sim collection.
8. `mcp__Blender__get_screenshot_of_window_as_image` — capture the viewport. (Also `render_thumbnail_to_path` to `99_exports/sim_prune-L03_wire-R02-down_2026-05-17.png` for the record.)
9. `mcp__Blender__execute_blender_code` — run **Pass 5: silhouette diff** (block E). Projects both versions' branch curves onto the front-view plane and prints bounding-box deltas (width, height, apex shift, right-side droop) so the silhouette change is a number, not a vibe.

## Code I would send through `execute_blender_code`

### Block A — sim collection (uses bundled `sim_collection.py`)

```python
PLANT_ID = "ficus-benjamina-01"
SCENARIO = "prune-L03_wire-R02-down"
SOURCE_COLLECTIONS = ["02_skeleton_curves", "03_procedural_geometry"]
DATE_OVERRIDE = "2026-05-17"
exec(open(r"C:/Users/Tony/Documents/GitHub/claude-skills/skills/houseplant/scripts/sim_collection.py").read())
# -> sim_prune-L03_wire-R02-down_2026-05-17 under ficus-benjamina-01__05_simulations
```

The script links (does not copy) the current-state curves into the sim. Anything I want to diverge gets `Make Single User` next.

### Block B — prune L03 (red marker + ghosted curve)

```python
import bpy
from mathutils import Vector

PLANT_ID = "ficus-benjamina-01"
SIM_NAME = "sim_prune-L03_wire-R02-down_2026-05-17"
sim = bpy.data.collections[SIM_NAME]

# 1. Single-user L03 inside the sim so hiding/recoloring it doesn't touch the canonical curve.
src = bpy.data.objects["ficus-benjamina-01_branch_L03"]
ghost = src.copy()
ghost.data = src.data.copy()
ghost.name = "ficus-benjamina-01_branch_L03__sim_removed"
sim.objects.link(ghost)
# Unlink the linked-from-canonical L03 from the sim only.
if src.name in sim.objects:
    sim.objects.unlink(src)

# 2. Ghost material (semi-transparent red) so the removed branch is visible as "gone-but-where".
mat = bpy.data.materials.get("mat_sim_removed_ghost") or bpy.data.materials.new("mat_sim_removed_ghost")
mat.diffuse_color = (1.0, 0.15, 0.15, 0.25)
mat.use_nodes = False
if ghost.data.materials:
    ghost.data.materials[0] = mat
else:
    ghost.data.materials.append(mat)
ghost.hide_render = True  # ghost shows in viewport only; the silhouette render uses the unghosted set
ghost.display_type = "WIRE"

# 3. Red cut marker at the L03 base (first control point in world space).
spline = src.data.splines[0]
base_local = spline.bezier_points[0].co if len(spline.bezier_points) else Vector(spline.points[0].co.xyz)
base_world = src.matrix_world @ base_local

PLANT_ID = "ficus-benjamina-01"
BRANCH_ID = "L03"
SUFFIX = "A"
LOCATION = tuple(base_world)
SEMANTIC = "cut"
RADIUS = 0.006
exec(open(r"C:/Users/Tony/Documents/GitHub/claude-skills/skills/houseplant/scripts/cut_marker.py").read())
```

### Block C — bend R02 down + wire coil

```python
import bpy, math
from mathutils import Vector, Matrix

PLANT_ID = "ficus-benjamina-01"
SIM_NAME = "sim_prune-L03_wire-R02-down_2026-05-17"
sim = bpy.data.collections[SIM_NAME]

# 1. Single-user R02 in the sim.
src = bpy.data.objects["ficus-benjamina-01_branch_R02"]
bent = src.copy()
bent.data = src.data.copy()
bent.name = "ficus-benjamina-01_branch_R02__sim_bent"
sim.objects.link(bent)
if src.name in sim.objects:
    sim.objects.unlink(src)

# 2. Rotate downstream control points about the branch base to drop the tip ~25 degrees.
#    Axis of rotation: branch-base tangent crossed with world up, so the bend is "downward in the front view".
spline = bent.data.splines[0]
pts = spline.bezier_points if len(spline.bezier_points) else spline.points
base = pts[0].co.xyz.copy()
tip_dir = (pts[-1].co.xyz - base).normalized()
axis = tip_dir.cross(Vector((0, 0, 1)))
if axis.length < 1e-4:
    axis = Vector((1, 0, 0))
axis.normalize()
bend_deg = 25.0
R = Matrix.Rotation(math.radians(-bend_deg), 4, axis)  # negative = downward in front view

for i in range(1, len(pts)):  # leave the base anchor fixed
    rel = pts[i].co.xyz - base
    pts[i].co.xyz = base + (R @ rel)
    if hasattr(pts[i], "handle_left"):
        rel_l = pts[i].handle_left.xyz - base
        rel_r = pts[i].handle_right.xyz - base
        pts[i].handle_left.xyz  = base + (R @ rel_l)
        pts[i].handle_right.xyz = base + (R @ rel_r)

# 3. Blue wire-anchor marker at the bend's anchor point.
base_world = bent.matrix_world @ base
PLANT_ID = "ficus-benjamina-01"
BRANCH_ID = "R02"
SUFFIX = "anchor"
LOCATION = tuple(base_world)
SEMANTIC = "wire"
RADIUS = 0.005
exec(open(r"C:/Users/Tony/Documents/GitHub/claude-skills/skills/houseplant/scripts/cut_marker.py").read())

# 4. Wire coil around the *bent* curve (~2.0 mm wire is a reasonable starting gauge for an R02-sized branch;
#    re-estimate from real caliper measurement before applying).
BRANCH_OBJ_NAME = "ficus-benjamina-01_branch_R02__sim_bent"
PLANT_ID = "ficus-benjamina-01"
BRANCH_ID = "R02"
SUFFIX = "2026-05-17"
TURNS_PER_METER = 18
WIRE_RADIUS = 0.0010   # 1.0 mm copper as a placeholder; bump if your branch caliper is >6 mm
COIL_RADIUS = None
exec(open(r"C:/Users/Tony/Documents/GitHub/claude-skills/skills/houseplant/scripts/wire_coil.py").read())

# 5. Re-link the coil into the sim collection so it lives with the rest of the scenario.
coil = bpy.data.objects.get("ficus-benjamina-01_wire_sim_R02_2026-05-17")
if coil and coil.name not in sim.objects:
    for c in list(coil.users_collection):
        c.objects.unlink(coil)
    sim.objects.link(coil)
```

### Block D — viewport framing

```python
import bpy

# Hide L03 in the sim's viewport so the prune actually reads.
ghost = bpy.data.objects["ficus-benjamina-01_branch_L03__sim_removed"]
ghost.hide_set(True)  # silhouette will see "L03 gone"; un-hide for the annotated still pass

# Isolate canonical twin + sim collection.
view_layer = bpy.context.view_layer
for layer_coll in view_layer.layer_collection.children:
    layer_coll.exclude = False
# Face the recorded front. Defaults to -Y if no front_axis property is set.
root = bpy.data.collections["Plant_ficus-benjamina-01"]
front_axis = root.get("front_axis", "-Y")

for area in bpy.context.screen.areas:
    if area.type == "VIEW_3D":
        with bpy.context.temp_override(area=area):
            bpy.ops.view3d.view_axis(type={"+X":"RIGHT","-X":"LEFT","+Y":"BACK","-Y":"FRONT","+Z":"TOP","-Z":"BOTTOM"}.get(front_axis, "FRONT"))
            bpy.ops.view3d.view_selected(use_all_regions=False)
        break
```

### Block E — silhouette diff (front-view projection)

```python
import bpy
from mathutils import Vector

PLANT_ID = "ficus-benjamina-01"
ROOT = bpy.data.collections[f"Plant_{PLANT_ID}"]
front_axis = ROOT.get("front_axis", "-Y")
# Project to the plane perpendicular to the front axis.
# For -Y front: silhouette = (X, Z). For +X: silhouette = (Y, Z). Etc.
PROJECT = {
    "-Y": lambda v: (v.x, v.z), "+Y": lambda v: (-v.x, v.z),
    "+X": lambda v: (-v.y, v.z), "-X": lambda v: (v.y, v.z),
    "+Z": lambda v: (v.x, v.y),  "-Z": lambda v: (v.x, -v.y),
}[front_axis]

def sample_obj(obj):
    if obj.type != "CURVE":
        return []
    out = []
    for spl in obj.data.splines:
        pts = spl.bezier_points if len(spl.bezier_points) else spl.points
        for p in pts:
            out.append(obj.matrix_world @ p.co.xyz)
    return out

# Current-state set: all canonical L01..L03 / R01..R02 plus trunk.
current_names = [f"{PLANT_ID}_trunk_curve"] + \
    [f"{PLANT_ID}_branch_L0{i}" for i in (1,2,3)] + \
    [f"{PLANT_ID}_branch_R0{i}" for i in (1,2)]
# Sim set: L03 removed, R02 replaced by the bent copy.
sim_names = [f"{PLANT_ID}_trunk_curve",
             f"{PLANT_ID}_branch_L01", f"{PLANT_ID}_branch_L02",
             f"{PLANT_ID}_branch_R01",
             f"{PLANT_ID}_branch_R02__sim_bent"]

def silhouette(names):
    pts2d = []
    for n in names:
        o = bpy.data.objects.get(n)
        if o is None: continue
        for w in sample_obj(o):
            pts2d.append(PROJECT(w))
    if not pts2d: return None
    xs = [p[0] for p in pts2d]; zs = [p[1] for p in pts2d]
    return {
        "min_x": min(xs), "max_x": max(xs),
        "min_z": min(zs), "max_z": max(zs),
        "width": max(xs) - min(xs),
        "height": max(zs) - min(zs),
        "apex_z": max(zs),
        "right_tip_z": max((p[1] for p in pts2d if p[0] > 0), default=None),
        "n": len(pts2d),
    }

cur = silhouette(current_names)
sim = silhouette(sim_names)
print("CURRENT", cur)
print("SIM    ", sim)
print("DELTAS",
      "width", round(sim["width"]-cur["width"], 4),
      "height", round(sim["height"]-cur["height"], 4),
      "apex_z", round(sim["apex_z"]-cur["apex_z"], 4),
      "right_tip_z", round(sim["right_tip_z"]-cur["right_tip_z"], 4))
```

The print line is what I'd read off the MCP response to give you actual numbers.

## What you'd see on the screenshot (and the silhouette call)

Without live MCP I can't paste real numbers, but here is the predicted silhouette change for this exact pair of edits on a top-heavy ficus with L03 acting as the secondary leader and R02 reaching upper-right:

- **Apex height:** unchanged (the main apex is on the trunk curve, not on L03), or slightly lower if L03's tip was the highest sample. If L03's tip was poking above the trunk apex you'll see `apex_z` drop by the gap between trunk apex and L03 tip.
- **Upper-left mass:** noticeably reduced. The left side of the canopy becomes cleaner and the trunk line reads more dominantly because the competing leader is gone. Expect `max_x` on the left side (i.e. `min_x` becoming less negative) to shrink by the projected L03 reach.
- **Right side:** the R02 tip drops. With a 25-degree downward rotation about the R02 base, `right_tip_z` decreases by roughly `R02_length * sin(25°) ≈ 0.42 * R02_length`. So if R02 is ~22 cm tip-to-base, the tip falls about 9 cm in front-view.
- **Overall canopy width:** modestly narrower (L03 gone reduces left reach) and a touch taller-feeling because the silhouette is no longer competing at the top.
- **Visual read:** trunk line + apex become the single clear "story" of the tree, with the new R02 angle pulling the eye downward to the right — the classic asymmetric bonsai silhouette that lets the nebari and trunk movement speak.

When you actually run this I'll replace the prediction above with the exact deltas from Block E's print line.

## Pruning + wiring plan

| Id | Action | Why | Risk | Verify before cutting/bending | Aftercare | Follow-up |
|---|---|---|---|---|---|---|
| L03-A | Remove branch L03 at its base, clean cut just outside the collar | L03 is acting as a secondary leader; removing it commits the trunk apex as the single leader and opens the upper-left canopy | Medium-to-High | Confirm the red marker `ficus-benjamina-01_cut_marker_L03_A` sits at the junction where L03 leaves the trunk on the upper-left from the chosen front. Confirm L03 is what's reaching up-and-left and competing with the apex, not L02 | Seal with sterile cut paste if available; stable bright indirect light; normal moisture; pause fertilizer 7 days | Photo + back-budding check at 3-4 weeks |
| R02-W | Wire R02 with ~1.0 mm copper, ~18 turns/m, bend tip down ~25 degrees | Lowers the right-side line so the silhouette reads asymmetric and the R02 tip stops competing for vertical attention | Medium | Confirm R02 caliper at the base (target wire ~1/3 of branch diameter — re-pick gauge if branch is >6 mm); confirm blue anchor marker sits at the R02 base, not partway up; bend in one continuous motion to avoid cracking | Inspect for wire bite every 7-10 days during active growth; remove wire as soon as the set is taken or bark starts to swell | First bite-in inspection in 7 days; full set typically 4-8 weeks on ficus |

**Do not cut:** L01, L02, R01, trunk apex. L01 and L02 are part of the keeper structure on the left after L03 comes off; the trunk apex becomes the sole leader.

## Output contract: Blender scene update

- **Scene file:** the `.blend` reported by `get_blendfile_summary_path_info`.
- **Untouched collections:** `Plant_ficus-benjamina-01__02_skeleton_curves`, `__03_procedural_geometry` (current-state twin preserved).
- **New simulation collection:** `Plant_ficus-benjamina-01__05_simulations/sim_prune-L03_wire-R02-down_2026-05-17`.
- **New objects:**
  - `ficus-benjamina-01_branch_L03__sim_removed` (single-user copy, ghost material, hidden in viewport for the silhouette pass)
  - `ficus-benjamina-01_branch_R02__sim_bent` (single-user copy, control points rotated -25 deg about base, downward in front view)
  - `ficus-benjamina-01_wire_sim_R02_2026-05-17` (copper helix curve, bevel_depth = 0.0010 m)
- **New markers** (in `__04_markers`):
  - `ficus-benjamina-01_cut_marker_L03_A` (red, at L03 base)
  - `ficus-benjamina-01_wire_anchor_R02_anchor` (blue, at R02 base)
- **Exports:** `99_exports/sim_prune-L03_wire-R02-down_2026-05-17.png` (viewport thumbnail render).
- **Custom properties:** sim collection stamped with `scenario`, `created`, `plant_id`. Wire object stamped with `wire_radius_m`, `turns_per_meter`, `applied_date`, `branch_id`.
- **Assumptions:**
  - Front axis = the `front_axis` custom property on `Plant_ficus-benjamina-01`, or `-Y` if unset.
  - Scene units in meters (the bundled scripts assume meters).
  - R02 wire gauge picked as a placeholder; the real number comes from a caliper read on the live branch.
  - L03 is the visually-up-and-left secondary leader, matching your description. The marker placement makes this verifiable before any cut.
- **Unresolved uncertainties:** R02 caliper (drives wire gauge); whether the bend should be staged in two passes (15 deg now, +10 deg in 2-3 weeks) on a ficus that's been recently stressed.

## Digital twin sync log entry to append to the plant record

```markdown
### Digital twin sync - 2026-05-17
- Scene/file: <as reported by Blender>
- Inputs: existing Plant_ficus-benjamina-01 curves (trunk, L01-L03, R01-R02)
- Changed objects: none in canonical collections; new sim copies of L03 and R02
- Simulations created: sim_prune-L03_wire-R02-down_2026-05-17
- Exported artifacts: 99_exports/sim_prune-L03_wire-R02-down_2026-05-17.png
- Care or styling decisions: planning structural prune of L03 + downward wire on R02; not yet executed on live plant
- Follow-ups: caliper R02 to confirm wire gauge; verify L03 identity from chosen front; if approved, execute prune then wire; bite-in check 7 days after wiring
- Uncertainties: R02 diameter, whether bend should be staged, plant's recent stress state
```

## Pre-action verification (before you touch the live plant)

1. Open the screenshot and confirm the red marker is on the branch you call L03 — the upper-left secondary leader.
2. Confirm the blue anchor marker is at the R02 base, not partway up the branch.
3. Caliper R02 at the base. If it's >6 mm, step up to 1.5 mm wire and re-run Block C with `WIRE_RADIUS = 0.0015`.
4. If the plant has had any stress in the last 2-3 weeks (move, repot, leaf drop), defer the L03 removal — combining a structural cut with a wire bend on a stressed ficus pushes this from Medium to High risk.

When you've run the MCP calls I'll swap the predicted silhouette deltas above for the real numbers from Block E.
