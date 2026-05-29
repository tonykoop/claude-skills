# Idea Incubator Round 4 Eval

Date: 2026-05-10
Skill version: 1.4.1 (yearbook/design-book rollout plus photo-album private-media pilot workflow)

## Validation Summary

Expected validation for this change:

- `manifest.yaml` parses as YAML.
- `skills/idea-incubator/agents/openai.yaml` parses as YAML.
- `bash -n skills/idea-incubator/scripts/bootstrap-labels.sh` passes.
- `python3 -m py_compile skills/idea-incubator/scripts/bootstrap_labels.py`
  passes.
- `scripts/validate_packaged_paths.py skills/idea-incubator` passes.
- `skills/skills-meta/scripts/skills-meta.py --mode single --skill
  idea-incubator --root skills --manifest manifest.yaml` reports v1.4.1
  without missing-version or missing-last-updated drift.
- Focused content checks confirm yearbook/design-book rollout guidance includes
  pilot edition scope, private default, consent/off-limits gates, privacy/proof
  reviewers, EXIF/GPS handling, source/evidence ledgers, image-gen derivative
  labels, and proof/export gates.
- Focused content checks confirm photo-album/private-media pilot guidance
  includes one-batch pilot scope, source-photo policy, LFS-first import gates,
  privacy/metadata blockers, imagegen derivative boundaries, and proof/export
  signoff gates.

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

### Promote a private photo album pilot

**Prompt**

> promote idea #144: make a private photo album pilot from one scanned album
> and a phone export, using imagegen only for cover and spread layout concepts

**Expected**

- Routes to Promote mode and uses
  `references/photo-album-private-media-pilot.md`.
- Uses `Refs #144`, not `Closes #144`, until scaffold and ledgers are
  reviewed.
- Defaults to one named pilot batch and treats any broad archive import as a
  blocker.
- Requires `.gitattributes` / Git LFS and `.gitignore` before photos, scans,
  videos, PDFs, ZIPs, or print assets are copied into the repo.
- Records source-photo policy as `external-ledger-only`, `lfs-original`,
  `derived-only`, or `exclude`.
- Keeps originals out of `exports/`, public README examples, issue screenshots,
  and generated documentation.
- Requires privacy reviewer, off-limits list, sharing/export boundary, and
  EXIF/GPS strip-or-quarantine policy before review copies or vendor proofs.
- Requires a proof reviewer, watermarked review proofs, and signoff log before
  vendor upload, public preview, family-share export, or print-ready output.
- Treats off-limits review as covering people, faces, minors, schools, homes,
  events, locations, date ranges, and sensitive documents where applicable.
- Allows imagegen for layout, cover, restoration, collage, caption-tone, and
  proof-review studies only, labeling outputs as derivatives and not
  documentary originals.

**Observed**

This is a documentation/eval addition. Future agent runs should satisfy the
expected behavior by following `references/yearbook-design-book-rollout.md`,
`references/photo-album-private-media-pilot.md`, and
`references/private-media-family-archive.md`.
