# Edge-Lit Acrylic Award Display — Tier 2 Build Packet

**Maker:** [Maker Name] (cleared: laser, woodshop)
**Facility:** Maker Nexus (Sunnyvale, CA)
**Date:** 2026-05-08
**Tier:** 2 (intermediate — multi-process, multi-material, fixturing required)

---

## 1. Project Overview

A standing edge-lit acrylic award display:

- **Display panel:** 6 in W x 9 in H x 0.25 in cast clear acrylic, laser-engraved on one face.
- **Base:** solid walnut block, 7 in W x 2.5 in D x 1.25 in H, with a routed slot to receive the panel and an LED strip.
- **Light source:** 12V warm-white LED strip (or RGB), wired to a barrel jack at the rear of the base.
- **Effect:** light enters the bottom edge of the acrylic, total-internal-reflects up the panel, and scatters out of the engraved areas — making the engraving glow against the dark room.

**Estimated total time:** 4–6 hours active (plus finish cure).

---

## 2. CRITICAL — Laser Material Safety (Maker Nexus rules)

You asked specifically about acrylic types and polycarbonate. Here is the safe-to-cut answer plus the reasoning. **Always verify against the current Maker Nexus laser SOP / posted "Safe Materials" list before cutting — facility rules are the source of truth and supersede this packet.**

### SAFE on the laser (this project)

| Material | Status | Notes |
|---|---|---|
| **Cast acrylic (PMMA), clear** | SAFE — preferred for engraving | Cuts cleanly, engraves with a bright frosted-white finish. This is what you want. Brand names: Chemcast, ACRYLITE GP, Plexiglas G. |
| **Extruded acrylic (PMMA)** | SAFE to cut, mediocre to engrave | Engraving comes out grayish/clear instead of frosted-white. Cuts faster but looks worse for an award. Avoid for this build. |

### BANNED on every CO2 laser (industry-wide, and confirmed at Maker Nexus)

| Material | Why banned |
|---|---|
| **Polycarbonate (Lexan, Makrolon, "PC")** | YES — banned. Confirmed. Polycarbonate absorbs strongly in the CO2 IR band, so it doesn't cut — it catches fire, yellows, and produces toxic fumes. Visually it can look identical to acrylic. **Always check the corner sticker / data sheet, not just appearance.** |
| **PVC / vinyl / faux leather** | Releases hydrogen chloride gas — corrodes the laser optics and gantry, harms lungs. Permanent ban. |
| **ABS** | Releases hydrogen cyanide and melts rather than cuts. |
| **Fiberglass / carbon fiber composites** | Toxic resin fumes, abrasive dust. |
| **HDPE / polystyrene foam** | Catches fire readily. |
| **Anything with chlorine or bromine** | Halogen-containing fumes destroy optics. |

### How to tell cast acrylic from polycarbonate (do this before you cut)

1. **Check the protective paper/film** — supplier name and material code are printed there. "PMMA" / "acrylic" / "Chemcast" / "ACRYLITE" = OK. "PC" / "Lexan" / "Makrolon" = STOP.
2. **Flame test on a scrap (outside, away from the shop):** acrylic burns with a clean blue-tipped flame and a sweet smell; polycarbonate self-extinguishes and gives a sooty acrid smell.
3. **If you can't confirm, don't cut it.** Ask a steward.

### Walnut on the laser

Walnut is fine to engrave and cut on the CO2. Clean kerf, mild scorch. Not relevant to this build (we're machining the walnut on woodshop tools, not the laser) but noted for completeness.

---

## 3. Bill of Materials

| # | Item | Spec | Qty | Source | Est. cost |
|---|---|---|---|---|---|
| 1 | Cast clear acrylic sheet | 6 x 9 x 0.25 in, PMMA | 1 | TAP Plastics (San Jose) or Estreet Plastics online | $9–14 |
| 2 | Walnut blank | 7 x 2.5 x 1.25 in, S4S, kiln-dried | 1 | MacBeath Hardwood (Berkeley) or Maker Nexus scrap | $6–12 |
| 3 | LED strip, 12V, 5050, warm white (or RGB) | ~3 in section, ~6 LEDs | 1 | Adafruit / Amazon | $4 |
| 4 | 12V 1A power supply, 2.1mm barrel | center-positive | 1 | Adafruit | $7 |
| 5 | Panel-mount 2.1mm barrel jack | for rear of base | 1 | Adafruit | $2 |
| 6 | Inline switch (optional) | 12V rated | 1 | Adafruit | $2 |
| 7 | 22 AWG hookup wire | red/black pair, ~12 in | — | shop stock | — |
| 8 | Heat-shrink tubing | assorted | — | shop stock | — |
| 9 | Wood finish | Tried & True Original or Osmo PolyX | — | shop stock or Rockler | — |
| 10 | Clear silicone or felt shim | for non-marring panel fit | — | shop stock | — |

**Subtotal:** ~$35–45.

---

## 4. Tooling & Stations

**Laser (Maker Nexus laser room):**
- 60W or 80W CO2 (Boss / Epilog — whichever has the open booking).
- Air assist ON.
- Honeycomb bed.

**Woodshop:**
- Miter saw or table saw (cut walnut to length).
- Planer / jointer (only if blank isn't already S4S).
- Router table + 1/4 in straight bit (for the panel slot).
- Drill press + 1/4 in and 5/16 in bits (LED wiring channel and barrel-jack hole).
- Random-orbit sander, 120 / 180 / 220 grit.
- Hand sanding block, 320 grit.

**Electronics bench:**
- Soldering iron, 30–60W.
- Wire strippers, flush cutters.
- Multimeter (continuity and 12V check).

**Fixturing / consumables:**
- Painters tape + isopropyl alcohol (for masking the laser-side of acrylic).
- Push sticks and featherboards for the router table.

---

## 5. Files (in this packet)

- `01-acrylic-panel.svg` — laser cut + engrave file, 6 x 9 in, with engraving artwork placeholder.
- `02-walnut-base-plan.svg` — top/side/section drawings for the walnut base.
- `03-wiring-diagram.svg` — barrel jack -> switch -> LED strip schematic.
- `04-cut-and-engrave-settings.md` — laser settings table for Maker Nexus machines.
- `05-step-by-step.md` — the actual build procedure.
- `06-safety-checklist.md` — pre-flight checklist (sign before each session).

---

## 6. Acceptance Criteria

The award is "done" when:

1. Panel slides into the slot with light, even friction (not loose, not hammered).
2. With the LEDs on in a dim room, the engraving glows brightly and the un-engraved field stays dark.
3. No visible scorch on walnut around the slot.
4. Barrel jack is flush and tight; cable strain-relieved.
5. Walnut finish is even, no sanding scratches visible under raking light.
6. Display stands upright on a flat surface without rocking.

---

## 7. Risk & Mitigations

| Risk | Mitigation |
|---|---|
| Cutting an unknown plastic that turns out to be PC | Section 2 verification; refuse to cut anything without a label. |
| Acrylic cracking when slotted into a too-tight base | Cut slot 0.260 in wide for 0.25 in stock; test fit on scrap first. |
| Burn marks on acrylic edges | Mask both faces; air assist on; one pass at correct power; do not multi-pass. |
| Scorch on walnut from over-tight slot + LED heat | LED strip is low power (~1W); slot has air gap; not a real thermal risk but verify after 30 min burn-in. |
| Wiring short inside base | Heat-shrink every joint; multimeter continuity check before powering. |

---
