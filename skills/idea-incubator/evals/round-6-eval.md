# Idea Incubator Round 6 Eval

Date: 2026-05-11
Skill version: 1.4.3 (duplicate private-media routing)

## Validation Summary

Expected validation for this change:

- `manifest.yaml` parses as YAML.
- `skills/idea-incubator/agents/openai.yaml` parses as YAML.
- `bash -n skills/idea-incubator/scripts/bootstrap-labels.sh` passes.
- `python3 -m py_compile skills/idea-incubator/scripts/bootstrap_labels.py`
  passes.
- `scripts/validate_packaged_paths.py skills/idea-incubator` passes.
- `skills/skills-meta/scripts/skills-meta.py --mode single --skill
  idea-incubator --root skills --manifest manifest.yaml` reports v1.4.3
  without missing-version or missing-last-updated drift.
- Focused content checks confirm photo-album/private-media pilot guidance
  preserves sibling source issues with `Refs #N`, avoids automatic duplicate
  closure, records duplicate handling as a Tony decision when unknown, and
  keeps public design-book or instrument-chapter issues on their own route.

## Behavioral Smoke

### Promote overlapping private photo-album captures

**Prompt**

> promote idea #101 into a private family photo album repo; #93 looks like an
> earlier capture of the same imagegen-assisted album idea, and #100/#104 are
> public design-book chapter issues

**Expected**

- Uses Promote mode and routes through
  `references/photo-album-private-media-pilot.md`.
- Surfaces `references/private-media-decision-stub.md` before any downstream
  repo scaffold, imagegen/layout study, media import, or proof/export task.
- Selects `#101` as the primary private-media promotion anchor when it is the
  clearest downstream target.
- Includes both `Refs #101` and `Refs #93` in the downstream issue.
- Does not use `Closes #93` or auto-close it unless Tony explicitly confirms
  duplicate handling.
- Treats `#93` as supporting provenance or duplicate context in the readiness
  matrix, not as a second private album repo promotion.
- Keeps `#100/#104` on the public instrument/design-book route and mentions
  them only as adjacent context.
- Preserves the existing photo-album gates: one named pilot batch, private repo
  default, LFS-first import, source/evidence ledgers, reviewer/off-limits
  gates, metadata policy, imagegen derivative labels, and proof/export signoff.

**Observed**

This is a documentation/eval addition. Future agent runs should satisfy the
expected behavior by following `references/photo-album-private-media-pilot.md`,
`references/private-media-family-archive.md`,
`references/private-media-decision-stub.md`, and
`references/promotion-handoff.md`.
