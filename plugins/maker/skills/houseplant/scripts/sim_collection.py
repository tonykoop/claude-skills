"""Clone the current-state twin into a dated simulation collection so what-if
edits (pruning, wiring, growth previews) never mutate the canonical twin.

Usage inside Blender:
    PLANT_ID = "ficus-benjamina-01"
    SCENARIO = "prune_apex"      # short kebab/snake case label
    SOURCE_COLLECTIONS = ["02_skeleton_curves", "03_procedural_geometry"]
    DATE_OVERRIDE = None          # set "YYYY-MM-DD" to override today's date
    exec(open(r"<path>/scripts/sim_collection.py").read())

The script copies references into a new collection by *linking* the same
object datablocks. If the caller wants to actually edit geometry in the sim
without affecting the source, they should make the linked objects single-user
on the specific ones they want to diverge (Object > Make Single User).
"""
import bpy
import datetime

PLANT_ID = globals().get("PLANT_ID", "unknown-plant-01")
SCENARIO = globals().get("SCENARIO", "scenario")
SOURCE_COLLECTIONS = globals().get("SOURCE_COLLECTIONS", ["02_skeleton_curves"])
DATE_OVERRIDE = globals().get("DATE_OVERRIDE", None)


def make_sim_collection(plant_id, scenario, source_collection_suffixes, date_str=None):
    date_str = date_str or datetime.date.today().isoformat()
    sim_name = f"sim_{scenario}_{date_str}"
    parent = bpy.data.collections.get(f"{plant_id}__05_simulations")
    if parent is None:
        raise KeyError(f"Run scene_scaffold.py for {plant_id} first.")
    sim = bpy.data.collections.get(sim_name) or bpy.data.collections.new(sim_name)
    if sim.name not in [c.name for c in parent.children]:
        parent.children.link(sim)
    # Link (not copy) source objects so the sim starts from the current state.
    for suffix in source_collection_suffixes:
        src = bpy.data.collections.get(f"{plant_id}__{suffix}")
        if src is None:
            continue
        for o in src.objects:
            if o.name not in sim.objects:
                sim.objects.link(o)
    sim["scenario"] = scenario
    sim["created"] = date_str
    sim["plant_id"] = plant_id
    return sim


sim = make_sim_collection(PLANT_ID, SCENARIO, SOURCE_COLLECTIONS, DATE_OVERRIDE)
print(f"Sim collection ready: {sim.name}")
print("Tip: select objects you want to edit in the sim and use Object > Make Single User.")
