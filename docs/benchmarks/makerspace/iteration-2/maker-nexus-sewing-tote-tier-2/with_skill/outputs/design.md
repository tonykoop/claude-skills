# Design — Heavy-Duty Waxed Canvas Tote

## Inputs (parametric)

These are the input dimensions the rest of the pattern derives from.
Change one of these and the rest of the pattern math updates.

| Input | Value | Notes |
|---|---|---|
| `W` (finished width) | 18 in | Mouth opening, side-to-side. |
| `H` (finished height) | 14 in | Top zipper to bottom seam. |
| `D` (finished depth) | 6 in | Boxed gusset depth. |
| `SA` (seam allowance) | 0.5 in | Standard for this build. Bound seams cover this. |
| `binding_width` | 1.0 in | Double-fold bias tape, finished width 0.5". |
| `strap_width` | 1.5 in | Finished. |
| `strap_drop` | 12 in | Hand-to-shoulder clearance; total length = 2× drop = 24". |
| `strap_pad_length` | 8 in | Foam-padded section centered on strap. |
| `pocket_W` | 8 in | Inside slip pocket. |
| `pocket_H` | 10 in | Inside slip pocket. |
| `zipper_length` | 20 in | YKK #10 molded, two-way pull. Finished opening = W + 2 in. |

## Derived pattern dimensions

All pattern pieces include `SA` on every edge unless noted.

### Body — front and back panels (cut 2 from canvas, cut 2 from lining)

- Pattern width = `W + 2*SA` = 19 in
- Pattern height = `H + 2*SA + 1.0` = 16 in
  (the +1.0" allows the panel to wrap up around the zipper tape)

### Gusset — wraps sides and bottom as one continuous strip (cut 1 from canvas, cut 1 from lining)

- Length = `2*H + W + 4*SA` = 48 in
  (up one side + across the bottom + up the other side)
- Width = `D + 2*SA` = 7 in

> Alternative: split the gusset into two side panels + one bottom
> panel for less wasteful nesting. See `cut-list.csv` row notes.

### Bottom reinforcement panel (cut 1 from canvas)

- Width = `W + 2*SA` = 19 in
- Length = `D + 2*SA` = 7 in
- Stitched onto the outside bottom of the gusset before assembly.

### Straps (cut 2 from canvas)

- Length = `2*strap_drop + 4` = 28 in (the +4 accommodates the
  anchor tabs that fold under the body panel and bartack-secure)
- Width = `4*strap_width + 2*SA` = 7 in
  (folded twice into a 1.5"-wide strap with all raw edges enclosed)

### Strap padding (cut 2 from 1/4" closed-cell foam)

- Length = 8 in
- Width = `strap_width - 0.25` = 1.25 in
  (slightly narrower than the strap so foam doesn't bunch at edges)

### Inside slip pocket (cut 1 from lining)

- Width = `pocket_W + 2*SA` = 9 in
- Height = `2*pocket_H + 2*SA + 1` = 22 in
  (cut as a single piece, folded in half to self-line; +1 for the
  hem at the pocket mouth)

### Zipper end tabs (cut 2 from canvas)

- 2 in × 2 in squares, folded to 2 in × 1 in finished caps that
  enclose each end of the zipper tape.

## Material choices and rationale

### 12-oz waxed canvas — exterior

Why: 12 oz is the sweet spot for totes — heavy enough to hold
shape and shrug off weather, light enough to sew without
specialty equipment. Waxed finish is repairable (re-wax with a
beeswax/paraffin blend) and develops patina.

Watch for:
- Wax can gum up the needle; wipe needle every 30 min or use a
  silicone needle lube.
- Wax transfers to the iron — press from the lining side or
  use a press cloth, never direct-iron the wax side at high heat.
- Pre-test stitch tension on a scrap; waxed canvas is denser than
  unwaxed so tension may need to come down 1-2 settings.

### Cotton twill — lining

Why: 5-7 oz cotton twill resists snags better than quilting
cotton, takes a stitch line cleanly, and matches the formality of
the canvas. Pre-wash before cutting (canvas does not need
pre-washing — the wax would rinse out).

### Bias-cut cotton bias tape — bound seams

Why: 1" double-fold (which finishes to 0.5") gives the seam a
crisp interior and reinforces the high-stress edges. Bias cut
turns curves cleanly. Cotton (not poly) will breathe and avoids
melt risk if the tote is near heat.

### YKK #10 molded coil zipper

Why: #10 is the right tooth size for a tote of this scale. Molded
coil (not metal) won't corrode, won't catch on the lining, and
two-way pulls let you open from either end. 20 in length gives a
generous mouth without overbuilding.

### Foam strap padding — 1/4" closed-cell EVA

Why: Closed-cell EVA doesn't compress out over time (open-cell
foam will). 1/4" is plenty for shoulder comfort with a fully
loaded bag.

### Optional bottom stiffener — 1/8" HDPE sheet, 5 in × 17 in

Why: Drops into a sleeve sewn into the lining bottom. Keeps the
floor of the bag flat under load. HDPE is washable, won't
delaminate. Cut to fit; rounded corners.

## Stitch and thread plan

| Operation | Thread | Needle | Stitch |
|---|---|---|---|
| Construction seams (canvas) | Tex 70 (V-69) bonded poly | 110/18 jeans/denim | Straight, 8-9 spi |
| Construction seams (lining) | Tex 40 (V-46) all-purpose poly | 90/14 universal | Straight, 10-11 spi |
| Topstitching | Tex 90 bonded poly | 110/18 topstitch | Straight, 6-7 spi |
| Bartacks (strap anchors) | Tex 70 bonded poly | 110/18 jeans | Box-X bartack, dense zigzag |
| Binding | Tex 40 all-purpose poly | 90/14 universal | Straight or narrow zigzag |

> Maker Nexus's industrial walking-foot machine should already be
> threaded for heavyweight work; verify and re-thread to Tex 70
> bonded if not. Keep a pre-wound bobbin in the same thread.

## Tolerances

- Cut accuracy: ± 1/8" on linear dimensions, ± 1/4" on diagonals.
- Seam allowance: 1/2" ± 1/16" — consistency matters more than
  exact value. Use a seam-guide attachment on the walking-foot.
- Final bag dimensions: ± 1/2" on W and H, ± 1/4" on D.
- Strap drop: ± 1/2" — measure both straps before bartacking the
  second to ensure they match.

## Open questions / TBD

- **Verify industrial sewing machine model** at Maker Nexus textile
  area. The plan assumes a Juki-class compound-feed walking foot
  (e.g., Juki LU-1508 or similar). If the actual machine is
  different, foot/needle compatibility may shift slightly. (See
  `risks.md` R-01.)
- **Verify cert sub-structure** — is `#textile-cert` still a
  single umbrella, or has it split into domestic-only / industrial
  sub-certs? See `README.md` headline section.
- **Stiffener install** — drop-in sleeve or sewn-in? Drop-in is
  easier to wash; sewn-in is sturdier. Default in this packet:
  drop-in sleeve.
