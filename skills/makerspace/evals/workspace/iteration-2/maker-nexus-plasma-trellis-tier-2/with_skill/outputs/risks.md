# Risks — Climbing-Vine Plasma Trellis

Red-team pass. Each risk includes an **observable test** so the
maker can verify their mitigation actually worked.

## Cut-quality risks

### R1 — Kerf assumption is wrong, leaf cusps collapse

**Failure mode:** the design uses a 0.060-in kerf assumption.
Maker Nexus's actual machine and consumable state may differ.
If the actual kerf is larger, the inward-offset internal-cutout
path eats into the cusps and the 0.20-in design radius drops
below the visual limit (~0.15 in). The cusp goes from "leaf"
to "burr."

**Mitigation:** kerf-test coupon (KT1) before any production
cut. Update CAM kerf parameter if delta > 0.010 in.

**Test:** v001 in `validation.csv`. Caliper the cut walls; if
the actual gap between two 1.000-in-spaced cuts is outside
[0.930, 0.950] in, recalibrate.

### R2 — Pierce blowout on a leaf interior

**Failure mode:** if the pierce delay is too short or the air
is wet, the pierce blows through unevenly and leaves a crater
on the part edge. Visible on a powder-coated finish.

**Mitigation:** pierce-test coupon (P1) with production
lead-in geometry on scrap before production. Drain air filter
the morning of.

**Test:** v002. Inspect each test pierce; reject any with
visible blowout petals.

### R3 — Part shifts during the production cut

**Failure mode:** an 86-in × 24-in sheet on a slat table can
flex or shift if a magnetic hold-down is too far from a
recently-cut feature. A shifted part means the next cut goes
off-path, ruining the program.

**Mitigation:** magnetic hold-downs at four corners and two
midpoints. Sequence internal cutouts before perimeter so the
parent sheet stays rigid until the last moment. Bridge-tab the
final perimeter segment so the part doesn't release mid-cut.

**Test:** Pause every leaf and visually confirm position
against the table's reference grid. If anything has shifted
more than 1/16 in, cycle-stop and reset.

### R4 — Heavy dross on the bottom edge

**Failure mode:** wrong feeds/speeds for the actual machine
and consumable state produces curtain dross that's hard to
remove and contaminates the powder-coat finish under the
texture.

**Mitigation:** kerf-test coupon doubles as a dross-quality
check. If the bottom edge of KT1 has curtain dross, dial
parameters before production: try +10% travel speed first.

**Test:** drag a finger (gloved!) along the KT1 bottom edge;
should feel like fine sandpaper, not like a saw blade.

## Structural risks

### R5 — Tendrils break off in handling or installation

**Failure mode:** the tendrils are 0.50-in-wide ribbons curling
back on themselves. They're the thinnest features and have a
high stress-concentration where they branch from the stem. A
sledgehammer impact during install transmits shock that can
crack the branch point.

**Mitigation:** strike the spike-end through a 2x4 wood buffer
during install. Never strike the rail or stem directly. Two-
person handle the trellis from the bottom rail and the top
tip, never from a tendril.

**Test:** v013 flatness check post-install. Visually inspect
each tendril branch under raking light for cracks. If a
tendril shows a hairline at the branch, it's going to fail
within the first season.

### R6 — Spike bends or shears in rocky soil

**Failure mode:** 1/4" mild steel spikes are stiff but not
unbreakable. Driven into rocky soil they can deflect, bend, or
shear at the rail-to-spike fillet.

**Mitigation:** pre-loosen soil where spikes will go. If the
bed is rocky, pre-drill with a rock bar before driving. Don't
force a spike that's not going.

**Test:** v014 plumb check. If a spike isn't plumb after
seating, it's already deflected — pull it, relocate, retry.

### R7 — Wind load on the broad face

**Failure mode:** 6 ft × 2 ft is enough sail area to feel
gusts. With shallow spikes, the trellis can lean over the
season as the soil compacts.

**Mitigation:** 12-in spike length sized for typical garden
soil. If the install site is exposed (open lawn, no
windbreak), drive a second pair of stakes flanking the trellis
and zip-tie or U-bolt the trellis to them.

**Test:** v015. After 30 days, check plumb again. If the
trellis has leaned more than 5 deg, add lateral stakes.

## Finish risks

### R8 — Powder coat fails at sharp edges first

**Failure mode:** powder coat is thinnest at sharp edges
(electrostatic Faraday-cage effect). The leaf cusps and the
spike tips are where rust will start if coverage is marginal.

**Mitigation:** spec SSPC-SP6 blast prep + iron-phosphate
pretreat at the coater. Inspect cusps and tips at pickup under
shop light.

**Test:** v011 visual at pickup. Then v015 at 30 days outdoor
— any tiny rust speck at a cusp means the coverage there was
marginal; touch up with a spray-can matching color.

### R9 — Body oil from handling causes coating fisheyes

**Failure mode:** any bare-hand contact between acetone wipe
and powder application leaves an oil shadow that the
powder-coat will fisheye over, leaving a visible defect.

**Mitigation:** nitrile gloves only after acetone wipe. Bag
the part for transport. Tell the coater the part has been
degreased.

**Test:** v011. Fisheyes are obvious under raking light.
Reject and request rework before paying.

### R10 — Heat distortion warps the trellis

**Failure mode:** an 86-in 1/4" plate has a lot of stored
residual stress. As the plasma cuts release stress unevenly,
the part can bow up to 1/4 in across its length. The
powder-coat oven (~400 deg F for 20 min) can either relax some
of this OR add to it.

**Mitigation:** sequence internal cutouts before perimeter to
keep the parent sheet rigid as long as possible. Cool the part
on the table 5+ min before lifting. After dross removal, lay
on a flat reference to check.

**Test:** v013 flatness. If deviation exceeds 1/8 in across
86 in, gently flatten with mechanical persuasion (a rubber
mallet on a flat surface) before sending to the coater. If
deviation appears after the coater, that's typically not
warranty-covered.

## Process risks

### R11 — Plasma consumables degrade mid-program

**Failure mode:** electrode hafnium pit deepens, nozzle bore
opens up, kerf widens, lead-ins go off-spec mid-program. Late
features come out worse than early ones.

**Mitigation:** start with fresh consumables. Have a spare set
on the bench. Estimate 12 pierces in this program; the Powermax
65 fine-cut electrode is rated for ~75 pierces in clean
conditions but degrades faster with wet air or aggressive cuts.

**Test:** mid-program pause after the most-interior leaf
finishes. Inspect the electrode through the shield. If the
hafnium pit is past the manufacturer's wear line, swap before
continuing.

### R12 — Wet compressed air destroys consumables fast

**Failure mode:** Maker Nexus shop air may have moisture if the
filter hasn't been drained recently. Wet air at the torch
splits the arc, multiplies dross, and burns electrodes in a
fraction of normal cycles.

**Mitigation:** drain the air filter the morning of. If the
shop has a desiccant cartridge, check its color.

**Test:** the kerf-test coupon will show it. Wet-air symptoms
are: erratic arc sound, heavy bottom dross, a noticeably
discolored cut wall. Stop and investigate before production.

## Documentation risk

### R13 — The next maker can't replicate this

**Failure mode:** if Tony cuts this once, learns the actual
kerf and parameters, but doesn't write the numbers back into
this packet, the next person (or future Tony) starts from
scratch.

**Mitigation:** after the production cut, update `design.md`
with the measured kerf. After 30 days outdoor, update
`risks.md` with anything that actually went wrong. Push the
updated packet to GitHub.

**Test:** read the packet six months later. If it still
matches what was actually done, the documentation worked.
