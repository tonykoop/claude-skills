# Design — Climbing-Vine Plasma Trellis

## Inputs (parametric)

| Symbol | Meaning | Value | Units |
|---|---|---|---|
| H | Overall trellis height (above grade) | 72.0 | in |
| W | Overall trellis width | 24.0 | in |
| t | Plate thickness (mild steel A36) | 0.25 | in |
| H_spike | Below-grade spike length | 12.0 | in |
| H_total | Total stock height (H + H_spike + 2") | 86.0 | in |
| W_stock | Stock width | 24.0 | in |
| n_leaves | Leaf count along stem | 9 | — |
| L_leaf | Leaf chord length (long axis) | 6.5 | in |
| W_leaf | Leaf width (short axis) | 3.5 | in |
| r_leaf_min | Minimum interior radius on a leaf cusp | 0.20 | in |
| w_stem_min | Minimum stem-rib width (structural) | 0.625 | in |
| w_stem_max | Maximum stem-rib width (root) | 1.50 | in |
| h_kerf | Plasma kerf width (Hypertherm Powermax 65, 1/4 mild, fine cut) | 0.060 | in (assumption) |
| h_pierce | Pierce hole diameter, allowance | 0.250 | in |
| d_lead_in | Lead-in length | 0.30 | in |
| d_lead_out | Lead-out length | 0.15 | in |

Verify `h_kerf` from a real cut sample on Maker Nexus's plasma before
committing the production file. The 0.060" value is a derived
estimate from typical Powermax 65 fine-cut consumables on 1/4" mild
steel; the actual machine and consumable state at the shop will
shift it ±0.010".

## Geometry rules

- **Stem.** A continuous sinuous spline from the bottom rail (at
  y = 0) to the top tip (at y = H). The stem tapers linearly from
  `w_stem_max` at the base to `w_stem_min` at the tip. The spline's
  control points lie alternately at (W·0.30, ...) and (W·0.70, ...)
  every 9 inches of height, producing a soft S-curve.
- **Leaves.** 9 leaves alternate sides along the stem at 7.5 in
  spacing starting 7.5 in above the base. Each leaf is a cardioid-ish
  closed curve attached to the stem along its chord; the leaf's long
  axis is rotated 25-40 deg from horizontal to suggest an upward reach.
- **Tendrils.** Three thin tendrils branch from the stem at heights
  18, 38, and 60 in. Each tendril is a 0.50-in-wide ribbon that
  curves outward and curls back on itself with a minimum interior
  radius of 0.30 in.
- **Bottom rail.** A 4 in × 24 in solid rectangle at the base
  carries the two spikes. The vine stem joins the rail with a
  generous fillet (r >= 0.75 in) to avoid a stress riser at the
  ground line.
- **Spikes.** Two 1.5 in × 12 in tapered points project below the
  rail. The taper bottoms out at a 30 deg point.

## Critical dimensions (drive these from the inputs)

- Overall outline: 24 × 86 in (H_total × W_stock).
- Base rail: 24 × 4 in.
- Spike spacing: spikes centered at x = 6 in and x = 18 in.
- Total cut-path length (estimated from CAM): ~480 in (40 ft).
  Refine after CAM.

## Plate orientation on the table

Mild steel A36 sheet has no grain. Orient the long axis of the
trellis along the table's long axis. Place the ground rail toward
the operator side so the cut sequence ends near the most
accessible edge.

## Why plasma, not waterjet

- The silhouette is forgiving — interior leaf radii are 0.20 in or
  larger, well above the plasma's minimum corner radius for 1/4"
  mild steel (~0.10 in with a fine cut consumable).
- Plasma is roughly 5-10x faster than waterjet at this thickness for
  organic curves with no tight inside corners.
- Edge finish after powder-coat blast prep is visually
  indistinguishable for a garden trellis.
- No abrasive cost, no kerf-taper compensation that needs a dual-axis
  waterjet head.

## Assumptions to confirm before cutting

- `h_kerf = 0.060 in` based on Powermax 65 fine-cut on 1/4" mild
  steel. **Cut a 2-in kerf-test coupon first** and measure with a
  caliper. If actual kerf differs by more than 0.010 in, regenerate
  the path with the corrected offset.
- Plate flatness within 1/16 in over 8 ft. If the sheet is bowed,
  use magnetic hold-downs at the four corners and the midpoints.
- Powder coater accepts 1/4-in steel up to 86 in long. Confirm
  oven dimensions with the chosen vendor (see `sourcing.csv`).
