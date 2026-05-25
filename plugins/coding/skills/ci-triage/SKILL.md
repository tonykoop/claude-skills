---
name: ci-triage
version: 0.1.0
last-updated: 2026-05-20
description: >-
  Run a read-only CI and Dependabot health check across all 7 WRFCoin repos
  (core4, backend, frontend, smart-contracts, infra, security-testing, mobile)
  and write a detailed markdown report to wrfcoin/docs/ci-triage/. Use this
  skill whenever the user wants to check CI health, see which GitHub Actions
  workflows are passing or failing, check billing status, triage Dependabot
  alerts, audit pipeline state, see if the spending limit was fixed, check if
  real failures appeared after billing was resolved, or just wants a status
  snapshot across repos. Trigger phrases include "ci-triage", "check CI",
  "ci status", "are workflows passing", "check the pipelines",
  "dependabot status", "any new failures", "did billing get fixed".
---

# CI Triage — WRFCoin Multi-Repo

Run a thorough, read-only diagnostic sweep across all WRFCoin repos and write a
detailed markdown report to `wrfcoin/docs/ci-triage/`. No code changes, no PRs,
no commits.

**Output file:** `/home/tony/wrfcoin/docs/ci-triage/YYYY-MM-DD-HH-MM-ci-triage.md`
Use the actual current UTC date/time in the filename (e.g. `2026-03-16-03-45-ci-triage.md`).

---

## Step 1 — Gather all data in parallel

Fire ALL of these bash commands simultaneously (all in one message, separate tool calls):

**A. CI run history — last 10 runs per repo:**
```bash
for repo in core4 backend frontend smart-contracts infra security-testing mobile; do
  echo "=== wrfcoin/$repo ==="
  gh run list --repo wrfcoin/$repo --limit 10 \
    --json databaseId,name,status,conclusion,createdAt,headBranch,event 2>&1
  echo ""
done
```

**B. Full Dependabot open alert detail (all repos, all fields):**
```bash
for repo in core4 backend frontend smart-contracts infra security-testing; do
  echo "=== wrfcoin/$repo ==="
  gh api repos/wrfcoin/$repo/dependabot/alerts --paginate \
    --jq '.[] | select(.state=="open") | {
      number,
      severity: .security_vulnerability.severity,
      package: .security_vulnerability.package.name,
      ecosystem: .security_vulnerability.package.ecosystem,
      summary: .security_advisory.summary,
      patched_versions: .security_vulnerability.patched_versions,
      cvss: .security_advisory.cvss.score
    }' 2>&1
  echo ""
done
```

**C. Workflow inventory per repo:**
```bash
for repo in core4 backend infra smart-contracts security-testing mobile frontend; do
  echo "=== wrfcoin/$repo ==="
  gh api repos/wrfcoin/$repo/actions/workflows \
    --jq '.workflows[] | {name, state, path}' 2>&1
  echo ""
done
```

**D. Repo metadata:**
```bash
for repo in core4 backend frontend smart-contracts infra security-testing mobile; do
  echo "=== wrfcoin/$repo ==="
  gh repo view wrfcoin/$repo \
    --json defaultBranchRef,isArchived,diskUsage,hasIssuesEnabled,openIssues:issues 2>&1
  echo ""
done
```

**E. Open Dependabot PRs:**
```bash
for repo in core4 backend frontend smart-contracts infra security-testing; do
  echo "=== wrfcoin/$repo ==="
  gh pr list --repo wrfcoin/$repo --author "dependabot[bot]" --state open \
    --json number,title,createdAt,headRefName 2>&1
  echo ""
done
```

---

## Step 2 — Deep-dive every recent failure

For each repo that has runs with `conclusion: "failure"` in the **last 3 runs**,
inspect the most recent failed run:

```bash
gh run view <RUN_ID> --repo wrfcoin/<repo> 2>&1
```

Then, if the failure is NOT billing (i.e. jobs actually ran), fetch the failure log:

```bash
gh run view <RUN_ID> --repo wrfcoin/<repo> --log-failed 2>&1 | head -120
```

Categorize each failure as:
- **`billing`** — annotation says "spending limit" or "account payments have failed"
- **`real`** — log shows actual test/lint/build/compile error with output
- **`config`** — missing secret, broken workflow reference, invalid syntax, missing external infra

Run these inspections in parallel (one tool call per repo in a single message).

---

## Step 3 — Write the detailed markdown report

Write the complete report to `/home/tony/wrfcoin/docs/ci-triage/<YYYY-MM-DD-HH-MM>-ci-triage.md`.

Use this structure — populate every section with real data, not placeholders:

