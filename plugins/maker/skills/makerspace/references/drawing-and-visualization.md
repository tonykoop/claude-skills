# Drawing and visualization

Standards for the drawings produced in Tier 2+ build packets. The goal
is *traceable, readable, manufacturable* drawings — not pretty pictures.

## Title block (every drawing)

Every drawing has a title block in the lower-right corner with:

- Project name + part name + part id
- Drawing number (e.g., `DWG-001`)
- Revision letter (A, B, C…)
- Drawing date and last-modified date
- Maker name
- Material callout
- Finish callout
- Tolerance block: general ± value, critical ± value
- Units (inches or mm — pick one and stick to it per drawing)
- Scale (e.g., `1:2`, `1:1`, `2:1`)
- Sheet number (1 of N)

## Required views

For most parts:

- **Plan / top view** — looking down at the part as it sits on the bench
- **Front elevation** — looking horizontally at the working face
- **Side elevation** — looking horizontally at the side
- **Section** view through any feature whose internals matter

For complex parts:

- **Isometric** view in a corner for orientation
- **Detail** views (zoomed-in callouts on small features)

## Datum chain

Every dimension references *something* — a face, an edge, a hole's
centerline. The set of "somethings" is the **datum chain**.

Rules:
- Pick three datum surfaces (one per axis) and stick with them.
- Don't dimension from datum A in one view and datum B in the next
  view of the same axis. The verifier flags this.
- Mark datums with an `A B C` callout on the relevant faces.
- Critical features (mating surfaces, alignment holes) reference
  datums directly.

## Tolerances

Two levels:

- **General tolerance** — applies to every dimension that doesn't
  specify a tighter tolerance. Pick a value at the start of the
  drawing (`±1/32"`, `±0.5 mm`, `±2°`) and put it in the title block.
- **Critical tolerance** — applies to specific features that must
  fit, mate, or align. Call out per-dimension (`Ø0.250 ±0.005`).

Don't over-tolerance. Tight tolerances cost shop time. Default to
loose, tighten only what *must* be tight.

## Units

Pick one per drawing. Mixing inches and mm in the same drawing
creates conversion errors. Add a note `units: inches` (or mm) to the
title block.

When the user's stock is sized in one and their tooling/CAD in the
other (e.g., 4×8 plywood sheet at imperial, but designed in mm),
note both in the BOM and stick with one in the drawing.

## Material and finish callouts

In the title block, plus on the drawing if multiple materials:
- Material: e.g., `Baltic birch ¼" plywood, Grade B/BB`.
- Finish: e.g., `Sand to 220 grit, two coats wipe-on poly satin`.
- Edge treatment: e.g., `1/8" chamfer all visible edges`.

## Tool/access notes

If the part needs special tooling or access:
- `Drill from face A only — backside is finished face`.
- `1/8" min bit reach for full depth — confirm tool length`.
- `Inside corners radius matches tool diameter`.

These notes save the next maker from asking.

## File formats

For the build packet:
- **SVG** is the canonical format — version-controllable, viewable in
  any browser, editable in Inkscape/Illustrator.
- **PDF** for the print packet (auto-generated from SVG).
- **DXF** for handing off to CAM software.
- **STEP/IGES** for CAD interchange.

Native CAD files (`.SLDPRT`, `.f3d`, `.skp`) live in `cad/` alongside
the exported SVG.

## Visual BOM

A visual BOM is a single page (poster-style) showing every part with
its image, callout number, name, qty, and unit cost. Used in the
print packet and capstone deck.

Layout:
- Hero photo or render in the top-left, large.
- Parts grid, 3-4 columns.
- Each part has a small thumbnail, callout number, name, qty, cost.
- Total at the bottom-right.

## Hand-drawn fallback

When CAD isn't available, hand-drawn drawings on graph paper —
photographed and inserted as images — are *acceptable for Tier 2*
provided they have:
- A title block (handwritten is fine)
- Dimensions on every critical feature
- Unit and scale indication
- A datum reference

For Tier 3, polish them up — vectorize in Inkscape (`Path → Trace
Bitmap → Centerline`), or redraw in CAD.

## Generating SVG drawings programmatically

If the project is parametric and a script can generate the drawings,
that's preferred — drawings stay in sync with `design.md` changes.

Pattern:
```python
# scripts/generate_drawings.py
from pathlib import Path
import svgwrite

def draw_part(part_name, dims, output):
    dwg = svgwrite.Drawing(output, profile='tiny')
    # ... add geometry, dimensions, title block ...
    dwg.save()
```

For most v0.1 makerspace projects, hand-authored SVG or screenshots
from CAD are fine. The auto-generation pattern matters for parametric
families (sizes S/M/L/XL of the same design).
