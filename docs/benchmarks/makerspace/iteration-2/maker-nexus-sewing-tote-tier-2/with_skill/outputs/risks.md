# Risks — Heavy-Duty Waxed Canvas Tote

Red-team walkthrough of failure modes, ordered by severity. Every
risk has a *test* attached so you can verify your mitigation
worked.

## R-01 — Industrial machine cert ambiguity (process risk)

**Risk:** Maker Nexus's `#textile-cert` currently covers domestic
*and* industrial sewing machines under one umbrella class
(`#class-textile-intro`, 2 hours). Other shop areas at Maker
Nexus have been splitting umbrella certs into machine-specific
sub-certs (cf. metalshop's lathe / mill / welder sub-certs noted
in `certifications.md`). If textile has split since this packet
was generated and the maker hasn't checked, they'll show up expecting
to use the walking-foot and find they need an industrial-machine
sub-cert they don't hold.

**Severity:** Medium (project-blocking, not safety-blocking).

**Mitigation:** Verify cert structure with the front desk or
textile-area channel *before* the build session. The README's
headline section calls this out.

**Workaround if blocked:** Do single- and double-layer ops on
the domestic machine; book a textile steward as a buddy for
the four high-stack ops (strap anchors, gusset corners, binding
crossovers, zipper end tabs).

**Test:** Confirmed cert status in member portal before build
day.

---

## R-02 — Strap anchor failure under load (catastrophic)

**Risk:** Strap anchors are the highest-stress joint in any
tote. If the bartack is undersized, or the canvas tears at the
attachment point, the strap rips off mid-carry. Result: contents
on the floor and possible bystander injury.

**Severity:** High (catastrophic failure mode).

