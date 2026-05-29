# Issue-Scout Freshness Contract

Defines cache TTL policy and staleness detection for the `run-swarm`
issue-scout artifact directory at
`/tmp/tonykoop-run-swarm-issue-scout-results/`.

See `issue-scout-schema.md` for the file structure and field definitions.

## TTL Policy

| Artifact | Max age before stale | Rationale |
|---|---|---|
| `open-issues.json` | **24 hours** | Issues open/close frequently during active sprints; a day-old list misfires duplicate detection and misses sprint-week closures |
| `closed-issues.json` | **7 days** | Closed issues change much less; a week is safe for duplicate lookups while avoiding a slow full rescan every run |
| `repo-inventory.txt` | **Always refresh on first run of the session; else 24 hours** | Repo count and open-issue totals are used for lane sizing, so stale counts cause mis-proportioned sprints |
| `meta.json` | Written with every refresh; if absent, treat entire cache as stale | The absence of `meta.json` is the canonical staleness signal |

## Staleness Detection

Before reading any cache file, the manager checks `meta.json`:

1. **`meta.json` missing** → cache is absent or corrupted. Treat as stale.
   Refresh everything.

2. **`meta.json` present** → compare `queried_at` against the current
   timestamp:
   - If `now - queried_at > 24h` → stale. Refresh everything.
   - If `now - queried_at ≤ 24h` → fresh. Agents may read without re-querying.

3. **Mode mismatch** → if the current run mode (`personal-github` vs
   `wrfcoin`) differs from `meta.json.mode`, the cache is for the wrong scope.
   Treat as stale and refresh.

```python
# Pseudocode — manager pre-flight check
import json, datetime, os

CACHE_DIR = "/tmp/tonykoop-run-swarm-issue-scout-results"
MAX_AGE_HOURS = 24

meta_path = os.path.join(CACHE_DIR, "meta.json")
if not os.path.exists(meta_path):
    return "stale"

meta = json.load(open(meta_path))
queried_at = datetime.datetime.fromisoformat(meta["queried_at"].replace("Z", "+00:00"))
age = datetime.datetime.now(datetime.timezone.utc) - queried_at

if age.total_seconds() > MAX_AGE_HOURS * 3600:
    return "stale"
if meta["mode"] != current_mode:
    return "stale"
return "fresh"
```

## Re-Run Trigger Conditions

Trigger a full cache refresh when any of the following is true:

- `meta.json` is absent.
- Cache age exceeds the TTL for the requested artifact.
- Run mode differs from `meta.mode`.
- The user explicitly says "re-scan", "fresh run", "force refresh", or similar.
- A swarm agent reports a label or issue that contradicts the cached state
  (e.g., an issue the cache shows as open is referenced as closed in a PR).

## Partial Refresh

When only one artifact is stale (e.g., `repo-inventory.txt` aged out but
`open-issues.json` is fresh), the manager may refresh only the stale file and
update `meta.json.queried_at` to the current time after the partial refresh.
Only do this if the run is explicitly scoped to a sub-task (e.g., "check repo
list") — for a full audit swarm, always refresh all four files together.

## Cleanup

The cache lives in `/tmp/` and is ephemeral — it does not persist across
reboots. Do not commit these files or copy them to a repo. After a sprint run
completes, the manager may optionally copy `meta.json` to the sprint handoff
directory for audit trail, but the cache files themselves stay in `/tmp/`.
