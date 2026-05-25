# Flat Pattern And DXF Handoff Checklist

This packet is design-authority only. Do not release any DXF for cutting
until the items below are confirmed against measured stock and shop-cleared
tools.

## Bend Allowance Numbers

Calculated by `scripts/sheet_metal_math.py bend-allowance`:

### Box (16 ga mild steel)

- Angle: 90 deg
- Inside radius: 0.060 in (= Material_T_Box)
- Thickness: 0.060 in
- K-factor: 0.44
- Bend allowance: 0.1357 in
- Min flange length: 0.240 in (4 x T)
- Min hole-to-bend distance: 0.180 in (3 x T)

### Dolly (12 ga mild steel)

- Angle: 90 deg
- Inside radius: 0.105 in (= Material_T_Dolly)
- Thickness: 0.105 in
- K-factor: 0.44
- Bend allowance: 0.2375 in
- Min flange length: 0.420 in (4 x T)
- Min hole-to-bend distance: 0.315 in (3 x T)

### Aluminum Variant (BOX-20x10x8-AL-ALT)

Recompute before release. Planning numbers using K=0.46 at R=0.063, T=0.063:
flat pattern will not match the mild-steel pattern, even though the
configurations share envelope. Re-export DXF per material configuration.

## DXF Layer Plan

Per skill DXF layer template:

| Layer | Purpose | CAM action |
| --- | --- | --- |
| `cut` | Through-cut perimeter and feature cuts | through-cut |
| `mark` | Layout / station / alignment witness | low-power scribe |
| `etch` | Part number, rev, configuration label | raster or vector etch |
| `bend-centerline` | Bend lines, for human reference only | excluded |
| `construction` | Datums, centerlines, dim chains | excluded |
| `registration` | Hardware-locating holes (hinge, latch) | through-cut |
| `drill-later` | Holes smaller than ~2*T | pierce/center only |

Filename pattern: `SWTB_{PART}_{MATERIAL}_{THICK_MILS}_{REV}.dxf`. Examples:
- `SWTB_Tub_MS_060_A.dxf`
- `SWTB_Lid_MS_060_A.dxf`
- `SWTB_DollyDeck_MS_105_A.dxf`
- `SWTB_CasterDoubler_MS_105_A.dxf`

## Pre-Export Checks Per Part

For every sheet-metal child part before DXF release:

- [ ] Part rebuilds without errors at the active configuration.
- [ ] Flat pattern feature is present and unfolds without overlap warnings.
- [ ] Inside bend radius matches `Inside_Bend_R_*` parameter; no per-feature
      overrides.
- [ ] K-factor matches `K_Factor_*` parameter.
- [ ] All bend reliefs are present at flange terminations - default
      circular relief diameter = `Relief_Size`.
- [ ] All corner reliefs are present at intersecting flanges.
- [ ] Min flange length is respected: no flange shorter than `Min_Flange`.
- [ ] All holes and slots are at least `Min_Hole_To_Bend` from the nearest
      bend centerline.
- [ ] Closed corners are set to Butt (not Overlap/Underlap) unless geometry
      requires.
- [ ] Hem feature is on the rim and lid skirt edge; hem style and radius
      verified achievable on available brake.
- [ ] Hardware holes match the latest hinge and latch datasheets (paste
      from purchased-hardware spec).

## Pre-Export Checks Per DXF

- [ ] Export at 1:1 scale. Document units (inch) in filename and inside
      the drawing note.
- [ ] All loops closed; no stray open polylines.
- [ ] Splines converted to arcs/lines if the CAM workflow demands it.
- [ ] Layers correctly assigned (cut / mark / etch / bend-centerline /
      construction / registration / drill-later).
- [ ] Bend-centerline layer present but excluded from CAM.
- [ ] Nest margin: 0.5 in around each part as planning default.
- [ ] Kerf compensation set against `Kerf_Plasma` (0.080 in planning) or
      measured kerf for the active cut settings.
- [ ] For each material change (e.g., AL-ALT), re-export and re-check; the
      flat pattern length differs even at same envelope.

## Test Coupons (Required Before First Cut)

- [ ] Bend coupon at `T = 0.060`, `R = 0.060`, K = 0.44 - confirm bend
      allowance against measured flat-pattern length.
- [ ] Tear-drop hem coupon on the available brake at 16 ga - confirm hem
      can be formed without cracking and without trapping.
- [ ] Bend coupon at `T = 0.105`, `R = 0.105`, K = 0.44 - confirm 12 ga
      math for the dolly deck.
- [ ] Tab-and-slot joint coupon for tub end closure - confirm slot fit
      after kerf compensation.
- [ ] Stack-rim coupon: form lid rim and box base shoulder, confirm
      clearance gap settles in 0.020 to 0.040 in.

## Risk Notes On Flat Pattern Unfold

- The 20 in tub wall edge flange may be near brake-finger capacity once
  end-wall flanges are added. Confirm finger set physically supports the
  bend without folding into adjacent walls.
- Hem on tub rim must come after closed corner. SolidWorks will let you
  hem first then closed-corner, but the flat pattern may show a corner
  notch that won't actually exist after forming - re-check before release.
- For the LARGE configuration (24 x 12 x 10), the 24 in wall is at 50% of
  the 48 in brake. Long parts at the limit of a brake can wander; budget
  extra time and consider a second hand on the part.
- For the AL-ALT material variant, 5052-H32 forms cleanly but the bend
  allowance differs - the same DXF cannot be reused.

## Authority Note

Numbers above come from skill planning assumptions and the script estimator.
No part of this checklist is fabrication authority. Final K-factor, hem
style, relief size, and tab-slot tolerance must be confirmed by measured
coupon and signed off by the shop instructor before any production cut.
