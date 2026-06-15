"""Trace a guided aerial-root path from a branch tip down to a substrate landing
point in the digital twin.

Aerial roots hang and droop rather than running in a straight line, so the path
is a gentle catenary-like sag between START (current tip) and END (target landing
point). The curve is teal (aerial-root color semantic) and lands in the plant's
04_markers collection with lifecycle state stamped for cross-session recovery
(see references/aerial-roots-nebari.md).

The pure-math helper `droop_path_points` is importable without bpy for testing.

Usage inside Blender:
    PLANT_ID = "ficus-benjamina-01"
    ROOT_ID = "aerialL01"
    START = (0.03, 0.06, 0.30)     # current aerial-root tip
    END = (0.01, 0.02, 0.00)       # target landing point on substrate
    STATE = "guided"               # lifecycle: tip_promising|guided|reached_soil|thickening|fused
    DROOP = None                   # extra sag depth in meters; None => auto from span
    SAMPLES = 40
    exec(open(r"<path>/scripts/aerial_root_trace.py").read())
"""
from __future__ import annotations
import math


def droop_path_points(start, end, droop=None, samples=40):
    """Return a list of (x, y, z) points tracing a drooping path from start to
    end. Pure math; importable without bpy.

    The horizontal (x, y) interpolates linearly start->end; the z is the linear
    interpolation minus a parabolic sag that is zero at both endpoints and
    maximal at the midpoint, so the root hangs before reaching the substrate.

    Args:
        start: (x, y, z) tip position.
        end: (x, y, z) landing position.
        droop: extra sag depth in meters at midpoint. None => auto (a fraction
            of the horizontal span, clamped to a sensible range).
        samples: number of points along the path (>= 2).

    Returns:
        list of (x, y, z) tuples.
    """
    if samples < 2:
        raise ValueError("Need at least 2 samples.")
    sx, sy, sz = start
    ex, ey, ez = end
    if droop is None:
        span = math.sqrt((ex - sx) ** 2 + (ey - sy) ** 2)
        # Sag a fraction of the horizontal span, clamped so tiny spans still
        # droop a little and large spans don't sag absurdly.
        droop = min(max(span * 0.35, 0.01), 0.20)
    pts = []
    for i in range(samples):
        t = i / (samples - 1)
        x = sx + (ex - sx) * t
        y = sy + (ey - sy) * t
        z_lin = sz + (ez - sz) * t
        sag = droop * (4 * t * (1 - t))  # parabola: 0 at ends, droop at t=0.5
        pts.append((x, y, z_lin - sag))
    return pts


try:
    import bpy
    _HAVE_BPY = True
except ImportError:
    _HAVE_BPY = False

PLANT_ID = globals().get("PLANT_ID", "unknown-plant-01")
ROOT_ID = globals().get("ROOT_ID", "aerial01")
START = globals().get("START", (0, 0, 0.3))
END = globals().get("END", (0, 0, 0.0))
STATE = globals().get("STATE", "guided")
DROOP = globals().get("DROOP", None)
SAMPLES = globals().get("SAMPLES", 40)

VALID_STATES = {"tip_promising", "guided", "reached_soil", "thickening", "fused"}


def _ensure_teal_material():
    name = "mat_aerial_teal"
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.diffuse_color = (0.10, 0.80, 0.75, 1.0)
    return mat


def aerial_root_trace(plant_id, root_id, start, end, state="guided",
                      droop=None, samples=40):
    import datetime
    if state not in VALID_STATES:
        raise ValueError(f"Unknown state {state!r}. Allowed: {sorted(VALID_STATES)}")
    pts = droop_path_points(start, end, droop=droop, samples=samples)
    name = f"{plant_id}_aerial_root_trace_{root_id}"
    curve_data = bpy.data.curves.get(name)
    if curve_data is None:
        curve_data = bpy.data.curves.new(name, type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = 0.0015  # thin visible strand
    curve_data.splines.clear()
    spl = curve_data.splines.new("POLY")
    spl.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        spl.points[i].co = (p[0], p[1], p[2], 1.0)
    obj = bpy.data.objects.get(name)
    if obj is None:
        obj = bpy.data.objects.new(name, curve_data)
    else:
        obj.data = curve_data
    mat = _ensure_teal_material()
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    # Place in the markers collection if it exists.
    target = bpy.data.collections.get(f"{plant_id}__04_markers")
    if target is not None and obj.name not in target.objects:
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        target.objects.link(obj)
    elif not obj.users_collection:
        bpy.context.scene.collection.objects.link(obj)
    obj["plant_id"] = plant_id
    obj["root_id"] = root_id
    obj["semantic"] = "aerial_root"
    obj["state"] = state
    obj["created"] = datetime.date.today().isoformat()
    return obj


if _HAVE_BPY:
    _obj = aerial_root_trace(PLANT_ID, ROOT_ID, START, END,
                             state=STATE, droop=DROOP, samples=SAMPLES)
    print(f"Aerial-root trace ready: {_obj.name} (state={STATE})")
