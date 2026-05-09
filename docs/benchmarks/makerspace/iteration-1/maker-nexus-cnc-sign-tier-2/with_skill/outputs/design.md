# CNC Welcome Sign — Design

Parametric design. Every dimension cited downstream traces back to
this file. Change a parameter here, rerun the math, and the rest of
the packet follows.

## Parameters

| Name | Symbol | Value | Unit | Source |
|------|--------|-------|------|--------|
| Sign length | L | 18.0 | in | input |
| Sign width | W | 6.0 | in | input |
| Stock thickness | t | 0.25 | in | input |
| Corner radius | r | 0.25 | in | input |
| Letter cap height | h | 3.0 | in | input |
| Letter count | n | 7 | — | input ("WELCOME") |
| V-bit angle | θ | 60 | deg | input (60° V-bit) |
| V-carve max depth | d_v | 0.125 | in | derived: t/2 |
| Profile-cut depth | d_p | 0.30 | in | input: t + 0.05 (clears spoilboard) |
| Profile-cut bit dia | D_p | 0.125 | in | input (1/8" upcut) |
| Profile passes | n_p | 3 | — | derived: ceil(d_p / 0.10) |
| Pass-per-pass profile | dz_p | 0.10 | in | input |
| Tab width | w_t | 0.25 | in | input |
| Tab height | h_t | 0.06 | in | input |
| Tab count | n_t | 6 | — | input (4 corners + 2 long edges) |
| Mounting cleat length | L_c | 5.0 | in | derived: W - 1.0 |
| Mounting cleat width | W_c | 0.75 | in | input |
| Keyhole slot length | L_k | 1.25 | in | input |
| Keyhole slot wide-end dia | D_kw | 0.40 | in | input (clears #8 screw head) |
| Keyhole slot narrow dia | D_kn | 0.18 | in | input (#8 shank + slip) |
| Keyhole slot pocket depth | d_k | 0.15 | in | derived: t × 0.6 |
| Mounting hole spacing | x_m | 12.0 | in | derived: L - 6.0 |

## Critical dimensions

- **Outline:** 18.000 × 6.000 in, four 0.25 in corner radii
- **Letter cap height (h):** 3.000 in; baseline centered on W/2 = 3.000 in
- **Letter horizontal centering:** "WELCOME" optical-centered on L/2 = 9.000 in
- **V-carve depth limit:** 0.125 in (= t/2). VCarve Pro will cap any
  letter that would exceed this depth so we never breach the back face.
- **Profile cut depth:** 0.300 in to clear into the sacrificial spoilboard
- **Keyhole slots (back face):** centered along length, x_m = 12.000 in
  apart, on the W/2 horizontal centerline
- **Mounting cleat (optional):** 5.0 × 0.75 × 0.25 in, cut from offcut

## Derived dimensions

- Letter cap height h = 3.0 in (chosen so border = (W − h)/2 = 1.5 in,
  visually balanced)
- Top/bottom border = (W − h) / 2 = (6.0 − 3.0) / 2 = **1.500 in**
- Letter run width = ~14.0 in (font-dependent; Bebas Neue Regular at
  3.0 in cap fits with ~0.5 in margin each side at L = 18.0)
- Side border (text margin) = (L − letter_run) / 2 ≈ **2.000 in**
- Profile passes n_p = ceil(0.30 / 0.10) = **3 passes**
- Keyhole slot center-to-center = x_m = 12.000 in (for #8 screws into
  studs at standard 16" o.c. — fits between two studs with ≥2" pad
  either side)

## Toolpath plan

| Order | Operation | Tool | Depth | Strategy |
|-------|-----------|------|-------|----------|
| 1 | V-carve "WELCOME" | 60° V-bit, 1/2" shank | up to 0.125 in | Vectric VCarve Pro V-carve toolpath, flat-depth limit on |
| 2 | Pocket keyhole slots (back) | 1/8" upcut endmill | 0.150 in | Pocket toolpath, two slots; flip required (see op-sequence) |
| 3 | Profile cut outline | 1/8" upcut endmill | 0.300 in | Outside profile, 3 passes × 0.10 in, 6 tabs |

## Stock plan summary

One 60 × 60 in sheet of 1/4" Baltic birch yields:

- 1× sign body (18 × 6) — primary part
- 2× mounting cleat (5 × 0.75) — from edge offcut
- 4× spacer block (1 × 1) — from offcut, optional
- ~3,180 in² of remaining offcut for future builds

Detailed layout in `cut-list.csv`.

## Open questions

- **Font choice.** Default is Bebas Neue Regular (free, condensed sans
  with clean V-carve geometry). User may swap for a serif (e.g.,
  Cinzel) before generating toolpaths — re-check letter run width if
  so. This is a generic welcome sign so any clean display
  face is fine.
- **Mounting style.** Default: keyhole slots cut into back face (no
  visible hardware). Alternate: through-holes with washers. User
  picks before CAM.
- **Finish color.** Default clear satin poly (shows birch grain).
  Alternate: stain coat between sealer and topcoat. User picks before
  finishing day.

## Notes

- Baltic birch is voidless and behaves predictably under a V-bit;
  Home Depot "birch ply" (often Lauan-cored) does not. Buy real BB.
- 1/4" stock is at the thin end of what holds a V-carve cleanly. We
  cap V-depth at t/2 = 0.125 in so we never weaken the back face.
- Sign is designed for sheltered exterior use (covered porch, eave).
  Direct rain exposure will eventually delaminate any plywood — for
  weatherproof, switch to PVC or HDPE (still CNC-friendly, both
  allowed at Maker Nexus per profile).
