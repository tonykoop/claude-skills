# SolidWorks Plan: RAV4 Prime Flat Roof Rack

Authority: design and CAD planning only. NOT fabrication-ready. NOT road-ready.

## File Structure

- `RoofRack_MasterLayout.SLDPRT`  Master Layout Part containing all global
  parameters and the 2D layout sketches for the deck, side rails, and clamp
  pattern. All downstream parts reference dimensions from this file.
- `Deck_Panel.SLDPRT`  Base flange sheet metal part using the master layout
  outline.
- `Side_Rail_L.SLDPRT` / `Side_Rail_R.SLDPRT`  Sheet metal side rails as
  separate parts so they can be rolled to follow the crossbar curve.
- `CrossMember_Stub.SLDPRT`  Optional internal bracing strap; can be aluminum
  extrusion T-slot purchased rather than fabricated.
- `RoofRack_Assembly.SLDASM`  Top-level assembly with all hardware suppressed
  until clamp model is selected.

## Global Variables (Equations Block)

Mirror these into SolidWorks Equations:

```
"Material_Thickness" = 0.102in
"Inside_Bend_Radius" = 0.125in
"K_Factor"           = 0.44
"Platform_Length"    = 52in
"Platform_Width"     = 48in
"Side_Rail_Flange"   = 1.5in
"Clearance_Gap"      = 0.06in
"Relief_Size"        = 0.20in
"Hardware_Pitch"     = 4.0in
"Deck_Slot_Width"    = 0.25in
"Deck_Slot_Length"   = 1.00in
"Deck_Slot_Pitch"    = "Hardware_Pitch"
"Crossbar_Spread"    = 32in   'PROVISIONAL - measure actual
"Crossbar_Mount_X"   = 16in   'distance from deck centerline to each bar
```

Mark `Crossbar_Spread` and `Crossbar_Mount_X` with a SolidWorks comment
"PROVISIONAL - measure actual" so future-you cannot accidentally treat them
as final.

## Feature Sequence

### Deck_Panel.SLDPRT

1. **Sheet Metal Defaults**: thickness = `Material_Thickness`, bend radius =
   `Inside_Bend_Radius`, K-factor = `K_Factor`. Use 5052-H32 aluminum as the
   material database entry.
2. **Base Flange / Tab**: rectangular sketch `Platform_Length` x
   `Platform_Width`, centered on the origin. This is the deck plate.
3. **Edge Flange** along each long edge: depth = `Side_Rail_Flange`, bend
   angle 90 deg downward. (If a stiffer one-piece option is preferred, this
   is the location to convert to separate side-rail parts that are slip-rolled
   to follow the crossbar curve.)
4. **Corner Reliefs**: rectangular reliefs at every corner, sized
   `Relief_Size` x `Relief_Size`. Add tear or circular reliefs at each
   internal corner where deck meets flange.
5. **Slot Pattern (perimeter tie-downs)**: linear pattern of slots
   `Deck_Slot_Length` x `Deck_Slot_Width` along all four sides at
   `Deck_Slot_Pitch`. Keep slot edges at least `3 x Material_Thickness` from
   any bend line. Distance from edge of slot to outer edge of deck: at least
   0.75 in to preserve material under strap loads.
6. **Crossbar Clamp Holes**: 4 holes per crossbar attachment point, sized to
   the chosen clamp's stud. DO NOT define final hole pattern until the
   commercial clamp is selected. Place as suppressed sketch with comment
   "depends on clamp selection."
7. **Anti-Whistle Features**: optional small radii on the deck leading edge,
   or a 0.5 in tall x 1 in wide formed bump (forming tool) along the front
   edge to disrupt laminar flow. Test first.
8. **Convert To Sheet Metal Flat Pattern**: verify the flat pattern unfolds
   cleanly with no overlapping geometry, no zero-width relief tabs, and no
   missing bend lines. Generate the flat-pattern DXF after design review.

### Side_Rail_L.SLDPRT / Side_Rail_R.SLDPRT (if separate)

If the deck cannot reasonably be one piece because of the crossbar curve, do
the side rails as separate slip-rolled parts:

1. **Base Flange / Tab**: long flat strip, `Platform_Length` x
   (`Side_Rail_Flange` + 0.75 in mating tab).
2. **Edge Flange**: 0.75 in mating tab folded under the deck (for screw or
   blind-rivet attachment).
3. **Slip-Roll Step**: not a Sheet Metal feature. Document in
   `fabrication-plan.md` that the side rail is hand-rolled to a large radius
   that matches the measured crossbar curve. The CAD model treats it as flat;
   the fabricator forms the curve.
4. Tie-down slot pattern same pitch as the deck so straps line up with the
   deck slots.

## Configurations (provisional)

Create three configurations driven by a design table to plan trade-offs:

| Config name | Material | Thickness | Estimated weight |
| --- | --- | --- | --- |
| `RR-AL-10ga` | 5052-H32 | 0.102 in | TBD (run script) |
| `RR-AL-1/8` | 5052-H32 | 0.125 in | heavier, stiffer |
| `RR-MS-1/8` | mild steel | 0.125 in | heaviest, cheap, needs paint/powder |

Run the design-table generator as a starter only:

```bash
python3 scripts/generate_design_table.py box-family --seed 52x48x1.5 --material 5052-aluminum
```

Then prune and rename configurations to match this part rather than a box.

## Common SolidWorks Traps For This Part

- Do NOT model the side rail bend as a sharp corner; it will fail
  to unfold or unfold with a huge gap.
- Do NOT punch the clamp holes through both the deck and the return flange
  with one extruded cut; the flange is at 90 deg and you will end up with a
  diagonal slot.
- Avoid placing tie-down slots on the bend centerline; they distort the bend.
- If the slip-rolled side rail is separate, model it as a Sheet Metal part
  with a Base Flange / Tab (flat), not as a swept feature. The "curve" is a
  shop operation, not a Sheet Metal feature.
- Do NOT apply the powder-coat finish in the SolidWorks appearance and treat
  it as planned thickness; powder adds about 0.003 to 0.008 in per side and
  affects hole fit.

## Drawing Package Targets (provisional)

- Deck flat pattern DXF (1:1, inch, layered).
- Side rail flat pattern DXF (1:1, inch, layered).
- Bend-table on deck drawing.
- Hardware schedule once clamp is selected.
- Final assembly drawing with torque callouts (requires clamp spec).

## Authority

This SolidWorks plan is design and CAD planning. It is not fabrication
authority and the part is not road-ready.
