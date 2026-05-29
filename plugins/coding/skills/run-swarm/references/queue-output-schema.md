# Run-Swarm Queue Output Schema

Use this contract when `run-swarm` is shaping a backlog or sprint queue. The
artifacts are read-only manager outputs. They summarize the live issue
landscape and do not edit sprint documents, GitHub issues, labels, PRs, or repo
files.

Recommended artifact names:

- `issue_landscape.json`
- `issue_landscape.csv`

## Queue Names

Use exactly one queue per issue:

| Queue | Use when | Safe manager action |
| --- | --- | --- |
| `ready-to-implement` | Evidence, repo target, owner skill, acceptance shape, and small work boundary are clear. | Dispatch an isolated implementation worktree or draft PR lane. |
| `tony-decision` | Visibility, priority, privacy, IP, cost, audience, or creative direction must be chosen first. | Ask the decision question and keep the safe default. |
| `archive-or-watch` | The finding is a duplicate, thin-evidence cluster, low-confidence note, or background context. | Preserve evidence; do not dispatch yet. |

## JSON Shape

Top-level fields:

| Field | Type | Notes |
| --- | --- | --- |
| `schema_version` | string | Start at `run-swarm.issue-landscape.v1`. |
| `generated_at` | string | ISO-8601 timestamp if available, otherwise the audit date. |
| `source` | object | Include workspace root, query/source command, and mode. |
| `counts` | object | Include `issues_total`, `pull_requests_total` when known, `queues`, `strict_dispatch_buckets`, and `owner_skills`. |
| `issues` | array | One object per issue or draft issue candidate. |
| `notes` | array | Optional manager caveats. |

Each `issues[]` object should include:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `repo` | string | yes | `owner/name` or local repo name. |
| `number` | number or null | yes | GitHub issue number, or null for a draft candidate. |
| `url` | string or null | no | GitHub URL when known. |
| `title` | string | yes | Issue or draft title. |
| `state` | string | no | Usually `open`, `closed`, or `draft`. |
| `labels` | array | no | Raw GitHub labels or suggested labels. |
| `queue` | string | yes | One of the three queue names above. |
| `owner_skill` | string | yes | Recommended skill owner for the next step. |
| `strict_dispatch_bucket` | string | yes | `skill-development`, `content-production`, `capture`, `deliverable`, or `ambiguous`. |
| `owner_skill_bucket` | string | yes | The owner-skill lens classification, often the same as `owner_skill`. |
| `implementation_boundary` | string | yes | Smallest safe PR/worktree/issue boundary. |
| `tony_decision` | string or null | yes | Direct question when queue is `tony-decision`; otherwise null. |
| `safe_default` | string or null | yes | What to do if no decision is made. |
| `evidence` | array | no | Paths, PRs, artifacts, issue links, or command evidence. |
| `risk_flags` | array | no | For example `ip-privacy`, `welfare`, `safety`, `needs-clarification`, or `batch-needs-review`. |
| `duplicate_of` | string or null | no | Existing issue reference for exact duplicates. |

Minimal example:

```json
{
  "schema_version": "run-swarm.issue-landscape.v1",
  "generated_at": "2026-05-11",
  "source": {
    "mode": "personal-github",
    "workspace_root": "/path/to/workspace",
    "query": "gh search issues --owner tonykoop --state open"
  },
  "counts": {
    "issues_total": 2,
    "pull_requests_total": 0,
    "queues": {
      "ready-to-implement": 1,
      "tony-decision": 1,
      "archive-or-watch": 0
    },
    "strict_dispatch_buckets": {
      "skill-development": 1,
      "content-production": 1
    },
    "owner_skills": {
      "run-swarm": 1,
      "idea-incubator": 1
    }
  },
  "issues": [
    {
      "repo": "tonykoop/claude-skills",
      "number": 117,
      "url": "https://github.com/tonykoop/claude-skills/issues/117",
      "title": "Add queue output to run-swarm",
      "state": "open",
      "labels": ["skill:run-swarm", "sprint:implementation-pass"],
      "queue": "ready-to-implement",
      "owner_skill": "run-swarm",
      "strict_dispatch_bucket": "skill-development",
      "owner_skill_bucket": "run-swarm",
      "implementation_boundary": "one skill-package PR updating run-swarm references",
      "tony_decision": null,
      "safe_default": null,
      "evidence": ["skills/run-swarm/SKILL.md"],
      "risk_flags": [],
      "duplicate_of": null
    },
    {
      "repo": "tonykoop/private-media-example",
      "number": 1,
      "url": null,
      "title": "Choose public/private album route",
      "state": "open",
      "labels": ["risk:ip-privacy"],
      "queue": "tony-decision",
      "owner_skill": "idea-incubator",
      "strict_dispatch_bucket": "content-production",
      "owner_skill_bucket": "idea-incubator",
      "implementation_boundary": "private decision stub only",
      "tony_decision": "Should this stay private or become a public-safe portfolio issue?",
      "safe_default": "keep private and do not dispatch implementation",
      "evidence": [],
      "risk_flags": ["ip-privacy"],
      "duplicate_of": null
    }
  ],
  "notes": ["Counts are a manager snapshot, not a sprint-doc mutation."]
}
```

## CSV Columns

CSV output should be a flat row-per-issue view that can be loaded into a
spreadsheet or compared across swarm runs.

Required columns:

```csv
repo,number,url,title,state,labels,queue,owner_skill,strict_dispatch_bucket,owner_skill_bucket,implementation_boundary,tony_decision,safe_default,evidence,risk_flags,duplicate_of
```

Encoding rules:

- Use UTF-8 CSV with a header row.
- Join list fields with `; `.
- Leave unknown optional fields blank rather than inventing evidence.
- Preserve the exact queue names from this reference.
- Keep private names, locations, and family/media details out of public CSVs;
  use a private artifact path or redacted evidence note instead.

Example row:

```csv
repo,number,url,title,state,labels,queue,owner_skill,strict_dispatch_bucket,owner_skill_bucket,implementation_boundary,tony_decision,safe_default,evidence,risk_flags,duplicate_of
tonykoop/claude-skills,117,https://github.com/tonykoop/claude-skills/issues/117,Add queue output to run-swarm,open,"skill:run-swarm; sprint:implementation-pass",ready-to-implement,run-swarm,skill-development,run-swarm,one skill-package PR updating run-swarm references,,,"skills/run-swarm/SKILL.md",,
```

## Manager Checks

Before using the artifacts for dispatch:

1. Confirm every item has exactly one `queue`.
2. Confirm every `ready-to-implement` item has an owner skill and a small
   implementation boundary.
3. Move items with `ip-privacy`, `welfare`, `safety`, `needs-clarification`,
   or `batch-needs-review` risk flags out of immediate dispatch unless the
   manager explicitly approves the route.
4. Compare `strict_dispatch_bucket` with `owner_skill_bucket` when sizing skill
   lanes; they answer different questions.
5. Treat the JSON/CSV files as evidence snapshots. Let `sprint-update` or the
   sprint manager decide whether to edit the sprint document.
