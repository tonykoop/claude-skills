# Drawing brief — CNC Welcome Sign

This brief describes the drawings the project should ship with at
Tier 2. Stub SVGs live in `drawings/`; the user should regenerate
them from CAD or VCarve when ready (or the `manufacturing-planner`
specialist can be dispatched to produce SVGs).

## Drawing list

### `drawings/plan-view.svg` — Top-down view of the sign body

- **Scale:** 1:2 on letter-size paper, or 1:1 if printed on tabloid
- **Title block:** project name, drawing name, scale, units (in),
  date, maker name, sheet 1 of 3
- **Datum:** lower-left corner of sign body = (0, 0)
- **Critical dimensions to call out:**
  - Overall length L = 18.000 in
  - Overall width W = 6.000 in
  - Corner radius r = 0.250 in (typ. 4 places)
  - Letter cap height h = 3.000 in
  - Top border = 1.500 in (= (W − h)/2)
  - Bottom border = 1.500 in
  - Left text margin = ~2.000 in (font-dependent)
  - Right text margin = ~2.000 in
- **Notes:** 60° V-carve, max depth 0.125 in; "WELCOME" centered

### `drawings/front-view.svg` — Profile thickness view

- **Scale:** 1:1
- **Title block:** as above, sheet 2 of 3
- **Critical dimensions:**
  - Stock thickness t = 0.250 in
  - V-carve depth d_v = 0.125 in (max)
  - Profile-cut depth into spoilboard = 0.050 in
- **Notes:** edge profile is square (no chamfer); V-carve
  cross-section visible

### `drawings/section-A.svg` — Back-face keyhole detail

- **Scale:** 2:1 (detail view, magnified)
- **Title block:** as above, sheet 3 of 3
- **Datum:** keyhole slot center = (0, 0); locate on sign with
  offset note (centerline at 3.000 in from edge, 3.000 in from
  end / 15.000 in from end for the second slot)
- **Critical dimensions:**
  - Slot length L_k = 1.250 in
  - Wide-end diameter D_kw = 0.400 in
  - Narrow-end diameter D_kn = 0.180 in
  - Pocket depth d_k = 0.150 in
  - Slot-to-slot center spacing x_m = 12.000 in
- **Notes:** screw head locks at narrow end; orient narrow end
  upward when mounting

## Drawing standards

- **Units:** decimal inches, 3 decimal places
- **Tolerances:** ±0.031 in (= 1/32 in) unless noted; ±0.005 in on
  V-carve depth
- **Line types:** continuous heavy for visible edges, dashed for
  hidden edges, phantom for centerlines
- **Title block contents:** project, drawing, scale, units, sheet,
  date, maker, license

## SVG generation

The SVGs in `drawings/` are stubs (placeholder geometry only). To
regenerate dimensioned drawings:

1. Export from VCarve Pro: File → Export → SVG (per toolpath layer)
2. Or run the makerspace skill's drawing generator (see
   `references/drawing-and-visualization.md` and
   `scripts/generate_drawings.py` if present)
3. Or hand-author in Inkscape against the dimensions in `design.md`

The drawings are reference for the maker and viewers; the CAM file
remains the source of truth for what actually gets cut.
