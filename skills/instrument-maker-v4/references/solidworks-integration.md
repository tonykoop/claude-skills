# SolidWorks Integration — v4

Tony's preferred parametric workflow is **master sketch + design table + global
equations**. SolidWorks holds the geometry; an Excel design table (embedded as
a Sheet inside the .SLDPRT) holds the per-configuration values; and a set of
named global variables under `Tools > Equations > Manage Equations` ties them
together.

This reference is the canonical doc for v4's SolidWorks side. It covers:

1. The three pillars — global equations, design tables, and the master-sketch convention.
2. The naming and units conventions Tony uses on both sides (Excel and SW).
3. The `Extract_Dimensions.swp` macro: what it does, what it emits, and how the skill consumes its CSV.
4. Two scripts the skill ships for SW work: `ingest_dimension_csv.py` (validate SW vs Excel) and `generate_sw_design_table.py` (emit a design-table xlsx from `family-spec.csv`).
5. The "design table" sheet format that SolidWorks expects (what a generator must emit to be SW-compatible).

When the user prompts you for SolidWorks work — "set up the SW model", "extend the design table", "extract dimensions", "verify SW matches Excel" — read this doc first.

---

## 1. The three pillars

### Global Equations (`Tools > Equations > Manage Equations`)

These are the named variables Tony hand-edits. Convention:

- snake_case identifiers, identical to the Excel `Master_Inputs` sheet variable names.
- Every numeric value in the model is *either* a global *or* an equation that references a global. **No hand-edited dimensions in features.** If a dimension exists in a feature, it must come from `=<global>` or `=<arithmetic with globals>`.
- Units: Tony uses inches in the equation values (`= 18in`, `= 0.5in`). SW interprets unit-suffixed numbers correctly even if the document's master units are millimeters.

Example from `TNG-000_MasterLayout`:

```
"drum_len_in"   = 18in
"drum_wid_in"   = 10in
"drum_hgt_in"   = 6in
"top_thk_in"    = 0.5in
"bottom_thk_in" = 0.5in
"side_thk_in"   = 0.5in
"end_cap_thk_in"= 0.5in
"slit_kerf_in"  = 0.125in
```

Quote the LHS variable name in the equation editor; SW preserves the quotes.

### Design Table (`Insert > Tables > Design Table > From Existing File`)

The design table is an Excel sheet *embedded* in the part. SW reads from it on every rebuild.

- Source: an `.xlsx` with a single sheet. Header row 2 has the special control columns and `$VALUE@<global_name>@Equations` columns.
- Each subsequent row is one configuration.
- Cell values are written as SW formulas: `=18in`, `=8` (unitless), `=0.5in`. SW substitutes them into the named globals when the configuration activates.

Example from `TNG-000_MasterLayout` (7 configurations, 46 columns):

| Configuration | $DESCRIPTION | $COLOR | $VALUE@drum_len_in@Equations | $VALUE@drum_wid_in@Equations | $VALUE@top_thk_in@Equations | … |
|---|---|---|---|---|---|---|
| MASTER_TEMPLATE | MASTER_TEMPLATE | 15000804 | =18in | =10in | =0.5in | … |
| Large_Bilateral_16T | Large - 8 tongues per side | 15000804 | =24in | =10in | =0.5in | … |
| Medium_Bilateral_12T | mid-sized - 6 per side | 15000804 | =22in | =9in | =0.4in | … |
| Medium_Bilateral_10T | Medium_Bilateral_10T | 15000804 | =18in | =8in | =0.35in | … |
| Small_Baseline_8T | Small_8T | 15000804 | =12in | =9.5in | =0.3in | … |
| Small_Baseline_6T | small 6 tongue, one side | 15000804 | =12in | =7.5in | =0.25in | … |
| Large_Bilateral_14T | Large_Bilateral_14T | 15000804 | =23in | =9in | =0.5in | … |

The first three columns (`$DESCRIPTION`, `$COLOR`, plus the configuration name) are SW reserved; the rest of the columns are user-defined `$VALUE@<global>@Equations` references.

When SW rebuilds, the active configuration's row drives the global equation values, which drive every dimension that references those globals — top of the chain.

### Master sketch convention

