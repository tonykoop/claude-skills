---
name: sprint-update
version: 1.1.1
last-updated: 2026-05-11
description: >-
  Update the current sprint document with new merge results, persona status changes,
  and velocity stats. Use when the user says "update sprint doc", "sprint update",
  "update the sprint", or after a batch of merges to bring the sprint document current.
---

# Sprint Document Update

Update the sprint doc at `docs/plans/<date>_Sprint.md` (or the most recent sprint file).

## Read-only refresh mode

Use read-only refresh mode when the manager needs current sprint telemetry,
queue drift, or PR pressure before deciding whether to edit the sprint doc.
This mode is especially useful after a swarm or TwinGrid audit has created
issue/PR pressure that may make the existing sprint document stale.

Read-only refresh mode must not edit sprint docs, issue labels, PRs, or memory
files. It produces a manager report or patch plan with:

- current open issue count and open PR count from GitHub;
- open PR split into `ready`, `draft`, and `overlap/de-dup review` clusters;
- stale sprint count comparison, naming the sprint doc snapshot versus live
  GitHub state;
- candidate queue changes, including items to promote, defer, remove as
  duplicate/superseded, or route to Tony-decision;
- personal GitHub routing metadata from live labels: `Label`, `Model`, `Batch`,
  `risk:*`, `sprint:*`, and owner skill labels;
- validation gaps when GitHub or artifact reads fail.

Treat read-only output as manager input, not as an applied sprint update. If the
report finds `risk:ip-privacy`, welfare/safety review labels, or
`needs-clarification`, keep those items out of automatic implementation
dispatch even when they also carry `sprint:implementation-pass`.

## Sprint doc structure

The sprint doc uses **per-persona queues** (not wave tables). WRFCoin sprint
docs use the compact queue table. Personal GitHub sprint docs use the expanded
queue table with `Label`, `Model`, and `Batch` columns so agents can be routed
from one generated queue without losing triage metadata.

WRFCoin personas (Alice, Bob, Cindy, Dan, Elsa) have their own section with
three tables:

```markdown
## <Persona> — <Domain>

### Active
| Status | Issue | Repo | Description | Handoff |

### Queue
| # | Priority | Issue | Repo | Description |

### Completed
| Issue | Repo | PR | SHA | Wave |
```

Personal GitHub sprint sections use the same Active and Completed tables, but
their Queue table is:

```markdown
### Queue
| # | Priority | Label | Model | Batch | Issue | Repo | Description |
|---|----------|-------|-------|-------|-------|------|-------------|
| 1 | P1 | instrument-maker | gpt-5.5 | batch-01 | #123 | repo-name | Short task |
```

Column meanings:
- `Label`: the primary GitHub label or routing category to preserve from queue
  generation, such as `instrument`, `maker`, `capture`, or `promote`.
- `Model`: the intended runtime/model lane when known. Use `TBD` if queue
  generation has not assigned a model.
- `Batch`: the generation batch, import batch, or sprint grouping. Keep it as
  traceability metadata; do not use it as the only dispatch theme.

## What to update

If the user explicitly asked for read-only refresh, stop after the report or
patch plan. Otherwise use the same checks below and then edit the sprint doc.

### 1. Move merged items: Active → Completed

When a PR merges, move its row from the persona's **Active** table to **Completed**:

```markdown
### Completed
| Issue | Repo | PR | SHA | Wave |
|-------|------|----|-----|------|
| ~~#NNN~~ | repo | #PR | sha7 | — |
```

Get merge SHAs:
```bash
gh pr view <num> --repo wrfcoin/<repo> --json mergeCommit --jq '.mergeCommit.oid'
```

### 2. Promote next queue item: Queue → Active

After clearing an Active slot, move the top Queue item to Active with status
`next`. When promoting from a personal GitHub queue, preserve useful `Label`,
`Model`, and `Batch` metadata in the Active description or handoff so the
assignment still carries its routing context:

```markdown
### Active
| Status | Issue | Repo | Description | Handoff |
|--------|-------|------|-------------|---------|
| next | #NNN | core4 | Description | [handoff](path.md) |
```

Re-number the remaining Queue rows starting from 1.

### 3. Header counts

