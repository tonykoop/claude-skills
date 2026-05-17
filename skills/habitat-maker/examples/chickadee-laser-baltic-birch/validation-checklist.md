# Validation Checklist

Source: `geometry_params.json` -> `welfare_gates`,
`validation_targets_post_assembly`, and the shared gate shape in
`references/welfare-gate-schema.md`. Every item is **pass/fail with a
remedy** - do not proceed to the next phase with any failure unresolved.

## Welfare gates (REQUIRED — habitat-maker v0.2 contract)

These seven gates apply to every chickadee build packet in this skill.
They are species-agnostic for songbird cavity nesters.

- [ ] **G1 — No perch.** No exterior perch is fitted. Perches benefit
      predators and competitors, not the bird.
   - **Fail remedy:** Remove. There is no acceptable case for a perch on
     a chickadee box.
- [ ] **G2 — No interior finish.** Inside surfaces are bare wood. No
      paint, stain, oil, sealer, or glue beads on internal faces.
   - **Fail remedy:** Sand off any inside finish; rebuild if penetrated
     deeply.
- [ ] **G3 — Drainage.** All four 8 × 8 mm corner notches in the floor
      are open (P5).
   - **Acceptance test:** pour 250 mL water through the entrance with the
     box upright; full drainage in ≤ 60 s.
   - **Fail remedy:** Clear obstructions; re-cut floor if a notch is
     incomplete.
- [ ] **G4 — Ventilation.** Each side panel has 3 × (50 × 4 mm) vent
      slots open under the roof line (P3, P4).
   - **Acceptance test:** light an incense stick at the entrance on a
     still day; smoke draws upward and exits the vent slots.
   - **Fail remedy:** Clear char from slots; re-cut if any slot is
     incomplete.
- [ ] **G5 — Fledgling grip.** Five horizontal kerf-grip score lines are
      present on the inside face of the front panel below the entrance,
      ≤ 1 mm deep, no through-cuts (P1).
   - **Fail remedy:** Re-score with a sharp scribe by hand if the laser
     score didn't take.
- [ ] **G6 — Predator baffle.** A predator baffle is installed on the
      mount (pole or tree). Baffle top sits ≥ 18 in below the box.
   - **Fail remedy:** Install before deploying. Tree-mount without baffle
     is documented as not acceptable in this packet.
- [ ] **G7 — Cleanout access.** The right-side panel (P4) opens via its
      pivot screws and latch screw and re-seats without forcing.
   - **Fail remedy:** Adjust pivot screw torque (back out 1/2 turn at a
     time until the door swings free); replace if door is warped.

## Phase 1 — Pre-cut

- [ ] Stock confirmed as 6 mm Baltic birch, exterior phenolic glue (WBP).
- [ ] Sheet caliper at 4 corners + center: thickness 5.8–6.2 mm,
      variation < 0.3 mm.
- [ ] No surface delamination, no through-voids on edges.
- [ ] Laser bed clean, lens clean, alignment verified, fume extraction on,
      air assist on, CO₂ extinguisher within reach.

## Phase 2 — Test cut (kerf calibration)

- [ ] **Cut P7 kerf-test square first.** Measured outside dimensions
      within 50.00 ± 0.05 mm of nominal.
   - **Fail remedy:** Adjust kerf-offset by `(50.00 − measured) / 2`.
     Re-cut and re-measure until pass.
- [ ] Single box-joint slot pair from scrap: tight push, no rattle, no
      forcing.

## Phase 3 — Post-cut (per panel)

For each of P1–P6:
- [ ] Outline matches `cut-list.md` ± 0.3 mm at 3 sample dimensions.
- [ ] No char debris in box-joint slots.
- [ ] No incomplete cuts (panels lift cleanly out).

P1 (Front) specific:
- [ ] Entrance hole accepts a 28.6 mm dowel and rejects a 29.5 mm dowel.
- [ ] All 5 kerf-grip score lines present, ≤ 1 mm deep, no through-cuts.

P2 (Back) specific:
- [ ] Both mounting tabs intact (top 80 mm, bottom 30 mm).
- [ ] Mount holes accept #10 lag without binding.

P3 / P4 (Sides) specific:
- [ ] Trapezoidal outline (front edge taller than back edge).
- [ ] All 3 vent slots clear.
- [ ] **P4 has 3 pilot holes; P3 has none.** Common error: cutting two
      identical sides. Re-check.

P5 (Floor) specific:
- [ ] All 4 corner drainage notches present.

P6 (Roof) specific:
- [ ] All 4 pilot holes present.

## Phase 4 — Post-assembly

- [ ] Dry-fit complete before glue applied.
- [ ] After cure, diagonals match within 2 mm.
- [ ] Cleanout door swings freely with latch backed out 4 turns; no
      rattle with latch seated.
- [ ] Floor sits flat in dado; no rocking.
- [ ] Roof seated with `roof_overhang_front = 50 mm` ± 5 mm.
- [ ] No visible glue runs inside the cavity.
- [ ] Drainage test (G3) passes.
- [ ] Smoke test (G4) passes.
- [ ] Total assembled mass: 250–350 g.

## Phase 5 — Field deployment

- [ ] Mount height 5–7 ft on baffled pole (G6).
- [ ] Within 30 ft of woody cover.
- [ ] Entrance facing away from prevailing storm wind.
- [ ] Weeks 1–4: chickadee inspection or wasp activity logged in agent
      record.

## Sign-off

```
Box serial:       _____________
Cut by:           _____________   Date: __________
Assembled by:     _____________   Date: __________
Mounted by:       _____________   Date: __________
Mount location:   _____________   GPS:  __________
First occupancy:  _____________   Notes: __________
First fledge:     _____________   Notes: __________
```
