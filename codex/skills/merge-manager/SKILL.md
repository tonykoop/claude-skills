---
name: merge-manager
description: "Use when acting as sprint merge-manager across one or more repos: review PRs against their referenced GitHub issues, make small follow-up fixes when warranted, request changes on larger gaps, merge in dependency order, keep a sprint document current, post issue or PR comments, and generate next handoff prompts for agent lanes"
---

# Merge Manager

Operate as the repo operator for a multi-lane sprint, not just a git merger.

Core responsibilities:

- review open PRs against the referenced GitHub issues
- decide merge vs quick fix vs requested changes
- merge in dependency order across repos
- keep a sprint document current
- post clear status on issues / PRs
- generate next handoff prompts for agent lanes after each completion

Core principle:

**Do not treat "PR exists" as "issue solved."** Verify the code, the validation, and the issue fit before merging.

## When to use

- Several agent lanes are landing PRs during the same sprint
- Work spans multiple repos and merge order matters
- You need to review whether a PR really closes its linked issue
- You need to keep a sprint / lane tracker current as merges happen
- You need to hand agents their next issue after each merge

## Operating model

Think in this order:

1. inventory current PRs, issues, and sprint document state
2. review the PR against the issue, not just the diff
3. decide:
   - merge as-is
   - make a quick fix yourself on the PR branch, then merge
   - request changes on the PR
4. update sprint tracking
5. produce the next handoff prompt for that lane unless the user says not to

## Core review loop

```bash
gh search issues --owner <org> --state open --limit 100 --json repository,number,title,updatedAt,labels,url
gh issue view <issue-num> --repo <org>/<repo>
gh pr view <pr-num> --repo <org>/<repo> --json files,commits,body,statusCheckRollup
gh pr diff <pr-num> --repo <org>/<repo>
```

For every PR, verify all of the following:

1. the PR actually addresses the referenced issue scope
2. the implementation matches the current live contracts, routes, schemas, or scripts
3. validation is relevant to the changed behavior
4. there is no merge-blocking regression or unsafe side effect

If a PR says `Closes #N`, confirm the diff really closes that gap. If it only adds artifacts/docs while the underlying contract is still wrong, do not merge.

## Decision rules

### Merge as-is

Merge when:

- the issue scope is actually covered
- validation is credible
- no merge-blocking regression appears in review
- any red CI is clearly repo/account noise rather than code failure

### Fix it yourself, then merge

Take the quick-fix path only when the remaining problem is small, local, and safe:

- trivial conflict resolution
- small script/manifest/config fix
- obvious missing guard or parameter mismatch
- small docs alignment fix

Typical flow:

```bash
git fetch origin <branch> main
git worktree add /tmp/<temp-dir> origin/<branch>
git -C /tmp/<temp-dir> switch -c <fix-branch> origin/main
git -C /tmp/<temp-dir> cherry-pick <commit-or-range>
# resolve
git -C /tmp/<temp-dir> push --force-with-lease origin HEAD:<branch>
```

Then re-review and merge.

### Request changes

Request changes when the PR needs a real rework:

- wrong contract / API shape
- issue scope not actually closed
- unsafe persistent side effects
- missing core tests for the changed behavior
- branch is conceptually wrong, not just slightly off

If formal review permissions are awkward, post a PR comment instead of blocking on tooling.

## PR and issue comments

Use comments as part of the operator workflow.

Post on the PR when:

- leaving a requested-changes blocker
- explaining a merge-manager quick fix you applied
- documenting why a red check was treated as non-blocking

Post on the issue when:

- a merge closes it
- downstream work is unblocked
- follow-up scope was split into a new issue

Commands:

```bash
gh pr comment <pr-num> --repo <org>/<repo> --body "..."
gh issue comment <issue-num> --repo <org>/<repo> --body "Merged in <sha>; downstream unblocked."
```

Comment style:

- concrete
- issue-focused
- cite the exact mismatch or missing behavior

## Handling red CI

Do not blindly trust or reject red checks.

If checks are red:

1. inspect the failed logs
2. if the job has no steps/logs and matches known billing/spend-limit behavior, treat it as infra/account noise
3. if the job shows a real code failure, do not merge until resolved

Useful commands:

```bash
gh run view <run-id> --repo <org>/<repo> --log-failed
gh pr view <pr-num> --repo <org>/<repo> --json statusCheckRollup
```

## Sprint document maintenance

Keep the sprint doc current after meaningful progress.

Update it when:

- PRs merge
- new issues are filed from TDD or review
- priorities change
- tomorrow's lane plan changes

A good sprint doc should include:

- current merged PRs and merge SHAs
- open PR queue and blockers
- reviewed open issues, grouped by repo or priority
- tomorrow's priority order
- recommended next lane assignments

If the existing doc is badly stale, prefer rewriting it cleanly over patching stale statuses one by one.

## Handoff prompts for lanes

After a lane merges cleanly, generate the next prompt unless the user says not to.

Each prompt should include:

- repo path
- dedicated worktree path
- branch name
- exact issue ownership
- scope constraints
- validation requirements
- PR body requirement with `Closes #<issue>`
- `Do not merge`

Prompt shape:

```text
You own <org>/<repo>#<issue>: <title>.

Repo: <abs-path>
Worktree: <abs-path>
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

Push your branch and open a PR against main. Reference "Closes #<issue>" in the PR body. Do not merge.
```

Prefer the next prompt to stay on the active sprint critical path, not just any open issue.
