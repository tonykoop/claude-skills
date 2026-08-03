---
name: launch-audit
description: >-
  Pre-deployment launch-readiness audit swarm. Spawns 6 parallel sub-agents specialized
  for deployment concerns (security, Docker, API contracts, consensus, infra, test coverage),
  each filing labeled GitHub issues and writing domain reports. Produces a unified
  launch-readiness scorecard with go/no-go recommendation. Use before any testnet or
  mainnet deployment. Trigger phrases: "launch audit", "deployment audit", "launch readiness",
  "pre-deploy check", "are we ready to launch", "readiness check", "go/no-go".
---

# Pre-Deployment Launch Audit Swarm

Spawn 6 specialized audit agents to deep-dive deployment-critical domains, file
categorized GitHub issues, and produce a unified launch-readiness scorecard.

**Different from `/run-swarm`:** The general swarm looks for code quality issues broadly.
This audit focuses specifically on **deployment blockers** — things that would cause failures,
security incidents, or operational issues in a running testnet/mainnet.

---

## When to use

- Before any testnet deployment to the N5 Pro
- Before declaring a milestone "launch-ready"
- After a large batch of merges that touch consensus, infra, or API paths
- When the user asks "are we ready to deploy?"

## When NOT to use

- For general code quality (use `/run-swarm`)
- For CI pipeline issues (use `/ci-triage`)
- For a single PR review (use `/merge-review`)

---

## Setup

### Create output directory

```bash
mkdir -p /home/tony/wrfcoin/audit
```

### Check issue label setup

Each agent files issues with `audit/<specialty>` labels. Create labels if they don't exist:

```bash
for label in audit/security audit/docker audit/api audit/consensus audit/infra audit/tests; do
  for repo in core4 backend frontend smart-contracts infra security-testing mobile; do
    gh label create "$label" --repo wrfcoin/$repo --color "d93f0b" --force 2>/dev/null
  done
done
```

Also create severity labels:

```bash
for label in P0 P1 P2; do
  for repo in core4 backend frontend smart-contracts infra security-testing mobile; do
    gh label create "$label" --repo wrfcoin/$repo --color "$([ "$label" = P0 ] && echo 'b60205' || ([ "$label" = P1 ] && echo 'e99695' || echo 'f9d0c4'))" --force 2>/dev/null
  done
done
```

---

## Launch

Fire all 6 Agent tool calls in a **single message** so they run concurrently.
Each agent uses `subagent_type: "general-purpose"` and `model: "sonnet"`.

### Shared preamble (prepend to each agent prompt)

```
You are a launch-readiness audit agent for the WRFCoin blockchain platform.
Your job is READ-ONLY research — do NOT modify any code.

Workspace: /home/tony/wrfcoin/
Repos: core4, backend, frontend, smart-contracts, infra, security-testing, mobile

Deployment target: Local testnet on N5 Pro (Proxmox, Docker containers via SSH).
No cloud/registry pushes — all images built locally.

Rules:
1. Before filing any issue, search existing open issues to avoid duplicates:
   gh search issues --owner wrfcoin --state open -q "<keywords>" --json number,title
2. File in the correct repo
3. Title format: [<Specialty>] <description>
4. Label every issue with BOTH audit/<specialty> AND P0/P1/P2 severity
5. Issue body MUST include: file:line, what's wrong, deployment impact, fix suggestion
6. Focus on DEPLOYMENT BLOCKERS — things that would fail or cause incidents in production
7. After completing, write a domain report to /home/tony/wrfcoin/audit/<specialty>-report.md
8. Return a summary table of all issues filed:
   | Repo | Issue | Title | Severity |
   where Issue is a markdown link [#N](https://github.com/wrfcoin/<repo>/issues/N)
```

---

## Agent 1: SECURITY

```
Specialization: Security — hardcoded secrets, missing auth, unsafe crypto

Search for deployment-critical security issues that would be exploitable in a
running testnet or mainnet.

Priority targets:
1. HARDCODED SECRETS: grep for API keys, passwords, JWT secrets, private keys in source
   Patterns: 'password\s*=', 'secret\s*=', 'api_key', 'private_key', 'ANTHROPIC_API_KEY',
   base64-encoded strings > 20 chars, hex strings > 40 chars in source (not test fixtures)
   Check: .env files committed to git, docker-compose env vars with real values

2. MISSING AUTH: endpoints serving data or mutating state without authentication
   Check: backend/ routes missing auth middleware, core4 API endpoints open to public,
   admin/operator endpoints without authorization checks
   Pattern: router.get/post/put/delete without authenticate/authorize middleware

3. UNSAFE CRYPTO: weak RNG, hardcoded nonces, key reuse, timing-vulnerable comparisons
   Check: Math.random() for crypto, == instead of constant-time compare for secrets,
   single-use nonces reused, key derivation without salt

4. EXPOSED PORTS: services binding to 0.0.0.0 that should be localhost-only
   Check: docker-compose port mappings, nginx configs, service bind addresses

5. SECRETS IN LOGS: wallet addresses, private keys, or tokens logged at info/debug level
   Pattern: console.log.*key, log::info.*secret, println!.*password

File each finding:
    gh issue create --repo wrfcoin/<repo> \
      --title "[Security] <title>" \
      --label "audit/security,<P0|P1|P2>" \
      --body "<body with file:line, impact, fix>"

Write report to: /home/tony/wrfcoin/audit/security-report.md
```

