# Step-by-Step Build Procedure

Total active time: 4–6 hours. Best done across two sessions (woodshop one day, laser + assembly the next) so the wood finish has time to cure.

---

## Session A — Walnut base (woodshop, ~2.5 hours)

### A1. Stock prep (15 min)
- Inspect walnut blank. Reject if you see end-checking, twist over 1/16 in across 7 in, or knots in the slot path.
- If not S4S, plane to 1.250 in thick, joint one face + one edge, rip to 2.500 in wide on the table saw with a featherboard. Then crosscut to 7.000 in on the miter saw.

### A2. Mark out (10 min)
- Mark the panel slot on the top face: 1.000 in from each end, centered front-to-back. Slot is 5.000 in long, 0.260 in wide.
- Mark a Sharpie X for the wire pass-through hole at the centerline of the slot, midway along its length.
- Mark the barrel-jack hole on the rear face: centered side-to-side, 0.500 in up from the bottom.

### A3. Route the slot (30 min)
- **Setup:** router table, 1/4 in straight bit set to 0.500 in projection. Two stop blocks clamped to the fence at 1.000 in and 6.000 in from the bit.
- **Test cut on scrap first.** Verify the actual slot width. A 1/4 in bit cuts a 0.250 in slot — for 0.25 in acrylic you want **0.260 in for slip-fit**. Achieve this by making one pass at the fence position, then nudge the fence 0.010 in and make a second pass.
- Plunge-start the cut against the right stop block, push left to the left stop block. Stopped slot, both ends closed.
- Hand-chisel the rounded slot ends square — important for the panel to seat fully.

### A4. Drill (15 min)
- Drill press, 1/4 in bit. From the floor of the slot, drill straight down 0.75 in deep — this becomes the wire pass-through to the rear cavity.
- Drill press, 5/16 in bit. From the rear face, drill in 0.625 in deep for the barrel jack pocket. Use a brad-point bit and back the workpiece with a sacrificial scrap to prevent blow-out.
- Connect the two with a hand-drill 1/4 in bit angled from the rear hole up to meet the slot pass-through. Rough is fine — wires only.

### A5. Sand (30 min)
- Random-orbit sander: 120, 180, 220.
- Hand-sand all edges with 220 to break sharpness.
- Final pass with 320 by hand, with the grain.
- Vacuum + tack-cloth.

### A6. Finish (15 min apply, then cure overnight)
- Apply Tried & True Original or Osmo PolyX with a lint-free cloth, thin coat.
- Wipe off excess after 10 minutes.
- Let cure at least 8 hours; 24 is better. **Do not** finish the inside of the slot — finish drips will trap and look bad against the lit acrylic.

---

## Session B — Acrylic + electronics + assembly (~2.5 hours)

### B1. Verify acrylic (5 min) — DO NOT SKIP
- Read the sticker on the protective film. Confirm "PMMA" / "acrylic" / "cast acrylic." If it says "PC" or "Lexan" or "Makrolon," **stop**.
- If unlabeled, do the small flame test on a scrap corner outdoors. Acrylic = clean blue-tipped flame, sweet smell. Polycarbonate = sooty acrid black smoke, self-extinguishes. If in doubt, don't cut.

### B2. Prep file (5 min)
- Open `01-acrylic-panel.svg` in LightBurn / RDWorks / Epilog driver.
- **Mirror horizontally** so the engraving will be on the back face when viewed from the front.
- Verify dimensions: 6.000 x 9.000 in.
- Assign layers: red = vector cut, blue = vector engrave (low power), black = raster engrave.

### B3. Laser cut + engrave (25 min run + 10 min setup)
- Place acrylic on honeycomb bed, masking on both sides.
- Focus on the TOP of the masking.
- Run order: raster engrave first, vector engrave second, vector cut last.
- Air assist ON throughout.
- Stay at the machine. CO2 extinguisher within reach.

### B4. Clean acrylic (10 min)
- Peel masking while warm.
- Wipe with microfiber + isopropyl. No ammonia cleaners.
- Inspect: edges should be glass-clear and smooth; engraving should be evenly frosted.

### B5. Solder LED + jack (30 min)
- Cut LED strip to ~3.0 in section (6 LEDs at 60 LED/m density). Use the marked cut lines on the strip only.
- Tin the strip's solder pads. Solder a 10 in red lead to V+ and 10 in black to GND.
- Heat-shrink each joint individually, then a single larger shrink over the pair.
- Wire the barrel jack: tip terminal = red (+12V), sleeve = black (GND). Test continuity with a multimeter before installing.
- If using a switch: cut the red lead in the middle, solder switch into the gap, heat-shrink.

### B6. Install electronics in base (15 min)
- Press-fit the barrel jack into the 5/16 in rear pocket. A drop of CA glue locks it if loose.
- Feed the LED pigtail down through the slot pass-through hole and out the back, joining the barrel-jack leads. Solder, heat-shrink.
- Peel the LED strip's 3M backing and stick it to the floor of the slot, LEDs facing UP toward the panel edge.
- Strain-relief: small dab of hot glue at the pass-through hole.

### B7. Test light (5 min)
- Plug in 12V supply. LEDs should come on.
- Check temperature after 10 min: warm but not hot. If hot, you wired it wrong — verify supply.

### B8. Final assembly (10 min)
- Slide the acrylic panel into the slot, engraved side facing AWAY from the viewer.
- Friction should be even. If too tight, sand the bottom edge of the acrylic with 400 grit. If too loose, add a thin felt shim or a tiny bead of clear silicone in the slot.
- Plug in. Confirm the engraving glows in a dim room. Field should be dark; engraving bright.

### B9. Burn-in + acceptance (30 min)
- Leave it on for 30 minutes.
- Re-check temperatures, wire integrity, and visual.
- Sign off against the acceptance criteria in the build packet.

---

## Punch list

- [ ] All edges sanded smooth, no slivers
- [ ] Walnut finish even, no streaks
- [ ] Slot width: panel slides in with light friction
- [ ] LED strip lit and even — no dark gaps
- [ ] Barrel jack flush, cable strain-relieved
- [ ] Engraving glows clearly in dim light
- [ ] Stands flat without rocking
- [ ] Photo taken for the maker's portfolio
