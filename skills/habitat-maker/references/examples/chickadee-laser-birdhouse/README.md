# Laser-Cut Chickadee Birdhouse Example

This is the canonical generator-backed `habitat-maker` example packet for a
small chickadee nest box. It combines Round 7 Alice's best A/B findings:
species welfare gates from Claude A and concrete SVG/JSON geometry from Codex B.

## Artifacts

- `design_params.json` - single source of truth for species constraints,
  material profiles, panel dimensions, mounting assumptions, and welfare checks.
- `geometry_params.json` - generated machine-readable geometry and derived
  validation values.
- `panels.svg` - generated laser vector template. Cut red paths, score green
  paths, optionally engrave text.
- `bom.csv` - bill of materials.
- `cut-list.csv` - panel and ply cut list.
- `safety-welfare-checklist.md` - pass/fail habitat and fabrication checklist.
- `design-table.md` - concise parametric design rationale.
- `agent-record.md` - provenance and validation record for this canonical packet.

## Regenerate

Run from the repo root:

```bash
python3 skills/habitat-maker/scripts/generate_chickadee_laser_packet.py \
  --input skills/habitat-maker/references/examples/chickadee-laser-birdhouse/design_params.json \
  --outdir skills/habitat-maker/references/examples/chickadee-laser-birdhouse
```

Then validate:

```bash
jq empty skills/habitat-maker/references/examples/chickadee-laser-birdhouse/geometry_params.json
python3 -c "import xml.etree.ElementTree as ET; ET.parse('skills/habitat-maker/references/examples/chickadee-laser-birdhouse/panels.svg')"
rsvg-convert skills/habitat-maker/references/examples/chickadee-laser-birdhouse/panels.svg -o /tmp/habitat-maker-chickadee.png
```

## Design Summary

The default material profile is untreated cedar laminated from three laser-cut
1/4 inch plies, giving about 3/4 inch finished wall thickness. A known
laser-safe exterior plywood profile is included as a fallback, but unknown
glues, treated wood, MDF, painted stock, and PVC are excluded.

Core welfare constraints:

- 1 1/8 inch entrance, with no positive oversize tolerance.
- No perch.
- Bare unfinished interior.
- Roughened or scored interior front wall for fledgling climb grip.
- Three protected side vent slots per side.
- Four corner drainage notches.
- Cleanout access.
- Baffled pole mount preferred, within about 30 feet of woody cover.
