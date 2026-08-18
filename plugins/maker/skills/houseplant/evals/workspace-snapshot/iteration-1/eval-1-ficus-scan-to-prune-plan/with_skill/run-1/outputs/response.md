# Ficus benjamina 01 — scan to reversible prune + wire plan

Good capture setup. Lazy-susan + dual-height orbits + a ruler-in-frame is the cleanest of the four modes the capture pipeline describes — the melted foliage is exactly the expected failure mode and we don't care, we're keeping the trunk and primaries and replacing leaves procedurally. Plan below is fully reversible: everything happens inside `05_simulations/` until you say "commit to the physical plant."

I'll assume `plant_id = ficus-benjamina-01` (matches `assets/ficus-benjamina-starter.md`). If you've renamed it in your Obsidian record, tell me and I'll re-key.

---

## Phase 0 — Orient before touching the file

First MCP calls, in order:

1. `mcp__Blender__get_blendfile_summary_path_info` — confirm which `.blend` we're in.
2. `mcp__Blender__get_blendfile_summary_datablocks` — see if a `Plant_ficus-benjamina-01/` collection already exists from a prior session.
3. `mcp__Blender__get_objects_summary` — list current objects so I don't collide names.
4. If the root collection exists, `mcp__Blender__get_object_detail_summary` on it to read `last_synced`, `front_axis`, and `scale_units` custom properties.

I won't write anything until those four reads come back. That's the orient step from `blender-digital-twin.md`.

---

## Phase 1 — Scaffold + import the Polycam .glb

Single `mcp__Blender__execute_blender_code` call running `scripts/scene_scaffold.py` with:

```python
PLANT_ID = "ficus-benjamina-01"
SCIENTIFIC_NAME = "Ficus benjamina"
COMMON_NAME = "Weeping fig"
FRONT_AXIS = "+Y"          # we'll confirm by screenshot, can flip later
SCALE_UNITS = "meters"
SOURCE_RECORD = "<path to your Obsidian note if you have one>"
exec(open(r"<skill>/scripts/scene_scaffold.py").read())
```

That gives me the seven-child contract (`00_source_scan` through `99_exports`) and stamps the parent collection.

Then I import the Polycam `.glb` into `ficus-benjamina-01__00_source_scan`:

```python
import bpy
bpy.ops.import_scene.gltf(filepath=r"<your .glb path>")
imported = bpy.context.selected_objects
src_coll = bpy.data.collections["ficus-benjamina-01__00_source_scan"]
for o in imported:
    for c in list(o.users_collection):
        c.objects.unlink(o)
    src_coll.objects.link(o)
    o.name = f"ficus-benjamina-01_source_scan_20260517"
```

Raw scan stays parked in `00_source_scan/` forever — that's the "preserve evidence" rule.

---

## Phase 2 — Scale calibration from the ruler photo

This is the load-bearing step. Everything downstream (wire gauge math, prune projection, bite-in timing) is meaningless until the scene is in real meters.

Workflow per `capture-pipeline.md` → "Scale Calibration":

1. In the viewport, find the ruler in the scan mesh. The 0 cm mark is at the pot rim corner, the 10 cm mark is on the trunk base — both should be visible in the reconstructed geometry since they were in the same orbit.
2. Snap two empties (`_ruler_0cm` and `_ruler_10cm`) to those points using the 3D cursor. I'd ask you to do this manually in the viewport, then read the coordinates back via `get_object_detail_summary`, because eyeballing the mark in code from a `.glb` is unreliable.
3. Run `scripts/scale_from_ruler.py`:

```python
POINT_A = (<empty _ruler_0cm coords>)
POINT_B = (<empty _ruler_10cm coords>)
REAL_DISTANCE_METERS = 0.10
TARGET_COLLECTION = "Plant_ficus-benjamina-01"
APPLY_SCALE = True
exec(open(r"<skill>/scripts/scale_from_ruler.py").read())
```

That parents the whole collection to a temp pivot, scales uniformly by `0.10 / current_distance`, and bakes the transform.

Eyeball sanity check after scaling: measure pot rim diameter in Blender, compare to the real pot. If it's within ~3%, we're good. If not, the ruler marks were picked badly and we redo step 2.

