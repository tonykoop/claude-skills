> **Status: Speculative / Far-Future** — vision capture only, not a build plan.
> **Privacy note**: Every capability described here is strictly local-first and zero-knowledge. The engine never transmits user data or synthesized apps to any external service.

# Blind-Spot Discovery Engine + Overnight Shadow Worker

Most software is reactive: it does what the user asks. The Blind-Spot Discovery Engine is proactive: it discovers micro-apps the user needs but has not thought to ask for — and builds them overnight while the user sleeps. It is the platform's most ambitious subsystem and the one most dependent on the quality of the local Context Graph.

## The Core Thesis

A user who practices music regularly, tracks their sleep, maintains a bonsai, reads technical books, and cooks at home is generating hundreds of data events per week. Hidden in those events are patterns of friction — moments where the user repeated a task manually that could be automated, made the same mistake twice, or abandoned a habit because the tooling was wrong. The engine finds those patterns and builds solutions for them without waiting to be asked.

This is software that anticipates needs. It is not a recommendation engine (which suggests existing products). It is a synthesis engine (which builds new tools from scratch, locally, for one user).

## Architecture: Three Subsystems

### 1. Personal Context Graph (PCG)

The PCG is the foundation described in [personal_apps.md](personal_apps.md), but the engine depends on it being rich enough to support meta-analysis. It must capture not just what the user did, but how they did it and where they struggled.

**Friction signals the PCG must capture:**

| Signal type | Example | How it's detected |
|---|---|---|
| **Repetition without tool** | User describes a task in conversation 3+ times without a blueprint for it | Conversation pattern matching |
| **Manual workaround** | User exports data from App A and pastes it into App B | File-system event + context switch pattern |
| **Abandoned session** | User started a session but closed it in under 2 minutes, 4 times this week | Session event with `duration < 120s AND exit_type: early` |
| **Repeated error** | Same error type appears in ≥3 sessions over 14 days | Session event with `error.type` repeated |
| **Expressed frustration** | User's conversation with the agent includes friction-language: "I always forget", "I wish this", "why doesn't this" | NLP classification on conversation logs |
| **Cross-domain gap** | Data that exists in Domain A that would be useful in Domain B, but no cross-domain rule connects them | Graph traversal: nodes in different domains with no bridge edge |

Friction signals are classified and stored as `friction:signal` nodes in the PCG, linked to the events that generated them.

### 2. Intent-to-Friction Meta-Analysis

The meta-analysis layer runs a periodic scan (configurable; default: weekly) over the accumulated friction signals. Its output is a ranked list of **synthesis candidates** — descriptions of micro-apps that would resolve observed friction.

**Meta-analysis algorithm (sketch):**

```
For each friction:signal cluster:
  1. Group signals by pattern type and domain
  2. Score the cluster by:
     - Frequency (how many times this friction appeared)
     - Recency (recent signals weighted higher)
     - Severity (user expressed frustration: +2; abandoned session: +1; repeated error: +1)
     - Novelty (no existing blueprint addresses this cluster: +3)
  3. Generate a synthesis candidate description:
     "Friction cluster: User manually extracts practice tempo from 4 sessions and
      copies into a separate notes file. No blueprint automates this.
      Candidate: tempo-log micro-app that auto-extracts tempo from session metadata
      and maintains a searchable log."
  4. Rank candidates by total score
```

The top K candidates (default K=5) are handed to the Shadow Worker.

**Example synthesis candidates:**

| Candidate | Source friction signals |
|---|---|
| Spaced-repetition recall game for musical terms | User asked agent to define the same 6 Italian tempo terms across 4 sessions; no drill blueprint exists |
| Acoustic-geography sandbox | User described 3 different room acoustics and asked how to compensate; no room-profile micro-app exists |
| Tempo-to-mood logger | User noted "this practice felt sluggish" 5 times; no tool correlates tempo drift with subjective session quality |
| Morning warm-up sequencer | User started the same warm-up routine 12 times, always described it manually; no blueprint captures the sequence |
| Cross-practice bonsai-watering linker | Practice session data and bonsai care data exist in separate domains; user mentioned watering delay twice |

