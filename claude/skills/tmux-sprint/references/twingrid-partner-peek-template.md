# TwinGrid Partner Peek Handoff Template

Use this template for Phase 2 after both blind sides have completed. The
manager should write one compact reveal brief for all lanes, then generate one
Partner Peek assignment per side/lane.

```markdown
# TwinGrid Partner Peek

The blind A/B pass is complete. Read only your lane section in the reveal brief
and inspect your partner's output folder. Improve your own deliverable without
erasing blind-run evidence.

## Identity

- Round: {{round_id}}
- Lane: {{lane}}
- Side: {{side}}
- Runtime: {{runtime}}
- Your output folder: {{own_output_folder}}
- Partner output folder: {{partner_output_folder}}
- Reveal brief: {{reveal_brief_path}}
- Manager comparison: {{manager_comparison}}
- Newly available tools: {{tool_probe_summary}}

## Rules

- Read only your lane section in the reveal brief.
- Do not edit your partner's output folder.
- Keep original blind outputs intact where practical.
- Add clearly named v2 artifacts such as `partner-peek-improvements.md`,
  `v2-*`, validation logs, or supplemental structured records.
- Do not self-report elapsed time, context remaining, usage remaining, or pane
  status.
- If you make repo or skill changes, use the assigned isolated worktree and
  open a draft PR.
- If the improvement is artifact-only, do not manufacture a PR. Include
  PR-worthy recommendations in the improvement memo instead.
- If a required tool is missing, name the exact command/tool and install hint.

## Required Phase 2 Outputs

- `partner-peek-improvements.md` describing what was preserved, adopted, and
  rejected.
- A Partner Peek record as JSON or Markdown.
- Validation command list and result summary.
- A concrete skill-improvement recommendation when the combined A/B result
  exposes a repeatable process or skill gap.

## Partner Peek Record

Finish with a Partner Peek record containing:

- `lane`
- `side`
- `runtime`
- `files_added_or_changed`
- `partner_ideas_adopted`
- `validation_run`
- `pr_or_issues_opened`
- `combined_ab_should_feed_skill_improvement`
- `skill_improvement_recommendation`
- `notes_for_manager`

Do not include elapsed time, context remaining, usage remaining, or token
claims in the Partner Peek record.
```

## Reveal brief minimum

Each lane section should include both output paths, a two-to-four sentence
manager comparison, and the specific second-pass ask. Keep it compact so
agents use partner artifacts as evidence rather than rereading the whole round
transcript.