Stamp `scale_units = "meters"` and `scale_confidence = "high|medium|low"` on the root collection. Verify with `mcp__Blender__get_screenshot_of_window_as_image` looking at the scaled scan next to a 10 cm reference cube.

---

## Phase 3 — Skeletonize trunk + primary branches

The Polycam mesh is evidence; we need editable curves for decisions. Hybrid recipe from `blender-digital-twin.md`:

1. Duplicate the source mesh into `02_skeleton_curves/` as `ficus-benjamina-01_scan_working`.
2. Hand-place Bezier curves through the visible trunk and each primary. Naming convention from the scene contract:
   - `ficus-benjamina-01_trunk_curve`
   - `ficus-benjamina-01_branch_L01`, `_L02`, … (left primaries as seen from chosen front)
   - `ficus-benjamina-01_branch_R01`, `_R02`, … (right primaries)
   - `ficus-benjamina-01_branch_B01` for back branch(es)
   - `ficus-benjamina-01_apex_curve` for the current leader

I'd do this with two-or-three-point Bezier curves per decision unit (one curve per branch you might want to cut or wire). Give each a `bevel_depth` matching the measured branch diameter at mid-length so it visually resembles the branch.

3. Discard the melted foliage faces from the working duplicate; keep only trunk + primaries. The scan in `00_source_scan/` is untouched.

4. In `03_procedural_geometry/`, instance simple leaf cards on the terminal portions of the branch curves via a Geometry Nodes modifier (Instance on Points along curve, ~200–400 instances per branch). Color drives off a `leaf_density` attribute we can dial down to preview the open-canopy result.

---

## Phase 4 — Front choice + apex measurement

Before any prune sim, lock the design front. From `bonsai-module.md` styling priority order, the front is the second decision (after health, which you've already assessed since you're doing structural work).

`mcp__Blender__render_thumbnail_to_path` for four orthographic-ish views (+Y, -Y, +X, -X), look at trunk movement and nebari, pick the best. Stamp `front_axis` on the root collection. Default I'll start with `+Y`; we change it if a screenshot says otherwise.

Then measure current apex height in scene units (top of `_apex_curve` minus top of nebari). Call this `H_apex_current`. Target reduction is 20% — so we're cutting back to a node at `0.80 * H_apex_current` (measured from nebari top). I'll pick the nearest outward-facing node *below* that line, not above; never above target.

---

## Phase 5 — Build the simulation collection (this is the reversibility step)

One call to `scripts/sim_collection.py`:

```python
PLANT_ID = "ficus-benjamina-01"
SCENARIO = "structural-prune-2026-05-17"
SOURCE_COLLECTIONS = ["02_skeleton_curves", "03_procedural_geometry"]
exec(open(r"<skill>/scripts/sim_collection.py").read())
```

That creates `sim_structural-prune-2026-05-17_2026-05-17` under `ficus-benjamina-01__05_simulations/` and **links** (does not copy) the skeleton curves and procedural geo into it. Current-state twin is untouched.

For the curves I actually want to cut or shorten in sim, I'll select them inside the sim collection and `Object > Make Single User > Object & Data` so edits diverge from the canonical twin. The other linked objects stay shared — that way only the diverged objects carry sim-specific state.

This is the bright line: anything inside `sim_structural-prune-2026-05-17_*` is reversible. Delete the collection and the twin reverts.

---

## Phase 6 — Plan the cuts (in sim, with markers)

Three goals from your prompt: drop apex 20%, open inner canopy for back-budding, preview the R01 wire bend. I'll place cut markers first so you can review before any curve is actually shortened.

For each candidate cut, run `scripts/cut_marker.py` with `SEMANTIC = "cut"` for removes, `"preserve"` for explicit do-not-cuts, `"watch"` for "I want to see how the plant responds before deciding." Example for the apex cut:

```python
PLANT_ID = "ficus-benjamina-01"
BRANCH_ID = "APEX"
SUFFIX = "20pct"
LOCATION = (<x,y,z at the 0.80*H_apex node>)
SEMANTIC = "cut"
RADIUS = 0.005
exec(open(r"<skill>/scripts/cut_marker.py").read())
```

