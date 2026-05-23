---
name: merge-review
version: 0.1.0
last-updated: 2026-05-20
description: >-
  Review one or more open PRs across WRFCoin repos. For each PR: read the linked issue,
  review the diff, check CI, post a structured review comment, then merge or request changes.
  Use when the user says "review PR", "check this PR", "review and merge", "merge PR #N",
  or pastes a PR URL.
---

# PR Review

Review open PRs against their linked GitHub issues. Post structured findings before
any merge decision.

## Workflow

### 1. Gather PR details

```bash
gh pr view <num> --repo wrfcoin/<repo> \
  --json url,state,mergeStateStatus,files,commits,statusCheckRollup,body,reviews
gh pr diff <num> --repo wrfcoin/<repo>
gh issue view <issue-num> --repo wrfcoin/<repo> --json title,body
```

### 2. Notify the issue

```bash
gh issue comment <issue-num> --repo wrfcoin/<repo> --body \
  "Merge-manager reviewing PR #<pr-num> for this issue. Will post findings shortly."
```

### 3. Codex review wait-gate (MANDATORY for enabled repos)

Codex-enabled repos: **core4, infra, frontend, backend**. (mobile,
storage-providers, defi-protocols, security-testing, smart-contracts
do NOT have codex auto-review configured — skip the gate there.)

For any PR in an enabled repo:

```bash
REPO=<repo>; PR=<num>
# Codex triggers on "ready for review" state — if the PR is draft, flip
# it first (`gh pr ready $PR --repo wrfcoin/$REPO`). Then wait up to 120s
# for a review to land against the current HEAD.

HEAD_SHA=$(gh api repos/wrfcoin/$REPO/pulls/$PR --jq '.head.sha')
deadline=$((SECONDS + 120))
while [[ $SECONDS -lt $deadline ]]; do
  latest=$(gh api repos/wrfcoin/$REPO/pulls/$PR/reviews \
    --jq '[.[] | select(.user.login | contains("codex"))][-1] // {}')
  latest_commit=$(echo "$latest" | jq -r '.commit_id // ""')
  if [[ "$latest_commit" == "$HEAD_SHA" ]]; then
    echo "codex reviewed HEAD $HEAD_SHA"
    break
  fi
  sleep 8
done

# After the gate, pull line-comments on the current HEAD:
gh api repos/wrfcoin/$REPO/pulls/$PR/comments \
  --jq '.[] | select(.user.login | contains("codex")) | select(.commit_id == "'$HEAD_SHA'")'
```

**Merge only if** (a) codex reviewed HEAD with zero P1 concerns, OR
(b) 120s elapsed without a fresh review (timeout). When timing out, note
`codex-timed-out` in the merge comment so the record is clear.

If codex flags P1 concerns, post them as manager-required revisions and
CHANGES REQUESTED verdict — do not merge.

For repos without codex config (mobile etc.), skip this step entirely and
note `no-codex-configured` in the review comment's CI row.

### 4. Review checklist

For every PR, verify ALL of the following:

1. **Scope match** — Does the PR actually address what the issue asks for?
2. **Test coverage** — Tests for the changed behavior (not just "tests exist")?
3. **CI status** — Green? If waived, document why.
4. **Code quality** — Dead code, panics in non-test code, security issues?
5. **Implementation correctness** — Does the code do what it claims? Edge cases?
6. **Merge safety** — Risk of regression? Shared state, public APIs, consensus logic?
7. **Codex review** — HEAD reviewed with zero P1 concerns (enabled repos) OR explicit `no-codex-configured` / `codex-timed-out` note.

### 5. Post structured review comment (MANDATORY)

```bash
gh pr comment <pr-num> --repo wrfcoin/<repo> --body "$(cat <<'REVIEW'
## Merge-Manager Review

**Issue:** #<issue-num> — <issue title>
**Verdict:** APPROVE / CHANGES REQUESTED

### Checklist
| Check | Result | Notes |
|-------|--------|-------|
| Scope match | pass/fail | ... |
| Test coverage | pass/fail | ... |
| CI status | pass/fail/waived | ... |
| Code quality | pass/fail | ... |
| Implementation | pass/fail | ... |
| Merge safety | pass/fail | ... |

### Findings
#### Blockers (must fix before merge)
- [ ] <specific finding citing file:line>

#### Warnings (should fix, not blocking)
- [ ] <specific finding>

#### What looks good
- <positive callout>
REVIEW
)"
```

### 6. Merge decision

