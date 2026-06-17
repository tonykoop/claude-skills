# Hybrid Hardware / Software / Firmware Issue Template

Story #239. A reusable skeletal template for ideas that span hardware,
software, and firmware - the common shape for HWE/maker captures. Use this when
a capture clearly has more than one discipline, or when an idea will need PDM
(product data management) artifacts to be considered complete.

This is the **reference** copy. The GitHub-native issue form that produces this
shape on `New issue` lives at `.github/ISSUE_TEMPLATE/hybrid-idea.md` in the
repo root.

```markdown
Title: <short hybrid idea title>

## Problem
<What hurts today, in one or two sentences. The pain, not the solution.>

## Intent
<What "done" looks like. The outcome, not the implementation.>

## Constraints
- Budget / cost ceiling: <...>
- Timeline / deadline: <...>
- Size / weight / power envelope: <...>
- Standards / compliance: <...>
- Shop / tooling limits: <...>

## Discipline split

### Hardware (HW)
- Mechanical scope: <enclosure, mounts, mechanism>
- Key dimensions / tolerances (confidence-marked): <...>
- Materials / process: <...>

### Software (SW)
- Host/app scope: <UI, service, data flow>
- Interfaces / APIs: <...>

### Firmware (FW)
- Target MCU / board: <...>
- Sensors / actuators / protocols: <...>
- Power / boot / update strategy: <...>

## Expected PDM Artifacts
Check the artifacts this idea will need before it can be called build-complete.
Leave unchecked items visible so the gap is obvious.

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
- <thing that must be resolved before scoping>

## Suggested labels
- capture
- maker
- <electronics / software / firmware as applicable>

## Promotion target
- <maker-engineering / makerspace / specialist skill / project repo>
```

## Usage notes

- A hybrid idea rarely has every PDM artifact at capture time - that is the
  point. The unchecked boxes are the to-do list the promotion step inherits.
- Mark dimensions and tolerances with confidence (observed / inferred /
  assumed) when the source is a photo, sketch, or memory - mirror the
  `reverse-engineer` discipline.
- If the idea is single-discipline, drop the unused HW/SW/FW subsection rather
  than leaving it empty.
- Keep the body phone-readable; the checklist is the load-bearing part.
