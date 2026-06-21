# Flywheel Operating Model

**Origin capture:** tonykoop/claude-skills#404 (2026-06-20)

## The flywheel

A self-sustaining loop where each stage amplifies the next:

```
(1) Infrastructure
         ↓  (compute + quotas)
(2) Overnight R&D / Code loops
         ↓  (new skills, fixes, features)
(3) Content creation (8-channel studio pipeline)
         ↓  (episodes, data, audience signals)
(4) Knowledge / metrics → refine infrastructure
         ↑__________________________________|
```

Each rotation of the flywheel produces:
- **Skills and automation** from the code loop
- **Published content** from the studio pipeline
- **Data and metrics** that feed back into infrastructure decisions
- **Token budget efficiency** as each loop tightens the hand-offs

## Three tuning levers

### 1. Eliminate friction (webhook hand-offs)
The highest-friction point is the gap between the coding loop finishing overnight work and the studio pipeline picking it up. Every manual step in this gap is friction. Goal: a webhook or dispatch file that wakes the media pipeline automatically when the coding loop pushes new content or skills.

**Current implementation:** StudioPipeline Daily Brief (SP2) — closes this gap with an automated morning dispatch.

### 2. Maximize leverage (cross-pollinate shared context)
Coding agents and media agents work in different repos but share knowledge: instrument designs appear in both the instrument-maker skill and the @InstrumentMaker channel. The more the agents share context (via qmd retrieval, shared manifests, cross-repo Refs), the less redundant work each loop produces.

**Current implementation:** qmd retrieval layer (15 collections) + shared `manifest.yaml` + `capstone-manifest.json` per repo.

### 3. Govern the token economy (quota governor)
Every provider (Anthropic, OpenAI, Gemini) has a rate/quota window. Exhausting a window mid-loop stalls the flywheel. The governor valve monitors usage and throttles dispatch when a provider is near its window.

**Current implementation:** StudioPipeline Fleet Command Center (SP1) — dashboards quota state.

## The four real epics (from this lens)

| Flywheel stage | Epic | Goal |
|---------------|------|------|
| Infrastructure | wrfcoin/infra N5 homelab (IN1) | Persistent compute + persistent quotas |
| Code loops | claude-skills CS1 + autoresearch AR1 | Overnight R&D without human handoff |
| Quota governor | StudioPipeline Fleet Command Center (SP1) | No mid-loop quota stalls |
| Hand-off automation | StudioPipeline Daily Brief (SP2) | Zero-friction coding-loop → media-pipeline transition |

## Using this model in idea-incubator prioritization

When Tony asks "what should I build next?" — apply the flywheel lens:

1. Is the friction at the coding → media hand-off? → Prioritize SP2 / webhook automation
2. Is the constraint quota exhaustion? → Prioritize SP1 governor / rate-aware dispatch
3. Is the bottleneck shared context? → Prioritize qmd indexing / cross-repo manifest work
4. Is it raw compute? → Prioritize N5 homelab / secondary account rate buckets

The flywheel model collapses "everything is important" into "what is the slowest spoke right now?"

## Source

> "this is my flywheel effect ... how can I turn this into my flywheel effect more efficiently and effectively self sustaining flywheel"
> — Tony (Automating Overnight Dev with loops.md, Gemini conversation, 2026-06-20)
