# Validation Checklist: RAV4 Prime Roof Rack

Authority: design and CAD planning. NOT fabrication-ready. NOT road-ready.

This checklist defines the gates a provisional rack must pass before it
moves from one risk tier to the next. The user owns each pass/fail. The
sheet-metal skill does not certify any gate as "passed."

## Gate 0 - Authority And Inputs (BEFORE fabrication)

- [ ] OEM Toyota dynamic roof load rating for the specific 2024 RAV4 Prime
      trim and options is in writing.
- [ ] Measured OEM crossbar cross-section, length, and front-to-rear spread
      are recorded (with photos and caliper readings).
- [ ] Commercially rated crossbar clamp is selected; its published working
      load and torque spec are recorded.
- [ ] Load case worksheet (`load-cases.csv`) is filled with real numbers,
      not assumptions.
- [ ] `safety-gate` decision is at PROVISIONAL or better, in writing.
- [ ] Maker Nexus instructor has confirmed the brake can handle 10 ga
      aluminum at full 48 in width.

If any of Gate 0 is unchecked, STOP. Do not cut metal.

## Gate 1 - Test Coupon (DURING fabrication)

- [ ] Test coupon 3 x 8 in cut from the same sheet as the deck.
- [ ] 90 deg test bend at planned `Inside_Bend_Radius` shows no surface
      cracks, no orange-peel, no severe thinning.
- [ ] Measured inside bend radius is within 0.020 in of design.
- [ ] Plasma kerf measured on the coupon matches the `Kerf` value in
      `parameters.csv` within 0.010 in.
- [ ] Drilled or plasma clamp-stud hole accepts the bolt with no binding
      and no shavings.

## Gate 2 - Bench Inspection (AFTER fabrication, BEFORE first load)

- [ ] Flat pattern matches the as-fabricated outline within 1/16 in.
- [ ] All bends within 1 deg of 90 deg.
- [ ] All slot edges deburred (verified by running a fingernail along each
      slot - no catch).
- [ ] All hole edges deburred and round, no spatter or dross.
- [ ] No cracks anywhere, especially at corner reliefs and bend ends.
- [ ] Deck is flat (no twist) when set on a known-flat surface.
- [ ] Hardware dry-fit; no thread interference, no clamp rotation.

## Gate 3 - Static Load Test (BEFORE going on the vehicle)

Perform with the rack mounted on two saw horses spaced at the measured
crossbar spread (not on the vehicle).

- [ ] Apply 1.5x the designed static payload (e.g., 1.5 x 135 lb = 202 lb)
      distributed evenly across the deck.
- [ ] Hold for 30 minutes.
- [ ] Inspect: no permanent deflection at center over 0.25 in, no cracks
      visible, no fastener loosening.
- [ ] Repeat with the load centered toward the rear (worst case for lumber
      cantilever).
- [ ] Repeat with a 50 lb point load at the worst stress concentration (a
      tie-down corner) for 5 minutes. No deformation.

If any part of Gate 3 fails, STOP and route the failure to maker-engineering.

## Gate 4 - Low-Speed Drive Test (LOW STAKES, parking lot / private road)

- [ ] Install on the vehicle using the commercial clamp at the
      manufacturer's torque spec.
- [ ] Mark every fastener with a torque-witness paint pen line.
- [ ] Drive at parking-lot speed (under 15 mph) with full designed payload
      for 30 minutes including aggressive cornering and a few hard stops.
- [ ] Stop, re-torque every fastener, inspect:
      - witness marks still aligned (no loosening)?
      - clamp position unchanged on bar (mark its position with paint pen
        before test)?
      - deck not making contact with vehicle roof anywhere?
      - no new cracks?
- [ ] If pass, proceed to Gate 5. If fail, stop and root-cause.

## Gate 5 - Surface Street Drive Test (LOW STAKES, low speed)

- [ ] 25 mph residential roads with designed payload, 25 miles.
- [ ] Re-torque, re-inspect at the end.
- [ ] No loosening, no clamp drift, no whistling, no rattle.

## Gate 6 - Highway Use (DOES NOT BELONG IN THIS PACKET)

The sheet-metal skill does NOT authorize highway use. To proceed past
Gate 5:

- Route the design and the test data through `maker-engineering`.
- Engage a qualified mechanical engineer or a vehicle outfitter shop for
  review.
- Get a published or written load rating from a competent authority.
- Set an inspection interval (e.g., every fueling, every long trip, every
  car wash).
- Define the stop-work conditions in writing on the vehicle (sticker on the
  rack itself).

## Stop-Work Conditions (apply at every gate)

Stop and dismount the rack immediately if any of:

- Visible crack anywhere on the deck, side rails, or near a fastener.
- Witness mark on any fastener shows movement.
- Clamp paint mark on the crossbar shows the clamp has rotated or slid.
- Any audible whistle, thump, or rattle at any speed.
- Galvanic corrosion staining at fastener interfaces (white powder for
  aluminum, rust for steel).
- Powder coat or finish chipping at a stress concentration.

## Inspection Intervals (post-installation, planning only)

- Before every load: walk-around visual and a hand-shake of every clamp.
- Every fueling: visual scan of witness marks and clamp paint marks.
- Every car wash / heavy rain trip: corrosion check at fastener interfaces.
- Every 6 months or 5,000 miles: full re-torque of every fastener and a
  crack search under good light.
- Every winter (if rack lives outside): full disassembly, isolation
  washers replaced, finish re-checked.

## Authority

This validation checklist is part of the planning packet. It is NOT a
substitute for a qualified review. It defines the user-side observations
that must pass before each next level of use.
