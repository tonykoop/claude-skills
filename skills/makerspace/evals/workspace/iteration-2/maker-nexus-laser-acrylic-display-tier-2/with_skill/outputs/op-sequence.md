# Operation sequence — Edge-Lit Acrylic Award Display

The order matters. The slot-cut on the walnut needs the *measured*
acrylic thickness, not the nominal — so cut and measure the acrylic
panel first, then cut the slot.

## Op 1 — Source and inspect material (off-shop, 30 min)

- **Tool:** caliper, eye
- **Fixturing:** none
- **Steps:**
  1. Pick walnut blank — clear, straight, no figured grain across the
     slot path. Photograph the face you'll use as "top."
  2. Acrylic sheet — verify protective film is intact on both sides.
     Confirm marked as **CAST acrylic** on the receipt or sticker.
     If extruded, accept it but expect duller engraving.
  3. Measure actual acrylic thickness with calipers in 3 places.
     Record in `design.md` Open Questions, then update slot-width
     formula.
- **Go/no-go check:** acrylic measures between 0.215 and 0.245 in
  (typical for ¼" cast); walnut is flat enough to plane to 0.750+ in.

## Op 2 — Mill walnut to size (woodshop, 45 min)

- **Tools:** jointer, planer, tablesaw, miter saw
- **Cert:** woodshop-cert (you have it)
- **Fixturing:** standard infeed/outfeed
- **Steps:**
  1. Joint one face flat on the jointer.
  2. Plane to final thickness 0.750–0.875 in (whatever your stock
     allows — taller base is fine).
  3. Joint one edge square to the planed face.
  4. Rip to width 3.000 in on tablesaw.
  5. Crosscut to length 8.000 in on miter saw, square ends.
- **Go/no-go check:** all 6 faces square to each other within 0.005 in
  across the surface. Diagonals match within 0.020 in.

## Op 3 — Cut acrylic panel on the laser (laser room, 20 min)

- **Tool:** CO2 laser cutter (`#laser-area`)
- **Cert:** laser-cert (you have it)
- **Reservation:** required
- **Material policy:** cast acrylic is on the allowed list. **Do NOT
  bring polycarbonate, PVC, vinyl, ABS, or PTFE** — all banned per
  Maker Nexus materials-policy.md.
- **Fixturing:** laser bed honeycomb; tape down corners with blue
  painters tape if sheet is wavy.
- **Toolpath:**
  1. Vector cut the 9.000 × 6.000 panel outline.
  2. Cut a 0.5" alignment notch in the bottom edge if you want
     repeatable engrave alignment in Op 5 (optional).
- **Settings (typical for 80W CO2, ¼" cast acrylic — verify against
  shop standards):**
  - Cut: 100% power, 8 mm/s, 1 pass, air assist on
  - First-time-on-this-machine: run a 1"x1" test square in the offcut
    region first to confirm clean through-cut.
- **Go/no-go check:** panel pops free without breaking, cut edges are
  flame-polished and clear (not crazed white). Measure: 9.000 × 6.000
  ±0.020 in.

## Op 4 — Cut slot in walnut base (woodshop, 30 min)

This is the dimensionally-critical op. **Use the *measured* acrylic
thickness from Op 1 + 0.012 in to set blade or bit width.**

- **Tool option A — tablesaw:** flat-tooth ripping blade, two passes
  with fence shifted ~0.005" between passes to widen kerf to target
  slot width. Set blade height to slot depth d_s = 0.560 in.
- **Tool option B — router table:** 1/4" straight bit, two passes,
  fence shifted between passes. Easier to get a flat-bottom slot for
  the LED channel.
- **Cert:** woodshop-cert
- **Fixturing:** miter gauge or sled, push-block, featherboard.
- **Steps:**
  1. Mark slot centerline on top face: 1.500 in from front edge.
  2. Mark slot endpoints: 0.990 in inset from each end of base.
  3. Make first pass; test-fit a *scrap* of the actual acrylic stock.
     Adjust fence and make second pass to bring slot to slip-fit.
  4. Stop slot ends at marks (don't run all the way through unless you
     plan to plug the ends — for this build, stopped slot is cleaner).
- **Go/no-go check:** acrylic panel slides into slot under finger
  pressure, doesn't rock, doesn't require hammer. Bottom of slot is
  flat (for LED channel in Op 5).

## Op 5 — Engrave acrylic panel on the laser (laser room, 20 min)

- **Tool:** CO2 laser cutter
- **Reservation:** required
- **Fixturing:** lay panel on bed, FRONT face up. Front face = the
  face the viewer looks at; engraving on this face frosts and scatters
  light cleanly. Back face stays smooth.
- **Toolpath:** raster engrave centered text in the 5.000 × 7.500
  safe area.
- **Settings (typical for 80W CO2, raster engrave on cast acrylic):**
  - 30% power, 300 mm/s, 500 DPI, 1 pass
  - Run a 0.5" test patch in scrap first; aim for matte-white frost,
    not yellow or melted.
- **Go/no-go check:** engraved letters are uniformly frosted, edges
  crisp at viewing distance, depth ~0.020 in (visible to the touch).

## Op 6 — Drill cable exit hole (woodshop, 10 min)

- **Tool:** drill press (or handheld with brad-point bit)
- **Cert:** woodshop-cert
- **Steps:**
  1. Mark hole center on rear face: centered side-to-side, 0.500 in up
     from bottom.
  2. Drill 0.250 in dia all the way through to the slot bottom — this
     is how the LED leads exit.
  3. Drill from the *rear face inward* with brad-point or Forstner to
     avoid blowout into the slot.
- **Go/no-go check:** hole breaks through into the slot floor cleanly.
  Run a wire through to confirm.

## Op 7 — Sand and finish walnut (woodshop, 30 min active + dry time)

- **Tools:** orbital sander, sandpaper progression 120 → 180 → 220,
  rags
- **Steps:**
  1. Sand all faces, breaking sharp arrises with a few light strokes.
  2. Vacuum and tack-cloth.
  3. Apply Watco Danish Oil per can directions: flood, wait 15 min,
     wipe off all excess. Dry overnight. 2 coats minimum.
- **Go/no-go check:** no bare spots, no gummy/wet-looking patches, no
  oil pooled in the slot (wipe slot interior thoroughly — finish in
  the slot interferes with panel fit).

## Op 8 — Install LED strip and wiring (electronics bench, 30 min)

- **Tool:** soldering iron, heat shrink, helping hands
- **Steps:**
  1. Cut LED strip to 5.980 in along marked cut line.
  2. Solder leads to barrel-jack pigtail (red = +, black = −).
  3. Heat-shrink the joint.
  4. Peel adhesive backing on strip; press strip into the channel at
     the bottom of the slot, LEDs facing UP toward the panel edge.
  5. Route wires through the cable exit hole.
  6. Apply felt feet to base bottom.
- **Go/no-go check:** plug into wall wart — strip lights up uniformly,
  no flicker, no hot spots.

## Op 9 — Final assembly and validation (bench, 15 min)

- Insert acrylic panel into slot, engraving facing forward.
- Plug in. Check that engraving glows evenly. Check from ~3 ft away —
  this is the viewing distance.
- Run through `validation.csv` checks v001–v007.

---

## Total time estimate

| Op | Time | Cumulative |
|----|------|------------|
| 1  | 0:30 | 0:30 |
| 2  | 0:45 | 1:15 |
| 3  | 0:20 | 1:35 |
| 4  | 0:30 | 2:05 |
| 5  | 0:20 | 2:25 |
| 6  | 0:10 | 2:35 |
| 7  | 0:30 + overnight | 3:05 + dry |
| 8  | 0:30 | 3:35 |
| 9  | 0:15 | 3:50 |

**Active shop time: ~4 hours** spread across two visits (separated by
finish dry time).
