# Dolly Design

## Function
- Transports 3 or 4 stacked toolboxes around the shop / jobsite.
- Provides a stable, low-profile rolling platform.
- The bottom box locks to the dolly via the same interlock pattern used between boxes (no separate hardware).
- Tall optional push handle for ergonomic moves.

## Geometry
- **Deck footprint:** `DollyWidth` x `DollyDepth` = (BoxWidth + 0.5 in) x (BoxDepth + 0.5 in)
  - For default 20 x 10 box: 20.5 x 10.5 in deck.
- **Deck construction:** Single sheet of 14 ga steel, 4-sided shallow tray (1.5 in upturned lip on all sides).
  - The upturned lip captures the bottom box perimeter (belt + suspenders to interlock).
- **Interlock pockets:** 4 female pockets stamped into deck floor, on the same grid as a box body bottom (driven by `InterlockGrid` sketch in MasterLayout).
- **Caster mount:** 4 reinforcement plates (10 ga, 4 x 4 in) welded/spot-welded to UNDERSIDE of deck at corners. Each plate has the `CasterBoltCircle` 4-hole pattern.

## Casters
- **Spec:** 3 in dia x 1.25 in wide polyurethane wheel, swivel top plate
- **Top plate:** 3 x 3 in square, 4-hole pattern on 2.5 in bolt circle (or 2-5/8 in)
- **Locking:** 2 of 4 casters have brake (front pair, accessible from push side)
- **Capacity:** 200 lb each (800 lb total, 4x margin over fully loaded stack)
- **Off-the-shelf example:** McMaster 2417T18 or equivalent

## Handle (Optional Add-on)
- **Tube:** 1 in OD x 0.083 in wall, mild steel, powder-coated black
- **Height:** 36 in above floor (ergonomic for push, not over for short users)
- **Style:** Inverted-U shape, 14 in wide grip
- **Mount:** Bolts to two upturned posts welded to dolly deck at one short side. Removable for tight storage.

## Loading Procedure
1. Set dolly on floor, engage caster locks.
2. Lower bottom box - interlock self-aligns it onto dolly.
3. Stack additional boxes (1, 2, or 3 more). Total stack = 3 or 4 boxes.
4. Release caster locks, push handle to move.

## Stability Analysis (rough)
- 4 boxes x ~50 lb load each = 200 lb at CG height of (DollyDeckHt + 2*BoxHeight) = 1.5 + 16 = 17.5 in
- Footprint: 20.5 x 10.5 in
- Tip angle (short axis): atan(10.5/2 / 17.5) = atan(0.30) = ~16.7 deg
- This is comparable to commercial dollies; acceptable for shop floor use.
- **Recommendation:** Limit to 4 boxes maximum; 3 boxes for off-shop transport on uneven ground.

## Parametric Behavior
- `BoxesOnDolly` global variable (3 or 4) drives the StackDemo assembly only - dolly part is identical for both.
- `DollyWidth` and `DollyDepth` auto-scale with `BoxWidth` and `BoxDepth`.
- For oversized box family (Large 24 x 12), upgrade to 12 ga deck and 4 in casters (separate config flagged in family table).

## Dolly Drawing Package
1. Dolly deck flat pattern (sheet metal)
2. Caster reinforcement plate (4x identical)
3. Handle tube weldment (cut list with bend coords)
4. Handle mount post (2x identical)
5. Dolly assembly drawing with welding callouts
6. BOM with caster part numbers
