# Assembly manual — Edge-Lit Acrylic Award Display

## Estimated total time

- Active shop time: ~4 hours
- Plus overnight finish dry between shop visits

## Tools needed

- Calipers (digital, 6")
- Pencil, marking gauge or square + knife
- Tablesaw OR router table
- Jointer, planer
- Miter saw
- Drill press with 0.250" brad-point or Forstner bit
- Random orbital sander, 120/180/220 grit
- CO2 laser cutter (Maker Nexus laser room)
- Soldering iron, helping hands, heat-shrink kit
- Multimeter (continuity check)

## Step 1 — Inspect and measure stock

- What you're doing: confirming the acrylic is cast (not extruded, not
  polycarbonate by mistake) and recording its actual thickness.
- Tool: calipers, eye, receipt
- Time: 10 min
- Photo placeholder: `images/step-01-stock.jpg`
- Notes / gotchas: TAP Plastics labels cast vs extruded on the sheet
  edge. If the sheet feels rubbery or the receipt says "Lexan," it's
  polycarbonate and is **banned on the laser** — return it.

## Step 2 — Update design.md with measured thickness

- What you're doing: plug measured t_p into the design and recompute
  slot width.
- Tool: calculator + design.md
- Time: 5 min
- Photo placeholder: none
- Notes / gotchas: write the value in pencil on the back of the
  walnut blank too — that way you can't forget at the saw.

## Step 3 — Mill walnut to 8.000 × 3.000 × 0.750–0.875 in

- What you're doing: turn S4S stock into a square, flat, sized base
  blank.
- Tool: jointer → planer → tablesaw → miter saw
- Time: 45 min
- Photo placeholder: `images/step-03-millwork.jpg`
- Notes / gotchas: keep one face marked as "top" — the slot goes in
  it. Square the ends with a chop on the miter saw.

## Step 4 — Laser-cut acrylic panel to 9.000 × 6.000 in

- What you're doing: cut the panel from the 12×24 sheet on the laser.
- Tool: CO2 laser cutter (`#laser-area`)
- Time: 20 min including setup
- Photo placeholder: `images/step-04-lasercut.jpg`
- Notes / gotchas: leave protective film on the *back* face during
  cut (protects against flashback marks); peel front face film if it
  resists clean cuts. Run a 1×1 test square first.

## Step 5 — Cut slot in walnut base

- What you're doing: cutting the slip-fit slot using measured acrylic
  thickness + 0.012 in for the target slot width.
- Tool: tablesaw with flat-tooth blade OR router table with 1/4"
  straight bit
- Time: 30 min
- Photo placeholder: `images/step-05-slotcut.jpg`
- Notes / gotchas: **test on a scrap piece first.** Adjust fence in
  0.005 in increments until panel slides in with finger pressure and
  doesn't rock. Don't over-widen — you can always recut wider, never
  narrower.

## Step 6 — Drill cable exit hole

- What you're doing: 0.250" hole through rear face into slot floor.
- Tool: drill press, 0.250" brad-point bit
- Time: 10 min
- Photo placeholder: `images/step-06-cablehole.jpg`
- Notes / gotchas: drill from the outside in. Back up the hole with
  scrap to prevent blowout into the slot.

## Step 7 — Engrave acrylic panel on the laser

- What you're doing: raster engrave the text onto the front face of
  the panel.
- Tool: CO2 laser cutter, raster mode
- Time: 20 min
- Photo placeholder: `images/step-07-engrave.jpg`
- Notes / gotchas: engrave through the protective film if it's thin
  (most are designed for this). Test settings on a scrap acrylic
  square first. Yellow tint = power too high; faint = power too low.

## Step 8 — Sand and finish walnut base

- What you're doing: 120 → 180 → 220 sanding, then Danish oil.
- Tool: orbital sander, rags
- Time: 30 min sanding + overnight cure
- Photo placeholder: `images/step-08-finishing.jpg`
- Notes / gotchas: tape the slot interior shut with painters tape
  before sanding to keep dust out. Wipe oil out of the slot
  thoroughly — finish in the slot interferes with panel fit and traps
  the LED strip.

## Step 9 — Assemble LED strip and wiring

- What you're doing: solder the LED strip to a barrel-jack pigtail
  and seat it in the slot.
- Tool: soldering iron, heat-shrink, multimeter
- Time: 30 min
- Photo placeholder: `images/step-09-led.jpg`
- Notes / gotchas: COB strips usually have copper pads marked + and
  −. Check polarity with the multimeter against the wall wart's
  center-positive pin before final solder. Heat-shrink the joint
  before powering.

## Step 10 — Final assembly and light-up

- What you're doing: insert the panel, plug in, validate.
- Tool: hands
- Time: 15 min
- Photo placeholder: `images/hero.jpg`, `images/step-10-glow.jpg`
- Notes / gotchas: run validation checks v010–v013. If glow is
  uneven, the strip likely shifted during install — pop the panel,
  reseat the strip, retry.
