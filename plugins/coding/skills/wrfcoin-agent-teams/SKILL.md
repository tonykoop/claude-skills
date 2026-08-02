---
name: wrfcoin-agent-teams
description: Run WRFCoin persona-led collaborative agent teams for sprint implementation, quality-gate audits, or cross-repo integration audits. Use when the user explicitly wants parallel subagent work coordinated under a persona or audit lead.
---

# WRFCoin Agent Teams

This skill is for persona-led collaboration. A persona owns the result, while subagents handle bounded sidecar work.

## Use only when the user explicitly wants team or subagent work

Do not spawn subagents by default. Use this skill when the user asks for collaborative teams, audit teams, or parallel agent work.

## Ownership model

- One runtime owns each persona for the session.
- A persona may open a collaborative team internally.
- Subagents must have disjoint write scopes.
- Cross-persona work must be coordinated through the sprint doc, not by sharing a branch.

## Team modes

- `sprint-ops`: implementation-heavy issue execution for a persona queue
- `quality-gate`: launch-readiness audit with specialist auditors plus a lead
- `cross-repo-integration`: contract and wiring audit across repos

Read `references/team-topologies.md` before choosing a team shape.

## Default delegation rules

- Keep the immediate blocking task local to the persona lead.
- Delegate concrete, bounded sidecar tasks.
- Use explorer-style subagents for read-only codebase questions.
- Use worker-style subagents for bounded implementation slices with disjoint files.
- Reconcile findings back into one persona-owned outcome.

## Required outputs

### Sprint-ops

- implementation plan
- issue-to-subagent split
- validation summary
- PR or handoff update

### Quality-gate

- issue table by severity
- domain scorecard
- go/no-go verdict

### Cross-repo integration

- mismatch table by contract or deployment chain
- prioritized fix order
- triage recommendation into persona queues
