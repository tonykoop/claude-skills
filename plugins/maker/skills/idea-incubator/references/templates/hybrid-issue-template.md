# Hybrid Hardware / Software / Firmware Issue Template

Story #239. A reusable skeletal template for ideas that span hardware,
software, and firmware - the common shape for HWE/maker captures. Use this when
a capture clearly has more than one discipline, or when an idea will need PDM
(product data management) artifacts to be considered complete.

This is the **reference** copy. The GitHub-native issue form that produces this
shape on `New issue` lives at `.github/ISSUE_TEMPLATE/hybrid-idea.md` in the
repo root. Keep both files in sync — the GitHub form is what users see; this
reference is what the conformance checker (`scripts/check_hybrid_issue_template.py`)
tests against as a drift guard.

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

### Hybrid (system integration)
- Interfaces between HW/SW/FW (what crosses each boundary): <...>
- Shared timing / state / data contracts: <...>
- Integration + end-to-end test strategy: <...>
- Open coupling risks (where a change in one layer breaks another): <...>

## Expected PDM Artifacts
Check the artifacts this idea will need before it can be called build-complete.
Leave unchecked items visible so the gap is obvious. The first three are
the required backbone for every hybrid issue; the rest are as-needed.

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
- **ICD** is required for any issue where hardware and software/firmware interact.
  At minimum it names the bus (I2C / SPI / UART / CAN), the baud rate or clock,
  and who is master. A one-paragraph ICD is enough at capture time.
- **Design Justification README** records why key choices were made (why this
  MCU, why this topology, why this material). Even a bullet list at capture time
  is valuable — it prevents re-litigating the same trade-offs at promotion.
- **CAD / source version** pins the revision so the ICD and justification stay
  coherent over time. Use a git commit hash or a file revision tag.
- Mark dimensions and tolerances with confidence (observed / inferred /
  assumed) when the source is a photo, sketch, or memory - mirror the
  `reverse-engineer` discipline.
- If the idea is single-discipline, drop the unused HW/SW/FW subsection rather
  than leaving it empty. Keep "Hybrid (system integration)" whenever two or more
  disciplines interact.
- Keep the body phone-readable; the checklist is the load-bearing part.

## Detecting non-conforming hybrid issues

Use `scripts/check_hybrid_issue_template.py` to detect issues that skipped the
template backbone. It checks for the required sections and artifacts from a file,
stdin, or a live issue via `gh`:

```bash
# Check a local file
python3 scripts/check_hybrid_issue_template.py --body-file issue.md

# Check a live issue (requires gh + repo access)
python3 scripts/check_hybrid_issue_template.py --issue 239

# List open maker issues and check each (example sweep)
gh issue list --label maker --state open --json number,body \
  | python3 -c "
import json, sys, subprocess, shlex
for i in json.load(sys.stdin):
    r = subprocess.run(
        ['python3', 'scripts/check_hybrid_issue_template.py', '--stdin'],
        input=i['body'], capture_output=True, text=True
    )
    if r.returncode != 0:
        print(i['number'], r.stdout.strip())
"
```

A zero-result output means all issues conform. Non-conforming issues can be
flagged with `needs-clarification` and a comment pointing to the template.
