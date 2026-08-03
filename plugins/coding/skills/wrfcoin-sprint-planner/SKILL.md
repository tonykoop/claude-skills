---
name: wrfcoin-sprint-planner
description: Use when reviewing the WRFCOIN sprint backlog, updating a sprint document, prioritizing open GitHub issues across repos, assigning or reassigning lane work, or writing next handoff prompts for agent lanes
---

# WRFCOIN Sprint Planner

Use this skill when the task is backlog shaping rather than code implementation.

Core responsibilities:

- inventory open issues, PRs, and merged work across WRFCOIN repos
- update the active sprint document with current status
- prioritize remaining work for the next day or next lane cycle
- assign issues to lanes with dependency-aware sequencing
- write precise handoff prompts for agent worktrees

Core principle:

**Prioritize the sprint by unblock value, not by issue age or repo symmetry.**

## When to use

- The user asks to review open issues and update the sprint plan
- Several repos have new issues and the next day needs a clean priority order
- Agent lanes need new assignments after merges or blocked PRs
- You need to decide which work belongs in the current sprint vs follow-up

## Default workflow

1. review the sprint document
2. inventory open issues and open PRs across the active repos
3. identify what merged today, what is blocked, and what is still missing
4. rank work by critical path:
   - merge blockers on active sprint goals
   - stateful protocol or contract gaps
   - developer/testnet blockers
   - cleanup and observability follow-ups
5. update the sprint document to reflect reality, not stale intent
6. write the next lane prompts with clear repo, worktree, branch, scope, and validation

## Useful commands

```bash
gh search issues --owner wrfcoin --state open --limit 200 --json repository,number,title,updatedAt,url
gh search prs --owner wrfcoin --state open --limit 100 --json repository,number,title,updatedAt,url
gh issue view <num> --repo wrfcoin/<repo>
gh pr view <num> --repo wrfcoin/<repo>
```

For local tracking:

```bash
sed -n '1,260p' docs/plans/<sprint-file>.md
rg -n "Closes #|Merged|blocked|priority|lane" docs/plans
```

## Priority rules

Promote work when it:

- unblocks an already-open PR or lane
- closes a live contract gap between repos
- turns TDD artifacts into runnable reality
- fixes deterministic state or replay behavior
- improves local/testnet developer throughput for active sprint work

Defer work when it is:

- broad cleanup without current unblock value
- speculative architecture
- cosmetic docs work
- a large platform redesign that exceeds the sprint slice

## Sprint document expectations

A good WRFCOIN sprint update should include:

- merged work with PR numbers and merge SHAs when known
- open PRs with real blockers
- new issues filed from today’s reviews or TDD
- tomorrow’s ordered priorities
- recommended lane assignments

If the sprint doc is stale, rewrite it cleanly instead of preserving old structure.

## Lane assignment rules

Each lane should get:

- one issue owner
- one repo
- one worktree path
- one branch name
- scope boundaries
- minimum validation commands
- PR body requirement with `Closes #<issue>`
- `Do not merge`

Avoid giving a lane work that depends on an unmerged branch unless the prompt says so explicitly.

## Handoff prompt shape

```text
You own wrfcoin/<repo>#<issue>: <title>.

Repo: /home/tony/wrfcoin/<repo>
Worktree: /home/tony/wrfcoin/worktrees/<repo>-<issue>-<slug>
Branch: codex/<repo>-<issue>-<slug>

Create your own worktree from origin/main and keep scope to <repo>-owned files.

Focus on:
- ...
- ...

Requirements:
- ...
- ...

Minimum validation:
- ...
- ...

Push your branch and open a PR against main. Reference “Closes #<issue>” in the PR body. Do not merge.
```

## Good outputs from this skill

- a clean next-day sprint priority list
- a rewritten sprint plan that matches current repo reality
- a lane map for four agents with sensible dependency order
- a triage note explaining what stays in sprint and what moves out
