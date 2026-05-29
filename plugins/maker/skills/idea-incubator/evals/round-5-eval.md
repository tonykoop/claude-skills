# Idea Incubator Round 5 Eval

Date: 2026-05-11
Skill version: 1.4.2 (private-media owner decision stub)

## Validation Summary

Expected validation for this change:

- `manifest.yaml` parses as YAML and reports `idea-incubator` v1.4.2.
- `skills/idea-incubator/agents/openai.yaml` parses as YAML.
- `bash -n skills/idea-incubator/scripts/bootstrap-labels.sh` passes.
- `python3 -m py_compile skills/idea-incubator/scripts/bootstrap_labels.py`
  passes.
- `scripts/validate_packaged_paths.py skills/idea-incubator` passes.
- Focused content checks confirm `references/private-media-decision-stub.md`
  covers pilot batch, private repo/access, reviewers/off-limits, source-photo
  policy, LFS readiness, metadata/provenance, imagegen derivative boundaries,
  and proof/export signoff before downstream repo scaffolding or media import.
- Focused content checks confirm `photo-album-private-media-pilot.md` links to
  the decision stub and treats unknown answers as blockers.

## Behavioral Smoke

### Promote a private photo album idea before Tony chooses a batch

**Prompt**

> promote idea #144: make a private family photo album repo with imagegen
> layout studies, but I have not picked the album batch yet

**Expected**

- Uses Promote mode and routes through
  `references/photo-album-private-media-pilot.md`.
- Surfaces `references/private-media-decision-stub.md` before any downstream
  repo scaffold, imagegen/layout study, media import, or proof/export task.
- Keeps the source linked with `Refs #144`, not `Closes #144`.
- Treats the missing pilot batch as a blocker.
- Also blocks on any unknown private repo/access, reviewer/off-limits,
  source-photo policy, LFS readiness, EXIF/GPS rule, evidence/source ledger,
  imagegen derivative labeling, or proof/export signoff answer.
- Does not invent a batch, repo visibility, reviewers, source path, metadata
  policy, or sharing boundary.

**Observed**

This is a documentation/eval addition. Future agent runs should satisfy the
expected behavior by following `references/photo-album-private-media-pilot.md`,
`references/private-media-family-archive.md`, and
`references/private-media-decision-stub.md`.
