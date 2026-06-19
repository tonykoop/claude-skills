# Provenance — AI-HWE Workflow Brainstorm v2 (Gemini, 2026-06-13)

Provenance anchor and spawned-issue index for the **AI-HWE workflow
benchmarking** brainstorm. Resolves [claude-skills#207](https://github.com/tonykoop/claude-skills/issues/207).

This is the durable record of where the ~24 golden ideas from that conversation
landed after triage against the existing MakerBench-HWE backlog, so any future
reader can trace an idea from raw capture → filed issue → repo, and so the same
brainstorm is never re-triaged from scratch.

## Source

| Field | Value |
|---|---|
| Source | Gemini conversation (48 messages), clipped to Obsidian |
| Date | 2026-06-13 |
| Original | `C:\Users\Tony\Documents\Second_Brain\Clippings\ai hwe workflow brainstorm v2.md` |
| Capture issue | [#207](https://github.com/tonykoop/claude-skills/issues/207) |

## Triage outcome

~24 candidate ideas were triaged against the existing MakerBench-HWE backlog
(Epic `tonykoop/makerbench-hwe#100`, already holding #87–#99 and #81–#83). Ideas
that overlapped an open item became cross-link comments; genuinely-missing ideas
were filed as new issues across **four homes**, indexed below.

## Spawned-issue index

### `tonykoop/makerbench-hwe` — backlog gaps filed

| Issue | Title | Note |
|---|---|---|
| #103 | GD&T + STL + CNC G-code deliverable contract | unsent reply, pt 1 |
| #104 | per-run `explorer.html` + cross-run `library.html` navigation | unsent reply, pt 2 |
| #105 | video / screen-recording submission contract | top interest |
| #106 | gamified HII badges (L0/L1/L2) | |
| #107 | Inspect-a-Run 3D viewer | |
| #108 | Delta-Dossier regression tracker | |
| #109 | `.mbc` certificate | |
| #110 | domain expansion (casting / robotics / glass-ceramics) | |
| #111 | `docs/REASONING_BUCKETS.md` (five reasoning buckets) | |
| #112 | Physical Verification Track (Alpha/Beta/Production multipliers + makerspace) | |
| #113 | community ops layer (r/HardwareAI) | |
| #89 | Autonomy Ratio metric | filed as a comment on #89 |

### `StudioPipeline/hwe` — new repo (the build-now plugin)

The "build now" dogfood plugin competing with Fable+Fusion+Adam.

| Issue | Title |
|---|---|
| Epic #6 | StudioPipeline/hwe tracking epic |
| #1 | Blender MCP driver |
| #2 | session recorder |
| #3 | WorkflowManifest / `.mbc` |
| #4 | packet exporter |
| #5 | run-nav + MakerBench submission |

### `tonykoop/claude-skills` (idea-incubator) — big-think captures

| Issue | Title |
|---|---|
| [#204](https://github.com/tonykoop/claude-skills/issues/204) | Koop's Law — Adaptive Manufacturing Scaling Law |
| [#205](https://github.com/tonykoop/claude-skills/issues/205) | Planetary Element Inventory + Manufacturing Capability Index |
| [#206](https://github.com/tonykoop/claude-skills/issues/206) | Evolution Pipeline plugin (prototype → finished-good PLM/DFM) |

### `wrfcoin/wrfatlas`

| Issue | Title |
|---|---|
| #1 | CE_total extraction-siting engine + AI mitigation targets |

## Next step (per the capture)

Build `StudioPipeline/hwe#1` (Blender MCP driver) — the first runnable slice of
the dogfood loop. That work lives in the external `StudioPipeline/hwe` repo and
is out of scope for this provenance anchor, which only records the mapping.

## Why this file exists

A captured brainstorm whose spawned issues live only in the issue body is a
provenance record one edit away from rotting. Committing the index as a
versioned file under `docs/provenance/` makes the brainstorm → issues → repos
trace durable, greppable, and reviewable alongside the rest of the repo, and
gives the four target repos a single canonical back-reference.
