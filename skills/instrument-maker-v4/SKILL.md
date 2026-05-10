---
name: instrument-maker-v4
version: 4.4.1
last-updated: 2026-05-10
partial-skill: true
canonical-install: ~/.claude/skills/instrument-maker-v4
description: >-
  Design, document, validate, and ship musical instruments end-to-end —
  woodwinds, strings, drums, percussion, idiophones, hybrid acoustic/electric.
  This repository entry hosts the v4.4 acoustic-law/reed boundary-condition
  enhancement (issue #73), the free-reed/khaen exploration template
  (issue #109), and the folded stopped-pipe drone/DXF helper enhancement
  (issue #108). The full skill body lives in the canonical install
  directory; this folder contains only additive references, validators,
  generators, tests, fixtures, and examples introduced by these issues.
---

# instrument-maker-v4 — partial-skill entry (v4.4 acoustic-law enhancement)

This folder is **not** a complete copy of the `instrument-maker-v4` skill.
The canonical skill body (SKILL.md, agents/, full references/, full
scripts/, assets/, etc.) lives at `~/.claude/skills/instrument-maker-v4/`
on Tony's installs and is not yet versioned in this repository.

What lives here is the **v4.4 acoustic-law / reed boundary-condition
enhancement** that closes
[issue #73](https://github.com/tonykoop/claude-skills/issues/73), the
**v4.4.1 free-reed/khaen exploration template** for
[issue #109](https://github.com/tonykoop/claude-skills/issues/109), and
the **v4.4.1 folded stopped-pipe drone template and DXF helper** that closes
[issue #108](https://github.com/tonykoop/claude-skills/issues/108):

```
skills/instrument-maker-v4/
├── SKILL.md                                    ← this stub
├── CHANGELOG.md                                ← v4.4 entry only
├── references/
│   ├── acoustic-models.md                      ← canonical + new "Reed boundary-condition decision tree" section
│   ├── family-aware-design.md                  ← canonical + new family-spec.csv schema (acoustic_law, end_condition, dimension_provenance)
│   ├── free-reed-khaen-exploration.md          ← P0 reed coupon / control-build template
│   └── folded-stopped-pipe-drone.md            ← new in v4.4.1; folded drone packet template
├── scripts/
│   ├── validate_acoustic_law.py                ← new in v4.4; focused validator
│   └── generate_folded_drone_dxf.py            ← new in v4.4.1; CSV-to-DXF folded bore helper
├── tests/
│   ├── test_validate_acoustic_law.py           ← focused acoustic-law validator tests
│   ├── test_generate_folded_drone_dxf.py       ← focused DXF generator tests
│   └── fixtures/family-spec/{pass,fail}/       ← 4 pass + 4 fail fixtures
└── examples/
    ├── khaen/
        ├── family-spec.csv                     ← combined traditional + sister + planning rows
        ├── p0-reed-coupon-log.csv             ← reed-alone pitch, pull-down, onset, blow/draw log
        ├── mouth-organ-dxf-checklist.csv       ← reed window / socket / gasket / windchest checklist
        └── free-reed-sourcing.csv              ← source_status values for unstable reed stock
    └── folded-drone/centerline-stations.csv    ← compact folded E2 proof-mule fixture
```

## Why this is a partial skill

The full instrument-maker-v4 skill is several MB of references, scripts,
agents, and assets that have not yet been reconciled with this repo's
manifest conventions. Importing the entire skill is out of scope for
issue #73. The smallest high-quality version that satisfies the issue is
this additive subset, which can be merged into the canonical install
with `cp -r` and will not collide with any other file there.

The canonical install (with the v4.4 changes applied) is what the
`/instrument-maker-v4` slash command invokes; this repo entry is for
review and version-control purposes only.

## How to apply v4.4 to a canonical install

```bash
cp -r skills/instrument-maker-v4/references/*.md \
      ~/.claude/skills/instrument-maker-v4/references/
cp     skills/instrument-maker-v4/scripts/validate_acoustic_law.py \
      ~/.claude/skills/instrument-maker-v4/scripts/
cp -r skills/instrument-maker-v4/examples/khaen \
      ~/.claude/skills/instrument-maker-v4/examples/
cp -r skills/instrument-maker-v4/examples/folded-drone \
      ~/.claude/skills/instrument-maker-v4/examples/
cp     skills/instrument-maker-v4/scripts/generate_folded_drone_dxf.py \
      ~/.claude/skills/instrument-maker-v4/scripts/
```

## How to validate a packet's family-spec.csv

```bash
python3 skills/instrument-maker-v4/scripts/validate_acoustic_law.py \
    path/to/your/family-spec.csv
```

Exit codes: `0` (clean), `1` (validation error), `2` (bad invocation).

Add `--strict` to also fail on warnings and `--json` to emit a
machine-readable findings document.

## How to generate a folded stopped-pipe drone DXF starter

```bash
python3 skills/instrument-maker-v4/scripts/generate_folded_drone_dxf.py \
    skills/instrument-maker-v4/examples/folded-drone/centerline-stations.csv \
    --output /tmp/folded-drone-layout.dxf \
    --duct-height-mm 42 \
    --tuning-tail-mm 180
```

The helper reads centerline stations plus a width schedule and emits a
DXF-first folded-bore layout with duct walls, bend zones, tuning-tail
allowance, leak-test notes, breath-contact safety notes, and a straight
reference tube comparison. It is a layout generator, not CAM.

## Trigger phrases

This stub does **not** add new trigger phrases. The canonical
instrument-maker-v4 skill keeps its existing triggers; the v4.4 changes
are invisible to the user except as a hard validator gate at packet
generation time.

For free-reed / khaen work in the canonical skill, load
`references/free-reed-khaen-exploration.md` before drafting CAD. The first
build should be a reed coupon and single-pipe control unless measured coupon
data already exists.

## Tests

```bash
python3 -m unittest discover -s skills/instrument-maker-v4/tests -v
```

All tests should pass.

## Status

`partial-skill: true` — see frontmatter. When the canonical
instrument-maker-v4 skill is brought into this repo as a full skill, this
stub merges into the proper SKILL.md and the partial-skill flag is
removed.
