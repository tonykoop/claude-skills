---
name: verification-gates
version: 0.1.0
last-updated: 2026-06-17
description: >-
  Run automated verification gates for agent-authored work when a headless
  runtime should decide pass/fail before human review: sandbox command
  execution, markdown and length linting, and URDF kinematic joint-limit
  checks. Use when the user asks for automated gates, generated-code sandbox
  validation, markdown/length linting, URDF robot output checks, or QA decision
  evidence. Do not use for benchmark score verification; use run-benchmark and
  the benchmark repo's own grader instead.
---

# Verification Gates

Use this skill when a PR, agent lane, or generated artifact needs a repeatable
machine gate before review. The output is a QA decision record that a release
or review skill can attach to a PR.

## Run

```bash
python3 plugins/coding/skills/verification-gates/scripts/verification_gates.py \
  --path <artifact-or-repo-path> \
  --qa-output qa-decision.json \
  --command "python3 -m unittest discover"
```

Run one or more `--command` values for project-specific tests. Commands are
executed without a shell and must be written as normal argv strings. A nonzero
exit code fails the sandbox execution gate.

## Gates

- **Sandbox execution** - runs each explicit `--command`, captures exit code,
  stdout/stderr snippets, and timeout state.
- **Markdown/length linter** - checks every `.md` file under `--path` as a
  rule matrix: UTF-8, nonempty content, trailing whitespace, tabs, line length
  (`--max-line-length`, default `120`), heading spacing, and fenced-code closure.
- **URDF kinematic check** - parses `.urdf` files and requires every
  `revolute` or `prismatic` joint to have a valid `<limit lower upper>` range.
  It also rejects negative `effort` or `velocity` values when present, missing
  parent/child links, missing axes on limited joints, invalid continuous-joint
  limit tags, and mimic references to missing joints. Add
  `--strict-urdf-joint-types` when unknown joint types should fail instead of
  being ignored.

## Output Contract

The script writes a JSON QA decision:

```json
{
  "schema_version": 1,
  "decision": "pass",
  "checks": [
    {
      "gate": "markdown:max-line-length",
      "path": "README.md",
      "status": "pass",
      "detail": "line lengths passed",
      "metadata": {}
    }
  ]
}
```

Use the JSON as the source of truth in PR bodies or release tickets. Do not
translate a failing gate into prose-only approval.

## Boundaries

- The gate runner does not install dependencies, download tools, or mutate the
  project under test.
- It does not certify physical safety, robot build safety, or benchmark score
  validity. Those need domain-specific review.
- It is safe to run before human review, but it does not replace review.
