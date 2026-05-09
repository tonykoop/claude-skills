# Drawing Brief — Pattern Pieces

This brief describes the pattern-piece drawings. For Tier 2, a
written brief plus an inline ASCII layout per piece is sufficient;
upgrade to dimensioned SVGs for Tier 3.

All drawings share these conventions:
- **Units:** inches.
- **Seam allowance (SA):** 0.5" included on all sides unless noted.
  Mark the SA line with a dashed border 0.5" inside the cut line.
- **Grain arrow:** drawn parallel to the longer dimension of each
  body and gusset piece, indicating direction parallel to the
  selvedge.
- **Notch marks:** small triangular notches on cut edges where
  pieces register against each other. Depth 1/4".
- **Fold line:** double-dash where a piece is mirrored along an
  axis (the strap and pocket are folded along a centerline).
- **Centerline / placement marks:** crosshair or X marker for
  where straps anchor on the body panel.

## P-01 / P-02 — Body panels (front, back)

```
              19" cut width
   +------------------------------------+   ^
   |   . . . . . . . . . . . . . . . .  |   |
   |   .   strap anchor X (top, 4" in,  |   |
   |   .   1.5" down from top edge)     |   |
   |   .                              . |   |
   |   .                              . |  16"
   |   .       (SA 0.5" all sides)    . | (cut)
   |   .                              . |   |
   |   .   strap anchor X (top right)  .|   |
   |   .                              . |   |
   |   . . . . . . . . . . . . . . . .  |   |
   +------------------------------------+   v
   ↕ grain arrow → →
```
- Quantity: 2 in canvas (P-01 front, P-02 back), 2 in lining
  (P-07 front, P-08 back).
- Notch midpoints of left and right edges (the gusset registers
  against these).
- Strap-anchor crosshairs on canvas pieces only:
  - 4" from each side seam
  - 1.5" down from the top cut edge
  - Each crosshair = the centerline of a 1.5"-wide × 1.5"-tall
    strap-end footprint.

## P-03 / P-09 — Gusset (continuous strip)

```
       7" cut width
   +-----+
   |  .  |
   |  .  |
   |  .  |
   |  .  |
   |  .  |
   |  .  |  ← grain arrow ↕
   |  .  |
   |  .  |
   |  .  |  ← notches at:
   |  .  |    16" from top end (1st corner — gusset turns from side to bottom)
   |  .  |    35" from top end (2nd corner — gusset turns from bottom to side)
   |  .  |
   |  .  |
   |  .  |
   |  .  |
   +-----+
   48" total cut length
```
- One continuous strip wraps up one side, across the bottom,
  back up the other side.
- The two notches mark the corners where the gusset pivots
  from vertical to horizontal.
- Quantity: 1 canvas (P-03), 1 lining (P-09).
- **Alternative split:** 2× 7×16 sides + 1× 7×19 bottom, joined
  with two seams. Saves yardage at the cost of two extra seams.

## P-04 — Bottom reinforcement panel

```
       7" cut width
   +-----+
   |     |
   |     |
   |     |  19" cut length
   |     |
   |     |
   +-----+
   ↕ grain arrow ↕
```
- Quantity: 1 canvas.
- Sewn to the *outside* of the gusset's bottom 19" before the
  shell is constructed. Acts as a doubler for abrasion against
  the ground.

## P-05 — Strap

```
              28" cut length
   +-----------------------------------+   ^
   |         (fold line, centerline)   |   |
   |- - - - - - - - - - - - - - - - - -|  7" cut width
   |                                   |   |
   +-----------------------------------+   v
   ↔ grain arrow ↔
```
- Quantity: 2 canvas.
- Folding sequence: bring both long raw edges to the centerline
  (creates a 3.5"-wide piece with raw edges meeting in the
  middle), then fold again along the centerline (creates a
  1.5"-wide finished strap with all raw edges enclosed). Insert
  foam (P-13) into the center 8" before final edge-stitching.

## P-06 — Zipper end tab

```
   +-----+
   |     | 2" × 2" square
   +-----+
```
- Quantity: 2 canvas.
- Folded in half once, then wrapped over the end of the zipper
  tape, edge-stitched.

## P-10 — Inside slip pocket

```
       9" cut width
   +-----+
   |     |
   |     |
   |     |
   |     |  22" cut length
   | - - |  ← fold line (centerline)
   |     |
   |     |
   |     |
   +-----+
   ↕ grain arrow ↕
```
- Quantity: 1 lining.
- Fold along centerline, RST. Hem the open mouth before sewing
  the side seams. Finished pocket = 8" wide × 10" tall.
- Position on P-08 (back lining body panel): centered side-to-
  side, top of pocket 4" down from the top cut edge.

## P-11 / P-12 — Stiffener sleeve

```
       5.5" cut width
   +-----+
   |     | 17.5" cut length
   +-----+
```
- Quantity: 2 lining (one top, one bottom of sleeve).
- Sewn 3 sides RST, turned, basted onto the bottom of the gusset
  lining (P-09) at center. Open side becomes the sleeve mouth
  for inserting the HDPE.

## P-13 — Strap padding

```
       1.25" cut width
   +-----+
   |     | 8" cut length
   +-----+
```
- Quantity: 2 EVA foam.
- No seam allowance.
- Inserted into the center 8" of each strap before edge-stitching.

## P-14 — Bottom stiffener (optional)

```
       5" cut width
   +-----+
   ( . . )   ← 0.5" radius rounded corners
   |     |
   |     |  17" cut length
   |     |
   ( . . )   ← 0.5" radius rounded corners
   +-----+
```
- Quantity: 1 HDPE.
- Cut on bandsaw (woodshop), round corners with belt sander.

## P-15 — Bias binding tape

- Continuous 1" double-fold tape, 6 yd total.
- Cut to length as you bind each interior seam.
- Pre-made tape recommended for consistency; bias-cutting your
  own from 1/4 yd of contrasting cotton is also fine for Tier 3
  upgrade.

## Tier 3 upgrade path

For a Tier 3 packet, regenerate these as full-scale dimensioned
SVGs with:
- Scale 1:1 print at letter or tabloid (tile if needed).
- Title block (project name, piece ID, qty, material, date,
  revision).
- Overall outside dimensions called out at every edge.
- Notch positions dimensioned from the corner.
- Strap-anchor positions dimensioned from the top and side
  edges.

The skill's `references/drawing-and-visualization.md` lists the
SVG generator script.
