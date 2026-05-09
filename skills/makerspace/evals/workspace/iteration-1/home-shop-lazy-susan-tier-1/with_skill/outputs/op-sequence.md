# Op Sequence — 3-Tier Hexagonal Walnut Lazy Susan (Tier 1)

**Tools used (all from user's stated kit):**
bandsaw · drill press · hand tools (combination square, marking gauge, marking
knife, compass, hand plane) · random-orbit sander · handheld router · clamps.

**Total estimated shop time:** 6–8 hours active, plus an overnight glue-up
cure.

## Step 0 — Stock prep (15 min)

- Inspect each walnut board. Pick the cleanest grain for tier 1 (most
  visible) and the lesser stock for tier 3 (smallest, partly hidden under
  bowls).
- If boards are rough on one face, hand-plane or send through to flatness
  before glue-up. With no jointer/planer in the home kit, **buy S2S
  (surfaced two sides) walnut** so this step is just touch-up with the block
  plane.
- Crosscut to ~17"/15"/13" rough lengths (per `cut-list.csv`).

**Go/no-go:** all glue-up strips flat within 1/32" across width. If a strip
is cupped, set it aside or rip it narrower.

## Step 1 — Edge-glue the three tier blanks (45 min active + overnight cure)

- For each tier, joint mating edges. With no jointer, use the **block plane
  on a shooting setup** or the bandsaw fence followed by a hand-plane pass
  to dress the edge.
- Test-fit dry. Edges should meet with no light visible through the seam.
- Glue with Titebond II/III, clamp with F-clamps every 8". Wipe squeeze-out.
- Let cure overnight. Don't rush this — a starved seam will fail at the
  router step.

**Go/no-go:** glue lines invisible end-to-end after cure. If a seam reads
proud, scrape and try again.

## Step 2 — Square up each blank (20 min)

- Strike a square line on one edge with combination square + marking knife.
- Bandsaw the square edge ~1/16" oversize, then hand-plane down to the line.
- From that reference edge, mark the other three edges to the **square blank
  size** specified in `cut-list.csv` (16.5", 14.5", 12.5").
- Bandsaw to the lines, hand-plane the cut edges flat.

**Go/no-go:** each blank is square within 1/32" corner-to-corner (measure
both diagonals — they should match).

## Step 3 — Lay out each hexagon (15 min)

For each blank, using compass + straightedge on the **top face**:

1. Draw both diagonals. Their intersection is the hex center.
2. Set the compass to side length s for that tier:
   - Tier 1: s = 8.000"
   - Tier 2: s = 7.000"
   - Tier 3: s = 6.000"
3. Strike a circle of radius s around the center. (Construction identity:
   for a regular hexagon, **side length equals circumscribed circle
   radius**.)
4. Pick any point on the circle — call it vertex A. Step the compass around
   the circle: A → B → C → D → E → F → back to A. Six steps, six vertices.
5. Connect adjacent vertices with a straightedge and marking knife.

**Verification before any cut:**
- Distance vertex-to-opposite-vertex = D (point-to-point). Should read
  16"/14"/12" within 1/32".
- Distance flat-to-opposite-flat = F. Should read 13.856"/12.124"/10.392"
  within 1/32".
- All six sides equal within 1/32".

**Go/no-go:** all three checks pass on every blank. **If any side is off
by more than 1/32", redraw the hex** before cutting — bandsaw correction is
much harder than pencil correction.

## Step 4 — Bandsaw the hex perimeters (45 min)

- Install the 1/2" 3-TPI blade. Tension and tracking checked.
- Set the bandsaw fence parallel to the blade (account for blade drift —
  test on scrap).
- Cut **just outside the line** on each of the six sides per blank. Don't
  try to split the line; leave 1/32" for clean-up.
- Rotate the blank 60° between cuts. The hex symmetry means each cut is the
  same setup.
- Repeat for tiers 2 and 3.

**Go/no-go:** all cuts within 1/32" outside the layout line, no scorched
edges, no wandering kerfs that crossed the line.

## Step 5 — Hand-plane sides to the line (45 min)

- Clamp each tier in the bench vise with one hex side facing up.
- Block-plane each side down to the marking-knife line. Stop just shy and
  sand the last whisker.
- Rotate, repeat for all six sides.
- Check: opposite sides should be parallel; opposite vertices should hit
  the design D within 1/32".

**Go/no-go:** all 18 hex sides (6 × 3 tiers) flat to the line, sides
parallel and angles 120° within ±0.5°. Use the combination square's 30°/60°
function or a printed 120° template to verify angles.

## Step 6 — Sand faces to 180 grit (45 min)

- Random-orbit sander, 80 → 120 → 180 grit.
- Both faces of all three tiers. Edges hit lightly with 180 by hand to
  break the corners — but **don't round them yet**, the router needs a
  crisp edge.
- Vacuum / blow off between grits.

**Go/no-go:** no swirl marks visible at 180 under raking light. No 80-grit
scratches surviving into 180.

## Step 7 — Roundover edges with the handheld router (30 min)

- Chuck the 1/4" bearing-guided roundover bit. Set depth so the bit's
  cutting edge meets the bearing flush.
- Clamp tier 1 to the bench, top face up, with one hex side overhanging.
- Run the router *clockwise* around the perimeter when the bit is on the
  top face (climb-cut hazard otherwise — see `safety-notes.md`).
- Flip and roundover the bottom face.
- Repeat for tiers 2 and 3.

**Go/no-go:** consistent 1/4" radius all the way around, no bearing burns,
no router skips at the vertices. Slow down through corners — the bit wants
to dig in there.

## Step 8 — Final sand (20 min)

- 220 grit by hand on the rounded-over edges and on both faces.
- Wipe with a damp rag to raise the grain. Let dry, then 220 again. Walnut
  is forgiving here.

**Go/no-go:** surfaces feel smooth as glass; rounded edges feel continuous,
no facets at the vertices.

## Step 9 — Locate and install the bearings (40 min)

For the tier-1 → tier-2 bearing (6" square):

1. On the **top** face of tier 1, mark the geometric center.
2. Position the bearing centered on that mark, square to one of the hex
   sides (so the bearing axes line up with a flat-to-flat axis — looks
   tidier).
3. Mark the four lower-plate screw holes through the bearing.
4. **Drill press**, 1/16" pilots, 3/8" deep. Don't blow through the 3/4"
   stock.
5. Screw the bearing's lower plate to tier 1 with #8 × 1/2" screws.
6. Mark the location of the bearing's **access hole** on tier 1 (the
   opening in the upper plate that exposes one of the upper-plate screw
   holes when rotated). Drill a 1/2" thru-hole at that location through
   tier 1 — this is how you'll drive the upper-plate screws after the
   stack is assembled.

For the tier-2 → tier-3 bearing (4" square):

7. Repeat steps 1–6 on tier 2's top face. Center it. Drill the 1/2" access
   thru-hole through tier 2.

**Go/no-go:** bearings spin freely, no rocking. Lower plates flush to the
wood, no screws proud.

## Step 10 — Stack and screw the upper plates (20 min)

1. Set tier 2 onto the tier-1 bearing's upper plate, centered (use the
   diagonals on tier 2's bottom face to find center, align with the
   bearing center).
2. Rotate tier 2 until the bearing's access hole on tier 1 lines up with
   one of the upper-plate screw holes. Drive a #8 × 1/2" screw up through
   tier 1's access hole into tier 2.
3. Rotate 90° (×3 more) and drive the remaining three screws.
4. Repeat with tier 3 onto tier 2's bearing.

**Go/no-go:** all three tiers concentric within 1/16". Stack spins
independently per tier — wiggle each tier and confirm only that one moves.

## Step 11 — Finish (30 min active + 24 hr cure)

- Disassemble (back out 8 screws). Removing tiers protects the bearings
  from oil drips.
- Wipe-on Danish oil per the can's instructions: flood, wait 15 min, wipe
  off all excess. Do both faces and all edges of all three tiers.
- Cure 24 hr per coat. 2 coats minimum; 3 coats for a richer surface.

## Step 12 — Reassemble and add feet (10 min)

- Re-install bearings (same screws, same holes).
- Stick four felt or rubber feet to the bottom of tier 1, near the
  vertices, so the lazy susan glides on the table without scratching.

**Final go/no-go:** stack height ~2.875"; all three tiers spin independently
with light finger pressure; no wobble; finish even on all visible faces.
