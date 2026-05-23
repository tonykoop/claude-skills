# Validation Checklist - Pass/Fail Gates

Treat each gate as blocking. A FAIL on any item means the corresponding
deliverable is not authoritative.

## Authority And Inputs

- [ ] Material thickness measured (not assumed from gauge table) for at
      least one sheet of each thickness in the build.
- [ ] Inside bend radius confirmed against the actual brake punch in use,
      not the SolidWorks default.
- [ ] K-factor confirmed against a measured bend coupon for each material
      and thickness.
- [ ] Hinge model selected; knuckle, leaf length, and bolt pattern frozen.
- [ ] Latch model selected; base pattern, keeper geometry, and grip range
      frozen.
- [ ] Caster model selected; bolt pattern, height, load rating frozen.

## CAD (SolidWorks)

- [ ] MLP contains all global variables matching `parameters.csv`.
- [ ] MLP has no production sheet metal bodies (planes/sketches only).
- [ ] Every production part derives controlling sketches from the MLP, not
      from a sibling.
- [ ] Design table on MLP rebuilds across all four seed configurations
      with no rebuild errors.
- [ ] Each sheet-metal part has a working Flat Pattern feature in all
      configurations.

## Geometry And DFM (Per Part)

- [ ] Inside bend radius >= material thickness for every bend.
- [ ] Straight flange length >= `Min_Flange` (4 x T) on every flange.
- [ ] Hole-to-bend distance >= `Min_Hole_To_Bend` (3 x T) on every hole or
      slot adjacent to a bend.
- [ ] Bend reliefs present at every flange termination; default circular
      relief diameter = `Relief_Size` (2 x T).
- [ ] Corner reliefs present at every intersecting flange pair.
- [ ] Hem style verified achievable on the chosen brake.
- [ ] No closed corner followed by a hem on the same edge.

## DXF Hygiene (Per Part)

- [ ] 1:1 scale, units in inches, documented in filename and drawing note.
- [ ] All loops closed.
- [ ] Splines converted to arcs/lines if required by CAM workflow.
- [ ] Layers correctly assigned (cut / mark / etch / bend-centerline /
      construction / registration / drill-later).
- [ ] Bend-centerline layer excluded from CAM.
- [ ] Nest margin >= 0.5 in around each part.

## Test Coupons

- [ ] Bend coupon for 16 ga mild steel at planned R and K - measured
      length matches calculated flat pattern within 0.020 in.
- [ ] Bend coupon for 12 ga mild steel at planned R and K - same tolerance.
- [ ] Tear-drop hem coupon at 16 ga - formed cleanly without cracking on
      the available brake.
- [ ] Tab-and-slot joint coupon - slot fit acceptable after kerf
      compensation.
- [ ] Stack-rim coupon - lid rim and box base shoulder mate with 0.020 to
      0.040 in clearance.

## Functional (Box)

- [ ] Lid opens to at least 100 deg without binding.
- [ ] Both draw latches engage with audible detent and hold lid closed
      under finger-pull test.
- [ ] Tub rim is flat within 0.030 in; lid skirt seats around tub without
      gap or interference.
- [ ] No raw edges accessible to bare hands anywhere on the assembly.
- [ ] Foot pads recessed inside stack shoulder so they don't lift the box
      off the rim below.

## Functional (Stack)

- [ ] Box drops onto rim of box below without forcing; locates with
      `Clearance_Gap` slip-fit.
- [ ] Stack-coupling draw latches engage and compress adjacent boxes.
- [ ] 3-high stack passes tilt test (15 deg each axis) with latches
      engaged - no separation.
- [ ] If 4-high is in scope: 4-high stack passes same tilt test, or 4-high
      is explicitly disallowed in user-facing documentation.

## Functional (Dolly)

- [ ] Bottom box drops onto dolly deck rim with same fit as box-on-box.
- [ ] All four casters spin and pivot (where swivel-rated) without
      binding.
- [ ] Swivel casters with brakes hold the dolly stationary on a level
      floor under a 3-high stack.
- [ ] Handle spine engages receiver bracket cleanly; deploys to hand-truck
      angle without flex that exceeds 0.250 in measured at the top of the
      handle under empty-stack load.
- [ ] Caster bolt pattern reinforced with doubler plates as specified.

## Load And Safety

- [ ] Stated maximum stack height in user-facing documentation.
- [ ] Stated maximum total stack weight in user-facing documentation,
      based on caster rating and tested.
- [ ] Center-of-gravity warning for stacks over 3-high.
- [ ] No overhead/lifting use case. If one appears, route to
      maker-engineering safety gate before any rated lifting hardware is
      added.
- [ ] No cat/pet/child-facing use case for this packet. If cat furniture
      or child-carry use case appears, route to a safety gate per the
      sheet-metal skill's animal/child-contact rules.

## Documentation

- [ ] Drawing package: 1 assembly drawing + 1 flat-pattern drawing per
      sheet-metal child part.
- [ ] Each flat-pattern drawing has: material callout, thickness, bend
      table (angle, radius, direction, allowance), inside radius and
      K-factor used, critical dimensions tagged.
- [ ] Each DXF filename follows `SWTB_{PART}_{MATERIAL}_{THICK_MILS}_{REV}`
      pattern.
- [ ] `agent-record.md` current with assumptions and reviewed-vs-generated
      status.

## Stop-Work Triggers

Stop and escalate (do not proceed to fabrication) if:

- A test coupon shows K-factor off by more than 0.04 from planning.
- A required hem cannot be formed on the available brake.
- Casters cannot be sourced at the assumed bolt pattern - the dolly deck
  must be redesigned, not patched.
- Loaded stack passes tilt test only at 2-high - cap the user-facing rated
  stack at 2-high.
- The user requests cat-facing, child-facing, vehicle-mounted, or overhead
  use of this hardware - route to a safety gate first.
