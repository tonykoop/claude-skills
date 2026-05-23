"""Place a colored marker at a coordinate to flag a pruning decision, bud, or
other event in the digital twin.

Color semantics (must stay in sync with SKILL.md):
- red    -> cut / remove
- amber  -> watch / uncertain
- blue   -> wire / bend
- green  -> preserve / encourage
- pink   -> bud / bloom event
- teal   -> aerial root / root work guidance

Usage inside Blender:
    PLANT_ID = "ficus-benjamina-01"
    BRANCH_ID = "L02"
    SUFFIX = "A"
    LOCATION = (0.12, -0.03, 0.18)
    SEMANTIC = "cut"   # one of: cut, watch, wire, preserve, bud, aerial_root
    RADIUS = 0.005     # meters
    exec(open(r"<path>/scripts/cut_marker.py").read())
"""
import bpy

PLANT_ID = globals().get("PLANT_ID", "unknown-plant-01")
BRANCH_ID = globals().get("BRANCH_ID", "X00")
SUFFIX = globals().get("SUFFIX", "A")
LOCATION = globals().get("LOCATION", (0, 0, 0))
SEMANTIC = globals().get("SEMANTIC", "cut")
RADIUS = globals().get("RADIUS", 0.005)

# semantic -> (material_name, RGBA, marker_kind)
SEMANTIC_TABLE = {
    "cut":          ("mat_cut_red",        (1.00, 0.10, 0.10, 1.0), "cut_marker"),
    "watch":        ("mat_watch_amber",    (1.00, 0.70, 0.00, 1.0), "watch_marker"),
    "wire":         ("mat_wire_blue",      (0.10, 0.40, 1.00, 1.0), "wire_anchor"),
    "preserve":     ("mat_preserve_green", (0.10, 0.85, 0.20, 1.0), "preserve_marker"),
    "bud":          ("mat_bud_pink",       (1.00, 0.40, 0.65, 1.0), "bud_marker"),
    "aerial_root":  ("mat_aerial_teal",    (0.10, 0.80, 0.75, 1.0), "aerial_root_marker"),
}


def ensure_material(name, color):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    return mat


def place_marker(plant_id, branch_id, suffix, location, semantic, radius):
    if semantic not in SEMANTIC_TABLE:
        raise ValueError(f"Unknown semantic {semantic!r}. Allowed: {list(SEMANTIC_TABLE)}")
    mat_name, color, kind = SEMANTIC_TABLE[semantic]
    name = f"{plant_id}_{kind}_{branch_id}_{suffix}"
    obj = bpy.data.objects.get(name)
    if obj is None:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
        obj = bpy.context.active_object
        obj.name = name
    else:
        obj.location = location
    mat = ensure_material(mat_name, color)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    # Move into the markers collection if it exists.
    target_coll = bpy.data.collections.get(f"{plant_id}__04_markers")
    if target_coll is not None and obj.name not in target_coll.objects:
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        target_coll.objects.link(obj)
    obj["plant_id"] = plant_id
    obj["branch_id"] = branch_id
    obj["semantic"] = semantic
    return obj


obj = place_marker(PLANT_ID, BRANCH_ID, SUFFIX, LOCATION, SEMANTIC, RADIUS)
print(f"Marker placed: {obj.name} ({SEMANTIC})")
