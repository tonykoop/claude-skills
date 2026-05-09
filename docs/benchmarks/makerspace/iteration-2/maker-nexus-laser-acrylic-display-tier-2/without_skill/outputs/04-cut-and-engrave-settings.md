# Laser Settings — Edge-Lit Acrylic Award

These are conservative starting points. **Always do a 1 in test square on scrap of the same sheet first** — wattage drifts with tube age, and the Maker Nexus machines are not all calibrated identically.

## Material: cast clear acrylic, 0.25 in

### Boss LS-1416 / LS-1630 (~80W CO2, typical Maker Nexus)

| Operation | Power | Speed | Passes | Air assist | Notes |
|---|---|---|---|---|---|
| **Vector cut (outline)** | 70% | 8 mm/s | 1 | ON (high) | Should fall through cleanly. If not, slow to 6 mm/s rather than adding a pass — second passes scorch edges. |
| **Vector engrave (blue accents)** | 25% | 40 mm/s | 1 | ON | Just kisses the surface. |
| **Raster engrave (text/logo)** | 35% | 300 mm/s | 1 | ON | DPI 300. Higher DPI on clear acrylic looks muddy in edge-lit display — coarser dots scatter light better. |

### Epilog Fusion (60W) — if that's the one you book

| Operation | Power | Speed | Frequency |
|---|---|---|---|
| Vector cut | 100% | 12% | 5000 Hz |
| Vector engrave | 30% | 60% | 500 Hz |
| Raster engrave | 60% | 100% | — |

## Prep checklist

1. **Verify it's acrylic, not polycarbonate.** See Section 2 of the build packet. Read the sticker on the protective film. If unlabeled, do not cut.
2. **Leave the protective masking on both sides.** The laser cuts straight through paper masking and protects the surface from flashback debris. Peel only after you finish.
3. **Engrave the BACK side, view from the FRONT.** This means your art needs to be MIRRORED in the file before sending. Edge-lit panels look much better with the engraving on the back face — light scatters toward the viewer instead of away.
4. **Center on the bed; don't auto-rotate.** Ensures grain of any text matches your fixturing.
5. **Crank air assist.** Acrylic flares without it.
6. **Stay at the machine the entire run.** Acrylic fires are real. Have the CO2 extinguisher within arm's reach.

## Post-cut

- Peel masking immediately while still warm — adhesive comes off cleaner.
- Wipe edges with a microfiber + a drop of isopropyl. Do **not** use Windex / ammonia cleaners on acrylic, they craze it.
- Inspect cut edge: should be glass-smooth and clear. Hazy = too slow / too much power. Frosted = edge-flame possible during cut, fine for this project but noted.

## Walnut on the laser (not used in this build, but for reference)

- 0.5 in walnut cut: 80W, 70%, 4 mm/s, 2 passes, air on.
- Engrave: 30%, 400 mm/s.
