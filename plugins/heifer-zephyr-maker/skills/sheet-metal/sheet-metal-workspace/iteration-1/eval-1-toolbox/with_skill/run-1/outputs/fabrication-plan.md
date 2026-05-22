# Fabrication Plan

Planning-grade operation sequence. Not fabrication-ready until materials,
brake fingers, hinge, casters, and bend allowance are confirmed.

## Bill Of Operations Summary

| Part | Cut | Deburr | Bend / Form | Join | Finish |
| --- | --- | --- | --- | --- | --- |
| Tub (10_SWTB_Tub) | Plasma 16 ga | Yes, while flat | Brake: corner reliefs, end walls, long walls, hem | Tab-slot + TIG seam at end-cap corners | Powder coat ext, oil/wax int |
| Lid (11_SWTB_Lid) | Plasma 16 ga | Yes, while flat | Brake: skirt, rim, hem | Tab-slot + TIG seam at skirt corners | Powder coat ext, oil/wax int |
| Tray (12_SWTB_Tray, optional) | Plasma 16 ga | Yes, while flat | Brake: walls, hem | Tab-slot + spot TIG corners | Match box finish |
| Dolly Deck (30_SWTB_Dolly_Deck) | Plasma 12 ga | Yes, while flat | Brake: skirts, rim, hem | Welded skirt corners; doublers MIG to underside | Powder coat |
| Caster Doubler (31) | Plasma 12 ga | Yes | None | Plug-welded to deck or bolted | Same as deck |
| Handle Bracket (32) | Plasma 12 ga | Yes | Brake: 2 bends | MIG to rear deck or bolted | Same as deck |

## Ordered Operation Sequence (Per Part)

### Tub

1. Nest tub blank, end-cap relief geometry, and a 4 x 4 in test bend
   coupon on a single sheet of 16 ga mild steel.
2. Plasma cut blank + coupon. Use kerf compensation per measured shop kerf.
3. Deburr while flat (file or sander on all cut edges; pay attention to
   tab-and-slot mating edges).
4. Pilot-drill / pierce-only any small hardware holes that plasma can't
   cut cleanly (below ~2 x T = 0.120 in).
5. Bend test coupon first; measure flat-pattern length vs as-bent length;
   confirm K-factor 0.44 holds. If off by more than 0.020 in, re-cut tub.
6. Brake bend order on tub:
   a. Long-edge wall flanges (front, then back) up to `Tub_Height`.
   b. Short-edge wall flanges (left, then right) up to `Tub_Height`.
   c. Tear-drop hem on tub rim - verify reach with current finger setup.
7. Close end-cap corners with tab-and-slot self-fixturing geometry.
8. TIG seam the two vertical end corners on the inside; light grind.
9. Drill or ream any holes that must be precise after bending (latch base
   if pierce-only quality was insufficient).
10. Inspect: tub rim flat within 0.030 in; tub squareness within 0.060 in
    diagonal.

### Lid

1. Nest blank + 4 x 4 coupon. Cut, deburr while flat.
2. Bend order on lid:
   a. Skirt edge flanges (front/back, then left/right) down by `Lid_Drop`.
   b. Stack rim edge flange up by `Stack_Rim_Height`. Confirm rim does not
      collide with skirt bend before later operations.
   c. Tear-drop hem on the bottom of the skirt - verify the lid will lift
      out of the brake after this bend (it should: rim is up, hem is at
      the bottom, opposite directions).
3. Close skirt corners (tab-and-slot + TIG seam, same approach as tub).
4. Mount-prep holes for piano hinge knuckle and latch keepers (verify
   pierce/drill plan).
5. Inspect: lid drops onto tub with `Clearance_Gap` on all four sides; rim
   sits proud of lid top by `Stack_Rim_Height` +/- 0.030 in.

### Dolly Deck

1. Nest deck + dolly skirt coupon + caster pattern test on a single sheet
   of 12 ga mild steel. Note: 12 ga is harder to bend than 16 ga; confirm
   brake capacity at this thickness before cutting.
2. Plasma cut deck blank + coupon. Deburr while flat.
3. Test-bend coupon: confirm bend allowance 0.2375 in at K = 0.44.
4. Brake bend order on deck:
   a. Skirts down by `Dolly_Skirt_Height` (front, back, left, right) -
      same logic as tub.
   b. Stack rim up by `Stack_Rim_Height` along the rim path.
   c. Tear-drop hem on the bottom of each skirt - confirm reach.
5. Plug-weld or MIG doubler plates onto the underside at each caster bolt
   pattern.
6. MIG welded skirt corners (12 ga is well suited to MIG seam closure).
7. Drill or ream caster bolt holes through deck + doubler stack.
8. MIG handle bracket to rear deck (or bolt through doubler).
9. Inspect: deck flat within 0.060 in; caster bolt patterns square within
   0.030 in; rim mates onto bottom of any seed-configuration box with
   `Clearance_Gap` slip-fit.

## Assembly (Box)

1. Bolt piano hinge between tub back and lid back skirt (or MIG hinge
   leaves to interior - decision pending hinge selection).
2. Bolt draw latches: bases on tub front, keepers on lid front skirt. Two
   per long face.
3. Apply rubber foot pads at four corners of tub base.
4. Confirm lid swings without binding and latches engage with audible
   detent.

## Assembly (Dolly)

1. Bolt casters through deck + doubler. Apply medium-strength threadlocker.
2. Bolt handle spine into receiver bracket. Confirm handle stows and
   deploys.
3. Drop a seed-configuration box base onto deck rim. Confirm self-locating
   feel.

## Stack Validation (Family Layout)

1. Stack 3 boxes on dolly. Push at slow pace across shop floor; confirm
   nothing slides relative to anything below.
2. Engage stack-coupling draw latches. Tilt-test to 15 deg side, 15 deg
   front; confirm no separation.
3. Lift handle spine to hand-truck angle; confirm casters carry the load
   and the stack remains coupled.
4. Repeat with 4 boxes if the use case requires; if center-of-gravity
   feels high or casters skid, cap at 3-high.

## Quality And Inspection

- Visual: no exposed raw edges on any hand-contact surface.
- Functional: lid open/close, latch engagement, hinge alignment, stack
  drop-in, dolly roll, brake engagement.
- Dimensional: outside envelope within 0.030 in per face; stack interface
  clearance within 0.020 to 0.040 in.

## Safety Notes (Shop Floor)

- Plasma fume capture on; PPE per shop policy.
- Eye and ear protection for grinding and shear operations.
- Bend brake: hands clear of upper beam pinch zone; never bend without
  the workpiece fully seated.
- TIG/MIG: gas, ventilation, and skin coverage per shop policy. Mild steel
  is the planning material; if the AL-ALT configuration is built,
  switch consumables and parameters and re-verify.
- Final finished part is heavy enough to require two-hand carry when empty
  and a partner or dolly when loaded. Don't try to carry a fully-loaded
  stack by hand.
