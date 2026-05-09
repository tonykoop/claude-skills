# 03 - Drawing Package

## Drawing list

| Sheet | Title | Scale | Purpose |
|---|---|---|---|
| D-01 | Trellis silhouette - overall | 1:8 | Outer + inner profile, datum origin |
| D-02 | Spine + tendril detail | 1:2 | Critical widths, fillet radii |
| D-03 | Leaf detail (3 sizes) | 1:1 | Interior vein slots, pierce locations |
| D-04 | Tab map | 1:8 | Where micro-tabs hold parts during cut |
| D-05 | Bracket plate (install) | 1:2 | Bolt hole positions |

## Datum strategy

- **Origin (0,0)**: bottom-center of the spine (where the stake portion meets the exposed trellis).
- **+X**: to the right (viewer's perspective).
- **+Y**: up.
- All dimensions referenced from this origin. Symmetric features mirrored about X=0.

## Tolerances

| Feature class | Tolerance |
|---|---|
| Silhouette curve (cosmetic) | +/- 0.030" (plasma typical) |
| Bolt holes (D-05 bracket) | +/- 0.015" - drill after plasma rather than cut, for fit |
| Leaf vein slots | +/- 0.040" - cosmetic only |
| Spine width (structural) | +0.060" / -0.000" - never go thinner than nominal |

## Vector file requirements (for plasma CAM)

The SVG / DXF handed to the plasma operator must:

1. Be in **inches**, not mm. Confirm units when exporting from Illustrator/Inkscape/Fusion.
2. Have **all closed paths** - no open loops, no overlapping segments.
3. Distinguish **outer profile** from **internal cuts** by layer or color (operator sets lead-ins differently for each).
4. Have **no text** as text - convert to outlines if any (none planned here).
5. Be **scaled 1:1** - no "fit to page" scaling.
6. Have **arc segments**, not high-density polylines, where possible. Smoother G-code, cleaner cut.

A concept SVG (`trellis_silhouette.svg`) is included alongside this packet. The final cut file should be regenerated in Fusion 360 or LightBurn from the master design with proper layer separation.
