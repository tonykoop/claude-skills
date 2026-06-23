> **Status: Speculative / Far-Future** — vision capture only, not a build plan.

# Decentralized Hub — P2P Agent Jams + Fork & Fuse + Firewall

Collaboration on personal apps should not require a central server. Two users should be able to co-create, remix each other's blueprints, and share context in real time using only a direct peer-to-peer connection — with a local firewall controlling precisely what leaves each device. The hub is not a cloud platform; it is a protocol running between local containers.

## P2P Agent Jams

An "agent jam" is a real-time collaborative session in which two or more users' local agents work together on a shared task, each contributing context from their own domain without either party surrendering control of their data.

### How it works

```
Alice's local container         Bob's local container
        │                               │
        └──────── WebRTC channel ───────┘
                  (direct, encrypted)

Session: "Let's build a shared ear-training drill that adapts to both our skill levels"

Alice's agent contributes:        Bob's agent contributes:
  - Alice's interval accuracy       - Bob's interval accuracy
    history (from her context graph)  history (from his context graph)
  - Her preferred session length    - His preferred interval set
  - Her current weakest intervals   - His current weakest intervals

Shared agent (neither Alice's nor Bob's):
  - Synthesizes a joint blueprint that targets both users' weak spots
  - Neither agent sends raw context graph data; each sends only
    derived summaries approved by its owner's firewall rules
```

No server is involved. The session metadata (who joined, when, what was shared) is written to each participant's local context graph. The shared blueprint, once agreed on, is stored in each participant's Blueprint Store under their own namespace.

### Technical substrate

WebRTC provides the P2P transport layer:
- **Signaling**: bootstrapped via a simple, stateless relay (a QR code scan, a short code, or a shared calendar event) — the relay carries only the session establishment handshake, not user data
- **Data channel**: all blueprint fragments and derived summaries travel over the direct WebRTC data channel, end-to-end encrypted
- **No relay after handshake**: once the P2P connection is established, the relay server is no longer involved

### Jam types

| Jam type | Description |
|---|---|
| **Co-authoring** | Both agents contribute context; synthesize a shared blueprint together |
| **Coaching** | One agent observes (read-only) and provides feedback; the other drives |
| **Mirror** | Both agents independently work on the same blueprint; diffs are reconciled at the end |
| **Relay** | Agent A hands off an in-progress session to Agent B (handoff protocol) |

## Fork & Fuse: Blueprint Remix Market

Fork & Fuse is the social layer of the marketplace: users share blueprints directly with each other, remix them, and optionally fuse improvements back.

### Fork

