> **Status: Speculative / Far-Future** — vision capture only, not a build plan.

# Self-Assembling Personal Apps

Personal software should compile from stated intent, do its job, and dissolve — leaving only data and a record of what was built. The era of installing monolithic applications ends when a local agent can synthesize a task-specific micro-app on demand and tear it down afterward, persisting nothing but the artifact and a re-instantiation blueprint.

## The Three-Layer Model

Every personal micro-app traverses three layers before it executes:

| Layer | Role | Example |
|---|---|---|
| **Translation** | Converts natural-language intent into a structured task graph | "Help me memorize the B-section of this tune" → task spec with session type, repetition count, feedback mode |
| **Execution** | Assembles runtime components (UI widget, audio engine, data bindings) to fulfill the task graph | Spawns a flash-card loop with waveform playback, fingering overlay, and a spaced-repetition scheduler |
| **Deployment** | Selects the right host surface (local process, browser tab, system tray widget, AR overlay) and tears it down cleanly when done | Runs in Electron sandbox; on close, writes session summary to the context graph and purges the temp UI |

The layers are stateless with respect to each other. Execution does not need to know how intent was translated; Deployment does not need to know what components were assembled.

## On-Demand Composition

A micro-app is not a template instantiation — it is a composition of reusable capability modules:

- **Sensor modules**: microphone, camera, file system, MIDI, CoreAudio tap
- **Cognitive modules**: pitch detection, rhythm alignment, spaced-repetition scheduling, text classification
- **Presentation modules**: canvas widget, floating HUD element, timeline scrubber, AR anchor
- **Integration modules**: write to context graph, emit to webhook, sync to calendar

The agent selects the minimum set of modules that satisfies the task spec, wires them together with a thin orchestration manifest, and renders that manifest into a live process. Module interfaces are versioned contracts; swapping one module (e.g. a different pitch-detection engine) requires no change to the orchestration manifest.

## Lifecycle: Instantiate, Run, Dissolve

```
User expresses intent
      │
      ▼
Translation layer produces task spec
      │
      ▼
Execution layer selects + wires modules
      │
      ▼
Deployment layer starts sandboxed process
      │
      ▼
User interacts with micro-app
      │
      ▼
On exit: session data → Context Graph
         blueprint   → Blueprint Store
         process     → terminated, temp files purged
```

The only durable artifacts are:
1. **Session data** — what happened (notes practiced, errors made, time spent)
2. **Blueprint** — the re-instantiation recipe (task spec + module selection + wiring manifest)

If the user asks "start another session like last week's," the agent retrieves the blueprint, re-runs the Execution and Deployment layers, and launches an identical micro-app in seconds.

## Persistent Local Context Graph

Across all micro-apps and sessions, a single local graph accumulates structured knowledge about the user's activities, preferences, and goals. It is the memory layer that makes personal apps feel coherent rather than isolated.

### Node types

| Node type | Example |
|---|---|
| `entity:skill` | Music/NAF/B-pentatonic, Music/Piano/chord-voicing |
| `entity:artifact` | SheetMusic/Greensleeves, Recording/practice-2026-06-22 |
| `entity:goal` | Goal/learn-scotland-the-brave-by-july |
| `event:session` | Session/2026-06-22T19:30 with performance metrics |
| `concept:topic` | Topic/spaced-repetition, Topic/MIDI-mapping |

### Edge types

| Edge | Meaning |
|---|---|
| `practiced` | session → skill |
| `improved` | session → metric (with delta) |
| `contributed_to` | session → goal |
| `derived_from` | micro-app → blueprint |
| `cross_domain` | skill → entity in another domain (e.g. "practicing this piece waters the bonsai tracker") |

### Query examples

- "What did I work on most this month?" → aggregate `practiced` edges by weight
- "Am I on track for my July goal?" → traverse `contributed_to` → `goal` and compare projected vs required pace
- "Show me everything connected to Greensleeves" → subgraph centered on `entity:artifact/SheetMusic/Greensleeves`

The graph lives in a local SQLite database. No cloud sync unless the user explicitly exports. The agent reads and writes it through a typed schema; raw SQL is never exposed to user-facing queries.

## Concrete Example: Interval Training App

A user says: "I want a ten-minute ear-training drill focusing on minor sixths."

1. **Translation**: `{ type: "ear-training", interval: "minor-sixth", duration: 600s, feedback: "immediate" }`
2. **Execution**: wires `sensor:microphone` + `cognitive:pitch-detection` + `cognitive:interval-classifier` + `presentation:flash-card-with-audio`
3. **Deployment**: launches a floating HUD widget; on completion writes `{ session, interval_accuracy: 0.72, errors: [...] }` to Context Graph and dissolves

Next time the user asks "how am I doing with minor sixths?" the agent queries the Context Graph for all interval-training sessions with `interval: "minor-sixth"` and returns a trend.

## Related Captures

- [ui_states.md](ui_states.md) — how micro-apps present themselves across Studio / HUD / AR surfaces
- [model_agnostic.md](model_agnostic.md) — which inference model drives Translation and Execution
- [local_devops.md](local_devops.md) — rollback and regression guard for evolving blueprints
- [blind_spot_engine.md](blind_spot_engine.md) — the engine that discovers missing micro-apps before the user asks
