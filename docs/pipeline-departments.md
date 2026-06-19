# Pipeline Department Definitions: Creative Ingestion ↔ Release Operations

Epic [#254](https://github.com/tonykoop/claude-skills/issues/254) —
Story [#260](https://github.com/tonykoop/claude-skills/issues/260)

Two departments form the front-to-back conveyor: one ingests raw ideas into
GitHub tickets; the other gates and delivers those tickets to production.
This document defines each department's role, agent mapping, heartbeat
schedule, and handoff contract.

---

## Department: creative-ingestion

**Purpose:** Morning heartbeat that turns raw text (voice memos, Telegram
dumps, Gemini brainstorms) into structured, labeled GitHub issues using the
**idea-incubator** skill.

**Skill:** `plugins/maker/skills/idea-incubator/SKILL.md`

**Heartbeat schedule:**
```
cron: "0 7 * * *"    # 07:00 daily (Pacific)
```
The heartbeat runs the idea-incubator's Intake mode against the unprocessed
capture queue (Telegram Saved Messages or a designated Obsidian inbox folder).

**Label triggers** (the heartbeat also processes on-demand when these appear):
| Trigger label | Action |
|---------------|--------|
| `needs-intake` | Run Intake mode on the labeled issue/capture |
| `brainstorm-ready` | Run full Gemini-export pipeline (gemini_to_github.py) |
| `retro-request` | Run Retrospective mode (retrospective_sweep.py) |

**Allowed tools / secrets:**
```yaml
allow_tools:  [github_read, github_push, web_search, web_fetch]
allow_secrets: [GITHUB_TOKEN]
deny_tools:   [shell, youtube_api, urdf_validate]
deny_secrets: [YOUTUBE_API_KEY, ROBOTICS_DEPLOY_KEY, STUDIOPIPELINE_TOKEN]
```

**Outputs per run:**
- One or more new GitHub issues with labels (`domain:`, `sp:N`, `wave:N`, `model:`)
- Cross-pollination opportunities comment on existing epics (when overlap found)
- Institutional Knowledge sweep artifact when retrospective mode runs

**Output label applied to each emitted issue:** `wave:0` (ready for triage)

---

## Department: release-operations

**Purpose:** Event-driven monitor that applies the **studio-release** skill to
every PR flagged `release-candidate` or asset labelled `pending-deploy`,
producing an atomic yes/no deploy ticket for human sign-off.

**Skill:** `plugins/coding/skills/studio-release/SKILL.md`

**Trigger events:**
| Event | Trigger |
|-------|---------|
| PR labelled `release-candidate` | Run studio-release gate on the PR diff |
| Issue labelled `pending-deploy` | Run studio-release gate on linked asset bundle |
| `push` to `dist/**` | Run studio-release gate if CI is green |

**No heartbeat** — release-operations is purely event-driven (no scheduled
polling). An agent monitors the `release-candidate` label queue via:
```bash
gh pr list --label release-candidate --json number,headRefName,labels
```

**Allowed tools / secrets:**
```yaml
allow_tools:  [github_read, github_push, shell, web_fetch]
allow_secrets: [GITHUB_TOKEN, STUDIOPIPELINE_TOKEN]
deny_tools:   [youtube_api, urdf_validate]
deny_secrets: [YOUTUBE_API_KEY, ROBOTICS_DEPLOY_KEY]
```

**Outputs per event:**
- A new GitHub issue of type `deploy-ticket` with a structured yes/no verdict,
  gate results (linter, compile, bundle), and a `human_signed_off: false`
  placeholder that must be manually set to `true` before any publish action.
- A review comment on the triggering PR citing the gate results.

**Output label applied to the deploy ticket:** `needs-human-signoff`

---

## Front-end ↔ Back-end Handoff Contract

```
 [raw text / Telegram]
        │
        ▼  07:00 heartbeat (creative-ingestion)
 [GitHub issue]  ← wave:0  ← domain: label  ← sp: label
        │
        │  agent grid (alice/bob/cindy/dan) implements the issue
        ▼
 [PR with linked issue, label: release-candidate]
        │
        ▼  event trigger (release-operations)
 [deploy-ticket issue]  ← needs-human-signoff
        │
        │  human sets human_signed_off: true on the ticket
        ▼
 confidence_router.check_deploy_clearance(audit) → DEPLOY_CLEAR
        │
        ▼
 [publish / push-to-main]
```

**Key invariants:**

1. `creative-ingestion` never touches production; it only writes to the issue
   inbox and does not merge PRs.
2. `release-operations` never self-approves; it produces the deploy ticket but
   cannot set `human_signed_off: true` on it.
3. The `check_deploy_clearance` gate in `governance/confidence_router.py` is
   the final mechanical barrier — exit code 1 blocks the push/publish action
   if `human_signed_off` is absent or false.

---

## Orchestrator Config (`governance/agent-roster.yaml`)

Both departments are defined under the `departments:` key so existing
governance modules (`spend_guard.py`, `review_router.py`) inherit them
automatically. See `governance/agent-roster.yaml` for the full entries.

The two agents wired to these departments:

| Agent | Department | Model | Role |
|-------|-----------|-------|------|
| `grace` | `creative-ingestion` | `claude-sonnet-4-6` | Intake + retrospective operator |
| `henry` | `release-operations` | `claude-opus-4-8` | Release gate operator |

Both agents have `can_audit: false` — they are operators, not adversarial QA
auditors. Cross-model QA for their outputs routes through the existing
`review_policy` in `agent-roster.yaml`.
