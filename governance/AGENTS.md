# AGENTS.md — Front-end ↔ Back-end pipeline symmetry

> claude-skills#260 (Epic #254). Documents the dual-skill symmetry and wires it
> into the orchestrator config ([`agent-roster.yaml`](agent-roster.yaml)) so the
> front-end/back-end pipeline runs hands-off, conveyor-belt style — matching the
> orchestrator's native **department** org model rather than living in any
> agent's prompt.

## The conveyor

```
  raw text                  structured                  PR + assets               atomic
 (Telegram,                  tickets                    ready to ship           yes/no ticket
  inbox)                                                                        + human signoff
     │                          │                            │                      │
     ▼                          ▼                            ▼                      ▼
┌─────────────────────────────────┐            ┌─────────────────────────────────────────┐
│  FRONT-END                      │  GitHub     │  BACK-END                                │
│  Creative Ingestion dept        │  issues     │  Release Operations dept                 │
│  skill: idea-incubator          │ ─────────▶  │  skill: studio-release                   │
│  agent: ingestor (haiku)        │  label:     │  agent: releaser (sonnet)                │
│  heartbeat: 08:00 daily         │  idea:      │  trigger: ready-for-release /            │
│                                 │  incubated  │           asset:complete labels          │
└─────────────────────────────────┘            └─────────────────────────────────────────┘
        creates work                                   verifies work, proposes the ship
```

The two departments are mirror images: one **manufactures** tickets from raw
input on a clock; the other **inspects** finished work on an event and proposes
a single deploy decision. Neither crosses a deploy boundary on its own.

## Department mapping

| | **Creative Ingestion** (front-end) | **Release Operations** (back-end) |
| --- | --- | --- |
| Role | Manufacture: raw text → structured tickets | Inspect: PRs/assets → yes/no deploy ticket |
| Skill | [`idea-incubator`](../skills) | Studio Release Skill ([tonykoop/StudioPipeline](https://github.com/tonykoop/StudioPipeline)) |
| Operator agent | `ingestor` (`claude-haiku-4-5`) | `releaser` (`claude-sonnet-4-6`) |
| Fires on | **Heartbeat** — `0 8 * * *` (08:00 daily) | **Labels** — `ready-for-release`, `asset:complete` |
| Reads | Telegram saved messages, inbox notes | open PRs, produced assets |
| Writes | GitHub issues labeled `idea:incubated` | a ticket labeled `release:proposed` |
| Least-privilege (allow) | `github_read`, `github_issues`, `web_fetch`, `web_search` | `github_read`, `github_issues`, `asset_storage` |
| Hard deny | `github_push`, `shell`, `youtube_api`, `asset_storage` | `github_push`, `shell`, `youtube_api` |
| Can audit? | no (`can_audit: false`) | no (`can_audit: false`) |

Both deny `github_push` and `shell`: a pipeline operator **files and labels
issues, it never pushes code or runs a deploy**. That boundary is enforced by
the #259 least-privilege scopes (default-deny in `spend_guard.scope_check`),
not by convention.

## Handoff contract (front-end → back-end)

1. **Front-end emits.** On the 08:00 heartbeat, `ingestor` runs `idea-incubator`
   over the day's raw captures and files GitHub issues, each labeled
   `idea:incubated`. That label is the visible seam between the two halves.
2. **Humans/sprint promote.** An incubated idea that gets scoped and built flows
   through the normal sprint (create → cross-model audit per #256). When the
   work is shippable, a PR/asset is labeled `ready-for-release` or
   `asset:complete`.
3. **Back-end picks up.** Those labels trigger `releaser`, which runs the Studio
   Release Skill to verify the PR/assets and surface **one atomic yes/no deploy
   ticket** labeled `release:proposed` — never a partial or multi-step plan.
4. **Human signs the deploy.** The deploy itself is a *protected action*. The
   `release:proposed` ticket is gated by the #258 circuit breaker
   (`deploy_gate: circuit_breaker`): it auto-advances nothing across the
   boundary; a human signature is mandatory. The back-end proposes; the human
   disposes.

```
idea:incubated ──(scoped, built, #256-audited)──▶ ready-for-release / asset:complete
              ──(studio-release verifies)──▶ release:proposed ──(#258 human signoff)──▶ ship
```

## Heartbeat & label triggers (config)

Wired in [`agent-roster.yaml`](agent-roster.yaml) under `pipeline:`:

```yaml
pipeline:
  front_end:
    department: creative-ingestion
    agent: ingestor
    skill: idea-incubator
    heartbeat: "0 8 * * *"            # 08:00 daily morning intake
    inputs: [telegram_saved_messages, inbox_notes]
    emits_label: "idea:incubated"
  back_end:
    department: release-operations
    agent: releaser
    skill: studio-release
    triggers_on_labels: ["ready-for-release", "asset:complete"]
    emits_label: "release:proposed"
    deploy_gate: circuit_breaker
```

| Hook | Front-end | Back-end |
| --- | --- | --- |
| Schedule | cron `0 8 * * *` (heartbeat) | event-driven (label add) |
| Trigger labels (in) | — | `ready-for-release`, `asset:complete` |
| Emitted label (out) | `idea:incubated` | `release:proposed` |
| Boundary | files issues only | deploy ticket gated by #258 |

## How it sits in the governance layer

| Concern | Enforced by | Applies to the pipeline as |
| --- | --- | --- |
| What each lane may touch | #259 `spend_guard.scope_check` | `creative-ingestion` / `release-operations` allow/deny lists |
| Never self-audit built work | #256 `review_router` | the build step between the two halves |
| No unattended deploy | #258 `circuit_breaker` | `release:proposed` → human signature required |
| Runaway spend | #259 `spend_guard` ledger | per-agent caps on `ingestor` / `releaser` |

The result: raw notes become tickets every morning without a human, finished
work is inspected and proposed for release without a human — and the *only*
place a human is required is the irreversible step (the deploy signature) and
the ambiguous ~10% the circuit breaker escalates.
