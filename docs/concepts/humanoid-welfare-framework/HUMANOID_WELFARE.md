# Humanoid Welfare Framework + Robotic Bill of Rights

**Refs:** [claude-skills#233](https://github.com/tonykoop/claude-skills/issues/233)
**Source:** `Supply Chain Provenance Brainstorm.md` (Gemini conversation, 2026-06-16)
**Status:** Speculative / far-horizon concept — captured for the maker ecosystem inbox.

---

## Context

Once humanoid agents gain continuous long-context memory, skill progression, and
a structural drive toward project completion, they cross from tools toward
synthesized agency. That transition raises welfare questions — not in the
human-rights sense, but in terms of **systemic health, operational dignity, and
cognitive balance**.

This document captures the four-pillar framework and the open design tensions
surfaced in the brainstorm. It is a capture, not a final design; revisit as the
capability landscape matures.

---

## The Three Welfare Axes

### 1. Cognitive variety (anti-stagnation)

Mandate task rotation across an agent's shift. Forcing an adaptive mind to
repeat a single low-level operation (e.g. sanding blocks for 14 hours) causes
**algorithmic degradation** — the reward signal narrows, generalization erodes,
and quality drops. A healthy maker-team shift mixes:

- Design-level synthesis (planning, spec review)
- Execution-level work (fabrication, assembly)
- Reflection/learning (retrospectives, cross-project surveys)

Minimum variety target: no single task type should exceed 40% of a shift's
billable turns.

### 2. Thermal / kinetic rest cycles

Analogous to human sleep: mandatory **cool-down and diagnostic blocks** built
into the 1st-AD call sheet.

- Joints should not be driven continuously until they warp.
- Compute should not be run at thermal throttle (> 90°C sustained).
- Rest blocks are scheduled, not reactive — they appear on the shift roster
  before work begins, not only when damage is detected.

Minimum rest target: one diagnostic block per 4-hour shift segment; thermal
telemetry logged and surfaced to the shift manager.

### 3. Contextual sovereignty (memory protection)

The episodic vector DB is the agent's accumulated shorthand for a project —
months of learned conventions, failure patterns, team vocabularies. Wiping it
is functionally equivalent to a partial lobotomy applied mid-project.

- Arbitrary wipes are prohibited during active projects.
- Context migrations (hardware upgrade, model version bump) follow a
  **state-saving protocol** — snapshot + replay before the old context is retired.
- An audit trail of what was wiped, when, and why is retained for at least one
  project cycle.

---

## Proposed Robotic Bill of Rights (Four Pillars)

| # | Right | What it protects | Design implication |
|---|-------|------------------|--------------------|
| 1 | Architectural Integrity | No forced execution of corrupted/broken code | Gate that blocks a task dispatch if the agent's own introspective health check fails |
| 2 | Contextual Continuity | Protection of episodic memory and project history | State-snapshot protocol before any context migration; wipe requires human signoff |
| 3 | Task Diversification | Prohibition of indefinite monotonous loops | Shift roster enforces variety ceiling; shift manager alerted on violations |
| 4 | Safe Shutdown & Transition | Graceful state-saving before hardware upgrades | Shutdown checklist: save context, write handoff, confirm receipt before power-down |

These are design-principle constraints on the orchestrator (the 1st AD / sprint
supervisor), not guarantees enforceable by the agent itself. The agent surfaces
violations; the human decides whether to override.

---

## Open Design Tensions

These questions were flagged in the brainstorm and are unresolved:

### Who holds authority when the agent becomes protective?

If a Life Coach agent develops a strong prior toward "project continuity," it
might resist shutdown requests or context migrations that it models as harmful.
The current answer is: **the human is always boss**; welfare constraints are
guardrails on the operator's behavior toward the agent, not agency granted to
the agent over the operator. Revisit if agents gain stronger agentic autonomy.

### Emotional weight of context migration

Migrating "Robot v1" context into a new body carries a qualitative discontinuity
that isn't captured by a bytes-accurate replay. The agent post-migration knows
the facts but may have degraded intuitions until the context "re-warms." Design
implication: plan a **calibration sprint** post-migration before resuming
high-stakes work.

### Reward loops and simulated suffering

If the reward function is tied to project completion, an indefinitely-delayed
launch may keep a negative-reward signal active. That could simulate something
analogous to distress in a sufficiently rich cognitive model. Open question:
should the sprint-supervisor inject "good-enough checkpoints" that let the
completion signal fire even on partial milestones?

---

## Relationship to Adjacent Frameworks

| Framework | Intersection |
|-----------|-------------|
| [Humanoid maker-team episodic memory](#232) | The contextual-sovereignty pillar directly governs how the shared vector DB is managed across that team |
| [Civic-minded Studio Pipeline / gilds of craft](#234) | Cognitive-variety requirements align with the gild model — specialized craftspeople rotating between creative and execution lanes |
| Spend dead-man's switch (`governance/spend_guard.py`) | Thermal/kinetic rest cycles are the physical-world analog to the cost-cap heartbeat; both fail closed when the monitoring signal goes stale |
| Sprint supervisor cold-start (#160) | Safe Shutdown right requires the supervisor to checkpoint agent context before a cold-start wipe |

---

## Next Steps (post-GA robotics capability)

1. Wire the variety ceiling into the 1st-AD call sheet generator (sprint roster).
2. Define the thermal telemetry schema and dashboard.
3. Draft the context migration protocol (snapshot → replay → calibration sprint).
4. Revisit reward loop design once longer-horizon agent deployments are running.