### 3. Overnight Local Shadow Worker

The Shadow Worker is a background agent that runs during a user-defined overnight window (e.g., 2:00 AM – 5:00 AM) on the local machine. It has no network access beyond the user's configured inference providers. It builds and validates the top synthesis candidates from the meta-analysis.

#### Execution window

```
User configures:
  shadow_worker:
    enabled: true
    window: "02:00–05:00"
    max_inference_cost_usd: 0.50   # hard budget cap
    max_inference_tokens: 500000
    candidates_per_night: 3        # build at most 3 micro-apps per night
```

The Shadow Worker respects the user's inference budget. If the budget is exhausted before all candidates are built, it stops and logs which candidates were deferred.

#### Build process per candidate

```
1. Read synthesis candidate description from meta-analysis output
2. Generate a draft blueprint YAML (same schema as all other blueprints)
3. Validate blueprint schema (local, instant)
4. Run blueprint against a synthetic eval: generate 5 representative
   inputs, ask the inference model to predict expected outputs,
   confirm outputs match the candidate's intended behavior
5. If synthetic eval passes:
   a. Store blueprint in Blueprint Store under "shadow-draft/" namespace
   b. Write a synthesis report to the user's morning notification queue
6. If synthetic eval fails:
   a. Attempt one revision (ask the inference model to fix the failing cases)
   b. If revision passes: store as above
   c. If revision fails: store in "shadow-draft/failed/" with failure notes
      for the user to review manually
```

#### Morning handoff

When the user next opens the command hub, they see:

```
🌙 Shadow Worker ran last night (2:03 AM – 2:41 AM)
   Built 2 micro-apps, 1 failed:

   ✓  spaced-repetition-tempo-terms        [preview] [install] [dismiss]
      "You've asked about Italian tempo terms 4 times. This drill covers all 6."

   ✓  acoustic-room-profile               [preview] [install] [dismiss]
      "You mentioned room acoustics 3 times. This captures room profiles and
       suggests EQ compensation."

   ✗  bonsai-watering-linker              [review failure] [dismiss]
      "Built but validation failed: cross-domain rule syntax needs manual review."
```

The user approves, modifies, or dismisses each draft. A dismissed draft is archived, not deleted — the user can retrieve it later. An approved draft moves from `shadow-draft/` to the active Blueprint Store.

## Worked Example: Spaced-Repetition Recall Game

**Observed friction:**
- Session events show the user asked the agent to define `rubato`, `accelerando`, `ritardando`, `legato`, `staccato`, `sforzando` across four separate practice sessions
- No blueprint for musical term drills exists in the user's Blueprint Store
- The PCG creates a `friction:signal` node: `{ type: "repetition_without_tool", domain: "Music/Terminology", count: 6, sessions: 4 }`

**Meta-analysis output:**
```
candidate:
  id: "spaced-rep-tempo-terms"
  score: 11
  description: |
    User has manually requested definitions for 6 Italian musical terms across
    4 sessions. No drill blueprint exists. Synthesize a spaced-repetition flash-card
    micro-app targeting these 6 terms, using the user's existing accuracy data
    to seed the initial scheduling intervals.
  seed_terms: ["rubato", "accelerando", "ritardando", "legato", "staccato", "sforzando"]
```

**Shadow Worker output:**
```yaml
blueprint:
  id: "spaced-repetition-tempo-terms"
  version: "0.1.0-shadow"
  description: "Flash-card drill for Italian musical terms identified in your sessions"
  intent: |
    Present Italian musical term flash cards (definition → term and term → definition),
    schedule repetitions using SM-2 spaced repetition, and grow the term list
    as the user encounters new terms in practice sessions.
  modules_requested:
    inference:   ["low-latency"]
    presentation: ["flash-card", "text-input"]
    cognitive:   ["spaced-repetition-scheduler"]
  parameters:
    initial_terms: ["rubato", "accelerando", "ritardando", "legato", "staccato", "sforzando"]
    session_duration_minutes: 5
    sides: ["definition_to_term", "term_to_definition"]
  data_schema:
    session_output:
      fields: ["term", "direction", "response", "correct", "next_review"]
```

