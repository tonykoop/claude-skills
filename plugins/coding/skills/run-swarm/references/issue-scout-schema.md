# Issue-Scout Cache Schema

Defines the structure of the persistent artifact cache written to
`/tmp/tonykoop-run-swarm-issue-scout-results/` during a `run-swarm` personal
GitHub or WRFCoin audit run.

See `freshness-contract.md` for TTL rules and staleness detection.

## Directory Layout

```
/tmp/tonykoop-run-swarm-issue-scout-results/
  open-issues.json          ← open issues across queried repos
  closed-issues.json        ← recently-closed issues (last 90 days)
  repo-inventory.txt        ← flat list of repos with metadata
  meta.json                 ← cache run metadata (timestamps, query params)
```

---

## `open-issues.json`

Array of issue objects. One element per open GitHub issue across all repos in
the run scope.

```json
[
  {
    "repo": "tonykoop/claude-skills",
    "number": 53,
    "url": "https://github.com/tonykoop/claude-skills/issues/53",
    "title": "Full inventory pass of D:\\ archive",
    "state": "open",
    "labels": ["capture", "ready-now"],
    "created_at": "2026-05-09T00:00:00Z",
    "updated_at": "2026-05-09T00:00:00Z",
    "body_excerpt": "First 400 characters of the issue body..."
  }
]
```

| Field | Type | Notes |
|---|---|---|
| `repo` | string | `owner/name` |
| `number` | integer | GitHub issue number |
| `url` | string | Full GitHub URL |
| `title` | string | Issue title |
| `state` | string | Always `open` in this file |
| `labels` | string[] | Raw GitHub label names |
| `created_at` | string | ISO-8601 |
| `updated_at` | string | ISO-8601 |
| `body_excerpt` | string | First ≤400 characters of body (no newlines); omit body if blank |

---

## `closed-issues.json`

Same shape as `open-issues.json`. Scoped to issues closed within the last 90
days. Used by agents for duplicate detection before filing new issues.

```json
[
  {
    "repo": "tonykoop/claude-skills",
    "number": 48,
    "url": "https://github.com/tonykoop/claude-skills/issues/48",
    "title": "...",
    "state": "closed",
    "labels": [],
    "created_at": "2026-04-01T00:00:00Z",
    "updated_at": "2026-05-01T00:00:00Z",
    "body_excerpt": "..."
  }
]
```

---

## `repo-inventory.txt`

One line per repo in the queried scope. Tab-separated columns.

```
owner/name<TAB>default_branch<TAB>open_issues_count<TAB>last_pushed_at
tonykoop/claude-skills<TAB>main<TAB>32<TAB>2026-05-25T00:00:00Z
tonykoop/instrument-maker<TAB>main<TAB>112<TAB>2026-05-29T00:00:00Z
```

Agents can use this file to scope searches without calling the GitHub API for
every repo.

---

## `meta.json`

Written by the manager at the end of each cache refresh. Used by the
freshness-contract check.

```json
{
  "schema_version": "run-swarm.issue-scout-cache.v1",
  "mode": "personal-github",
  "queried_at": "2026-05-29T08:00:00Z",
  "query_scope": ["tonykoop"],
  "repos_scanned": 14,
  "open_issues_count": 147,
  "closed_issues_window_days": 90,
  "closed_issues_count": 23
}
```

| Field | Type | Notes |
|---|---|---|
| `schema_version` | string | Pin to `run-swarm.issue-scout-cache.v1` |
| `mode` | string | `personal-github` or `wrfcoin` |
| `queried_at` | string | ISO-8601 timestamp of the refresh |
| `query_scope` | string[] | GitHub owner(s) or org(s) queried |
| `repos_scanned` | integer | Number of repos included |
| `open_issues_count` | integer | Total open issues across all repos |
| `closed_issues_window_days` | integer | Lookback window for closed issues |
| `closed_issues_count` | integer | Total closed issues in that window |

---

## Usage Notes

- Agents receive the cache paths in their prompt preamble; they read the files
  directly rather than calling `gh issue list` for every sub-task.
- `closed-issues.json` is used only for duplicate detection, not for sprint
  shaping or dispatch.
- The `repo-inventory.txt` format is intentionally plain text so agents can
  `grep` it without parsing JSON.
- Never commit these files to any repo. They are ephemeral manager artifacts.
