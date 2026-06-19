---
name: run-swarm
version: 1.3.0
last-updated: 2026-06-19
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
severity/readiness, Tony decision needed (if any), recommended owner skill, and
the smallest safe implementation boundary.
```

## Outputs

Manager collects:

- combined issue/report table
- machine-readable queue artifacts when the swarm is shaping a sprint queue:
  `issue_landscape.json` and `issue_landscape.csv`, following
  `references/queue-output-schema.md`
- duplicate/overlap notes
- top 5 next-sprint recommendations
- skill-owner routing for each actionable item
- "ready to implement now" versus "needs Tony decision" split with reasons
- archive/PR follow-through check so swarm artifacts do not stay hidden in
  `/tmp`

### Machine-Readable Queue Output

When the swarm is used for backlog triage, sprint shaping, or a Personal
GitHub audit, emit a human summary plus JSON/CSV artifacts. Keep the run
read-only: these files describe the issue landscape and manager queues, but
they do not edit sprint docs, repos, labels, issues, or PRs by themselves.

Use the queue names from `references/queue-output-schema.md`:

- `ready-to-implement`
- `tony-decision`
- `archive-or-watch`

Include both classification lenses when they matter:

- `strict_dispatch_bucket`: separates actual skill-development work from
  content-production, capture, public-deliverable, or privacy-gated work.
- `owner_skill_bucket`: names the skill that should own the next decision or
  implementation boundary, even when the item is not safe to dispatch yet.

Also include skill-owner counts and queue counts so a sprint manager can size
lanes without re-parsing prose.

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

### Manager Queue Rules

Classify every actionable item into exactly one queue:

- **Ready for implementation swarm**: enough evidence, repo context, owner
  skill, and acceptance shape exist for an agent to open an isolated worktree
  and draft a PR without asking Tony for taste, privacy, priority, or scope
  decisions.
- **Needs Tony decision**: the next step depends on Tony choosing visibility,
  audience, priority, cost, family/media privacy, IP/patent handling, or which
  creative direction to pursue.
- **Archive or watch**: useful finding, but not ready for issue or
  implementation because evidence is thin, it is an exact duplicate, it is a
  weak cluster that needs more evidence, or it should stay as background
  context.

For each ready item, name the owner skill and implementation boundary, such as
`makerspace -> one build-packet PR in <repo>` or `skills-meta -> metadata drift
audit issue only`. For each Tony-decision item, phrase the decision as a direct
question and name the safe default if no decision is made.

## Cache Contract

Between audit runs, `run-swarm` writes a persistent issue-scout cache to
`/tmp/tonykoop-run-swarm-issue-scout-results/`. Agents read from this cache
instead of calling `gh issue list` for every sub-task.

Before dispatching agents, the manager checks cache freshness using the rules
in `references/freshness-contract.md`. Fresh = within 24 hours and same mode.
Stale or absent = refresh all four cache files before the swarm starts.

The cache files and their schemas are documented in
`references/issue-scout-schema.md`.

Key rules:
- Never commit cache files to any repo. They live in `/tmp/` and are ephemeral.
- Agents receive cache paths in their prompt preamble; they do not call
  `gh issue list` directly unless the cache is marked stale.
- `closed-issues.json` (7-day window) is used only for duplicate detection.

## Guardrails

- Do not file duplicate issues; search first.
- Do not edit repos by default.
- Do not publish private family/career media details into public issues.
- Do not turn prototype-grade instrument packets into public-ready claims.
- For physical builds, separate observed evidence, assumptions, and validation
  gates.
- For implementation swarms, create isolated worktrees and draft PRs only after
  manager approval.
