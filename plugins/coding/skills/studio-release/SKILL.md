---
name: studio-release
version: 0.2.0
last-updated: 2026-06-18
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

This is the back-end release engine: the downstream counterpart to
`idea-incubator`. Where idea-incubator is the front-end ingest shovel, this gate
clears the drain — it runs headless validation, scores a confidence value, routes
the work through the human-in-the-loop circuit breaker, assigns a distinct-model
QA auditor (so the agent that produced an asset never certifies it), and stages a
publish-ready bundle for the Studio Pipeline.

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
     --ref "PR #123" \
     --deploy-target studio-pipeline \
     --creator-agent <agent> --creator-model <model>
   ```

   `--creator-agent`/`--creator-model` are optional. When supplied, the gate
   routes the candidate to a distinct-model auditor through the governance
   adversarial-QA router (it auto-discovers the repo's `governance/` directory,
   or pass `--roster <dir>`). Omit them and auditor routing is recorded as
   skipped.

3. Review the generated `qa-decision.json`. A passing bundle has
   `decision: "pass"` and no failed checks. The `routing` field tells you
   whether the gate is confident (`auto_release_eligible`), needs a human on an
   ambiguous case (`escalate_human_review`), or is `blocked`.
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
- A dirty source checkout fails the gate unless `--allow-dirty` downgrades it to
  a warning.

If a repository has stronger local checks, run those before or after this gate
and add their exact command lines to the approve/deploy ticket.

## Confidence Routing (Circuit Breaker)

The gate scores a confidence value and a routing disposition so a human only
spends attention on the ambiguous minority:

- `auto_release_eligible` (confidence ~0.95) - clean pass, no warnings.
- `escalate_human_review` (confidence 0.55-0.85) - warnings present (e.g. an
  allowed-dirty checkout); the ambiguous ~10% that needs eyes.
- `blocked` (confidence 0.0) - a failed check, or a requested auditor that could
  not be routed to a distinct model family.

A human reviewer always signs the single approve/deploy ticket; the routing only
governs how much scrutiny the pipeline asks for.

## Adversarial QA Auditor

When `--creator-agent`/`--creator-model` are supplied, the gate calls the
governance `review_router` (claude-skills#256) to assign a QA auditor running a
DISTINCT model family from the creator. The agent that produced an asset never
certifies it. If no distinct-family auditor can be certified, the routing fails
closed to `blocked`. The assignment is recorded in both `qa-decision.json` and
the ticket. Routing is skipped cleanly (not failed) when creator identity is
absent or the governance modules are not on disk, keeping the skill portable.

## Output Contract

Every staging directory must contain:

- `source/` - the staged copy of the release candidate.
- `qa-decision.json` - machine-readable checks, timestamps, source path, ref,
  decision, confidence, routing, and auditor assignment.
- `publish-manifest.json` - publishing metadata for the Studio Pipeline: deploy
  target, ref, decision/confidence/routing, the assigned auditor, and a
  checksummed (`sha256`) inventory of every staged artifact.
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