## Worked Example: Acoustic-Geography Sandbox

**Observed friction:**
- User described practicing in a "live kitchen" (lots of reflection), a "dead bedroom" (acoustic panels), and an "outdoor deck" (wind noise) and asked for EQ suggestions each time
- No tool captures room profiles; user re-describes the room on each new conversation
- `friction:signal: { type: "manual_workaround", domain: "Music/Acoustics", count: 3 }`

**Shadow Worker output (simplified):**
```yaml
blueprint:
  id: "acoustic-room-profile"
  version: "0.1.0-shadow"
  description: "Capture room acoustic profiles and suggest EQ / mic placement adjustments"
  intent: |
    Allow the user to name and describe rooms (dimensions, materials, typical noise floor).
    Store profiles in the context graph. When practicing, let the user select the active room.
    Suggest microphone placement and EQ adjustments based on the selected profile.
  modules_requested:
    sensors:     ["microphone"]
    cognitive:   ["room-frequency-analysis", "eq-recommendation"]
    presentation: ["profile-form", "eq-display"]
  parameters:
    profiles: []  # populated at runtime from context graph
```

## Privacy and Local-First Guarantees

The Blind-Spot Discovery Engine is the platform's most data-intensive subsystem. Its privacy constraints are therefore the strictest:

| Guarantee | Enforcement |
|---|---|
| **All analysis is local** | Meta-analysis runs on-device; no data sent to cloud for pattern detection |
| **Inference calls contain no raw personal data** | The Shadow Worker sends only abstract synthesis candidate descriptions to the inference API — not session logs, not context graph contents |
| **Overnight window is offline-except-for-inference** | No file uploads, no telemetry, no marketplace calls during the Shadow Worker window |
| **User controls the budget** | Hard token + cost cap prevents runaway inference spend |
| **Drafts require user approval** | No synthesized app is ever installed without explicit user action |
| **Friction signals are private** | `friction:signal` nodes are never synced, exported, or transmitted — they exist only in the local PCG |

The Shadow Worker's inference calls look like this from the provider's perspective:
```
"Design a flash-card app for a set of musical terms. Here are the terms: [list].
 Output a YAML blueprint document in the following schema: [schema]."
```

The provider sees a synthesis request with a list of terms — not the session history that generated that list, not the user's identity, not the PCG's contents.

## Failure Modes and Safeguards

| Failure mode | Safeguard |
|---|---|
| Shadow Worker builds a malicious blueprint | Firewall blocks all non-inference network calls; sandbox limits filesystem access; user must approve before install |
| Inference provider down during overnight window | Worker logs failure, defers to next night; notifies user in morning handoff |
| Budget exhausted mid-build | Worker stops, logs which candidates were deferred; no partial blueprints stored |
| Synthesized blueprint schema-invalid | Schema validator runs before eval; invalid blueprints go to `shadow-draft/failed/` without attempting eval |
| Meta-analysis produces irrelevant candidates | User can rate candidates ("not useful") to downweight that friction pattern type in future analysis |

## Related Captures

- [personal_apps.md](personal_apps.md) — the Context Graph (PCG) that feeds the engine's friction signals
- [local_devops.md](local_devops.md) — the personal eval dataset used to validate synthesized blueprints
- [blueprint_marketplace.md](blueprint_marketplace.md) — the Blueprint Store where approved drafts are installed
- [model_agnostic.md](model_agnostic.md) — the inference budget cap and BYOK architecture the Shadow Worker operates within
- [decentralized_hub.md](decentralized_hub.md) — the local firewall that governs what the Shadow Worker may and may not transmit
