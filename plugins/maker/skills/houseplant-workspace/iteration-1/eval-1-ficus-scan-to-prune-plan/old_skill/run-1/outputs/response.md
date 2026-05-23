# Ficus benjamina-01 — Scan-to-Prune-Plan, 2026-05-17

Good capture method, Tony — the fixed-tripod-on-lazy-susan with two height passes is exactly the right Polycam setup for a trunk-and-branch reconstruction, and the ruler photo gives us a clean metric anchor. The "melted blob" foliage is expected and fine; per `references/blender-digital-twin.md` we keep the trunk/root scan as evidence and replace foliage procedurally only where useful.

Below is the full plan: routing, scene contract, Blender MCP call sequence with pseudocode, the structural prune, and the wire simulation for the front-right primary — all reversible, all in `05_simulations/` until you greenlight any cut.

---

## 1. Plant record (collection-records-and-care.md)

Treating this as a sync session against `ficus-benjamina-01`. If you don't have that record yet, here's the minimal stub I'll write/append; otherwise I'll merge into the existing one.

```yaml
---
plant_id: ficus-benjamina-01
common_name: Weeping fig (bonsai-in-training)
scientific_name: Ficus benjamina
location: <fill — indoor bench? south window?>
indoor_outdoor: indoor (assumed)
pot:
substrate:
last_repotted:
last_pruned:
last_wired:
last_fertilized:
digital_twin: //Blender/ficus-benjamina-01.blend
media_folder: //media/ficus-benjamina-01/
health_flags: []
---
```

Open questions I need from you to firm the record up (none are blockers for the Blender work):