The master sketch sits on the Front plane and contains the *driving* dimensions for the part's overall envelope. Other sketches reference it via `Convert Entities` or `Pierce` relations. This keeps the dependency graph clean: the master sketch is the root; everything downstream rebuilds through it.

Tony's preferred sketch dependency order (from the `drone-flutes/sw-reference/` doc):

```
Sketch_Master_Profile (root, on Front plane)
  ├── Reference plane: Foot_Plane (offset along master)
  ├── Reference plane: Window_Plane (offset along master)
  ├── Sketch_Bore_Profile (pierces master, references diameters)
  ├── Sketch_Tone_Holes (pierces master, references hole offsets)
  └── Sketch_Inlay_Layout (references facet width, band positions)
```

When you (the agent) propose a new SW model, follow this hierarchy. Don't introduce a sketch that bypasses the master profile.

---

## 2. Naming and units conventions

| Side | Convention |
|---|---|
| Excel `Master_Inputs` sheet | snake_case identifiers, blue cells = inputs, no formulas |
| SW global equations | identical snake_case identifiers, quoted LHS, `=<value>in` form |
| SW design-table headers | `$VALUE@<same_global_name>@Equations` |
| SW dimension full names | `<dim_name>@<sketch_name>@<part_name>.Part` |
| Macro CSV `DimFullName` | identical to SW dimension full name |
| Excel `Design_Table` sheet | one column per configuration, formulas referencing `Master_Inputs` |

The *iron-clad* rule: **the same identifier must appear unchanged on both sides**. If `drum_len_in` is the global on the SW side, it is `drum_len_in` in `Master_Inputs!B7`, in the SW design-table column `$VALUE@drum_len_in@Equations`, and in the macro CSV `DimFullName` substring (e.g., `drum_len_in@SK_OUTER_BOX@TNG-000_MasterLayout.Part`).

The only place identifiers diverge is when SW auto-generates a sketch-local copy with `_sketch` appended — that's a SW behavior we tolerate but don't propagate. The macro CSV reports both forms when both exist (one row per dimension entity).

---

## 3. The `Extract_Dimensions.swp` macro

`assets/solidworks/Extract_Dimensions.swp` is Tony's hand-written SolidWorks VBA macro. It walks a SolidWorks assembly, iterates every component, every configuration, every feature, and every dimension, and emits a CSV with one row per dimension entity per configuration.

