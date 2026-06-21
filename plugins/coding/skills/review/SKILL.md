---
name: review
description: >-
  Review a single open PR and post a VERIFY-FIRST structured APPROVE/CHANGES verdict via
  the gh CLI. Never merges. Use when the user runs /review <PR#> (optionally with a repo),
  pastes a PR URL, or asks to "review", "verdict", or "check" a specific PR. For the
  broader review-AND-merge / queue workflow use merge-review instead — this skill is the
  focused, verdict-only, no-merge pass.
---

# PR Review Verdict

Post a structured verdict on ONE open PR. **VERIFY-FIRST** (prior CHANGES verdicts are
often stale once fixes land). **Never merge** unless the user explicitly says to.

> Relationship to `merge-review`: that skill owns the full review→merge queue (codex
> wait-gate, merge ordering, post-merge prune). This one is the lightweight gate reviewer —
> gather evidence, post exactly one verdict, stop. The supervisor (or `merge-review`)
> merges on the posted verdict.

## Argument

`$ARGUMENTS` is the PR — a number (`114`), a number + repo (`114 -R owner/repo`), or a PR
URL. If no repo is given, default to the current repo (`gh repo view --json nameWithOwner`).

## 1. Gather state (VERIFY-FIRST)

Re-check the **current** state before judging — do not trust earlier verdicts:

```bash
PR=<num>; REPO=<owner/repo>
gh pr view $PR -R $REPO --json state,mergeStateStatus,statusCheckRollup,headRefOid,files,body,reviews,comments
gh pr diff $PR -R $REPO
```

- Confirm the PR is still **open** and read the **latest** commit (`headRefOid`) — a prior
  `CHANGES` verdict may already be addressed by newer commits.
- Read the linked issue if referenced, to judge scope.

## 2. Re-verify CI and latest commits

- Check `statusCheckRollup` against the **current** HEAD. If red, inspect the failing run
  (`gh run view <id> -R $REPO --log-failed`) before deciding — distinguish real failures
  from infra/billing-abort noise (document a waiver if it's the known spend-limit pattern).
- If there's a prior `CHANGES` comment, decide whether the cited blocker is now resolved on
  HEAD. If it is, the verdict flips to APPROVE — say so explicitly.

## 3. Judge

Scope match, test coverage for changed behavior, CI green (or documented waiver), code
quality (no dead code / panics / leaked secrets), implementation correctness, merge safety.

## 4. Post the verdict (never merge)

```bash
gh pr comment $PR -R $REPO --body "$(cat <<'V'
## Review — <APPROVE | CHANGES>

**Model:** <model>  •  **HEAD:** <short-sha>  •  **CI:** <green/waived/red>

### Findings
- <specific finding citing file:line>

### What looks good
- <positive callout>
V
)"
```

- For a quick two-model gate, a single line is fine: `Model: <model> — APPROVE: <reason>`
  or `CHANGES: <reason>`.
- If a prior CHANGES is now resolved, note `(prior CHANGES resolved on <sha>)`.

**Do NOT run `gh pr merge`** unless the user explicitly asked to merge. Report the verdict
and stop.

## Example

`/review 114`  → gathers #114's current state, re-verifies CI on HEAD, posts an
APPROVE/CHANGES verdict comment, and stops (no merge).
