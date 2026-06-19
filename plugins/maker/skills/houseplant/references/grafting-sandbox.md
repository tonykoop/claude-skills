# Virtual Grafting Sandbox (Blender boolean fusion preview)

Read this reference when the user wants to **preview** a graft — approach-graft, trunk-graft, or multi-tree fusion — before cutting into the live plant. Ficus species fuse readily, so a graft can patch a bare trunk spot or build a fused multi-trunk/braided nebari. This is a **simulation-only** workflow: it lives in `05_simulations/` and never touches the current-state twin. It extends the [`../scripts/sim_collection.py`](../scripts/sim_collection.py) pattern with [`../scripts/grafting_sim.py`](../scripts/grafting_sim.py), and pairs with [`bonsai-module.md`](bonsai-module.md) (risk) and [`aerial-roots-nebari.md`](aerial-roots-nebari.md) (fused-root nebari).

## Prerequisite gate

Grafting is an **advanced** operation. Before previewing one:

- Confirm the basic Blender pruning/wiring workflow on this twin has been validated (the user has successfully run a prune/wire sim). Do not lead a new user straight into grafting.
- Confirm plant health. Per `bonsai-module.md` and `health-diagnostics.md`, **fusion grafting on a weak or pest-flagged plant is High risk** — say so and recommend deferring.
- Confirm the species fuses well (ficus: yes; many conifers/others: poorly). State the assumption.

## Concept: boolean union + smooth blend = fused silhouette

A real graft heals over months/years as cambium layers merge and callus bridges the join. We can't simulate biology, but we can preview the **silhouette** the user is aiming at:

1. Bring the two source meshes (e.g. a scion branch and the trunk, or two trunks) into a dated sim collection.
2. Position the scion against the stock at the intended graft point.
3. Boolean-**union** them, then apply a smoothing pass (a remesh/smooth-corrective or a shrinkwrap-and-relax) across the seam to approximate callus rounding rather than a hard CSG crease.
4. Render pre- vs. post-fusion silhouettes so the user can judge the design before committing the cut.

## Workflow with `grafting_sim.py`

```python
PLANT_ID = "ficus-benjamina-01"
SCION_OBJ = "ficus-benjamina-01_branch_scionA"   # the piece being grafted in
STOCK_OBJ = "ficus-benjamina-01_trunk"           # what it fuses to
GRAFT_LABEL = "approach_trunk_patch"
BLEND_RADIUS = 0.01          # meters of seam-smoothing around the join
DATE_OVERRIDE = None          # "YYYY-MM-DD" to override today
exec(open(r"<path>/scripts/grafting_sim.py").read())
```

The script:

- Creates (or reuses) `Plant_<plant_id>__05_simulations` -> `sim_graft_<label>_<date>` via the same dated-sim convention as `sim_collection.py`.
- **Duplicates** the scion and stock into the sim (single-user copies) so the canonical twin is never mutated.
- Applies a boolean **UNION** modifier (scion onto a stock copy), then a corrective-smooth / subdivision pass limited to the seam region to approximate callus rounding.
- Stamps `graft_label`, `scion`, `stock`, `created`, and `blend_radius` on the result for cross-session recovery.
- Leaves the result selected and prints the object name; it does **not** auto-render — call the render step next.

## Pre/post comparison renders

After building the fused preview, render the comparison so the user can judge the silhouette:

1. Hide the sim, render the current-state twin from the chosen front -> "pre" image (`render_viewport_to_path` / `render_thumbnail_to_path`).
2. Show the sim's fused result, hide the separate scion/stock originals -> render "post" from the same camera/front.
3. Present them side by side and describe the **multi-year heal window**: the real join will round and blend over seasons; this preview shows the end-state silhouette, not next month's look. Make that explicit.

## Output contract

```markdown
## Grafting Sandbox Preview — <plant_id> — <YYYY-MM-DD>
- Graft type: <approach | trunk patch | multi-tree fusion>
- Sim collection: 05_simulations/sim_graft_<label>_<date> (canonical twin untouched)
- Scion: <obj>   Stock: <obj>   Seam blend: <radius> m
- Renders: pre <path>, post <path>
- Heal expectation: silhouette is the multi-year end-state; real fusion takes <range> of warm-season growth
- Risk: <Medium on a healthy vigorous ficus | High on a weak/pest-flagged plant or non-fusing species>

The `<range>` and `<risk>` are computed by
[`../scripts/graft_heal_window.py`](../scripts/graft_heal_window.py) — feed it the
graft type, species fusion-readiness (`readily`/`moderate`/`poorly`), conditions,
and plant health, and it returns a conservative multi-year heal window (months +
dates) with confidence plus the Medium/High risk verdict (High on weak/pest-flagged
plants or non-fusing species). Paste its values into the block:
- Recommendation: <proceed-after-validation | defer | adjust-position-and-re-preview>
- "Before cutting" verification: confirm scion/stock contact faces and that cambium will align on the real plant
```

## Decision rules

- **Never** mutate the current-state twin. All geometry edits happen on single-user copies inside `05_simulations/`.
- This is a design preview only — it does not assert the graft will take. Real success depends on cambium contact, binding pressure, season, and species.
- Flag High risk for weak/pest-flagged plants and for species that do not fuse readily.
- Defer grafting until the basic prune/wire twin workflow is validated for this specimen.
