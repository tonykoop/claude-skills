---
name: ci-triage
version: 0.3.0
last-updated: 2026-11-17
description: >-
  Run a read-only CI and Dependabot health check across the public WRFCoin
  repos (wrfcoin org: core4, backend, frontend, mobile, infra,
  smart-contracts, docs, oracle-reference, testnet-support, meteo-types,
  forecast-score, defi-protocols, storage-providers) plus the 8 self-hosted
  CT102 runners, and write a markdown report to wrfcoin/docs/ci-triage/. Use
  this skill whenever the user wants to check CI health, see which GitHub
  Actions workflows pass or fail, find why a run is stuck queued or pending,
  check that the CT102 runners are back on, triage Dependabot alerts, or get a
  status snapshot across repos. Trigger phrases include "ci-triage", "check
  CI", "ci status", "are workflows passing", "check the pipelines",
  "dependabot status", "any new failures", "why is CI stuck", "are the
  runners on".
---

# CI Triage — WRFCoin public repos

Read-only sweep. No code changes, no PRs, no commits, no reruns. The only file it
writes is the report.

**Output file:** `/home/tony/wrfcoin/docs/ci-triage/YYYY-MM-DD-HH-MM-ci-triage.md`
(actual current UTC time in the name).

## Where CI runs (2026-11)

- **Public repos** (the `wrfcoin/*` repos without `-archive`) run on GitHub-hosted
  `ubuntu-latest` (a few jobs on `macos-14` / `windows-2022`). Public repos get hosted
  minutes free, so there is **no billing block** any more. A failure here is `real`,
  `config`, `stuck` or `flaky`, never "billing".
- **CT102 self-hosted runners: 8 in total**, registered to the private archive repos:
  `core4-archive` (4, label `n5pro`), `backend-archive` (2, `ct102-backend`),
  `infra-archive` (2, `n5pro`). Release replay and some archive gates use them. Steps
  that stop them (release kits, maintenance) have left them off for a day before, so
  always count them.
- The `*-archive` repos are read-only history. Do not triage their workflows beyond
  the runner count.

Get the current public list instead of trusting the one above:

```bash
gh repo list wrfcoin --limit 100 --visibility public --no-archived \
  --json name -q '.[].name' | grep -v '^\.github$' | sort
```

Never include private repos (security testing, incubation, `*-archive`) in the
report's per-repo sections. The report is a local file, but parts of it may be
pasted into public issues.

---

## Step 1 — Gather data in parallel

Set `REPOS` from the command above, then fire these as separate tool calls in one
message.

**A. Runner count (must be 8):**
```bash
for r in core4-archive backend-archive infra-archive; do
  gh api repos/wrfcoin/$r/actions/runners \
    --jq "\"$r \(.total_count) total, \([.runners[]|select(.status==\"online\")]|length) online, \([.runners[]|select(.busy)]|length) busy\""
done
```
Online across the three must add up to **8**. Fewer means a runner service is down
on CT102. Report it as P0 and give Tony the read-only check to run on the Proxmox
host: `pct exec 102 -- systemctl list-units --type=service --state=active
--no-legend 'actions.runner.*' | wc -l` (must print 8). Do not start or stop
runners yourself, and don't call them fixed until you have seen the 8.

**B. Run history, last 10 per repo:**
```bash
for repo in $REPOS; do
  echo "=== wrfcoin/$repo ==="
  gh run list --repo wrfcoin/$repo --limit 10 \
    --json databaseId,name,status,conclusion,createdAt,headBranch,event 2>&1
done
```

**C. Stuck runs (queued):**
```bash
for repo in $REPOS; do
  gh api "repos/wrfcoin/$repo/actions/runs?status=queued&per_page=50" \
    --jq ".workflow_runs[] | \"$repo \(.id) \(.name) \(.created_at) \(.head_branch)\"" 2>&1
done
```

**D. Dependabot open alerts:**
```bash
for repo in $REPOS; do
  echo "=== wrfcoin/$repo ==="
  gh api "repos/wrfcoin/$repo/dependabot/alerts?state=open&per_page=100" --paginate \
    --jq '.[] | {number, severity: .security_vulnerability.severity,
      package: .security_vulnerability.package.name,
      ecosystem: .security_vulnerability.package.ecosystem,
      summary: .security_advisory.summary,
      patched: .security_vulnerability.first_patched_version.identifier}' 2>&1
done
```
A 403/404 means alerts are off for that repo; say so, don't guess.

