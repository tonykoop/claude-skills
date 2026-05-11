---
name: run-swarm
version: 1.2.0
last-updated: 2026-05-10
description: >-
  Launch a read-only multi-agent audit swarm for either WRFCoin repos or
  Tony's personal GitHub projects. Use when the user says "/run-swarm",
  "run the swarm", "audit sweep", "what are we missing", "seed the backlog",
  "launch audit agents", or asks for a collaborative specialist team across
  musical instruments, woodworking, crafts, career highlights, photo/story
  projects, or maker documentation. Defaults to issue/report generation; do
  not edit repos unless the user explicitly asks for an implementation swarm.
---

# run-swarm

Run a specialist audit swarm. The default mode is read-only: agents inspect,
summarize, de-duplicate, and file or draft GitHub issues. They do not modify
files, open PRs, or merge.

## Mode Selection

- **WRFCoin mode**: use for `/home/tony/wrfcoin`, WRFCoin repos, launch,
  blockchain, backend/frontend/mobile/infra/security/contract work.
- **Personal GitHub mode**: use for `/mnt/c/Users/Tony/Documents/GitHub` and
  Tony's musical instrument, woodworking, craft, habitat, photo/story, career
  highlight, portfolio, and maker repos.

If the workspace or request is ambiguous, ask one short clarifying question or
run a read-only inventory and choose the safer personal mode.

## Personal GitHub Swarm

Read `references/personal-project-swarm.md` before launching personal-project
agents. The default eight lenses are:

1. Instrument acoustics and empirical validation.
2. CAD, fabrication, DXF/CNC, and shop packet readiness.
3. Documentation, design-book, build-log, and storytelling quality.
4. Visual assets, image-gen-2 prompts, diagrams, and presentation polish.
5. Repo hygiene, stale branches, LFS, manifests, and packaging.
6. Public readiness, IP/privacy, provenance, and family/story safety.
7. Backlog triage, idea-incubator promotion, and sprint queue design.
8. Career highlights, portfolio framing, and audience fit.

## WRFCoin Swarm

Use the original WRFCoin codebase lenses:

1. Security and hardening.
2. Performance and efficiency.
3. Bug hunting.
4. Test coverage and fuzzing.
5. Feature completion.
6. Platform cohesion.
7. Wildcard/growth/DX.
8. Expert blind spots.

## Launch Contract

When `multi_agent = true` is available, spawn the agents in one round so they
run concurrently. If external subagents are not available, dispatch the same
lenses into tmux panes or run them serially and say so.

Every agent receives this contract:

```text
You are a run-swarm audit agent. Work read-only unless the manager explicitly
assigns implementation. Search existing issues before filing. Cite concrete
files, folders, artifacts, PRs, or repo evidence. Prefer one high-quality issue
over many vague ones. Return a summary table with repo, issue/draft, title,
severity/readiness, and recommended owner skill.
```

## Outputs

Manager collects:

- combined issue/report table
- duplicate/overlap notes
- top 5 next-sprint recommendations
- repo or skill owners
- "ready to implement now" versus "needs Tony decision" split
- archive/PR follow-through check so swarm artifacts do not stay hidden in
  `/tmp`

## Issue Filing Mode

Issue filing is a manager action after the read-only audit pass, not something
individual audit agents do on their own. Before filing, search existing open
and closed issues in the target repo using the candidate title keywords, repo
names, artifact paths, and likely labels from the agent report.

Classify each candidate before creating anything:

- **Exact duplicate**: same repo, same actionable outcome, and same evidence.
  Do not open a new issue. Add a concise comment or manager note on the
  existing issue with any new evidence, then mark the swarm candidate as
  `duplicate-of #<number>` and move it to the archive/watch queue.
- **Related issue**: overlapping area but a distinct outcome, owner skill, or
  acceptance test. Open a new issue only if it can stand alone, and include
  `Refs #<number>` links instead of closing or replacing the related issue.
- **Cluster**: several findings that need one scaffold issue. File one parent
  issue with a short checklist and keep lower-confidence findings in the
  manager report until Tony chooses the split.

Ready-to-file items need concrete evidence, a target repo, an owner skill, and
the smallest safe implementation boundary. Items that depend on visibility,
family/media privacy, IP handling, priority, or creative direction stay in the
Tony-decision queue instead of becoming public issues.

When labels are useful, first list the repo's labels and reuse existing names.
Create missing standard swarm labels only when the manager has explicitly
approved GitHub mutation for that repo. If label creation is not approved,
include a `Suggested labels:` line in the draft or issue body instead.

## Guardrails

- Do not file duplicate issues; search first.
- Do not edit repos by default.
- Do not publish private family/career media details into public issues.
- Do not turn prototype-grade instrument packets into public-ready claims.
- For physical builds, separate observed evidence, assumptions, and validation
  gates.
- For implementation swarms, create isolated worktrees and draft PRs only after
  manager approval.