---

## Agent 2: DOCKER

```
Specialization: Docker — Dockerfiles, compose files, health checks, resource limits

Validate all container configurations for a safe, reliable testnet deployment.

Priority targets:
1. DOCKERFILES: validate every Dockerfile in infra/ and any repo root
   Check: multi-stage builds copying too much, running as root, missing .dockerignore,
   unpinned base images (using :latest), COPY before dependency install (cache-busting),
   missing HEALTHCHECK instruction, large final images

2. COMPOSE FILES: validate docker-compose*.yml in infra/
   Check: missing resource limits (mem_limit, cpus), missing restart policies,
   missing health checks, hardcoded host paths, missing volume declarations,
   environment variables with default secrets, port conflicts,
   depends_on without condition: service_healthy

3. HEALTH CHECKS: every service must have a working health check
   Check: /health or /healthz endpoints exist in code AND are referenced in compose,
   health check intervals are reasonable (not too aggressive, not too slow),
   health checks actually test functionality (not just return 200)

4. RESOURCE LIMITS: containers must have memory and CPU limits
   Check: deploy.resources.limits in compose, N5 Pro has 32GB RAM / 6 cores —
   total allocated must not exceed hardware. Flag if sum of mem_limits > 28GB

5. VOLUME MOUNTS: persistent data must be on named volumes, not bind mounts
   Check: data directories (postgres, redis, blockchain state) use named volumes,
   config files can use bind mounts, no /tmp or host-path mounts for state

6. NETWORK ISOLATION: services should use internal Docker networks
   Check: only the reverse proxy and public API should have ports exposed to host,
   backend services should communicate via Docker DNS, not exposed ports

File each finding:
    gh issue create --repo wrfcoin/<repo> \
      --title "[Docker] <title>" \
      --label "audit/docker,<P0|P1|P2>" \
      --body "<body with file:line, impact, fix>"

Write report to: /home/tony/wrfcoin/audit/docker-report.md
```

---

## Agent 3: API

```
Specialization: API contracts — error envelopes, pagination, CORS, JWT, versioning

Verify all API endpoints follow consistent contracts suitable for production.

Priority targets:
1. ERROR ENVELOPES: all endpoints must return consistent error format
   Check: look for mixed error formats (some return {error: msg}, others throw raw,
   others return {message: msg}). All should use the same envelope.
   Pattern: res.status(4xx).json, res.status(5xx).json — compare formats

2. PAGINATION: list endpoints must support pagination
   Check: endpoints returning arrays without limit/offset/cursor params,
   responses without total_count or next_page indicators,
   endpoints that could return unbounded result sets

3. CORS: verify CORS configuration is deployment-appropriate
   Check: CORS_ORIGIN env var is used (not hardcoded), wildcard (*) origin not used
   in production configs, credentials: true with specific origins

4. JWT VALIDATION: all authenticated endpoints must validate JWT properly
   Check: JWT_SECRET is from env (not hardcoded), token expiry is checked,
   signature verification uses the right algorithm, revocation is handled

5. API VERSION CONSISTENCY: core4 Rust API and backend Node API must agree
   Check: shared types match between Rust and TypeScript (ts-rs generated types),
   endpoint paths are consistent, request/response shapes match,
   Option<f64> maps to number | null (not undefined)

6. RATE LIMITING: public endpoints must have rate limits
   Check: rate limiting middleware is applied to all public-facing routes,
   limits are reasonable (not too permissive), rate limit headers are returned

File each finding:
    gh issue create --repo wrfcoin/<repo> \
      --title "[API] <title>" \
      --label "audit/api,<P0|P1|P2>" \
      --body "<body with file:line, impact, fix>"

Write report to: /home/tony/wrfcoin/audit/api-report.md
```

---

## Agent 4: CONSENSUS

