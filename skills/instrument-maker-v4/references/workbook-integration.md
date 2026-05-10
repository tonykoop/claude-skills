# Workbook Integration — v4 (rewritten)

This reference rewrites v3's `workbook-integration.md` with the *actual*
schema of the two source workbooks Tony uses, derived from
`scripts/inspect_instrument_workbook.py` runs in May 2026.

The two workbooks have different jobs:

- **`Musical Instruments V2.xlsx`** is the *design surface*. 54 sheets,
  one per instrument family or category. Each instrument sheet has the
  blue-cell input convention (input cells colored blue, formula cells
  not) so a human can poke values and see derived dimensions update.
- **`Instrument Workshop Master v3.xlsx`** is the *operations
  surface*. 16 sheets organized as a relational model — one row per
  instrument in the Master Catalog, foreign keys to design sheets,
  CAD/CNC files, materials, builds, suppliers, training, DoE studies.

In v4, the operations workbook gets promoted to a SQLite database (see
`catalog-database.md`); the design workbook remains the human-edit
surface but its sheet structure is documented here in detail.

## Musical Instruments V2.xlsx — 54 sheets

### Sheet categories

The 54 sheets group into 9 functional categories. The category determines
how the sheet is structured and which generator scripts know how to read
it.

#### Reference / index

- `Index` — workbook-level index of all instrument sheets
- `Technical Drawings` — drawing references and layouts
- `Tuning Reference` — frequency reference (A4 = 440 Hz, scale tables)
- `Mode 1&4 Pent.` — scale-mode reference (pentatonic mode 1 and 4
  offsets)
- `Wolfram Export` — staging area for export to Wolfram notebooks

#### Workshop / business

- `Built` — log of completed instruments
- `Price Calculator` — pricing model
- `Customers` — customer/order history
- `Pivot Table 2` — analysis pivot (probably built/sold by family)

#### CNC operations

- `CNC Flute Dimensions` — CNC parameters per flute design
- `CNC Guitar Bodies` — CNC parameters for guitar body cutouts

#### Wind instruments — duct flutes

- `Low to High Range` — fujara range chart (legacy NAF design table)
- `Irish Flute`, `Shakuhachi`, `Tin Whistle`
- `Fujara`, `Kena - Kenacho`, `Xiao Family`, `Duduk Family`
- `Moseño`, `Andean Duct Flutes`, `Siku - Zampoña`
- `Didgeridoo`

#### Wind instruments — vessel flutes / bagpipes

- `Ocarina`
- `Great Highland Bagpipe`

#### Percussion — beam idiophones

- `Tongue Drum`, `Steel Tongue Drum`, `Wood Shell Tongue Drum`,
  `Ceramic Tongue Drum`
- `Marimba`, `Xylophone`, `Glockenspiel`
- `Tubular Bells`
- `Resonant Box`
- `Duntong`

#### Percussion — drums

- `Segmented Ashiko`, `Segmented Conga`
- `Cajón`
- `Handpan`, `Steel Pan`
- `Udu Drum Family`

#### Strings

- `Floor Harp`
- `Whamola Bass`
- `Ukulele`, `Acoustic Violin`
- `Kora`, `Ngoni`, `Stave Lute-Oud`
- `Electric Guitar Bodies`, `Electric Violin`, `Ceramic Electric
  Violin`

#### Misc

- `Rainstick`
- `Sheet1`, `Sheet2` — scratch sheets

### Common per-instrument sheet structure

Each instrument sheet typically has:

1. **Header band** (rows 1–3) — title, family, key/scale, blank.
2. **Input block** (rows 5–~20) — blue cells where the user types
   target fundamental, target key, material, dimensions to fix.
3. **Derived block** (rows ~20–~40) — formula cells that pull from
   input block. Frequencies, lengths, hole positions, scale offsets.
4. **Per-note schedule** (rows ~40–~80) — one row per note in the
   scale; each row has frequency, position from end, hole diameter,
   etc.
5. **Validation block** (bottom) — sanity checks, A4 reference,
   tolerance.

Formula counts and blue-cell counts vary widely:

- Most-formula sheets: `Kena - Kenacho` (797), `Xiao Family` (675),
  `Tin Whistle` (500), `Irish Flute` (500), `Didgeridoo` (504).
- Most-blue-cell sheets: `Xiao Family` (425), `Kena - Kenacho` (382),
  `Tin Whistle` (336), `Irish Flute` (299), `Shakuhachi` (289),
  `Moseño` (228), `Didgeridoo` (205).

The legacy `Low to High Range` sheet is the original cross-tab fujara
design table — 897 formulas across 34000 cells. It's flagged in
`Instrument Workshop Master v3.xlsx → Design Sheets` as needing
modernization into one-row-per-variant.

### Blue-cell convention (preserve when extending)

Tony's input convention is **blue fill = user input, no fill = derived
formula**. When the orchestrator dispatches the manufacturing-planner
or acoustician to extend the workbook, preserve this convention. New
input cells must be blue-filled; new formula cells must reference the
input cells, not contain hardcoded values.

