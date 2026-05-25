# SolidWorks Sheet Metal Plan: Beetleweight Wedge Chassis

Authority: design and CAD planning only. Not fabrication-ready. All
features below are starting points; the actual brake's punch radius and
the measured stock thickness must override these numbers before any DXF
is cut.

## Global Variables (Equations)

Define these in Tools > Equations > Global Variables before the first
Sheet Metal feature. Pulled from parameters.csv.

```text
"Material_Thickness"      = 0.063in
"Inside_Bend_Radius"      = "Material_Thickness"
"K_Factor"                = 0.45
"Part_Length"             = 7.0in
"Part_Width"              = 6.0in
"Part_Height_Rear"        = 2.5in
"Front_Lip_Height"        = 0.20in
"Wedge_Angle"             = 20deg
"Hardware_Pitch"          = 1.0in
"Fastener_Hole_Dia"       = 0.128in    'M3 clearance, verify on coupon
"Relief_Size"             = 2 * "Material_Thickness"
"Wheel_Clearance"         = 0.10in
"Service_Access_Target"   = 60         'seconds, documentation only
```

In the Sheet Metal feature defaults:

- Sheet thickness: `"Material_Thickness"`
- Bend radius: `"Inside_Bend_Radius"`
- K-Factor: `"K_Factor"`
- Auto-relief: Rectangular, ratio 0.5 (override per feature where needed)

## Part Decomposition

Plan the assembly as four sheet metal parts plus optional spares.
Keeping these as separate parts (rather than a single unfolding monocoque)
trades a small weight penalty for two big wins for a middle-school team:
the top panel is a true removable service hatch, and a damaged wheel
guard can be swapped without disturbing the lower tub.

1. `lower-tub.sldprt` — base floor plus two side walls plus rear wall,
   folded from a single blank.
2. `wedge-front.sldprt` — wedge face that bolts to the front of the tub,
   folds up into a short return flange that rivets/screws to the side
   walls.
3. `top-deck.sldprt` — sloped top deck/service panel, bolts down onto the
   tub side walls.
4. `wheel-guard.sldprt` — small folded U-channel, two instances, bolt
   onto the side walls outside of each wheel. Treat as consumable spare.

## Feature Sequence Per Part

### lower-tub.sldprt

1. Base Flange/Tab from a rectangular sketch sized
   `"Part_Length"` x `"Part_Width"` (floor of the tub).
2. Edge Flange on left side: height `"Part_Height_Rear"`, 90 degrees up,
   inside bend radius `"Inside_Bend_Radius"`.
3. Edge Flange on right side: same parameters, mirrored.
4. Edge Flange on rear edge: height `"Part_Height_Rear"`, 90 degrees up.
5. Closed Corner (Butt or Overlap) on both rear corners to tie the side
   walls into the rear wall — avoids gaps that an opponent wedge could
   bite into.
6. Corner Relief: circular, diameter `"Relief_Size"` at each fold
   intersection (skill default: dogbone or circular relief at internal
   corners).
7. Hem (Tear Drop or Closed) along the top edge of each side wall and the
   rear wall. Hem direction: inward, so the top panel sits on a folded-
   over rolled edge rather than a raw cut edge. Confirm the hem can be
   made before the side walls are folded — a closed hem after a 90 fold
   is a known shop trap.
8. Linear pattern of `"Fastener_Hole_Dia"` clearance holes along the top
   of each side wall and rear wall, pitch `"Hardware_Pitch"`, offset
   `0.30in` below the hem so the screw heads land on flat sheet not on
   the hem radius.
9. Add a dedicated battery strap slot and an access notch for the main
   power switch on the rear wall — sketch features, not bends.

### wedge-front.sldprt

1. Base Flange/Tab: trapezoidal sketch sized to bridge the full
   `"Part_Width"`, height set so that when folded at `"Wedge_Angle"` the
   tip sits at `"Front_Lip_Height"` off the floor.
2. Edge Flange (return tab) along each side, height ~`0.50in`, 90 degrees
   inward — this is the screw-down ear that bolts to the side walls.
3. Edge Flange along the top edge, short return ~`0.25in` to stiffen the
   wedge's trailing edge against impact.
4. Two clearance holes per side ear at `"Fastener_Hole_Dia"` for M3
   screws into the tub side walls.
5. Optional: shallow embossed stiffening rib along the wedge centerline
   if the team has access to a forming tool. Skill default: skip unless
   a real tool exists.

### top-deck.sldprt

1. Base Flange/Tab: rectangular blank sized to overhang the tub side
   walls by `0.05in` per side; length matches `"Part_Length"` plus the
   wedge slope projection.
2. Edge Flange — short downward lip along the front edge to deflect
   debris and stiffen the front of the panel. Height ~`0.25in`.
3. Edge Flange — same short downward lip along the rear edge.
4. Linear pattern of `"Fastener_Hole_Dia"` clearance holes matching the
   tub-wall hole pattern from `lower-tub.sldprt`. Anchor this pattern to
   the same global variables so the panels stay aligned when the
   envelope changes.
5. Service-access cutout: rectangular hand notch above the battery so
   the strap can be popped without removing the whole panel — optional;
   verify it does not weaken the diaphragm action.

### wheel-guard.sldprt

1. Base Flange/Tab: rectangular blank sized to cover the wheel
   diameter plus `0.50in` margin above and `0.25in` below the wheel
   centerline.
2. Edge Flange on top: 90 degrees inward, height enough to land two
   M3 screws into the side wall.
3. Edge Flange on bottom: 90 degrees inward, shorter, single M3 screw.
4. Mirror the part with a configuration so left and right come from one
   model.

## Configurations And Design Table

Set up two configurations on each part:

- `Default-5052-0.063` — planning baseline.
- `Spares-5052-0.063` — same geometry, used to tag a second blank of
  every part in the cut list so the team can build a backup in one
  session.

A design table is overkill for this build. Single configuration plus a
spare flag is enough.

## Assembly Mates And Build Order

1. Insert `lower-tub` as fixed.
2. Mate `wedge-front` side ears to the inside face of each side wall,
   align bolt holes.
3. Mate one `wheel-guard` to each outside face of the side walls.
4. Mate `top-deck` onto the hemmed top edge of the side walls + rear
   wall.

Add a Smart Component or simple assembly feature representing the M3
screw stack so the team can audit hardware count from one place.

## Common SolidWorks Traps To Watch

- Do not model the wedge as a thin extrusion that you "convert to sheet
  metal" later. Start from Base Flange so the unfold is clean.
- If a feature refuses to unfold, the most common cause is a bend that
  intersects another bend without a relief — re-cut the relief instead
  of fighting the unfold.
- When the hem is added, watch flat-pattern length grow; re-check that
  the blank still fits the stock and the plasma bed.
- Keep the M3 hole pattern driven by `"Hardware_Pitch"` and not hard-
  coded numbers, so the side walls and top deck stay aligned after any
  envelope change.

## Drawing Package Target

For each part: one drawing with the folded view, the flat-pattern view,
a bend table, the hole pattern dimensioned from a single datum corner,
and a notes block stating material, thickness, K-factor, kerf
assumption, and an explicit `design and CAD planning only` authority
note. Mark fabrication-ready only after the team's measured stock and
brake radius are confirmed.
