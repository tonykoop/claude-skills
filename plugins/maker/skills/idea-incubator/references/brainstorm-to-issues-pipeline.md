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
7. **File via the GitHub MCP:** create the epic first, then its stories, then backfill the epic's `## Stories` checklist + rollup. Use the conventions below.
8. **Post overlap cross-link comments**, then refresh routing memory.

## Issue conventions
- **Labels:** epic = `["epic","enhancement"]`; story = `["story","enhancement","sp:N"]` with `sp:N` ∈ {`sp:2`,`sp:3`,`sp:5`,`sp:8`} (Fibonacci only). Applying a missing label via the API auto-creates it. NOTE: `update_issue` REPLACES the whole label array — always pass the issue's existing labels PLUS your additions.
- **Epic body:** `**Tracking epic.** <1-paragraph summary>. Source: ` + the doc filename + ` (<source + date>).` then `## Vision`, `## Stories` (a checkbox list `- [ ] #N - <title> (sp N)`, backfilled after the children exist), `**Rollup:** ~N points.`, `## Links`.
- **Story body:** `**Story points:** N`, `## Scope`, `## Why`, `## Acceptance` (3–5 bullet criteria), `## Links` (referencing `Epic #N` + any cross-links, ending with the source citation).
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

## Care rules
- **IP:** anything patentable goes to a PRIVATE repo with a statutory-clock guardrail checklist; public repos get cross-link comments only, never inventive steps.
- **Masonic / fraternal:** never encode, interpret, or reveal any oath / ritual / secret content. Only neutral, public-history governance abstractions (rotating chair; Apprentice / Fellow / Master tiers) are allowed, plus a guardrail directive that forbids agents from ingesting ritual content.
