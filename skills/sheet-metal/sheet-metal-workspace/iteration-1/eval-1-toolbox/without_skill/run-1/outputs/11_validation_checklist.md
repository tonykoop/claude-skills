# Design & Manufacturability Validation Checklist

## Parametric Integrity
- [ ] Changing `BoxWidth` from 20 to 24 in MasterLayout causes full assembly rebuild without errors.
- [ ] Changing `BoxHeight` from 8 to 12 propagates to body height, lid position unchanged.
- [ ] Changing `BoxDepth` from 10 to 12 propagates to body depth, dolly width auto-grows.
- [ ] Switching design table configuration (Small / Medium / Large) rebuilds in < 30 sec.
- [ ] Zero "dangling" external references after configuration change.
- [ ] All sheet metal flat patterns remain valid across all configurations.

## Sheet Metal Manufacturability
- [ ] All bends are 90 deg (or documented exception).
- [ ] No flange shorter than 4T (~0.19 in for 18 ga).
- [ ] All hole-to-bend distances >= 2.5T verified via Measure tool.
- [ ] All hole-to-edge distances >= 2T.
- [ ] All bend reliefs present at torn corners (4 per box body, 4 per lid, 4 per dolly).
- [ ] Closed corners specified for all body/lid corners (butt or overlap chosen).
- [ ] Flat pattern of each part fits within 48 x 96 in stock sheet.
- [ ] K-factor consistent (0.44) across all features.
- [ ] No feature requires a "trapped" bend (impossible press-brake sequence).
- [ ] Forming-tool features (interlock embosses) use library forming tools, not freeform pockets.

## Stacking & Interlock
- [ ] Male boss height = `InterlockHt` (0.250 in) confirmed in lid model.
- [ ] Female pocket depth = `InterlockHt + SheetThk` confirmed in body model.
- [ ] Clearance per side = `InterlockClear` (0.015 in) -> total fit gap 0.030 in.
- [ ] 15 deg draft applied to both male and female features.
- [ ] Boxes self-align from up to 0.060 in lateral offset in test (verify via assembly motion study).
- [ ] Two stacked boxes do not exceed 2 x `BoxHeight` total height (no gap between, no overlap penalty).
- [ ] Top of bottom box and bottom of top box share contact plane fully (no edge crushing).
- [ ] Dolly female pockets share the same grid as body female pockets.

## Dolly
- [ ] Dolly deck width = `BoxWidth + 2*DollyClearance` matches user's box selection.
- [ ] Caster bolt pattern fits selected caster (3 x 3 in, 2.5 in bolt circle).
- [ ] 4 boxes fully stacked on dolly is stable on level ground (CG within footprint).
- [ ] Caster wheels do not protrude beyond dolly footprint (toe-stub risk).
- [ ] Brake casters located on push-handle side (operator-accessible).
- [ ] Handle clear of stack when boxes loaded.
- [ ] Handle removable for storage.

## Strength / Function
- [ ] Box body loaded with 50 lb static doesn't deflect more than 0.030 in at floor center (FEA or hand calc).
- [ ] Lid handle pocket can sustain 60 lb single-hand lift (one-handed carry case).
- [ ] Latches engage and disengage without binding.
- [ ] Hinge pins captured (cannot fall out in service).
- [ ] Empty box weight < 15 lb (target).

## Drawings
- [ ] All 12 drawings created and reviewed.
- [ ] Title blocks complete (revision, scale, material, finish, designer, date).
- [ ] All critical dimensions toleranced.
- [ ] Bend tables present on every sheet metal flat pattern.
- [ ] BOM table on each assembly drawing.
- [ ] DXF files exported for laser cutter, layers correctly named.

## Cost / Procurement
- [ ] Per-box fabricated cost < $50 in volume (BOM target).
- [ ] Per-dolly fabricated cost < $175 in volume.
- [ ] All purchased components have valid part numbers and active vendors.
- [ ] Powder-coat vendor identified and pricing locked.

## Safety / Compliance
- [ ] All external corners rounded R 0.125 in min.
- [ ] All internal sheet edges deburred.
- [ ] Capacity label on each box and dolly (load rating).
- [ ] No pinch points in lid/body engagement.
- [ ] Casters certified for stated capacity.

## Documentation
- [ ] Design brief (this package) approved.
- [ ] Global variables locked (no orphaned constants in features).
- [ ] Design table verified against family of sizes spec.
- [ ] Modeling plan archived with files for next engineer.
- [ ] All 12 deliverable docs in `outputs/` folder, version stamped.
