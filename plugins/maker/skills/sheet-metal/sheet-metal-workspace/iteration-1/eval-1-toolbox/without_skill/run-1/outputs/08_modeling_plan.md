# SolidWorks Modeling Plan (Step-by-Step)

## Phase 0: Set Up Project Folder
1. Create folder `Toolbox_System/` with subfolders: `parts/`, `assemblies/`, `drawings/`, `flat_patterns/`, `library/`.
2. Set SW system options:
   - Units: IPS (inch, pound, second), 3 decimal places.
   - Drafting standard: ANSI.
   - Sheet metal default K-factor: 0.44.

## Phase 1: Master Layout Part (~30 min)
1. New part: `00_MasterLayout.sldprt`. Save to `parts/`.
2. Open Equations dialog. Paste global variables from `02_global_variables.txt`.
3. Create sketch `BoxFootprint_Top` on Top plane:
   - Center rectangle at origin, dimensioned `BoxWidth` x `BoxDepth`.
4. Create sketch `BoxProfile_Front` on Front plane:
   - Rectangle from origin, `BoxWidth` x `BoxHeight`.
   - Horizontal construction line at `BodyHeight` (lid split).
5. Create sketch `InterlockGrid` on Top plane:
   - 4 points at corners inset by `InterlockInset`.
   - Convert to a derived sketch usable by Body and Lid.
6. Create sketch `DollyOutline_Top` (offset of BoxFootprint_Top by `DollyClearance`).
7. Create sketch `CasterPattern` (4 points inset 1.0 in from corners of DollyOutline_Top).
8. Add named reference planes: `LidSplit`, `DollyDeckTop`, etc.
9. **Save.** This part has no solid bodies - that's correct.

## Phase 2: Box Body (~1.5 hr)
1. New sheet metal part: `10.1_Body.sldprt`. Save under `parts/`.
2. Insert MasterLayout as base reference (Insert > Part > 00_MasterLayout, position at origin, do NOT bring in solid bodies, only sketches/planes).
3. Sheet Metal > Base Flange/Tab:
   - Sketch on Top plane: Convert Entities from `BoxFootprint_Top`.
   - Thickness: link to global `SheetThk`.
   - Bend radius: link to `BendRadius`.
   - K-factor: link to `KFactor`.
4. Edge Flange on all 4 perimeter edges:
   - Flange length: link to `BodyHeight - SheetThk` (so finished OAH = BoxHeight - LidHeight + lap).
   - Use Bend Outside material condition.
   - Add rectangular bend reliefs (Rectangular, ratio 1.5, depth 2T).
5. Closed Corners on all 4 corners (Butt type).
6. Add interlock pockets (female):
   - Forming tool OR Emboss feature using sketches derived from `InterlockGrid`.
   - 4 pockets, square pyramidal, depth `InterlockHt + SheetThk`.
   - Draft 15 deg.
7. Add hand-grab cutout (optional v1) on each short end:
   - Slotted hole, 4 in x 1 in, centered, top edge 1.5 in from rim.
   - Edge-to-bend distance check vs `MinHole2Bend`.
8. Add corner stitch-weld pattern (just sketch marks for shop).
9. Verify flat pattern: Sheet Metal > Flatten. Inspect for self-intersections.
10. **Save.**

## Phase 3: Lid (~1 hr)
1. New sheet metal part: `10.2_Lid.sldprt`.
2. Insert MasterLayout reference.
3. Base Flange:
   - Sketch: offset of `BoxFootprint_Top` outward by `LidLapDepth - SheetThk` so lid skirts overlap body walls.
4. Edge Flanges, length `LidHeight`, all 4 edges, BENT DOWNWARD.
5. Closed Corners.
6. Add interlock bosses (male):
   - 4 emboss features, square pyramidal frustum, height `InterlockHt`.
   - Draft 15 deg, positioned via `InterlockGrid`.
7. Add handle pocket:
   - Recessed pocket in top center, `HandleWidth` x 2 in, depth `HandleDepth`.
   - This is a separate emboss before main bends.
8. Hinge mount holes on rear edge: 2 sets of 2 holes, 1/8 in dia, for pop rivets to hinges.
9. Latch keeper holes on front edge: 2 holes spaced `LatchSpacing`, 5/16 in dia.
10. Verify flat pattern.
11. **Save.**

## Phase 4: Box Sub-Assembly (~30 min)
1. New assembly: `10_Box.sldasm`. Save under `assemblies/`.
2. Insert `00_MasterLayout` first, fix at origin.
3. Insert `10.1_Body`. Mate three planes (Front-to-Front, Right-to-Right, Top-to-BoxBottom of master).
4. Insert `10.2_Lid`. Distance mate to layout `LidSplit` plane (or use BoxTop and offset).
5. Insert hinge x 2, draw latch x 2, foot x 4 (purchased components - simplified models OK).
6. Verify rebuild. Test change: edit `BoxWidth` in MasterLayout, rebuild assembly, confirm body and lid grow.

## Phase 5: Dolly Parts (~1.5 hr)
1. New sheet metal part: `20.1_DollyDeck.sldprt`.
2. Insert MasterLayout reference.
3. Base Flange from `DollyOutline_Top` sketch.
4. Edge Flange on all 4 edges, length `DollyWallHt`, bent UP.
5. Closed Corners.
6. Interlock pockets (female) - same as Body Bottom, positioned via `InterlockGrid` (offset for dolly clearance).
7. Caster mount holes - 4 patterns of 4 holes from `CasterPattern` sketch, dia `CasterBoltDia`.
8. Reinforcement plate `20.1.1_CasterPlate.sldprt`:
   - Flat plate 4 x 4 in, 10 ga, with caster bolt pattern.
   - Acts as backing under the deck.
9. New weldment part: `20.2_DollyHandle.sldprt`:
   - 3D sketch of inverted-U: two 36 in verticals + one 14 in horizontal crossbar.
   - Apply Structural Member: 1 in OD x 0.083 wall, plain carbon steel.
10. **Save.**

## Phase 6: Dolly Assembly (~30 min)
1. New assembly: `20_Dolly.sldasm`.
2. Insert MasterLayout, then DollyDeck, then 4x CasterPlate, then 4x Caster (simplified purchased model).
3. Add Handle and mount posts as optional config (`with_handle` vs `no_handle` configuration).

## Phase 7: Stack Demo Assembly (~30 min)
1. New assembly: `99_StackDemo.sldasm`.
2. Insert `20_Dolly` first, fix at origin.
3. Insert `10_Box`, mate to dolly's interlock pockets.
4. Linear Component Pattern: direction = vertical, spacing = `BoxHeight`, instances = `BoxesOnDolly`.
5. Add display states: `3_boxes`, `4_boxes`.
6. Add exploded view for marketing/instruction images.

## Phase 8: Family Table / Design Configurations (~45 min)
1. In `00_MasterLayout`, open ConfigurationManager.
2. Insert > Design Table > Auto-create. SW pulls in all globals.
3. Open in Excel, paste rows from `03_parameters_family_table.csv`.
4. Save and close. SW generates a configuration per row.
5. Test: switch configurations in top assembly, verify rebuild.

## Phase 9: Drawings (separate session, see `09_drawing_list.md`)

## Phase 10: Validation (see `11_validation_checklist.md`)
