# Safety notes — CNC Welcome Sign

Build-specific safety notes. Not a substitute for the Maker Nexus
shop-safety orientation and CNC certification — those are
prerequisites, not optional reading.

## PPE for this build

- ANSI Z87.1 safety glasses — entire CNC run. Chips fly.
- Hearing protection — the spindle at 18,000 RPM is loud; routing BB
  at 80 ipm is louder.
- N95 dust mask — baltic birch dust is fine and continuous during
  the profile cut. Run the dust shoe / vacuum throughout.
- Closed-toe shoes, no loose sleeves.

## Tool-specific risks

- **CNC router:** never reach into the work envelope while the
  spindle is running. Use the e-stop, not the door, to bring the
  machine to a stop if something goes wrong.
- **V-bit:** the tip is thin and brittle. A plunge into a void or a
  knot will shear the tip. Baltic birch is chosen specifically
  because it's voidless — but inspect each sheet before cutting.
- **1/8" endmill:** small bits snap at high feed rates. Stick to
  60-80 ipm at 18,000 RPM, 0.10 in per pass on the profile cut.
- **Carpet tape:** fingertips stick to it; once it's set, it really
  doesn't want to release. Use a putty knife to lift the part, never
  pry with fingers.

## Material-specific risks

- **Baltic birch dust:** very fine, lingers in the air, irritates
  eyes and lungs. The CNC area's dust collection should be running;
  if it's not, stop and fix before you cut.
- **Voidless ply:** baltic birch is voidless on real BB stock. If
  the stock is "birch ply" from a big-box store with a Lauan core, a
  V-bit can suddenly drop into a void and chip out. This packet
  spec'd MacBeath Berkeley BB explicitly to avoid that.
- **Finish (spar urethane):** flammable, VOC-bearing. Apply in a
  ventilated area; rags can spontaneously combust if balled up wet.
  Lay rags flat to dry, then dispose.

## Process-specific risks

- **Stock movement during cut:** if the carpet tape lets go
  mid-profile, the part can grab the bit and fling. Mitigation:
  walk-on the tape to set, leave 6 tabs in the toolpath, listen for
  any change in cut sound.
- **Z-zero error after tool change:** between Op 5 (V-bit) and Op 6
  (endmill), bit length changes. Re-zero Z. Forgetting to do this
  either snaps the endmill on the spoilboard or air-cuts the
  profile.
- **Flip alignment for keyhole slots (Op 10):** if XY origin is off
  on the flipped setup, the keyhole slots end up off-center. Mitigation:
  reference off the freshly-cut profile edge, not off the original
  stock corner.

## Emergency / fire / fume notes

- E-stop on the CNC is a red palm button. Know where it is before
  you start.
- A spindle-on, no-feed condition (cutter dwelling at depth) burns
  baltic birch in seconds. If the controller hangs, hit e-stop.
- No solvent finishing inside the CNC area. Move to the finish bench
  or take it home for Op 12. Don't bring rags soaked in spar
  urethane near machine tools.
- Fire extinguisher locations: confirm before starting (CNC area
  should have a Class A/B/C within ~15 ft).
