> **Status: Speculative / Far-Future** — vision capture only, not a build plan.

# Malleable Software + Per-Tenant Branching + Cross-Domain Integration

Software today is immutable for the user: you can configure it within the bounds the developer chose, but you cannot reshape it. Malleable software inverts this. The user is the developer — not through code, but through conversation. The app reshapes itself around the user's needs, maintains a personal branch that survives upstream updates, and reaches across domain boundaries to connect disparate parts of the user's life.

## Conversational Deep-Edit

Deep-edit is the ability to modify software behavior through natural language, with changes that persist and propagate correctly — not a chatbot overlay that forgets everything next session.

### What it means

| Level | Traditional app | Deep-edit |
|---|---|---|
| **Preferences** | Change settings in a settings panel | "Make the flash cards bigger and stop playing audio when I answer correctly" — agent updates the blueprint parameters |
| **Behavior** | Submit a feature request and wait months | "Add a 5-second countdown before each question" — agent modifies the orchestration manifest immediately |
| **Workflow** | File a bug report | "When I miss an interval twice in a row, pause and show me the interval on a staff" — agent extends the session logic |
| **Structure** | Fork the repo and maintain a divergent copy | "Split the minor-interval drill into two separate apps — one for hearing, one for singing" — agent forks the blueprint, creates two new entries in the Blueprint Store |

Every deep-edit creates a checkpoint (see [local_devops.md](local_devops.md)). The user can undo any edit by rolling back to a named checkpoint.

### What it does not mean

Deep-edit is not unconstrained code generation. The agent rewrites the blueprint and may regenerate module wiring, but it does not write arbitrary code that runs outside the sandbox. The edit surface is the blueprint schema; the execution surface remains the sandboxed module system. This keeps deep-edits auditable and reversible.

## Per-Tenant Branching (Not Forking)

A fork implies a permanent divergence — you take a copy, maintain it yourself, and drift away from the original. A per-tenant branch is different: it is a personal deviation that tracks upstream and rebases on updates automatically.

### The branching model

```
upstream blueprint: ear-training-minor-intervals@1.2.0
                          │
              ┌───────────┴───────────┐
tony's branch │ ear-training-minor-intervals@1.2.0+tony.3 │
              └───────────────────────────────────────────┘
                  personal edits:
                  - feedback_mode: "delayed" (overrides upstream "immediate")
                  - added: countdown_seconds: 5
                  - removed: "singing" module
```

When upstream publishes `@1.3.0`, the agent:
1. Applies the upstream diff to the base (`@1.2.0` → `@1.3.0`)
2. Attempts to rebase Tony's personal edits onto `@1.3.0`
3. If no conflict: branch automatically tracks the new version as `@1.3.0+tony.3`
4. If conflict: agent presents the conflict in plain language ("The upstream changed `feedback_mode` to `instant`; your branch had it as `delayed` — keep yours or accept upstream?")

This is the git model applied to intent-level documents, not code files. Merge conflicts are expressed in the user's vocabulary, not as `<<<<<<< HEAD` hunks.

### Why branching, not forking

| | Fork | Per-tenant branch |
|---|---|---|
| Relationship to upstream | Severed | Maintained |
| How updates are received | Manual copy-paste | Automatic rebase |
| User maintenance burden | High | Low |
| Creator's reach | Creator's updates don't reach forked users | Creator's updates reach all tenant branches unless overridden |

The tenant branch is the user's personalized view of a living upstream. The creator still ships improvements; the user still benefits from them while preserving their personal deviations.

## Cross-Domain Integration

Personal apps exist inside a shared context graph. An event in one domain can naturally trigger action in another — not through explicit integration code, but through graph traversal.

### The "practice waters the bonsai" example

This is the canonical illustrative example: a user's music practice sessions are automatically cross-linked to their bonsai care tracker.

**Setup**:
- The music micro-app writes `event:session` nodes with `practiced:skill/Music/NAF/B-section` edges
- The bonsai tracker reads `event:water` and `event:check` nodes with `care_event:bonsai/morning-light` edges
- The context graph agent applies a user-declared cross-domain rule: "Completing a full practice session counts as a watering reminder trigger for the bonsai"

**Result**:
- After a successful 30-minute practice session, the bonsai tracker automatically marks "watered today" and adjusts the next-water reminder
- The connection is visible as an edge in the context graph: `event:session/2026-06-22T19:30 → triggered → event:bonsai-watered/2026-06-22`
- The user can query "did I water the bonsai today?" from either the music app or the bonsai tracker; both see the same fact

### Cross-domain rule syntax

Cross-domain rules are declared in the context graph configuration, not in individual apps:

```yaml
cross_domain_rules:
  - name: "practice-waters-bonsai"
    trigger:
      event_type: "session"
      condition: "duration_minutes >= 25 AND accuracy >= 0.70"
    action:
      event_type: "bonsai-watered"
      target: "bonsai/morning-light"
      note: "Triggered by practice session (cross-domain)"
```

Rules are plain YAML, editable by the user, and subject to the same version-control as blueprints.

### More cross-domain examples

| Trigger domain | Triggered domain | Example rule |
|---|---|---|
| Music practice | Habit tracker | "Completing 3 sessions this week marks the 'consistency' habit" |
| Yoga session | Sleep tracker | "A yoga session after 8pm flags sleep quality correlation in the journal" |
| Reading session | Book club calendar | "Finishing a chapter writes a timestamp to the book club's shared timeline" |
| Cooking log | Grocery list | "Using the last of an ingredient auto-adds it to next week's grocery list" |

Cross-domain integration does not require two apps to "know about" each other. They both write to the context graph; the cross-domain rules are the only coordination layer.

## The User as Platform Steward

Malleable software shifts a responsibility that traditionally belongs to developers onto the user — in a way that does not require developer skills. The user decides:

- Which features exist in their instance of an app
- How their apps relate to each other
- Which upstream updates to accept and which to override
- How their personal data flows between domains

The agent is the translator between the user's natural-language intent and the underlying blueprint/context-graph machinery. The user's authority is real — not the illusion of control through preference toggles.

## Related Captures

- [blueprint_marketplace.md](blueprint_marketplace.md) — the distribution format that makes blueprints forkable
- [local_devops.md](local_devops.md) — rollback and conflict resolution for per-tenant branches
- [personal_apps.md](personal_apps.md) — the context graph that enables cross-domain integration
- [decentralized_hub.md](decentralized_hub.md) — the fork-&-fuse remix market (community-scale branching)