`scripts/inspect_instrument_workbook.py` reports `blueish` count per
sheet by detecting cells with blue fill (theme color or RGB). Use this
as the audit signal — if you add a sheet and `blueish` is 0, you broke
the convention.

## Instrument Workshop Master v3.xlsx — 16 sheets

### Sheets and tables

Every sheet has a named Excel table with a clean schema. The schema is
the source-of-truth for the v4 catalog database promotion.

| Sheet | Table | Range | Key columns |
|---|---|---|---|
| `Start Here` | `Table_1` | A13:D27 | Sheet, Purpose, Use When, Go To Tab |
| `Dashboard` | (no table) | counts | KPI cells via COUNTIF/COUNTA |
| `Master Catalog` | `Table_2` | A4:X266 | 24 columns (full schema below) |
| `Design Sheets` | `Table_3` | A4:L64 | 12 columns |
| `SolidWorks Tables` | `Table_4` | A4:N74 | 14 columns |
| `CAD CNC Library` | `Table_5` | A4:V126 | 22 columns |
| `Production Log` | `Table_6` | A4:Q244 | 17 columns |
| `Materials Inventory` | `Table_7` | A4:R144 | 18 columns |
| `BOM Budget` | `Table_8` | A4:L94 | 12 columns |
| `Suppliers Resources` | `Table_9` | A4:K44 | 11 columns |
| `Training Plan` | `Table_10` | A4:L64 | 12 columns |
| `Contacts` | `Table_11` | A4:J64 | 10 columns |
| `Roadmap` | `Table_12` | A4:I54 | 9 columns |
| `Legacy Imports` | `Table_13` | A4:G54 | 7 columns |
| `Lists` | (no table) | A4 | Validation lists |
| `DoE Studies` | `Table_14` | A4:L7 | 12 columns *(new vs v3)* |

### Master Catalog — full schema (Table_2, A4:X266)

This is the canonical schema. Every other table foreign-keys back to
`Master Catalog` via `Instrument ID`.

```
Column A  Instrument ID                    e.g. TNG-001, ASH-001, NAF-G4-PAD
Column B  Family                           Drums, Woodwinds, Strings, ...
Column C  Instrument Type                  Tongue drum, Native American style flute, ...
Column D  Variant/Size                     Small, Family member, ...
Column E  Key/Scale                        D minor / A minor, G4, ...
Column F  Design Stage                     Research, Concept, Sized, ...
Column G  Build Status                     Idea, In progress, Built, Legacy imported
Column H  Priority                         High / Medium / Low
Column I  CAD Design ID                    FK → CAD CNC Library
Column J  CNC Plan ID                      FK → CAD CNC Library
Column K  Material ID                      FK → Materials Inventory
Column L  Primary Material                 Steel or hardwood top, Padauk, ...
Column M  Target Price                     numeric
Column N  Estimated Cost                   numeric
Column O  Estimated Margin                 formula: =IF(OR(M="",N=""),"",M-N)
Column P  Maker Nexus Tool                 ShopBot CNC, 100W laser, lathe, ...
Column Q  Next Step                        free text
Column R  Due Date                         date
Column S  Notes                            free text
Column T  Source Workbook                  legacy import provenance
Column U  Source Sheet                     legacy import provenance
Column V  Source Row                       legacy import provenance
Column W  Legacy Link/Design Sheet         FK → Design Sheets
Column X  GitHub Repo                      e.g. https://github.com/tonykoop/tongue-drum
```

### DoE Studies — new in v3 → exposed in v4

The `DoE Studies` sheet (`Table_14`, A4:L7) is the bridge between the
Workshop Master workbook and the per-instrument GitHub repo's
`study/` folder. Schema:

```
Study ID, Instrument ID, Family, Study Name, Phase, Status,
Hypothesis / Research Question, Repo Path, Protocol Path,
Data Path, Last Updated, Notes
```

Example row:

```
DOE-TNG-001, TNG-001, Drums, "Tongue Drum Key Tuning",
"Phase 1 — Small drum: noise floor + species sweep",
"Documentation only — no data collected",
"Q1 wood-property variance bound; Q2 dominant geometric tuning levers; Q3 cantilever-scaling f1 prediction within ±X cents",
https://github.com/tonykoop/tongue-drum,
https://github.com/tonykoop/tongue-drum/blob/main/study/README.md,
tongue-drum/study/data/  (CSV per session — schema in study/data-template.csv),
2026-04-26,
"Build the magazine-plan small drum first..."
```

In v4, `references/doe-integration.md` documents how to read this sheet,
follow the `Data Path`, and ingest measurement CSVs back into the
empirical-learning loop.

### Design Sheets — modernization index (Table_3)

This sheet inventories which sheets in `Musical Instruments V2.xlsx`
(and other legacy workbooks) need to be normalized from cross-tab
acoustic calculators into one-row-per-variant design records that can
foreign-key against `Master Catalog`.

Schema:

```
Design Sheet ID, Family, Instrument Type, Design Sheet Name,
Source Workbook, Current Structure, Rows, Columns,
Modernization Status, Canonical Fields Needed,
Next Transformation, Notes
```

