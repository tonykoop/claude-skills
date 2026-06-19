# Humanoid Maker-Team — shared episodic memory + cross-embodiment task-switching

A forward-looking design sketch for [claude-skills#232](https://github.com/tonykoop/claude-skills/issues/232).
Status: **capture / far-horizon.** The issue was captured for the inbox as "not
yet scoped work"; this doc is the first scoping pass — it turns the raw vision
into named components, a data model, and open questions, without claiming any of
it is built. Companion to the Koop's Law (#204) / Capability Index (#205)
concept docs.

## The vision in one line

A solo maker runs a team of humanoid robots on the Maker Bench, fused with
long-context foundation models so they are workshop co-keepers — not stateless
cog-turners chained to one station.

## Three pillars (the issue's three ideas, scoped)

### 1. Shared episodic memory loop

The robots share a **localized multi-modal long-context vector store** that acts
as the studio's collective memory and chronological build timeline. Robot A
3D-scans an inlay block Tuesday; Robot B recalls that exact geometric profile
Wednesday to route the matching pocket.

A first-pass record schema for one memory entry:

```yaml
episode_id: 2026-06-19T14:03Z-robotA-scan-inlay-07
actor: robotA                 # which embodiment produced it
project: zither-build-12
timeline_index: 47            # monotonic position in the build timeline
modality: [point_cloud, rgb, force]   # multi-modal payload kinds
artifact_ref: scans/inlay-07.ply
geometry_digest: <hash of the canonicalized geometry>  # the recall key
intent: "scanned inlay block to derive matching pocket profile"
embedding_ref: vec://studio-memory/  # vector handle for similarity recall
provenance: { tool: hand-scanner-3, operator: robotA, verified: false }
```

`geometry_digest` + `embedding_ref` are the load-bearing fields: they make a
later "find the geometry I scanned for this project" query a vector lookup, not
a human hunt. `timeline_index` is what lets the team reason about *when* in the
build something happened (the chronological understanding the issue calls for).

### 2. Long-horizon planning (the narrative arc)

Hand a robot a rough sketch ("let's build a custom zither today") and the planner
expands it into a **multi-day dependency tree** held in active context. Sketch of
the plan node:

```yaml
goal: build-custom-zither
nodes:
  - id: mill-soundboard
    depends_on: [select-stock, scan-stock]
    embodiment_skills: [cnc-milling]
    est_block: 2026-06-20-AM
  - id: route-inlay-pocket
    depends_on: [mill-soundboard, scan-inlay-07]   # cross-actor dependency
    embodiment_skills: [cnc-milling, vision-grain-inspection]
```

The plan references episodic-memory entries by id (e.g. `scan-inlay-07`), so the
two pillars compose: the planner schedules around what the team has already
sensed and built. Global project state is the dependency tree plus the open
frontier of ready nodes.

### 3. Cross-embodiment skill-switching (anti-boredom)

One humanoid "brain" holds weights/adapters for multiple task families and
switches modes mid-episode: bandsaw rough-cut → vision-language grain inspection
→ tweak its own CAD table to compensate for a knot → delicate camera-slider work.
The design implication is a **skill registry** the brain selects from per node:

```yaml
skills:
  cnc-milling:        { adapter: lora://milling-v3,   sensors: [force, position] }
  vision-grain:       { adapter: lora://grain-vlm-v2, sensors: [rgb] }
  cad-compensation:   { tool: openscad-mcp,           writes: project_cad_table }
  camera-slider:      { adapter: lora://fine-motion,  sensors: [rgb, imu] }
```

## Re-engineered reward: bias toward completion

The issue's anti-"warehouse psychological prison" point becomes a reward shape:
reward the **end-to-end realization of a validated product**, not per-station
throughput, so agents develop a systemic bias toward project completion and
predictive handoffs (pre-heating the heat gun before the final terminal pin).

```
reward = w_done · completed_validated_product
       + w_handoff · predictive_handoff_quality
       - w_idle · station_lock_penalty
```

`completed_validated_product` should lean on a real verification gate (the same
discipline as the verification-gates skill) so "validated" is graded, not
asserted.

## Open questions / what makes this falsifiable-later

- **Does shared episodic memory actually beat per-robot memory** on a real
  multi-day build, or does retrieval noise dominate? Needs a build-completion
  metric to test.
- **Embedding drift across modalities** — is one shared vector space enough, or
  do point-cloud and RGB need separate indices with a join key (the
  `geometry_digest`)?
- **Skill-switch cost** — does mid-episode adapter swapping pay for itself versus
  task-batching per embodiment?
- **Reward gaming** — a completion-biased reward can incentivize cutting
  verification corners; the validation gate must be adversarial.

## Scope

Far-horizon RFC. No code — the components above (multi-modal studio memory,
dependency-tree planner, skill registry, completion-biased reward) are named so
later work has concrete handles. Natural long-term home is the robotics /
StudioPipeline ecosystem; it lives here as the scoping sketch. Ties to the civic
orchestration ethic in [#234](https://github.com/tonykoop/claude-skills/issues/234)
and the capability/limits grounding in [#205](../manufacturing-capability-index/README.md).
