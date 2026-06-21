# Gemini -> Obsidian -> GitHub Export Pipeline

Design doc for the **Gemini-API-export half** of the autonomous idea pipeline
(Story #237). This document specifies how a brainstorm conversation captured in
Gemini becomes a set of tracked GitHub issues, with idempotency, dedup, and
failure handling that lets the run be retried safely.

> Scope boundary: #237 owns the *export* side (Gemini conversation -> Obsidian
> vault inbox -> parsed idea blocks -> draft issue payloads). The *sync* side
> (writing parsed notes into the durable issue inbox and reconciling state) is
> coordinated with StudioPipeline #57's "notes-to-issues sync". See
> [Coordination with StudioPipeline #57](#coordination-with-studiopipeline-57).

## The flow

```
[1] Gemini conversation / Saved item
      | export (Gemini API or manual "export to Markdown")
      v
[2] Obsidian vault inbox  (vault/00-inbox/*.md)
      | watcher or manual "process my inbox"
      v
[3] Claude parse  (idea-incubator Intake mode + prior-lessons pre-read)
      | split into idea blocks -> draft issue payloads
      v
[4] GitHub issues  (capture-labeled, deduped, idempotent)
```

Each arrow is a stage that can be run, retried, and audited independently. The
pipeline is deliberately **stage-isolated** so a failure at stage [4] never
corrupts the Obsidian inbox at stage [2], and a re-run never double-files.

### Stage 1 - Gemini export

> **Mobile path:** on iOS or Android, a one-tap share action (iOS Shortcuts /
> Android Tasker) clips the Gemini chat URL and writes a stub `.md` file directly
> into the vault inbox via Obsidian Advanced URI, bypassing manual desktop steps.
> See [`mobile-capture-bridge.md`](mobile-capture-bridge.md) for setup and
> [`scripts/url_upsert.py`](../scripts/url_upsert.py) for the filename-stability
> contract.

Two supported intake forms:

1. **API export** (preferred, automatable): pull the conversation transcript
   via the Gemini API and write a single Markdown file per conversation into
   the Obsidian inbox. The exporter is responsible only for fidelity (preserve
   the user's words) and for stamping provenance front-matter.
2. **Manual export** (fallback, no credentials): the user pastes or drops a
   `*.md` / `*.json` brainstorm file into the inbox folder. The downstream
   parser does not care which form produced the file.

Every exported file MUST carry provenance front-matter so later stages can dedup
and attribute:

```yaml
---
source: gemini
conversation_id: <stable id from Gemini, or sha256 of the transcript>
exported_at: <ISO-8601 UTC>
title: <human title of the brainstorm>
---
```

If the API does not expose a stable conversation id, synthesize one as
`sha256(normalized_transcript)` and record it. This id is the anchor for
idempotency across the whole pipeline.

### Stage 2 - Obsidian vault inbox

- Exported files land in a dedicated inbox folder (default `00-inbox/`).
- The inbox is append-only from the exporter's perspective; the parser MOVES
  processed files to `01-processed/` (or stamps `processed: true` in
  front-matter) so a re-run does not reprocess them.
- The vault is the human-auditable buffer: the user can edit, split, or delete
  a brainstorm file before it is parsed.

### Stage 3 - Claude parse

The parser runs idea-incubator **Intake mode** over each unprocessed inbox
file. Before generating any epics or issues, it performs the **prior-lessons
pre-read** (Story #241): load relevant entries from
[`institutional-knowledge.md`](institutional-knowledge.md) filtered by the
draft's domain tags, and let those lessons shape splitting, labeling, and
scoping decisions.

Parsing rules:

- Split into idea blocks on clear separators (headings, blank-line gaps,
  numbered/bulleted lists of distinct ideas). When a split is uncertain, keep
  the candidate items together and mark the ambiguity (mirrors the existing
  Intake-mode rule in `SKILL.md`).
- Emit one **draft issue payload** per idea block: `title`, `body`
  (issue-template skeleton), `labels` (domain auto-routing per
  [`domain-label-routing.md`](domain-label-routing.md)).
- Do not invent ideas the user did not capture.

### Stage 4 - GitHub issues

Draft payloads become issues in the durable inbox repo. This stage enforces the
dedup and idempotency contract below. By default the helper script
([`scripts/gemini_to_github.py`](../scripts/gemini_to_github.py)) runs in
`--dry-run` mode and only prints payloads; creating issues requires explicit
opt-in plus credentials.

## Data contract

The unit that flows between stages 3 and 4 is the **draft issue payload**:

```json
{
  "fingerprint": "<sha256 of conversation_id + normalized idea-block text>",
  "conversation_id": "<from stage-1 front-matter>",
  "source": "gemini",
  "title": "<short idea title>",
  "body": "<issue-template skeleton, see references/issue-template.md>",
  "labels": ["capture", "<domain label>"],
  "block_index": 0
}
```

- `fingerprint` is the dedup key (see below).
- `body` follows the existing `references/issue-template.md` skeleton, including
  a `## Capture` block that records `source: gemini` and the `conversation_id`
  so the issue itself is self-describing for future dedup.
- `labels` always include `capture`; domain labels come from the routing table.

## Idempotency / dedup strategy

Two layers, both keyed on the **fingerprint**:

1. **Pre-flight search.** Before creating an issue, search the inbox repo for
   an existing issue carrying the same fingerprint. The fingerprint is embedded
   in the issue body as an HTML comment marker:
   `<!-- idea-fingerprint: <sha256> -->`. If found, skip creation and (in
   verbose mode) print the existing issue URL.
2. **Stage-2 processed marker.** Because processed inbox files are moved /
   stamped, a re-run of the watcher will not re-emit payloads for already
   handled conversations even if GitHub search is unavailable.

Fingerprint construction:

```
fingerprint = sha256(conversation_id + "\n" + normalize(idea_block_text))
normalize(t) = lowercased, whitespace-collapsed, trailing punctuation stripped
```

Using `conversation_id` in the fingerprint means the *same idea text* captured
in two *different* brainstorms is treated as two captures (intentional - they
have different provenance), while a re-run of the *same* brainstorm is deduped.

## Failure handling

| Failure | Stage | Behavior |
|---|---|---|
| Gemini API auth / rate limit | 1 | Exporter aborts before writing; inbox untouched. Safe to retry. |
| Malformed export file | 2 | Parser quarantines the file to `99-quarantine/` with an error note; other files still process. |
| Ambiguous idea split | 3 | Keep candidates in one payload, mark ambiguity, label `needs-clarification`. Never guess. |
| GitHub auth / network error | 4 | Per-payload try/except; failed payloads are written to a `--failed-out` file for replay. Inbox file is NOT marked processed until all its payloads succeed. |
| Duplicate fingerprint found | 4 | Skip creation; this is success, not failure. |

The whole pipeline is **resumable**: re-running with the same inbox is a no-op
for already-filed ideas and only retries the gaps.

## Coordination with StudioPipeline #57

StudioPipeline #57 owns a broader "notes-to-issues sync". This pipeline (#237)
is the Gemini-API-export half that *feeds* it:

- #237 produces deduped, fingerprinted draft payloads and (optionally) files
  them as `capture` issues.
- #57's sync layer is responsible for ongoing reconciliation (closing,
  relabeling, linking) of those issues against the wider studio backlog.
- The shared contract is the **fingerprint marker** in the issue body. As long
  as both halves agree on `<!-- idea-fingerprint: ... -->`, either side can
  dedup against issues the other created. Do not change the marker format
  without updating #57.

## Operating rules (inherited)

- Default to mobile-friendly, copy-pasteable Markdown for any drafts surfaced
  to the user.
- Do not hard-code repo ownership/visibility; use a placeholder or ask.
- Do not auto-close ideas; do not invent ideas the user did not capture.
- `--dry-run` is the default for the helper script; issue creation is opt-in.