The macro is stored as a Microsoft Compound Document (OLE2 container) — the standard SW VBA format. It is **opaque to non-SW tooling** (you can't read the source from outside SW), but its **output schema is the contract** the rest of v4's SW tooling depends on.

### Output schema (canonical)

```
AssemblyConfigName    — the active assembly configuration (e.g., MASTER_TEMPLATE)
Component             — the part instance (e.g., TNG-000_MasterLayout-1)
ConfigName            — the part-level configuration (often same as assembly config)
FeatureName           — the SW feature (e.g., SK_OUTER_BOX, SK_CAVITY, SK_HEIGHT_STACK)
FeatureType           — ProfileFeature, Equation, etc.
DimFullName           — the SW full dimension name, e.g. drum_len_in_sketch@SK_OUTER_BOX@TNG-000_MasterLayout.Part
Value_mm              — value in mm (SW's stored canonical units)
Value_in              — value in inches (computed for Tony's shop)
Tolerance_Type        — N/A or per-feature tolerance class
IsDriven              — TRUE if dimension is driven (computed) rather than driving
IsLinked              — TRUE if dimension is linked across multiple sketches
IsGlobalVar           — TRUE if this row represents a global equation (vs a feature dimension)
EquationOrComment     — the global's equation string (e.g., "drum_len_in" = 18in) or comment text
```

### Reference example

`assets/solidworks/sample-dimensions-extract.csv` is the May 2026 capture of `TNG-000_TongueDrum`. 1071 rows across 7 configurations:

- 833 global-variable rows (one per global × per configuration)
- 238 feature-dimension rows (one per dimension × per configuration)
- Configurations: MASTER_TEMPLATE, Large_Bilateral_16T, Medium_Bilateral_12T, Medium_Bilateral_10T, Small_Baseline_8T, Small_Baseline_6T, Large_Bilateral_14T

### What the macro is *for*

Three jobs:

1. **Verify SW matches Excel.** When you suspect drift between the SW design table and the Excel design workbook, run the macro to dump the SW state, then run `scripts/ingest_dimension_csv.py` to diff against the Excel `Master_Inputs` and `Design_Table` sheets.

2. **Capture a known-good baseline.** Before a destructive edit (rebuild graph reorganization, sketch migration), capture the macro's output. After the edit, capture again and diff. Any unintended dimension change shows up immediately.

3. **Feed the catalog DB.** The CSV is structured tabular data; `ingest_dimension_csv.py` can append per-instrument-id rows to the `cad_dimensions` table in the v4 catalog SQLite (table not yet defined; see future-work below). This is the SW side of the empirical-learning loop: when Tony measures a built drum and the prediction is off, the *as-modeled* dimension from the SW dump is the bridge between the design table and the measured value.

### Where the macro source belongs

Until we have a SW-running environment to extract and verify the VBA source, the binary `.swp` is the artifact of record. **Do not ship a hand-written `.bas` parallel** without verification — VBA is finicky enough that a syntactically-clean source could fail at runtime in subtle ways.

When Tony runs the macro on a new assembly, he should drop the resulting CSV into the build packet's `cad/dimensions/<date>-<config>.csv` and the skill picks it up from there.

---

## 4. Skill scripts for SolidWorks

### `scripts/ingest_dimension_csv.py`

Reads the macro's CSV output and validates it against the matching Excel design table. Reports:

- **Match:** dimension exists on both sides with equal values (within tolerance).
- **SW-only:** dimension in SW that doesn't appear in the Excel design table.
- **Excel-only:** dimension in Excel that's missing from the SW model.
- **Mismatch:** dimension on both sides but values disagree.

Usage:

```bash
python3 scripts/ingest_dimension_csv.py \
  --csv assets/solidworks/sample-dimensions-extract.csv \
  --workbook /path/to/Drone-Flutes-Design.xlsx \
  --design-sheet Master_Inputs \
  [--config MASTER_TEMPLATE]   # restrict to one configuration
  [--tolerance-percent 0.5]    # ±0.5% default
  [--report findings.md]       # write a structured report
  [--write-validation packet/validation.csv]   # append findings to packet
  [--dry-run]
```

The default report identifies the configuration → list of issues with the dimension name and the Excel/SW values side-by-side. Issues are categorized by severity (mismatch on a driving dimension is high; a sketch-local `_sketch` suffix mismatch is informational).

### `scripts/generate_sw_design_table.py`

Reads `family-spec.csv` from a build packet and emits a SolidWorks-compatible design-table xlsx. Usage:

```bash
python3 scripts/generate_sw_design_table.py \
  ./build-packets/2026-05-02-tng-001-tongue-drum \
  --output ./build-packets/2026-05-02-tng-001-tongue-drum/cad/sw-design-table.xlsx \
  --part-name TNG-001_TongueDrum \
  [--global-prefix dim_]   # optional: prefix family-spec column names
```

The output has:

- Row 1: `Design Table for: <part-name>` (free text — SW ignores).
- Row 2: empty cell, `$DESCRIPTION`, `$COLOR`, then `$VALUE@<global>@Equations` per family-spec column whose name matches a SW global naming convention.
- Row 3+: one row per `family-spec.csv` member. Description is the row's `notes` column; values are SW-formula form (`=<value>in` or `=<value>` for unitless).

Tony then in SolidWorks runs `Insert > Tables > Design Table > From Existing File`, picks this xlsx, and SW imports it as the embedded design table for the part. **One-time wiring.** From then on, edits in `family-spec.csv` propagate through the regenerator → SW design table → SW global → all dimensions.

### Convention: which `family-spec.csv` columns become SW globals

The generator looks at the family-spec headers and treats columns as SW-global candidates if they:

1. Normalize to a safe snake_case name. Human-readable headers such as
   `Scale Length (in)` normalize to `scale_length_in`.
2. Are not in a deny-list of bookkeeping or acoustic-target columns
   (`member_id`, `target_note`, `target_hz`, `notes`).
3. Have numeric values (or empty-but-numeric-after-cleanup).

Columns *not* promoted become free-text columns in the design table that SW ignores at rebuild time but preserves in the export. (`notes` column is a useful place to keep build-tracker context without contaminating the SW global namespace.)

### Public handoff pattern

When a packet does not contain real SolidWorks files yet, ship a handoff starter
rather than pretending CAD exists:

- `family-spec.csv` with readable public headers and one row per configuration.
- `cad/sw-design-table.xlsx` generated from that CSV when Python dependencies
  are available.
- `cad/SolidWorks-MasterLayout-Plan.md` describing the master sketch,
  named globals, configurations, and features Tony should build in SW.
- A README note that the file is a design-table handoff, not verified CAD,
  until it has been imported into SolidWorks and rebuilt.

Small `family-spec.csv` example:

```csv
member_id,target_note,target_hz,Scale Length (in),Bore ID (in),Wall Thickness (in),notes
NAF-A4,A4,440,18.25,0.875,0.125,prototype baseline
NAF-G4,G4,392,20.50,1.000,0.125,longer bore variant
```

Expected dry-run behavior:

```bash
python3 scripts/generate_sw_design_table.py ./packet --dry-run
```

The generator should promote `Scale Length (in)`, `Bore ID (in)`, and
`Wall Thickness (in)` to `$VALUE@scale_length_in@Equations`,
`$VALUE@bore_id_in@Equations`, and
`$VALUE@wall_thickness_in@Equations`. It should not promote `target_hz`;
acoustic targets are validation data, not CAD globals.

Troubleshooting import failures:

- If SW reports a bad column header, inspect row 2 and confirm every driving
  column is exactly `$VALUE@<global>@Equations`.
- If values import as text, confirm cells use formula form such as `=18.25in`
  or `=8` for unitless counts.
- If a dimension does not update, confirm the matching global exists in
  `Tools > Equations` before importing the design table.
- If rebuilds fail, reduce to one configuration, rebuild all, then re-enable
  the full design table after the master sketch is stable.

---

## 5. Quality gates for SW work

Before declaring a SW package complete:

- [ ] Every global equation in `Tools > Equations` has a matching variable in the Excel `Master_Inputs` sheet with identical name and value.
- [ ] The design-table sheet's `$VALUE@<global>@Equations` columns reference only global names that exist in `Tools > Equations`.
- [ ] Every feature dimension is driven by a global or a global-arithmetic expression. *No raw numbers.*
- [ ] The master sketch is the root of the rebuild graph; no sketch bypasses it.
- [ ] `Extract_Dimensions.swp` runs cleanly on the assembly and produces a CSV with no errors.
- [ ] `ingest_dimension_csv.py` reports zero mismatches between the SW dump and the Excel design table.
- [ ] Configurations rebuild without errors (run `Edit > Rebuild All` after activating each configuration).

If any of these fail, escalate to the human — SW debugging needs a running SW environment.

---

## 6. Future work (v4.x)

- **VBA source extraction.** Once Tony exports the `.swp` source as `Extract_Dimensions.bas`, ship it alongside the binary so the macro is open-source and editable. Until then, the binary is the artifact of record.
- **Catalog DB `cad_dimensions` table.** Add a SQLite table that stores SW dimension dumps over time, keyed by (instrument_id, configuration, dimension_name, capture_date). This becomes the SW history alongside the `production_log` build history.
- **Two-way sync.** Today edits in SW that change a global value need to be re-typed into Excel. A bidirectional script that diffs the two and proposes the merge would close that loop.
- **Multi-part assembly support.** The current macro emits one row per dimension per *configuration of the active part*. For multi-part assemblies (e.g., a flute body + drone block + bird block), the macro and ingest script need to handle component-level configurations cleanly. Sample CSV is from a single-part assembly; extend when Tony has a multi-part case.

---

## References

- `assets/solidworks/Extract_Dimensions.swp` — the macro binary
- `assets/solidworks/sample-dimensions-extract.csv` — example output (TNG-000, May 2026)
- `assets/solidworks/sample-design-table.xlsx` — example SW design table (TNG-000, 7 configurations)
- The `drone-flutes/sw-reference/Drone-Flutes-SolidWorks-MasterLayout.docx` in Tony's GitHub — Tony's authored SW master-layout reference, the human counterpart to this doc.
