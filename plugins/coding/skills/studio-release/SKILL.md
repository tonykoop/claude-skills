---
name: studio-release
version: 0.1.0
last-updated: 2026-06-17
description: >-
  Verify and stage an agent-produced skill, script, or release bundle when a
  feature branch reaches pull-request review or the end of an assigned work
  block. Use when the user says to prepare a studio release, run the studio
  release gate, package a verified staging bundle, create an approve/deploy
  ticket, or QA an agent branch before handoff. Do not use for raw idea capture
  or backlog shaping; use idea-incubator for upstream brainstorm intake.
---

# Studio Release

Use this skill when work is ready to leave an agent lane and enter human review.
The goal is not to publish automatically. The goal is to produce a small,
auditable staging bundle with validation evidence and one explicit
approve/deploy ticket.

## Trigger Points

- A feature branch has an open PR and needs release QA evidence.
- A Gantt block, sprint lane, or agent assignment is done and needs handoff.
- A skill, command, hook, benchmark, or script needs headless lint/sandbox
  validation before it is copied into a studio pipeline.

## Workflow

1. Confirm the source path and issue/PR identifier. If the source path is dirty,
   include the dirty-state note in the ticket instead of hiding it.
2. Run the release gate:

   ```bash
   python3 plugins/coding/skills/studio-release/scripts/studio_release_gate.py \
     --source <path> \
     --staging-root dist/studio-release \
     --ticket-title "Approve/deploy <name>" \
     --ref "PR #123"
   ```

3. Review the generated `qa-decision.json`. A passing bundle has
   `decision: "pass"` and no failed checks.
4. Attach or paste the generated `approve-deploy-ticket.md` into the PR body or
   review thread.
5. Stop at human approval. Do not deploy, publish, tag, or copy into live
   installs unless the user explicitly asks for that separate action.

## Validation Gate

The bundled gate is intentionally dependency-light so it can run in headless
sandboxes:

- Markdown files must be readable, nonempty, free of tab characters, and free
  of trailing whitespace.
- Python files are compiled with `py_compile`.
- Shell scripts are checked with `bash -n` when Bash is available.
- The staged bundle includes a copied source tree, `qa-decision.json`, and
  `approve-deploy-ticket.md`.

If a repository has stronger local checks, run those before or after this gate
and add their exact command lines to the approve/deploy ticket.

## Output Contract

Every staging directory must contain:

- `source/` - the staged copy of the release candidate.
- `qa-decision.json` - machine-readable checks, timestamps, source path, ref,
  and final decision.
- `approve-deploy-ticket.md` - the single human review ticket with changed
  behavior, validation, known gaps, reviewer focus, and deploy bar.

## Boundaries

- Do not self-certify release quality. The gate produces evidence; a reviewer
  makes the release decision.
- Do not include private credentials, local auth files, or generated secrets in
  the staged source.
- Do not use this skill for benchmark result verification; use `run-benchmark`
  and the benchmark repo's own integrity contract.
- Do not use this skill for sprint supervision or PR merging; use
  `sprint-supervisor` or `merge-review`.
