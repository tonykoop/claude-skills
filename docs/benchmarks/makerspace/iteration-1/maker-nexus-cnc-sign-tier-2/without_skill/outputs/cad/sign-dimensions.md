# Sign dimensions

All dimensions in inches. Origin is lower-left of the finished part.

## Outside profile

```
                              18.000
   +----------------------------------------------------------+
   |                                                          |
   |   +--------------------------------------------------+   |  <- 0.500 inset
   |   |                                                  |   |     border line
   |   |                                                  |   |
   |   |               W E L C O M E                      |   |   6.000
   |   |                                                  |   |
   |   |                                                  |   |
   |   +--------------------------------------------------+   |
   |                                                          |
   +----------------------------------------------------------+
   ^
   (0,0)
```

## Key dimensions

| Feature | Dimension | Notes |
|---|---|---|
| Outside width | 18.000 in | finished |
| Outside height | 6.000 in | finished |
| Corner radius | 0.125 in | matches 1/8" end mill radius |
| Border inset (all 4 sides) | 0.500 in | from outside edge |
| Border stroke width | V-carve, ~0.06 in wide at surface | 60 deg V-bit, depth 0.05 in |
| Letter cap height | ~3.000 in | tune to font |
| Letter baseline | 1.500 in from bottom | centers caps in 6.000 in height |
| Letter tracking | +25 to +50 units | open up "WELCOME" |
| Max V-carve depth | 0.180 in | leaves ~0.07 in stock |

## Stock blank

- Blank size: 20.000 x 8.000 in (1.000 in margin on every side of
  finished part).
- Stock thickness: 0.250 in nominal Baltic birch (~0.236 in actual,
  measure your sheet).

## Hanging slot (back face, second op)

```
   back-face view (top of sign)
   +---+---+---+---+---+---+---+---+
                  +-----+
                  |     |       <- 0.625 wide x 1.000 tall
                  |  o  |          keyhole slot, centered
                  +-----+          on top edge, 0.500 in
                                   below top edge
```

| Feature | Dimension |
|---|---|
| Slot width (overall) | 0.625 in |
| Slot height (overall) | 1.000 in |
| Slot depth | 0.180 in (leaves ~0.07 in stock) |
| Round head pocket dia | 0.375 in |
| Slot offset from top edge | 0.500 in (center of slot) |
| Designed screw | #8 panhead, 1.0-1.25 in long |

## Sources of truth

- Master CAD: `cad/sign-layout.svg` (placeholder; build in Inkscape
  or Illustrator).
- Master CAM: VCarve Pro / Carbide Create / Fusion 360 file (not
  included in this packet - generated on-site after final font
  selection).
- Tolerances: +/- 0.020 in on outside dimensions, +/- 0.005 in on
  V-carve depth.
