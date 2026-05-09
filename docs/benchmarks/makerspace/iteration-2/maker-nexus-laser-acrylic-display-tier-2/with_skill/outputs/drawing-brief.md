# Drawing brief — Edge-Lit Acrylic Award Display

This brief describes the dimensioned drawings that should accompany
the build. SVGs not yet generated; produce on demand from the
parameters in `design.md` using `references/drawing-and-visualization.md`
+ `scripts/generate_drawings.py` (in the makerspace skill repo).

## Drawing pack — what to produce

The full pack is six drawings. All inches, third-angle projection,
tolerance ±0.020 in unless otherwise specified, scale stated on each
sheet.

### D-01 — Acrylic panel front view

- **Scale:** 1:2 on letter-size paper
- **Shows:** 9.000 × 6.000 × 0.250 panel with engraved text region
  (5.000 × 7.500 in safe area, centered).
- **Dimensions called:** overall H_p, W_p, t_p, engrave area W and H,
  engrave area offsets from edges (0.500 in margin all sides).
- **Title block:** project name, drawing number D-01, scale, units in,
  date, maker.
- **Notes:** "Front face only — engrave this side. Cast acrylic.
  Cut and engrave on Maker Nexus CO2 laser."

### D-02 — Acrylic panel section A-A

- **Scale:** 2:1
- **Shows:** vertical cross-section through panel showing engraving
  depth d_eng = 0.020 in.
- **Dimensions called:** t_p = 0.250, d_eng = 0.020, residual
  thickness 0.230.
- **Notes:** "Engraving on front face only. Back face unbroken."

### D-03 — Walnut base plan view (top)

- **Scale:** 1:2
- **Shows:** top face of base with slot location.
- **Dimensions called:** L_b = 8.000, W_b = 3.000, slot length L_s =
  6.020, slot width w_s (= measured t_p + 0.012), slot endpoint
  offsets 0.990 in from each end, slot centerline 1.500 in from front
  edge.
- **Notes:** "Slot width must use measured acrylic thickness, not
  nominal 0.250."

### D-04 — Walnut base front view

- **Scale:** 1:2
- **Shows:** front-face elevation of the base.
- **Dimensions called:** L_b = 8.000, H_b = 1.250.
- **Notes:** "Cable hole 0.250 dia exits rear face — see D-05."

### D-05 — Walnut base section B-B

- **Scale:** 1:1
- **Shows:** cross-section through the slot, showing slot depth and
  the LED channel at slot bottom.
- **Dimensions called:** d_s = 0.560 in, w_lc = 0.414 in × d_lc =
  0.090 in centered in slot bottom, base wall thickness front/back =
  1.369 in.
- **Notes:** "LED strip seats in channel, faces up. Cable exits via
  rear hole D-06."

### D-06 — Walnut base rear view

- **Scale:** 1:2
- **Shows:** rear face with cable hole location.
- **Dimensions called:** cable hole dia 0.250, hole center 0.500 in
  from base bottom, centered side-to-side.
- **Notes:** "Drill from rear inward; back with scrap to prevent
  blowout into slot."

## Drawing standards

- Title block in lower-right of every sheet (project, drawing
  number, scale, units, date, drawer initials, sheet N of 6).
- Datum: bottom-front-left corner of base = origin (0,0,0); X = base
  length, Y = base width (front to back), Z = base height. Panel
  origin = bottom-center of panel front face.
- Tolerance default ±0.020 in; slot width tolerance ±0.003 in
  (drives the fit). Engraving depth ±0.005 in.
- Hidden edges in dashed line; cutting planes labeled with arrows
  and section letter (A-A, B-B).

## Concept image (optional)

A 3D isometric concept render showing the lit award (panel glowing,
walnut base, cable trailing off) belongs in `images/hero.jpg` after
the build, but a pre-build concept render in `images/concept.png`
helps stakeholders sign off on the look. Generate via Claude Design
or a quick OpenSCAD assembly.

## Output location

When generated, drawings go in `drawings/` as:

```
drawings/
├── D-01-panel-front.svg
├── D-02-panel-section-A-A.svg
├── D-03-base-plan.svg
├── D-04-base-front.svg
├── D-05-base-section-B-B.svg
└── D-06-base-rear.svg
```

For Tier 2, SVG is sufficient. Tier 3 would convert to a print-packet
PDF with all six on a single multi-page sheet.