Forking is low-friction and always permitted (subject to the source blueprint's license):
1. User discovers a blueprint in the marketplace or receives a share link
2. "Fork" copies the blueprint into their local Blueprint Store as a new per-tenant branch (see [malleable_software.md](malleable_software.md))
3. The fork retains a `parent` pointer to the original: `parent: "ear-training-minor-intervals@1.2.0 by tonykoop"`
4. The forked blueprint is immediately editable via conversation

The fork is purely local. No server records the fork. Attribution is preserved in the blueprint's YAML, not in a database.

### Fuse

Fuse is the remix-contribution direction: a fork owner proposes that their changes be incorporated into the upstream blueprint (like a pull request, but for intent documents).

```
Bob forks Alice's blueprint: ear-training-minor-intervals@1.2.0
Bob adds: "also_test: singing_accuracy" (a singing-response mode Alice didn't have)

Bob: /fuse ear-training-minor-intervals to tonykoop

Alice receives a notification:
  "Bob proposes adding a singing-response mode to your interval drill.
   Here is the change:
   + modules_requested: [..., 'voice-recognition', 'pitch-comparison']
   + parameters: { response_mode: 'singing' }
   Accept, modify, or decline?"

Alice accepts → her blueprint gains Bob's feature; Bob receives attribution credit
```

Fuse is entirely local on Alice's side — the agent applies the diff to her blueprint and creates a checkpoint. There is no merge queue on a server.

### Remix market

The marketplace surfaces fork relationships as a graph:

- Each blueprint page shows "N forks" and links to known forks (forks that opted in to visibility)
- Forks show their `parent` and any fused changes attributed back
- The graph reveals which features have been most commonly added via fork (signals what the upstream might absorb)

## Local Context Firewall

The firewall is the user's privacy enforcement layer. It sits between the local container and any outbound channel — P2P jam connections, background sync, marketplace submissions, fuse proposals — and applies per-destination rules before any data leaves the device.

### Firewall rule model

Rules are evaluated in order; the first match wins:

```yaml
firewall_rules:
  - name: "block all context graph data by default"
    match:
      data_type: "context_graph.*"
      destination: "*"
    action: deny

  - name: "allow derived summaries to P2P jam partners"
    match:
      data_type: "context_graph.derived_summary"
      destination: "p2p_jam:*"
      condition: "user_approved_session == true"
    action: allow

  - name: "allow blueprint exports to marketplace"
    match:
      data_type: "blueprint.*"
      destination: "marketplace:*"
    action: allow

  - name: "never send personal eval dataset"
    match:
      data_type: "eval:personal.*"
      destination: "*"
    action: deny

  - name: "allow aggregate accuracy stats to coaching partner"
    match:
      data_type: "context_graph.session.accuracy_aggregate"
      destination: "p2p_jam:coaching"
      condition: "partner_identity in user.trusted_contacts"
    action: allow
```

Rules are plain YAML, stored locally, editable by the user. The default ruleset blocks all context graph data except explicitly approved derived summaries.

### Zero-knowledge guarantee

The firewall enforces that the platform never transmits:
- Raw context graph nodes or edges
- Personal eval dataset entries
- Session recordings (audio / MIDI)
- OS keychain contents
- Blueprint Store contents (unless the user explicitly publishes)

Even in a P2P jam, the agent communicates only derived summaries (e.g., "this user's weakest interval set is [minor 6th, major 7th]") — never the raw session log that produced that summary.

### Firewall audit log

Every outbound request is logged locally:
```
2026-06-22T19:30Z  ALLOW  p2p_jam:alice  context_graph.derived_summary  "interval_weak_spots"
2026-06-22T19:30Z  DENY   p2p_jam:alice  context_graph.session.raw      (rule: block-all-default)
2026-06-22T19:31Z  ALLOW  marketplace    blueprint.ear-training          "ear-training-minor@1.2.0"
```

The user can review this log from the command hub at any time.

## Living Documentation Console

The living documentation console is a local timeline that records the history of the user's personal-app platform — not just what they did in apps, but how the apps themselves changed.

### What it captures

| Event type | Example entry |
|---|---|
| Blueprint install | `"Installed ear-training-minor-intervals@1.2.0 from marketplace"` |
| Deep-edit | `"Added countdown before each question (session 42 conversation)"` |
| Upstream rebase | `"Rebased to upstream v1.3.0: no conflicts"` |
| Checkpoint created | `"Milestone: session-42 personal best"` |
| Fork | `"Forked bonsai-tracker@0.9.1 from bob-gardens"` |
| Fuse accepted | `"Accepted Bob's singing-response addition"` |
| P2P jam | `"Jammed with alice (30 min): co-authored joint-interval-drill"` |
| Regression blocked | `"Blocked upgrade: minor-6th accuracy dropped 12%"` |

### Console UX

The console is accessible as a timeline in the Studio window's ambient sidebar. Each entry links to:
- The blueprint snapshot at that moment (from the local checkpoint store)
- The context graph nodes affected
- The agent conversation that triggered the event (if any)

It is read-only — a record of what happened, not an interface for making things happen.

## Related Captures

- [malleable_software.md](malleable_software.md) — per-tenant branching that fork & fuse builds on
- [blueprint_marketplace.md](blueprint_marketplace.md) — the catalog layer that fork & fuse surfaces in
- [model_agnostic.md](model_agnostic.md) — BYOK architecture that keeps inference keys off the P2P channel
- [local_devops.md](local_devops.md) — checkpoint store referenced by the living documentation console