When the orchestrator dispatches you to extend a sheet in
`Musical Instruments V2.xlsx`, check `Design Sheets` first — it tells
you whether the target sheet is "Needs normalization" (the cross-tab
era) or already "Normalized" (one-row-per-variant). For "Needs
normalization" sheets, the right move is to add the new variant in the
*new* normalized sheet and leave the legacy cross-tab in place for
historical reference.

### CAD CNC Library (Table_5)

Per-CAD-design tracker. Schema:

```
Design ID, Family, Instrument Type, Variant/Size, Key/Scale,
Source Design Sheet, CAD File Path, Drawing File Path,
CAM File Path, CNC/Toolpath File, Machine/Process,
Work Envelope Check, Material Thickness, Tooling/Bit,
Workholding/Jig, Toolpath Status, CNC Readiness, Revision,
Last Reviewed, Next CAD Task, Notes, GitHub Repo
```

`CNC Readiness` values: Research, Ready for CAM, Ready for test cut,
Proven. The `Dashboard` counts "Ready for CAM" + "Ready for test cut"
+ "Proven" as the readiness KPI.

### SolidWorks Tables (Table_4)

Tracker for SolidWorks design-table-driven configurations. Schema:

```
SW Table ID, Family, Instrument Type, SolidWorks File,
Design Table Name, Configuration Examples, Driving Parameters,
Outputs to Track, Source Data, Linked CAD/CNC ID, Priority,
Status, Next Step, Notes
```

This is where Tony's parametric SolidWorks workflow is tracked.
`Driving Parameters` lists the Excel-linked parameter cells (e.g.,
`ShellHeight, HeadDiameter, BaseDiameter, StaveCount, StaveThickness,
BevelAngleTheta, LengthL, DimensionsA-D` for a stave ashiko).

### Production Log (Table_6)

Build history. Schema:

```
Build ID, Instrument ID, Family, Instrument Type, Operation, Status,
Start Date, Finish Date, Maker Nexus Tool, Material ID,
Time Hours, Shop Fee/Outside Cost, Materials Cost,
Total Direct Cost, QC/Tuning Result, Next Step, Notes
```

`Total Direct Cost` is a formula: `=IF(COUNTA(K:M)=0,"",SUM(K:M))` —
sum of time, shop fee, materials.

### Materials Inventory (Table_7)

```
Material ID, Category, Material/Species, Form, Dimensions,
Qty On Hand, Unit, Unit Cost, Total Value, Supplier,
Storage Location, Moisture %, Status, Allocated To,
Reorder Point, Need to Buy, Notes, Source
```

`Total Value` formula: `=IF(OR(F="",H=""),"",F*H)` (qty × unit cost).
`Need to Buy` formula: `=IF(AND(F<>"",O<>"",F<O),"Yes","")` (flags
when below reorder point).

### Lists — validation drop-downs

The `Lists` sheet provides drop-down values used throughout the
workbook (families, instrumentTypes, designStages, buildStatuses,
priorities, tools, cadStatus, materialCategories, materialForms,
materialStatuses, yesNo, productionStatus). When extending a table,
respect these enumerations — don't introduce new values without
adding them to `Lists` first.

## How v4 generators read these workbooks

Each generator script reads a specific subset:

- `inspect_instrument_workbook.py` — generic auditor; works on any of
  these and on `Flutes-AI.xlsx`.
- `build_catalog_db.py` — reads all 14 named tables from
  `Workshop Master v3.xlsx` and writes them as SQLite tables. Foreign
  keys are inferred from the column names (`Instrument ID`,
  `Material ID`, etc.).
- `generate_build_packet.py` — reads one row from `Master Catalog` (by
  `Instrument ID`) and one sheet from `Musical Instruments V2.xlsx` (the
  design sheet) and emits a `build-packets/<slug>/` folder.
- `record_measurement.py` — appends to a packet's `validation.csv`,
  updates `Production Log` in `Workshop Master v3.xlsx` (or the
  promoted SQLite db, if it exists), and updates the per-family
  corrections database.
- `generate_drawings.py` — reads `family-spec.csv` (in the packet) and
  emits SVGs.
- `generate_capstone_docs.py` — reads the packet folder, doesn't touch
  the workbooks directly.
- `generate_site.py` — reads the packet folder and the deck/print
  artifacts; doesn't touch the workbooks directly.

## Things to never do to these workbooks

- **Don't break the blue-cell convention** in
  `Musical Instruments V2.xlsx`. New inputs must be blue-filled.
- **Don't paste static computed dimensions** where a formula belongs.
  Future-Tony will twiddle the input and expect the dependent cells to
  update.
- **Don't introduce new column orderings** in `Workshop Master v3.xlsx`
  tables. Other sheets `INDEX/MATCH` against these columns by header
  name; reordering breaks formulas silently.
- **Don't add free-text where a `Lists` enumeration is expected.** Add
  the new value to `Lists` first.
- **Don't delete legacy cross-tab sheets** in `Musical Instruments V2`
  marked "Needs normalization." Modernize alongside, leave the original
  intact for historical reference.