- Last repot date and substrate type (drives pruning risk).
- Is the plant in active growth right now? (Mid-May 2026 in your hemisphere — I'm assuming northern, warm-season, healthy and actively pushing. Tell me if not.)
- Wire gauges and material you have on hand (I'll size the coil suggestion now and you can confirm).

---

## 2. Routing decision

- **Blender digital twin work** → `references/blender-digital-twin.md` (primary).
- **Pruning + wire plan** → `references/bonsai-module.md`.
- **Record + reminders** → `references/collection-records-and-care.md`.

No handoff to `reverse-engineer` or `makerspace` — we have direct geometry from Polycam, not sparse photos of an unknown object.

---

## 3. Blender scene contract

Per `blender-digital-twin.md` scene contract, I'll build:

```
Plant_ficus-benjamina-01/
  00_source_scan/
    ficus-benjamina-01_source_scan_20260517         (raw GLB import, locked)
    ficus-benjamina-01_trunk_mesh_cleaned           (duplicate, decimated, foliage-blob removed)
  01_reference_photos/
    ficus-benjamina-01_ruler_photo_20260517         (image-empty for scale check)
    ficus-benjamina-01_front_photo_20260517         (image-empty, oriented to chosen front)
  02_skeleton_curves/
    ficus-benjamina-01_trunk_curve
    ficus-benjamina-01_branch_FR01                  (front-right primary — wire target)
    ficus-benjamina-01_branch_FL01
    ficus-benjamina-01_branch_B01                   (back branch)
    ficus-benjamina-01_branch_L02, R02, ...         (secondaries, as resolved)
  03_procedural_geometry/
    ficus-benjamina-01_foliage_proc                 (instanced leaves on terminal curves)
  04_markers/
    ficus-benjamina-01_cut_marker_APEX_A            (red — apex reduction)
    ficus-benjamina-01_cut_marker_INNER_<n>         (red — inner-canopy thinning)
    ficus-benjamina-01_keep_marker_<n>              (green — do not cut)
    ficus-benjamina-01_wire_anchor_FR01             (blue)
  05_simulations/
    sim_prune_apex_2026-05-17/                      (apex −20% ghost geometry)
    sim_prune_inner_canopy_2026-05-17/              (inner thinning ghost)
    sim_wire_FR01_down_25deg_2026-05-17/            (bent duplicate of FR01)
  99_exports/
```

Custom properties on `Plant_ficus-benjamina-01` collection:

```python
plant_id        = "ficus-benjamina-01"
scientific_name = "Ficus benjamina"
common_name     = "Weeping fig"
source_record   = "obsidian://ficus-benjamina-01"   # or your spreadsheet row
capture_date    = "2026-05-17"
scale_units     = "cm"
front_axis      = "+Y"                              # facing camera in default view
confidence      = "scale: high; branch IDs: medium until you confirm"
last_synced     = "2026-05-17"
notes           = "Polycam GLB, foliage noisy and replaced procedurally"
```

---

## 4. Blender MCP call sequence

Blender MCP isn't connected in this sandbox, so this is the call plan I'd execute. Each `execute_blender_code` block is idempotent — it looks up by name before creating.

### Step 4.1 — Inspect first, don't assume

**Tool:** `mcp__Blender__get_blendfile_summary_datablocks` then `mcp__Blender__get_objects_summary`

Reason: per the reference, "use `bpy` to inspect before writing; do not assume object names from memory." If the `.blend` is empty I scaffold; if it already has a `Plant_ficus-benjamina-01` collection I merge.

### Step 4.2 — Scaffold collections + custom properties

**Tool:** `mcp__Blender__execute_blender_code`

```python
import bpy

PLANT_ID = "ficus-benjamina-01"
PARENT = f"Plant_{PLANT_ID}"
SUBS = [
    "00_source_scan", "01_reference_photos", "02_skeleton_curves",
    "03_procedural_geometry", "04_markers", "05_simulations", "99_exports",
]

def ensure_collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col

parent_col = ensure_collection(PARENT)
for s in SUBS:
    ensure_collection(s, parent_col)

props = {
    "plant_id": PLANT_ID,
    "scientific_name": "Ficus benjamina",
    "common_name": "Weeping fig",
    "capture_date": "2026-05-17",
    "scale_units": "cm",
    "front_axis": "+Y",
    "confidence": "scale:high; branch_ids:medium",
    "last_synced": "2026-05-17",
}
for k, v in props.items():
    parent_col[k] = v

# Units → centimeters so 1 BU = 1 cm matches the ruler.
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 0.01
bpy.context.scene.unit_settings.length_unit = 'CENTIMETERS'
```

### Step 4.3 — Import the GLB into `00_source_scan/` and lock it

**Tool:** `mcp__Blender__execute_blender_code`

```python
import bpy, os

GLB_PATH = r"<path you'll give me>/ficus-benjamina-01_polycam_20260517.glb"
target = bpy.data.collections["00_source_scan"]

before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=GLB_PATH)
new_objs = [o for o in bpy.data.objects if o not in before]

# Move imports under 00_source_scan, rename, lock transforms
for i, o in enumerate(new_objs):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    target.objects.link(o)
    o.name = f"ficus-benjamina-01_source_scan_20260517" + (f"_{i:02d}" if i else "")
    o.hide_select = True   # treat as evidence — protect from accidental edits
    o.lock_location = o.lock_rotation = o.lock_scale = (True, True, True)
```

### Step 4.4 — Set scale from the ruler photo

You said: 0 cm mark = one corner of the pot rim, 10 cm mark = a known point on the trunk base. In the viewport I'll:

1. Click those two points on the source scan to capture world-space coords.
2. Compute the current distance; the desired distance is 10.0 cm.
3. Scale the source scan (and any descendants) by `10.0 / current_distance` about the pot-rim corner.

**Tool:** `mcp__Blender__execute_blender_code`

```python
import bpy
from mathutils import Vector

# You'll paste these in after I show you the two points in the viewport,
# or I'll prompt via MCP screenshot + click confirmation.
P_RIM_CORNER = Vector((x0, y0, z0))   # 0 cm
P_TRUNK_BASE = Vector((x1, y1, z1))   # 10 cm
TARGET_CM = 10.0

current = (P_TRUNK_BASE - P_RIM_CORNER).length
scale_factor = TARGET_CM / current

# Apply about P_RIM_CORNER so the rim corner stays put
src = bpy.data.collections["00_source_scan"]
for o in src.objects:
    o.hide_select = False
    o.lock_scale = (False, False, False)
    o.location = P_RIM_CORNER + (o.location - P_RIM_CORNER) * scale_factor
    o.scale = tuple(s * scale_factor for s in o.scale)
    o.lock_scale = (True, True, True)
    o.hide_select = True

bpy.data.collections["Plant_ficus-benjamina-01"]["scale_calibrated"] = True
bpy.data.collections["Plant_ficus-benjamina-01"]["scale_factor_applied"] = scale_factor
```

Risk note: Polycam's exported scale is sometimes correct already. We'll check `current` against 10 cm before scaling — if it's already within ~3% we just lock it and record `scale_factor_applied = 1.0`.

### Step 4.5 — Orient + define the front

`mcp__Blender__jump_to_view3d_object_by_name` to frame the trunk, then a small operator that rotates the collection so the chosen front faces `+Y` and the trunk base sits at world origin. Store `front_axis = "+Y"` on the parent collection.

### Step 4.6 — Build the branch skeleton (trunk + primaries as curves)

Per the reference: "one curve per meaningful decision unit." I'll trace these by clicking nodes along the scan in front view:

- `ficus-benjamina-01_trunk_curve` (base → apex)
- `ficus-benjamina-01_branch_FR01` (front-right primary — your wire target)
- `ficus-benjamina-01_branch_FL01`
- `ficus-benjamina-01_branch_B01` (back branch for depth)
- Whatever secondaries are visible in the GLB

**Tool:** `mcp__Blender__execute_blender_code`

```python
import bpy

def make_branch_curve(name, points, bevel_depth=0.15):
    if name in bpy.data.objects:
        return bpy.data.objects[name]
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = bevel_depth   # cm — rough visual thickness
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for bp, (co, handle_len) in zip(spline.bezier_points, points):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    bpy.data.collections["02_skeleton_curves"].objects.link(obj)
    obj["branch_id"] = name.split("_")[-1]
    obj["diameter_cm_estimate"] = bevel_depth * 2
    return obj

# Placeholder points — I'll click these along the source scan
make_branch_curve("ficus-benjamina-01_trunk_curve",
                  [((0,0,0),0), ((0.2,0,8),0), ((0.4,0,18),0), ((0.6,0,26),0)],
                  bevel_depth=1.1)   # ~22 mm trunk
make_branch_curve("ficus-benjamina-01_branch_FR01",
                  [((0.4,0,18),0), ((4,-3,19),0), ((8,-5,18),0), ((12,-7,17),0)],
                  bevel_depth=0.4)   # ~8 mm — drives wire gauge
```

Custom property `branch_id` on each curve keeps IDs stable for future plans, exactly per the reference.

### Step 4.7 — Procedural foliage replacement

Hide the foliage blob on the scan duplicate, then instance a small leaf mesh along the terminal portions of each branch curve via a Geometry Nodes "Distribute Points on Curve → Instance on Points" setup. Material: matte green, low-poly. This isn't botanically accurate — it's a silhouette aid for the prune simulation.

---

## 5. Pruning plan (bonsai-module.md)

**Specimen:** `ficus-benjamina-01` — Ficus benjamina, multi-year training, structural prune.
**Assumptions (state these aloud, per Decision Rules):**
- Healthy, in active warm-season growth (mid-May, indoor northern hemisphere assumed).
- Not recently repotted (>6 weeks) — confirm before cutting.
- You're styling toward an informal upright; the apex is currently the tallest leader and there's congestion in the inner canopy.

**Goals you set:**
1. Drop apex by ~20% of current height.
2. Open inner canopy for back-budding.
3. Preview wiring on front-right primary (FR01) to lower it ~25°.

### 5.1 Pruning Plan table

| Id | Action | Why | Risk | Verify Before Cutting | Aftercare | Follow-up |
|---|---|---|---|---|---|---|
| APEX-A | Reduce apex by ~20% of measured trunk-to-apex height, cutting back to the next viable outward/forward-facing node | Lowers profile, shifts vigor to lower branches, encourages back-budding | **Medium** | In Blender, confirm the red `cut_marker_APEX_A` lands on a node, not mid-internode. Physically: that node has a visible bud or leaf scar and the cut leaves at least 2 leaves on the leader below it | Bright stable light, normal moisture, hold fertilizer 7-10 days, seal large cuts with cut paste if >6 mm diameter | Photograph 3 weeks out; expect back-budding 3-6 weeks at warm-season ficus rates |
| INNER-1 | Remove inward-growing twigs in upper-third interior (mark each in Blender as `cut_marker_INNER_<n>`) | Opens light to inner buds for back-budding; reduces fungal/airflow risk | Low | Confirm each marked twig points *toward* the trunk centerline from the chosen front, not away | Same | 3 weeks |
| INNER-2 | Remove any bar branches (two opposite branches at the same node) by keeping the stronger one | Avoids reverse-taper and visual symmetry flaws | Medium | Confirm the pair is truly at the same node — Polycam can fuse nearby nodes; check on the physical plant before cutting | Same | 3 weeks |
| INNER-3 | Shorten downward-hanging weak shoots to 2 nodes | Eliminates sap-draining weak growth, redirects vigor upward and outward | Low | Confirm the shoot is genuinely weak (thin, pale, few leaves) and not a planned cascade element | Same | 3 weeks |
| FR01-W | **No cut.** Wire-and-bend simulation only — see §6 | Bring front-right primary down ~25° for visual weight and depth | Medium (if executed) | See §6 verification | See §6 | Bite-in checks every 7-10 days |

**Do-not-cut list (green markers):**

- Trunk leader below APEX-A.
- Back branch `B01` — provides depth; if anything, encourage it.
- Any visible aerial roots forming on trunk — mark teal per the bonsai reference; ficus rewards keeping these.
- Any branch with a fresh terminal bud cluster you've been counting on for next flush.

### 5.2 Apex-reduction simulation

**Tool:** `mcp__Blender__execute_blender_code`

```python
import bpy
from mathutils import Vector

trunk = bpy.data.objects["ficus-benjamina-01_trunk_curve"]
spline = trunk.data.splines[0]

# Apex point = last bezier point. Drop it by 20% of trunk vertical extent.
pts = [bp.co.copy() for bp in spline.bezier_points]
base_z = pts[0].z
apex_z = pts[-1].z
new_apex_z = base_z + 0.8 * (apex_z - base_z)

# Build a *simulation duplicate*, do not mutate the current-state trunk
sim_col = bpy.data.collections.get("sim_prune_apex_2026-05-17") \
          or bpy.data.collections.new("sim_prune_apex_2026-05-17")
if sim_col.name not in [c.name for c in bpy.data.collections["05_simulations"].children]:
    bpy.data.collections["05_simulations"].children.link(sim_col)

sim_trunk_data = trunk.data.copy()
sim_trunk = bpy.data.objects.new("ficus-benjamina-01_trunk_curve__sim_apex_-20pct", sim_trunk_data)
sim_col.objects.link(sim_trunk)

sim_spline = sim_trunk_data.splines[0]
# Walk from apex back until we find the first bezier point at or below new_apex_z, drop the rest
keep = [bp for bp in sim_spline.bezier_points if bp.co.z <= new_apex_z]
# (rebuild spline with `keep` — bezier rebuild snippet omitted for brevity)

# Place a red cut marker at the new apex
marker = bpy.data.objects.new("ficus-benjamina-01_cut_marker_APEX_A", None)
marker.empty_display_type = 'SPHERE'
marker.empty_display_size = 0.5
marker.location = (pts[-1].x, pts[-1].y, new_apex_z)
marker["risk"] = "Medium"
marker["action"] = "apex reduction -20%"
bpy.data.collections["04_markers"].objects.link(marker)
```

Then render a front-view comparison: hide the original trunk curve, show the simulation duplicate, screenshot via `mcp__Blender__render_viewport_to_path` → `99_exports/sim_prune_apex_2026-05-17_front.png`. Repeat for side view.

### 5.3 Inner-canopy thinning simulation

For each inner twig you and I tag in the viewport, place a red empty (`cut_marker_INNER_<n>`) and add a "ghost" duplicate of the twig curve with material set to 20% red, 50% transparent, inside `sim_prune_inner_canopy_2026-05-17/`. Originals stay untouched. Toggle the sim collection on/off to A/B the canopy openness.

---

## 6. Wire-and-bend simulation — FR01 down 25°

`bonsai-module.md` says: wire only with a clear design goal, estimate gauge ~⅓ of branch diameter, plan anchor + coil + bend amount + bite-in cadence.

**Plan inputs:**
- Branch: `ficus-benjamina-01_branch_FR01`
- Estimated diameter at base: ~8 mm (will be re-measured from the calibrated scan)
- Target bend: −25° at the base, easing along the branch (don't kink the tip)
- Wire gauge estimate: **2.5 mm aluminum** (≈⅓ of 8 mm; bump to 3 mm if the branch is more lignified than it looks)
- Coil direction: clockwise viewed from anchor → tip when bending the branch *downward on the right side* (this is the convention that tightens, not loosens, under the bend)
- Anchor: wrap one full turn around the trunk just below the FR01 takeoff; if FR01 has a sibling branch nearby, anchor across both as a paired wire instead.

### 6.1 Blender simulation

**Tool:** `mcp__Blender__execute_blender_code`

```python
import bpy, math
from mathutils import Vector, Matrix

src = bpy.data.objects["ficus-benjamina-01_branch_FR01"]
sim_col = bpy.data.collections.new("sim_wire_FR01_down_25deg_2026-05-17")
bpy.data.collections["05_simulations"].children.link(sim_col)

# 1) Duplicate the branch curve — bend the duplicate, not the original
sim_branch_data = src.data.copy()
sim_branch = bpy.data.objects.new("ficus-benjamina-01_branch_FR01__sim_bend_-25deg", sim_branch_data)
sim_col.objects.link(sim_branch)

# 2) Apply a graded rotation: 0° at the anchor (first point), full -25° at the tip
spline = sim_branch_data.splines[0]
pts = spline.bezier_points
anchor = pts[0].co.copy()
n = len(pts) - 1
axis = Vector((1, 0, 0))   # bend axis — roughly tangent to trunk at takeoff; adjust after inspection

for i, bp in enumerate(pts):
    t = i / n
    angle = math.radians(-25.0) * t   # ease-in linear; swap for smoothstep if needed
    rel = bp.co - anchor
    bp.co = anchor + (Matrix.Rotation(angle, 4, axis) @ rel)
    bp.handle_left  = anchor + (Matrix.Rotation(angle, 4, axis) @ (bp.handle_left  - anchor))
    bp.handle_right = anchor + (Matrix.Rotation(angle, 4, axis) @ (bp.handle_right - anchor))

# 3) Build a blue helical wire curve along the bent branch
wire = bpy.data.curves.new("ficus-benjamina-01_wire_sim_FR01_20260517", 'CURVE')
wire.dimensions = '3D'
wire.bevel_depth = 0.125   # 2.5 mm wire => 1.25 mm radius
helix_spline = wire.splines.new('POLY')
samples = 60
turns = 6   # ~one wrap per 1.5-2 cm along an 8-10 cm branch
helix_pts = []
for i in range(samples + 1):
    t = i / samples
    # Sample along the bent branch (approximation — full surface eval would use evaluated_get)
    p = pts[0].co.lerp(pts[-1].co, t)
    # Add a perpendicular offset that rotates with t
    angle = turns * 2 * math.pi * t
    radius = 0.5   # 5 mm — branch radius + wire radius
    offset = Vector((math.cos(angle) * radius, math.sin(angle) * radius, 0))
    helix_pts.append(p + offset)
helix_spline.points.add(len(helix_pts) - 1)
for sp, p in zip(helix_spline.points, helix_pts):
    sp.co = (*p, 1)
wire_obj = bpy.data.objects.new(wire.name, wire)
sim_col.objects.link(wire_obj)

# Blue material per SKILL.md color semantics
mat = bpy.data.materials.get("mat_wire_blue") or bpy.data.materials.new("mat_wire_blue")
mat.diffuse_color = (0.15, 0.45, 1.0, 1.0)
wire_obj.data.materials.append(mat)

# 4) Metadata on the simulation
sim_col["target_branch"] = "FR01"
sim_col["bend_deg"]      = -25.0
sim_col["wire_gauge_mm"] = 2.5
sim_col["wire_material"] = "aluminum"
sim_col["applied_date"]  = ""   # blank until you physically apply
sim_col["inspection_interval_days"] = 10
sim_col["removal_window_weeks"] = "6-10 (sooner if bite-in visible)"
```

This gives you a viewport you can A/B by toggling `sim_wire_FR01_down_25deg_2026-05-17` on/off against the untouched original branch curve. Render front + top-down via `mcp__Blender__render_viewport_to_path` for the comparison stills.

### 6.2 Wire plan summary

| Field | Value |
|---|---|
| Target branch | FR01 (front-right primary) |
| Bend goal | −25° at base, eased to tip |
| Wire material | Aluminum |
| Gauge estimate | 2.5 mm (confirm against branch caliper; 3 mm if it resists) |
| Anchor | One full wrap around trunk below takeoff, or paired with adjacent primary if applicable |
| Coil direction | CW viewed anchor→tip (tightens under the downward bend) |
| Staging | Single stage if the branch flexes freely to ~30° by hand; otherwise stage at −15° now, −25° in 3-4 weeks |
| Risk | Medium |
| Verify before bending | Branch flexes without audible cracking; bark is supple, not papery; node at the base isn't already a healed wound |
| Bite-in inspections | Every 7-10 days in active growth |
| Removal window | 6-10 weeks, **sooner** at first sign of bark swelling over the wire |

---

## 7. Exports + sync log

After running the above I'd produce, via `mcp__Blender__render_viewport_to_path`:

- `99_exports/ficus-benjamina-01_current_state_front_20260517.png`
- `99_exports/sim_prune_apex_2026-05-17_front.png` + `_side.png`
- `99_exports/sim_prune_inner_canopy_2026-05-17_front.png`
- `99_exports/sim_wire_FR01_down_25deg_2026-05-17_front.png` + `_top.png`
- `99_exports/ficus-benjamina-01_combined_plan_20260517.png` (all sims toggled on)
- `99_exports/ficus-benjamina-01_digital_twin_20260517.glb` (full export for archive)

### Digital twin sync — 2026-05-17

- **Scene/file:** `//Blender/ficus-benjamina-01.blend`
- **Inputs:** Polycam GLB (lazy-susan + dual-height orbit, 2026-05-17); ruler photo (0 cm = pot rim corner, 10 cm = trunk base point)
- **Changed objects:** scaffolded `Plant_ficus-benjamina-01` hierarchy; imported + locked source scan; created trunk + FR01/FL01/B01 skeleton curves; added APEX-A red cut marker + inner-canopy red markers; added blue wire sim on FR01
- **Simulations created:** `sim_prune_apex_2026-05-17`, `sim_prune_inner_canopy_2026-05-17`, `sim_wire_FR01_down_25deg_2026-05-17` — all in `05_simulations/`, current-state twin untouched
- **Exported artifacts:** see §7 list above
- **Care or styling decisions:** none physical yet — sim only
- **Follow-ups:** confirm branch IDs on the physical plant; confirm last-repot date; confirm wire gauges on hand
- **Uncertainties:** branch ID confidence is medium (Polycam foliage blob obscured some takeoffs); scale confidence high pending ruler-point click verification; species-specific bite-in rate assumed typical-vigorous warm-season ficus

---

## 8. Calendar-ready reminders

```markdown
### Reminder
- Title: Ficus-01 — back-bud check after structural prune
- Plant: ficus-benjamina-01
- Date/time: 2026-06-07 (3 weeks after planned cut date)
- Recurrence: one-off, then re-evaluate
- Priority: Medium
- Trigger/evidence: APEX-A apex reduction + inner-canopy thinning on 2026-05-17 (if executed)
- Checklist:
  - Photograph from the same front angle as the 05-17 capture
  - Count new buds on the upper-third interior
  - Compare canopy openness to sim render
  - Note any dieback near APEX-A cut
- Done condition: photo logged + bud count entered in record
```

```markdown
### Reminder
- Title: Ficus-01 — FR01 wire bite-in check
- Plant: ficus-benjamina-01
- Date/time: starts 7 days after wire application
- Recurrence: every 7-10 days until removal
- Priority: High (wire scarring is fast on vigorous ficus)
- Trigger/evidence: 2.5 mm aluminum wire on FR01, −25° bend
- Checklist:
  - Inspect bark above and below each coil for swelling
  - If swelling visible, remove wire immediately and re-wire only if branch hasn't set
  - Confirm bend has held (or note spring-back angle)
- Done condition: wire removed cleanly, bend set, no scarring
```

```markdown
### Reminder
- Title: Ficus-01 — re-scan for digital twin update
- Plant: ficus-benjamina-01
- Date/time: 2026-08-17 (3 months out, or after FR01 wire comes off — whichever is later)
- Recurrence: quarterly during training
- Priority: Low
- Trigger/evidence: structural prune + wire applied 2026-05-17
- Checklist:
  - Same lazy-susan + dual-height orbit method
  - Same ruler placement (0 = pot rim corner, 10 = trunk base point)
  - Same front orientation
  - Re-run Polycam, drop GLB into Blender, version the scene
- Done condition: new source_scan_YYYYMMDD locked and old one archived
```

I'll only create live calendar events if you ask — drafts only, per the reference.

---

## 9. Care checklist — `ficus-benjamina-01` — 2026-05-17 (post-prune, if executed)

- Place in stable bright indirect light; no relocation for 2 weeks.
- Check soil moisture at root depth daily for the first week; water on the dry side of normal.
- Hold fertilizer for 7-10 days, then resume at half strength for the first feed.
- Inspect cut sites for clean callusing; seal any cut >6 mm with cut paste if not already done.
- Inspect FR01 wire coils every 7-10 days (see reminder).
- Watch upper-third interior for back-budding starting week 3.
- Log any aerial-root tips with a teal marker in Blender and a dated photo.
- Re-capture front photo from the same angle weekly for the first month.

---

## 10. What I need from you to actually run this

1. **GLB file path** (and the ruler photo path) — drop them in the chat and I'll wire them into the import step.
2. **Confirm scale anchors** — I'll show you the source scan and you click the pot-rim-corner and trunk-base points, or paste coords.
3. **Confirm front** — I'll render four candidate fronts; you pick.
4. **Confirm branch IDs** — I'll annotate the front render with FR01/FL01/B01/etc. labels; you sign off before any cut markers are treated as physical guidance.
5. **Confirm wire gauge** — what's actually in your wire kit?
6. **Last repot date + current health** — to keep risk levels honest.

Nothing physical happens until those five are confirmed and you explicitly greenlight the cut. Everything above is reversible: simulations live in `05_simulations/`, the source scan is locked and hide-selected, and the current-state skeleton curves stay untouched until you tell me to commit a simulation back to the current state.
