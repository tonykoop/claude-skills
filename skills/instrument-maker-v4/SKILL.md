---
name: instrument-maker-v4
version: 4.4.0
last-updated: 2026-05-10
partial-skill: true
canonical-install: ~/.claude/skills/instrument-maker-v4
description: >-
  Design, document, validate, and ship musical instruments end-to-end —
  woodwinds, strings, drums, percussion, idiophones, hybrid acoustic/electric.
  This repository entry hosts the v4.4 acoustic-law/reed boundary-condition
  enhancement (issue #73). The full skill body lives in the canonical install
  directory; this folder contains only the additive references, validator,
  tests, fixtures, and examples that v4.4 introduces.
---

# instrument-maker-v4 — partial-skill entry (v4.4 acoustic-law enhancement)

This folder is **not** a complete copy of the `instrument-maker-v4` skill.
The canonical skill body (SKILL.md, agents/, full references/, full
scripts/, assets/, etc.) lives at `~/.claude/skills/instrument-maker-v4/`
on Tony's installs and is not yet versioned in this repository.

What lives here is the **v4.4 acoustic-law / reed boundary-condition
enhancement** that closes
[issue #73](https://github.com/tonykoop/claude-skills/issues/73):

```
skills/instrument-maker-v4/
├── SKILL.md                                    ← this stub
├── CHANGELOG.md                                ← v4.4 entry only
├── references/
│   ├── acoustic-models.md                      ← canonical + new "Reed boundary-condition decision tree" section
│   └── family-aware-design.md                  ← canonical + new family-spec.csv schema (acoustic_law, end_condition, dimension_provenance)
├── scripts/
│   └── validate_acoustic_law.py                ← new in v4.4; focused validator
├── tests/
│   ├── test_validate_acoustic_law.py           ← 16 unit tests
│   └── fixtures/family-spec/{pass,fail}/       ← 4 pass + 4 fail fixtures
└── examples/
    └── khaen/family-spec.csv                   ← combined traditional + sister + planning rows
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
```

## How to validate a packet's family-spec.csv

```bash
python3 skills/instrument-maker-v4/scripts/validate_acoustic_law.py \
    path/to/your/family-spec.csv
```

Exit codes: `0` (clean), `1` (validation error), `2` (bad invocation).

Add `--strict` to also fail on warnings and `--json` to emit a
machine-readable findings document.

## Trigger phrases

This stub does **not** add new trigger phrases. The canonical
instrument-maker-v4 skill keeps its existing triggers; the v4.4 changes
are invisible to the user except as a hard validator gate at packet
generation time.

## Tests

```bash
python3 -m unittest discover -s skills/instrument-maker-v4/tests -v
```

All 16 tests should pass.

## Status

`partial-skill: true` — see frontmatter. When the canonical
instrument-maker-v4 skill is brought into this repo as a full skill, this
stub merges into the proper SKILL.md and the partial-skill flag is
removed.
