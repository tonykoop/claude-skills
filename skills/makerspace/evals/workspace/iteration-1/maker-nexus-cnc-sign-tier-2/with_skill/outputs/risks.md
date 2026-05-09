# Risks — CNC Welcome Sign

For each risk: severity (low/med/high), description, root cause,
mitigation, *test* (how you verify the mitigation worked).

## High severity

### V-carve breakthrough on back face

- **Severity:** high
- **Description:** A V-carve toolpath cuts deeper than 0.125 in
  (= t/2) and breaks through to the back of the 1/4" stock,
  ruining the sign.
- **Root cause:** Default V-carve toolpaths in VCarve Pro size depth
  to letter geometry; large open letterforms can want depth >
  stock/2. If "flat-depth limit" isn't set, the toolpath obeys
  geometry and ignores stock thickness.
- **Mitigation:** In VCarve Pro, set "Flat depth" to 0.125 in on
  the V-carve toolpath. Confirm in 3D simulation that the deepest
  letter shows a flat bottom, not a vee.
- **Test:** Before running on stock, simulate the toolpath in
  VCarve and inspect the deepest stroke (typically the inner of
  the 'O' or the 'E' counters). PASS = simulation shows max depth
  ≤ 0.125 in across all letters. FAIL = any letter shows >0.125 in.
  Backstop test: after Op 5, backlight the sign with a phone
  flashlight; PASS = no light through the back, FAIL = any light.

### Z-zero error on 1/8" endmill after tool change

- **Severity:** high
- **Description:** After swapping the V-bit for the 1/8" endmill,
  the operator forgets to re-zero Z. Either the 1/8" bit snaps on
  the spoilboard (if it's longer than the V-bit) or the profile
  air-cuts and doesn't release the part (if it's shorter).
- **Root cause:** The two bits are different lengths; XY origin is
  preserved across tool change but Z origin is not.
- **Mitigation:** Op 6 in the op-sequence explicitly calls out
  "re-zero Z." Make it a checkbox on a printed shop card.
- **Test:** After Op 6 and before pressing Cycle Start on the
  profile toolpath, jog Z to Z=0.005 above stock. PASS = bit just
  clears the surface. FAIL = bit is buried in the surface OR the
  bit is more than ~0.05 in above the surface.

## Medium severity

### Carpet tape lets go mid-cut

- **Severity:** medium
- **Description:** The double-sided carpet tape releases during the
  profile cut. The part is grabbed by the bit and either flung or
  destroyed.
- **Root cause:** Tape was laid on a dusty spoilboard, or stock
  wasn't pressed down hard enough to set the tape.
- **Mitigation:** Vacuum spoilboard before taping. Lay strips along
  the long axis. Walk on the part for 30 sec to set.
- **Test:** Before Op 5, lift one corner with a fingernail. PASS =
  no movement. FAIL = any lift. If it lifts, peel and re-tape.

### Keyhole-flip alignment off

- **Severity:** medium
- **Description:** When the sign body is flipped face-down for Op
  10, the new XY origin is set incorrectly and the keyhole slots
  end up off-center.
- **Root cause:** The original stock corner is gone after the
  profile cut, so the operator must reference off the freshly-cut
  profile edge — which requires offsetting by the bit radius.
- **Mitigation:** Op 10 explicitly calls out the bit-radius offset.
  Use a 1-2-3 block or square against the profile edge to set the
  bit position before zeroing.
- **Test:** After zeroing in Op 10, jog to (12.0, 0). PASS = bit
  is over the location of the second keyhole slot, mirrored from
  the first. FAIL = bit is somewhere visibly wrong.

### Spar urethane runs on edges

- **Severity:** medium
- **Description:** First or second coat of spar urethane drips off
  the bottom edges and pools, leaving runs that show under raking
  light.
- **Root cause:** Foam brush over-loaded; sign laid flat means
  edges are vertical and gravity pulls finish off them.
- **Mitigation:** Apply thin coats. Use the brush to wick drips
  off edges before they cure.
- **Test:** 30 minutes after each coat (still tacky), inspect all
  four edges under raking light. PASS = no drips, no pooling.
  FAIL = drip visible — wipe with a clean foam brush before cure.

## Low severity

### Stock thickness variance breaks math

- **Severity:** low
- **Description:** A baltic birch sheet that measures 0.245 or
  0.260 in (instead of nominal 0.250) shifts the breakthrough
  margin by a few thou.
- **Root cause:** Manufacturing tolerance on imported BB.
- **Mitigation:** Caliper the sheet on arrival. If thickness is
  outside [0.245, 0.260], adjust V-carve flat-depth to (t/2 −
  0.005) for safety.
- **Test:** Calipers on four corners and center of the stock.
  PASS = all five within [0.245, 0.260]. FAIL = any outside →
  adjust flat-depth before CAM post.

### Tab nubs proud of perimeter after sanding

- **Severity:** low
- **Description:** The 6 tabs from the profile cut leave nubs that
  catch a fingernail along the edge.
- **Root cause:** Tab height of 0.06 in is small enough to be
  missed during fast sanding.
- **Mitigation:** Op 11 specifies 180-grit on the edge until smooth.
- **Test:** Slide a fingernail along the perimeter. PASS = no
  catch. FAIL = nub felt → sand more.

### Mounting screw heads too tight to wall

- **Severity:** low
- **Description:** Screws are driven flush; the keyhole slot
  doesn't slide onto them.
- **Root cause:** Keyhole is designed for a screw head with a
  stand-off gap (~1/8 in); flush screws have no clearance.
- **Mitigation:** Step 15 of the assembly manual calls out
  ~1/8 in head-to-wall standoff.
- **Test:** Try to slide the sign onto the installed screws. PASS
  = sign drops on and locks. FAIL = sign hits the heads → back
  screws out 1/16 in, retry.

## Risks considered and dismissed

- **Lauan-cored "birch ply" voids:** dismissed because the BOM
  specifically calls for Baltic Birch from MacBeath, which is
  voidless. Risk re-applies if user substitutes big-box "birch ply."
- **Laser-cutter material policy violation:** dismissed because the
  laser is not used in this build. (User isn't cleared on it
  anyway.)
- **Aluminum/ferrous on the CNC:** dismissed because materials
  policy bans it and this build doesn't need it.
- **Solvent fume in the CNC area during finish:** dismissed because
  Op 12 (finish) is offsite or at the dedicated finish bench, not
  near the router.
- **Bit chatter on V-carve due to long stickout:** dismissed
  because Op 5 fixes stickout at ~1/2 in. Re-applies if user
  extends stickout.
- **Heat buildup on plywood:** dismissed because feeds/speeds in
  Op 5 and Op 8 are conservative; baltic birch at 18,000 RPM and
  60-80 ipm doesn't burn unless the bit dwells.