**Mitigation:**
- Box-X bartack with 30+ stitches per anchor, walking-foot
  machine, Tex 70 bonded thread (op #15).
- 1.5" overlap of strap onto body panel — distributes load.
- Optional reinforcement: add a 2"×2" canvas patch behind the
  body panel at each anchor before bartacking.

**Test:** v012 in `validation.csv` — hang 25 lb from each strap
for 1 minute. No thread breakage, no fabric tear. The 25 lb is
1.25× the rated 20 lb working load.

---

## R-03 — Needle break crossing thick stacks (eye injury)

**Risk:** Crossing the bartack stacks (4 layers canvas + binding
+ strap = 6+ layers) at high SPM with a 110/18 needle can break
the needle. Fragments can fly toward the operator's face.

**Severity:** Medium (rare but real injury risk).

**Mitigation:**
- Safety glasses (mandatory — `safety-rules.md`).
- Reduce speed at the strap-anchor crossings — let the walking
  foot do the work, don't push fabric.
- Use a fresh 110/18 jeans needle for each high-stack op; old
  needles flex more before snapping.
- Consider a 120/19 needle for the highest-stack joints if
  available.

**Test:** Inspect the needle after each strap-anchor bartack.
Replace if there's any visible deflection or burrs.

---

## R-04 — Zipper failure under load (functional)

**Risk:** A #10 zipper is correctly specified, but the failure
mode is the *attachment* — if the zipper tape isn't stitched
through cleanly, the tape can pull free of the fabric under
load. Two-way pulls double the chance of a misaligned seam at
the slider crossover.

**Severity:** Medium (project-disabling, not safety).

**Mitigation:**
- Tex 70 bonded thread on the zipper seam (op #17).
- 3/8" SA on the zipper attachment — gives the seam something
  to bite into without crowding the teeth.
- End tabs (P-06) sealed and bartacked; this is where most
  zipper-tape failures start.
- Optional topstitch alongside the teeth (op #18) — anchors the
  fabric so it doesn't roll into the slider.

**Test:** v013, v014 in `validation.csv` — operate the zipper
end-to-end, tug each end tab.

---

## R-05 — Bottom seam abrasion in service (lifecycle)

**Risk:** The bottom corners of any tote are the highest-wear
zone. Set the bag on concrete a few times and the wax wears
through, then the cotton fibers, then the seam. This shows up
3-6 months in.

**Severity:** Medium (long-term durability, not immediate).

**Mitigation:**
- Bottom reinforcement panel P-04 doubles the canvas under the
  bottom 19" (op #19).
- Optional HDPE stiffener P-14 keeps the bottom from sagging
  and grinding against the ground.
- Re-wax the corners and the bottom edge every 6-12 months
  (op #28; M-14 in BOM).

**Test:** v023, v024 in `validation.csv` — 30-day soak test,
inspect wear pattern. Wear should be at corners/anchors, not
mid-panel.

---

## R-06 — Wax-clogged needle / thread breakage during build (process)

**Risk:** Beeswax/paraffin from the canvas accumulates on the
needle eye and shaft. Causes thread to drag, skip stitches, or
break. Operator wastes time and may compromise seam integrity
without noticing.

**Severity:** Low (annoying, not dangerous).

**Mitigation:**
- Wipe the needle every ~30 minutes with a lint-free rag.
- Silicone needle lubricant if the shop has it.
- Replace the needle if you see visible wax buildup.
- Reduce machine speed slightly when sewing waxed canvas vs
  unwaxed — heat from friction softens the wax onto the needle.

**Test:** v022 in `validation.csv` — visual inspection of every
seam for skipped stitches. Spot-check by tugging seams during
build.

---

## R-07 — Cotton lining shrinkage if not pre-washed (fit)

**Risk:** Cotton twill shrinks 2-4% on first wash. If lining
isn't pre-washed and the bag gets washed later, the lining
shrinks against the canvas (which doesn't shrink because of the
wax) and puckers the bag.

**Severity:** Low (aesthetic, not functional).

**Mitigation:** Pre-wash lining (op #1, phase 0).

**Test:** Visual inspection of the bag after first laundering
event. Lining should sit flat against the canvas.

---

## R-08 — Iron damage to wax (process)

**Risk:** Direct iron contact with the wax side at high heat
melts the wax, gums up the iron sole plate, and stains the
fabric. The next user of that iron also has problems.

**Severity:** Low (cosmetic + shop-citizenship).

**Mitigation:**
- Press waxed canvas from the lining side, or use a press cloth.
- Iron temperature at "wool" or below.
- Wipe the iron sole if any wax transfers.

**Test:** Inspect iron after use. Any wax residue → clean
immediately with iron cleaner.

---

## R-09 — HDPE stiffener too rigid → corner stress (long-term)

**Risk:** A 1/8" HDPE stiffener at the bag's exact bottom
dimensions (5×17") leaves no flex. Under heavy load, the
stiffener's corners can press into the fabric and create wear
points.

**Severity:** Low.

**Mitigation:**
- Round the stiffener corners to 0.5" radius (cut-list P-14).
- Cut stiffener 1/2" smaller than the bottom panel on each axis
  (5×17 vs the 6×18 finished bottom) so it floats.
- Drop-in sleeve (not sewn-in) — easier to remove if it ever
  causes problems.

**Test:** Inspect bag bottom after 30-day soak test — no visible
HDPE-corner imprints in the canvas.

---

## R-10 — Asymmetric strap length (aesthetic + functional)

**Risk:** If the two straps differ in length by more than 1/2",
the bag hangs lopsided and one strap takes more load.

**Severity:** Low (aesthetic + minor durability).

**Mitigation:** v009 in `validation.csv` — measure both straps
before bartacking the second.

**Test:** Hang the empty bag by the strap centers — should hang
level.

---

## Risk summary

| ID | Risk | Severity | Test |
|---|---|---|---|
| R-01 | Industrial cert ambiguity | Medium | Verify in member portal |
| R-02 | Strap anchor failure | High | v012 — 25 lb hang test |
| R-03 | Needle break / eye injury | Medium | Inspect needle, wear glasses |
| R-04 | Zipper failure under load | Medium | v013, v014 |
| R-05 | Bottom abrasion in service | Medium | v023, v024 |
| R-06 | Wax-clogged needle | Low | v022 |
| R-07 | Lining shrinkage | Low | Pre-wash, post-wash inspection |
| R-08 | Iron damage to wax | Low | Press cloth |
| R-09 | HDPE stiffener corner stress | Low | Rounded corners + size down |
| R-10 | Asymmetric straps | Low | v009 |
