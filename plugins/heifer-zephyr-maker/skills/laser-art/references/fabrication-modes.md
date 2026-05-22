# Fabrication Modes

Choose the mode before committing the artwork. Many projects use two modes:
for example, a spray stencil over a lightly engraved panel, or a CNC inlay with
laser-etched texture.

## Spray-Paint Stencil Set

Use for flat art, posterboard, canvas, wood panels, murals, and instrument tapa
surfaces where paint must stay thin.

- Typical layers: shadow, midtone 1, midtone 2, highlight, detail.
- Materials: laser-safe Mylar, cardstock, chipboard, or thin plywood test masks.
- Add registration holes or corner marks to every stencil and the substrate/jig.
- Add bridges to all floating islands before cutting.
- Recommend dry "ghost passes" over wet coats when detail matters.
- Include overspray control: light tack adhesive, magnets, weights, masking, and
  adequate dry time between layers.

## Stacked Laser-Cut Relief

Use for wall art, sculptural panels, dimensional portraits, layered landscapes,
and shadow-rich wood or paper work.

- Define backer, visible layers, spacer strategy, and alignment dowels.
- Keep each layer structurally self-supporting.
- Account for kerf and char on visible edges.
- Plan glue access, clamp method, sanding access, and finish sequence.
- Include an exploded layer map and an assembly order.

## Laser Etching and Engraving

Use for tonal panels, line art, photographs, maps, labels, and texture fields.

- Decide raster engrave, vector engrave, vector score, or cut.
- Use dithering/halftone for photographic value only when the material can hold
  the detail.
- Separate preview art from machine settings unless machine/material data is
  known.
- Include a test grid or coupon before final engraving.
- For acoustic instruments, keep engraving/paint shallow and light unless an
  instrument specialist has validated the effect.

## CNC or Laser Inlay

Use for contrasting wood, veneer, acrylic, shell, or multi-material insert work.

- Maintain separate pocket, insert, boundary, and reference layers.
- Include allowance/clearance strategy and note that final values depend on
  tooling tests.
- Avoid tiny isolated inserts unless there is a practical way to place and glue
  them.
- For CNC, record bit type, included angle, flat depth, pocket depth, and
  sanding reveal target.
- For laser veneer, record kerf compensation and veneer orientation.

## Rotary Laser Wrap

Use for tumblers, cylinders, bowls, handles, drums, tubes, and curved objects.

- Unwrap the design to a rectangle: width equals circumference, height equals
  usable engraving length.
- Record object diameter, circumference, seam location, usable height, taper,
  handle/fixture obstructions, and rotation axis.
- Keep critical faces, text, and registration features away from the seam unless
  the seam is intentional.
- For tapered objects, warn that a simple rectangular unwrap may distort; use
  taper compensation or a conical template when needed.
- Include focus checks and a small alignment mark/test pass.

## CAD Safe-Zone Art

Use when art must fit around screw holes, bracing, ports, tongues, joins, or
other mechanical/acoustic features.

- Define an `Art_Safe_Zone` sketch or equivalent boundary.
- Put registration points in both the art files and the physical/CAD fixture.
- Keep separate configurations or layers for stencil, engrave, cut, inlay, and
  preview art.
- For cajon-like faces, avoid screw lines and leave finish/paint clearance near
  edges.
- For tongue drums or other resonant parts, avoid heavy paint or deep engraving
  on vibrating tongues until validated.
