# TwinGrid Blind A/B Handoff Template

Use this template for Phase 1 of a TwinGrid round. Generate one assignment per
lane side. The Claude side is usually side A and the Codex side is usually side
B, but the template should name the actual runtime explicitly.

```markdown
# TwinGrid Blind Dispatch

You are one side of a TwinGrid A/B pair. Work independently. Do not inspect
your partner's output or shared reveal materials during the blind pass.

## Identity

- Round: {{round_id}}
- Lane: {{lane}}
- Side: {{side}}
- Runtime: {{runtime}}
- Paired side/runtime: {{partner_side}} / {{partner_runtime}}
- Task: {{task}}
- Named skill(s): {{skills}}
- Output folder: {{output_folder}}
- Assigned worktree: {{worktree_or_none}}
- Branch: {{branch_or_none}}
- Issue: {{issue_or_none}}

## Rules

- Use a fresh task context, but keep the current runtime session.
- Load and follow the named skill(s).
- Write outputs only under the output folder or assigned worktree.
- Do not edit shared checkouts unless this assignment explicitly requires a
  repo change.
- Do not open a PR unless you make concrete repo changes.
- Preserve evidence and validation logs.
- Do not self-report elapsed time, context remaining, usage remaining, or
  pane status. The manager captures those from tmux/statusline telemetry.
- If a required tool is missing, name the exact command/tool and install hint.
- If the task references an image or file that is not available in this
  runtime, state the limitation at the top of the artifact and continue only
  in the appropriate degraded/no-file intake mode.

## Required Outputs

For content-generation rounds:

- Primary artifact(s) requested by the task.
- `agent_record.json` or `agent_record.md`.

For skill-development rounds:

- Focused repo change in the assigned worktree.
- Validation output.
- Commit and draft PR when concrete repo changes are made.

## Agent Record

Finish with a TwinGrid agent record containing:

- `lane`
- `side`
- `runtime`
- `actual_model`
- `task`
- `output_folder`
- `artifacts_produced`
- `validation_run`
- `subjective_quality_notes`
- `would_route_here_again`
- `ab_comparison_notes_for_manager`

Do not include elapsed time, context remaining, usage remaining, or token
claims in the agent record.
```

## Content-generation versus skill-development knobs

Use `worktree_or_none: none`, `branch_or_none: none`, and `issue_or_none: none`
for artifact-only rounds. For skill-development rounds, set all three and add
repo-specific guardrails such as "work only in this worktree" and "open a draft
PR against main."
