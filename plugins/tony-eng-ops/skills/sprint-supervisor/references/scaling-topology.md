# Scaling topology — multiple supervisors

This reference is for when the user has grown beyond a single twingrid (18 panes) and wants to run multiple supervisors in parallel, each scoped to a topic-coherent slice of grids.

## When to scale up

Rough heuristic for when one supervisor stops being enough:

| Topology | Pane count | Recommended supervisors |
|---|---|---|
| Single grid (1× 3×3) | 9 | 1 |
| Twingrid (2× 3×3) | 18 | 1 |
| Triplegrid (3× 3×3) | 27 | 2 |
| Triplegrid wide (3× 3×4) | 36 | 2-3 |
| Quadgrid (4× 3×3) | 36 | 3 |
| Quadgrid wide (4× 3×4) | 48 | 3-4 |

The bottleneck isn't model context — it's **time per cycle**. A single supervisor needs to capture-pane on each target and apply the rubric. At ~18 panes per cycle this fits comfortably in 240s with cache warm. Past ~30 panes you start running long enough that you miss stalls and the cache cools between cycles.

## Topology examples

### Twingrid (single supervisor — default)

```
Manager (0:0)
├── twingrid-a (9 panes)
└── twingrid-b (9 panes)

Supervisors:
└── default → watches manager + twingrid-a + twingrid-b
```

Invocation: `/sprint-supervisor`

### Triplegrid (two supervisors, split by topic)

```
Manager (0:0)
├── twingrid-a (9 panes) — consensus + smart-contracts
├── twingrid-b (9 panes) — core4 + infra
└── twingrid-c (9 panes) — backend + frontend

Supervisors:
├── consensus     → watches manager + twingrid-a
└── application   → watches manager + twingrid-b + twingrid-c
```

Invocations (in separate Claude sessions):
```
/sprint-supervisor consensus --targets twingrid-a
/sprint-supervisor application --targets twingrid-b,twingrid-c
```

Why this split: consensus/smart-contracts panes generate fewer but heavier prompts (contract deploys, state migrations) and benefit from a dedicated supervisor that doesn't get distracted by application-tier churn. The application supervisor takes the high-throughput, lower-stakes traffic.

### Quadgrid (three supervisors, deep specialization)

```
Manager (0:0)
├── twingrid-a (9 panes) — consensus
├── twingrid-b (9 panes) — smart-contracts
├── twingrid-c (9 panes) — infra + backend
└── twingrid-d (9 panes) — frontend + UX

Supervisors:
├── consensus       → watches manager + twingrid-a + twingrid-b
├── infra-backend   → watches manager + twingrid-c
└── frontend        → watches manager + twingrid-d
```

Invocations:
```
/sprint-supervisor consensus --targets twingrid-a,twingrid-b
/sprint-supervisor infra-backend --targets twingrid-c
/sprint-supervisor frontend --targets twingrid-d
```

The manager is watched by **all three**. This is intentional — the manager is the brain, and if it stalls every supervisor needs to notice. Watching the same pane from three places is fine because they won't see open prompts simultaneously (codex shows the prompt to whoever has focus first; subsequent reads see "answered").

## Lockfile coordination

Each supervisor writes a lockfile at `/tmp/sprint-supervisor/<scope>.lock`:

```json
{
  "scope": "consensus",
  "targets": ["twingrid-a", "twingrid-b"],
  "started": "2026-05-12T22:14:03-07:00",
  "heartbeat": "2026-05-12T22:42:11-07:00",
  "exclude_panes": []
}
```

**Rules:**

1. **Refresh `heartbeat`** at the start of each cycle.
2. **Read all peer lockfiles** before scanning. Build a set `peer_owned_panes` from any peer with `heartbeat` within 15 min.
3. **Skip panes claimed by a fresher peer.** If you see a stuck pane in your scope but a peer's lockfile says they own it, log it and move on. The peer will handle it.
4. **Always watch `0:0` (the manager)** regardless of peer claims.
5. **Stale lockfile (>15 min old heartbeat)** = abandoned. Ignore it for ownership purposes and surface it in your next response: "Peer supervisor `consensus` has gone stale (last heartbeat 23 min ago). Should I take over its scope or wake the other session?"
6. **On exit, delete your lockfile.** `rm -f /tmp/sprint-supervisor/<scope>.lock`.

**Conflict resolution (overlap on startup):** if two supervisors claim overlapping targets, the one with the **earlier `started`** timestamp keeps the overlap. The later one drops the conflicting targets and notes it. Deterministic, no negotiation needed.

## Topic specialization — what changes per scope

The rubric is the same across all scopes — codex prompts look the same whether they're from a consensus pane or a frontend pane. What changes per scope:

1. **Morning summary scope** — each supervisor reports only on its slice. The first supervisor to report covers the shared manager state; the rest skip that section.
2. **Refusal sensitivity** — a `consensus` supervisor should be **extra strict** about smart-contract deployment commands (more frequent escalation, lower threshold for "I'm not sure"). A `frontend` supervisor can be more permissive about CSS/asset changes. Both inherit the base refusal list; specialization just shifts the discretionary "anything else" cases.
3. **Escalation triggers** — `>8 stuck panes` is the default. For a 9-pane scope, lower it to `>5`. Scale linearly with scope size.

## Naming conventions

Pick scope names that:
- Match the topic the user uses in conversation (`consensus`, `infra`, `frontend` — not `supervisor-a`, `supervisor-b`).
- Are valid as filename fragments (no spaces, no `/`).
- Make sense in the morning summary: "From the `consensus` supervisor:" reads better than "From the `sup1` supervisor:".

## When NOT to add another supervisor

- **Your existing supervisor is keeping up.** Cycle time well under 240s, no missed stalls — adding a second one just creates lockfile coordination overhead with no benefit.
- **The user is awake.** Multiple supervisors only matter when nobody's watching. If the user is at the keyboard, one supervisor handling everything (or no supervisor at all) is simpler.
- **Just to "be safe."** Each supervisor burns model budget per cycle. Don't run a quadgrid setup if you have a triplegrid.
