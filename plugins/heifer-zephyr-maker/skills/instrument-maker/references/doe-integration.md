# DoE Integration — v4

The `Instrument Workshop Master v3.xlsx → DoE Studies` sheet
(`Table_14`) is new since v3 was written. v4 wires it into the skill
explicitly: when the user mentions a Design-of-Experiments protocol,
study results, or statistical analysis of build outcomes, the skill
follows this sheet's foreign keys to the per-instrument GitHub repo
where the protocol and raw data live.

## The DoE Studies sheet

Schema (12 columns):

```
Study ID, Instrument ID, Family, Study Name, Phase, Status,
Hypothesis / Research Question, Repo Path, Protocol Path,
Data Path, Last Updated, Notes
```

Each row points to:

- `Repo Path` — top-level GitHub repo for the instrument
  (e.g., `https://github.com/tonykoop/tongue-drum`).
- `Protocol Path` — markdown file describing the DoE protocol
  (e.g., `https://github.com/tonykoop/tongue-drum/blob/main/study/README.md`).
- `Data Path` — folder where raw measurement CSVs live
  (e.g., `tongue-drum/study/data/`).

## How the skill reads this

When the orchestrator dispatches you to do DoE-related work:

1. Read the sheet (or query the catalog db's `doe_studies` table).
2. Identify the relevant study by `Study ID` or
   `Instrument ID + Phase`.
3. Follow `Protocol Path` — read the protocol markdown to understand
   what's being measured, what the conditions are, what the
   statistical design is (full-factorial, fractional, response-surface,
   etc.).
4. Follow `Data Path` — list CSVs, identify the schema (typically
   `data-template.csv` lives alongside).
5. For ingestion, treat each CSV row as an individual measurement and
   feed it through `record_measurement.py` (or batch-ingest via
   `record_measurement.py --csv path/to/data.csv`).

## DoE vs single measurement

A single measurement (one tuner reading on one finished instrument) is
the fast path documented in `empirical-learning-loop.md`. A DoE study
is the slow path:

- **Single measurement:** "I built a cherry tongue drum, the A4 tongue
  reads 442.3 Hz." → `record_measurement.py`.
- **DoE study:** "I built three small tongue drums in cherry / maple /
  walnut, struck each tongue 162 times to characterize the noise floor,
  and recorded the mean and stddev of the fundamental for each
  species." → DoE protocol, multi-CSV data folder, statistical
  analysis.

DoE studies are the tongue-drum-style three-build investigations. They
yield not single corrections but *characterized* corrections with
confidence intervals.

## DoE → empirical-learning loop

Once a DoE study completes:

1. Compute per-condition mean fundamental and stddev.
2. For each (species, geometry) combination, derive a corrected
   K-constant or empirical correction with a confidence interval.
3. Update `corrections.sqlite` with the new value *and the
   confidence interval*. The acoustician specialist reads CI when
   computing predictions for new instruments — wider CI → wider
   tolerance band in `validation.csv`.

The corrections schema needs an extension for this:

```sql
CREATE TABLE corrections_summary (
  family TEXT,
  parameter TEXT,           -- 'k_constant', 'k2', 'end_correction', etc.
  parameter_band TEXT,      -- e.g., 'cherry / 0.875" bore'
  current_value REAL,
  ci_low REAL,
  ci_high REAL,
  source_study_id TEXT,     -- DoE source if from a study
  n_measurements INTEGER,
  last_updated TEXT,
  PRIMARY KEY (family, parameter, parameter_band)
);
```

## Standard protocol references

DoE protocols Tony's catalog references:

- `tongue-drum/study/README.md` — phase 1: small-drum noise floor +
  species sweep. ~486 strikes for noise floor, 2-4 species variants.
- (Future) `gemshorn/study/` — slip-cast vessel-flute mold-shrinkage
  characterization.
- (Future) `udu/study/` — dual-port Helmholtz coupling factor.

When designing a new DoE for a family that doesn't have one yet, the
skill can scaffold a `study/` folder following the tongue-drum
template:

```
study/
├── README.md              (protocol)
├── data-template.csv      (column schema for raw data)
├── data/                  (raw CSVs, one per session)
└── analysis/
    ├── notebook.ipynb     (or .nb / .R)
    └── summary.md         (results + corrections updates)
```

Ask Tony before scaffolding — DoE protocols are time-intensive to
execute, and the skill should not spawn one casually.

## Quality gates for DoE work

- [ ] The DoE Studies row exists and has `Status` set appropriately
      (Documentation only, Data collection in progress, Data complete,
      Analysis complete).
- [ ] `Protocol Path` and `Data Path` resolve (real paths, real files).
- [ ] `data-template.csv` exists and the data CSVs match the template
      schema exactly (no silent column drift).
- [ ] If results are ingested into `corrections.sqlite`, the source
      `Study ID` is recorded — don't anonymize the source.
- [ ] If results are inconclusive (CI too wide to update predictions
      meaningfully), say so explicitly — don't update the corrections
      with low-confidence values.
