"""Virtual grafting sandbox: boolean-union a scion mesh onto a stock mesh inside
a dated 05_simulations/ collection to preview the fused silhouette before
cutting into the live plant (see references/grafting-sandbox.md).

SIMULATION ONLY. This never mutates the current-state twin: the scion and stock
are DUPLICATED (single-user copies) into the sim collection, and all boolean and
smoothing work happens on those copies.

Approach:
  1. Reuse the dated-sim convention from sim_collection.py:
     Plant_<plant_id>__05_simulations -> sim_graft_<label>_<date>.
  2. Duplicate STOCK_OBJ and SCION_OBJ into the sim collection.
  3. Apply a boolean UNION (scion -> stock copy), then a corrective-smooth pass
     to approximate callus rounding across the seam instead of a hard CSG crease.
  4. Stamp metadata. Leave the fused result selected. Does NOT auto-render —
     call render_viewport_to_path / render_thumbnail_to_path next for pre/post.

Usage inside Blender:
    PLANT_ID = "ficus-benjamina-01"
    SCION_OBJ = "ficus-benjamina-01_branch_scionA"
    STOCK_OBJ = "ficus-benjamina-01_trunk"
    GRAFT_LABEL = "approach_trunk_patch"
    BLEND_RADIUS = 0.01          # seam-smoothing scale, meters
    DATE_OVERRIDE = None          # "YYYY-MM-DD" to override today
    exec(open(r"<path>/scripts/grafting_sim.py").read())
"""
import bpy
import datetime

PLANT_ID = globals().get("PLANT_ID", "unknown-plant-01")
SCION_OBJ = globals().get("SCION_OBJ")
STOCK_OBJ = globals().get("STOCK_OBJ")
GRAFT_LABEL = globals().get("GRAFT_LABEL", "graft")
BLEND_RADIUS = globals().get("BLEND_RADIUS", 0.01)
DATE_OVERRIDE = globals().get("DATE_OVERRIDE", None)


def _ensure_sim_collection(plant_id, label, date_str):
    parent = bpy.data.collections.get(f"{plant_id}__05_simulations")
    if parent is None:
        raise KeyError(f"Run scene_scaffold.py for {plant_id} first (no 05_simulations).")
    sim_name = f"sim_graft_{label}_{date_str}"
    sim = bpy.data.collections.get(sim_name) or bpy.data.collections.new(sim_name)
    if sim.name not in [c.name for c in parent.children]:
        parent.children.link(sim)
    return sim


def _duplicate_into(obj, sim_collection, new_name):
    """Make a single-user mesh copy of obj and link it into sim_collection."""
    new_mesh = obj.data.copy()
    dup = bpy.data.objects.new(new_name, new_mesh)
    dup.matrix_world = obj.matrix_world.copy()
    sim_collection.objects.link(dup)
    return dup


def grafting_sim(plant_id, scion_obj, stock_obj, label="graft",
                 blend_radius=0.01, date_str=None):
    date_str = date_str or datetime.date.today().isoformat()
    scion = bpy.data.objects.get(scion_obj)
    stock = bpy.data.objects.get(stock_obj)
    if scion is None or stock is None:
        raise KeyError(f"Need both SCION_OBJ ({scion_obj!r}) and STOCK_OBJ ({stock_obj!r}).")
    if scion.type != "MESH" or stock.type != "MESH":
        raise TypeError("Grafting preview needs MESH objects (convert curves to mesh first).")

    sim = _ensure_sim_collection(plant_id, label, date_str)

    # Single-user copies inside the sim — canonical twin stays untouched.
    stock_copy = _duplicate_into(stock, sim, f"{plant_id}_graft_{label}_{date_str}")
    scion_copy = _duplicate_into(scion, sim, f"{plant_id}_graft_scion_{label}_{date_str}")

    # Boolean UNION the scion copy onto the stock copy.
    boolean = stock_copy.modifiers.new(name="graft_union", type="BOOLEAN")
    boolean.operation = "UNION"
    boolean.object = scion_copy
    try:
        boolean.solver = "EXACT"
    except (AttributeError, TypeError):
        pass

    # Corrective smoothing to approximate callus rounding across the seam.
    smooth = stock_copy.modifiers.new(name="graft_callus_smooth", type="CORRECTIVE_SMOOTH")
    smooth.factor = min(1.0, max(0.0, blend_radius * 20))  # scale radius -> factor
    smooth.iterations = 8

    # Apply modifiers on the copy so the union is real geometry in the sim.
    ctx_obj = stock_copy
    try:
        with bpy.context.temp_override(object=ctx_obj, active_object=ctx_obj,
                                       selected_objects=[ctx_obj]):
            bpy.ops.object.modifier_apply(modifier="graft_union")
            bpy.ops.object.modifier_apply(modifier="graft_callus_smooth")
    except Exception as exc:  # fall back: leave modifiers live if apply is unavailable
        print(f"Note: could not apply modifiers automatically ({exc}); they remain live.")

    # Hide the scion copy from the fused result so renders show the union only.
    scion_copy.hide_render = True
    scion_copy.hide_viewport = True

    stock_copy["plant_id"] = plant_id
    stock_copy["graft_label"] = label
    stock_copy["scion"] = scion_obj
    stock_copy["stock"] = stock_obj
    stock_copy["blend_radius"] = blend_radius
    stock_copy["created"] = date_str
    stock_copy["sim_only"] = True

    # Select the fused result for the caller.
    for o in bpy.context.selected_objects:
        o.select_set(False)
    stock_copy.select_set(True)
    bpy.context.view_layer.objects.active = stock_copy
    return sim, stock_copy


if SCION_OBJ and STOCK_OBJ:
    _sim, _fused = grafting_sim(PLANT_ID, SCION_OBJ, STOCK_OBJ,
                                label=GRAFT_LABEL, blend_radius=BLEND_RADIUS,
                                date_str=DATE_OVERRIDE)
    print(f"Graft sim ready: {_sim.name} -> fused object {_fused.name}")
    print("Render pre (hide sim) and post (show fused) from the same front for comparison.")
else:
    print("Set PLANT_ID, SCION_OBJ, STOCK_OBJ before exec.")
