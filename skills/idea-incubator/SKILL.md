---
name: idea-incubator
version: 1.4.2
last-updated: 2026-05-11
description: >-
  Capture, classify, connect, review, and promote speculative ideas into a
  searchable GitHub issue inbox. Use when the user says "new idea", "incubate
  this", "add this to my inbox", "process my Telegram dump", "review my
  ideas", "does this connect to anything?", "promote idea #N", or wants to
  turn a rough note, voice fragment, or URL into a tracked issue. Telegram
  Saved Messages is the quick-capture layer; GitHub issues are the durable
  layer. Do not use for ideas that are already scoped and ready to build —
  route those directly to maker-engineering or the relevant specialist.
---

# Idea Incubator

Use this skill to turn rough ideas into a searchable GitHub issue inbox,
connect them to related work, review the backlog, and promote ready ideas
into specialist handoffs.

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
- `yearbook rollout`
- `design book rollout`
- `private media pilot`
- `photo album pilot`

The phrases are kept punctuation-free so substring-matching agents (Codex,
Gemini CLI) hit them as reliably as Claude does.

## Do not trigger for

- Ideas that already have a clear build plan — route to `maker-engineering` instead.
- Feature requests for active code projects — open a GitHub issue directly.
- Tasks the user wants done immediately rather than tracked.

## Modes

1. **Capture** - turn one idea into one issue draft. If the input is a note,
   URL, or voice-to-text fragment, keep the draft short and actionable.
2. **Intake** - split a pasted Telegram dump into candidate ideas. Keep
   uncertain splits visible instead of guessing.
3. **Connect** - search for related ideas, prerequisites, duplicates, and
   cross-pollination candidates. Link them; do not auto-close.
4. **Review** - surface stale ideas, best-fit-for-now ideas, and clusters
   worth revisiting. Summarize; do not score emotional resonance numerically.
5. **Promote** - draft the handoff text for the downstream repo or specialist
   skill. Include `closes #N` only when the user wants the tracked issue closed
   by the downstream work. Route to `maker-engineering` for physical builds,
   to a domain specialist (`instrument-maker`, `makerspace`, `reverse-engineer`)
   when the scope is clear, or to a project repo when the idea belongs in an
   existing backlog. Always include the **promotion-readiness matrix** from
   [`references/promotion-handoff.md`](references/promotion-handoff.md) before
   selecting a single issue, and run the **binary-asset / LFS prompts** when
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
6. **Promote-batch** - cluster-aware promotion. Use when multiple capture
   issues share a recovery, archive, intake-dump, or thematic root and should
   be triaged as a unit instead of one-by-one. See the dedicated section
   below; the worked example is in
   [`references/promote-batch-example.md`](references/promote-batch-example.md).

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
2. **Already-satisfied flagging** - mark any issue whose deliverable already
   exists in the repo, working dir, or upstream system. Recommend `close`,
   not `promote`, for those.
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

## Operating rules

- Default to mobile-friendly, copy-pasteable Markdown.
- Use GitHub issues as the durable incubation layer.
- Treat Telegram Saved Messages as the quick capture layer.
- If `gh` is available, you may create labels or issues directly; otherwise
  print the exact command or issue draft.
- Do not hard-code repository ownership or visibility when the target repo is
  unknown. Use a placeholder or ask the user first.
- Do not auto-close ideas, and do not invent ideas that the user did not capture.

## Bundled references

- [`references/label-schema.md`](references/label-schema.md)
- [`references/issue-template.md`](references/issue-template.md)
- [`references/promotion-handoff.md`](references/promotion-handoff.md)
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
- [`references/private-media-decision-stub.md`](references/private-media-decision-stub.md)
  - Compact owner checklist for photo-album/private-media pilots before
    downstream repo scaffolds, imagegen/layout studies, or media imports.
- [`references/promote-batch-example.md`](references/promote-batch-example.md)
  - Worked example: legacy-import / Weather Balloon Camera Vessel cluster.

## Optional helpers

Both helpers create the same labels and need an authenticated `gh`. Pick the
one that matches the host shell:

- [`scripts/bootstrap-labels.sh`](scripts/bootstrap-labels.sh) - bash, for
  WSL, macOS, Linux, and Git Bash on Windows.
- [`scripts/bootstrap_labels.py`](scripts/bootstrap_labels.py) - Python 3,
  for native PowerShell on Claude Desktop (Windows) or any environment where
  bash is awkward but Python is available.

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
