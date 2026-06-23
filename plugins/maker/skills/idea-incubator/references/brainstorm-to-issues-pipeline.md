# Brainstorm → GitHub Issues Ingestion Pipeline

Tony's durable idea-ingestion workflow: turn a brainstorm document into GitHub **epics, stories, and issues with story points**, routed across his repo ecosystem.

## When to run this
Trigger when Tony uploads or points to a brainstorm document (usually a Gemini conversation clipped to Markdown via the Obsidian Web Clipper) and wants it filed. Cues: "file gh issues/stories/epics from this", "ingest this brainstorm", "pull the ideas out and file them", "break this into epics and stories", "here's my next brainstorming doc."

## The upstream pipeline (context)
voice → Gemini (fast, uninhibited idea expansion) → Obsidian Web Clipper → `.md` file → THIS step (Claude/Codex parses into structured epics/stories) → GitHub issues → AI dev team (a tmux persona grid, Alice–Iris) implements. This GitHub layer is the *durable* layer; Telegram/quick-capture is the *inbox* layer (the rest of this skill).

## Process
1. **Read the whole doc.** If it's large (>~600 lines), delegate full extraction to a subagent that returns a dedup-aware, routing-ready plan, so the main context stays clean.
2. **Extract every distinct idea in reading order** so nothing is lost.
3. **Group into coherent epics** (~4–9 stories each) and **estimate Fibonacci story points** per story using the rubric below.
4. **Dedup against already-filed epics:** for overlaps, post a cross-link **comment** on the existing epic instead of duplicating; only file genuinely-new or clearly-differentiated work.
5. **Route each epic** to the right repo by domain (table below).
6. **Confirm the genuine forks with AskUserQuestion BEFORE filing** — scope, repo routing, public-vs-private for IP, philosophy handling. Do NOT gate the first read on a question; ask once the plan is shaped.
7. **Red-team every top-level epic BEFORE filing.** After the optimist pass drafts an epic + its stories, run the Devil's Advocate / Red Team role ([`../agents/devils-advocate.md`](../agents/devils-advocate.md)) and fold its critique into a `### Technical Risks & Assumptions` section on the epic body (see the epic-body convention below). The optimist `## Vision` / `## Stories` / `**Rollup:**` content is preserved unchanged — the red-team output is *appended*, never a rewrite.
8. **File via the GitHub MCP:** create the epic first, then its stories, then backfill the epic's `## Stories` checklist + rollup. Use the conventions below.
9. **Post overlap cross-link comments**, then refresh routing memory.

## Issue conventions
- **Labels:** epic = `["epic","enhancement"]`; story = `["story","enhancement","sp:N"]` with `sp:N` ∈ {`sp:2`,`sp:3`,`sp:5`,`sp:8`} (Fibonacci only). Applying a missing label via the API auto-creates it. NOTE: `update_issue` REPLACES the whole label array — always pass the issue's existing labels PLUS your additions.
- **Epic body:** `**Tracking epic.** <1-paragraph summary>. Source: ` + the doc filename + ` (<source + date>).` then `## Vision`, `## Stories` (a checkbox list `- [ ] #N - <title> (sp N)`, backfilled after the children exist), `**Rollup:** ~N points.`, then a **mandatory** `### Technical Risks & Assumptions` section, then `## Links`.
- **`### Technical Risks & Assumptions` (every top-level epic):** the filed form of the Devil's Advocate / Red Team pass. It opens with an attribution line — `_Red-Team pass (Devil's Advocate role — [`../agents/devils-advocate.md`](../agents/devils-advocate.md)). Optimist breakdown above is unchanged._` — followed by concrete, checkable bullets distilled from the critique (challenged assumptions → what breaks, the weakest story, hidden dependencies/collisions, top failure modes, estimate reality check). Never generic boilerplate: each bullet names a specific story, file, interface, or assumption from *this* epic. If the red-team pass genuinely finds nothing, say so explicitly and name what was checked.
- **Story body:** `**Story points:** N`, `## Scope`, `## Why`, `## Implementation plan`, `## Acceptance` (3–5 bullet criteria), `## Links` (referencing `Epic #N` + any cross-links, ending with the source citation).
- **`## Implementation plan` (write stories as plans, not feature requests):** this section is the single largest throughput multiplier for the downstream agent grid (5–10x) — an agent that only *transcribes* a finished design runs ~3–5x faster than one that must design while it builds. Spell out, as concretely as the brainstorm allows: the **file(s) to create or extend** (real paths), the **interface/class/function names + signatures**, the **key methods or schema fields** to add, where to wire it in, and **what the tests should cover** (named cases, expected output). Write "create `incident-detector.ts` exporting `class IncidentDetector` with `detect(run: Run): Trigger[]`; add `incident_triggers` to `types.ts`; tests cover empty-run, single-trigger, multi-trigger" — NOT "add incident detection." If the brainstorm is too vague to name files/interfaces honestly, say so in the section and add `needs-clarification` rather than inventing a false-precision plan. See [[feedback-autonomous-session-throughput]].
- **Additive over refactor; no runtime cross-dependencies.** Prefer stories that add a new file or a new section to an existing file over stories that rename/refactor shared code — additive work has zero merge-conflict surface when sibling agents branch off clean `main` in parallel. Sequence stories so none has a *runtime* dependency on a prior story's PR being merged: each branch must recreate what it needs from `main` (duplicate a small type rather than depend on an unmerged one). When two stories genuinely must touch the same file, note the collision in the epic's `### Technical Risks & Assumptions`. Flag any unavoidable hard dependency explicitly with `blocked-by #N`.
- **Point rubric:** `sp:2` trivial/config/docs/tiny single-file; `sp:3` small contained feature or schema; `sp:5` substantial multi-component feature; `sp:8` large/complex/cross-cutting/research-heavy.
- **Always cite the source brainstorm filename + date** in every issue.
- **End state:** every open issue should fit the Jira scheme — belongs to an epic or story, and every story has exactly one `sp:N` value.

