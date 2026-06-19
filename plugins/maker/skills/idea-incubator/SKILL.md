---
name: idea-incubator
version: 1.14.0
last-updated: 2026-06-19
description: >-
  Capture, classify, connect, review, and promote speculative ideas into a
  searchable GitHub issue inbox. Use when the user says "new idea", "incubate
  this", "add this to my inbox", "process my Telegram dump", "review my
  ideas", "does this connect to anything?", "promote idea #N", or wants to
  turn a rough note, voice fragment, or URL into a tracked issue. Telegram
  Saved Messages is the quick-capture layer; GitHub issues are the durable
  layer. Do not use for ideas that are already scoped and ready to build —
  route those directly to maker-engineering or the relevant specialist.
  Also use when Tony hands over a brainstorm document (a clipped
  Gemini/Obsidian conversation) to be filed as GitHub epics, stories, and
  issues with Fibonacci story points across his repo ecosystem — phrases like
  "file gh issues/stories/epics from this", "ingest this brainstorm", "break
  this into epics and stories", "here's my next brainstorming doc".
---

# Idea Incubator

Use this skill to turn rough ideas into a searchable GitHub issue inbox,
connect them to related work, review the backlog, and promote ready ideas
into specialist handoffs.

## Mode: Brainstorm → epics/stories/points ingestion

Tony's primary idea-ingestion path is turning a clipped brainstorm document (voice → Gemini → Obsidian → .md) into GitHub **epics, stories, and issues with story points**, deduplicated and routed across his repo ecosystem, then implemented by an Alice–Iris agent grid. When he uploads a brainstorm doc to be filed, follow `references/brainstorm-to-issues-pipeline.md` — it has the full process, the epic/story label + body conventions, the Fibonacci point rubric, the domain→repo routing table, and the IP / Masonic care rules. Confirm scope and routing forks with one AskUserQuestion pass before filing; comment cross-links on existing epics instead of duplicating.

## Connectors

This skill works best with these MCP connectors. Claude will suggest connecting any that aren't already linked at the point they're needed (via `mcp__mcp-registry__suggest_connectors`).

- **GitHub** — required to create, label, search, and promote idea-issues. The default issue inbox lives in a GitHub repo. No registry UUID; configure via the Claude Code GitHub connector if available.
- **Linear** (`fa50c30c-9f62-4f94-b851-217868185db6`) — optional alternative inbox if the team uses Linear instead of GitHub Issues.
- **Notion** (`69f3a300-cc60-48c4-b237-dfac56530dbf`) — optional alternative inbox for workspace-based capture.
- **Atlassian Rovo** (`11ba10d9-477b-4988-bd1c-90a7fa680dc1`) — optional alternative for Jira/Confluence shops.

## Trigger phrases

- `new idea`
- `incubate this`
- `add this to the inbox`
- `process my Telegram dump`
- `review my ideas`
- `does this connect to anything`
- `promote idea #N`
- `promote the cluster`
- `batch promote`
- `review the cluster`
- `cross-pollinate`
- `tag this idea`
- `what reuses this`
- `yearbook rollout`
- `design book rollout`
- `private media pilot`
- `photo album pilot`
- `file gh issues/stories/epics from this`
- `ingest this brainstorm`
- `break this into epics and stories`
- `here's my next brainstorming doc`
- `red-team this epic`
- `devil's advocate`
- `retro this epic`
- `lessons learned`
- `process my inbox`

The phrases are kept punctuation-free so substring-matching agents (Codex,
Gemini CLI) hit them as reliably as Claude does.

## Do not trigger for

- Ideas that already have a clear build plan — route to `maker-engineering` instead.
- Feature requests for active code projects — open a GitHub issue directly.
- Tasks the user wants done immediately rather than tracked.

## Modes

1. **Capture** - turn one idea into one issue draft. If the input is a note,
   URL, or voice-to-text fragment, keep the draft short and actionable. At
   capture time, also apply the **functional-tagging schema** in
   [`references/functional-tagging-schema.md`](references/functional-tagging-schema.md)
   so the idea joins the cross-pollination web from the start.
