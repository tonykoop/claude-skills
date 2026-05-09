# Risks — Edge-Lit Acrylic Award Display

Red-team review of failure modes. Severity-grouped. Every risk has a
*test* — a way to confirm whether the mitigation worked.

## Severity: HIGH (safety, fire, injury, or build-killing failure)

### R-H1 — Wrong material in the laser

- **Failure mode:** maker brings polycarbonate (Lexan) instead of
  cast acrylic, runs it on the laser → toxic fumes, fire risk,
  damaged optics, banned-material incident report.
- **Why it happens:** PC and PMMA look identical on the shelf. Both
  clear, both rigid, both ~0.25" thick. Receipts get tossed; sheets
  get re-shelved by other members; mislabeled stock exists.
- **Mitigation:** buy from a vendor that prints CAST on the edge
  sticker (TAP Plastics does). Keep the receipt. If a sheet is
  unmarked, **don't laser it** — the fallback is the bandsaw +
  router-table edge polish for the panel cut. Confirm against
  `materials-policy.md` universal-bans list before any cut.
- **Test:** before powering the laser, hold the sheet up and call out
  "this is cast acrylic from TAP, receipt dated <X>." If you can't
  say that with confidence, abort.

### R-H2 — Acrylic ignition during cut

- **Failure mode:** focus off, power too high, or air-assist failed →
  acrylic flames during cut, fire, possible bed damage.
- **Why it happens:** improperly leveled bed, dirty mirrors, air
  pump unplugged, settings copied from a thicker-stock job.
- **Mitigation:** confirm air assist running before pressing start.
  Run a 1×1 test square on the offcut region with the planned
  settings; if it ignites or chars, abort and consult staff.
- **Test:** test square produces a clean through-cut with flame-
  polished edges and *no flame visible*. If you see flame at any
  point, hit pause.

### R-H3 — Tablesaw kickback during slot cut

- **Failure mode:** slot cut on the tablesaw is a captive cut. If the
  workpiece lifts or twists, kickback toward the operator.
- **Why it happens:** featherboard not deployed, blade height set
  wrong, hand-feed not push-block, twisty stock.
- **Mitigation:** featherboard pinning the workpiece to the fence;
  push-block always; blade set to 0.560 in (slot depth), no higher.
  If the slot cut feels sketchy, switch to the router table.
- **Test:** before the cut, verify the workpiece slides freely along
  the fence with the blade lowered, then raise blade and proceed.
  Never proceed with a workpiece that binds or rocks.

## Severity: MEDIUM (build is salvageable but slot/fit/finish suffers)

### R-M1 — Slot cut too narrow → cracked panel during fit-up

- **Failure mode:** maker hammers panel into slot → acrylic cracks
  along stress line. Build done.
- **Why it happens:** "it's almost in, just a little more" → applied
  force exceeds acrylic's notch sensitivity.
- **Mitigation:** test fit on a *scrap of the same acrylic stock*
  (cut off a 1×1 from the panel offcut) before final fit.
  Slot widening is reversible (recut 0.005 wider); cracks are not.
- **Test:** scrap-panel fit slides in with finger pressure, doesn't
  rock, doesn't require any force. If not, recut 0.005 wider.

### R-M2 — Slot cut too wide → panel rocks, glue required

- **Failure mode:** slot is sloppy, panel tilts or rocks → must glue,
  loses field-replaceability.
- **Why it happens:** over-shoot on second pass.
- **Mitigation:** approach final width in 0.005 in increments, not
  0.020 in jumps. Test each pass.
- **Test:** finger-pressure fit holds the panel plumb. If panel
  tilts > 1° from vertical without glue, slot is too wide → fallback
  is to glue with clear silicone (not epoxy — too rigid).

### R-M3 — LED strip facing wrong direction

- **Failure mode:** strip installed sideways or upside-down → light
  doesn't enter the panel edge → no edge-lit effect.
- **Why it happens:** strip is symmetrical at a glance; wires can be
  routed in either direction.
- **Mitigation:** before peeling adhesive backing, *power up the
  strip and confirm light direction* — LEDs visible side faces UP.
- **Test:** plug in and look — LEDs face the slot opening (panel
  edge). If unsure, peel and re-stick. Adhesive tolerates 1–2
  reseatings.

### R-M4 — Engraving too deep, panel weak

- **Failure mode:** engraving cuts too deep, weakening the panel
  along the engrave path → panel cracks if dropped.
- **Why it happens:** raster power set too high, multiple passes
  unintentionally.
- **Mitigation:** target depth 0.020 in. Test on scrap first.
  Single pass.
- **Test:** depth-gauge or fingernail check — engraving feels like a
  shallow scratch, not a groove. Depth ≤ 0.030 in.

## Severity: LOW (cosmetic / inconvenience)

### R-L1 — Yellow / melted engraving

- **Failure mode:** engraving comes out yellow-tinted instead of
  matte white → looks cheap.
- **Why it happens:** raster power too high, speed too low, beam
  defocused.
- **Mitigation:** test settings on scrap. Frosted matte white = good.
- **Test:** hold engraved panel against dark backdrop; color is
  bright matte white, not yellow or beige.

### R-L2 — Walnut tearout on slot cut

- **Failure mode:** slot edges chip on the visible top face.
- **Why it happens:** climb-cut direction on router, dull blade,
  figured grain.
- **Mitigation:** sharp blade; conventional cut direction; pick a
  walnut blank without figured grain across the slot path.
- **Test:** under raking light, slot edges are crisp — no chips
  bigger than 0.010 in.

### R-L3 — Cable strain pulling LED loose

- **Failure mode:** someone trips on the cord → strip rips out of the
  slot.
- **Why it happens:** no service loop; thin cable adhesive.
- **Mitigation:** leave a 1" service loop inside the slot before the
  cable exits. Tie a knot inside the slot as a strain relief.
- **Test:** with assembly complete, give the cable a gentle tug at
  the wall — base shifts as a unit, strip stays put.

### R-L4 — Felt feet shed and scratch surfaces

- **Failure mode:** cheap peel-stick felt sheds fibers or pulls free
  → award scratches the surface it sits on.
- **Why it happens:** low-quality adhesive.
- **Mitigation:** use rubber-cored felt feet (not pure felt). Check
  adhesion before delivery.
- **Test:** lift award by base, no feet detach. Run finger across
  base bottom, no fiber shedding.
