# Assembly manual — CNC Welcome Sign

## Estimated total time: 3:30 active shop time + 24h finish cure
## Tools needed: CNC router (Maker Nexus), 60° V-bit, 1/8" upcut endmill, double-sided carpet tape, hex keys for collet, vacuum, putty knife, hand sandpaper (180/220/320), foam brushes, tack cloths, drill (for mounting at home)

This is the build sequence after the design is fixed and CAM is
prepared. CAM prep happens at home; this manual starts when you
arrive at the shop.

---

### Step 1 — Set up at the CNC

- What you're doing: arrive, unpack, vacuum the spoilboard, lay out
  stock and bits.
- Tool: CNC router area
- Time: 10 min
- Photo placeholder: `images/step-01-setup.jpg`
- Notes / gotchas: vacuum any prior chips off the spoilboard
  *before* you tape down. A grain of grit under the stock will
  rock the part.

### Step 2 — Tape stock to spoilboard

- What you're doing: laying four strips of double-sided carpet tape
  on the spoilboard, lining up stock, pressing it down hard.
- Tool: double-sided carpet tape (b004), bare hands
- Time: 5 min
- Photo placeholder: `images/step-02-tape.jpg`
- Notes / gotchas: lay tape long-axis under the part, not in random
  patches. Walk on the part for 30 seconds to set the tape — that
  matters more than people expect.

### Step 3 — Install V-bit, set XY and Z origin

- What you're doing: putting the 60° V-bit in the collet, jogging
  the machine to the lower-left corner of the sign body, setting
  XY zero, then touching off Z on the top of the stock.
- Tool: CNC router, hex keys, touch-off plate
- Time: 10 min
- Photo placeholder: `images/step-03-v-bit-zero.jpg`
- Notes / gotchas: collet snug, but don't over-torque. Bit stickout
  about 1/2" — too much stickout chatters; too little risks the
  collet hitting the work.

### Step 4 — Run V-carve toolpath

- What you're doing: starting the V-carve toolpath and watching the
  first letter come out.
- Tool: CNC router (V-bit), VCarve Pro post file on USB
- Time: 30 min run + 5 min watch
- Photo placeholder: `images/step-04-vcarve.jpg`
- Notes / gotchas: stand at the e-stop until the first letter
  finishes. Listen for any change in cut sound. Burning smell =
  pause and check feed/RPM. Chatter = pause and check stickout.

### Step 5 — Tool change to 1/8" endmill

- What you're doing: swapping the V-bit for the 1/8" upcut endmill,
  then re-zeroing Z (XY stays).
- Tool: CNC router, hex keys, touch-off plate
- Time: 5 min
- Photo placeholder: `images/step-05-tool-change.jpg`
- Notes / gotchas: the bit length is different — Z-zero MUST be
  redone. Forgetting this is the #1 way people break a 1/8" bit.

### Step 6 — Run profile-cut toolpath

- What you're doing: running the outside profile cut with 6 tabs
  holding the part to the parent stock.
- Tool: CNC router (1/8" endmill)
- Time: 25 min
- Photo placeholder: `images/step-06-profile.jpg`
- Notes / gotchas: stand by the e-stop. After the first pass, the
  outline should be visible — pause briefly and confirm before
  running passes 2-3.

### Step 7 — Release the part, snap tabs, sand flush

- What you're doing: pausing the spindle, vacuuming, sliding a
  putty knife under the part, snapping the 6 tabs, hand-sanding
  the nubs with 180.
- Tool: putty knife, sandpaper, hand bench
- Time: 15 min
- Photo placeholder: `images/step-07-release.jpg`
- Notes / gotchas: don't pry with fingers — putty knife only.
  Snap tabs by flexing the part; if a tab won't snap, use a chisel.

### Step 8 — Flip and re-tape for keyhole pockets

- What you're doing: flipping the sign body face-down, taping
  again, finding XY origin off the freshly-cut profile edge.
- Tool: carpet tape, putty knife, edge-finder or eyeball
- Time: 10 min
- Photo placeholder: `images/step-08-flip.jpg`
- Notes / gotchas: this is the highest-risk alignment step. Use
  the profile edge as the reference, not the original stock corner
  (which is gone). Re-zero XY with the bit touching the lower-left
  corner edge, then offset by the 0.0625 in bit radius.

### Step 9 — Run keyhole pocket toolpath

- What you're doing: pocketing two keyhole slots into the back
  face, 0.15 in deep.
- Tool: CNC router (1/8" endmill)
- Time: 15 min
- Photo placeholder: `images/step-09-keyhole.jpg`
- Notes / gotchas: 0.15 in into 0.25 in stock leaves 0.10 in of
  substrate — fine if Z-zero was right. If Z-zero was off and you
  go to 0.20 in, you might breach the V-carve from behind. Look
  *during* the cut.

### Step 10 — Hand-sand all faces

- What you're doing: 180 → 220 across the whole sign, paying extra
  attention to V-carve edges (light pass only).
- Tool: hand sanding block, 180/220-grit paper
- Time: 30 min
- Photo placeholder: `images/step-10-sanding.jpg`
- Notes / gotchas: it is very easy to round over the V-carve edges
  if you sand too aggressively. Sand the flat surfaces, then run
  the paper *along* the V-grooves, not across.

### Step 11 — Apply sanding sealer

- What you're doing: brushing on one coat of sanding sealer (b005)
  to all faces and edges. Wait 2 hours.
- Tool: foam brush, finish bench
- Time: 15 min active, 2 h cure
- Photo placeholder: `images/step-11-sealer.jpg`
- Notes / gotchas: brush thinly. Plywood edges drink finish — hit
  edges twice. Lay flat to dry, not standing on edge.

### Step 12 — Scuff sand with 320, tack-cloth

- What you're doing: light pass with 320 to break the surface,
  then wipe with tack cloth.
- Tool: 320-grit, tack cloth
- Time: 10 min
- Photo placeholder: `images/step-12-scuff.jpg`
- Notes / gotchas: don't sand through the sealer — it's there to
  block grain raise. A *light* scuff is enough.

### Step 13 — First coat spar urethane

- What you're doing: brushing a thin coat of Helmsman spar
  urethane on all surfaces. Wait 4 hours.
- Tool: foam brush
- Time: 15 min active, 4 h cure
- Photo placeholder: `images/step-13-poly-1.jpg`
- Notes / gotchas: thin coats avoid runs. Watch for drips off the
  edges; wipe with the brush.

### Step 14 — Scuff and second coat

- What you're doing: 320-grit scuff, tack cloth, second coat of
  spar urethane. Wait 24 hours for full cure.
- Tool: 320-grit, tack cloth, foam brush
- Time: 20 min active, 24 h cure
- Photo placeholder: `images/step-14-poly-2.jpg`
- Notes / gotchas: 24 h cure is real for outdoor durability — not
  optional.

### Step 15 — Mount

- What you're doing: locating mounting screws on the wall (12.0 in
  apart, level), driving #8 × 1-1/4" pan-head screws to leave
  about 1/8" head-to-wall, hanging the sign on the keyholes.
- Tool: drill, level, tape measure
- Time: 15 min
- Photo placeholder: `images/step-15-mount.jpg`
- Notes / gotchas: the keyhole locks downward as the sign hangs,
  so screw head height matters. If a screw is too tight to the
  wall, the keyhole won't slide on; back it out 1/16" until the
  sign drops cleanly.

---

## Done.

Take the hero photo (`images/hero.jpg`) — see `photo-shotlist.md`
when Tier 3 is added.
