# Institutional Knowledge Store

Story #241. The durable lessons-learned store for the idea-incubator pipeline,
plus the **pre-read** contract that feeds those lessons into the next brainstorm
parse so the incubator gets smarter every cycle.

This store is *written* by the retrospective agent
([`../agents/retrospective.md`](../agents/retrospective.md)) and *read* by the
parser before it generates new epics. Together with the Devil's Advocate agent
([`../agents/devils-advocate.md`](../agents/devils-advocate.md)) this closes the
learning loop: critique up front, lesson captured at close, lesson re-applied
next time.

## Entry format

One entry per lesson. Keep each entry small and transferable. The three fields
are load-bearing; the date and source are provenance.

```markdown
### <short lesson title>
- **Context:** <when/where this applies - the situation that produced it>
- **Lesson:** <the transferable takeaway, stated as guidance>
- **Applies-to:** <comma-separated tags: domains, modes, artifact types>
- **Source:** <epic #N retro, YYYY-MM-DD>
```

`Applies-to` tags are the index. Use the same vocabulary as the domain labels
(`instrument`, `woodworking`, `sheet-metal`, `electronics`, `firmware`,
`software`, `maker`, `skills`, `yoga`) plus pipeline modes (`capture`,
`intake`, `promote`, `promote-batch`, `estimation`, `dependencies`, `lfs`,
`provenance`). Consistent tags are what make the pre-read filter work.

## The pre-read step

Before the parser generates new epics/stories from a brainstorm (Stage 3 of the
[Gemini export pipeline](gemini-export-pipeline.md)):

1. **Derive the draft's tags.** Run the same domain routing
   ([`domain-label-routing.md`](domain-label-routing.md)) over the raw
   brainstorm to get candidate domain tags.
2. **Load matching lessons.** Select store entries whose `Applies-to` tags
   intersect the draft tags. If none match, load the small set of
   cross-cutting lessons tagged `general`.
3. **Inject as context.** Prepend the selected lessons to the parse prompt as a
   "prior lessons to honor" block. The parser should let them shape splitting,
   labeling, scoping, and which stories to pre-flag for the Devil's Advocate.
4. **Cite, do not silently obey.** When a lesson changes a decision, note it in
   the generated epic ("applied lesson: <title>") so the choice is auditable.

Steps 2–3 are automated by
[`../scripts/prior_lessons_preread.py`](../scripts/prior_lessons_preread.py):
pass `--tags <a,b>` (or `--brainstorm <file>` for naive tag derivation) and it
parses this store plus any per-epic notes under
[`institutional-knowledge/`](institutional-knowledge/), ranks by tag overlap,
caps to `--limit` (default 5), falls back to `general` lessons when nothing
matches, and prints the ready-to-prepend block. It exits cleanly with an
explicit "no prior lessons" note when the store/folder is empty or missing.

Keep the pre-read cheap: cap the injected lessons (e.g. top 5 by tag overlap)
so the parse prompt does not bloat. Stale or contradicted lessons should be
edited at the source by a later retro, not worked around in the parser.

## Seed entries

These are starter lessons distilled from existing incubator practice so the
pre-read has something to load on day one. Retros append more over time.

### Recovery/import captures keep their source issue open
- **Context:** Promoting archive, legacy, or recovery captures into a new repo.
- **Lesson:** Default to `Refs #N`, not `Closes #N`, so the source capture
  stays open as a provenance anchor until the evidence ledger lands.
- **Applies-to:** promote, promote-batch, provenance
- **Source:** seeded from idea-incubator 1.2.0 practice, 2026-06-16

### Promote one cluster member first to set conventions
- **Context:** A cluster of 5+ sibling captures sharing a scaffold.
- **Lesson:** Promote one first to lock LFS rules, labels, and README
  structure; the rest mirror it. Avoids a rebase wave when lanes land parallel.
- **Applies-to:** promote-batch, lfs, dependencies
- **Source:** seeded from idea-incubator 1.2.0 practice, 2026-06-16

### Run LFS prompts before any binary-asset repo scaffold
- **Context:** Captures mentioning CAD, media, ZIPs, PDFs, audio, or video.
- **Lesson:** Decide the LFS/large-asset policy before the first commit, not
  after a >100 MB file is already in history.
- **Applies-to:** promote, lfs, maker, instrument
- **Source:** seeded from idea-incubator 1.2.0 practice, 2026-06-16

### Keep uncertain idea splits together
- **Context:** Intake of a dump where item boundaries are unclear.
- **Lesson:** When a split is uncertain, keep candidates in one issue and mark
  the ambiguity rather than guessing into two wrong issues.
- **Applies-to:** intake, capture, general
- **Source:** seeded from idea-incubator Intake mode, 2026-06-16

### Write stories as implementation plans, not feature requests
- **Context:** Filing stories for the autonomous Alice–Iris agent grid to drain.
- **Lesson:** The single biggest throughput multiplier (5–10x) is a story that
  names the file(s) to create/extend, the interface/class/function signatures,
  the key methods/schema fields, and what the tests should cover — so the agent
  transcribes a finished design instead of designing while it builds. If the
  brainstorm is too vague to name files/interfaces honestly, mark
  `needs-clarification` rather than inventing false precision.
- **Applies-to:** software, firmware, electronics, general, estimation
- **Source:** wrfcoin/autoresearch 40-PR session retro, 2026-06-21

### Ship a loop contract and keep tests fast for autonomous epics
- **Context:** An epic intended to be drained by one autonomous session.
- **Lesson:** Resolve every recurring decision upfront in a `loop-build.md` the
  session Reads first — next-issue order, branch naming (`feat/N-name`), PR body
  (`Refs #N`, never `Closes`), never self-merge, no sub-agents, and an explicit
  termination signal (`DOMAIN DRAINED`). Keep the repo's test suite under ~10s:
  the verify-and-move-on loop, not model speed, is the real throughput ceiling.
- **Applies-to:** software, firmware, general, dependencies
- **Source:** wrfcoin/autoresearch 40-PR session retro, 2026-06-21

### Sequence stories additive-only with no runtime cross-dependencies
- **Context:** Stories that sibling agents implement in parallel off clean main.
- **Lesson:** Prefer adding new files/sections over refactoring shared code
  (zero merge-conflict surface), and sequence so no story has a runtime
  dependency on a prior story's PR being merged — each branch recreates what it
  needs from main. Flag any unavoidable hard dependency with `blocked-by #N` and
  note same-file collisions in the epic's Technical Risks section.
- **Applies-to:** software, firmware, dependencies, general
- **Source:** wrfcoin/autoresearch 40-PR session retro, 2026-06-21
