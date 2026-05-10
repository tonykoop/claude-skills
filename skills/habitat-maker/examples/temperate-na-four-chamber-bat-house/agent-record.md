# Agent Record

## Provenance

- Source issue: `tonykoop/claude-skills#102`
- Source sprint: Round 9 TwinGrid Frank lane
- Manager synthesis: hybrid recommendation combining generator-backed geometry
  with shop-packet and validation structure

## Generated Vs Hand Authored

- Hand authored: `geometry_params.json`, packet prose docs, validation schema,
  validation report, and this record.
- Generated from `geometry_params.json`:
  - `four-chamber-bat-house-layout.svg`
  - `generated-cut-list.csv`

## Source Data Used

- Bat Conservation International bat-house guidance for multi-chamber houses,
  no mesh, roughened wood, no interior finish, color/thermal tuning, paired
  thermal options, and mounting cautions.
- Batweek installation guidance for building/pole mounting, tree-mount
  discouragement, height, and open drop space.
- Round 9 Frank A/B artifacts for the four-chamber parameter set, generator
  expectation, split-front vent, trapezoid side-wall recommendation, passage
  holes, mounting worksheet, and validation-report pattern.

## Validation Run

Run from repo root:

```bash
python3 -m unittest discover skills/habitat-maker/tests
```

The tests parse the JSON, run the generator, parse the generated SVG, confirm
required bat welfare gates, and verify packet file shape.

