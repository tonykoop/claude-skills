# Validation Checklist: Beetleweight Wedge Chassis

Authority: design and CAD planning only. Not fabrication-ready and not
arena-cleared. Every gate below must be checked by a human on the
actual hardware — not by reading this file.

## Gate 1: Material And Stock Verified

- [ ] Stock alloy is 5052-H32 (confirmed by mill cert or supplier
      callout, not just "aluminum sheet").
- [ ] Stock thickness measured with calipers at four points on the
      sheet, all within 0.060 to 0.066 in.
- [ ] Sheet is flat, no kinks or rolling stress visible. A kinked
      sheet bends unpredictably.

## Gate 2: Test Coupon Survived

- [ ] One coupon cut from the actual stock with the actual cutter.
- [ ] Two 90 deg bends at R = T with no surface cracking visible to the
      naked eye or under a 10x loupe.
- [ ] Circular relief and square relief both held without tearing.
- [ ] M3 clearance hole at 3 x T from bend shows no visible distortion.
      Hole at 0.10 in from bend (deliberately too close) shows visible
      ovaling — confirms the rule is real and worth enforcing.

## Gate 3: Per-Part Inspection

For each of lower-tub, wedge-front, top-deck, and both wheel-guards:

- [ ] Flat blank dimensions match the SolidWorks flat pattern within
      `+/- 1/32 in`.
- [ ] All bend angles within `+/- 2 deg`.
- [ ] All M3 holes pass an M3 screw by hand, no force.
- [ ] No cracks at any relief.
- [ ] All edges deburred, no fingertip-cutting edges.
- [ ] Mass within 10 percent of estimate.

## Gate 4: Fit Check (Dry Assembly, No Threadlocker)

- [ ] Wedge-front bolts to lower-tub side walls; bolt heads sit flush.
- [ ] Top-deck sits on the hemmed top edge with no rocking.
- [ ] Wheel-guards mount with the wheel installed; wheel spins freely
      with at least 0.10 in clearance.
- [ ] Battery slides in and out through the top-panel opening.
- [ ] Power switch reachable through the rear wall notch.
- [ ] Receiver antenna has a clear path that does not get pinched by
      the top deck.

## Gate 5: Service-Access Timing

- [ ] With one M3 hex key, a niece can remove the top deck, swap the
      battery, and re-secure the top deck in under 60 seconds. Time it.
- [ ] Same for swapping a damaged wheel-guard. Target under 90 seconds.

## Gate 6: Weight Audit

- [ ] Final assembled chassis (all four parts, all hardware) at or
      under 400 g.
- [ ] Full robot (chassis + drive + electronics + battery + weapon if
      any) at or under 1360 g. Weigh on the same scale the event will
      use, or a calibrated scale of known accuracy.
- [ ] At least 20 g margin to the class limit recorded before the
      first match.

## Gate 7: Edge Safety Sign-Off (Kid-Facing Rule)

- [ ] An adult runs a fingertip along every accessible exterior edge.
- [ ] The wedge tip specifically inspected for sharpness — file chamfer
      verified.
- [ ] All four interior box-corner reliefs inspected for burrs left
      after deburring.
- [ ] If any edge fails, return to deburring before any match.

## Gate 8: Pre-Match Smoke Test

Before each event, not just before the first event:

- [ ] All twelve M3 screws checked for tightness (vibration loosens
      them across a tournament).
- [ ] No new cracks at any bend relief.
- [ ] Wheel guards still aligned and not bent inward into the tires.
- [ ] Battery strap intact, battery not swelling.

## Stop-Work Boundary

This design and these gates do not constitute event safety clearance.
Final tech-inspection at the actual event is the authority. The
skill's job here is to make sure nothing fails at the build stage that
should have been caught at the design stage.

The chassis is non-vehicle, non-overhead, non-human-carrying — it lives
inside the event's enclosed combat box. Standard arena PPE (eye
protection at minimum) applies for both the nieces and any adult
helper during build and test.

## Pass Definition

The build moves from design planning to "ready for arena tech
inspection" only when all eight gates above are checked off in writing,
with the date and the name of the person who checked them.
