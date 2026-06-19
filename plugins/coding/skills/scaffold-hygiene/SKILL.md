---
name: scaffold-hygiene
version: 0.2.0
last-updated: 2026-06-19
description: >-
  Scaffolding hygiene sweep across WRFCoin repos. Checks for drift between
  build/test/deploy scripts, docs, CI workflows, env vars, Docker configs,
  cross-repo API contracts, and operator guides. Fires 4 parallel sub-agents,
  files GitHub issues for real drift, and writes a timestamped report.
  Use when the user says "scaffold hygiene", "scaffolding check",
  "check for drift", "hygiene sweep", "are the docs still accurate",
  "do the scripts still work", or at sprint closeout / every ~25 merged PRs /
  before a testnet relaunch.
---

# Scaffolding Hygiene Sweep

Run a read-only scaffolding hygiene pass across the WRFCoin multi-repo workspace.
Check for drift between code, docs, scripts, CI, Docker configs, env vars, and
cross-repo API contracts. File GitHub issues for real findings.

**Reference:** `docs/scaffolding-hygiene-checklist.md`
**Output:** `/home/tony/wrfcoin/docs/scaffolding-hygiene/YYYY-MM-DD-scaffold-hygiene.md`

## When to run

- Every ~25 merged PRs (check sprint doc for current count)
- At sprint closeout
- Before testnet relaunch or operator onboarding
- After a large rebase wave across 3+ repos
- After any launch-path outage caused by config/script/doc drift

## Timebox

30-45 minutes total. If a section uncovers a launch blocker, stop the broad
pass, file the issue immediately, and report back.

---

## Step 1 — Gather baseline data

Run these in parallel to seed all sub-agents:

```bash
# Recent merges to understand what changed
gh search prs --owner wrfcoin --state merged --limit 30 \
  --json repository,number,title,mergedAt --jq '.[] | "\(.repository.name)#\(.number) \(.title) [\(.mergedAt)]"'
```

```bash
# Current open PR count per repo
for repo in core4 backend frontend smart-contracts infra security-testing mobile storage-providers; do
  count=$(gh pr list --repo wrfcoin/$repo --state open --json number --jq 'length' 2>/dev/null)
  echo "$repo: $count open PRs"
done
```

```bash
# Sprint doc current merged count
head -5 /home/tony/wrfcoin/docs/plans/*[Ss]print*.md 2>/dev/null | grep -i "merged"
```

Note the merged PR count — compare against the last hygiene pass to confirm the
trigger threshold was met.

---

## Step 2 — Launch 4 parallel inspection agents

Fire all 4 Agent tool calls in a **single message**. Each agent covers 2-3
checklist sections and produces structured findings.

### Agent A — Workspace, Build, and CI (Sections 1, 2, 5)