2. **Intake** - split a pasted Telegram dump into candidate ideas. Keep
   uncertain splits visible instead of guessing. For brainstorms exported from
   Gemini, use the
   [`references/gemini-export-pipeline.md`](references/gemini-export-pipeline.md)
   flow and the
   [`scripts/gemini_to_github.py`](scripts/gemini_to_github.py) helper to split
   into idea blocks and emit draft issue payloads. Run the
   **prior-lessons pre-read** from
   [`references/institutional-knowledge.md`](references/institutional-knowledge.md)
   before generating epics, and apply domain auto-routing per
   [`references/domain-label-routing.md`](references/domain-label-routing.md).
3. **Connect** - search for related ideas, prerequisites, duplicates, and
   cross-pollination candidates. Link them; do not auto-close. Use the
   functional tags (#243) and the **Cross-Pollination Librarian** agent in
   [`agents/cross-pollination-librarian.md`](agents/cross-pollination-librarian.md)
   to surface when a mechanism solved in one idea fits another idea's need.
4. **Review** - surface stale ideas, best-fit-for-now ideas, and clusters
   worth revisiting. Summarize; do not score emotional resonance numerically.
   The Obsidian **Shared Subassemblies MOC** in
   [`references/obsidian/shared-subassemblies-MOC.md`](references/obsidian/shared-subassemblies-MOC.md)
   is the human-facing dashboard for recurring subassemblies. Outside Obsidian
   (Codex/Gemini CLI, CI, terminal), run
   [`scripts/shared_subassemblies.py`](scripts/shared_subassemblies.py)
   `--dir <notes>` for the same shared-subassembly / shared-interface /
   candidate-pair views from the functional-tag frontmatter.
5. **Promote** - draft the handoff text for the downstream repo or specialist
   skill. Include `closes #N` only when the user wants the tracked issue closed
   by the downstream work. Route to `maker-engineering` for physical builds,
   to a domain specialist (`instrument-maker`, `makerspace`, `reverse-engineer`)
   when the scope is clear, or to a project repo when the idea belongs in an
   existing backlog. Always include the **promotion-readiness matrix** from
   [`references/promotion-handoff.md`](references/promotion-handoff.md) before
   selecting a single issue. For instrument design-book, yearbook, portfolio,
   or showcase chapter promotions, use the dedicated instrument chapter
   pattern in that reference before drafting a downstream issue. Run the
   **binary-asset / LFS prompts** when
   the capture mentions CAD, media, ZIPs, PDFs, audio, video, or any asset
   likely to exceed 100 MB. When the idea involves private media, family
   archives, photo albums, scanned documents, or personal video, also run the
   privacy-first checklist in
   [`references/private-media-family-archive.md`](references/private-media-family-archive.md).
   When the idea is a yearbook, design book, school archive, cohort book, or
   print-book rollout with identifiable people or private source media, also
   run the rollout gates in
   [`references/yearbook-design-book-rollout.md`](references/yearbook-design-book-rollout.md).
   If the user asks for a photo album or private media pilot, use the focused
   workflow in
   [`references/photo-album-private-media-pilot.md`](references/photo-album-private-media-pilot.md)
   before drafting downstream repo work, and surface the compact owner
   decision stub in
   [`references/private-media-decision-stub.md`](references/private-media-decision-stub.md)
   before any downstream repo scaffold, imagegen/layout work, or media import.
   For design-generation handoffs, prepend the **constraint-injection prompt**
   in [`references/prompts/constraint-injection.md`](references/prompts/constraint-injection.md)
   so generated designs default to the Universal Interface standards.
6. **Promote-batch** - cluster-aware promotion. Use when multiple capture
   issues share a recovery, archive, intake-dump, or thematic root and should
   be triaged as a unit instead of one-by-one. See the dedicated section
   below; the worked example is in
   [`references/promote-batch-example.md`](references/promote-batch-example.md).
7. **Cross-pollinate** - semantic-web mode. Use the functional tags (#243) to
   notice when a mechanism solved for one gadget is the exact fit another
   gadget needs. Reads the **circuits inventory** of solved functional
   primitives in [`references/circuits-inventory.md`](references/circuits-inventory.md)
   (built by [`scripts/build_circuits_inventory.py`](scripts/build_circuits_inventory.py)),
   surfaces shared subassemblies via the Obsidian MOC (#244), and posts
   suggestions via the Cross-Pollination Librarian agent (#247). Standardize
   mating boundaries against the **Universal Interface guide** in
   [`references/universal-interface-guide.md`](references/universal-interface-guide.md)
   so primitives stay swappable (the "Lego rule").

## Agent roles

The incubator can spawn (or paste-in, on hosts without subagents) two dual-role
agents that close the learning loop around generated epics:

- **Devil's Advocate / Red Team** —
  [`agents/devils-advocate.md`](agents/devils-advocate.md). Adversarially
  reviews a freshly generated epic *before* it is filed: challenges
  assumptions, names the weakest story, surfaces hidden dependencies, and lists
  failure modes. Invoke right after an epic is generated. **Every generated
  top-level epic MUST carry a `### Technical Risks & Assumptions` section** —
  the filed form of this pass, appended to the epic body with a role-attribution
  line, leaving the optimist `## Vision` / `## Stories` / `**Rollup:**` content
  unchanged. The section must list concrete, epic-specific risks, never generic
  boilerplate. Verify with
  [`scripts/check_epic_risks_section.py`](scripts/check_epic_risks_section.py).
- **Retrospective / Lessons-Learned** —
  [`agents/retrospective.md`](agents/retrospective.md). Reviews a *closed* epic
  and its stories/PRs, scores estimate accuracy, and writes lessons into
  [`references/institutional-knowledge.md`](references/institutional-knowledge.md),
  which the Intake pre-read loads on the next cycle.

## Promote-batch mode

Use Promote-batch when N capture issues share enough structure that promoting
them one at a time would re-do the same triage work N times.

### Cluster detection heuristics

A capture cluster is worth Promote-batch treatment when **any two** of the
following hold:

- **Burst:** N >= 5 `capture`-labeled issues opened within a 48-hour window.
- **Shared root:** issues share a substring in title or body (e.g. `archive`,
  `recovery`, `legacy`, a folder path, a specific event/source).
- **Shared template:** issue bodies follow the same `Capture / What this is /
  Why it matters / Next step / Promotion target` skeleton verbatim.
- **Shared blocker:** a single prerequisite (an inventory pass, a provenance
  decision, a repo-naming decision) gates all of them.

Clusters smaller than 5 are usually fine to promote individually with the
Promote mode's readiness matrix.

### Required Promote-batch outputs

1. **Promotion-readiness matrix** across the whole cluster (see
   [`references/promotion-handoff.md`](references/promotion-handoff.md)).
   When issue JSON, local repos, or inventory CSVs are available, use
   [`scripts/promote_batch_readiness.py`](scripts/promote_batch_readiness.py)
   and [`references/promote-batch-readiness.md`](references/promote-batch-readiness.md)
   to draft the matrix before making the final recommendation.
2. **Already-satisfied flagging** - mark any issue whose deliverable already
   exists in the repo, working dir, or upstream system. Recommend `close`,
   not `promote`, for those.
   Explicitly check existing anchors before recommending a new repo:
   local repos, staging folders, archive inventories, upstream systems, and
   already-merged PRs.
3. **One-promote-first recommendation** so the first promotion sets the
   shared scaffold conventions (LFS rules, label set, milestone naming, README
   structure) the rest mirror. This avoids a rebase wave when sibling lanes
   land in parallel.
4. **Binary-asset / LFS pass** - run the prompts from `promotion-handoff.md`
   for every cluster member that mentions binary or large-asset content.
5. **Provenance notes** - for recovery/import clusters, every promoted issue
   gets an `evidence-ledger` entry in the target repo separating archive
   facts from inferred claims. The ledger template is in
   `promotion-handoff.md`.

### When to use `Refs #N` vs `Closes #N`

- Use **`Closes #N`** when the downstream work fully delivers the captured
  idea and there is no reason to keep the source issue open as a provenance
  anchor.
- Use **`Refs #N`** when the source capture should remain open until the
  downstream evidence ledger or scaffold review lands - common for archive
  recovery, legacy import, and any promotion where provenance discipline
  outranks closing speed.

When in doubt for a recovery/import cluster, default to `Refs`.

## Cross-pollination engine

The cross-pollination engine (epic #236) turns the incubator from a linear
conveyor belt into a semantic web. Its pieces compose:

1. **Tag at intake** - apply the functional-tagging schema
   ([`references/functional-tagging-schema.md`](references/functional-tagging-schema.md))
   so every idea carries `functions:` / `interfaces:` / `materials:` facets.
2. **See the overlaps** - the Obsidian Shared Subassemblies MOC
   ([`references/obsidian/shared-subassemblies-MOC.md`](references/obsidian/shared-subassemblies-MOC.md))
   groups ideas by shared tags using Dataview.
3. **Standardize the boundary** - the Universal Interface guide
   ([`references/universal-interface-guide.md`](references/universal-interface-guide.md))
   keeps subassemblies swappable; the constraint-injection prompt
   ([`references/prompts/constraint-injection.md`](references/prompts/constraint-injection.md))
   enforces it on generated designs.
4. **Automate the match** - the Cross-Pollination Librarian agent
   ([`agents/cross-pollination-librarian.md`](agents/cross-pollination-librarian.md))
   scans inbox + vault and posts cross-pollination suggestion comments.
5. **Catalog the primitives** - the circuits inventory
   ([`references/circuits-inventory.md`](references/circuits-inventory.md),
   built by [`scripts/build_circuits_inventory.py`](scripts/build_circuits_inventory.py))
   indexes solved functional primitives for reuse.

## Operating rules

- Default to mobile-friendly, copy-pasteable Markdown.
- Use GitHub issues as the durable incubation layer.
- Treat Telegram Saved Messages as the quick capture layer.
- If `gh` is available, you may create labels or issues directly; otherwise
  print the exact command or issue draft.
- Do not hard-code repository ownership or visibility when the target repo is
  unknown. Use a placeholder or ask the user first.
- Do not auto-close ideas, and do not invent ideas that the user did not capture.
- Do not guess functional tags. If you cannot name a function honestly, add
  `needs-clarification` and ask — a wrong tag produces false cross-pollination
  matches.

## Bundled references

- [`references/label-schema.md`](references/label-schema.md)
- [`references/issue-template.md`](references/issue-template.md)
- [`references/promotion-handoff.md`](references/promotion-handoff.md)
- [`references/brainstorm-to-issues-pipeline.md`](references/brainstorm-to-issues-pipeline.md)
  - Brainstorm → GitHub epics/stories/points ingestion pipeline: process,
    label/body conventions, Fibonacci point rubric, domain→repo routing
    table, and IP / Masonic care rules.
- [`references/templates/hybrid-issue-template.md`](references/templates/hybrid-issue-template.md)
  - Skeletal hardware/software/firmware hybrid issue template with an Expected
    PDM Artifacts checklist. GitHub-native form lives at
    `.github/ISSUE_TEMPLATE/hybrid-idea.md`.
- [`references/gemini-export-pipeline.md`](references/gemini-export-pipeline.md)
  - Design doc for the Gemini -> Obsidian -> GitHub export pipeline, including
    data contract, idempotency/dedup, failure handling, and coordination with
    StudioPipeline #57.
- [`references/domain-label-routing.md`](references/domain-label-routing.md)
  - Data-driven keyword/signal -> domain-label routing table with confidence
    thresholds and a needs-triage fallback.
- [`references/institutional-knowledge.md`](references/institutional-knowledge.md)
  - Lessons-learned store format plus the pre-read step that feeds prior
    lessons into the next brainstorm parse. Written by the retrospective agent.
- [`references/functional-tagging-schema.md`](references/functional-tagging-schema.md)
  - Controlled vocabulary + YAML frontmatter spec (`functions:` /
    `interfaces:` / `materials:`) applied to every idea at intake (epic #236).
- [`references/obsidian/shared-subassemblies-MOC.md`](references/obsidian/shared-subassemblies-MOC.md)
  - Obsidian Map-of-Content with Dataview queries that group ideas by shared
    functional tags to surface recurring subassemblies (epic #236).
- [`references/universal-interface-guide.md`](references/universal-interface-guide.md)
  - Standardized mechanical/electrical interfaces (the "Lego rule") so
    subassemblies stay swappable across projects (epic #236).
- [`references/prompts/constraint-injection.md`](references/prompts/constraint-injection.md)
  - Reusable prompt fragment that injects Universal Interface constraints into
    design-generation requests (epic #236).
- [`references/circuits-inventory.md`](references/circuits-inventory.md)
  - Portfolio-wide index of reusable functional primitives ("circuits") with
    schema and currency rules (epic #236).
- [`references/private-media-family-archive.md`](references/private-media-family-archive.md)
  - Privacy-first promotion template for family archives, photo albums,
    scanned documents, and personal video.
- [`references/yearbook-design-book-rollout.md`](references/yearbook-design-book-rollout.md)
  - Rollout workflow for yearbooks, design books, cohort books, and private
    print projects with consent, provenance, proof, and image-gen derivative
    gates.
- [`references/photo-album-private-media-pilot.md`](references/photo-album-private-media-pilot.md)
  - Pilot workflow for private photo albums and media collections, including
    source-photo, LFS, privacy, and imagegen derivative rules.
- [`references/promote-batch-readiness.md`](references/promote-batch-readiness.md)
  - Helper workflow for readiness matrices, existing-anchor checks, and
    GitHub query fallbacks when live API evidence is uneven.
- [`references/private-media-decision-stub.md`](references/private-media-decision-stub.md)
  - Compact owner checklist for photo-album/private-media pilots before
    downstream repo scaffolds, imagegen/layout studies, or media imports.
- [`references/promote-batch-example.md`](references/promote-batch-example.md)
  - Worked example: legacy-import / Weather Balloon Camera Vessel cluster.

## Bundled agents

- [`agents/devils-advocate.md`](agents/devils-advocate.md) - adversarial
  red-team review of a freshly generated epic.
- [`agents/retrospective.md`](agents/retrospective.md) - blameless retro of a
  closed epic that writes lessons into the institutional-knowledge store.
- [`agents/cross-pollination-librarian.md`](agents/cross-pollination-librarian.md)
  - Scheduled librarian that scans the issue inbox + Obsidian vault, matches
    solved mechanisms to open needs via functional tags and/or embeddings, and
    posts cross-pollination suggestion comments (epic #236).
- [`agents/openai.yaml`](agents/openai.yaml) - OpenAI/Codex interface
  descriptor for the skill.

## Optional helpers

Both label helpers create the same labels and need an authenticated `gh`. Pick
the one that matches the host shell:

- [`scripts/bootstrap-labels.sh`](scripts/bootstrap-labels.sh) - bash, for
  WSL, macOS, Linux, and Git Bash on Windows.
- [`scripts/bootstrap_labels.py`](scripts/bootstrap_labels.py) - Python 3,
  for native PowerShell on Claude Desktop (Windows) or any environment where
  bash is awkward but Python is available.
- [`scripts/promote_batch_readiness.py`](scripts/promote_batch_readiness.py) -
  offline-first helper that converts saved issue JSON plus local anchor roots
  and inventory CSVs into a Promote-batch readiness matrix.
- [`scripts/gemini_to_github.py`](scripts/gemini_to_github.py) - dry-run-first
  helper that splits an exported Gemini brainstorm into idea blocks and emits
  fingerprinted draft issue payloads (Story #237).
- [`scripts/build_circuits_inventory.py`](scripts/build_circuits_inventory.py) -
  offline-first helper that walks repos/vault for tagged ideas and emits the
  circuits inventory as Markdown/JSON (dry-run by default).
- [`scripts/image_chapter_validator.py`](scripts/image_chapter_validator.py) -
  validates an image-gen-2 chapter manifest against the asset-contract defined
  in `references/image-gen-2-chapter-template.md` (Refs #92, #100, #210):
  checks required sidecar fields, enforces `derivative: true` and
  `non_dimensional: true` on all generated assets, validates `kind` values,
  enforces `packet_ref`, blocks publication when any asset is below
  `proof-reviewed`, and enforces the two-source rule on authority artifacts.
  Exit 0 = pass, 1 = violations, 2 = bad input. Use `--require-publishable`
  to fail on a valid-but-draft chapter.

If neither works (mobile zip-upload, sandboxed Codex Desktop, no `gh`), fall
back to the copy-pasteable `gh label create` block in
[`references/label-schema.md`](references/label-schema.md), or apply the
labels by hand from the GitHub web UI.

## Platform notes

This skill is intentionally portable. Behavior shifts a little by host:

- **Claude Code / Claude Desktop on WSL or macOS** - full path; `gh` and bash
  scripts work as written.
- **Claude Desktop on native Windows** - prefer the Python bootstrap helper;
  paths in this skill are POSIX-relative and resolve correctly.
- **Codex CLI / Codex Desktop** - invoke explicitly with `$idea-incubator`
  when you want guaranteed routing. The `$skill-name` syntax is a Codex
  convention; do not paste it into other clients.
- **Gemini CLI** - triggers match by substring, so the phrases above work;
  bundled scripts run via the host shell as usual.
- **Mobile zip-upload (Claude.ai)** - assume no `gh`, no shell. Stay in
  copy-pasteable Markdown mode and emit the issue draft and `gh label create`
  commands as text blocks for the user to run later.
