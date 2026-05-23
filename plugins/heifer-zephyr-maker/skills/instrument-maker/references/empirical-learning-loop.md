# Empirical Learning Loop — v4 (Tier 1 #4 + Tier 3 #10)

The 17-years-of-built-instruments asset is only valuable if v4 makes it
*compounding*. Every measured fundamental should:

1. Update the packet's `validation.csv` with cents error vs predicted.
2. Append to a per-family corrections database that future packets in
   the same family read automatically.
3. Flag any sibling packets in the same family whose predictions just
   shifted by more than 2 cents — those packets get a regeneration
   prompt.

This is the closest v4 gets to the brainstorm's Tier 3 #10 vision:
"Tongue drum K-constant for cherry got revised? Every cherry tongue
drum in the catalog gets a flag: 'your prediction is now off by 2.3%,
want to regenerate?'"

## The data flow

```
       [tuner reading]
              │
              ▼
   record_measurement.py
              │
              ├──► packet/validation.csv  (cents error vs predicted)
              │
              ├──► production_log table   (qc_tuning_result update)
              │
              ├──► corrections.sqlite     (per-family corrections row)
              │
              └──► sibling_packets[]      (flagged for regeneration)
```

## record_measurement.py — usage

```bash
python3 scripts/record_measurement.py \
  --packet ./build-packets/2026-05-02-tng-001-tongue-drum \
  --note-id A4 \
  --measured-hz 442.3 \
  --tuner "Korg OT-120" \
  --environment "shop, 68F, 45% RH" \
  [--corrections-db ./corrections.sqlite] \
  [--dry-run]
```

`--note-id` matches a row in the packet's `validation.csv` (the
note-id column in the validation schedule the acoustician emitted).
`--corrections-db` defaults to `<skill-folder>/corrections.sqlite`.

The script:

1. Opens `validation.csv`, finds the row matching `--note-id`.
2. Reads the `predicted_hz` column for that row.
3. Computes `cents_error = 1200 · log2(measured_hz / predicted_hz)`.
4. Writes `measured_hz`, `cents_error`, `tuner`, `environment`,
   `measurement_date` to the row.
5. Reads the packet's `design.md` to extract the governing model and
   the empirical correction values used (K, K2, end correction).
6. Appends a row to `corrections.sqlite` table `measurements`:

   ```sql
   CREATE TABLE measurements (
     measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
     instrument_id TEXT,           -- packet's instrument ID
     family TEXT,
     note_id TEXT,
     predicted_hz REAL,
     measured_hz REAL,
     cents_error REAL,
     governing_model TEXT,
     k_constant REAL,
     k2_correction REAL,
     end_correction REAL,
     wood_species TEXT,
     bore_diameter REAL,
     tuner TEXT,
     environment TEXT,
     measurement_date TEXT,
     packet_path TEXT
   );
   ```

7. Recomputes the family's empirical-correction proposed value (e.g.,
   for cherry tongue drums, the new K_cherry as a Bayesian update over
   prior measurements).
8. If the proposed value differs from the current default by more than
   2%, scans the catalog db for sibling instruments in the same family
   and material, recomputes their predicted fundamental with the new
   correction, and writes flagged packets to
   `corrections.sqlite` table `pending_regenerations`:

   ```sql
   CREATE TABLE pending_regenerations (
     instrument_id TEXT,
     packet_path TEXT,
     old_prediction_hz REAL,
     new_prediction_hz REAL,
     cents_delta REAL,
     reason TEXT,
     flagged_at TEXT
   );
   ```

9. Reports a summary to stdout.

## How predictions get updated

The default empirical corrections live in
`references/acoustic-models.md` (the K-constant table, the K2 NAF
table). The corrections database is the *override* — when present, it
takes precedence.

The acoustician specialist's loading priority (per
`agents/specialists/acoustician.md` step 3) is:

1. Per-family corrections from `corrections.sqlite` (most recent
   Bayesian-updated value).
2. Defaults from `acoustic-models.md`.

For a family with N>=3 measurements, use the median measured K (or K2,
or end correction); for N<3, blend with the prior (default value)
weighted toward the prior. This keeps single bad measurements from
swinging the family default.

## Bayesian update formulation (informal)

For a single empirical correction value (e.g., K_cherry):

```
prior:        K_default (from acoustic-models.md)
observations: K_meas[1], K_meas[2], ..., K_meas[N] (back-derived from
              measured fundamentals via the formula)
posterior:    K_posterior = (w_prior · K_default + Σ K_meas[i]) / (w_prior + N)
```

where `w_prior = 3` for soft Bayesian smoothing — three "virtual"
measurements at the prior mean. This means the prior dominates until
real measurements outnumber it, then real data takes over.

## When to NOT update

- The cents error is large (>50 cents) — likely a tuning bug, a wrong
  note-ID match, or an instrument played at the wrong octave. Flag
  it; don't let it pollute the corrections database. Require
  human confirmation before ingesting.
- The instrument is at the edge of the family's acoustic range —
  a 1.25" bore NAF measurement shouldn't update the K2 default for
  a 0.625" bore instrument; the K2 correction is bore-dependent. The
  per-family corrections are *banded* by the parameter that drives
  them (bore for K2; species for K; bore-to-chamber ratio for vessel
  end corrections).
- The tuner / environment isn't recorded — the empirical correction
  baseline assumes shop conditions (~68F, ~45% RH). Off-spec
  measurements get logged but flagged with a `confidence_low` tag.

## Schema for `validation.csv` (v4 enforcement)

The acoustician's `validation.csv` template (carried forward from v3,
extended for v4):

```csv
note_id,target_hz,predicted_hz,tolerance_cents,measured_hz,cents_error,tuner,environment,measurement_date,result,action
A4,440.0,438.7,±5,,,,,
G4,392.0,391.2,±5,,,,,
F4,349.2,348.5,±5,,,,,
```

`result` values: empty (not measured), "pass" (within tolerance),
"flat" (cents_error < -tolerance), "sharp" (cents_error >
+tolerance), "way off" (|cents_error| > 50).

`action` is free-text describing the response (e.g., "shorten end
plug 1mm", "open tone hole 2 by 0.4mm").

## Quality gates for the loop

- [ ] Every measurement has tuner + environment + date logged.
- [ ] Cents error is computed and stored as a number, not free-text.
- [ ] If |cents error| > 50 for any note, the script blocks and
      requires human confirmation before updating the corrections db.
- [ ] If a correction value moves by >5% in one update, the script
      blocks and requires human confirmation — that's a flag for
      either a model error or a measurement error.
- [ ] `pending_regenerations` is reported to the user after each
      ingestion; not silently held for later.

## What the loop does not do (yet)

- It does not auto-regenerate flagged packets. The user is in control
  of when to regenerate (a regeneration is a destructive change to
  files in a working repo).
- It does not handle multi-fundamental instruments (a tubular bell with
  measured first AND second mode) — only the fundamental is tracked.
  v4.x will extend.
- It does not handle DoE-scale data ingestion (hundreds of strikes per
  drum). For DoE work, use `references/doe-integration.md` and the
  per-instrument-repo `study/` folder; only the per-build summary
  fundamental gets recorded here.
