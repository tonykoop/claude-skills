---
name: sweep
description: >-
  Sweep open PRs across a set of repos, skip already-reviewed/merged ones, VERIFY-FIRST
  check CI, post a verdict comment on each qualifying PR, and report the queue count.
  Never merges. Use when the user runs /sweep (optionally with repos or a branch filter),
  or asks to "sweep the PR queue", "review all open PRs", or "do a review pass". This is
  the multi-PR loop that fans the `review` skill's verdict logic across repos.
---

# PR Review Sweep

Cross-repo verdict pass. List open PRs, **skip** the ones already reviewed at their current
HEAD (and merged/closed), **VERIFY-FIRST** the rest, post one verdict comment each, and
report the queue count. **Never merge.**

> Per-PR verdict logic is the `review` skill — apply it inline here; do not fan out
> sub-agents (under load, per-PR review sub-agents hit GitHub secondary rate-limits and
> hang). Work the queue **serially / a few inline per turn**.

## Argument

`$ARGUMENTS` is optional:
- A space-separated repo list (`tonykoop/StudioPipeline wrfcoin/core4`) — sweep exactly these.
- A branch-prefix filter (`sg2/`, `sg/`, `feat/`) — only PRs whose head branch matches.
- Empty → use the **default working set** below and the default sprint branch filter.

**Default working set** (the "sg/" sprint repos — edit to taste): the repos with active
sprint PRs across `tonykoop`, `wrfcoin`, and `studiopipeline`. Discover them when unsure:

```bash
# repos under an owner that currently have open PRs
for owner in tonykoop wrfcoin studiopipeline; do
  gh repo list "$owner" --no-archived --limit 200 --json nameWithOwner -q '.[].nameWithOwner'
done
```

**Default branch filter:** `sg2/|sg/|feat/|story/|fix/|patent/|ip/|episode-plan/|cadfit/|opus-|cbuild|sb-`
(the sprint branch families). Adjust per the user's request.

## 1. List candidates (keep gh load light — list first)

For each repo, list open **non-draft** PRs whose head branch matches the filter:

```bash
REPO=<owner/repo>
gh pr list -R $REPO --state open --json number,mergeStateStatus,isDraft,headRefName,headRefOid \
  -q '.[] | select(.isDraft==false) | select(.headRefName|test("<branch-filter>")) | "\(.number)\t\(.headRefOid)\t\(.headRefName)"'
```

## 2. Skip already-reviewed / merged (VERIFY-FIRST skip)

For each candidate, pull the last verdict comment and compare to current HEAD:

```bash
gh pr view $PR -R $REPO --json comments,headRefOid \
  -q '{head:.headRefOid, last:([.comments[]|select(.body|test("Model:|APPROVE|CHANGES"))]|last|.body)}'
```

- **Skip** if a verdict exists AND no new commits landed since it (verdict still reflects HEAD).
- **Do NOT skip** if commits landed after the last verdict — HEAD moved, so a prior CHANGES
  may now be resolved. Re-review it (this is the VERIFY-FIRST core).
- Merged/closed PRs never appear (state==open filter), but double-check before posting.

## 3. Verdict each qualifying PR (apply the `review` skill inline)

For each PR that needs review, run the `review` flow: gather state + diff, re-verify CI on
**current HEAD** (distinguish real red from billing-abort noise), judge, and post exactly
one comment:

```bash
gh pr comment $PR -R $REPO --body "Model: <model> — APPROVE: <reason>"   # or CHANGES: <reason>
```

If a prior CHANGES is now resolved on HEAD, note `(prior CHANGES resolved on <sha>)`.

**Never run `gh pr merge`.** The supervisor / `merge-review` merges on the posted verdicts.

## 4. Report the queue

Print a compact summary and the **queue count**:

```
Swept N repos · M open candidates · K reviewed this pass · S skipped (already current) · 0 merged
| repo#PR | branch | CI | verdict |
|---------|--------|----|---------|
| ...     | ...    | .. | APPROVE/CHANGES/skipped |
```

Report the count of PRs still awaiting action (CHANGES outstanding + anything unreviewed),
so the user knows the live queue depth.

## Cadence note (for autonomous loops)

When run on a schedule (sprint-supervisor / ScheduleWakeup), stretch the cadence as the
queue drains and tighten it when new PRs appear. An empty sweep is a valid no-op — report
`queue empty` and stop; do not invent work.

## Example

`/sweep` → default sprint repos + branch filter.
`/sweep sg2/` → only PRs on `sg2/*` branches.
`/sweep tonykoop/StudioPipeline tonykoop/claude-skills` → just those two repos.
