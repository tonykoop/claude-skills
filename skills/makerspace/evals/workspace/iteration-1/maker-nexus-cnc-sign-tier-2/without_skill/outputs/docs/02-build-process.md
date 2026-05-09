# Build process

A start-to-finish shop log written in the order I'd actually run it.

## 0. Before leaving home

- [ ] CAD/CAM finalized; toolpaths simulated.
- [ ] G-code exported and copied to USB stick (filename: `welcome-sign-v1.nc`
      or whatever the Maker Nexus post wants).
- [ ] Printed copy of the toolpath summary (`cam/toolpaths.md`).
- [ ] Bits packed: 60 deg V-bit, 1/8" two-flute upcut. Spares of each.
- [ ] Calipers, feeler gauges, painter's tape, double-sided tape.

## 1. Stock prep (Maker Nexus woodshop, ~30 min)

1. Pull the 24 x 30 in Baltic birch sheet from inventory or your bin.
2. **Inspect both faces.** Pick the cleanest one - that's the show face
   and goes UP on the CNC bed.
3. On the table saw, rip a 20 in wide strip, then crosscut to 8 in. End
   blank: 20 x 8 in.
4. Joint one long edge so it's straight - useful as a fence reference if
   the CNC fixture wants a square edge.
5. Lightly sand the show face with 180 grit to knock off mill marks. Do
   NOT round the edges yet.
6. Mark a small pencil arrow on the back face pointing "up" so you don't
   load the blank rotated 180 deg.

## 2. CNC setup (~20 min)

1. Boot the controller, home all axes.
2. Vacuum the spoilboard. Inspect for any stuck debris or screws.
3. Apply 4-6 strips of double-sided carpet tape to the spoilboard in the
   footprint of the blank. Avoid the toolpath area where possible (tape
   under a profile cut is fine; tape under a deep V-carve is not).
4. Press the blank down, show face up, with the pencil arrow oriented
   away from the operator. Walk on it or use a roller - tape needs
   pressure to stick.
5. Load the 60 deg V-bit. Set stick-out to ~0.75 in (enough for the
   0.18 in carve plus dust shoe clearance, no more).
6. Set work zero:
   - X/Y at the lower-left corner of the blank (or wherever your CAM
     post expects). Use an edge finder or jog by eye to a pencil tick
     mark.
   - Z on top of stock using the touch plate.
7. **Air-cut the first 30 seconds with the spindle off**, jogging Z
   up by ~1 in, to confirm the toolpath origin is where you think it is.

## 3. The cut (~25 min spindle time)

1. Start dust collection.
2. Run the V-carve toolpath. Watch the first letter ("W") finish before
   leaving the machine. Listen for chatter - if the carve sounds
   buzzy, pause and slow the feed by 20%.
3. When the V-carve completes, **do not** lift the part. Tool change to
   the 1/8" upcut. Re-zero Z on top of stock (X/Y stays).
4. Run the perimeter profile. This toolpath includes 4 tabs (one per
   side, ~0.25 in long, 0.06 in tall) so the part doesn't fly free at
   the end.
5. Pause the spindle. Vacuum the bed before moving anything.

## 4. Release and clean up (~15 min)

1. Slide a thin putty knife under the part to break the carpet tape.
2. Cut the four tabs with a flush-trim Japanese saw or a sharp utility
   knife.
3. File or sand the tab nubs flush.

## 5. Sanding (~30 min)

| Pass | Grit | Tool | Notes |
|---|---|---|---|
| 1 | 120 | random orbit | Faces only - skip the V-carves |
| 2 | 180 | random orbit | Faces only |
| 3 | 220 | hand block | Faces |
| 4 | 220 | folded sheet | Edges and a light ease (NO roundover) |
| 5 | - | compressed air | Blow chips out of the V-carves |

Do **not** sand inside the V-carves with a power tool - you'll round
the crisp edges that are the whole point of V-carving.

## 6. Finish (~45 min active, +overnight cure)

See `docs/04-finishing.md` for the full procedure.

## 7. Hardware

- Drill a small starter hole or rout a keyhole slot on the back top
  center for a single #8 panhead wood screw.
- Felt bumpers on the back two bottom corners keep the sign from
  rocking on the wall.

## 8. Photograph

Shoot before installation - see `photos/README.md` for the shot list.

## 9. Reset the shop

- Vacuum the bed and the floor under the CNC.
- Wipe the spindle and table.
- Return the touch plate, tape, and any borrowed bits.
- Log the session in whatever check-in system Maker Nexus uses.
