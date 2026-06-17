# Guided Design Intake

Use `scripts/design_input.py` when a user asks for a new instrument, family,
or packet but has not already selected a Master Catalog row or workbook sheet.
The goal is to lower the floor without replacing the catalog/workbook system.

## Inputs To Capture

- Instrument ID, family, instrument type, variant/size, key/scale.
- Target fundamental or range.
- Primary material and construction pipeline.
- Design workbook and sheet when one exists.
- Done-bar reference repo to model on.
- Notes about constraints, unknowns, or why this design exists.

## Workflow

1. Prefer existing artifacts first: Master Catalog, `Musical Instruments V2.xlsx`,
   current repo files, sketches, photos, measurements.
2. If the user starts from a fuzzy idea, run:

```bash
python3 scripts/design_input.py \
  --instrument-type "Duntong" \
  --family "cylindrical tongue drum" \
  --key-scale "D minor pentatonic" \
  --primary-material "Cherry" \
  --infer-sheet "Duntong" \
  --output-dir ./build-packets/<slug>/data
```

3. Read `design-intake.json` before dispatching specialists.
4. Feed `design-input-row.csv` into workbook, catalog, or packet generators as
   the canonical single-row starting point.
5. Keep `TBD` values visible. Do not hide unknowns inside narrative prose.

## Workbook-Aware Behavior

`design_input.py --list-sheets` prints the sheets in `Musical Instruments V2.xlsx`.
`--infer-sheet` performs a lightweight name match and records a hint block with
sample row labels, formulas, and blue input cells. Treat the hint as orientation,
not proof that the sheet is complete for the requested design.

## Output Contract

`design-intake.json` is the human-readable/full record. `design-input-row.csv`
is the stable machine handoff. Downstream scripts and workbook updates should
preserve these column names:

```text
instrument_id,family,instrument_type,variant_size,key_scale,
target_fundamental_hz,primary_material,construction_pipeline,
design_workbook,design_sheet,master_workbook,done_bar_repo,notes
```
