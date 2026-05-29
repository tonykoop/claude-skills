# CNC/Laser Fabrication Handoff Blocker Checklist

This example is a generator-backed handoff gate for projects where a design
repo has to move into laser cutting, CNC routing, or a fabrication partner's
CAM workflow.

The generated checklist is a blocker list, not a pass certificate. It can show
that every required gate is present and schema-valid, but shop readiness still
depends on fabrication-owner review of the CAD/DXF revision, drawings,
materials, CAM setup, workholding, and safety constraints.

## Files

- `design_params.json` is the single source of truth for the example.
- `handoff_checklist.json` is the generated machine-readable checklist.
- `validation.csv` is the generated shop-audit view using the standard
  makerspace `validation.csv` schema.

Regenerate the checked-in outputs with:

```bash
python3 skills/makerspace/scripts/generate_cnc_handoff_checklist.py
```

For an isolated comparison run:

```bash
python3 skills/makerspace/scripts/generate_cnc_handoff_checklist.py \
  --out-dir /tmp/makerspace-cnc-handoff-check
cmp /tmp/makerspace-cnc-handoff-check/handoff_checklist.json \
  skills/makerspace/references/examples/cnc-laser-fabrication-handoff/handoff_checklist.json
cmp /tmp/makerspace-cnc-handoff-check/validation.csv \
  skills/makerspace/references/examples/cnc-laser-fabrication-handoff/validation.csv
```

## Use

Route here when the user asks whether a DXF, CAD folder, CAM setup, or
fabrication repository is ready for another person or shop to cut. This also
fits repo-backed woodworking, furniture, jig, fixture, puzzle-box, and
mechanism projects when the concept already exists and the missing step is a
shop-floor handoff. Extract only fabrication-relevant facts from the repo and
leave private/story context out of public shop docs.

The output should block handoff when revision authority, units, layers,
material, workholding, CAM assumptions, or safety policy are still implicit.
Passing schema validation only proves the checklist is structurally readable;
it does not certify that a fabrication partner can cut the job.

Generated concept images can support story or review, but they are never a
substitute for the CAD/DXF revision, drawing callouts, and CAM setup record.