## Routing table (domain → repo)
- Hardware PDM/PLM, doc taxonomy, design-history, metrology/QMS, vendor/tribology, reverse-engineering (point-cloud), IP-provenance/canaries/signature, cabling, right-to-repair, brand-doc engine, geo-equity supply-chain → **tonykoop/HWE-Pipeline** (open-core).
- Generative / voice-to-CAD, functional-architecture & parametric-envelope engine, PCBA DFM audit, interactive design-approval + Wolfram → **StudioPipeline/hwe** (org `StudioPipeline`, repo `hwe`).
- The "GitHub work tracker" / Jira-for-Makers PDM dashboard, agentic media studio org, modular video node pipeline, template gallery, dashboard forecasting → **tonykoop/StudioPipeline**.
- Benchmark content (4D matrix placements, eval harvesters, workflows league) → **tonykoop/makerbench-hwe**.
- Shop-floor tool catalogs, jigs, make/order/buy/borrow, community credentialing → **tonykoop/makerspace**.
- Idea-incubator workflow + cross-pollination meta-improvements, and speculative far-future captures → **tonykoop/claude-skills** (this repo's issue inbox; labels `capture`/`intake`/`maker`/`general`/`skills`).
- IP / patent captures / the "select algorithm" / Reverse-DFM / consulting-firm moat → **PRIVATE**: `tonykoop/Advanced-HWE` (Reverse-DFM + consulting) and `tonykoop/StudioPipeline-Selecta` (select algorithm + patent captures). NEVER put inventive steps in a public repo — avoid starting the statutory one-year disclosure clock.
- wrf ecosystem (org `wrfcoin`): material-provenance / extraction ledger → `wrfcoin/wrfatlas`; decentralized situational-awareness + People's News Network → `wrfcoin/wrfsentinel`; DAO governance / tokenomics → `wrfcoin/smart-contracts`.
- Philosophy / ethics / physics-of-constants corpus + AI-governance constitution → **tonykoop/philosophy** (private). Fold related musings as stories under the existing corpus epic rather than spawning new epics.

## Agent-grid readiness (make the sprint mechanically executable)

The GitHub layer exists so the Alice–Iris agent grid can implement it autonomously. A single Sonnet session pushed **40 PRs in ~3h** off a well-structured epic — the win was structural, not prompting. Bake that structure in at filing time so every epic is ready to drain in one sitting (lesson: [[feedback-autonomous-session-throughput]]).

- **Issues as implementation plans** — enforced by the `## Implementation plan` story convention above. This is the highest-leverage item; treat a story with no nameable files/interfaces as not-yet-ready (`needs-clarification`) rather than filing a vague one.
- **Ship a loop contract with the epic.** When an epic is meant to be drained autonomously, copy the canonical template [`templates/loop-build.md`](templates/loop-build.md) to the target repo root as `loop-build.md` (fill its `<…>` placeholders with the epic number, repo slug, and the repo's real test/lint commands), and reference it from the epic body's `## Links`. It encodes the recurring-decision rules the session Reads first, so the agent never stalls to ask:
  - **Next:** lowest-numbered open story in this epic, in numeric order.
  - **Branch:** `feat/N-short-name`.
  - **PR body:** `Refs #N` (never `Closes` — the human merges and closes).
  - **Merge policy:** never self-merge; branch off clean `main` every time.
  - **Sub-agents:** none — one context implements the whole epic directly (a tight single-domain sprint is faster in one context that knows the structure than five that must rediscover it).
  - **Termination signal:** an explicit phrase (e.g. `DOMAIN DRAINED: <repo>/<epic>`) emitted when every story is implemented, so the session knows when to stop.
- **Keep the target repo's test suite under ~10s.** The verify-and-move-on loop is the real throughput ceiling: ~4 min/PR fits ~40 PRs in 3h; a 5-min suite collapses that to 6–8. If a story will balloon the suite, file a sibling story to keep a fast subset the agent runs after each change.
- **Sequence for parallel, conflict-free branches** — additive-only, no runtime cross-dependencies, as covered in the story conventions above.

## Care rules
- **IP:** anything patentable goes to a PRIVATE repo with a statutory-clock guardrail checklist; public repos get cross-link comments only, never inventive steps.
- **Masonic / fraternal:** never encode, interpret, or reveal any oath / ritual / secret content. Only neutral, public-history governance abstractions (rotating chair; Apprentice / Fellow / Master tiers) are allowed, plus a guardrail directive that forbids agents from ingesting ritual content.
