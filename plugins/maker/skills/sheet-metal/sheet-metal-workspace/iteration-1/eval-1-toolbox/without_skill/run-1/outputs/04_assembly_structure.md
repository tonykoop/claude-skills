# Top-Down Assembly Structure

## Philosophy
This is a **top-down (in-context, skeleton-driven)** assembly. All geometry derives from a single Master Layout part that owns the global variables. Child parts reference the layout, never each other.

## File Tree
```
Toolbox_System.sldasm                    [TOP LEVEL]
|-- 00_MasterLayout.sldprt               (skeleton part - owns globals & key sketches)
|-- 10_Box.sldasm                        (single toolbox sub-assembly)
|   |-- 10.1_Body.sldprt                 (sheet metal - 5-sided open box)
|   |-- 10.2_Lid.sldprt                  (sheet metal - inverted shallow tray)
|   |-- 10.3_InterlockBoss_Lid.sldprt    (sheet metal pad/emboss feature)
|   |-- 10.4_HingePin.sldprt             (turned/cut rod)
|   |-- 10.5_DrawLatch.sldprt            (purchased - represented as simplified)
|   |-- 10.6_HandleGrip.sldprt           (overmold or formed flange)
|   `-- 10.7_Foot.sldprt                 (rubber bumper - purchased)
|-- 20_Dolly.sldasm                      (dolly sub-assembly)
|   |-- 20.1_DollyDeck.sldprt            (sheet metal tray with upturned lip)
|   |-- 20.2_DollyHandle.sldprt          (bent tube - weldment)
|   |-- 20.3_Caster.sldprt               (purchased - simplified)
|   `-- 20.4_CasterHardware.sldprt       (bolts/nuts - toolbox standard)
`-- 99_StackDemo.sldasm                  (visualization sub-assy: dolly + N boxes stacked)
```

## Master Layout Part (`00_MasterLayout.sldprt`)
Contains ZERO solid bodies. Only:
- All Global Variables (from `02_global_variables.txt`)
- **Sketch: BoxFootprint_Top** - centered rectangle, `BoxWidth` x `BoxDepth`
- **Sketch: BoxProfile_Front** - rectangle `BoxWidth` x `BoxHeight`, with lid/body split line at `BodyHeight` height
- **Sketch: InterlockGrid** - 4 corner points inset by `InterlockInset` from each corner; centered datum point
- **Sketch: CasterPattern** - 4 caster center points at `DollyWidth-2 in` x `DollyDepth-2 in` rectangle
- **Sketch: DollyOutline_Top** - centered rectangle `DollyWidth` x `DollyDepth`
- Reference planes:
  - `BoxTop`, `BoxBottom`, `BoxFront`, `BoxBack`, `BoxLeft`, `BoxRight`
  - `LidSplit` (at `BodyHeight` from BoxBottom)
  - `DollyDeckTop` (at `DollyDeckHt` from caster top)

## Top-Down Workflow
1. Insert `00_MasterLayout.sldprt` into top assembly, fix at origin.
2. Insert each new component as **"New Part" in-context** OR insert empty part and use **Convert Entities** referencing the master layout sketches.
3. Lock all geometry references to master layout edges/sketches - never to neighbor parts.
4. External references show as `->` in the FeatureManager - this is intentional.

## Mate Strategy
- All components mate to `00_MasterLayout` reference planes, NOT to each other.
- Box body to layout: 3 plane-to-plane mates (Box Front/Bottom/Left).
- Lid to body: distance mate `BodyHeight - LidLapDepth` (uses global variable).
- Stack demo assembly: pattern `BoxesOnDolly` instances along Z with spacing `BoxHeight`.

## Change Propagation Test
When user changes `BoxWidth` from 20 to 24:
- MasterLayout sketches update -> Box body flat pattern widens -> Lid widens -> Interlock positions shift outward -> Dolly deck widens -> Caster pattern widens -> StackDemo updates with new spacing.
- **Acceptance:** Full rebuild < 30 sec; zero "dangling" external references; flat patterns remain valid.
