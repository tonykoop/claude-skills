"""Generate a helical wire-coil curve wrapped around a branch curve.

Approach: sample the branch curve into a poly-line backbone, then for each
segment compute a tangent frame and emit a helical offset around that frame.
The result is a single poly-curve with bevel_depth set to the wire thickness,
which renders as a tube without needing a Screw modifier on a non-axis-aligned
branch.

Usage inside Blender:
    BRANCH_OBJ_NAME = "ficus-benjamina-01_branch_R02"
    PLANT_ID = "ficus-benjamina-01"
    BRANCH_ID = "R02"
    SUFFIX = "2026-05-17"
    TURNS_PER_METER = 18    # default loose-ish wrap
    WIRE_RADIUS = 0.0015    # 1.5 mm wire (~ 15 gauge)
    COIL_RADIUS = None      # None => auto from wire radius; set in meters
    exec(open(r"<path>/scripts/wire_coil.py").read())

Notes:
- Pass the branch curve itself, not a mesh. If you only have a mesh branch,
  convert it to a curve first (Object > Convert > Curve) or build a Bezier
  curve through its skeleton.
- The coil is inserted in the parent collection of the branch by default. The
  caller can re-link it to <plant_id>__05_simulations afterward.

The pure-math helper `helix_points_along_backbone` is importable without
Blender for testing.
"""
from __future__ import annotations
import math


def helix_points_along_backbone(backbone, turns_per_meter: float = 18.0,
                                 coil_radius: float = 0.0045):
    """Generate helical poly-line points wrapped around a list of 3D backbone
    points. Pure math; importable without bpy.

    Args:
        backbone: iterable of (x, y, z) tuples forming the branch backbone.
        turns_per_meter: helix density.
        coil_radius: distance from backbone to helix path, in meters.

    Returns:
        list of (x, y, z) tuples describing the helix curve.
    """
    pts = [tuple(p) for p in backbone]
    if len(pts) < 2:
        raise ValueError("Backbone needs at least 2 points.")

    def vsub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    def vadd(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
    def vscale(v, s): return (v[0] * s, v[1] * s, v[2] * s)
    def vlen(v): return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    def vnorm(v):
        L = vlen(v)
        return (0.0, 0.0, 0.0) if L == 0 else (v[0] / L, v[1] / L, v[2] / L)
    def vcross(a, b):
        return (a[1] * b[2] - a[2] * b[1],
                a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0])

    helix = []
    arc_len = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        seg = vsub(b, a)
        seg_len = vlen(seg)
        if seg_len == 0:
            continue
        tangent = vnorm(seg)
        up = (0.0, 0.0, 1.0) if abs(tangent[2]) < 0.9 else (1.0, 0.0, 0.0)
        side = vnorm(vcross(tangent, up))
        up = vnorm(vcross(side, tangent))
        steps = max(8, int(seg_len * turns_per_meter * 8))
        for s in range(steps + 1):
            t = s / steps
            angle = (arc_len + t * seg_len) * turns_per_meter * 2 * math.pi
            offset = vadd(
                vscale(side, math.cos(angle) * coil_radius),
                vscale(up, math.sin(angle) * coil_radius),
            )
            point = vadd(vadd(a, vscale(tangent, t * seg_len)), offset)
            helix.append(point)
        arc_len += seg_len
    return helix


try:
    import bpy
    from mathutils import Vector
    _HAVE_BPY = True
except ImportError:
    _HAVE_BPY = False

BRANCH_OBJ_NAME = globals().get("BRANCH_OBJ_NAME")
PLANT_ID = globals().get("PLANT_ID", "unknown-plant-01")
BRANCH_ID = globals().get("BRANCH_ID", "X00")
SUFFIX = globals().get("SUFFIX", "")
TURNS_PER_METER = globals().get("TURNS_PER_METER", 18)
WIRE_RADIUS = globals().get("WIRE_RADIUS", 0.0015)
COIL_RADIUS = globals().get("COIL_RADIUS", None)


def _sample_curve(curve_obj, samples_per_segment=12):
    """Return world-space points along the first spline of curve_obj."""
    spline = curve_obj.data.splines[0]
    mat = curve_obj.matrix_world
    pts = []
    if len(spline.bezier_points):
        bps = spline.bezier_points
        for i in range(len(bps) - 1):
            a = bps[i]
            b = bps[i + 1]
            for s in range(samples_per_segment):
                t = s / samples_per_segment
                # de Casteljau cubic
                p = (
                    (1 - t) ** 3 * a.co
                    + 3 * (1 - t) ** 2 * t * a.handle_right
                    + 3 * (1 - t) * t ** 2 * b.handle_left
                    + t ** 3 * b.co
                )
                pts.append(mat @ p)
        pts.append(mat @ bps[-1].co)
    else:
        pts = [mat @ Vector(p.co.xyz) for p in spline.points]
    return pts


def _ensure_copper_material():
    name = "mat_wire_copper"
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = (0.72, 0.45, 0.20, 1.0)
        mat.metallic = 0.9
        mat.roughness = 0.35
    return mat


def wire_coil(branch_obj, plant_id, branch_id, suffix="",
              turns_per_meter=18, wire_radius=0.0015, coil_radius=None):
    if branch_obj.type != "CURVE":
        raise TypeError("BRANCH_OBJ must be a curve object.")
    backbone = _sample_curve(branch_obj, samples_per_segment=12)
    if len(backbone) < 2:
        raise ValueError("Branch curve has fewer than 2 sample points.")
    helix_points = []
    arc_len = 0.0
    for i in range(len(backbone) - 1):
        a, b = backbone[i], backbone[i + 1]
        seg = b - a
        seg_len = seg.length
        if seg_len == 0:
            continue
        tangent = seg.normalized()
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
    coil_name = f"{plant_id}_wire_sim_{branch_id}"
    if suffix:
        coil_name += f"_{suffix}"
    curve_data = bpy.data.curves.new(coil_name, type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = wire_radius
    spl = curve_data.splines.new("POLY")
    spl.points.add(len(helix_points) - 1)
    for i, p in enumerate(helix_points):
        spl.points[i].co = (p.x, p.y, p.z, 1.0)
    obj = bpy.data.objects.new(coil_name, curve_data)
    mat = _ensure_copper_material()
    obj.data.materials.append(mat)
    # Drop into the same collection as the branch by default.
    target_coll = branch_obj.users_collection[0] if branch_obj.users_collection else bpy.context.scene.collection
    target_coll.objects.link(obj)
    # Stamp metadata so future sessions can recover the wire's intent.
    obj["plant_id"] = plant_id
    obj["branch_id"] = branch_id
    obj["wire_radius_m"] = wire_radius
    obj["turns_per_meter"] = turns_per_meter
    obj["applied_date"] = suffix or ""
    return obj


if _HAVE_BPY and BRANCH_OBJ_NAME:
    branch = bpy.data.objects.get(BRANCH_OBJ_NAME)
    if branch is None:
        raise KeyError(f"Branch object {BRANCH_OBJ_NAME!r} not found.")
    coil = wire_coil(branch, PLANT_ID, BRANCH_ID, suffix=SUFFIX,
                     turns_per_meter=TURNS_PER_METER,
                     wire_radius=WIRE_RADIUS, coil_radius=COIL_RADIUS)
    print(f"Created coil: {coil.name}")
elif _HAVE_BPY:
    print("Set BRANCH_OBJ_NAME, PLANT_ID, BRANCH_ID before exec.")
