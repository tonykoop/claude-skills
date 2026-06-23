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
- Each story body has an `## Implementation plan` — follow it. It names the
  files, interfaces, and tests. You are transcribing a finished design, not
  redesigning it. If a story's plan is genuinely missing or wrong, leave a
  comment on the story, skip it, and move to the next — do not block.

## Branch + PR
- Branch off clean `main` for every story: `git switch -c feat/<N>-<short-name>`.
- One story → one branch → one PR. Never bundle stories.
- PR title: `feat(#<N>): <story title>`.
- PR body: start with `Refs #<story-number>` (NOT `Closes` — a human merges and
  closes). Then 2–4 bullets: what changed, files touched, how it was verified.

## Merge + isolation
- **Never self-merge.** Open the PR and move on. The human merges.
- Always branch from `main`, never from another feature branch. Each branch
  recreates what it needs — if you need a type another open PR also adds,
  duplicate the small piece rather than depending on the unmerged branch.
- Do not rebase or resolve conflicts against unmerged sibling PRs.

## How to work
- Work **directly** in this one context. **No sub-agents, no Task tool** — a
  single context that holds the whole repo structure is faster than spawning
  fresh ones that must rediscover it.
- Prefer **additive** changes (new file / new section) over refactors or renames.
- Verify after every change with the fast suite, then move on:
  - Test: `<test command, e.g. npm test>`  (keep this under ~10s)
  - Lint/typecheck: `<lint/typecheck command, e.g. npm run check>`
- A story is done when its acceptance criteria pass and the suite is green.

## Termination signal
- When **every** story under Epic #<N> is implemented and has an open PR, stop
  and emit exactly:

  `DOMAIN DRAINED: <repo-slug>/<epic short-name>`

- Then summarize the PRs you opened. Do not start unrelated work.
```

## Usage notes

- **Keep the test command genuinely fast (<~10s).** The verify-and-move-on loop
  is the real throughput ceiling: ~4 min/PR fits ~40 PRs in 3h, a 5-min suite
  collapses that to 6–8. If the full suite is slow, point the `Test:` line at a
  fast subset and run the full suite in CI.
- **`Refs`, never `Closes`,** so the human stays the merge gate — mirrors the
  pipeline's `Refs #N` PR convention and the recovery-capture provenance rule.
- **No sub-agents is deliberate** for a tight single-domain sprint; do not
  "optimize" it back in. It is the opposite default from multi-domain work.
- If the epic has an unavoidable hard dependency between two stories, the filing
  step should have marked it `blocked-by #N`; add a one-line **Dependencies**
  note to the contract naming the order, rather than letting the agent discover
  it mid-loop.
- This contract assumes stories were filed as implementation plans. If they were
  not, fix the stories first — no loop contract rescues vague stories.
