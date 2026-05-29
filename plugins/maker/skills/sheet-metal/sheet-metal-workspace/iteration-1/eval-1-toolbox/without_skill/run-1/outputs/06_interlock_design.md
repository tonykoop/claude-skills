# Stacking Interlock Design

## Concept
Each box stacks on the one below via four corner interlocks plus an optional center alignment rib. The geometry is **emboss/coin formed** into the sheet metal of the lid (male, protruding up) and the bottom of the body (female, protruding down/recessed up). No separate parts - the interlock is a feature of the body and lid sheet metal.

```
   ----------- Lid top face -----------
   |   [M]                   [M]    |    <-- 4 male bosses protrude UP
   |                                |
   |          (handle pocket)       |
   |                                |
   |   [M]                   [M]    |
   ----------------------------------
            (box above sits here)
   ----------------------------------
   |   [F]                   [F]    |    <-- 4 female pockets recessed UP into bottom
   |                                |
   |        Body bottom face        |
   |                                |
   |   [F]                   [F]    |
   ----------------------------------
```

## Male Boss (Lid)
- **Shape:** Square pyramidal frustum (square base, smaller square top) to ease alignment
- **Base footprint:** `InterlockSize` x `InterlockSize` = 1.000 x 1.000 in
- **Top footprint:** `InterlockSize - 2*InterlockHt*tan(15)` ~ 0.866 in (15 deg draft per side)
- **Height:** `InterlockHt` = 0.250 in
- **Position:** 4 corners, inset by `InterlockInset` = 0.625 in from each outside wall
- **Forming:** Stamped/pressed before main lid bends. Single-station press die.

## Female Pocket (Body Bottom)
- **Shape:** Mirror of male, with `InterlockClear` = 0.015 in clearance per side
- **Base footprint:** 1.030 x 1.030 in
- **Depth (from outside bottom):** `InterlockHt + SheetThk` to allow boss to seat fully
- **Position:** Matches male grid exactly via shared master sketch
- **Forming:** Same press die operated in reverse direction

## Engagement
- **Lead-in:** 15 deg draft self-centers boxes within 0.060 in misalignment
- **Engagement height:** 0.250 in - enough to resist lateral slide but allows easy unstack
- **Removal force:** ~5 lb (deliberate two-hand lift, no latches required)

## Optional Center Rib
For boxes wider than 20 in, add a single longitudinal rib:
- 0.250 in tall, 0.500 in wide, full depth of box
- Stamped at the same time as corner interlocks
- Counterpart groove on box bottom
- Prevents lid-flex induced wobble in long stacks

## Dolly-Side Mating
- Dolly deck has the same **female pocket pattern** as a body bottom.
- Bottom box drops onto dolly and self-aligns just like stacking on another box.
- This means: dolly == body bottom face, for interlock purposes.

## Parametric Behavior
- Boss/pocket positions are driven by `InterlockInset` from each corner of `BoxFootprint_Top` in MasterLayout.
- When `BoxWidth` changes, inserts stay inset from corners - they move outward with the box, maintaining the same fit regardless of size.
- Same interlock geometry works across the entire family-of-sizes (Small/Medium/Large) - boxes of different footprints CANNOT stack on each other (intentional - prevents instability), but boxes of the SAME footprint can stack regardless of height.

## Failure Modes Addressed
| Risk | Mitigation |
|---|---|
| Stack tips during transport | Draft + corner pattern resists shear in all 4 directions |
| Boxes won't separate | Light interference (clearance, not press fit) + draft |
| Hard to align in dark/dirty environment | 15 deg lead-in cone |
| Bottom box slips off dolly | Same interlock + 1.5 in upturned dolly walls capture box perimeter |