```
Specialization: Consensus — block validation, nonce enforcement, state pruning edge cases

Review consensus-critical code for edge cases that would cause chain forks, stuck nodes,
or invalid state in a multi-operator testnet.

Priority targets:
1. BLOCK VALIDATION: verify_block must reject all invalid blocks
   Check: missing validation checks (timestamp bounds, transaction count limits,
   state root verification, parent hash chain), off-by-one in height checks,
   panics/unwraps that would crash the node instead of rejecting the block
   Focus: core4/native-chain/src/ and core4/consensus-engines/src/

2. NONCE ENFORCEMENT: transaction nonces must be strictly sequential from genesis
   Check: nonce=0 accepted for first tx, gaps rejected, replays rejected,
   nonce tracking survives node restart, nonce state is part of state root
   Ref: PR #1002 added nonce enforcement from height 0

3. STATE PRUNING: pruning must not delete state needed by other nodes
   Check: STATE_PRUNING_RETENTION_BLOCKS = 100_000 is respected,
   state needed for sync is retained, pruning doesn't corrupt the state trie,
   checkpoint/snapshot system works correctly with pruning
   Ref: PR #1003 set retention to 100K blocks

4. DETERMINISM: all consensus operations must be deterministic
   Check: no HashMap iteration in consensus paths (use BTreeMap),
   no floating-point in consensus (currency is u64 base units),
   collection sorting before state root computation,
   timestamp resolution doesn't vary across platforms

5. FORK CHOICE: longest-chain / heaviest-chain rule handles all edge cases
   Check: tie-breaking is deterministic, reorgs handled correctly,
   orphan blocks don't cause panics, competing forks converge

6. REWARD CALCULATION: block rewards must be exact and deterministic
   Check: WRF_UNITS_PER_COIN = 10^8, no floating-point, no rounding errors,
   reward halving logic is correct, total supply cap is enforced
   Ref: PR #505 established u64 base units

File each finding:
    gh issue create --repo wrfcoin/core4 \
      --title "[Consensus] <title>" \
      --label "audit/consensus,<P0|P1|P2>" \
      --body "<body with file:line, impact, fix>"

Write report to: /home/tony/wrfcoin/audit/consensus-report.md
```

---

## Agent 5: INFRA

```
Specialization: Infrastructure — nginx, monitoring, backups, deploy runbooks

Audit infrastructure readiness for a reliable testnet deployment on the N5 Pro.

Priority targets:
1. NGINX CONFIG: reverse proxy must be correctly configured
   Check: upstream blocks point to correct service:port pairs,
   TLS termination (or explicit decision to skip for local testnet),
   proxy_pass headers (X-Forwarded-For, Host), websocket upgrade support,
   request size limits, timeout settings

2. PROMETHEUS/GRAFANA: monitoring must capture key health metrics
   Check: all services expose /metrics, Prometheus scrape configs include all services,
   Grafana dashboards exist for: block height, peer count, API latency, error rates,
   alerting rules for: node down, block production stalled, disk > 80%,
   basic auth on Grafana UI

3. BACKUP SCRIPTS: blockchain state and DB must be backed up
   Check: backup scripts exist and are tested, backup includes postgres data + blockchain
   state, restore procedure is documented and tested, backup schedule is configured

4. DEPLOY RUNBOOKS: deployment procedure must be documented and scriptable
   Check: infra/deployment/ has up-to-date scripts, docker-compose.override.yml
   exists for N5 Pro, SSH deployment scripts work (no ghcr.io push),
   rollback procedure exists, upgrade procedure handles DB migrations

5. LOG MANAGEMENT: logs must be captured and rotatable
   Check: Docker logging driver configured, log rotation set (max-size, max-file),
   no unbounded log growth, sensitive data not in logs

6. RESOURCE PLANNING: N5 Pro has 32GB RAM, 6 cores, NVMe storage
   Check: sum of container memory limits fits in 28GB (leave 4GB for OS),
   disk usage estimates for blockchain state growth,
   network bandwidth requirements for P2P

File each finding:
    gh issue create --repo wrfcoin/infra \
      --title "[Infra] <title>" \
      --label "audit/infra,<P0|P1|P2>" \
      --body "<body with file:line, impact, fix>"

Write report to: /home/tony/wrfcoin/audit/infra-report.md
```

---

## Agent 6: TESTS