Markers land in `ficus-benjamina-01__04_markers/` (the script auto-routes them) and the rest of the twin is undisturbed.

### Pruning Plan (provisional — refined after I see screenshots)

| Id | Action | Why | Risk | Verify Before Cutting | Aftercare | Follow-up |
|---|---|---|---|---|---|---|
| APEX-20pct | Cut leader back to first outward node below `0.80 * H_apex_current` | Drops apex ~20%, shifts vigor downward into inner canopy, sets up replacement leader at a lower node | Medium | Confirm the red APEX-20pct marker sits at an outward-facing node, not an inward one; confirm a viable replacement bud/branch is below the cut | Sterile cut paste over weeping latex; bright indirect light; pause fertilizer 7 days; do not move plant | Photo + viewport screenshot at 2 weeks, 4 weeks; expect back-budding in 3–4 weeks |
| INNER-A | Remove 2–3 strongest crossing/bar branches inside the canopy (specific ids assigned after I see the skeleton) | Opens light + airflow to dormant inner buds; back-budding driver | Medium | Each red marker should be at the branch base, not mid-length; confirm no marker is on a primary you want to keep for structure | Same as APEX | 3–4 weeks; mark new buds with pink `bud_marker_<date>` |
| INNER-B | Shorten 3–5 long lateral whips to the second node | Reduces apical dominance on extensions; encourages internal buds | Low | Confirm node is outward-facing | Light water check only | 2 weeks |
| R01-WIRE | Wire-bend front-right primary downward ~25° (see Phase 7) | Lowers branch line, improves visual depth, opens space above for back-budding light | Medium | Confirm wire goes around at 45° pitch, anchored at a sub-branch crotch, not floating | Wire-bite-in checks every 7–10 days during active growth | Remove wire when set; reapply if needed |

Do-not-cut list (green `preserve` markers):
- The trunk line itself below the apex cut.
- Any branch contributing to the braided aerial-root nebari at the base.
- Any healthy back branch — those are gold for visual depth.

I'll run `scripts/cut_marker.py` once per row above, then `render_thumbnail_to_path` of the sim collection alone (hide the current-state twin) for the side-by-side.

---

## Phase 7 — Wire-coil preview on R01 (~25° downward)

Estimate first, simulate second:

