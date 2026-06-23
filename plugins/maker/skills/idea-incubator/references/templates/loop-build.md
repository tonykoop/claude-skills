# `loop-build.md` — Autonomous Build-Loop Contract Template

The canonical loop contract an autonomous build session (Alice–Iris agent grid)
Reads **first**, before touching any code. Its job is to resolve every recurring
decision upfront so the session never stalls to ask — branch naming, PR body
convention, merge policy, sub-agent policy, and a termination signal. A single
Sonnet session draining one well-structured epic this way pushed **40 PRs in
~3h**; the contract is what removed the dozens of round-trips that would
otherwise have interrupted it. See
[`../institutional-knowledge.md`](../institutional-knowledge.md) (lessons
"Ship a loop contract…" and "Write stories as implementation plans…") and the
[brainstorm-to-issues pipeline](../brainstorm-to-issues-pipeline.md)
"Agent-grid readiness" section.

## How to use it

- **Where it lives:** drop the filled-in block below at the **repo root** of the
  target repo as `loop-build.md` (sibling to `README.md`), so any session can
  `Read loop-build.md` as its first action. One per repo, or one per epic if a
  repo hosts several independently-drainable epics — name them
  `loop-build-<epic>.md` in that case.
- **Who fills it in:** the ingestion step fills the `<…>` placeholders when it
  files the epic, using the epic number, repo slug, and the repo's real
  test/lint commands. Do not ship it with placeholders unresolved.
- **The handoff prompt** that launches the session should say only: *"Read
  `loop-build.md` and drain the epic. Follow it exactly. Stop at the termination
  signal."* All the actual rules live in the file, not the prompt — that is what
  keeps the prompt short and the behavior reproducible across agents.

## Template (copy this block to `<repo-root>/loop-build.md` and fill the `<…>`)

```markdown
# Build Loop — <repo-slug> / Epic #<N>: <epic title>

You are draining this epic autonomously. Read this whole file first, then work
the loop below until the termination signal. Do not ask for confirmation on
anything covered here — it is already decided.

## What to work on
- Implement the **lowest-numbered open story** under Epic #<N>, in numeric order.
- **Skip already-done work FIRST.** Before implementing a story, check for a
  MERGED PR that references it (`Closes #<n>` / `Refs #<n>` / `feat(#<n>)`). If one
  exists, the story is done: comment "already delivered by PR #X", make sure the
  issue is closed, and move to the next. Never re-implement finished work.
- If **every** story under this epic is already closed/merged, do not start —
  emit `DOMAIN DRAINED: <repo-slug>/<epic> (already complete)` and stop.
- Each open story has an `## Implementation plan` — follow it. It names the files,
  interfaces, and tests. You are transcribing a finished design, not redesigning
  it. If a plan is genuinely missing or wrong, comment on the story, skip it, and
  move to the next — do not block.

## Branch + PR
- Branch off clean `main` for every story: `git switch -c feat/<N>-<short-name>`.
- One story → one branch → one PR. Never bundle stories.
- PR title: `feat(#<N>): <story title>`.
- PR body: start with `Closes #<story-number>` so the merge auto-closes the story.
  (The human still merges, so they stay the gate — this just removes the manual
  close that otherwise rots into agents re-doing finished work.) Then 2–4 bullets:
  what changed, files touched, how it was verified.
  - **Exception:** for recovery / import / provenance captures that must stay open
    as an evidence anchor, use `Refs #<story>` instead — intentional, not a slip.
  - Never `Closes` the **epic** — epics close via the reconcile sweep once all
    their stories are closed.

## Merge + isolation
- **Never self-merge.** Open the PR and move on. The human merges.
- Always branch from `main`, never from another feature branch. Each branch
  recreates what it needs — if you need a type another open PR also adds,
  duplicate the small piece rather than depending on the unmerged branch.
- Do not rebase or resolve conflicts against unmerged sibling PRs.

## Guardrails — STOP and ask before any of these
- Touching files outside this epic's scope, or refactoring/renaming shared code.
- Changing repo visibility, pushing to a public repo, or cross-linking a private
  repo from a public one (IP firewall).
- Deleting data, force-pushing, rewriting history, or committing a secret.

## How to work
- Work **directly** in this one context. **No sub-agents, no Task tool** — a
  single context that holds the whole repo structure is faster than spawning
  fresh ones that must rediscover it.
- Prefer **additive** changes (new file / new section) over refactors or renames.
- Verify after every change with the fast suite, then move on:
  - Test: `<test command, e.g. npm test>`  (keep this under ~10s)
  - Lint/typecheck: `<lint/typecheck command, e.g. npm run check>`
- After opening each PR, append one line to `loop-progress.md` at the repo root:
  `#<story> -> PR #<pr> (<short note>)`. This makes the sprint **resumable** — if
  your context compacts or you die, the next session reads this log plus the
  skip-done check and continues without re-doing or asking.
- A story is done when its acceptance criteria pass and the suite is green.

## Dependencies   ← fill only if this epic has a blocked-by ordering
- <e.g. "Story D recreates the audio interface from main if C's PR is unmerged.">

## Stop & escalate (break the loop and surface it)
- A spec is ambiguous or self-contradictory in a way the implementation plan
  doesn't resolve.
- A story would require a **Guardrails** action above.
- You've been blocked on the same thing twice — stop and report it; don't thrash.

## Termination signal
- When **every** story under Epic #<N> has an open PR (or is already
  closed/merged), stop and emit exactly:

  `DOMAIN DRAINED: <repo-slug>/<epic short-name>`

- Then summarize the PRs you opened. Do not start unrelated work.
```

## Usage notes

- **Keep the test command genuinely fast (<~10s).** The verify-and-move-on loop
  is the real throughput ceiling: ~4 min/PR fits ~40 PRs in 3h, a 5-min suite
  collapses that to 6–8. If the full suite is slow, point the `Test:` line at a
  fast subset and run the full suite in CI.
- **`Closes #<story>` for normal stories** (auto-closes on merge → no open-issue
  rot → agents stop re-doing finished work), **`Refs #<story>` only for
  recovery/provenance captures** that must stay open as an evidence anchor. Either
  way the human stays the merge gate — merging is the human action; `Closes` just
  removes the easily-forgotten manual close. Epics are never `Closes`d; they close
  in the reconcile sweep when all their stories are closed.
- **Skip-done + progress log make the loop self-reconciling and resumable.** The
  skip-done check stops re-work even if close-hygiene slips; `loop-progress.md`
  lets a fresh session resume mid-epic after a compaction or crash.
- **Guardrails + Stop-&-escalate** keep a beast-mode agent from sprawling outside
  the epic or tripping an IP-firewall / destructive action without a human.
- **No sub-agents is deliberate** for a tight single-domain sprint; do not
  "optimize" it back in. It is the opposite default from multi-domain work.
- If the epic has an unavoidable hard dependency between two stories, the filing
  step should have marked it `blocked-by #N`; add a one-line **Dependencies**
  note to the contract naming the order, rather than letting the agent discover
  it mid-loop.
- This contract assumes stories were filed as implementation plans. If they were
  not, fix the stories first — no loop contract rescues vague stories.
