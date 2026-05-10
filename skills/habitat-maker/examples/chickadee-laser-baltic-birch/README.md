# Canonical Example — Chickadee Laser-Cut Birdhouse (6 mm Baltic-birch)

This is the **first canonical packet** for `habitat-maker` v0.2. It is
normative for any new species/method packet in this skill: the file
layout, the parameter schema, the welfare gate set, and the agent record
format below are the pattern other packets should mirror.

**Target species:** Black-capped chickadee (_Poecile atricapillus_) and
relatives that accept a 1-1/8" entrance hole. Compatible without changes
for Carolina, Mountain, Boreal, and Chestnut-backed chickadees, plus
house wren (with the caveat that wrens are aggressive nest competitors).
Not sized for titmice, bluebirds, or larger cavity nesters.

**Method:** Laser-cut from 6 mm Baltic-birch plywood. Box-joint corners,
removable cleanout door, single-slope roof shedding away from the entrance.

**Audience:** Makerspace family build (parent or grandparent + child).

## Files

| File | Role |
|---|---|
| `geometry_params.json` | **Single source of truth.** All dimensions, welfare gates, and references live here. The generator reads this file. |
| `chickadee-panels.svg` | **Generated artifact.** Re-run the generator to refresh. Do not hand-edit. |
| `cut-list.md` | Per-panel dimensions, derived from `geometry_params.json` |
| `BOM.md` | Bill of materials |
| `validation-checklist.md` | Welfare-integrated build acceptance gates |
| `safety-notes.md` | Laser, glue, finish, child-build safety |
| `agent-record.md` | Provenance |

## Regenerate the SVG

From the repo root:

```bash
python3 skills/habitat-maker/scripts/generate_chickadee_packet.py \
    --packet skills/habitat-maker/examples/chickadee-laser-baltic-birch
```

Or with no arguments — the script defaults to this packet:

```bash
python3 skills/habitat-maker/scripts/generate_chickadee_packet.py
```

The script consumes `derived_panel_geometry_mm` from
`geometry_params.json` and writes `chickadee-panels.svg`. If you change
a cavity dimension or welfare gate in the JSON, update the
`derived_panel_geometry_mm` block accordingly and re-run the generator
— the prose docs in this folder cite the same JSON values, so the
packet stays consistent.

## Validate

```bash
# JSON parses
jq -e . geometry_params.json > /dev/null

# SVG renders
rsvg-convert -o /tmp/preview.png chickadee-panels.svg

# Smoke test from repo root
python3 -m unittest discover skills/habitat-maker/tests
```

## Material variant

The JSON declares both a primary material profile (6 mm Baltic-birch) and
an alternate (3-ply 1/4" cedar lamination → 19 mm wall). The Baltic-birch
build is what the SVG and cut list describe. The cedar-lamination variant
needs a different joinery scheme (lap joints + screws, not box joints) and
different overall panel dimensions; if a future maker picks the alternate,
they should fork this packet folder, swap the `material.primary` block in
JSON, update `derived_panel_geometry_mm` for the new wall thickness, and
re-run the generator. The Baltic-birch build remains the default because
it is laser-friendly on diode lasers, single-session-buildable, and works
for shops without a cedar policy.