Update the top-line counts:
- Total PRs merged
- Open PRs (check all repos)
- Approximate open issues

For read-only refresh, report the current count beside the sprint doc's
existing snapshot and call out material drift instead of editing the header.

### 4. Velocity table

Update the sprint row with new PR count and key milestones.

### 5. Launch readiness

Update "What's working" and "What's blocking launch" if merges changed the picture.

### 6. Stale issue refresh

Before promoting queued work or regenerating dispatch prompts, refresh any Active
or Queue row whose state may be stale:

- issue or PR state was last checked in a previous sprint day;
- the row says `next`, `blocked`, `changes-req`, `stale`, `parked`, or similar;
- the description references a branch, PR, artifact, or dependency that may have
  moved since the sprint doc was written;
- an issue is duplicated, superseded, closed, or already satisfied by a recent
  merge.

Use GitHub as the source of truth, then update the sprint doc rather than
copying stale table text forward:

```bash
gh issue view <num> --repo wrfcoin/<repo> \
  --json number,title,state,labels,updatedAt,closedAt,url
gh pr list --repo wrfcoin/<repo> --state all --search "#<num>" \
  --json number,state,isDraft,mergedAt,title,headRefName,url
```

Apply these outcomes:

- **Open and still actionable**: keep the row, refresh the title/description if
  it drifted, and preserve priority unless current labels clearly changed it.
  For personal GitHub sprint queues, also preserve any `Label`, `Model`, or
  `Batch` columns already present; refresh stale values, but do not drop the
  routing metadata during cleanup.
- **Closed as completed or merged**: move it to Completed if it belongs to the
  sprint ledger, with PR and SHA when available.
- **Duplicate, superseded, or no longer useful**: remove it from dispatchable
  Queue/Active work and note the reason in launch readiness or velocity notes.
- **Blocked by another issue/PR**: keep it queued only if the blocker is explicit
  and dispatch prompts name the prerequisite.

If a row cannot be refreshed because GitHub is unavailable, leave the row in
place, mark the validation gap in the sprint notes, and do not promote it ahead
of freshly verified work.

In read-only refresh, classify candidate queue changes instead of applying
them:

- **Promote candidate**: live issue/PR state is open, owner skill is clear,
  risk labels are absent, and the smallest safe implementation boundary is
  visible.
- **Tony-decision / manager-review**: visibility, privacy, IP, welfare, safety,
  priority, or creative direction must be chosen before dispatch.
- **Defer or watch**: useful evidence exists, but the item is weakly scoped,
  blocked, duplicate-looking, or better handled after another issue/PR.
- **Remove candidate**: the issue is closed, superseded, exact duplicate, or
  already satisfied by a recent merge.

For personal GitHub sprint queues, preserve live label-derived routing fields
in the report so a later applied update can keep `Label`, `Model`, and `Batch`
columns intact.

### PR pressure refresh

When live PR pressure is part of the refresh, split PRs into:

- **Ready**: non-draft PRs that can enter review or merge-manager flow.
- **Draft**: active implementation work that should not be counted as
  review-ready throughput.
- **Overlap/de-dup review**: clusters with similar titles, branches, labels,
  changed paths, or sprint themes that should be reviewed before launching more
  related work.

Do not assign new work into an overlap/de-dup cluster until the manager has
decided whether to merge, close, combine, or retarget the existing PRs.

### 7. Archive follow-up

During each sprint update, check whether recent sprint artifacts need durable
follow-through:

- swarm reports, blind summaries, merge-review notes, or dispatch outputs under
  `/tmp`, sprint archive folders, or linked PR artifacts;
- strong implementation ideas that were written to summaries but never promoted
  to an issue, PR, or sprint queue row;
- completed work whose proof should be linked from the sprint doc before the
  temporary artifact disappears.

For each artifact worth preserving, choose one public-safe action:

- add or update a sprint Queue row that points at the artifact and names the next
  engineering action, preserving label/model/batch metadata when the sprint doc
  uses personal GitHub queue columns;
- file or link a GitHub issue when the work belongs in a repo backlog;
- add the artifact path/PR URL to Completed or velocity notes when it is only
  evidence for work already done;
- explicitly skip it when it is obsolete, duplicate, private, or not actionable.

