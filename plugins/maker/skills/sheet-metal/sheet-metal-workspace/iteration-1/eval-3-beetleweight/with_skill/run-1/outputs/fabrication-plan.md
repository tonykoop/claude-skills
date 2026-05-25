# Fabrication Plan: Beetleweight Wedge Chassis

Authority: design and shop planning only. Not fabrication-ready until
the team has measured stock, confirmed brake radius, cut a test coupon,
and had an adult on-site sign off on edge safety for the middle-school
builders. Combat robotics has impact loads — design intent here is
forgiving construction, not maximum performance.

## Shop Profile Assumed

Maker Nexus-style starting profile from the skill reference. Confirm
each before scheduling shop time.

- GoFab CNC plasma table, 48 x 96 in bed (or laser if the shop has it —
  laser is preferable for the M3-clearance hole tolerance).
- 48 in box-and-pan / finger brake.
- 48 in stomp shear.
- Hand tools: deburring wheel or file set, drill press with M3
  clearance and M3 tap-drill bits, hex driver set.
- Optional but useful: bench-top vise with soft jaws, sandpaper down to
  220 grit for final edge work.

## Ordered Operation Sequence Per Part

The skill's standard sequence (cut, deburr flat, drill criticals, bend
inner first, bend outer second, fit, fasten, finish, inspect) applied
per part.

### lower-tub.sldprt

1. Plasma- or laser-cut the flat blank including reliefs, hem allowance,
   bend centerlines on a separate layer, and the M3 holes on the
   `drill-later` layer (do not torch-cut the M3 holes).
2. Deburr the entire perimeter while the part is still flat. A flap
   wheel followed by 220 grit by hand is plenty. Check that no edge can
   cut a fingertip — explicit gate for the kid-facing build.
3. Drill the M3 clearance holes with the part held flat against a backer
   board. Deburr both faces of every hole.
4. Roll or fold the hems along the top of each side wall and the rear
   wall. Hems first — this is a closed-form feature that becomes
   impossible after the side walls are bent up.
5. Bend the rear wall up 90 deg using the brake's center, with the
   bend-centerline mark up-side on the brake (operator preference; the
   skill defers to the brake's posted convention).
6. Bend the left side wall up 90 deg.
7. Bend the right side wall up 90 deg. Confirm the part is not trapped
   under the upper beam between bends 5, 6, and 7 — re-orient the part
   on the brake as needed.
8. File any closed-corner fitup gaps. Hand-sand all exterior edges.
9. Inspect: outside envelope within `+/- 1/32 in` of design, all hems
   intact, no cracks at the relief, all 8 fastener holes free of burrs.

### wedge-front.sldprt

1. Plasma- or laser-cut the blank.
2. Deburr while flat. The wedge tip is the highest-risk edge for both
   the opponent and the operator's hand — file a small chamfer along
   the tip edge before any folding.
3. Drill M3 clearance holes in the side ears.
4. Bend the two side-ear returns 90 deg inward.
5. Bend the wedge ramp at the chosen angle (90 deg between ears if the
   wedge angle is set in the assembly, otherwise the chosen wedge
   angle).
6. Sand the wedge tip again after folding. Re-check the tip is not
   sharp.
7. Inspect.

### top-deck.sldprt

1. Plasma- or laser-cut.
2. Deburr flat, including the optional hand-notch.
3. Drill the M3 clearance hole pattern. Use the lower-tub side walls as
   a transfer jig if any holes drift — drill matching pairs by hand.
4. Bend the front and rear short return flanges 90 deg downward.
5. Inspect: the panel sits flat on the tub's hemmed top edge with no
   rocking; all screws thread freely into nylocks underneath.

### wheel-guard.sldprt (x2)

1. Plasma- or laser-cut both blanks (and at least two spares).
2. Deburr flat.
3. Drill the M3 clearance holes.
4. Bend the top return flange 90 deg inward.
5. Bend the bottom return flange 90 deg inward.
6. Hand-fit each guard onto the side wall so the screws line up before
   final tightening.

## Joining Strategy

- Primary: M3 socket-head cap screws plus M3 nylock nuts. Stainless
  hardware preferred (does not rust on the workbench, tolerates the
  arena humidity).
- No permanent welds, rivets, or adhesive. Every joint should be re-
  buildable by the nieces between rounds.
- Galvanic note: stainless against aluminum in arena conditions is fine
  for a season; if the build sees outdoor storage, add a thin nylon
  washer or anti-seize. Not a blocking concern for indoor middle-school
  events.

## Finish Plan

- Deburr-only on all interior surfaces.
- Light hand-sanding on all exterior edges and corners. Run a finger
  along every accessible edge as the final check — explicit kid-safety
  gate.
- Optional: matte clear-coat or anodize for cosmetic and corrosion
  resistance. Confirm any coating is applied after final assembly fit-
  check and before final tightening, so the threads stay clean.
- No paint that would obscure the M3 hole locations from the team
  during between-match service.

## Inspection Gates

| Gate | Pass criterion |
| --- | --- |
| Material | Caliper reading within 0.060 to 0.066 in for 0.063 in nominal |
| Bend angle | 90 deg +/- 2 deg on every 90 deg fold |
| Hole alignment | All M3 screws turn in by hand, no forcing |
| Edge safety | Adult signs off: no edge sharp enough to cut a fingertip |
| Wheel clearance | Wheel spins freely with at least 0.10 in guard gap |
| Service access | Battery swap with one tool in under 60 seconds |
| Weight | Each part within 10 percent of estimated mass |
| Assembled chassis weight | At or under 400 g (skill chassis budget upper bound) |

## Stop-Work Conditions

Stop and route back for review (or to an adult on-site, or to
`maker-engineering` / `safety-gate` specialists) if any of:

- Crack visible at a bend relief.
- Crack or fold-line tearing on the wedge fold (5052 should not crack
  at R = T, but verify the actual stock alloy — 5052-H38 or 6061 sheets
  sometimes get shipped instead of 5052-H32).
- Brake's actual punch radius is larger than `"Inside_Bend_Radius"`.
  Update the global variable, re-export DXFs, recut.
- Hardware does not match the design — for example, M3 buttonhead
  shipped instead of socket-head changes the through-hole geometry.
- Total robot weight including all electronics is projected over 1360 g.
  Stop before final assembly and re-allocate.
