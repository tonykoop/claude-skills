# 3-Tier Hexagonal Walnut Lazy Susan — Tier 1 Design

**Space profile:** `home-shop-default` (no makerspace named)
**Tools available (per user):** bandsaw, drill press, hand tools, random-orbit sander, handheld router, clamps. **No CNC, no laser.**
**Tier:** 1 — shop-ready

## Intent

Three solid walnut hexagonal disks stacked on a common vertical axis, each tier
rotating independently on its own lazy-susan bearing. Bottom tier is the
largest; each tier above steps inward by 2" of point-to-point diameter. Built
with the bandsaw + router + drill press kit only.

## Parameters

| Name | Symbol | Value | Unit | Source |
|------|--------|-------|------|--------|
| Bottom tier point-to-point diameter | D1 | 16 | in | input |
| Step-down between tiers (point-to-point) | dD | 2 | in | input |
| Number of tiers | n | 3 | — | input |
| Walnut tier thickness | t | 0.75 | in | input (4/4 walnut, S4S to ~3/4") |
| Roundover radius (top + bottom edges) | r | 0.25 | in | input |
| Bearing 1 (between tiers 1 and 2) | B1 | 6 | in square | input |
| Bearing 2 (between tiers 2 and 3) | B2 | 4 | in square | input |
| Lazy-susan screw length | Ls | 0.5 | in | input (#8 wood screws) |

## Derived dimensions (formulas, not snapshots)

For a regular hexagon, given point-to-point diameter D:

- Side length: `s = D / 2`
- Apothem (center-to-flat): `a = s × √3 / 2 = D × √3 / 4`
- Across-flats diameter: `F = 2a = D × √3 / 2 ≈ D × 0.8660`
- Internal angle at each vertex: 120°
- Cut angle for each side (off a square blank): vertices lie at 60° increments

### Per-tier geometry

| Tier | Point-to-point D (in) | Side s (in) | Apothem a (in) | Across-flats F (in) |
|------|------------------------|-------------|-----------------|---------------------|
| 1 (bottom) | D1 = 16 | 8.000 | 6.928 | 13.856 |
| 2 (middle) | D1 − dD = 14 | 7.000 | 6.062 | 12.124 |
| 3 (top) | D1 − 2·dD = 12 | 6.000 | 5.196 | 10.392 |

**Square blank size to lay out each hex** = D (point-to-point), so a tier-1
blank is at least 16"×16". A 16"×16"×3/4" walnut panel (glued up from boards)
holds the full hex with no margin. **Recommend +1/2" each direction** for
layout slop → tier-1 blank = 16.5"×16.5", tier-2 = 14.5"×14.5", tier-3 =
12.5"×12.5".

### Stack height

- Tier thickness: 3 × t = 2.25"
- Lazy-susan bearings (typical 4-bolt-hole hardware): ~5/16" each, so 2 × 0.3125 = 0.625"
- **Total assembled stack height ≈ 2.875"** (excluding rubber feet on bottom)

## Critical dimensions

- D1 = 16 in (point-to-point), tolerance ±1/16"
- D2 = 14 in (point-to-point), tolerance ±1/16"
- D3 = 12 in (point-to-point), tolerance ±1/16"
- t  = 0.75 in (final thickness after S4S), tolerance ±1/32"
- All six sides on each hex within ±1/32" of nominal s
- All six interior angles 120° ±0.5°
- Tier 1 and tier 2 must be **concentric** within ±1/16" so the bearing seats
  cleanly. Same for tier 2 / tier 3.

## Layout method (no CNC, no laser)

The hex layout is done with a compass and straightedge on the blank itself.
Standard six-around-one construction:

1. Mark center of square blank (diagonal-to-diagonal).
2. Set compass radius = s (side length for that tier).
3. Strike a circle of radius s about center. **The radius equals the side
   length for a regular hexagon — this is the construction trick.**
4. Walk the compass around the circle: starting at any point on the circle,
   step the compass radius six times to mark six vertices.
5. Connect adjacent vertices with a straightedge → regular hexagon, sides = s.

Verify: distance across opposite vertices = D (point-to-point). Distance
across opposite flats = F (across-flats). If both check, the hex is good.

## Bearing placement

Each lazy-susan bearing sits centered on the lower tier's top face, hidden
under the tier above. Bearings are square; centerlines align with the
geometric center of each hex.

- Tier-1 → tier-2 bearing (B1, 6" sq): centered on tier 1, between tier 1 and tier 2
- Tier-2 → tier-3 bearing (B2, 4" sq): centered on tier 2, between tier 2 and tier 3

Bearing access hole: drill a 1/2" thru-hole in the upper plate of each
bearing's mounting rectangle on the **lower** tier so the bearing's screws
into the **upper** tier can be driven from below after the upper tier is in
place. (Standard lazy-susan installation — every bearing manufacturer
documents this.)

## Edge profile

Roundover both top and bottom of every tier with a 1/4" roundover bit in the
handheld router. The bottom roundover hides any minor sand-through and gives
the stack a friendlier silhouette. Optional: leave the bottom of tier 1
square if the lazy susan will live on a tablecloth.

## Open questions / assumptions

- **Walnut blank source — assumption:** the user is gluing up tier blanks
  from 4/4 (≈13/16" rough → ≈3/4" S4S) walnut boards, not finding a single
  16"-wide walnut slab. Glue-up is in `op-sequence.md` step 1.
- **Bearing brand/SKU — assumption:** Generic 6" and 4" square 4-bolt
  lazy-susan bearings (Rockler, Lee Valley, Amazon, Home Depot all stock
  these). Final SKU goes in Tier 2's `sourcing.csv`; for Tier 1 the size +
  load rating is what matters.
- **Finish — assumption:** wipe-on oil/varnish (Watco Danish or equivalent).
  Listed in BOM but the user can swap to whatever they like; the design
  doesn't depend on it.

## Notes

- The bandsaw — not the router — defines the precision floor on this build.
  A drift-free bandsaw fence and a sharp 1/2" 3-TPI blade are what hold the
  hex sides parallel and the angles at 120°. See `op-sequence.md`.
- Concentricity matters more than absolute diameter. If tier 1 ends up
  15-15/16" instead of 16", that's fine; if tiers 1 and 2 are off-center
  relative to each other by 1/8", the lazy susan will look wrong every time
  it spins.
