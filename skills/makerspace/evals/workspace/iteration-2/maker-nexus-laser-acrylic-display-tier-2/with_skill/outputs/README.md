# Edge-Lit Acrylic Award Display

A 6"×9" quarter-inch clear-acrylic panel with engraved lettering, slotted
into a walnut hardwood base with an inset LED strip that side-fires up
through the panel edge. The engraving glows against a dark walnut
backdrop.

- **Shop:** Maker Nexus (Sunnyvale, CA)
- **Tier:** 2 — Portfolio-ready
- **Maker certs needed:** Shop Safety, Woodshop, Laser (already cleared)
- **Estimated build time:** 4–5 hours of shop time + finish dry time
- **Estimated material cost:** ~$45 + LED strip + power supply

## Hero photo

`images/hero.jpg` — final piece lit, slightly raking, dark room, no
hands. (Placeholder — capture after final assembly.)

## File map

| File | Tier | Purpose |
|------|------|---------|
| `README.md`            | 2 | This file — front door |
| `design.md`            | 1 | Parametric design + critical dimensions |
| `bom.csv`              | 1 | Bill of materials |
| `cut-list.csv`         | 1 | Stock plan / part list |
| `op-sequence.md`       | 1 | Ordered manufacturing operations |
| `safety-notes.md`      | 1 | Build-specific safety risks |
| `sourcing.csv`         | 2 | Vendors, SKUs, lead times, alternates |
| `validation.csv`       | 2 | Verification checks |
| `assembly-manual.md`   | 2 | Step-by-step build |
| `risks.md`             | 2 | Failure modes from red-team review |
| `drawing-brief.md`     | 2 | Drawing pack description (drawings/ TBD) |

## Quick start

1. Read `design.md` for the parametric model — every dimension flows
   from there.
2. Pull `bom.csv` and `sourcing.csv` to source materials before booking
   shop time. The acrylic is the long-lead item if ordered online.
3. Read `safety-notes.md` and `risks.md` *before* loading material into
   any machine.
4. Follow `op-sequence.md` to walk into the shop with a plan; use
   `assembly-manual.md` once you're at the bench.
5. As you build, fill in `validation.csv` so the next build inherits
   the lessons.

## Materials policy — the polycarbonate question

You asked: *what acrylic types are okay for the laser, and is
polycarbonate really banned?*

**Confirmed against `spaces/maker-nexus/materials-policy.md`:**

- **Cast acrylic (PMMA): OK on the laser.** Cuts cleanly, engraves with
  a frosted-white finish, ideal for edge-lit work.
- **Extruded acrylic (PMMA): OK on the laser.** Cuts fine; engraving
  comes out grayer/duller than cast — cast is preferred for edge-lit
  visibility.
- **Polycarbonate (Lexan / PC): BANNED on the laser.** Listed in the
  universal bans on `materials-policy.md`. Polycarbonate yellows,
  catches fire, and produces toxic fumes under a CO2 beam.
- **Other banned materials on the laser** (from the same policy doc):
  PVC and vinyl (chlorinated → hydrochloric acid, eats the optics and
  the lungs), ABS (cyanide-bearing fumes), PTFE / Teflon (fluoride).

For this project, **specify cast acrylic.** TAP Plastics in Mountain
View stocks 6"×9" off-the-shelf or will cut a 12"×24" sheet to size.

## Project intent

The award is a small, quiet object — clear panel, dark base, engraved
text, single warm-white LED strip. The visual idea is the lettering
"floating" inside the acrylic. The build emphasizes:

- Tight slot fit between acrylic and walnut (panel sits plumb without
  glue).
- Clean engraving on the front face only — back face left untouched
  so light scatters off the engraved face cleanly.
- Hidden cable channel routed out the back of the walnut base.

## Next actions

After the build, return to the packet and:

1. Fill `pass`/`fail` into `validation.csv`.
2. Drop process and detail photos into `images/`.
3. If you change LED type or supply voltage, update `bom.csv` and
   `sourcing.csv`.
4. If anything in the slot fit was off, log a `record_measurement.py`
   entry against `v005` so the empirical-learning loop can correct
   the next slot-cut.
