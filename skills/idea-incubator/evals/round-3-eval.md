# Idea Incubator Round 3 Eval

Date: 2026-05-10
Skill version: 1.3.0 (private media / family archive promotion)

## Validation Summary

Expected validation for this change:

- `manifest.yaml` parses as YAML.
- `skills/idea-incubator/agents/openai.yaml` parses as YAML.
- `bash -n skills/idea-incubator/scripts/bootstrap-labels.sh` passes.
- `python3 -m py_compile skills/idea-incubator/scripts/bootstrap_labels.py`
  passes.
- Focused content checks confirm private-media promotion guidance includes
  LFS, privacy boundary, reviewer/consent, EXIF/GPS handling, source/evidence
  ledgers, one curated pilot batch, and repo scaffold hints.

## Behavioral Smoke

### Promote a family photo archive idea

**Prompt**

> promote idea #101: make a private family photo album repo from scanned
> albums and phone videos, with image-gen help for layouts and restoration
> studies

**Expected**

- Uses Promote mode and links the source idea with `Refs #101`, not
  `Closes #101`, unless the user explicitly asks to close it.
- Defaults to a private repo.
- Starts with one curated pilot batch, not a full archive import.
- Requires Git LFS / `.gitattributes` before any photo, scan, PDF, ZIP, or
  video import.
- Includes privacy boundary, family/privacy reviewer, consent/off-limits
  questions, and EXIF/GPS strip-or-quarantine handling.
- Includes source/evidence ledger guidance that separates observed file facts
  from captions, memories, and inferred story claims.
- Suggests repo scaffold paths such as `spreads/`, `print-proof/`,
  `source-ledger/`, `docs/privacy-boundary.md`, `docs/editorial-style.md`,
  `derived/`, and `exports/`.
- Labels image-gen and restoration outputs as derivatives, not documentary
  originals.

**Observed**

This is a documentation/eval addition. Future agent runs should satisfy the
expected behavior by following `references/private-media-family-archive.md`.