**E. Open Dependabot PRs:**
```bash
for repo in $REPOS; do
  gh pr list --repo wrfcoin/$repo --author "app/dependabot" --state open \
    --json number,title,createdAt 2>&1 | sed "s|^|$repo |"
done
```

---

## Step 2 — Deep-dive each recent failure

For each repo whose **last 3 runs on `main`** include `conclusion: failure`, look at
the newest failed run:

```bash
gh run view <RUN_ID> --repo wrfcoin/<repo>
gh run view <RUN_ID> --repo wrfcoin/<repo> --log-failed | tail -120
```

If `--log-failed` prints nothing (common for cancelled, timed-out or never-started
jobs), use the jobs API:

```bash
gh api repos/wrfcoin/<repo>/actions/runs/<RUN_ID>/jobs \
  --jq '.jobs[] | {id, name, status, conclusion, runner_name, started_at, completed_at,
        failed_steps: [.steps[]|select(.conclusion=="failure")|.name]}'
gh api repos/wrfcoin/<repo>/actions/jobs/<JOB_ID>/logs | tail -120
```

`gh run view` shows only the first page of check runs on big workflows; when a job
seems missing, page the jobs API (`?per_page=100`).

Never print secrets: if a log excerpt shows a token, key or `.env` value, drop that
line from the report.

Categorize each failure:
- **`real`**: test, lint, type-check, build or compile error in the log.
- **`config`**: missing secret, bad workflow reference, invalid YAML, missing external
  service, a self-hosted label with no runner.
- **`stuck`**: run sits `queued`/`pending` with 0 jobs (see below).
- **`flaky`**: the same commit passed on a rerun or a neighbouring run. Name the test.

### Stuck runs hold concurrency groups

A run that sits `pending` with **zero jobs** is usually blocked by an older run still
`queued` in the same concurrency group (for example one that targeted a self-hosted
label with no runner). `cancel-in-progress: true` does not evict a queued run, and
`gh run cancel` often only "submits" the request. Close/reopen, rebase and rerun all
fail the same way.

Diagnosis (read-only): from C, match the workflow and PR/branch, and note the old
run's id and age. The fix is
`gh api -X POST repos/wrfcoin/<repo>/actions/runs/<OLD_ID>/force-cancel`. That
changes state, so this skill only **recommends** it (P0 item with the exact command);
run it only if the user explicitly asks.

---

## Step 3 — Write the report

```markdown
# CI Triage — YYYY-MM-DD HH:MM UTC

## Summary
| Item | Value |
|---|---|
| CT102 runners online | N / 8 (core4-archive a, backend-archive b, infra-archive c) |
| Public repos green on main | N / M |
| Repos with real failures | N |
| Stuck (queued/pending) runs | N |
| Open Dependabot alerts | N (C critical, H high, M medium, L low) |
| Open Dependabot PRs | N |

## Runners
[Counts from A. If not 8: which repo is short, and the exact check for Tony.]

## Per-repo CI
### <repo>   (one section per public repo)
- Last run on main: [time, workflow, result]
- Last 10 runs: table (run id, workflow, branch, event, result, when)
- Failures: category, root cause, short log excerpt (no secrets)

## Stuck runs
[repo, run id, workflow, age, blocking run id, recommended force-cancel command]

## Dependabot
[Per repo: counts by severity; critical/high rows with package and fix version.
Flag smart-contracts alerts as on-chain risk. Note repos with alerts off.]

## Open Dependabot PRs
[repo, #, title, age; or "none"]

## Changes since the previous report
[Diff against the newest file in docs/ci-triage/, if any.]

## Action items
### P0 (blocks merges or releases)
### P1 (this week)
### P2 (track)
```

## Step 4 — Finish

1. Print the report path as a Firefox link in a code block:
   `file://///wsl.localhost/Ubuntu/home/tony/wrfcoin/docs/ci-triage/<name>.md`
2. Print a short summary: runners N/8, how many repos are green, any real failures or
   stuck runs, critical alerts.
3. Do not print the whole report.

## Rules

- Read-only. If asked to fix something mid-triage, log it as an action item and say
  that fixing is a separate task (`gh-fix-ci` or `heal`).
- No `gh run rerun` loops and no retry loops on `gh` errors: report the error.
- Count claims come from the tool's own count (`total_count`, `length`), not from
  eyeballing output.
- Never mention private security work, private branches or unreleased
  security fixes in the report.
