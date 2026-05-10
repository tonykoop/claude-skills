# Catalog Database — v4 (Tier 3 #8)

In v3, the Master Catalog lived only in
`Instrument Workshop Master v3.xlsx`. Reads required opening Excel and
running INDEX/MATCH; cross-instrument queries (e.g., "every cherry
tongue drum with measured tuning error >5 cents") were impossible
without a custom pivot.

In v4, the workbook is promoted to a SQLite database. The xlsx remains
the *write surface* (humans edit there); the SQLite database is the
*read API* (scripts query there). The promotion is one-way per session
— you build the db, query it, and rebuild it next session if the
workbook changed.

## Schema

The database mirrors the 14 named tables in
`Instrument Workshop Master v3.xlsx`. Table names are normalized to
lowercase snake_case; column names are normalized to lowercase
snake_case with non-alphanumeric chars dropped.

### `master_catalog` (from Table_2)

```sql
CREATE TABLE master_catalog (
  instrument_id TEXT PRIMARY KEY,
  family TEXT,
  instrument_type TEXT,
  variant_size TEXT,
  key_scale TEXT,
  design_stage TEXT,
  build_status TEXT,
  priority TEXT,
  cad_design_id TEXT,           -- FK → cad_cnc_library
  cnc_plan_id TEXT,             -- FK → cad_cnc_library
  material_id TEXT,             -- FK → materials_inventory
  primary_material TEXT,
  target_price REAL,
  estimated_cost REAL,
  estimated_margin REAL,
  maker_nexus_tool TEXT,
  next_step TEXT,
  due_date TEXT,
  notes TEXT,
  source_workbook TEXT,
  source_sheet TEXT,
  source_row INTEGER,
  legacy_link TEXT,
  github_repo TEXT
);
```

### `design_sheets` (from Table_3)

```sql
CREATE TABLE design_sheets (
  design_sheet_id TEXT PRIMARY KEY,
  family TEXT,
  instrument_type TEXT,
  design_sheet_name TEXT,
  source_workbook TEXT,
  current_structure TEXT,
  rows INTEGER,
  columns INTEGER,
  modernization_status TEXT,
  canonical_fields_needed TEXT,
  next_transformation TEXT,
  notes TEXT
);
```

### `cad_cnc_library` (from Table_5)

```sql
CREATE TABLE cad_cnc_library (
  design_id TEXT PRIMARY KEY,
  family TEXT,
  instrument_type TEXT,
  variant_size TEXT,
  key_scale TEXT,
  source_design_sheet TEXT,     -- FK → design_sheets
  cad_file_path TEXT,
  drawing_file_path TEXT,
  cam_file_path TEXT,
  cnc_toolpath_file TEXT,
  machine_process TEXT,
  work_envelope_check TEXT,
  material_thickness REAL,
  tooling_bit TEXT,
  workholding_jig TEXT,
  toolpath_status TEXT,
  cnc_readiness TEXT,
  revision TEXT,
  last_reviewed TEXT,
  next_cad_task TEXT,
  notes TEXT,
  github_repo TEXT
);
```

### `production_log` (from Table_6)

```sql
CREATE TABLE production_log (
  build_id TEXT PRIMARY KEY,
  instrument_id TEXT,           -- FK → master_catalog
  family TEXT,
  instrument_type TEXT,
  operation TEXT,
  status TEXT,
  start_date TEXT,
  finish_date TEXT,
  maker_nexus_tool TEXT,
  material_id TEXT,             -- FK → materials_inventory
  time_hours REAL,
  shop_fee_outside_cost REAL,
  materials_cost REAL,
  total_direct_cost REAL,
  qc_tuning_result TEXT,
  next_step TEXT,
  notes TEXT
);
```

### `materials_inventory`, `bom_budget`, `suppliers_resources`, `training_plan`, `contacts`, `roadmap`, `legacy_imports`

Same pattern — one column per workbook column, primary key on the table's
ID column.

### `doe_studies` (from Table_14)

```sql
CREATE TABLE doe_studies (
  study_id TEXT PRIMARY KEY,
  instrument_id TEXT,           -- FK → master_catalog
  family TEXT,
  study_name TEXT,
  phase TEXT,
  status TEXT,
  hypothesis_research_question TEXT,
  repo_path TEXT,
  protocol_path TEXT,
  data_path TEXT,
  last_updated TEXT,
  notes TEXT
);
```

### `solidworks_tables` (from Table_4)

Same shape, one row per SW Table ID.

### `sw_table_id`

(Already covered in `solidworks_tables`.)

### Indices the build script creates

```sql
CREATE INDEX idx_master_family ON master_catalog(family);
CREATE INDEX idx_master_status ON master_catalog(build_status);
CREATE INDEX idx_master_priority ON master_catalog(priority);
CREATE INDEX idx_production_instrument ON production_log(instrument_id);
CREATE INDEX idx_production_status ON production_log(status);
CREATE INDEX idx_doe_instrument ON doe_studies(instrument_id);
CREATE INDEX idx_cad_readiness ON cad_cnc_library(cnc_readiness);
```

## Build script — usage

```bash
python3 scripts/build_catalog_db.py \
  "/path/to/Instrument Workshop Master v3.xlsx" \
  --output ./catalog.sqlite \
  [--dry-run]
```

`--dry-run` prints the schema and the row counts per table without
writing the .sqlite file.

The script:
1. Opens the xlsx with openpyxl.
2. Walks each defined table in the workbook.
3. Maps the table to a SQL table; maps each column to a SQL column with
   inferred type (TEXT for strings, REAL for numerics, INTEGER for
   integers).
4. Drops empty rows and rows where the primary-key column is empty.
5. Creates indices.
6. Writes SQL `INSERT` statements in a transaction.

## Query patterns the brainstorm calls out

### "Every open-pipe instrument with measured-vs-predicted error >5 cents"

```sql
SELECT mc.instrument_id, mc.family, mc.key_scale,
       pl.qc_tuning_result, pl.notes
FROM master_catalog mc
JOIN production_log pl ON pl.instrument_id = mc.instrument_id
WHERE mc.family = 'Woodwinds'
  AND pl.qc_tuning_result LIKE '%cents%'
  AND CAST(SUBSTR(pl.qc_tuning_result, ...) AS REAL) > 5
ORDER BY ABS(...) DESC;
```

(In practice, cents-error parsing is brittle when stored as freeform
text in `qc_tuning_result`. v4 enforces a structured format —
"+3.2 cents @ A4 / -1.1 cents @ G4" — so the query above can split on
delimiters reliably. See `empirical-learning-loop.md`.)

### "Average build time for slip-cast vessel flutes"

```sql
SELECT AVG(pl.time_hours) AS avg_hours,
       COUNT(*) AS build_count
FROM production_log pl
JOIN master_catalog mc ON mc.instrument_id = pl.instrument_id
WHERE mc.family = 'Woodwinds'
  AND mc.instrument_type LIKE '%vessel%'
  AND pl.status = 'Complete';
```

### "Every cherry tongue drum whose prediction is now off by >2%"

This is the cross-instrument empirical-learning trigger. After a new
measurement updates the cherry K-constant, run:

```sql
SELECT mc.instrument_id, mc.notes,
       cad.cad_file_path
FROM master_catalog mc
JOIN cad_cnc_library cad ON cad.source_design_sheet = mc.legacy_link
WHERE mc.family = 'Drums'
  AND mc.instrument_type LIKE '%tongue%'
  AND mc.primary_material LIKE '%cherry%';
```

Then for each row, recompute the predicted fundamental with the new K
and compare to the old prediction stored in the packet's `design.md`.
If delta > 2%, flag the packet for regeneration.

### "Where do I have unspent budget?"

```sql
SELECT bb.category,
       SUM(bb.extended_cost) AS total_budgeted
FROM bom_budget bb
WHERE bb.purchased = 'No'
GROUP BY bb.category
ORDER BY total_budgeted DESC;
```

### "What DoE study has data ready to ingest?"

```sql
SELECT ds.study_id, ds.study_name, ds.data_path, mc.github_repo
FROM doe_studies ds
JOIN master_catalog mc ON mc.instrument_id = ds.instrument_id
WHERE ds.status LIKE '%data collected%'
   OR ds.status LIKE '%measurements logged%';
```

## Limitations of the v4 db

- The db is a *snapshot* — rebuild after any workbook change.
- Formula columns (e.g., `estimated_margin`) get the *value* at the
  time of the snapshot, not the formula. Re-derive in SQL if needed.
- The two-way sync (db → workbook) is not implemented in v4. Edits in
  the db must be replayed to the xlsx by the human, or the db gets
  rebuilt and edits are lost.

## Future extensions (not in v4)

- DuckDB instead of SQLite for analytical queries (group-bys over many
  rows are faster).
- A two-way sync that writes back to the xlsx without overwriting blue
  cells.
- A Datasette layer over the .sqlite for a web view of the catalog.
- Per-row revision history.
