# Changelog

## 1.14.0 - 2026-06-19

- **image-gen-2 chapter asset-contract validator (#210).** Added
  `scripts/image_chapter_validator.py` — a pure-stdlib gate that validates a
  chapter JSON manifest against the contract defined in
  `references/image-gen-2-chapter-template.md`. Enforces: all 10 required asset
  sidecar fields, `derivative: true` and `non_dimensional: true` on every
  generated asset, allowed `kind` values, `packet_ref` present and matching,
  `proof-reviewed` threshold for publication (blocks on draft/privacy-reviewed),
  and the two-source rule (authority artifacts may NOT carry `derivative: true`).
  JSON output with `decision`, `publishable`, `violations[]`, and asset/artifact
  counts. Exit 0 = pass, 1 = violations, 2 = bad input; `--require-publishable`
  flag for CI use. 47 tests in `tests/test_image_chapter_validator.py`.
  Also adds `tests/` directory (first tests for idea-incubator).

## 1.13.0 - 2026-06-19

- **Offline Shared Subassemblies reporter (#244).** Added
  `scripts/shared_subassemblies.py` — the portable, unit-tested twin of the
  Obsidian Shared Subassemblies MOC. It reproduces the MOC's Dataview dashboards
  (shared subassemblies = functions in 2+ ideas, shared interfaces, and
  cross-pollination candidate pairs) from the `functions:` / `interfaces:`
  frontmatter, in pure stdlib, so the view works in Codex/Gemini CLI, CI, and a
  terminal where Dataview isn't available. The MOC + SKILL Review mode point at
  it. Added `tests/test_shared_subassemblies.py` (11 cases). Also realigns the
  SKILL.md version with the manifest (see note below).

## 1.12.0 - 2026-06-19

- **Cross-pollination Opportunities Detected report (#247, PR #298).** Upgraded
  `agents/cross-pollination-librarian.md` to v0.2.0: epics MUST now carry a
  `### Cross-Pollination Opportunities Detected` section distinguishing
  interface-reuse, interoperability, and silo-alert classes; in-place
  replacement is idempotent so re-runs don't duplicate the section.
- Added `scripts/check_cross_pollination_section.py`: conformance checker
  readable from a file, stdin, or a live issue via `gh`.
- 8 tests, all green.

## 1.11.0 - 2026-06-19

- **Confidence-weighted domain router (#242, PR #297).** Added
  `scripts/domain_router.py` (139 lines) implementing the
  `references/domain-label-routing.md` rules: keyword-signal weighting,
  confidence threshold gating, and `needs-triage` fallback.
- `scripts/gemini_to_github.py` updated to delegate domain labelling to
  `domain_router` instead of the inline ad-hoc fallback.
- Updated `references/domain-label-routing.md` to document the routing
  algorithm and tuning knobs.

## 1.10.0 - 2026-06-19

- **Prior-lessons pre-read loader (#241, PR #294).** Added
  `scripts/prior_lessons_preread.py`: parses the aggregate Institutional
  Knowledge store, ranks lessons by `Applies-to` tag overlap with the draft's
  tags, caps to `--limit` (default 5), falls back to `general`-tagged lessons
  when nothing matches, and renders a ready-to-prepend "prior lessons to honor"
  block.
- Updated `references/institutional-knowledge.md` with the pre-read step and
  cross-links to the new script.

## 1.9.0 - 2026-06-19

- **Retrospective sweep + Institutional Knowledge folder (#240, PR #293).**
  Added `scripts/retrospective_sweep.py`: given `--epic N`, parses the epic's
  `## Stories` checklist, pulls each child story's final state and labels,
  collects commits referencing the epic via `git log --grep`, and writes
  `epic-<N>-sweep.json` (raw evidence) and `epic-<N>-retro.md` (retro note
  with `Source: epic #N` backlink) into the Institutional Knowledge folder.
- Added `references/institutional-knowledge/README.md` documenting the folder
  layout and file-naming conventions.
- Updated `agents/retrospective.md` to invoke the sweep script and point to
  the output folder.

## 1.8.0 - 2026-06-18

- **Devil's Advocate / Red Team output wiring (#238, epic #235).** Made the
  red-team pass produce a durable, attributable artifact instead of an
  ephemeral critique: every generated top-level epic now MUST carry a
  `### Technical Risks & Assumptions` section.
- `references/brainstorm-to-issues-pipeline.md`: added the mandatory section to
  the epic-body convention and a red-team-before-filing process step; the
  optimist `## Vision` / `## Stories` / `**Rollup:**` content is preserved
  unchanged (the section is appended, never a rewrite).
- `agents/devils-advocate.md`: added a "Filed form" contract mapping the
  critique into the canonical `### Technical Risks & Assumptions` section with a
  role-attribution line.
- Added `scripts/check_epic_risks_section.py`: a dependency-light checker that
  flags epics missing the section, the role attribution, or carrying only
  boilerplate. Readable from a file, stdin, or a live issue via `gh`.
- Added `tests/test_check_epic_risks_section.py` (6 cases, all green).

## 1.7.0 - 2026-06-17

- **Cross-Pollination Engine (epic #236)** - turns the incubator from a linear
  conveyor belt into a semantic web that notices when a mechanism solved for
  one gadget is the exact fit another gadget needs. Source brainstorm:
  `HWE Project Management and Documentation Brainstorm.md` (Gemini, 2026-06-16).
- Added `references/functional-tagging-schema.md`: a controlled vocabulary plus
  YAML frontmatter spec (`functions:` / `interfaces:` / `materials:`) applied to
  every idea at intake. This is the backbone the rest of the epic builds on
  (Closes #243).
- Added `references/obsidian/shared-subassemblies-MOC.md`: an Obsidian
  Map-of-Content with Dataview and dataviewjs queries that group ideas by
  shared functional tags to surface recurring subassemblies (Closes #244).
- Added `references/universal-interface-guide.md`: the "Lego rule" design guide
  standardizing mounting patterns, fasteners, tolerance classes, connectors/
  pinouts, and naming so subassemblies stay swappable. Cross-links HWE-Pipeline
  #39 (cross-layer maker signature / cohesion) (Closes #245).
- Added `references/prompts/constraint-injection.md`: a reusable prompt fragment
  that injects the Universal Interface constraints into design-generation
  requests, with usage notes and a before/after example (Closes #246).
- Added `agents/cross-pollination-librarian.md`: an agent definition for a
  scheduled librarian that scans the GitHub issue inbox + Obsidian vault, uses
  functional tags and/or embeddings to match solved mechanisms to open needs,
  and posts cross-pollination suggestion comments with noise guardrails
  (Closes #247).
- Added `references/circuits-inventory.md` and
  `scripts/build_circuits_inventory.py`: a portfolio-wide index of reusable
  functional primitives ("circuits") plus an offline-first, dry-run-default
  builder that walks repos/vault for tagged ideas and emits Markdown/JSON
  (Closes #248).
- Updated `SKILL.md`: added a Cross-pollinate mode (mode 7), a Cross-pollination
  engine section, new trigger phrases (`cross-pollinate`, `tag this idea`,
  `what reuses this`), a Bundled agents section, and references to the new
  files; tag-honesty operating rule added.

## 1.6.0 - 2026-06-17

Epic #235 - Idea-Incubator Workflow Automation & Agent Roles. Makes the
Gemini -> Obsidian -> Claude -> GitHub pipeline more autonomous and
self-improving with adversarial review, skeletal hybrid templating, and a
closed-loop retrospective.

- Added `references/gemini-export-pipeline.md`: design doc for the Gemini-API
  export half of the pipeline (flow, data contract, fingerprint-based
  idempotency/dedup, failure handling, and coordination with StudioPipeline
  #57) (Closes #237).
- Added `scripts/gemini_to_github.py`: dry-run-first helper that splits an
  exported Gemini brainstorm into idea blocks and emits fingerprinted draft
  issue payloads with inline domain routing (Closes #237).
- Added `agents/devils-advocate.md`: dual-role adversarial red-team agent that
  reviews a freshly generated epic before filing - challenges assumptions,
  names the weakest story, surfaces hidden dependencies, lists failure modes
  (Closes #238).
- Added `references/templates/hybrid-issue-template.md` and a GitHub-native
  form at `.github/ISSUE_TEMPLATE/hybrid-idea.md`: skeletal HW/SW/firmware
  hybrid issue with an Expected PDM Artifacts checklist (CAD, BOM, schematic,
  firmware, test plan, DHF links, etc.) (Closes #239).
- Added `agents/retrospective.md`: blameless retrospective agent for closed
  epics that scores estimate accuracy and writes lessons into the
  institutional-knowledge store (Closes #240).
- Added `references/institutional-knowledge.md`: lessons-learned store format
  plus the pre-read step that feeds prior lessons into the next brainstorm
  parse; cross-linked to the retrospective agent (Closes #241).
- Added `references/domain-label-routing.md`: data-driven keyword/signal ->
  domain-label routing table with confidence thresholds and a needs-triage
  fallback (Closes #242).
- Updated `SKILL.md`: documented the export pipeline, agent roles, hybrid
  template, routing, and pre-read; added new trigger phrases; bumped version to
  1.6.0.

## 1.5.0 - 2026-06-17

- Added brainstorm-to-issues ingestion mode + reference
  (`references/brainstorm-to-issues-pipeline.md`): documents Tony's
  voice→Gemini→Obsidian→GitHub epics/stories/points pipeline, label/body
  conventions, point rubric, domain→repo routing table, and IP/Masonic care
  rules.

## 1.4.4 - 2026-05-18

- Added `references/private-media-decision-stub.md`, a compact owner checklist
  for photo-album/private-media pilots before downstream repo scaffolds,
  imagegen/layout studies, media imports, or proof/export work.
- Updated the photo-album/private-media pilot workflow to surface unknown owner
  decisions as blockers before promotion proceeds.

## 1.4.3 - 2026-05-18

- Added `scripts/promote_batch_readiness.py`, an offline-first helper that
  drafts Promote-batch readiness matrices from saved issue JSON, local anchor
  roots, and archive inventory CSVs (Closes #96).
- Added `references/promote-batch-readiness.md` with existing-anchor /
  already-satisfied checks and GitHub query fallback guidance for uneven
  `gh search` fields or API connectivity.
- Added a fixture and example output shape in `evals/` so agents can validate
  matrix generation without live GitHub access.

## 1.4.2 - 2026-05-17

- Added instrument design-book / yearbook chapter promotion guidance to
  `references/promotion-handoff.md` (Refs #104).
- Promote mode now routes instrument chapter ideas through the readiness mirror
  rule before drafting downstream work in `tonykoop/instrument-maker`.
- Downstream issue pattern uses `Refs #100`, not `Closes #100`, until the
  chapter scaffold and one L2+ pilot scaffold are proven; build-ready claims
  stay gated to L3+ and measured/empirical claims stay gated to L4.

## 1.4.1 - 2026-05-10

- Added a focused photo-album/private-media pilot workflow with source-photo
  rules, LFS-first import gates, privacy/metadata blockers, and imagegen
  derivative boundaries.
- Added proof/export gates for watermarked review proofs, proof-review signoff,
  consent/off-limits review, and vendor/public/family-share export boundaries.
- Updated skill routing and promotion handoff guidance so pilot requests use
  the source-photo workflow before downstream repo work.

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
