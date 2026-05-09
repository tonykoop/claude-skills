# 05 - Plasma Setup Card

Settings below are typical for **Hypertherm Powermax 85** on 1/4" mild steel. **Verify against Maker Nexus's actual machine and consumable manual** - the shop has a laminated quick-reference card by the table; trust that over this document.

## Machine settings (starting point)

| Parameter | Value | Notes |
|---|---|---|
| Amperage | 65 A | Sweet spot for 1/4" mild on Powermax 85; higher = wider kerf, more dross |
| Cut speed | 60 ipm | Slow enough for tight curves; CAM will auto-modulate |
| Pierce delay | 0.5 s | Increase to 0.7 s if pierces don't clear |
| Pierce height | 0.15" | Standard |
| Cut height | 0.06" | Standard |
| Air pressure | 90 psi at the torch | Check regulator under load, not at rest |
| Voltage (THC) | 128 V auto-set | If shop's table has torch height control, leave on AUTO |

## Consumable check

Before you fire:
- **Electrode**: pit depth < 0.040". If deeper, replace.
- **Nozzle/tip**: orifice round, not oval. If oval, replace - oval orifice = beveled cut and dross.
- **Swirl ring**: clean, no carbon buildup in the slots.
- **Shield**: no craters, no slag stuck to face.

A tired consumable on a 6-foot single-pass cut will degrade halfway through and you'll see a clear quality cliff in the lower half of the trellis. **Start with fresh tip and electrode.**

## Air supply

- Compressor must keep 90 psi at the torch DURING cut, not just at idle.
- 1/4" plate at 65A pulls ~7 SCFM. Most makerspace compressors handle this fine but verify recovery cycle is short.
- If pressure sags, your cut will dross out and the kerf will close - expensive failure mode.
- Use **dry, oil-free air**. Inline desiccant filter is mandatory; oil contamination shortens electrode life by 5x.

## Material setup

- Plate must be **flat**. Check with a straightedge - 1/4" hot-rolled can have 0.05-0.10" bow over 78". If bowed, weight the corners or pre-flatten.
- Slat bed must be **clean of slag** under the cut areas - slag buildup deflects torch and wrecks the cut. Scrape slats before loading.
- Ground clamp directly to the plate, **not** the table frame, on a clean (descaled) spot. Bad ground = inconsistent arc.
- Magnetic plate squares can hold a thin offcut against the main piece if you want to nest the bracket plates next to the trellis.

## CAM software notes

The shop likely uses SheetCAM or Fusion 360's Manufacture workspace driving a Plasma post.
- Set kerf width to **0.060"** (verify with test cut and adjust).
- Enable **lead-in/lead-out arcs**, 0.25" radius, on closed paths.
- Enable **automatic corner slowdown** (G64 or equivalent).
- Set **plunge feed = pierce only**, not whole cut.
- Generate **toolpath preview** and visually walk through it BEFORE posting G-code. Look for: (a) lead-ins inside scrap, (b) pierces never on the cut line, (c) tab placements where you specified.

## What to do if it goes wrong mid-cut

- **Pause** (not estop) if a small feature drosses or the kerf closes - you can retry that feature.
- **Estop** if the torch crashes, the part lifts off the slats, or you smell burning rubber (cable damage).
- **Walk away with shop staff** if the table catches fire (uncommon but possible if there's oil on the slats - which is why we check).
