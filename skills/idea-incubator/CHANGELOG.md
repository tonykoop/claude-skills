# Changelog

## 1.4.0 - 2026-05-10

- Added yearbook/design-book rollout promotion guidance for yearbooks, cohort
  books, school archives, class/team books, workshop books, and private
  print-on-demand books with identifiable people or private media.
- New reference: `references/yearbook-design-book-rollout.md` with pilot
  edition defaults, consent/off-limits gates, privacy/proof reviewers,
  source/evidence ledger templates, EXIF/GPS handling, proof/export gates,
  explicit source-media policy values, and image-gen derivative boundaries.
- `promotion-handoff.md` and `private-media-family-archive.md` now route
  yearbook/design-book captures through the rollout checklist before drafting
  downstream issues.
- `SKILL.md` frontmatter now uses top-level `version` and `last-updated` keys
  so `skills-meta` can compare the skill against `manifest.yaml`.
- Added round-4 eval expectations for promoting a private yearbook/design-book
  rollout idea.

## 1.3.0 - 2026-05-10

- Added private media / family archive promotion guidance for photo albums,
  scanned documents, personal video, and image-gen-assisted private album work.
- New reference: `references/private-media-family-archive.md` with private-repo
  default, one curated pilot batch, privacy boundary, reviewer/consent checks,
  EXIF/GPS strip-or-quarantine policy, source/evidence ledger templates, repo
  scaffold hints, and media LFS defaults.
- `promotion-handoff.md` now routes private media captures through the
  privacy-first checklist before drafting downstream issues.
- Added round-3 eval expectations for promoting a family photo archive idea.

## 1.2.0 - 2026-05-10

- Added Promote-batch (mode 6) for cluster-aware promotion of recovery /
  archive / intake-dump captures. Defines burst, shared-root, shared-template,
  and shared-blocker heuristics for cluster detection (Refs #67).
- Promotion-readiness matrix is now a required output of both Promote and
  Promote-batch. Template added to `references/promotion-handoff.md`.
- Added binary-asset / Git LFS prompts and an LFS-first scaffold sequence
  to `references/promotion-handoff.md`. Default extension list covers
  SolidWorks/CAD; runbooks for audio/video/PDF clusters add their own.
- Added evidence-ledger template (observed vs inferred columns) for
  recovery/import promotions. Source archive facts and inferred public
  claims are now structurally separated.
- Refs vs Closes guidance: recovery/import promotions default to `Refs #N`
  so source captures remain open as provenance anchors.
- New worked example: `references/promote-batch-example.md` documents the
  Weather Balloon Camera Vessel cluster pattern from Round 7 TwinGrid.
- New trigger phrases: `promote the cluster`, `batch promote`,
  `review the cluster` (added to `SKILL.md` and `agents/openai.yaml`).

## 1.1.0 - 2026-05-08

- Cross-platform compatibility pass for Claude Code, Claude Desktop, Codex,
  Codex Desktop, Gemini CLI, and mobile zip-upload.
- Added `scripts/bootstrap_labels.py` Python companion to the bash bootstrap
  script for hosts where bash is awkward (native Windows, sandboxed Codex).
- Documented a copy-pasteable `gh label create` fallback in `label-schema.md`
  for mobile and `gh`-less environments.
- Normalized trigger phrases (dropped trailing `?`) in SKILL.md and
  `agents/openai.yaml` so substring-matching agents route reliably.
- Added a Platform notes section explaining per-host behavior.

## 1.0.0 - 2026-05-08

- Initial `idea-incubator` skill.
- Added capture, intake, connect, review, and promote modes.
- Added label schema, issue template, promotion handoff reference, and
  optional GitHub label bootstrap helper.