```
You are a scaffolding hygiene inspector for WRFCoin. READ-ONLY — do not edit files.

Workspace: /home/tony/wrfcoin/
Active repos: core4, backend, frontend, smart-contracts, infra, security-testing, mobile, storage-providers

Inspect these three areas and report findings:

**1. Workspace and Entry Points**
For each active repo, verify:
- The documented dev/start entrypoint actually exists (check CLAUDE.md, README.md)
- Startup commands in docs match real files
- No references to deleted/legacy server paths (grep for removed entrypoints)
- Check: `ls <repo>/package.json <repo>/Cargo.toml 2>/dev/null`
- Check: `rg -n "cargo run|npm start|npm run dev|npx tsx" <repo>/CLAUDE.md <repo>/README.md 2>/dev/null`

**2. Build, Test, and Lint Plumbing**
For each active repo, verify:
- Build command works: check Cargo.toml members, package.json scripts
- Test command exists and is documented
- Any new helper scripts from recent PRs have stable paths
- Check: `rg -n "cargo check|cargo test|npm test|npx tsc|npx hardhat" <repo>/CLAUDE.md 2>/dev/null`
- For core4: verify `cargo check --workspace` still lists the documented 8 members

**3. CI and Review Scaffolding**
For each repo with CI:
- `gh run list --repo wrfcoin/<repo> --limit 5 --json name,status,conclusion`
- Verify workflow names match what the CLAUDE.md documents
- Check for silently skipped or empty CI treated as green
- Verify required checks are still the ones that matter
- Check: `ls <repo>/.github/workflows/*.yml 2>/dev/null | wc -l`

Format findings as:
- BLOCKER: <finding> (breaks launch/merge/onboarding)
- DRIFT: <finding> (real mismatch, not blocking)
- OK: <section checked, no issues>

Keep findings under 300 words total.
```

### Agent B — Launch Path, Docker, and Infra (Sections 3, 4)

```
You are a scaffolding hygiene inspector for WRFCoin. READ-ONLY — do not edit files.

Workspace: /home/tony/wrfcoin/
Key files:
- infra/testnet/docker-compose.testnet.yml
- infra/testnet/docker-compose.override.yml
- infra/scripts/relaunch-testnet.sh (or similar)
- backend/package.json, backend/server/
- core4/native-chain/src/bin/launch_api/

CRITICAL CONSTRAINT: All deployment is local builds via SSH to N5 Pro (192.168.0.10, CT 101).
NEVER push Docker images to ghcr.io. 3-file compose stack with named Docker volumes.

Inspect these areas:

**3. Launch and Testnet Path**
- Verify relaunch scripts point to real entrypoints
- Check env vars in compose files match what services actually read
- Verify backend, core4, and compute-agent agree on the launch contract
- Check: `rg -n "CORE4_API_URL|MAIN_API_WS_URL|WRFCOIN_OPERATOR_TOKEN|API_PORT" infra/testnet/ backend/.env* core4/.env* 2>/dev/null`
- Verify smoke-test commands in docs work against real routes
- Check: `rg -n "curl.*localhost|curl.*127.0.0.1|curl.*health" infra/ docs/ 2>/dev/null | head -20`

**4. Docker, Compose, and K8s**
- Verify compose files reference current images, commands, ports
- Check no deploy path depends on ghcr.io or legacy image assumptions
- Verify health checks target real routes
- Check: `rg -n "ghcr.io|docker push|image:" infra/testnet/ infra/docker/ 2>/dev/null`
- Check: `rg -n "healthcheck|readiness|liveness" infra/testnet/ infra/k8s/ 2>/dev/null | head -15`
- Verify override files and operator docs agree on service names/volumes
- Check: `rg -n "volumes:|container_name:" infra/testnet/docker-compose*.yml 2>/dev/null`

Format findings as BLOCKER / DRIFT / OK. Under 300 words.
```

### Agent C — Docs, Runbooks, and Operator Guides (Section 6)

```
You are a scaffolding hygiene inspector for WRFCoin. READ-ONLY — do not edit files.

Workspace: /home/tony/wrfcoin/
Key doc locations:
- docs/ (workspace root)
- core4/docs/
- infra/scripts/CLAUDE.md
- backend/CLAUDE.md
- frontend/CLAUDE.md

Inspect documentation accuracy:

**6. Docs, Runbooks, and Operator Guides**
- Verify operator guides use commands that exist today
- Check file paths referenced in docs point to real files
  - Extract paths from docs: `rg -n "core4/|backend/|infra/|frontend/" docs/*.md core4/docs/*.md 2>/dev/null | head -30`
  - Spot-check 10 referenced paths actually exist
- Verify runbooks describe real current failure domains
- Check new launch blockers or caveats from recent sprint were added to docs
- Look for outdated examples left beside current ones without warning
- Check CLAUDE.md files across repos for stale cross-references:
  - `rg -n "core4/frontend/|core4/backend/|core4/contracts/|core4/infra/" core4/CLAUDE.md 2>/dev/null`
  (these paths were extracted to their own repos — any remaining references are stale)
- Verify port numbers in docs match actual code:
  - `rg -n "4001|3000|4000|6000|6001|7000|3002|8080|8000|8556" docs/ --type md 2>/dev/null | head -15`

Format findings as BLOCKER / DRIFT / OK. Under 300 words.
```

### Agent D — Cross-Repo Contracts and Generated Assets (Sections 7, 8, 9)

```
You are a scaffolding hygiene inspector for WRFCoin. READ-ONLY — do not edit files.

Workspace: /home/tony/wrfcoin/
Cross-repo boundaries:
- Frontend → Backend: HTTP API calls
- Backend → Core4: HTTP/gRPC calls
- Infra scripts → Backend/Core4 APIs
- Smart-contracts: independent deploy, RPC/events

Inspect these areas:

**7. Cross-Repo Contract Drift**
- Check backend route names match frontend API calls:
  - `rg -n "fetch\(|apiClient\.|axios\." frontend/src/ --type ts 2>/dev/null | grep -oP "['\"]/[^'\"]*['\"]" | sort -u | head -20`
  - `rg -n "router\.(get|post|put|delete|patch)" backend/server/ --type js 2>/dev/null | head -20`
- Check core4 API routes match backend expectations:
  - `rg -n "CORE4_API_URL|core4.*fetch|core4.*axios" backend/ 2>/dev/null | head -10`
- Check shared env var names are consistent:
  - `rg -n "MAIN_API_WS_URL|CORE4_API_URL|WRFCOIN_OPERATOR_TOKEN|JWT_SECRET" backend/ infra/ core4/ frontend/ 2>/dev/null | head -20`

**8. Generated Assets and Compatibility Layers**
- Check if ts-rs bindings are current (compare struct definitions to generated TS):
  - `ls core4/sdks/generated/ 2>/dev/null`
  - Check for Option<T> → `T | null` compliance in generated types
- Check mock data paths are not silently active in production routes:
  - `rg -n "MOCK_|mock_data|fallback.*mock|fake.*data" backend/server/ --type js 2>/dev/null | head -10`
- Check test fixtures still represent current protocol

**9. Drift and Debt Sweep**
- Look for stale scripts or duplicate launch paths:
  - `rg -rn "TODO|FIXME|HACK|XXX" core4/native-chain/src/ backend/server/ --type-add 'code:*.{rs,ts,js}' --type code 2>/dev/null | wc -l`
- Check for repeated "known issue" patterns across PRs
- Verify sprint doc reflects reality

Format findings as BLOCKER / DRIFT / OK. Under 300 words.
```

---

## Step 3 — Compile findings and file issues

After all 4 agents complete:

1. **Compile the report.** Merge findings from all agents into the output file using
   this template:

```markdown
## Scaffolding Hygiene — <date>

- Trigger: <25 merges / sprint closeout / relaunch prep>
- Merged PR count: <N> (last hygiene pass: <M>)
- Scope: all 8 active repos
- Findings:
  - Launch-blocking: <count>
  - Medium drift: <count>
  - Low-priority cleanup: <count>
- Issues filed: <list>
- Sprint impact: <none / reprioritized lanes / blocked relaunch path>

### Agent A — Workspace, Build, CI
<paste findings>

### Agent B — Launch Path, Docker, Infra
<paste findings>

### Agent C — Docs, Runbooks, Operator Guides
<paste findings>

### Agent D — Cross-Repo Contracts, Generated Assets, Drift
<paste findings>

### Action Items
| # | Severity | Finding | Issue | Owner |
|---|----------|---------|-------|-------|
| 1 | BLOCKER | ... | wrfcoin/repo#NNN | Dan |
| 2 | DRIFT | ... | wrfcoin/repo#NNN | Alice |
```

2. **File GitHub issues** for every BLOCKER and DRIFT finding. Use labels:
   `scaffolding`, plus `launch` / `docs-drift` / `ci` / `ops` as appropriate.

```bash
gh issue create --repo wrfcoin/<repo> --title "<finding title>" \
  --body "<description with file:line references>" \
  --label "scaffolding,<severity-label>"
```

3. **Do NOT file issues for OK findings** or cosmetic nits.

4. **Update the sprint doc** with a short "Scaffolding Hygiene" note in the
   velocity table if any lane reprioritization is needed.

---

## Decision rules

- If a finding can break launch, relaunch, onboarding, or merge confidence: **file now**
- If a finding is cosmetic or low-risk: **defer** unless the same drift has happened twice
- If the fix is under 10 lines and in the same file being touched: **fold into active work**
- Otherwise: **create a separate issue** so hygiene stays visible

## Do NOT turn this into

- A broad cleanup day
- An unbounded refactor
- "Fix everything while we are here"
- A replacement for normal PR review

The goal is to keep the support structure trustworthy, not to stop feature work.
