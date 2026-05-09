# Safety notes — Edge-Lit Acrylic Award Display

Build-specific safety. The general shop rules in
`spaces/maker-nexus/safety-rules.md` still apply.

## PPE for this build

- Safety glasses — entire shop time, no exceptions on the woodshop
  side. Laser room: shop-issued safety interlock on the lid; do not
  defeat it.
- Hearing protection — tablesaw, planer, jointer, router.
- N95 or better — when sanding walnut. Walnut dust is a known
  sensitizer; some makers develop reactions over time.
- No gloves on the tablesaw or any rotating tool — gloves can be
  pulled into the blade.

## Tool-specific risks

- **Laser:** never leave running unattended. Acrylic can ignite if a
  setting is wrong or focus is off — keep the fire extinguisher in
  view. Air assist must be on for cuts.
- **Tablesaw (slot cut):** narrow, captive cut between fence and
  blade. Use a push-block, never your fingers. The slot cut is a
  through cut on the top face only — blade must be set to slot depth
  (0.560 in), not full kerf.
- **Router table:** if used for slot cut, climb-cut risk if pushing
  the wrong direction. Confirm feed direction with featherboard
  pointing the right way.
- **Planer/jointer:** read the grain on the walnut blank; reverse the
  feed direction if you see tearout.
- **Drill press:** clamp the workpiece; do not hand-hold. Walnut at
  3 in wide can grab and spin.
- **Soldering:** ventilation, no inhaling solder fume directly. Don't
  set the iron on the wood base.

## Material-specific risks

**This is the section the skill flags as critical for this build.**

- **Cast acrylic on the laser: ALLOWED.** Listed in
  `spaces/maker-nexus/profile.yaml` `laser-area.allowed_materials`.
  Cuts cleanly with air assist, mild non-toxic odor.
- **Extruded acrylic on the laser: ALSO ALLOWED.** Same chemistry
  (PMMA), engraves duller; cast is preferred for this edge-lit build
  but extruded won't hurt anything.
- **Polycarbonate (Lexan/PC): BANNED on the laser.** Universal ban in
  `materials-policy.md`. Polycarbonate yellows, ignites, and produces
  toxic smoke under the CO2 beam. *Do not bring it into the laser
  room.* If unsure whether a sheet is acrylic or polycarbonate, the
  receipt or supplier's spec sheet is the answer — visual ID is
  unreliable.
- **PVC / vinyl: BANNED everywhere on the laser.** Releases
  hydrochloric acid that destroys the optics and your lungs. (One
  more banned material called out per the materials policy.)
- **Also banned on the laser:** ABS (cyanide-bearing fumes), PTFE /
  Teflon (fluoride-bearing fumes). Do not bring any of these.
- **Acrylic dust** (from sanding edges): mild irritant; wear N95 if
  cleaning up panel edges with sandpaper.
- **Walnut dust:** sensitizer; respiratory PPE during sanding,
  especially for a closed laser-room — sand in the woodshop area, not
  near the laser.
- **Danish oil rags:** spontaneous combustion risk. Lay flat to dry
  outside, or submerge in water before discarding.

## Process-specific risks

- **Slot cut depth:** running the tablesaw blade too tall risks
  cutting through the bottom of the base — set the blade height
  carefully and use a scrap test piece.
- **Acrylic chipping during fit-up:** push the panel into the slot
  with even pressure. If it binds, *don't hammer it* — recut the
  slot 0.005 in wider rather than crack the panel.
- **LED strip orientation:** strip must face *up* toward the panel
  edge, not sideways. Backwards LED = no edge-lit effect.
- **Cable strain:** the cable exit is small (0.250 in) — leave a
  service loop inside the slot before adhering the strip so a tug
  on the cable doesn't pull the joint.

## Emergency / fire / fume notes

- Fire extinguisher: laser-room near the door. Know its location
  before powering up.
- Smoke alarm: laser-room exhaust can saturate the alarm if a cut
  goes wrong. If alarm sounds, hit the e-stop on the laser, evacuate,
  and pull staff.
- Fume extraction: confirm shop's laser exhaust is running before
  starting any cut. No exhaust = no cut.
- First aid: kit in the main shop; AED at the front desk.
