---
name: merge-review
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

## Merge order (dependency-first)

1. `shared-protocol`, `primitives` (upstream)
2. `consensus-engines`, `native-chain` (runtime)
3. `backend` (depends on core4)
4. `infra` (observability)
5. `smart-contracts` (independent)
6. `frontend`, `mobile` (consumer-facing)