Privacy boundary: do not publish private family/media details, raw archive
contents, EXIF/GPS data, private source paths, or personal names into public
issues or sprint docs. Use a redacted summary, a private-repo pointer, or a
private handoff note when the artifact is useful but not public-safe.

### 8. Dispatch Prompt Patterns (always include)

After updating counts and tables, generate **themed dispatch prompt patterns** for
each persona that has queued work. These go into the sprint doc as a new subsection
under each persona, right after their Queue table and before Completed:

In read-only refresh mode, generate these as proposed prompt patterns in the
manager report rather than writing them into the sprint doc.

```markdown
### Dispatch Prompts
<!-- Auto-generated by sprint-update. Copy-paste to launch agents. -->

**Round 0 — Revisions** (if any Active items are changes-requested):
> fix the N changes-requested Dan PRs on their existing branches: ...

**Round 1 — [Theme]** (N agents, M issues):
> launch N agents on Dan's [theme] [priority]: ...

**Round 2 — [Theme]** (N agents, M issues):
> launch N agents on Dan's [theme] [priority]: ...
```

#### Rules for generating prompts

1. **Sizing**: 2-3 issues per agent, max 4 agents per round, 8-12 issues per round
2. **Grouping**: Group by repo + theme (e.g., "infra Docker", "backend resilience"),
   or by repo + label/theme for personal GitHub queues. Do NOT group only by
   batch number ("infra batch 1").
3. **Priority order**: Work top-down by priority — P0 first, then P1, then P2, etc.
   Don't mix priorities in a single round unless they share a theme.
4. **Revision round first**: If any Active items have status `changes-req`, generate
   a Round 0 that lists the specific fixes needed per PR (from review comments).
5. **Name each round**: Use a descriptive theme name, not a number. E.g.:
   - "backend integration wiring" not "backend round 1"
   - "infra Docker hardening" not "infra P2 batch"
   - "core4 consensus fixes" not "Alice round 2"
6. **Include issue numbers**: Every prompt must list the specific issue numbers.
   For personal GitHub queues, include label, model, and batch context when the
   prompt would otherwise be ambiguous.
7. **Estimate rounds**: Show how many rounds it would take to clear the queue.
   Only generate detailed prompts for the next 3-4 rounds. Summarize the rest.
8. **All 5 personas**: Generate prompts for every persona that has queued work,
   not just the one the user is currently focused on.
9. **Personal GitHub columns**: When regenerating personal sprint queues, keep
   the `Label`, `Model`, and `Batch` columns in the Queue table even if a value
   is unknown. Use `TBD` for unknown model or batch values instead of dropping
   the column.

#### Example output for a persona section

```markdown
### Dispatch Prompts

**Round 0 — Revisions** (fix 2 changes-requested PRs):
> fix changes-requested PRs: backend#509 (target enhanced_unified_api_optimized.ts),
> infra#301 (add CORS to expose-lan.sh + docker-compose.lan.yml)

**Round 1 — backend integration** (2 agents, 6 issues):
> launch 2 agents on Dan's P2 backend integration issues:
> - backend security/config: #486 dev key fallback, #487 CORS 8080, #493 health→core4
> - backend performance: #367 pg.Pool exhaustion

**Round 2 — infra integration + compose** (2 agents, 6 issues):
> launch 2 agents on Dan's P2 infra items:
> - infra integration: #291 onboarding secrets, #297 missing depends_on, #253 ZFS overrides
> - infra Docker: #259/#261 single-stage, #266 wrf limits, #224 PAYMASTER_CHAIN_ID
```

Personal GitHub queues should carry the extra routing columns into the prompt:

```markdown
**Round 1 — maker documentation capture** (2 agents, 5 issues):
> launch 2 agents on P1 maker documentation issues:
> - label maker-docs, model gpt-5.5, batch batch-03: #41, #44, #49
> - label portfolio, model gpt-5.4, batch batch-03: #52, #53
```

#### When to regenerate

Regenerate dispatch prompts every time sprint-update runs. Old prompts are replaced
entirely — they reflect the queue state at update time, not historical plans.

## After updating

Update the sprint progress memory file:
```
~/.claude/projects/<project-slug>/memory/project_sprint_progress.md
```