- **APPROVE**: All 6 checks pass → merge, post closing comments on PR AND issue
- **Quick fix**: Truly trivial fix (typo, missing import) → fix on branch, post comment, merge
- **CHANGES REQUESTED**: Any blocker → post review, comment on issue, write revision handoff

### 7. After merge

Post closing comments explaining HOW the code addresses the issue:

```bash
gh pr comment <pr-num> --repo wrfcoin/<repo> --body \
  "Merged to main (<sha>). <1-2 sentences citing key changes.>"
gh issue comment <issue-num> --repo wrfcoin/<repo> --body \
  "Closed by PR #<pr>. <1-2 sentences citing file:line.>"
```

### 8. Post-merge cleanup (MANDATORY)

After each successful merge, prune the merged branch and reset/remove its
worktree. Prevents the disk-bloat failure mode from the 2026-05 WSL2 vhdx
overflow incident — see `feedback_post_merge_prune.md`.

```bash
~/.claude/skills/disk-cleanup/scripts/prune-after-merge.sh \
  --repo <repo> --branch <head-branch> --apply --json
```

The script is safe-by-default:

- Refuses unmerged branches, `main`/`master`/`HEAD`, and live-pattern branches.
- Refuses dirty worktrees (re-checks immediately before acting — active agent
  work is never destroyed).
- Persona worktrees (`<repo>-{alice,bob,cindy,dan,elsa,frank}`) are **reset**
  to a clean main (`git checkout -B park/<persona>-clean origin/main` +
  `git clean -fdx` + `cargo clean`), not removed — they are semi-permanent.
- Ephemeral worktrees (`agent-*`, `/tmp/<temp-dir>`, etc.) are removed entirely.

If `skipped_dirty` shows up for a worktree you expected to be parked, that
worktree is currently being used — leave it alone. The supervisor's periodic
sweep (`prune-after-merge.sh --sweep`) will pick it up on a later pass.

## Quick-fix-then-merge

When the remaining problem is small, local, and safe — trivial conflict, small
script/manifest/config fix, obvious missing guard or parameter mismatch, docs
alignment — fix it on the PR branch yourself and re-review rather than bouncing
back to the persona. Typical flow:

```bash
git fetch origin <branch> main
git worktree add /tmp/<temp-dir> origin/<branch>
git -C /tmp/<temp-dir> switch -c <fix-branch> origin/main
git -C /tmp/<temp-dir> cherry-pick <commit-or-range>
# resolve
git -C /tmp/<temp-dir> push --force-with-lease origin HEAD:<branch>
```

Document the quick fix in the PR comment so the record is clear, then re-run
the review checklist and merge. Take this path only for trivially safe scope —
anything touching contracts, schemas, consensus, or shared types goes back to
the persona as CHANGES REQUESTED.

## Handling red CI

Don't blindly trust or reject red checks.

1. Inspect the failed logs:
   ```bash
   gh run view <run-id> --repo wrfcoin/<repo> --log-failed
   ```
2. If the job has no steps/logs and matches the known billing/spend-limit
   pattern, treat it as infra/account noise and document the waiver in the
   review comment's CI row.
3. If the job shows a real code failure, do not merge until resolved.

## Parallel review for 3+ PRs

When the queue has three or more open PRs across repos, fan out one
`general-purpose` Agent per PR (single message, all calls in parallel) rather
than reviewing serially.

Each sub-agent gets a prompt that names the repo + PR number, instructs it to
follow steps 1-4 of the workflow above (gather, notify, codex wait-gate,
review checklist) **read-only** — no merging, no edits, no posting — and
return a structured verdict block:

```
VERDICT: APPROVE | CHANGES_REQUESTED | BLOCKED
REPO: wrfcoin/<repo>
PR: #<number>
ISSUE: #<issue-num>
BLOCKERS: <comma-separated list, or "none">
WARNINGS: <comma-separated list, or "none">
REVIEW_COMMENT: |
  ## Merge-Review — PR #<number>
  <full review comment body following step 5's template>
```

Sub-agent config: `subagent_type: general-purpose`, `model: sonnet` (Opus is
3× slower with no quality lift for review-only work), `name:
review-<repo>-<pr-number>`.

After all sub-agents return, the main session aggregates into a results table
and then processes the actual merges **sequentially in dependency order**
(steps 5-8 per PR — never parallelize the merge step, because dependency order
matters).

## Merge order (dependency-first)

1. `shared-protocol`, `primitives` (upstream)
2. `consensus-engines`, `native-chain` (runtime)
3. `backend` (depends on core4)
4. `infra` (observability)
5. `smart-contracts` (independent)
6. `frontend`, `mobile` (consumer-facing)
