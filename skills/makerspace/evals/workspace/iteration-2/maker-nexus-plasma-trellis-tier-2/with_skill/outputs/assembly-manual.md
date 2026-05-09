# Assembly Manual — Climbing-Vine Plasma Trellis

> Photo placeholders are marked `[PHOTO: ...]`. Capture them on the
> day of the build for the portfolio README.

## Step 0 — Confirm the cut file

Open the production CAM file in SheetCAM or Fusion 360. Verify:

- Kerf compensation set to your measured kerf value (default 0.060 in).
- Lead-ins are arc-style, 0.30 in, on smooth segments.
- Internal cutouts run clockwise; perimeter runs counter-clockwise.
- The perimeter ends with a 0.25-in bridge tab (or your machine's
  equivalent "tab and skip" feature) on the bottom rail's inboard
  side.

`[PHOTO: laptop screen with CAM preview, lead-ins highlighted]`

## Step 1 — Load the sheet

Two-person lift the 24x96 in sheet onto the plasma table. Square
the long edge to the X rail with a machinist's square. Set
magnetic hold-downs at the four corners and the two midpoints.
Confirm there's no large scrap chunk under the sheet that could
buoy it off the slats.

`[PHOTO: sheet squared and clamped, magnets visible]`

## Step 2 — Kerf-test cut (KT1)

Run the KT1 program. It cuts two parallel 1.000-in-spaced lines on
a small scrap area. After cooldown:

1. Caliper the actual gap between the cut walls.
2. Compute kerf = 1.000 - measured_gap.
3. If kerf differs from the 0.060-in design assumption by more
   than 0.010 in, **stop**. Update the CAM kerf parameter,
   re-export the production file, and proceed.

`[PHOTO: caliper on the kerf-test coupon]`

## Step 3 — Pierce-test cut (P1)

Run the pierce-test program. Three pierces with the production
lead-in geometry land on a small scrap area. After cooldown,
inspect each pierce: clean dimple, no blowout, lead-in arc cleanly
joined to the cut line. If anything looks off, swap consumables
and re-test before the production cut.

`[PHOTO: three pierce holes, calipered]`

## Step 4 — Production cut

Run the trellis program. **Stay at the table the entire run.**
Pause every leaf or so to confirm the part hasn't shifted. The
program ends with the perimeter cut leaving a bridge tab; the
part should still be tied to the parent sheet when the torch
parks.

Total run time: ~25-35 minutes of cutting plus pauses.

`[PHOTO: torch mid-cut on a leaf cusp, sparks]`

## Step 5 — Cool, sever, and lift

Let the part cool on the table 5 minutes minimum. Sever the bridge
tab with a cut-off wheel on an angle grinder. Two-person lift the
trellis onto the welding table.

`[PHOTO: trellis lifted clear of the parent sheet]`

## Step 6 — Knock dross

Chipping hammer along the bottom edge into a catch tray. Most
dross will fragment off in chunks. Don't try to flap-disc curtain
dross — it'll load the disc immediately.

`[PHOTO: dross fragments in a tray]`

## Step 7 — Edge finish

Flap-disc the bottom edge: 40-grit until smooth, 80-grit for
finish. Then flap-disc the top edge with 80-grit only — minimal
dross there. Keep the disc moving; static contact burns a flat.

Wire-wheel both faces to remove most mill scale. The coater's
sandblast will finish the rest.

`[PHOTO: edge before and after flap-disc]`

## Step 8 — Inspect against the design

Lay the trellis on a flat reference. Tape-measure overall length
and width. Spot-check leaf chord lengths against `design.md`.
Record deltas in `validation.csv`.

`[PHOTO: tape measure overlaying the design drawing]`

## Step 9 — Spike weld (only if spikes are separate pieces)

The packet's primary plan cuts the spikes integral to the
silhouette — no weld step needed. If you opted to cut spikes
separately to save sheet:

1. Mark spike positions on the back of the bottom rail (centerline
   at x = 6 in and x = 18 in).
2. Clamp each spike square to the rail with a machinist's square.
3. MIG tack four corners of the spike footprint, then run a 1-in
   stitch on each side. Don't fully welt-around — outdoor mounting
   only needs structural tacks.

`[PHOTO: spike clamped square, tack welds visible]`

## Step 10 — Degrease for powder coat

Acetone-wipe the entire trellis with lint-free rags. After this
point, **nitrile gloves only**. Bag the part in plastic for
transport.

`[PHOTO: trellis bagged on a moving blanket in the truck]`

## Step 11 — Powder-coat handoff

Drop off at the coater. Spec sheet:

- Blast prep: SSPC-SP6 commercial blast.
- Pre-treat: iron-phosphate wash.
- Powder: matte black, RAL 9005 texture (or shop equivalent).
- Cure: per powder manufacturer's data sheet.
- Hooks: hang from the spike tips so the silhouette face shows
  no hook marks.

Lead time: typically 5-7 business days at a Bay Area coater.

`[PHOTO: trellis on the coater's rack]`

## Step 12 — Pickup and inspect

At pickup, inspect under shop light:

- No runs, sags, or orange-peel beyond the texture spec.
- No bare spots.
- No contamination (dust, fiber pickoffs).
- Even color across both faces.

If defects exceed spec, request rework before paying.

`[PHOTO: finished trellis, both faces, against a neutral wall]`

## Step 13 — Install in the garden

Choose the bed. Soft-loosen the soil where the spikes will go.
Drive the spikes with a sledge **through a wood buffer** (a 2x4
scrap on top of the bottom rail). Never strike the powder-coated
rail directly. Plumb with a level after seating.

If the soil is heavy clay, pre-drill spike holes with a metal
pry-bar to start, then drive. If the soil is rocky, relocate the
trellis — bent spikes are very hard to recover.

`[PHOTO: trellis installed, sunlit, hero shot for README]`

## Step 14 — Document for the portfolio

- Hero shot, both faces, in garden context.
- Detail shots: a leaf cusp, a tendril curl, a spike base.
- Pull `validation.csv` data into the README.
- Capture any deltas from the design as lessons learned in
  `risks.md` for the next packet.
