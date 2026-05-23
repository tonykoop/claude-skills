# Fabrication Plan: RAV4 Prime Roof Rack

Authority: design and CAD planning only. NOT fabrication-ready. The skill
does not authorize starting fabrication until the safety-gate items in
`design-brief.md` are cleared.

## Shop Profile Assumed

- GoFab CNC plasma table, 48 x 96 in bed.
- 48 in stomp shear.
- 48 in box-and-pan / finger brake.
- Floor slip roller (48 in, ~1 in min planning radius).
- TIG/MIG welding (likely not needed for this design if mechanical fasteners
  are used).
- Grinders, sanders, deburring tools, blasting cabinet.
- Maker Nexus instructor available; confirm 10 ga aluminum capacity on the
  brake before cutting stock.

Confirm all of the above against current shop policy and instructor
guidance. Posted machine limits override this skill's assumptions.

## Operation Sequence (Deck Panel)

1. **Verify stock.** Caliper-measure aluminum sheet thickness; confirm
   5052-H32 marking (or chosen alternative). Reject stock if it does not
   match `Material_Thickness` within +/- 0.005 in.
2. **Cut a test coupon.** 3 x 8 in strip from the same sheet. Use it to:
   - Confirm plasma kerf with the chosen settings.
   - Bend a 90 deg test bend on the same brake/tooling planned for the
     deck. Measure inside radius and confirm it matches
     `Inside_Bend_Radius`. Confirm no cracking on the outer fiber.
   - Drill or plasma a clamp-stud hole and check fastener fit.
3. **Plasma cut the deck blank.** Layers honored: `0-CUT` and `6-DRILL-LATER`
   (if drilling holes later) only on plasma. `1-MARK` and `2-ETCH` if the
   shop's plasma table supports marking; otherwise scribe by hand using the
   layered reference DXF.
4. **Deburr while flat.** Use deburring wheel, file, or sanding block. Inside
   slot edges and hole edges must be smooth enough that a strap will not
   chafe. Re-inspect every tie-down slot edge.
5. **Drill / ream critical holes.** Clamp-stud holes are drilled or reamed
   to final size on the drill press, NOT plasma, unless the test coupon
   showed plasma holes were round enough.
6. **Mark bend lines.** Apply layout dye and scribe bend centerlines from
   the construction layer if not already etched.
7. **Bend Edge Flanges (B1, B2 long sides first).** Set brake angle to 90
   deg with the appropriate die for `Inside_Bend_Radius`. Make B1, then B2.
   - Watch for the part trying to swing into the upper beam after B1; this
     part is wide enough that the operator may need a second set of hands
     or a roller stand on each side.
   - If B3 / B4 (short end flanges) are included, bend them AFTER the long
     sides so the part does not trap itself in the brake. If trap risk is
     high, use Closed Corner or bolt-on corner brackets instead.
8. **(Optional) Slip-roll the side rails** if separate parts: hand-roll to
   the measured crossbar curve. Mark the curve direction on the part.
9. **Trial-fit on a mock crossbar setup** before any vehicle work. Use saw
   horses with a piece of pipe or extrusion at the measured crossbar spread
   to simulate the OEM bars. Verify clamp holes align.
10. **Deburr a second time after bending.** Bending sometimes raises burrs
    at the bend ends and at the relief edges.
11. **Finish.**
    - 5052 aluminum: blast cabinet for a matte uniform finish, then either
      leave bare (anodize at vendor) or apply marine-grade polyurethane.
    - Powder-coat option requires the deck to be free of oil and the holes
      to be masked. Powder adds 0.003 to 0.008 in per side; recheck hole
      fit afterward.
    - If mild steel chosen instead: media blast, prime with zinc-rich
      primer, then powder coat. No bare areas under the clamps.
12. **Install hardware (DRY-FIT first).** Use stainless M8 hardware with
    nylon washers between fastener and aluminum to limit galvanic action.
    Anti-seize on threads. Loctite 243 (blue) on every clamp-stud nut.
    Torque to the clamp manufacturer's spec. Do NOT guess torque.
13. **Inspect.** See `validation-checklist.md`.

## Operation Sequence (Side Rails, if separate slip-rolled parts)

1. Shear strips from the same sheet on the 48 in stomp shear.
2. Plasma or laser any tie-down slots while strip is still rectangular.
3. Deburr.
4. Form the 0.75 in mating tab on the brake first.
5. Slip-roll the strip to the measured crossbar curve. Plan unbent flats at
   the leading and trailing edges (typical roller leaves about 1 to 2 in
   unbent at each end). Either:
   - trim the unbent flats off, or
   - pre-form them with a hand brake / press brake before rolling.
6. Trial-fit against the deck and drill matching screw or rivet holes
   in-place to guarantee alignment.
7. Deburr again, finish, install.

## Joining Strategy

- **Primary load path:** commercial rated clamp around OEM crossbar -> M8
  stud -> deck through-hole -> stainless flat washer -> Nyloc nut OR
  Nyloc + Loctite.
- **Deck to side rail (if separate):** stainless M5 button-head machine
  screws on 4 in pitch with nylon washers under heads and Nyloc nuts.
- **NO** self-tappers anywhere on the load path.
- **NO** rivets in any joint that carries the rack to the vehicle.
- **NO** welding aluminum unless the user has a documented TIG procedure for
  5052; not recommended for this design.

## Fastener Anti-Loosening

- Nyloc nuts AND blue Loctite on all clamp-to-deck fasteners.
- Mark fasteners with a torque-witness paint pen line after final torque so
  loosening is visible at inspection.
- Re-torque after 5, 25, 100 miles of carrying load (see validation).

## Corrosion And Finish

- All hardware: stainless, with HDPE or nylon washer between hardware and
  aluminum deck.
- Bare aluminum touching clamp: acceptable if both are aluminum; verify
  clamp material. If clamp is steel or zinc-plated, add a nylon isolation
  pad between clamp and deck.
- Anodize or powder-coat preferred for long-term outdoor storage. Bare 5052
  patinas but does not flake.

## Tools That Will And Will Not Get Used

- Will use: plasma, brake, shear, drill press, deburring wheel, blast
  cabinet.
- Will probably skip: TIG, MIG (this design is mechanically fastened).
- Will use later, outside of fabrication: torque wrench (clamp manufacturer
  spec), torque-witness paint pen.

## Authority Reminder

This fabrication plan is design and CAD planning. No part may be installed
on the vehicle until the load case worksheet (`load-cases.csv`) is filled
with real numbers, the OEM rating is confirmed, a commercially rated clamp
is selected, and `maker-engineering` review is complete.
