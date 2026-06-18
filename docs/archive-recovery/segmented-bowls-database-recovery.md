# Segmented Bowls Database Recovery

Issue: #51

## Contract

Issue #51 asks to review `Segmented Bowls Database.xlsx` from `To Organize2\`
and determine whether it should feed instrument-maker-v4 parametric tables or
migrate to reference docs, especially for the segmented-turning work in `conga`.

## Archive evidence

The matching archive file was found with a typo in the filename:

`/mnt/d/External Hard Drive Consolidation/Segmeted Bowls Database.xlsx`

Mounted archive metadata:

- Size: 29 KiB
- Timestamp: Feb 27 2016
- Format: Excel `.xlsx`
- Zip package entries: 20
- Worksheets: 6

Worksheet inventory from `openpyxl`:

| Sheet | Rows | Columns | Nonempty cells | Formula cells |
| --- | ---: | ---: | ---: | ---: |
| `Vessel #1` | 45 | 28 | 459 | 84 |
| `Sheet2` | 6 | 49 | 98 | 48 |
| `Vessel #4` | 51 | 24 | 381 | 61 |
| `Sheet1` | 75 | 6 | 195 | 75 |
| `Sheet5` | 32 | 15 | 220 | 0 |
| `Joe's Designs` | 13 | 23 | 162 | 0 |

The workbook includes segmented-vessel/bowl data such as side count, miter or
half-angle, layer number, width, length, base diameter, and formula-driven angle
tables. Example visible labels include:

- `6" Small Bowl - 12 Sides - θ=75°`
- `9" Medium Bowl - 12 Sides - θ=75°`
- `6" Vessel #4 - 16 Sides - θ=78.75°, Wall = .50"`
- `Joe's 1st Lidded Vessel`

## Downstream fit

`tonykoop/conga` exists and is private. The local checkout inspected was:

`/mnt/c/Users/Tony/Documents/GitHub/instruments/percussion/conga`

That repo already has a segmented-vessel pipeline:

- `tools/segment-designer.html` generates segmented vessel cut data.
- `conga-design-table.xlsx` exists as a current design table.
- `CAD/Conga/segmented/Segmented Conga.xlsx` is already recorded as a recovered
  segmented workbook archive.
- `visual-output-register.csv` marks the recovered segmented workbook as
  `reference_only` and says it must be mapped into the current packet before
  relying on it.

The conga README says the designer can generate ring-by-ring cut data with OD,
ID, segment edge length, board width, economy length, and miter angle. That maps
well to this recovered bowl workbook's side/angle/width/length formulas, but
the recovered bowl workbook should remain reference data until normalized and
validated against the current conga formulas.

No GitHub repo named `tonykoop/instrument-maker-v4` was found. In this context,
`instrument-maker-v4` appears to be a skill/reference target rather than a
standalone GitHub repo promotion target.

## Verification commands

Commands run from this `claude-skills` worktree:

```bash
qmd search "Segmented Bowls Database integrate into instrument-maker-v4"
qmd search "Segmented Bowls Database" -c instrument-builds
qmd search "segmented bowl" -c woodworking
gh issue view 51 -R tonykoop/claude-skills --json number,title,body,labels
find /mnt/c/Users/Tony/Documents/GitHub/archive -iname '*Segmented*Bowl*'
find /mnt/c/Users/Tony/Documents/GitHub/archive -iname '*bowl*.xlsx'
find /mnt/d/External\ Hard\ Drive\ Consolidation -maxdepth 5 -iname '*Segmented*Bowl*'
find /mnt/d/External\ Hard\ Drive\ Consolidation -maxdepth 5 -iname '*bowl*.xlsx'
ls -lh /mnt/d/External\ Hard\ Drive\ Consolidation/Segmeted\ Bowls\ Database.xlsx
python3 -c '<openpyxl workbook shape inspection>'
gh repo view tonykoop/instrument-maker-v4 --json nameWithOwner,visibility,url,defaultBranchRef
gh repo view tonykoop/conga --json nameWithOwner,visibility,url,defaultBranchRef
rg -n "segment|stave|bowl|ring|angle" /mnt/c/Users/Tony/Documents/GitHub/instruments/percussion/conga -S
sed -n '32,56p' /mnt/c/Users/Tony/Documents/GitHub/instruments/percussion/conga/README.md
sed -n '8,14p' /mnt/c/Users/Tony/Documents/GitHub/instruments/percussion/conga/visual-output-register.csv
ls -lh /mnt/c/Users/Tony/Documents/GitHub/instruments/percussion/conga/conga-design-table.xlsx /mnt/c/Users/Tony/Documents/GitHub/instruments/percussion/conga/CAD/Conga/segmented/Segmented\ Conga.xlsx
git -C /mnt/c/Users/Tony/Documents/GitHub/instruments/percussion/conga status --short --branch
```

## Assessment

#51 has concrete spreadsheet evidence. The workbook is relevant to segmented
turning and probably useful as reference input for conga's segmented-vessel
designer and future instrument-maker-v4 reference material.

Recommended next step:

1. Preserve the typo-bearing source filename in provenance notes.
2. Extract each worksheet to CSV or normalized JSON with explicit sheet names.
3. Map workbook fields to the current conga designer schema: sides, angle,
   layer, width, length, base/diameter, and derived segment calculations.
4. Add validation comparing recovered formulas with the current conga README
   formulas before using the data as fabrication authority.

Until that validation is done, treat the workbook as reference-only recovered
data, not a current cut list or shop-ready design table.
