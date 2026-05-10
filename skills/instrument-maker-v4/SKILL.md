---
name: instrument-maker
version: 4.5.0
last-updated: 2026-05-17
partial-skill: true
canonical-install: ~/.claude/skills/instrument-maker
legacy-alias: instrument-maker-v4
legacy-install: ~/.claude/skills/instrument-maker-v4
description: >-
  Design, document, validate, and ship musical instruments end-to-end —
  woodwinds, strings, drums, percussion, idiophones, hybrid acoustic/electric.
  The official public skill name is instrument-maker; instrument-maker-v4 is
  retained only as a compatibility alias and historical repo folder during
  migration. This repository entry hosts the v4.4 acoustic-law/reed
  boundary-condition enhancement (issue #73), the v4.4.1 free-reed/khaen
  exploration template (issue #109), the folded stopped-pipe drone/DXF helper
  enhancement (issue #108), and the v4.4.2 sheng/hulusi/chalumeau validation
  guardrail, plus the v4.4.3 prototype validation-loop upgrade template and
  v4.4.4 repo-first bare-bones packet readiness template, the v4.4.5
  DXF/image-gen-2 visual authority guard, the v4.4.6 invocation rename and
  early visual-register trigger, the v4.4.7 instrument design-book chapter
  contract (issue #104), Round 12 hulusi/bawu stopped-pipe free-reed
  validation guidance, and the v4.5 experimental acoustic rig template
  (issue #107). The full skill body lives in the canonical install directory;
  this folder contains only the additive references, validators, tests,
  fixtures, and examples that these changes introduce.
---

# instrument-maker - partial-skill entry (v4 readiness additions)

The official public skill name and user-facing invocation is
`instrument-maker`. The `instrument-maker-v4` name is kept only as a
backward-compatible alias and as the historical repo folder name during
the staged migration. Treat `v4` as release lineage / implementation
history, not as part of the public skill name.

This folder is **not** a complete copy of the `instrument-maker` skill.
The canonical skill body (SKILL.md, agents/, full references/, full
scripts/, assets/, etc.) should live at `~/.claude/skills/instrument-maker/`
on Tony's installs. Existing installs may still expose
`~/.claude/skills/instrument-maker-v4/` or
`~/.codex/skills/instrument-maker-v4/` as a compatibility alias until the
runtime install roots are migrated.

What lives here is the **v4.4 acoustic-law / reed boundary-condition
enhancement** that closes
[issue #73](https://github.com/tonykoop/claude-skills/issues/73), the
**v4.4.1 free-reed/khaen exploration template** for
[issue #109](https://github.com/tonykoop/claude-skills/issues/109), plus
the **folded stopped-pipe drone template and DXF helper** for
[issue #108](https://github.com/tonykoop/claude-skills/issues/108), plus
the **v4.4.2 sheng/hulusi/chalumeau validation guardrail**, plus a
**v4.4.3 prototype validation-loop upgrade template** for repos that already
have instrument packets but still need empirical measurement and iteration
tracking, plus a **v4.4.4 repo-first bare-bones packet readiness template**,
plus a **v4.4.5 DXF/image-gen-2 visual authority guard**, plus the
**v4.4.6 public invocation rename and early visual-register trigger**, plus the
**v4.4.7 instrument design-book chapter contract**
([issue #104](https://github.com/tonykoop/claude-skills/issues/104)), plus
Round 12 **hulusi/bawu stopped-pipe free-reed validation guidance**, plus the
**v4.5 experimental acoustic rig template** for coupled-resonator / yaybahar-style
systems ([issue #107](https://github.com/tonykoop/claude-skills/issues/107)):

```
skills/instrument-maker-v4/
├── SKILL.md                                    ← this stub
├── CHANGELOG.md                                ← v4.4+ entries only
├── references/
│   ├── acoustic-models.md                      ← canonical + new "Reed boundary-condition decision tree" section
│   ├── drawing-and-visual-authority.md         ← DXF/CAD authority + early visual-register + image-gen-2 guard
│   ├── experimental-acoustic-rigs.md           ← bench-rig-first workflow for coupled systems
│   ├── family-aware-design.md                  ← canonical + new family-spec.csv schema (acoustic_law, end_condition, dimension_provenance)
│   ├── free-reed-khaen-exploration.md          ← P0 reed coupon / control-build template
│   ├── folded-stopped-pipe-drone.md            ← folded drone packet template
│   ├── hulusi-bawu-stopped-pipe-free-reed.md   ← stopped-pipe free-reed HUL-P0/HUL-P1 gates
│   ├── prototype-validation-loop-upgrade.md     ← upgrade path for existing prototype packets
│   ├── repo-first-bare-bones-packet.md         ← minimal public repo-first packet contract
│   └── instrument-design-book-chapter-contract.md ← public chapter readiness / asset-ledger contract
├── assets/
│   └── templates/experimental-acoustic-rig/    ← README, validation plan, risks, matrix, log, sensor/safety checklists
├── scripts/
│   ├── apply_experimental_rig_runtime_patch.py  ← idempotently patches canonical SKILL.md routing guidance
│   ├── generate_folded_drone_dxf.py            ← CSV-to-DXF folded bore helper
│   ├── validate_acoustic_law.py                ← new in v4.4; focused validator
│   └── validate_visual_authority.py            ← new in v4.4.5; DXF/image-gen-2 authority validator
├── tests/
│   ├── test_validate_acoustic_law.py           ← acoustic-law validator tests
│   ├── test_experimental_rig_templates.py      ← template/schema smoke tests
│   ├── test_generate_folded_drone_dxf.py       ← focused DXF generator tests
│   ├── test_validate_visual_authority.py       ← visual authority unit tests
│   ├── test_validation_loop_templates.py       ← validation-loop template contract tests
│   ├── test_repo_first_bare_bones_template.py  ← readiness template contract tests
│   ├── test_invocation_rename.py               ← public-name migration contract tests
│   ├── fixtures/family-spec/{pass,fail}/       ← 4 pass + 5 fail fixtures
│   └── fixtures/visual-authority/{pass,fail}/  ← DXF/image-gen-2 authority fixtures
└── examples/
    ├── repo-first-bare-bones-packet/           ← readiness:bare-bones starter packet
    │   └── string-spike-fiddle/                ← erhu/huqin bare-bones guardrail variant
    ├── folded-drone/centerline-stations.csv    ← compact folded E2 proof-mule fixture
    ├── hulusi-bawu/                            ← stopped-pipe free-reed validation scaffold
    └── khaen/
        ├── family-spec.csv                     ← combined traditional + sister + planning rows
        ├── p0-reed-coupon-log.csv             ← reed-alone pitch, pull-down, onset, blow/draw log
        ├── mouth-organ-dxf-checklist.csv       ← reed window / socket / gasket / windchest checklist
        ├── free-reed-sourcing.csv              ← source_status values for unstable reed stock
        └── prototype-validation-loop.csv        ← validation-loop upgrade CSV example
```

## Why this is a partial skill

The full instrument-maker skill is several MB of references, scripts,
agents, and assets that have not yet been reconciled with this repo's
manifest conventions. Importing the entire skill is out of scope for
issues #73, #109, and #107. The smallest high-quality version that
satisfies these issues is this additive subset, which can be merged into
the canonical install with `cp -r` and will not collide with any other
file there.

The canonical install (with the v4.4 and v4.5 changes applied) is what the
`/instrument-maker` slash command invokes. `/instrument-maker-v4` may
continue to work as a deprecated alias during migration, but new docs,
handoffs, and routing should use `instrument-maker`.

## How to apply v4.5 to a canonical install

```bash
cp -r skills/instrument-maker-v4/references/*.md \
      ~/.claude/skills/instrument-maker/references/
cp -r skills/instrument-maker-v4/assets/templates/experimental-acoustic-rig \
      ~/.claude/skills/instrument-maker/assets/templates/
cp     skills/instrument-maker-v4/scripts/apply_experimental_rig_runtime_patch.py \
      ~/.claude/skills/instrument-maker/scripts/
cp     skills/instrument-maker-v4/scripts/validate_acoustic_law.py \
      ~/.claude/skills/instrument-maker/scripts/
cp     skills/instrument-maker-v4/scripts/validate_visual_authority.py \
      ~/.claude/skills/instrument-maker/scripts/
cp     skills/instrument-maker-v4/scripts/generate_folded_drone_dxf.py \
      ~/.claude/skills/instrument-maker/scripts/
cp -r skills/instrument-maker-v4/examples/khaen \
      ~/.claude/skills/instrument-maker/examples/
cp -r skills/instrument-maker-v4/examples/folded-drone \
      ~/.claude/skills/instrument-maker/examples/
cp -r skills/instrument-maker-v4/examples/hulusi-bawu \
      ~/.claude/skills/instrument-maker/examples/
cp -r skills/instrument-maker-v4/examples/repo-first-bare-bones-packet \
      ~/.claude/skills/instrument-maker/examples/
python3 ~/.claude/skills/instrument-maker/scripts/apply_experimental_rig_runtime_patch.py \
      ~/.claude/skills/instrument-maker/SKILL.md
```

The final command updates the runtime-facing canonical `SKILL.md` with
the v4.5 bench-rig-first routing block. Copying only the reference and
template files is not sufficient for issue #107, because the invoked
slash-command behavior lives in the canonical skill body.

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

## How to validate visual-output authority

When a packet includes DXF/CAD drawings, SVG/PDF previews, or image-gen-2
prompts/outputs, create a `visual-output-register.csv` or JSON equivalent and
run:

```bash
python3 skills/instrument-maker-v4/scripts/validate_visual_authority.py \
    path/to/your/visual-output-register.csv
```

The validator fails if generated image artifacts are marked as fabrication
authority or if a build/cut visual packet has no DXF/CAD/design-table authority
record. See `references/drawing-and-visual-authority.md`.

## Trigger phrases

This stub changes the canonical public trigger to `instrument-maker`.
The canonical instrument-maker skill keeps its existing domain triggers;
the v4.4 changes are invisible to the user except as a hard validator
gate at packet generation time. Keep `instrument-maker-v4` only as a
deprecated compatibility alias while active installs and PRs migrate.

The v4.5 addition adds an internal routing rule: prompts for yaybahar-style
systems, coupled string-spring-membrane rigs, resonance test beds,
experimental acoustic apparatus, or unknown coupled resonators should
produce a **bench-rig packet before a performance-instrument packet**.

When this rule applies, read `references/experimental-acoustic-rigs.md`
and seed the packet with:

- `variable-matrix.csv`
- `measurement-log-template.csv`
- `sensor-capture-checklist.md`
- `stored-energy-safety-checklist.md`
- `README.md`
- `validation-plan.md`
- `risks.md`

For free-reed / khaen work in the canonical skill, load
`references/free-reed-khaen-exploration.md` before drafting CAD. The first
build should be a reed coupon and single-pipe control unless measured coupon
data already exists.

For hulusi, bawu, or stopped-pipe free-reed prototype repos, also load
`references/hulusi-bawu-stopped-pipe-free-reed.md`. Keep the route
readiness-gated at `L1_packet -> measurement_required`, use HUL-P0 reed coupon
and HUL-P1 single-pipe checks before boundary-condition claims, and do not
promote concept visuals or unmeasured workbook rows into build-ready DXF/CAD
authority.

If a reed/free-reed packet includes generated concept images, keep those
images out of the fabrication authority chain. Record the governing DXF, CAD,
design table, or measured template as the build authority, and mark generated
images as concept/story/visual-BOM support only.

For existing instrument prototype repos that already have packets, load
`references/prototype-validation-loop-upgrade.md` before editing the repo. Add
the validation loop without redesigning the instrument, keep CAD/DXF/design
tables as fabrication authority, and mark generated images as concept/story
support only.

For `readiness:bare-bones` or "make the first repo packet" work, load
`references/repo-first-bare-bones-packet.md` before drafting a full packet.
Use the example folder as a root-level starter and keep CAD/DXF authority as
future work unless measured geometry already exists.

For erhu/huqin or other string/spike-fiddle starters, use the
`examples/repo-first-bare-bones-packet/string-spike-fiddle/` variant and keep
qianjin-to-bridge speaking length, bridge/qianjin setup, resonator interface,
and neck/spike alignment as measurement-required until measured or reviewed.

For concept visuals, image-gen-2 prompts, visual BOM images, or build-log
imagery, load `references/drawing-and-visual-authority.md` before generating
or accepting visuals. Generated images can support communication, but DXF/CAD,
design tables, measured templates, or reviewed drawings remain fabrication
authority.

## Instrument design-book chapter scaffold

This repo entry also contains the Round 9 additive reference
`references/instrument-design-book-chapter-contract.md`. Use it when an
incubated idea promotes public design-book, yearbook, portfolio, or showcase
chapters for instrument repos. The contract requires public chapter readiness
to mirror source instrument readiness, defines the readiness banner,
asset-ledger, prompt appendix, generated-image labels, and LFS-first media
policy, and keeps `Refs #100` as the downstream source-link pattern until the
scaffold and one L2+ pilot chapter are proven.

## Tests

```bash
python3 -m unittest discover -s skills/instrument-maker-v4/tests -v
```

All instrument-maker tests should pass.

## Status

`partial-skill: true` — see frontmatter. When the canonical
instrument-maker skill is brought into this repo as a full skill, this
stub merges into the proper SKILL.md and the partial-skill flag is
removed.
