# Cut-Path Strategy — Plasma at 1/4" Mild Steel

This is the load-bearing document for this packet. The user has
not run the plasma at this scale before; everything below is about
turning a clean CAD silhouette into a clean steel part on the first
production run.

Assumptions: **Hypertherm Powermax 65** with fine-cut consumables
at 45 A, on 1/4" A36 mild steel, on a downdraft slat table with
SheetCAM or Fusion 360 plasma post. If Maker Nexus runs a different
machine, every numeric value below should be re-verified against
the manufacturer's cut chart for that consumable set.

## 1. Lead-in placement

A lead-in is the short ramp-on segment that takes the torch from
its pierce hole to the actual cut line. Where you put it matters
because the pierce dimples the metal and the lead-in path leaves a
visible witness on the cut wall.

**Rules used in this packet:**

- **Length:** 0.30 in lead-in, 0.15 in lead-out. Long enough that
  the pierce hole sits clear of the finished cut wall; short enough
  not to waste cut time.
- **Geometry:** arc lead-in (a quarter-circle that meets the cut
  line tangentially) for every closed contour. Straight lead-ins
  leave a sharper witness mark and are reserved for thin slots.
- **Position on the part:**
  - **Internal cutouts (negative space inside the silhouette,
    e.g., the gaps between leaves and stem):** lead-ins start at
    the *centroid-side* of the cutout, in the smoothest part of
    the curve, never at a tight cusp. The pierce hole then sits
    in the scrap, not on the finished edge.
  - **External perimeter (the trellis silhouette itself):**
    lead-ins start in scrap, attack the cut tangentially from
    *outside* the part, and lead out away from the part. The
    pierce hole and any pierce dimple stay in the drop sheet, not
    on the trellis edge.
- **Avoid lead-ins at corners and at the start of fine details
  (tendril tips, leaf cusps).** Place them mid-segment along a
  long, gentle curve.

## 2. Kerf compensation

Kerf is the width of metal the plasma actually removes. If the CAD
file says the cut runs along the part outline, but the torch removes
0.060 in of metal centered on the toolpath, the part comes out
0.060 in undersized in every dimension unless you compensate.

**Rules used in this packet:**

- **Direction:** offset the toolpath *outward* from the part for
  external contours, *inward* for internal contours. The CAM post
  handles this if you set the side correctly. Verify by previewing
  the toolpath in the CAM software before exporting.
- **Magnitude:** start with `kerf = 0.060 in`, half-kerf offset =
  0.030 in. **Cut a kerf-test coupon first** (op-sequence step 4):
  two parallel cuts 1.000 in apart, measure both cut walls with a
  caliper, compare to nominal. Update the CAM kerf parameter if
  delta exceeds 0.010 in.
- **Why it matters here:** the leaf cusps are the tightest features
  (interior radius 0.20 in). If kerf is under-estimated, the cusp
  collapses to nothing. If over-estimated, the cusp opens up and
  loses visual sharpness. Both are visible on a 6-ft trellis.

## 3. Pierce-point planning

The pierce is the moment the torch punches through the sheet. It is
the riskiest single event in a plasma program: blowback can
contaminate the nozzle, slag splatter can mar the part edge, and a
pierce in the wrong spot leaves a permanent dimple.

**Rules used in this packet:**

- **Pierce location:** every pierce sits inside scrap, never on the
  finished cut line. For internal cutouts, the pierce is at the
  pierce-point of the lead-in arc (~0.30 in from the cut line). For
  the perimeter, the pierce is in the surrounding scrap field at
  least 0.30 in clear of the silhouette.
- **Pierce delay:** use the consumable manufacturer's published
  pierce-delay for 1/4 mild steel at 45 A — typically 0.7-1.0
  seconds for the Powermax 65 fine-cut set. Too short and the
  pierce blows through unevenly; too long and the slag puddle
  oversizes the pierce hole.
- **Pierce count:** estimate 12 pierces (1 perimeter + 11 internal
  cutouts between/inside the leaves and tendrils). Each pierce
  consumes electrode life. Plan to swap consumables if the
  electrode hafnium pit deepens below the manufacturer's wear-line
  before the program is half done.
- **Pierce-height vs cut-height:** the torch should sit higher
  during the pierce (typically 0.15 in) than during the cut
  (typically 0.06 in) to keep blowback off the consumable. The
  CAM post and the Powermax cut chart together set this; do not
  override unless you know what you're doing.
- **Pre-flight test:** run the pierce-test coupon (op-sequence step
  5) with the production lead-in geometry on scrap. Inspect for
  blowout, dimple radius, and slag pattern before committing the
  trellis program.

