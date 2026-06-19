---
name: Hybrid hardware/software idea
about: Capture a hardware + software + firmware idea with an Expected PDM Artifacts checklist
title: "[hybrid] "
labels: ["capture", "maker"]
assignees: []
---

## Problem
<!-- What hurts today, in one or two sentences. The pain, not the solution. -->

## Intent
<!-- What "done" looks like. The outcome, not the implementation. -->

## Constraints
- Budget / cost ceiling:
- Timeline / deadline:
- Size / weight / power envelope:
- Standards / compliance:
- Shop / tooling limits:

## Discipline split

### Hardware (HW)
- Mechanical scope:
- Key dimensions / tolerances (mark observed / inferred / assumed):
- Materials / process:

### Software (SW)
- Host/app scope:
- Interfaces / APIs:

### Firmware (FW)
- Target MCU / board:
- Sensors / actuators / protocols:
- Power / boot / update strategy:

### Hybrid (system integration)
<!-- The cross-cutting concerns that no single discipline owns. This is what
     makes the issue hybrid rather than three parallel tracks. -->
- Interfaces between HW/SW/FW (what crosses each boundary):
- Shared timing / state / data contracts:
- Integration + end-to-end test strategy:
- Open coupling risks (where a change in one layer breaks another):

## Expected PDM Artifacts
<!-- Check the artifacts this idea will need before it is build-complete.
     Leave unchecked items visible so the gap is obvious. The first three are
     the required backbone for every hybrid issue; the rest are as-needed. -->

### Required backbone
- [ ] **ICD** — Interface Control Document defining every HW/SW/FW interface
- [ ] **Design Justification README** — why this design, trade-offs, rejected alternatives
- [ ] **CAD / source version** — pinned CAD revision + firmware/software commit or tag

### As needed
- [ ] CAD model (part/assembly) + revision
- [ ] Drawing(s) with GD&T where needed
- [ ] Bill of Materials (BOM) with sourcing
- [ ] Schematic (electronics)
- [ ] PCB layout / Gerbers
- [ ] Firmware source + build/flash instructions
- [ ] Wiring / harness diagram
- [ ] Test plan + acceptance criteria
- [ ] Calibration / setup procedure
- [ ] DHF / design-history links (if regulated or safety-relevant)
- [ ] Risk / FMEA notes
- [ ] Assembly / shop-floor work instructions
- [ ] Provenance / evidence ledger (if recovery or archive sourced)

## Open questions / unknowns
-

## Promotion target
<!-- maker-engineering / makerspace / specialist skill / project repo -->
