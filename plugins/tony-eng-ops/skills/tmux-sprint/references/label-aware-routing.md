# Label-Aware Routing

Issue labels are sprint inputs, not decorative metadata. The manager preserves
them from planning through dispatch so agents receive the right work batch, the
right model recommendation, and the right review gate.

## Label Classes

| Label class | Example | Manager use |
| --- | --- | --- |
| `skill:*` | `skill:tmux-sprint` | Groups issues by owning skill or workflow. |
| `artifact:*` | `artifact:validation-loop` | Names the expected deliverable type. |
| `risk:*` | `risk:high` | Raises model strength and review scrutiny. |
| `readiness:*` | `readiness:blocked` | Prevents dispatch or marks a blocker. |
| `model:*` | `model:gpt-5.5` | Overrides the default model picker. |
| `batch:*` | `batch:needs-review` | Routes work into implementation, review, or follow-up lanes. |
| `sprint:*` | `sprint:implementation-pass` | Records why the issue entered the sprint. |

Unknown labels are preserved in sprint docs and assignment headers. They do not
change routing until a manager documents a class for them.

## Smart Model Picker

Use this deterministic order when preparing a sprint round:

1. If an issue has exactly one `model:*` label, use that model as the suggested
   model.
2. If multiple `model:*` labels are present, keep all labels and mark the
   suggested model as `manager-review`.
3. If no model label is present, choose from the batch:
   - high ambiguity, high risk, architecture, synthesis, or review lanes:
     strongest available reasoning model.
   - narrow implementation, validators, docs, or mechanical follow-up lanes:
     standard coding model.
   - routine lint, formatting, or evidence collection lanes:
     fast economy model.
4. The model is a recommendation. The handoff still names the runtime adapter
   so dispatch remains honest about what pane can actually run.

## Batching Rules

- Batch by `skill:*` first so agents stay inside one workflow family.
- Split by `artifact:*` when outputs need different validation, such as docs
  versus validation-loop evidence.
- Route `batch:needs-review` to a reviewer lane or make it the explicit review
  gate for the implementing lane.
- Do not dispatch `readiness:blocked` until the blocker note names the owner and
  unblocking condition.

## Assignment Header

Every generated handoff should start with a compact routing header:

```text
Issue: #47 [swarm/workflow] Add label-aware sprint batching and smart model picker
Labels: skill:tmux-sprint, artifact:validation-loop, model:gpt-5.5, batch:needs-review, sprint:implementation-pass
Suggested model: gpt-5.5
Batch notes: tmux-sprint implementation pass; include reviewer lane because batch:needs-review is present
Review gate: agentic-skill
Worktree: /tmp/tmux-sprint-alice-r10-label-routing
Branch: sprint/alice-r10-label-routing
```

The header is intentionally redundant with the sprint doc. Redundancy catches
copy/paste errors before an agent starts work in the wrong worktree or model
lane.

## Sprint-Update Output Shape

When a sprint-update assistant writes the next round, each lane row includes:

```markdown
| Persona | Lane | Issues | Labels | Suggested model | Batch notes | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Alice | tmux-sprint routing | #47 | `skill:tmux-sprint`, `model:gpt-5.5`, `batch:needs-review` | `gpt-5.5` | Pair implementation with review lane | READY |
```

The sprint-update assistant must preserve labels exactly as fetched from the
issue tracker. If it adds derived batch notes, those notes are plain text and do
not replace the source labels.

For GitHub issue JSON, use the reference planner:

```bash
gh issue list --json number,title,url,labels \
  | bash scripts/plan-label-batches.sh
```

The helper accepts one issue, an issue array, or an object with `issues`,
`items`, or `nodes`, and can emit Markdown or JSON with `--format`.
