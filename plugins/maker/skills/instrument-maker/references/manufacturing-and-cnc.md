# Manufacturing And CNC

Design for Tony's likely shop context: Maker Nexus tools plus home woodworking. Always adapt to the actual machine, stock, training, and fixturing constraints the user gives.

## Available Tools (Maker Nexus + Tony's Home Shop)

- **CNC router** (ShopBot or similar).
- **Wood lathe** (12"+ swing; needs 15"+ for conga belly diameter).
- **Table saw**, **band saw**, **jointer/planer**, **drum sander**, **drill press**, hand tools.
- **Epilog laser cutter** (templates, engraving, rosettes, gaskets, thin parts).
- **SolidWorks CAD** with parametric design tables linked to Excel.
- Wolfram, OpenSCAD, STL bridging for early parametric models.

## CNC Patterns

| Pattern | Use Case | Key Details |
| --- | --- | --- |
| **Flip jig with datum pins** | 2-sided routing (guitar cavities, resonant box chambers, flute halves) | Alignment pins critical; verify centerline with dial indicator |
| **Miter sled** | Segmented drum rings | 11.25° ashiko (16 seg), 9° conga (20 seg) |
| **Split-blank** | Didgeridoo bore routing, bored flute bodies | Rip blank, route bore profile in each half, re-glue, then turn/sand |
| **Profile routing** | Guitar body perimeters, ukulele halves, templates | Leave 0.030" skin on rough pass, tabs to hold blank |
| **3D surfacing** | Les Paul carved top, Strat contours, marimba arch undercuts | 3/4" ball-end, calculate stepover for surface finish |
| **Pocket routing** | Pickup cavities, control cavities, Helmholtz chambers | 1/4" upcut spiral; verify depth with calipers |
| **Laser templates** | Stave labels, hole patterns, drilling guides, rosettes | Include kerf compensation and registration marks |

## Lathe Boring Techniques

### Headstock-Driven Deep-Bore Drilling

Use `references/techniques/headstock-driven-deep-bore-drilling.md` when a
woodwind packet needs a long straight bore through square or non-round solid
stock before the outside is turned. The drill is held in a headstock Jacobs
chuck, while a rigid tailstock vise or guided carrier advances the stationary
blank into the spinning bit.

Good candidates: pan-flute tubes, siku/zampona, kena/quena, shakuhachi, fujara,
small didgeridoo studies, chalumeau/reed-pipe prototypes, and other straight
woodwind bores where split-blank routing would add unnecessary glue-line risk.

Packet requirements:

- Confirm headstock Morse taper and Jacobs chuck capacity.
- Include the tailstock vise/carrier drawing or fixture photo.
- Pilot on scrap and add a validation row for bore wander before drilling
  tonewood.
- Use peck drilling, conservative speed, and frequent chip clearing.
- Ream/lap to final bore after drilling when tuning-critical.

## Standard CNC Bits

| Bit | Use |
| --- | --- |
| 1/8" upcut spiral | Tongue slits, fine detail, slit kerf in resonant box |
| 1/4" downcut spiral | Pickup cavities, pockets, clean top surface |
| 1/2" downcut spiral | Perimeter profiles, neck pockets |
| 3/4" ball-end | 3D surfacing, marimba arches, guitar contours |
| 3/4" flat-bottom | Helmholtz chamber pockets |
| 1" surfacing bit | Flattening blanks on CNC bed |

Add feed/speed, chipload, depth of cut, and hold-down notes before sending a toolpath to a machine.

## v4.2 CNC Operation Plans

Use `scripts/generate_cnc_plan.py` before CAM or G-code work. The script emits:

- `cnc/cnc-plan.json` — machine-readable operation graph.
- `cnc/operations.csv` — shop-sortable operation list.
- `cnc/setup-sheet.md` — human setup sheet with release checks.

This is pre-CAM planning, not verified toolpath output. Treat the generated
plan as the handoff into Vectric, Fusion, SolidWorks CAM, laser software, or
lathe setup. Before cutting material, add the actual machine, stock, bit,
feed/speed, depth of cut, hold-down, and simulation/air-cut result.

Run:

```bash
python3 scripts/generate_cnc_plan.py ./build-packets/<slug>
```

Escalate instead of generating a confident plan when the packet lacks a
dimensioned drawing, the stock exceeds the machine envelope, the required bit
is not in the available tool list, or the workholding cannot survive the last
operation in the sequence.

## Segmented Construction

Use for ashiko, conga, djembe, dundun, kora bowls, calabash replacements, decorative shells.

```text
miter_angle = 180 / segments_per_ring
segment_edge_length = π × ring_outer_diameter / segments_per_ring
```

### Reference Builds

- **Ashiko**: 29 rings × 16 segments = **464 pieces**, miter angle **11.25°**, diamond pattern (Maple/Walnut base + Cherry/Yellowheart accents).
- **Conga**: 34 rings × 20 segments = **680 pieces**, miter angle **9°**, barrel profile, 3 woods.
- **Kora/Ngoni bowls**: segmented replacement for calabash gourd — same miter sled technique, adapted ring count.

Track ring number, outer diameter, inner diameter/wall, ring thickness, species pattern, segment count, glue-up order. Include turning allowance and final wall-thickness targets. For complex decorative patterns, add color/species maps and labels so the build table survives the shop.

## Steam Bending

Use for frame drums, lute/oud ribs, hoops, ribs, curved fixtures.

- Wood must be straight-grained, green or soaked.
- Minimum bend radius varies by species and thickness.
- Steam time rule of thumb: about **1 hour per inch of thickness at 212°F**.
- Steam box: 212°F minimum.
- Bend over CNC-routed mold form immediately after steaming.
- Thin oud/lute ribs may be around `2.8 mm` thick, but confirm by instrument family and species.
- Rib dimensions (oud): 14–21 ribs, 75 cm × 2.5–4 cm × 2.8 mm.
- CNC-routed forms should include springback allowance, clamping strategy, stop blocks.
- Label bend direction and grain direction in drawings.

## Guitar And Solid Body Notes

For electric guitar or bass bodies:

- Define scale length, neck pocket, bridge line, pickup routes, control cavity, jack, contours, strap buttons, centerline.
- Hardware-specific templates required for bridge, pickups, neck heel, tremolo block, ferrules.
- Body blank reference often starts around `14 × 20 × 1.75 in`, then adapts by model.
- Use Strat blueprint quality for view completeness: outline, cavities, contours, axes, sections, drilling references.

## Design-For-Manufacture Checks

- Machine envelope and stock size fit.
- Bit diameter can cut all inside radii or the drawing marks dogbones/relief.
- Workholding survives every operation.
- Flip/registration datums are repeatable.
- Grain direction and glue lines appropriate for stress, tone, appearance.
- Tool access reaches pockets/bores without collisions.
- Critical tuning features have trim or tuning allowance.
- Build packet includes dry-run, measurement, tuning checkpoints.
