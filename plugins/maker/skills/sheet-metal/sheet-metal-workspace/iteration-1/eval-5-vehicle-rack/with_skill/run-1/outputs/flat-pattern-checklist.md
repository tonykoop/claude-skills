# Flat Pattern Checklist: RAV4 Prime Roof Rack

Authority: design and CAD planning. NOT fabrication-ready. NOT road-ready.

Use this checklist BEFORE exporting any DXF for plasma or laser cut.

## Pre-Export

- [ ] Material verified in SolidWorks part property: 5052-H32 aluminum (or
      chosen alternative).
- [ ] `Material_Thickness` matches actual measured stock (caliper-verified).
- [ ] `Inside_Bend_Radius` matches actual brake tooling; verified by test
      coupon if first time with this material/thickness combo.
- [ ] `K_Factor` chosen for material: 0.42 to 0.48 starting range for 5052
      aluminum. Confirm by a measured test bend if the part is load-bearing.
- [ ] Flat pattern unfolds cleanly with no overlapping faces, no missing bend
      lines, no inverted bends.
- [ ] All bends terminate at corner reliefs; no bends terminate in raw
      material that would tear.

## DXF Layer Hygiene

Use the standard layer template (`scripts/generate_dxf_layer_template.py
--units inch`):

- [ ] `0-CUT`  outer profile and through cuts (cut path).
- [ ] `1-MARK`  etch/scribe lines, part number, orientation arrow.
- [ ] `2-ETCH`  optional surface marking (logos, panel ID).
- [ ] `3-BEND-CL`  bend centerlines for reference only (do NOT cut).
- [ ] `4-CONSTRUCTION`  geometry that is NOT cut (origin, bounding box).
- [ ] `5-REGISTRATION`  alignment marks, datum holes.
- [ ] `6-DRILL-LATER`  small holes flagged to be drilled rather than plasma
      pierced.

## Closed Loops And CAM Hygiene

- [ ] All cut-path loops closed (no gaps over 0.001 in).
- [ ] Splines converted to arcs and lines if the CAM workflow needs it.
- [ ] No overlapping segments at corner reliefs.
- [ ] No tiny stitch segments left over from blocks/imports.
- [ ] Inner cutouts have leadin/leadout planned where the operator allows;
      typical plasma leadin 0.125 in arc into scrap.

## Hole / Slot Strategy

- [ ] Slots `Deck_Slot_Length x Deck_Slot_Width` (1.00 x 0.25 in) are large
      enough for plasma; OK to plasma.
- [ ] Clamp-stud holes (size depends on selected clamp; M8 stud means about
      0.34 in clearance hole) are at the lower edge of plasma capability for
      10 ga aluminum. CONSIDER drilling/reaming after deburr.
      - If plasma: budget `Kerf` of 0.07 in and check that the resulting hole
        is round enough for the bolt to seat without binding.
      - If drilling: include center-pierce / mark on layer `6-DRILL-LATER`
        and final-drill on the bench.
- [ ] Hole-to-bend distance: at least `3 x Material_Thickness`
      (3 x 0.102 = 0.306 in) from any bend line. For load-bearing perimeter
      slots, increase to `4 x T` or more if any cracking is observed in a
      test coupon.

## Bend Allowance / Bend Table

For each 90 deg bend at R = 0.125 in, T = 0.102 in, K = 0.44:

```
BA = pi * 90/180 * (0.125 + 0.44 * 0.102)
   = 1.5708 * (0.125 + 0.04488)
   = 1.5708 * 0.16988
   = 0.2668 in (per 90 deg bend)
```

(Run `python3 scripts/sheet_metal_math.py bend-allowance --angle-deg 90
--radius 0.125 --thickness 0.102 --k-factor 0.44` to verify and tighten.)

Bend table to include on the drawing:

| Bend ID | Angle (deg) | Direction | Inside R (in) | BA (in) | Notes |
| --- | ---: | --- | ---: | ---: | --- |
| B1 | 90 | Down | 0.125 | 0.267 | Long side rail, left |
| B2 | 90 | Down | 0.125 | 0.267 | Long side rail, right |
| B3 | 90 | Down | 0.125 | 0.267 | Short end flange, front (optional) |
| B4 | 90 | Down | 0.125 | 0.267 | Short end flange, rear (optional) |

## Reliefs

- [ ] Corner reliefs at every internal corner: rectangular `Relief_Size x
      Relief_Size` (0.20 x 0.20 in) OR circular about 0.2 in dia.
- [ ] Bend reliefs at each end of every Edge Flange where the bend
      terminates: width >= `Material_Thickness` (0.102 in), depth >=
      `Inside_Bend_Radius + Material_Thickness` = 0.227 in. Round to 0.25 in.

## Stock And Nesting

- [ ] Deck blank fits inside Maker Nexus plasma bed (48 x 96 in): deck flat
      pattern needs about 54 in length x 51 in width including bend
      allowances and reliefs. CRITICAL: confirm flat pattern stays within
      48 in in the narrower direction or rotate the nest.
- [ ] Add 0.5 in plasma nesting margin around the outside.
- [ ] Add a test coupon strip (3 in x 8 in) for a bend test and a hole-fit
      check on the same sheet.

## Units And Scale

- [ ] DXF exported at 1:1 scale.
- [ ] Units stated as "inch" in the drawing title block AND in the DXF
      handoff note.
- [ ] Origin documented on the construction layer.

## Final DXF Acceptance

- [ ] Opens in LibreCAD/Inkscape/AutoCAD without errors.
- [ ] All layers visible and named per the template.
- [ ] Construction lines are clearly NOT cut.
- [ ] An orientation arrow on the etch layer ("UP / fore" or similar).

## Authority

This is the flat-pattern checklist for a provisional design. Do NOT release
the DXF to plasma cutting until the design brief's open questions are
answered and the safety gate is cleared.