```markdown
# CI Triage Report — YYYY-MM-DD HH:MM UTC

> Generated automatically. Re-run `/ci-triage` at any time for a fresh snapshot.

## Summary

| Item | Value |
|------|-------|
| Billing status | BLOCKED / UNBLOCKED |
| Repos with clean CI (main) | N / 7 |
| Repos with real failures | N |
| Repos with no CI | N |
| Total open Dependabot alerts | N (C critical, H high, M medium, L low) |
| Open Dependabot PRs | N |
| Budget used this cycle | X min / 3,000 min |

---

## Billing & Budget

[Current billing status. Quote the annotation message if billing-blocked.
Note which repos have had runs since the last billing event.
Flag if minutes are running low (< 500 remaining).]

---

## Per-Repo CI Status

### core4
- **Workflows active:** N
- **Last run on main:** [timestamp, workflow name, result]
- **Recent run summary (last 10):**

| Run # | Workflow | Branch | Result | Triggered | When |
|-------|----------|--------|--------|-----------|------|
| ...   | ...      | ...    | ✓/✗    | push/pr/schedule | ... |

- **Failures detail:**
  [For each failing workflow, category + root cause + relevant log excerpt]

### backend
[same structure — note if no workflow files exist]

### frontend
[same structure]

### smart-contracts
[same structure]

### infra
[same structure — note the alignment-campaign-rollup schedule noise]

### security-testing
[same structure]

### mobile
[same structure]

---

## Workflow Inventory

### core4 (N workflows)
| Workflow | State | Classification | Notes |
|----------|-------|---------------|-------|
| Rust Shared/Native Parity Gate | active | Essential | ... |
| CI Readiness | active | Essential | ... |
| ... | ... | ... | ... |

Classify each as: **Essential** (build/test/lint), **Optional** (compliance/docs/release),
**Aspirational** (not yet functional), or **Broken-by-design** (references missing infra/secrets).

[Repeat for infra, smart-contracts, security-testing, mobile, frontend]

---

## Dependabot Alert Detail

### core4
#### Critical
| # | Package | Ecosystem | Summary | CVSS | Fix Available |
|---|---------|-----------|---------|------|---------------|
| N | pkg | rust/npm/pip | ... | X.X | yes / no |

#### High
[same table]

#### Medium
[same table]

#### Low
[same table]

### backend
[same sections]

### frontend
[same]

### smart-contracts
[same — flag OpenZeppelin contract vulnerabilities explicitly as on-chain risk]

### infra
[same]

### security-testing
[same]

### mobile
> Dependabot alerts disabled for this repo.

---

## Open Dependabot PRs

[List any open PRs from dependabot[bot] across all repos, with title and age.
If none: "No open Dependabot PRs across any repo."]

---

## Runtime Dependency Analysis (Rust — core4)

For HIGH and CRITICAL Rust alerts in core4, note whether the vulnerable package
is in the runtime binary dependency chain or dev/test only.
Use results from cargo tree analysis if available in prior context; otherwise note
that a `cargo tree -i <pkg>` check is needed.

Key known runtime packages (from prior analysis):
- `yamux` → wrfcoin-p2p (runtime P2P) — HIGH, no fix available
- `ed25519-dalek` → wrfcoin-p2p (runtime P2P identity) — MEDIUM
- `ring@0.17` → wrfcoin-p2p (libp2p-noise) — MEDIUM
- `bytes` → wrfcoin-native-chain (actix-web) — MEDIUM
- `protobuf` → wrfcoin-native-chain + shared-protocol (prometheus) — MEDIUM, no fix

---

## Changes Since Previous Triage

[Compare against the last report in docs/ci-triage/ if one exists.
List: new failures, resolved failures, alert count changes, new workflows, etc.
If this is the first report, compare against the 2026-03-15 baseline below.]

**2026-03-15 baseline:**
- All CI billing-blocked
- core4: ~68 open alerts (2 critical, 22 high, 41 medium, 13 low)
- backend: 19 open alerts (1 critical, 7 high)
- frontend: 4 open alerts
- smart-contracts: 22 open alerts
- infra: 3 open alerts
- security-testing: 22 open alerts
- 0 open Dependabot PRs

---

## Priority Action Items

[Ordered by urgency. Be specific — include file paths, workflow names, issue numbers.]

### P0 — Blocking (fix before next merge to main)
1. ...

### P1 — High (fix this sprint)
1. ...

### P2 — Track (schedule for later)
1. ...

---

## Known Context

- **backend** has 0 workflow files — CI never runs for this repo
- **frontend** has `documentation-pipeline.yml` — runs weekly Wednesday 04:00 UTC
- **mobile** Dependabot alerts disabled (enable in repo Security settings)
- **core4** npm alerts come from stale `frontend/` + `backend/` subdirs pending PR #376
- Branch protection API returns 403 on all repos (private repos, GitHub Teams required)
- core4 burns ~95% of Actions minutes budget — 3,000 min/month included (Teams plan)
- **core4 CI Readiness currently failing (real)**: `tests/unit/carbon-credit/carbon-audit-service.test.ts` and `tests/unit/network/protocol-validation.test.ts` import missing `backend/` modules
- **32 workflows converted to weekly on 2026-03-16** — a workflow last run several days ago is likely just waiting for its scheduled day, not broken

## Weekly workflow schedule (effective 2026-03-16)

All 32 converted workflows also have `workflow_dispatch` for manual runs.

| Day | Repo(s) | Workflows (UTC) |
|-----|---------|-----------------|
| Mon | core4 | CI Readiness (04:00), TDD Phase 3C (03:00), Supply Chain (04:00), Parity Gate (05:00) |
| Tue | core4 | CLI Integration (04:00), Chromatic (05:00), Component Discovery (06:00) |
| Wed | core4, frontend, smart-contracts | Gap Report (04:00), SBOM (05:00), Docs Pipeline (04:00), Audit Readiness (04:00), Governance Verify (05:00) |
| Thu | infra | Alignment Rollup (04:00), Integrity Observability (05:00), Game Day (06:00) |
| Fri | infra | Sanctions Parity (04:00), WRF Nano (05:00), Policy Bundle (06:00) |
| Sat | infra, security-testing | Docs Sync (04:00), Launch Contract (05:00), P2P Partition (06:00), Adversarial Bot Farms (02:00), Sanction Evasion (03:00), Borderless (04:00), Sanction Parity (05:00) |
| Sun | core4, security-testing, mobile | Docker Scan (02:00), Policy Evasion (02:00), Determinism (03:00), Forecast Gaming (04:00), Consensus Liveness (05:00), Mobile CI (06:00) |
```

---

## Step 4 — Finish up

After writing the file:
1. Print the full path of the report file to stdout so the user knows where it is
2. Print a one-paragraph executive summary to stdout (the TL;DR — billing status,
   how many workflows are green, any critical new findings)
3. Do NOT print the entire report to stdout — it's in the file
