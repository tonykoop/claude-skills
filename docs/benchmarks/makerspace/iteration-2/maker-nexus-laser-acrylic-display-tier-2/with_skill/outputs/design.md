# Edge-Lit Acrylic Award Display — Design

Parametric design for a 6"×9" cast-acrylic panel slotted into a walnut
base with an LED strip in the slot.

## Parameters

| Name | Symbol | Value | Unit | Source |
|------|--------|-------|------|--------|
| Panel height | H_p | 9.000 | in | input |
| Panel width  | W_p | 6.000 | in | input |
| Panel thickness | t_p | 0.250 | in | input (¼" cast acrylic) |
| Panel insertion depth | d_ins | 0.500 | in | input (panel sits 0.5" into base) |
| Base length | L_b | W_p + 2.0 = 8.000 | in | derived (1" overhang each end) |
| Base width  | W_b | 3.000 | in | input (front-to-back footprint) |
| Base height | H_b | 1.250 | in | input (gives mass + depth for slot + LED) |
| Slot width  | w_s | t_p + 0.012 = 0.262 | in | derived (slip-fit, 0.006" per side) |
| Slot depth  | d_s | d_ins + 0.060 = 0.560 | in | derived (panel depth + 0.060" LED clearance) |
| Slot length | L_s | W_p + 0.020 = 6.020 | in | derived (0.010" each end clearance) |
| LED strip width | w_led | 0.394 | in | input (10 mm, COB strip) |
| LED strip height | h_led | 0.080 | in | input (typical w/ adhesive) |
| LED channel width | w_lc | w_led + 0.020 = 0.414 | in | derived (slip-fit) |
| LED channel depth (within slot) | d_lc | h_led + 0.010 = 0.090 | in | derived |
| Letter cap height | h_letter | 0.625 | in | input |
| Engraving depth | d_eng | 0.020 | in | input (raster engrave) |
| Cable exit hole dia | d_cable | 0.250 | in | input (rear-bottom of base) |
| Felt-pad thickness | t_felt | 0.062 | in | input (rubber/felt feet) |

## Critical dimensions

- Panel: 9.000 × 6.000 × 0.250 in
- Base: 8.000 × 3.000 × 1.250 in walnut
- Slot in base top: 6.020 × 0.262 in × 0.560 in deep
- LED channel at slot bottom: 0.414 × 0.090 in deep, centered in slot
- Engraving: front face only, centered, h_letter = 0.625 in
- Cable hole: 0.250 in dia, exits centered on rear face of base, 0.500 in
  up from bottom

## Derived dimensions

- Slot wall thickness (front/back): (W_b − w_s) / 2 = (3.000 − 0.262) / 2 = **1.369 in**
- Slot wall thickness (each end of slot): (L_b − L_s) / 2 = (8.000 − 6.020) / 2 = **0.990 in**
- Effective panel exposed height = H_p − d_ins = 9.000 − 0.500 = **8.500 in**
- Panel free aspect ratio (visible) = 8.500 / 6.000 = 1.417
- Engraving area (safe, with 0.5" margin all sides) = 5.000 × 7.500 in
- Total mass estimate: walnut base ~0.55 lb + acrylic ~0.30 lb ≈ **0.85 lb**

## Slot fit math (the dimension that matters most)

The slot width drives whether the panel sits plumb without glue.

- Cast acrylic ¼" stock: actual thickness typically 0.220–0.236 in
  (industry tolerance, *not* a true 0.250). **TBD — measure actual stock
  before final slot cut.**
- Slot width target = measured acrylic thickness + 0.012 in (0.006" per
  side gives a slip-fit with no rock).
- Cut method: tablesaw with a flat-tooth ripping blade for a flat-bottom
  kerf, OR two passes on a router table with a 1/4" straight bit. See
  `op-sequence.md` step 4.

## Lighting math

- LED strip: 12V COB, ~24 LEDs/in, 320 lumens/ft warm white (3000K).
- Length needed = L_s − 0.040 = **5.980 in** (sit just inside slot ends).
- Strip wattage at 5.98 in ≈ 0.5 ft × 4 W/ft = **2.0 W**.
- Power supply: 12V, 1A wall wart is overkill (×6 headroom) but cheap
  and standard.

## Engraving design

- Text content: TBD — provide on build day.
- Font: Sans-serif at this small a cap height; serifs lose detail in
  raster engrave. Suggested: Inter Bold or similar.
- Layout: centered in 5.000 × 7.500 in safe area.
- Engrave on FRONT face only (the face you'll be looking at). Rear face
  stays smooth — frosted text reads cleaner this way.

## Open questions

- **Acrylic stock thickness — measure before cutting the slot.** Plug
  measured value into the Slot fit math section.
- **Engraving content** — provide before laser session.
- **LED color temperature** — warm white (3000K) is the spec; if cool
  white (5000K) is preferred, change the BOM line item but no
  dimensional impact.

## Notes

- Panel sits in slot dry — no adhesive. Walnut + acrylic glue joints
  are unreliable; relying on slot friction makes the award field-
  serviceable (replaceable LED, cleanable slot).
- All vertical dimensions assume the base sits on rubber/felt feet, so
  cable exit can be at 0.500 in up from base bottom without conflict.
