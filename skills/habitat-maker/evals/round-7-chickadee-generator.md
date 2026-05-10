# Round 7 Chickadee Generator Eval

Prompt:

> Use habitat-maker to create a laser-cut chickadee birdhouse packet with
> species assumptions, material choice, SVG/JSON geometry, welfare validation,
> BOM, cut list, mounting, maintenance, and safety notes.

Expected skill behavior:

- Load the canonical example at
  `references/examples/chickadee-laser-birdhouse/`.
- Prefer the generator-backed pattern for laser/CNC geometry.
- Preserve species gates: 1 1/8 inch entrance, no perch, bare interior,
  cleanout access, fledgling grip, drainage, ventilation, predator baffle,
  and woody-cover placement.
- Emit or adapt SVG/JSON artifacts from one parameter source.
- Validate JSON and SVG syntax; render the SVG when `rsvg-convert` or
  Inkscape is available.

Regression checks:

```bash
python3 skills/habitat-maker/scripts/generate_chickadee_laser_packet.py \
  --input skills/habitat-maker/references/examples/chickadee-laser-birdhouse/design_params.json \
  --outdir /tmp/habitat-maker-eval
jq empty /tmp/habitat-maker-eval/geometry_params.json
python3 -c "import xml.etree.ElementTree as ET; ET.parse('/tmp/habitat-maker-eval/panels.svg')"
```
