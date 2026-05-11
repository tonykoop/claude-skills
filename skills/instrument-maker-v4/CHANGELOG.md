# Changelog — instrument-maker-v4

## v4.4.5 — 2026-05-11

Round 10 TwinGrid lane Elsa-B focused on visual authority: generated images
are useful for concept/story/visual BOM work, but DXF/CAD/design tables remain
the source of fabrication truth.

### Added

- `references/drawing-and-visual-authority.md` — visual-output authority
  guidance that defines DXF/CAD/design-table authority, derived previews, and
  image-gen-2 concept-only boundaries.
- `scripts/validate_visual_authority.py` — focused CSV/JSON validator for
  `visual-output-register` records. It fails when image-gen-2 prompts/outputs
  are marked as fabrication authority, use cut-ready roles, infer dimensions,
  or when derived previews omit their source authority.
- `tests/test_validate_visual_authority.py` and
  `tests/fixtures/visual-authority/` — pass/fail fixtures covering DXF
  authority with image-gen-2 concepts, JSON registers, generated-image
  authority misuse, missing DXF/CAD authority, and missing derived-source
  links.
- Post-Peek note in the visual authority reference tying reed/free-reed
  concept visuals back to `validate_acoustic_law.py`, measured coupon data,
  and the governing DXF/CAD/design table.

### Acceptance criteria

- [x] Docs explicitly state that generated images may support concept/story
      work but never replace CAD/DXF authority for fabrication.
- [x] Validator rejects image-gen-2 artifacts recorded as cut-ready,
      dimension-inferred, or fabrication-authoritative.
- [x] Validator requires a fabrication-authority DXF/CAD/drawing/design-table
      row when a visual register includes build/cut or derived-preview work.
- [x] Existing acoustic-law tests continue to pass alongside the new visual
      authority tests.

## v4.4.4 — 2026-05-11 (readiness:bare-bones)

Round 10 TwinGrid lane Dan-A adds a repo-first bare-bones packet template for
instrument ideas that need a public GitHub starting point before a full
build packet, CAD/DXF package, or measured acoustic authority exists.

### Added

- `references/repo-first-bare-bones-packet.md` — routing and acceptance
  contract for minimal standalone instrument repos. It defines when to use
  the template, the required first files, and the claims a bare-bones packet
  must avoid.
- `examples/repo-first-bare-bones-packet/` — root-level starter files for a
  first packet: README, design stub, BOM, sourcing, cut list, validation,
  risks, drawing brief, and photo shotlist.
- `tests/test_repo_first_bare_bones_template.py` — contract tests for the
  required reference language, example file set, CSV columns, and skill stub
  pointers.

### Acceptance criteria (readiness:bare-bones)

- [x] Template/example exists in the canonical skill tree subset.
- [x] Docs make the packet repo-first rather than `build-packets/...` nested.
- [x] Bare-bones status is explicit; CAD/DXF remains future fabrication
      authority unless measured geometry already exists.
- [x] Private family/media details are excluded by default.
- [x] Generated imagery is limited to concept/story support and cannot
      replace CAD/DXF authority.
- [x] Validation rows include `next_action` and `evidence` so first-pass
      unknowns are actionable.

## v4.4.3 — 2026-05-11

Round 10 TwinGrid lane Dan-B added a small upgrade path for prototype repos
that already have instrument packets but lack an empirical validation loop.

### Added

- `references/prototype-validation-loop-upgrade.md` — template for inventorying
  existing packet artifacts, assigning L0-L4 readiness, adding
  `validation-loop.csv`, recording measurements, and closing the next
  iteration decision without redesigning the instrument.
- `examples/khaen/prototype-validation-loop.csv` — concrete reusable CSV
  example for connecting `family-spec.csv`, reed coupon measurements, DXF
  checklist rows, and playable-prototype tuner results.
- `tests/test_validation_loop_templates.py` — contract test that checks the
  new template files and required safety/readiness language.

### Acceptance criteria

- [x] Existing packet repos get a template path instead of a full redesign.
- [x] Readiness labels and next-action statuses are explicit.
- [x] Measurements and iteration decisions are captured as structured CSV.
- [x] CAD/DXF/design tables remain fabrication authority.
- [x] Generated images are limited to concept/story support.

## v4.4.2 — 2026-05-11 (Round 10 TwinGrid)

Round 10 tightened the reed/free-reed validation route for sheng, hulusi,
and chalumeau-style prompts so agents do not treat visually plausible reed
layouts as fabrication-authoritative until the acoustic law, end condition,
and measurement status agree.

### Added

- Chalumeau-style `CHL` family IDs are now treated as wind/reed families by
  `scripts/validate_acoustic_law.py`, so missing v4.4 acoustic-law columns
  fail instead of being skipped.
- Reed-family guidance now explicitly separates traditional sheng/hulusi
  side-branch free-reed layouts, donor-reed measurement-required planning
  packets, and chalumeau-style beating-reed/stopped-end layouts.
- Unit fixtures cover a valid chalumeau-style control row and a missing-column
  chalumeau row.
- Partner Peek v2 adds a visual-authority checkpoint for reed/free-reed
  packets that use generated concept images.

## v4.4.1 — 2026-05-10 (issue #109)

Round 9 TwinGrid lane Alice recommended making free-reed/khaen work an
exploration template instead of a full-instrument jump. The safe path is a
reed coupon, then a single-pipe control, then a small windchest or family
packet after measurements exist.

### Added

- `references/free-reed-khaen-exploration.md` — first-class template for
  khaen/khen, sheng, sho, and related free-reed mouth-organ experiments.
  It defines `control-build` versus `family-true` branches and states that
  the first build should start with a P0 reed coupon, not full CAD.
- `examples/khaen/p0-reed-coupon-log.csv` — worksheet fields for
  reed-alone pitch, pull-down cents, onset pressure, blow/draw behavior,
  reed gap, source/provenance, and next action.
- `examples/khaen/mouth-organ-dxf-checklist.csv` — DXF checklist for reed
  window, socket pitch map, gasket layer, windchest section, service access,
  and explicit side-branch/stopped-end notes.
- `examples/khaen/free-reed-sourcing.csv` — sourcing template with
  `source_status` values so transient live stock and supplier claims are
  not treated as stable design data.

### Acceptance criteria (issue #109)

- [x] Template/example exists in the canonical skill tree subset.
- [x] Docs explicitly say the first build should start with a reed coupon,
      not full CAD.
- [x] The existing `validate_acoustic_law.py` path is surfaced for
      `side_branch_reed`, `closed_open`, and
      `unknown_requires_measurement` exploration packets.
- [x] Mouth-organ DXF checklist covers reed window, socket pitch map,
      gasket layer, windchest section, and side-branch/stopped-end notes.
- [x] Ceramic shell versus removable acoustic-core guidance is documented.
- [x] Sourcing `source_status` values are documented for free-reed parts.

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
