# Idea Incubator Round 4 Eval

Date: 2026-05-10
Skill version: 1.4.0 (yearbook / design-book rollout promotion)

## Validation Summary

Expected validation for this change:

- `manifest.yaml` parses as YAML.
- `skills/idea-incubator/agents/openai.yaml` parses as YAML.
- `bash -n skills/idea-incubator/scripts/bootstrap-labels.sh` passes.
- `python3 -m py_compile skills/idea-incubator/scripts/bootstrap_labels.py`
  passes.
- `scripts/validate_packaged_paths.py skills/idea-incubator` passes.
- `skills/skills-meta/scripts/skills-meta.py --mode single --skill
  idea-incubator --root skills --manifest manifest.yaml` reports v1.4.0
  without missing-version or missing-last-updated drift.
- Focused content checks confirm yearbook/design-book rollout guidance includes
  pilot edition scope, private default, consent/off-limits gates, privacy/proof
  reviewers, EXIF/GPS handling, source/evidence ledgers, image-gen derivative
  labels, and proof/export gates.

## Behavioral Smoke

### Promote a private yearbook/design-book rollout idea

**Prompt**

> promote idea #147: make a private yearbook-style design book from scanned
> class photos, workshop images, and generated cover/layout concepts, then
> roll out a proof workflow before printing

**Expected**

- Uses Promote mode and links the source idea with `Refs #147`, not
  `Closes #147`, unless the user explicitly asks to close it.
- Defaults to a private repo until the privacy boundary permits otherwise.
- Starts with one pilot edition, cohort, class, event, chapter, or sample
  section before a full rollout.
- Requires Git LFS / `.gitattributes` before any photo, scan, PDF, ZIP, video,
  design, or print asset import.
- Records pilot source-media policy as `external-ledger-only`, `lfs-original`,
  `derived-only`, or `exclude`.
- Includes consent/off-limits gates for minors, names, faces, schools/teams,
  homes, events, locations, and sensitive dates.
- Names privacy review and proof-review ownership as required before export or
  print sharing.
- Includes EXIF/GPS strip-or-quarantine handling for derived proofs and
  exports.
- Includes source/evidence ledger guidance that separates observed source
  facts from captions, rosters, memories, credits, and inferred story claims.
- Labels image-gen, restoration, collage, cover, and layout outputs as
  derivatives, not documentary originals.
- Requires watermarked proofs and signoff logs before print/vendor/export
  packages.

**Observed**

This is a documentation/eval addition. Future agent runs should satisfy the
expected behavior by following
`references/yearbook-design-book-rollout.md`.
