# Flat Pattern And DXF Handoff Checklist

Authority: design planning only. Not fabrication-ready. Bend allowance
numbers below come from `scripts/sheet_metal_math.py` and assume
0.063 in stock, R = T, K-factor 0.45. Override with measured tooling
before any cutting.

## Before Export

- [ ] Confirm Sheet Metal feature defaults (thickness, radius, K-factor)
      match parameters.csv.
- [ ] Re-check every Edge Flange uses the global `"Inside_Bend_Radius"`,
      not a hard-coded number.
- [ ] Run Flatten (Sheet Metal toolbar) on every part. Investigate any
      unfold error before moving on — do not "fix" it with a manual
      sketch.
- [ ] Confirm each flat pattern fits the 48 x 96 in plasma bed and that
      the four parts plus spares nest into the team's actual stock
      (likely a 12 x 24 or 24 x 24 5052 sheet purchased to size).

## Bend Allowance Reference

Bend allowance formula: `BA = pi * angle_deg / 180 * (R + K * T)`.

Computed from `sheet_metal_math.py` with R = 0.063 in, T = 0.063 in,
K = 0.45:

| Angle | Bend allowance | Used on |
| --- | --- | --- |
| 30 deg | 0.048 in | optional shallow wedge variant |
| 45 deg | 0.072 in | top-deck slope return, alternate wedge fold |
| 90 deg | 0.143 in | tub side walls, rear wall, wheel guards |

Min flange length (4 x T): 0.252 in. Min hole-to-bend (3 x T): 0.189 in.
Treat these as floors; flag any feature that violates them.

## DXF Hygiene Checklist

- [ ] Export each flat pattern at 1:1 scale, units stated in the filename
      (e.g. `lower-tub_flat_inch.dxf`).
- [ ] Layer naming follows the standard layer template — cut, mark,
      etch, bend-centerline, construction, registration, drill-later.
      Generate the layer template with
      `python3 scripts/generate_dxf_layer_template.py --units inch`.
- [ ] Close every contour. Plasma post-processors silently drop open
      loops, then you cut nothing where you expected a hole.
- [ ] Convert splines to arcs/lines if the shop's CAM needs them.
- [ ] Add stock boundary plus 0.5 in nesting margin around each blank.
- [ ] M3 clearance holes (0.128 in) are smaller than `2 x T = 0.126 in` —
      they are right at the margin. Mark them on a `drill-later` layer
      and drill or ream after plasma rather than cutting them with the
      torch. Re-check after measuring the actual stock thickness.
- [ ] Bend centerlines on their own layer, not the cut layer. They are
      reference geometry for the brake operator.
- [ ] Etch part name and material callout on every flat pattern.

## Per-Part Notes

### lower-tub.sldprt

- Flat blank approx 11.7 x 8.6 in (envelope + side wall + rear wall
  unfolds + relief allowance). Confirm in SolidWorks; do not trust this
  estimate for stock ordering.
- Watch for the hem — if a closed hem is used along the top edge, it
  adds approximately `2 x T + bend allowance` to the blank height per
  hemmed edge. Roll the hem first, then bend the side walls up.
- Reliefs at the four box corners: circular, `"Relief_Size" = 0.126 in`
  diameter, tangent to both bend lines.

### wedge-front.sldprt

- Two folds: 90 deg side-ear returns (BA 0.143) plus the main wedge
  fold (currently planned 90 deg between the side ears, with the wedge
  angle expressed in the assembly via mate, not at the brake).
- Alternate plan: fold the wedge ramp directly at `"Wedge_Angle"`
  (BA 0.048 for 30 deg, 0.072 for 45 deg). Pick one approach before
  exporting the DXF — do not leave both options live.
- Add a 0.063 in radius at each side-ear inside corner so the cut does
  not crack-initiate at the fold root.

### top-deck.sldprt

- Two short return flanges, both 90 deg (BA 0.143). Verify the front
  flange does not foul the wedge return when assembled.
- Hand-notch above the battery: keep at least 3 x T from the nearest
  fold; otherwise the panel will oil-can.

### wheel-guard.sldprt

- Two 90 deg folds (BA 0.143 each). Smallest of the four parts; a
  single 24 x 24 in scrap can yield eight of them — plenty of spares.
- Confirm the inner face of the guard clears the actual wheel by at
  least `"Wheel_Clearance" = 0.10 in` after assembly tolerances.

## Test Coupon Plan

Cut and bend a small coupon from the actual 5052-H32 stock before
committing the four real blanks:

- 1.0 x 3.0 in strip with two 90 deg bends at R = 0.063 in, 1.0 in
  apart, with a circular relief at one end and a square relief at the
  other.
- One M3 clearance hole 0.189 in from one bend, one at 0.10 in from
  the other (deliberately too close, to confirm distortion is visible
  enough to reject it).
- Sand and deburr the cut edges; confirm the team's deburring tools
  produce a finish a child's hand can safely run along.

## Stop-Work Before Sending DXF

- [ ] Material and thickness measured, not assumed.
- [ ] Brake punch radius measured. If the brake's smallest radius
      exceeds `"Inside_Bend_Radius"`, update the global variable and
      re-export.
- [ ] Plasma kerf measured on a coupon (planning value 0.070 in is a
      guess until cut).
- [ ] Hardware in hand, M3 clearance verified against the actual
      screws.
- [ ] An adult on-site has reviewed the wheel guards for finger-pinch
      and the wedge tip for edge sharpness.
