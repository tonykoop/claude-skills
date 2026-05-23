"""Scaffold the Plant_<plant_id>/ collection hierarchy for the houseplant skill.

Idempotent: re-running with the same plant_id will not duplicate collections.
Designed to be sent through mcp__Blender__execute_blender_code with PLANT_ID set.

Usage inside Blender:
    PLANT_ID = "ficus-benjamina-01"
    SCIENTIFIC_NAME = "Ficus benjamina"
    COMMON_NAME = "Weeping fig"
    exec(open(r"<path>/scripts/scene_scaffold.py").read())

Or paste the body and edit PLANT_ID.
"""
import bpy
import datetime

# --- caller-overridable parameters ---
PLANT_ID = globals().get("PLANT_ID", "unknown-plant-01")
SCIENTIFIC_NAME = globals().get("SCIENTIFIC_NAME", "")
COMMON_NAME = globals().get("COMMON_NAME", "")
FRONT_AXIS = globals().get("FRONT_AXIS", "+Y")  # which world axis faces the chosen design front
SCALE_UNITS = globals().get("SCALE_UNITS", "meters")
SOURCE_RECORD = globals().get("SOURCE_RECORD", "")  # e.g. path to Obsidian note

CHILDREN = [
    "00_source_scan",
    "01_reference_photos",
    "02_skeleton_curves",
    "03_procedural_geometry",
    "04_markers",
    "05_simulations",
    "99_exports",
]


def ensure_collection(name, parent):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        parent.children.link(coll)
    return coll


def scaffold(plant_id):
    scene_root = bpy.context.scene.collection
    root = ensure_collection(f"Plant_{plant_id}", scene_root)
    for child in CHILDREN:
        ensure_collection(f"{plant_id}__{child}", root)
    # Stamp custom properties for cross-session recovery.
    root["plant_id"] = plant_id
    if SCIENTIFIC_NAME:
        root["scientific_name"] = SCIENTIFIC_NAME
    if COMMON_NAME:
        root["common_name"] = COMMON_NAME
    if SOURCE_RECORD:
        root["source_record"] = SOURCE_RECORD
    root["front_axis"] = FRONT_AXIS
    root["scale_units"] = SCALE_UNITS
    root["last_synced"] = datetime.date.today().isoformat()
    return root


if __name__ == "__main__" or True:
    root = scaffold(PLANT_ID)
    print(f"Scaffold ready: {root.name}; children: {[c.name for c in root.children]}")
