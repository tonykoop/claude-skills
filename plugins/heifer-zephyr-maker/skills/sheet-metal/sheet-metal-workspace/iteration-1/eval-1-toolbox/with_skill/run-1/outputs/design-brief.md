# Stackable Sheet Metal Toolbox Family + Dolly - Design Brief

## Object And Use Case

A parametric family of stackable sheet metal toolboxes plus a wheeled dolly
that carries three or four stacked boxes at a time. The seed size is a
20 x 10 x 8 inch (L x D x H) clamshell case in the modular-toolbox/tackle-box
tradition. The CAD lives in a top-down SolidWorks assembly: a Master Layout
Part (MLP) drives every child part, a Design Table drives multiple sizes, and
the dolly is dimensioned off the same envelope so stack geometry stays
consistent across the family.

Primary use cases:

- Tool, fastener, and small-parts storage that travels between bench, truck,
  and jobsite.
- Modular stacks 3-4 high latched together; bottom box absorbs dynamic load.
- Dolly carries the stack on swivel + fixed casters, with a removable handle
  spine for hand-truck mode.

## Outside Envelope (Seed Configuration)

| Dimension | Value | Source |
| --- | ---: | --- |
| Box outside length `Box_Length` | 20.000 in | user seed |
| Box outside depth `Box_Depth` | 10.000 in | user seed |
| Box outside height `Box_Height` | 8.000 in | user seed |
| Stack envelope (3 high, with rims) | ~27 in tall | derived `Box_Height*3 + 3` |
| Stack envelope (4 high, with rims) | ~35 in tall | derived `Box_Height*4 + 4` |
| Dolly deck outside | 22 x 12 in | derived `Box_+ 2 in` margin |
| Dolly overall height (deck + caster) | ~5.5 in (planning) | assumption, caster TBD |

Stack pose: boxes nest into a perimeter clocking rim (~0.50 in upward rim on
each lid; corresponding ~0.50 in inset shoulder on the next box's base). Two
draw latches per long face couple adjacent boxes. The bottom box of the
stack drops into a recessed locating rim on the dolly deck.

## Interfaces

- Tub-to-lid: continuous piano hinge along the back long face; two
  over-center draw latches along the front long face.
- Box-to-box (stack): perimeter clocking rim on the lid, perimeter inset
  shoulder on the next box's base. Optional pair of draw latches captures
  stack vertically. Inset matches rim outside dimension + `Clearance_Gap`.
- Box-to-dolly: dolly deck has the same upward locating rim as a lid, so the
  bottom box drops in and self-locates. Optional pair of strap or buckle
  hooks for highway-grade restraint when moving full stacks.
- Hardware mounting: hardware pitch 2.0 in on center for hinge knuckles,
  latch bases, foot pads. Hardware list is purchased, not custom-cut.

## Material And Process (Planning)

| Item | Planning value | Authority |
| --- | --- | --- |
| Box body (tub + lid) | 16 ga mild steel, 0.060 in nominal | planning; measure stock before flat-pattern release |
| Dolly chassis (deck + skirts) | 12 ga mild steel, 0.105 in nominal | planning; uprate to 11 ga if 4-high heavy loads expected |
| Cut process | CNC plasma (48 x 96 in bed) | Maker Nexus-style planning profile |
| Forming | 48 in box-and-pan brake / finger brake | planning; verify available fingers for 20 in walls |
| Joining (box) | Self-fixturing tab-and-slot + TIG or rivets | planning |
| Joining (dolly) | TIG welded, doubler plates at caster mount pattern | planning |
| Finish | Powder coat outside, oil/wax inside | planning |

## Constraints And Safety

- No exposed raw edges on any hand-contact surface. Use closed or
  tear-drop hems on tub rim, lid skirt edge, and handle slot.
- Stack height greater than 3 x base width triggers a center-of-gravity
  warning; default cap at 4 boxes for the seed size (4 x 8 in = 32 in tall
  against 10 in deep, which is over 3x and demands caster brakes + strap).
- The dolly will roll across uneven surfaces. Caster bolt patterns must be
  doubled with reinforcement plates. Caster selection is purchased hardware,
  not in scope for sheet metal authority.
- Strap-down / overhead-rated lifting is out of scope. If a use case appears
  for crane lift or overhead carry, route to maker-engineering safety gate.
- Empty box target weight: under 14 lb for the seed size (planning estimate
  ~10 lb tub + ~3 lb lid + hardware; verify with cut nest area after
  flat-pattern).

## Authority Ladder For This Packet

- `concept`: this brief, mood references, stackable-toolbox precedent.
- `design`: parameters.csv, solidworks-plan.md, equation list, design-table
  CSV, flat-pattern checklist - all derived from planning assumptions.
- `fabrication`: NOT YET. Material thickness, brake fingers, hinge selection,
  caster selection, and bend allowance must be confirmed against measured
  stock and shop-cleared tools before any DXF is released.

This packet is design-authority only. Treat every dimension as parametric
intent, not a release for cutting.

## Open Questions (3 max)

1. Which hinge style: continuous piano hinge (welded or riveted) versus
   discrete cabinet hinges? Drives whether the back long face has a
   continuous knuckle pocket.
2. Caster selection: total stack weight target (3 vs 4 boxes, target load
   per box) governs caster rating and bolt pattern. Provisional plan is
   four 3 in casters (two swivel-with-brake front, two rigid rear) rated
   200 lb each.
3. Confirm shop access to the 48 in box-and-pan brake with adequate finger
   set to bend a 20 in tub wall at the same time as the 10 in end walls
   without trapping the part. If not, switch to four-sided tray + welded
   end caps construction.