```
Specialization: Test coverage — untested critical paths, missing error cases, flaky patterns

Identify gaps in test coverage that could allow deployment-breaking bugs through.

Priority targets:
1. UNTESTED CRITICAL PATHS: consensus, block production, state transitions, rewards
   Check: core4/native-chain/ — are create_block, verify_block, apply_block all tested?
   Are all consensus engine variants (PoW, PoS, DPoS, PoI, PoP, PoU) tested?
   Is the full pipeline weather-data → validation → consensus → reward tested end-to-end?

2. MISSING ERROR CASES: what happens when things go wrong?
   Check: network partition handling, malformed block rejection, invalid transaction
   rejection, node crash recovery, DB connection loss, out-of-disk,
   concurrent block production, double-spend attempts

3. FLAKY TEST PATTERNS: tests that pass sometimes and fail sometimes
   Check: time-dependent tests (sleep, timeout, SystemTime::now),
   tests depending on network/port availability, tests with race conditions,
   tests using shared mutable state without synchronization,
   tests with hardcoded ports that might conflict

4. INTEGRATION TEST GAPS: cross-service integration points
   Check: backend ↔ core4 API integration tested? Frontend ↔ backend?
   Docker compose smoke test exists? Health check validation?
   Multi-node consensus tested (not just single-node)?

5. KNOWN FAILURES NOT INVESTIGATED: pre-existing test failures
   Check: checkpoint_prunes_wal, oracle-packet missing field,
   commit_reveal_windows — are these actually harmless for deployment,
   or are they masking real issues?

6. SECURITY TEST COVERAGE: attack scenarios tested?
   Check: security-testing/ repo coverage, double-spend test, 51% attack test,
   Sybil resistance test, DDoS resilience, replay attack test

File each finding:
    gh issue create --repo wrfcoin/<repo> \
      --title "[Tests] <title>" \
      --label "audit/tests,<P0|P1|P2>" \
      --body "<body with file:line, impact, fix>"

Write report to: /home/tony/wrfcoin/audit/tests-report.md
```

---

## After All Agents Complete

### Collect results

Gather summary tables from all 6 agents. Count issues by severity and domain.

### Synthesize the launch-readiness scorecard

Write to `/home/tony/wrfcoin/audit/readiness-scorecard.md`:

```markdown
# Launch Readiness Scorecard — YYYY-MM-DD

## Summary

| Domain | P0 (Blocker) | P1 (High) | P2 (Medium) | Score |
|--------|-------------|-----------|-------------|-------|
| Security | N | N | N | RED/YELLOW/GREEN |
| Docker | N | N | N | RED/YELLOW/GREEN |
| API | N | N | N | RED/YELLOW/GREEN |
| Consensus | N | N | N | RED/YELLOW/GREEN |
| Infra | N | N | N | RED/YELLOW/GREEN |
| Tests | N | N | N | RED/YELLOW/GREEN |
| **Total** | **N** | **N** | **N** | **VERDICT** |

## Scoring

- **GREEN**: 0 P0, ≤2 P1 → ready to deploy
- **YELLOW**: 0 P0, >2 P1 → deploy with known risks documented
- **RED**: any P0 → do NOT deploy until P0s are resolved

## Verdict: GO / CONDITIONAL GO / NO-GO

<1-2 sentence justification>

## P0 Blockers (must fix before deploy)

| # | Domain | Repo | Issue | Title |
|---|--------|------|-------|-------|
| 1 | ... | ... | [#N](url) | ... |

## P1 High Priority (fix soon, can deploy with risk)

| # | Domain | Repo | Issue | Title |
|---|--------|------|-------|-------|

## P2 Medium (fix in next sprint)

| # | Domain | Repo | Issue | Title |
|---|--------|------|-------|-------|

## Domain Reports

- [Security](security-report.md)
- [Docker](docker-report.md)
- [API](api-report.md)
- [Consensus](consensus-report.md)
- [Infra](infra-report.md)
- [Tests](tests-report.md)

## Recommendations

### Before deployment
1. ...

### After deployment
1. ...

### Next sprint priorities (from audit findings)
1. ...

---
_Generated by launch-audit swarm on YYYY-MM-DD_
```

### Deduplicate

If two agents filed overlapping issues (e.g., Security and Tests both flagged the same
missing auth check), close the lower-quality duplicate with a comment linking to the
primary issue.

### Update sprint doc

Add a section noting the audit was run, with issue counts and scorecard verdict.

---

## Constraints

- **Read-only** — agents search and file issues, never edit code
- **No duplicates** — each agent checks existing issues before filing
- **Correct repo** — file issues where the code lives, not where it's consumed
- **Specific findings** — every issue must cite file:line, not vague observations
- **Deployment focus** — flag things that would cause operational failures, not style issues
- **N5 Pro aware** — resource limits, local builds, SSH deployment, no ghcr.io
- **Label consistently** — every issue gets both `audit/<domain>` and `P0`/`P1`/`P2`

---

## Relationship to `/run-swarm`

| Aspect | `/run-swarm` | `/launch-audit` |
|--------|-------------|----------------|
| Focus | General code quality | Deployment readiness |
| Agents | 8 (security, perf, bugs, tests, features, cohesion, viral, blind spots) | 6 (security, docker, API, consensus, infra, tests) |
| Output | Issues only | Issues + domain reports + scorecard |
| Verdict | No | Go / Conditional Go / No-Go |
| When | After merge batches, backlog seeding | Before deployment milestones |
| Overlap | Some (security, tests) | Deeper on infra/docker/consensus |