1. Read R01 branch diameter from the scan at the wire-application point (mid-length, just past the crotch). Use Blender's measure tool or `get_object_detail_summary` on a measurement empty.
2. Heuristic from `bonsai-module.md`: wire diameter ≈ branch diameter / 3 for ficus (warm-season cambium is fast, so I'd round *up* if the bend is meaningful). For ficus benjamina with a ~6 mm primary, that's ~2 mm wire (≈ 12 AWG aluminum or annealed copper). If the user's actual stock differs, swap `WIRE_RADIUS`.
3. Anchor: in real life this is a sub-branch crotch or the trunk itself. In sim, the helix simply runs along the branch curve; I'll annotate the anchor point with a blue `wire` semantic marker via `cut_marker.py` with `SEMANTIC = "wire"`.

Generate the coil with `scripts/wire_coil.py`:

```python
BRANCH_OBJ_NAME = "ficus-benjamina-01_branch_R01"
PLANT_ID = "ficus-benjamina-01"
BRANCH_ID = "R01"
SUFFIX = "2026-05-17"
TURNS_PER_METER = 18      # loose-ish starting wrap per skill default
WIRE_RADIUS = 0.001       # 2 mm wire => radius 1 mm; adjust to your stock
COIL_RADIUS = None        # auto from wire radius
exec(open(r"<skill>/scripts/wire_coil.py").read())
```

Then re-link the resulting `ficus-benjamina-01_wire_sim_R01_2026-05-17` curve into the sim collection (script drops it in the branch's parent collection by default per its docstring; I'll move it).

To preview the 25° bend without destroying the original R01 curve:

1. In the sim, single-user the R01 curve.
2. Edit-mode: select the bezier handles from mid-length outward and rotate around the wire anchor empty by -25° about the local horizontal axis (the axis perpendicular to the branch's outward direction at the anchor). I'd do this by setting the 3D cursor to the anchor empty, pivot point = 3D cursor, then `R Y -25` (or whichever axis matches the front-right geometry after I look at the screenshot).
3. The wire helix is bound to the curve via the helix being built from the same backbone samples — I'll regenerate the helix after the bend by re-running `wire_coil.py` so the coil follows the new shape. Alternatively, parent the wire curve to the branch curve via a Hook modifier before the bend; that's cleaner for iterating.

Custom properties stamped automatically by `wire_coil.py`: `wire_radius_m`, `turns_per_meter`, `applied_date`. I'll also stamp `target_bend_degrees = -25` and `inspection_cadence_days = 10` on the wire object so future sessions inherit context.

Render comparison: `mcp__Blender__render_viewport_to_path` of the sim with three states — pre-bend (hide wire), wire-applied-no-bend, wire-applied-bent — into `99_exports/`.

---

## Phase 8 — Side-by-side review render

Before you cut anything physical:

1. Hide `04_markers/` overlay temporarily.
2. Render `99_exports/ficus_currentstate_front_2026-05-17.png` from the current-state twin.
3. Render `99_exports/ficus_postprune_front_2026-05-17.png` from the sim collection (apex cut + inner thinning + R01 bent + procedural foliage `leaf_density` reduced ~30% to approximate the opened canopy).
4. Repeat both renders from the side view.

You eyeball the comparison. If the silhouette doesn't read the way you want, we iterate inside the sim — no physical cuts yet.

---

## Phase 9 — Commit or discard

- **Discard:** delete `sim_structural-prune-2026-05-17_2026-05-17` collection. Twin reverts.
- **Commit (physical):** keep the sim collection as the historical "intended state." Do the physical cuts using the markers as your map. After cutting, take fresh phone photos; in a future session, update `02_skeleton_curves/` to match reality (shorten the curves to where the cuts actually landed). The sim then becomes a documented before/after pair.

I will *not* mutate the current-state twin until you've made the physical cuts and confirmed. The Blender markers are recommendations, not confirmation.

---

## Digital twin sync log entry (drop this into your Obsidian note)

```markdown
### Digital twin sync - 2026-05-17
- Scene/file: <your .blend path>
- Inputs: Polycam .glb from lazy-susan + dual-orbit phone capture; ruler photo (0 cm at pot rim corner, 10 cm on trunk base)
- Changed objects: Plant_ficus-benjamina-01/ scaffold + all child collections; ficus-benjamina-01_source_scan_20260517 imported to 00_source_scan; trunk and primary branch curves built in 02_skeleton_curves; procedural foliage in 03_procedural_geometry; cut/preserve/wire markers in 04_markers
- Simulations created: sim_structural-prune-2026-05-17_2026-05-17 (apex -20%, inner-canopy thinning, R01 wire @ -25°)
- Exported artifacts: 99_exports/ficus_currentstate_front_2026-05-17.png, ficus_postprune_front_2026-05-17.png (+ side views)
- Care or styling decisions: drop apex ~20% to first outward node below 0.80*H_apex; thin 2-3 inner crossings; wire-bend front-right primary R01 down ~25°
- Follow-ups:
    - Physical cuts pending user confirmation of sim
    - Wire bite-in inspection every 7-10 days during active growth
    - Photo review at 2 weeks and 4 weeks; expect back-budding in 3-4 weeks
- Uncertainties: branch ids L01/L02/R01/R02 provisional until skeleton screenshot is approved; wire gauge assumes ~6 mm R01 diameter — confirm by measuring on the scaled scan; front_axis defaulted to +Y, may flip after ortho-view review
```

---

## What I need from you to run this for real

1. The path to the Polycam `.glb`.
2. The path to the `.blend` you want to use (or "make a new one").
3. After Phase 2 step 2, the coordinates of the two ruler-mark empties (I'll guide you to set them; you read them back to me).
4. Confirmation of the design front after I send the four ortho renders.
5. Your wire stock (gauges/material on hand) so I can match `WIRE_RADIUS` to reality.

Once I have 1–2, I'll run Phases 0–3 and send a screenshot for you to mark the ruler endpoints. Everything from there is reversible until you make a physical cut.
