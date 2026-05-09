# CNC V-Carved Welcome Sign

A portfolio build packet for a small "WELCOME" sign routed on a CNC machine at
**Maker Nexus** (Sunnyvale, CA). The sign is V-carved into 1/4" Baltic birch
plywood at roughly 18 in x 6 in, finished with hand-rubbed oil, and sized for a
front-door or entryway installation.

---

## Project at a glance

| Field | Value |
|---|---|
| Sign size | 18.000 in x 6.000 in (457 x 152 mm) |
| Stock | Baltic birch plywood, 1/4" nominal (~6 mm actual) |
| Stock blank size | 20 x 8 in (cut from a 24 x 30 in B/BB sheet) |
| Letters | "WELCOME", V-carved, ~3 in cap height |
| Typeface | Single-line / V-carve friendly serif (e.g. *Trajan Pro*, *Cinzel*, or *EB Garamond Caps*) |
| Carve tool | 60 deg V-bit, 1/4" shank |
| Pocket/profile tool | 1/8" two-flute upcut |
| Finish | Sand to 220, two coats Osmo Polyx-Oil 3032 satin |
| Estimated CNC runtime | ~25 min (V-carve + perimeter cut) |
| Total project time | ~3.5 hr including setup, sanding, finish |
| Skill clearances required | Maker Nexus Woodshop + CNC Router (the user has both) |
| Skill clearances NOT used | Laser (deliberately avoided per scope) |

---

## Repository layout

```
.
|-- README.md                  This file - overview, build narrative, photos
|-- docs/
|   |-- 01-design-brief.md     Goals, constraints, design decisions
|   |-- 02-build-process.md    Step-by-step shop log
|   |-- 03-safety-and-ppe.md   Hazards, PPE, machine-specific notes
|   |-- 04-finishing.md        Sanding schedule and oil-finish procedure
|   |-- 05-lessons-learned.md  What I'd do differently next time
|-- cad/
|   |-- sign-layout.svg        Vector layout of the sign (placeholder)
|   |-- sign-dimensions.md     Dimensioned drawing in markdown/ASCII
|-- cam/
|   |-- toolpaths.md           Tool list, feeds & speeds, op order
|   |-- post-and-machine.md    Machine, post-processor, fixturing notes
|-- bom/
|   |-- bom.csv                Bill of materials (machine-readable)
|   |-- bom.md                 Bill of materials (human-readable)
|   |-- sourcing-notes.md      Where to buy, prices, substitutes
|-- photos/
|   |-- README.md              Shot list for documenting the build
```

---

## Build narrative (short version)

1. **Design** the sign in Inkscape or Illustrator: 18 x 6 in artboard, "WELCOME"
   in a V-carve-friendly serif, centered, with a 0.125 in inset rectangular
   border.
2. **CAM** in VCarve Pro / Carbide Create / Fusion: V-carve toolpath for the
   letters and border, plus a 2D profile toolpath with tabs for the perimeter.
3. **Stock prep:** cut a 20 x 8 in blank from a 24 x 30 in Baltic birch sheet
   on the table saw, joint one edge for fence reference.
4. **Fixture:** double-sided tape blank to a sacrificial MDF spoilboard, X/Y
   zero at lower-left, Z zero on top of stock with a touch plate.
5. **Cut:** V-carve first (cleanest letters when stock is fully captured), then
   perimeter profile last with tabs.
6. **Release & finish:** snap tabs with a flush-trim saw, sand 120 -> 180 -> 220,
   ease all edges, two coats Osmo Polyx-Oil with light 320 buff between coats.
7. **Photograph** for the portfolio (see `photos/README.md` for shot list).

The full step-by-step is in [`docs/02-build-process.md`](docs/02-build-process.md).

---

## Status & known unknowns

This packet is written **before** the cut. Items I did not verify and would
confirm in person at Maker Nexus before running:

- [ ] **Exact CNC make/model on the floor.** Maker Nexus's published equipment
  list should be checked. I assumed a hobby-class 3-axis router (ShopBot Desktop
  or Onefinity-class) with a ~24 x 18 in work envelope, which is more than
  enough for a 20 x 8 in blank. Feeds & speeds in `cam/toolpaths.md` are
  conservative starting points and should be tuned to whatever machine and
  spindle/router are actually installed.
- [ ] **Member rate, reservation system, and material-fee policy** at Maker
  Nexus - confirm at the front desk. The price column in `bom/bom.csv` reflects
  *retail* material cost only, not shop time.
- [ ] **Approved adhesives / fixturing methods.** Some shops ban CA glue or
  certain double-sided tapes near the CNC. Verify before bringing your own.
- [ ] **Dust-collection setup.** Note in `docs/03-safety-and-ppe.md` assumes a
  shop-provided dust shoe; confirm it's present and working.
- [ ] **Bit availability.** Confirm whether Maker Nexus stocks 60 deg V-bits and
  1/8" upcuts in the tool crib, or whether members bring their own.

Everything marked `TBD` or `[verify]` in the rest of the packet falls into the
same category - factual gaps I'd close before cutting, not creative decisions.

---

## License

Design files and documentation released under **CC BY 4.0**. Attribution
appreciated; commercial use permitted.
