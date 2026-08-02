# WRFCoin Team Topologies

Use these patterns when a top-level persona or audit lead is explicitly asked to run a collaborative team.

## 1. Sprint-Ops Team

Purpose: move a persona queue item from issue to validated implementation.

Recommended shape:

- Lead persona: owns the issue, branch, sprint-doc updates, and final PR state
- Explorer: reads issue context, code paths, and prior PRs
- Worker A: implements the primary change
- Worker B or validator: adds tests, checks edge cases, or verifies the diff

When to use:

- One persona has 2-4 tightly related issues in one repo
- The lead can keep the blocking work local and use helpers for analysis or verification

Avoid:

- Splitting one issue across multiple workers that need the same files
- Letting helpers update the sprint doc directly

## 2. Quality-Gate Team

Purpose: produce a launch-readiness scorecard instead of implementation changes.

Observed repo pattern:

- Lead auditor
- Security auditor
- Infra auditor
- Coverage auditor

This mirrors the 2026-03-26 scorecard in `docs/audit/2026-03-26-quality-gate-scorecard.md`.

Outputs:

- issue counts by severity
- correlated findings
- fix order for the next sprint wave
- go/no-go verdict

## 3. Cross-Repo Integration Team

Purpose: find contract drift and deployment-chain breakage across repos.

Recommended shape:

- Lead integrator
- API contracts auditor
- Infra wiring auditor
- Auth and security chain auditor
- Feature-completion or contract-drift auditor

This mirrors the integration-audit pattern summarized in the sprint doc as a 4-agent cross-repo audit.

Outputs:

- endpoint and type mismatches
- env and port mismatches
- auth chain gaps
- deploy-chain breakage
- triage into persona queues

## 4. Persona Scaling

If five personas are not enough, add Frank and Gina as full personas with their own queues and worktrees.

- Frank: recommended as overflow backend or protocol persona
- Gina: recommended as overflow application, audit, or integration persona

Keep the same rule: one runtime owns each persona for the session.
