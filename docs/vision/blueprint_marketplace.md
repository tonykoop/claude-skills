> **Status: Speculative / Far-Future** — vision capture only, not a build plan.

# Next-Gen App Store / Blueprint Marketplace

The app store of the future does not distribute binaries. It distributes **blueprints** — structured intent specifications that a local agent compiles into running software on the user's machine. Blueprints are readable, forkable, remixable, and self-healing. The marketplace is a catalog of blueprints, not a repository of executables.

## Blueprints vs. Binaries

| Attribute | Traditional binary app | Blueprint |
|---|---|---|
| **Distribution unit** | Compiled executable or package | Structured text document (JSON / YAML) |
| **Execution model** | Run on target OS directly | Compiled to a micro-app by the local agent at install time |
| **Update mechanism** | Download new version, replace binary | Receive updated blueprint; agent recompiles locally |
| **OS compatibility** | Must target each platform explicitly | Agent handles platform adaptation |
| **Readability** | Opaque to users | Human-readable; user can inspect and edit |
| **Malware surface** | High (arbitrary code in binary) | Low (blueprint is data, not executable; agent is the only executor) |
| **Forking** | Fork = copy source repo | Fork = duplicate and modify blueprint text |

A blueprint is a declarative document, not a program. It says what the app should do, not how to do it. The local agent reads the blueprint and decides how to implement it given the user's available modules, model capabilities, and device configuration.

## Blueprint Schema (Sketch)

```yaml
blueprint:
  id: "ear-training-minor-intervals"
  version: "1.2.0"
  author: "tonykoop"
  license: "CC-BY-4.0"
  description: "Spaced-repetition drill for minor intervals (2nd, 3rd, 6th, 7th)"

  intent: |
    Present audio examples of minor intervals, prompt the user to identify them,
    give immediate feedback, and schedule future repetitions based on recall accuracy.

  modules_requested:
    inference:   ["low-latency"]
    sensors:     ["microphone", "voice-recognition"]
    cognitive:   ["spaced-repetition-scheduler", "pitch-detection"]
    presentation: ["flash-card", "audio-playback", "score-display"]

  parameters:
    session_duration_minutes: 10
    intervals: ["minor-2nd", "minor-3rd", "minor-6th", "minor-7th"]
    feedback_mode: "immediate"

  data_schema:
    session_output:
      fields: ["timestamp", "interval_presented", "user_response", "correct", "latency_ms"]

  context_graph_writes:
    - node: "event:session"
      edges: ["practiced:skill/Music/Intervals/minor"]
```

The schema is intentionally minimal. The agent fills in everything not specified using defaults and user preferences from the context graph.

## Sandboxed Execution

Blueprints run in a sandboxed subprocess managed by the local container. The sandbox enforces:

| Constraint | Mechanism |
|---|---|
| **Filesystem scope** | Access only to user-approved directories; no system paths |
| **Network scope** | Only the inference provider endpoints listed in the user's registry |
| **Process isolation** | Separate process with no shared memory with other micro-apps |
| **No persistent background code** | Process exits when the session ends; no daemons |
| **Audit log** | Every filesystem read/write and network call is logged locally |

Because blueprints are data (not code), the risk surface is the agent + the module implementations, not the blueprint itself. A malicious blueprint can declare malicious intent, but the user's agent (subject to the user's review) is the one that decides whether to execute it.

## Self-Healing on OS Update

Traditional apps break when the OS changes an API, moves a framework, or removes a deprecated feature. Blueprint apps do not, because the binary is never cached — the agent recompiles from the blueprint on every launch.

When the OS updates:
1. The module registry detects that a module's underlying dependency changed
2. On next launch, the agent re-resolves the `modules_requested` declarations against the updated registry
3. If the original module is unavailable, the agent selects the closest compatible substitute and logs the substitution
4. The user sees the app launch normally; the substitution note appears in the session log if relevant

Self-healing works because blueprints describe intent, and the agent can translate intent into different technical implementations. A blueprint that requests `"audio-playback"` does not care whether the underlying implementation uses AVFoundation, Web Audio API, or SDL2 — that is the agent's concern.

## Publish and Monetize

The marketplace enables creators to publish blueprints and, optionally, earn from them.

### Publication flow

```
1. Creator authors a blueprint locally
2. Creator runs: /publish blueprint <blueprint-id>
3. Agent validates blueprint schema, checks for obvious malicious intent patterns
4. Agent packages blueprint + metadata + preview session recording
5. Package uploaded to marketplace registry (creator's chosen host)
6. Blueprint appears in marketplace search under creator's handle
```

### Monetization options

| Model | Description |
|---|---|
| **Free / open** | Blueprint is free; creator gets attribution |
| **Pay-once** | Buyer pays once; blueprint transferred to buyer's local store |
| **Subscription** | Blueprint updates stream to subscribers; creator earns monthly |
| **Tip jar** | Free blueprint with optional tip prompt after first successful session |
| **Remixable with attribution** | Fork is free; creator receives credit and optional tip on each fork's install |

Payments route through a user-controlled payment layer (Stripe, Lightning, or any payment provider the creator chooses). The marketplace does not take a platform cut by default — it is a catalog, not a gatekeeper.

### Discovery

The marketplace exposes:
- **Full-text search** across blueprint intent fields and descriptions
- **Module tag filters** (e.g., "requires microphone", "works offline")
- **Author pages** with all published blueprints
- **Remix graph** showing fork relationships between blueprints
- **Session count** (how many users have run this blueprint, with privacy preservation — counts only, no identity)

## Blueprint Store (Local)

Every installed blueprint lives in the user's local Blueprint Store — a flat-file directory, not a database:

```
~/.local/share/personal-apps/blueprints/
├── ear-training-minor-intervals@1.2.0.yaml
├── bonsai-care-tracker@0.9.1.yaml
├── morning-movement-routine@2.0.0.yaml
└── ...
```

Blueprints can be edited directly with any text editor. The agent re-reads the blueprint on next launch; no compilation step, no cache invalidation ritual.

## Related Captures

- [malleable_software.md](malleable_software.md) — how users reshape installed blueprints by conversation
- [decentralized_hub.md](decentralized_hub.md) — fork-&-fuse remix market (P2P blueprint sharing)
- [local_devops.md](local_devops.md) — rollback of blueprint edits via local version control
