---
name: gh-fix-ci
version: 0.1.0
last-updated: 2026-06-15
description: >-
  Use when a user asks to debug or fix failing GitHub PR checks that run in
  GitHub Actions; use `gh` to inspect checks and logs, summarize failure
  context, draft a fix plan, and implement only after explicit approval. Treat
  external providers (for example Buildkite) as out of scope and report only
  the details URL. Trigger phrases: "fix CI", "fix the failing checks", "debug
  this PR's checks", "why is CI red", "gh pr checks failing".
---

# gh-fix-ci — inspect and fix failing GitHub Actions PR checks

Use `gh` to locate failing PR checks, fetch the GitHub Actions logs for the
actionable failures, summarize the failure snippet, then propose a fix plan and
implement **only after explicit approval**.

> **Provenance:** ported from the Codex-only `codex/skills/gh-fix-ci` so the
> coding plugin has a Claude-usable variant. The Codex CLI copy (which leans on
> Codex's `create-plan` skill) is retained as a runtime variant; see
> `references/codex-variant.md`. Behavior is identical — only the plan-drafting
> step differs by runtime.

## Scope

- **In scope:** checks whose `detailsUrl` is a GitHub Actions run.
- **Out of scope:** Buildkite or any other external CI provider. Label those
  external and report only the details URL — do not attempt to drive them.

## Prerequisites

Authenticate with the GitHub CLI once (`gh auth login`), then confirm with
`gh auth status`. Repo + workflow scopes are typically required to read run
logs.

## Inputs

- `repo`: path inside the repo (default `.`).
- `pr`: PR number or URL (optional; defaults to the current branch's PR).
- `gh` authentication for the repo host.

## Quick start

```bash
python3 "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "<number-or-url>"
```

Add `--json` for machine-friendly output for summarization.

## Workflow

1. **Verify gh auth.** Run `gh auth status` in the repo. If unauthenticated,
   ask the user to run `gh auth login` (repo + workflow scopes) before going on.
2. **Resolve the PR.** Prefer the current branch PR
   (`gh pr view --json number,url`); if the user supplies a number/URL, use it.
3. **Inspect failing checks (GitHub Actions only).**
   - Preferred: run the bundled script (handles `gh` field drift and job-log
     fallbacks):
     `python3 "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "<n>"`
     (add `--json` for machine output).
   - Manual fallback:
     - `gh pr checks <pr> --json name,state,bucket,link,startedAt,completedAt,workflow`
       (if a field is rejected, rerun with the fields `gh` reports as available).
     - For each failing check, extract the run id from `detailsUrl` and run:
       - `gh run view <run_id> --json name,workflowName,conclusion,status,url,event,headBranch,headSha`
       - `gh run view <run_id> --log`
     - If the run log says it is still in progress, fetch job logs directly:
       - `gh api "/repos/<owner>/<repo>/actions/jobs/<job_id>/logs" > "<path>"`
4. **Scope non-GitHub-Actions checks.** If `detailsUrl` is not a GitHub Actions
   run, label it external and report only the URL. Do not attempt Buildkite.
5. **Summarize failures.** Failing check name, run URL (if any), and a concise
   log snippet. Call out missing logs explicitly.
6. **Draft a plan and get approval.** On Claude Code, draft a concise plan
   inline (or use a plan-drafting skill if one is available) and request
   approval before editing anything.
7. **Implement after approval.** Apply the approved plan, summarize diffs/tests,
   and ask about opening/updating a PR.
8. **Recheck status.** After changes, re-run the relevant tests and
   `gh pr checks` to confirm.

## Bundled resources

### scripts/inspect_pr_checks.py

Fetch failing PR checks, pull GitHub Actions logs, and extract a failure
snippet. Exits non-zero when failures remain so it can be used in automation.

```bash
python3 "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "123"
python3 "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "https://github.com/org/repo/pull/123" --json
python3 "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --max-lines 200 --context 40
```
