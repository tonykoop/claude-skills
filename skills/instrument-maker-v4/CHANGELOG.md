# Changelog — instrument-maker-v4

## v4.4.0 — 2026-05-10 (issue #73)

Round 7 TwinGrid lane Irene exposed that two specialist agents
confidently picked **different governing acoustic models** for the same
free-reed instrument (khaen) — one quarter-wave (closed_open), one
half-wave (side_branch_reed). Both packets passed self-review. The
divergence was undetectable from the deliverables alone and was only
surfaced by the blind A/B overlay.

v4.4 makes the acoustic model an explicit, machine-checkable field so
this class of "silent wrong physics" error is caught at packet
generation time rather than at first-build time.

### Added

- `references/acoustic-models.md` — new top-of-file section **"Reed
  boundary-condition decision tree (READ FIRST for any free-reed
  instrument)"**. Explicit decision tree (a)–(g) covering every
  free-reed configuration and the controlled vocabulary the validator
  enforces.
- `references/family-aware-design.md` — new **"Required columns
  (v4.4+)"** subsection in the family-spec.csv schema. Three required
  columns for wind/free-reed families: `acoustic_law`, `end_condition`,
  `dimension_provenance`. Worked examples for traditional khaen,
  quarter-wave sister, and idiophone (skipped) cases.
- `scripts/validate_acoustic_law.py` — focused validator script.
  Exit code 0 (clean) / 1 (errors) / 2 (bad invocation). Supports
  `--strict` and `--json`. Cross-checks declared acoustic_law against
  computed pipe length within 1 mm or 0.5 % tolerance.
- `tests/test_validate_acoustic_law.py` — 16 unit tests covering pass
  fixtures (traditional khaen, quarter-wave sister, planning packet,
  idiophone), fail fixtures (missing column, bad vocabulary,
  incompatible end-condition, physics mismatch), formula correctness
  (cross-checked against the v2-octave-output values from the Round 7
  partner peek), controlled vocabulary, and the CLI entry point.
- `tests/fixtures/family-spec/pass/`, `tests/fixtures/family-spec/fail/`
  — 8 fixture files including the actual KHN-007 G3 = 866.9 mm half-wave
  numbers and the KHN-Q quarter-wave numbers.
- `examples/khaen/family-spec.csv` — combined family-spec.csv showing
  traditional half-wave khaen, quarter-wave sister, and a
  measurement-required planning row.

### Acceptance criteria (issue #73)

- [x] `references/acoustic-models.md` includes a boundary-condition
      decision tree.
- [x] `references/family-aware-design.md` updates `family-spec.csv`
      schema with `acoustic_law`.
- [x] Validator fails if family specs omit `acoustic_law` or use values
      outside the vocabulary.
- [x] Khaen examples distinguish traditional long-pipe side-branch reed
      behavior from compact quarter-wave experiments.
- [x] Output record identifies whether CAD dimensions are
      physics-derived, empirically seeded, or measurement-required.

### Partner ideas incorporated

From Codex B (Round 7 lane Irene, side B):

- Half-wave open-open as the default model for free-reed instruments
  with side-branch reed location (Codex's `pipe-reed-windchest-parameters.csv`
  identified this; the validator's `predicted_length_from_formula()`
  enforces it).
- The "Do not reuse Tony's NAF K2 corrections" guard becomes the
  explicit `acoustic_law` controlled vocabulary so the wrong corrections
  cannot be silently applied.

### Known limits

- Default end-correction in `validate_acoustic_law.py` is the 8.13 mm
  value derived from a 12 × 12 mm rectangular channel (the khaen
  family default). Other channel sizes use the same default; the 1 mm
  / 0.5 % tolerance is generous enough that the cross-check stays
  honest, but a future v4.5 can read channel dimensions from the row
  and compute the per-row end correction.
- The script does not yet update `validate_packet.py` (the iterating
  v4 verifier). That's a follow-up; a single additional call site is
  enough to wire it in once the canonical skill is brought into the
  repo as a full skill.

### Migration

Existing pre-v4.4 family-spec.csv files for **idiophones, strings, and
membranes** are unaffected — the validator skips them when no
wind/free-reed prefix is present.

Existing pre-v4.4 family-spec.csv files for **wind/free-reed
instruments** must add the three required columns before they validate
clean. The fix is mechanical: open the file in a CSV editor, add the
columns, fill them per the decision tree in
`references/acoustic-models.md`.
