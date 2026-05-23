"""Calibrate scene units from a ruler segment visible in the imported scan.

Approach: pick two points on the imported scan that correspond to known ruler
markings (e.g. the 0 cm and 10 cm marks). Pass their current Blender-space
coordinates plus the real-world distance between them. The script computes the
scale factor and applies it uniformly to the target object/collection.

The caller is responsible for placing the two endpoints accurately (the
suggested workflow is to snap two empties to those marks in the viewport, then
read their coordinates).

Usage inside Blender:
    POINT_A = (0.123, -0.045, 0.011)
    POINT_B = (0.198, -0.045, 0.011)
    REAL_DISTANCE_METERS = 0.10  # 10 cm
    TARGET_COLLECTION = "Plant_ficus-benjamina-01"  # collection to scale
    exec(open(r"<path>/scripts/scale_from_ruler.py").read())

`compute_scale_factor` is the pure-math helper and is importable without
Blender for testing.
"""
from __future__ import annotations
import math


def compute_scale_factor(a, b, real_distance: float) -> float:
    """Return the uniform scale factor that maps |b-a| (current Blender units)
    onto real_distance (meters). Pure-math; importable without bpy."""
    ax, ay, az = a
    bx, by, bz = b
    current = math.sqrt((bx - ax) ** 2 + (by - ay) ** 2 + (bz - az) ** 2)
    if current == 0:
        raise ValueError("Endpoint A and B are coincident; pick distinct ruler marks.")
    return real_distance / current


try:
    import bpy
    from mathutils import Vector
    _HAVE_BPY = True
except ImportError:
    _HAVE_BPY = False

POINT_A = globals().get("POINT_A")  # tuple of 3 floats in current Blender units
POINT_B = globals().get("POINT_B")
REAL_DISTANCE_METERS = globals().get("REAL_DISTANCE_METERS")
TARGET_COLLECTION = globals().get("TARGET_COLLECTION")
APPLY_SCALE = globals().get("APPLY_SCALE", True)  # bake the scale into mesh data


def scale_collection_uniform(coll_name, factor, apply=True):
    coll = bpy.data.collections.get(coll_name)
    if coll is None:
        raise KeyError(f"Collection {coll_name!r} not found.")
    # Create an empty as a pivot so we don't depend on object origins.
    pivot_name = f"_scale_pivot_{coll_name}"
    pivot = bpy.data.objects.get(pivot_name) or bpy.data.objects.new(pivot_name, None)
    if pivot.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(pivot)
    pivot.location = (0, 0, 0)
    # Parent every top-level object in the collection to the pivot temporarily.
    targets = [o for o in coll.all_objects if o.parent is None]
    originals = {}
    for o in targets:
        originals[o.name] = o.matrix_world.copy()
        o.parent = pivot
        o.matrix_parent_inverse = pivot.matrix_world.inverted()
    pivot.scale = (factor, factor, factor)
    bpy.context.view_layer.update()
    if apply:
        # Bake transforms by clearing the parent while keeping transform.
        for o in targets:
            world = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = world
        # Remove pivot.
        bpy.data.objects.remove(pivot, do_unlink=True)
    return factor


if _HAVE_BPY and POINT_A is not None and POINT_B is not None and REAL_DISTANCE_METERS and TARGET_COLLECTION:
    factor = compute_scale_factor(POINT_A, POINT_B, REAL_DISTANCE_METERS)
    print(f"Scale factor: {factor:.6f}")
    scale_collection_uniform(TARGET_COLLECTION, factor, apply=APPLY_SCALE)
    print(f"Applied to {TARGET_COLLECTION}.")
elif _HAVE_BPY:
    print("Set POINT_A, POINT_B, REAL_DISTANCE_METERS, TARGET_COLLECTION before exec.")