## 4. Sequencing — internal cutouts before perimeter

Cut order matters because once the perimeter releases the part from
the parent sheet, the part is loose and can shift, drop into the
slats, or rotate under the torch.

**Order for this packet:**

1. **Kerf-test coupon (KT1).** Validate kerf assumption. Stop and
   recalibrate if needed.
2. **Pierce-test coupon (P1).** Validate pierce parameters and
   lead-in geometry on scrap.
3. **All internal cutouts.** Every closed loop *inside* the
   trellis silhouette — the gaps between leaves and the stem, the
   negative space inside each tendril curl, the keyhole between
   the bottom rail and the stem. Cut these from the most-interior
   feature outward, so each new cut is supported by uncut sheet.
4. **Tendril fine details.** Cut the small interior loops of each
   tendril last among internal features; they're the most likely
   to deflect from heat distortion if cut while large hot zones
   are still nearby.
5. **Perimeter — bottom-up, ending near the operator side.** The
   final cut releases the part. Keep the last 2 in of perimeter
   in a "bridge tab" if the program supports it; sever the bridge
   manually with a cut-off wheel after the part has cooled. This
   prevents the 86-in part from dropping into the slats while the
   torch is mid-cut.

**Why bridge-tab the last segment:** an 86-in × 24-in piece of
1/4" steel weighs ~30 lb. If it releases unsupported during the
final inches of the perimeter cut, it can drop, tilt, or rotate
into the torch. A bridge tab keeps it tied to the parent sheet
until you remove it deliberately.

## 5. Dross management

Dross is the re-solidified slag on the bottom edge of a plasma cut.
It's normal at this thickness; the goal is to minimize it (good
parameters) and remove it cleanly (good post-process).

**Rules used in this packet:**

- **Top dross vs bottom dross:**
  - **Top dross** (raised slag on the entry face) means cut speed
    is too slow, amperage is too high, or torch height is too
    high. Symptom: hard, brittle slag bonded to the top edge.
    Fix: increase travel speed by 10%, re-test on scrap.
  - **Bottom dross** (raised slag on the exit face) means cut
    speed is too fast, amperage is too low, or torch height is too
    low. Symptom: a curtain of slag hanging off the bottom edge.
    Fix: decrease travel speed by 10%, re-test on scrap.
  - **Goal at 1/4 mild steel, 45 A fine cut:** light dust dross
    that wipes off with a flap disc. If the kerf-test coupon
    produces curtain dross or hard top dross, dial the parameters
    before the production cut.
- **Direction of cut vs the part:** plasma cuts a tapered kerf —
  the "good side" is on the *right* of travel direction (with the
  arc rotating clockwise when viewed from above). The CAM post
  should orient cuts so the right-hand side of the toolpath is
  the keep side. For internal cutouts the path runs clockwise;
  for the perimeter it runs counter-clockwise. Verify in the CAM
  preview before exporting.
- **Post-process dross removal:**
  1. Let the part cool 5 min on the table after the program ends.
     Hot dross fractures off in chips; cold dross fractures off
     and the underlying steel is colder, which makes flap-discing
     more efficient.
  2. **Chipping hammer** the bottom edge to knock off curtain
     dross before any abrasive contact. Chip into a catch tray;
     dross fragments are sharp.
  3. **Flap disc, 40-grit** along the bottom edge until smooth.
     Then **80-grit** for finish. Keep the disc moving — pausing
     burns a flat into the edge.
  4. **Do not** angle-grind the top face — leave the mill-scale
     for the powder coater's sandblast prep.
- **Acceptance criterion:** every cut edge should pass a clean
  cotton rag without snagging. Any spot that snags gets one more
  pass with the 80-grit.

## 6. Pre-flight checklist (the day of)

- [ ] Production CAM file exported with kerf, lead-ins, pierce
      points, and sequencing per this document.
- [ ] Kerf-test coupon KT1 program ready as a separate file.
- [ ] Pierce-test coupon P1 program ready as a separate file.
- [ ] Fresh fine-cut electrode + nozzle installed. Spare set on
      the bench.
- [ ] Air dryer/filter checked — wet air destroys consumables
      faster than anything else.
- [ ] Sheet flat, square to the table, magnetic hold-downs in
      place, table slats clear of large scrap chunks.
- [ ] PPE on: ANSI Z87 shaded glasses (#5 minimum), leather
      gloves, leather apron, cotton or wool clothing (no
      synthetics), respirator (or downdraft confirmed running).
- [ ] Phone laid down somewhere it won't catch a stray spark.
- [ ] Kerf-test FIRST. Pierce-test SECOND. Production THIRD.
      Don't skip the order.
