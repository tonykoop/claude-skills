# TwinGrid Blind A/B Handoff — TEMPLATE

> Per-lane, per-side. The manager produces one of these per pane and writes it
> to a path the pane can read. Replace every `{{...}}` placeholder.

## Round identity

- Round: `{{round_number}}`
- Lane: `{{lane}}`
- Side: `{{A | B}}`
- Runtime: `{{claude | codex}}`
- Output folder: `{{/tmp/twingrid-r<N>-<runtime>-<lane>-<slug>}}`
- Round mode: `{{content-generation | skill-development}}`

## Pairing

You are one side of an A/B pair. Your paired lane gets the same task and must
work independently. Do **not** read the other side's pane buffer or output
folder during the blind pass. The Partner Peek handoff arrives in a later
phase.

## Assignment

```
{{assignment_body}}
```

## Skills you may use

{{named_skills_or_"no_constraint"}}

## Required outputs

1. Write all artifacts under your output folder. Do not edit shared
   checkouts unless the assignment explicitly requires a repo change.
2. If you make repo changes, work in your assigned isolated worktree and open
   a draft PR. If your assignment is artifact-only, do not manufacture a PR.
3. Finish with an **agent record** matching
   [`agent-record.schema.yaml`](agent-record.schema.yaml). Both YAML and JSON
   forms are accepted; the schema documents required keys.

## Do NOT self-report

Do **not** include any of the following in the agent record:

- `elapsed_time`
- `context_remaining`
- `usage_remaining`
- `blocked_state`

The manager captures these from tmux and the statusline. Self-reporting is
unreliable across runtimes and produces false comparisons. Self-reported
fields will be discarded by the lane-matrix script.

## Toolchain announcement

The manager probed CLI tools at round start. The result is appended below by
the manager before this handoff is written to your pane:

```
{{toolchain_announcement}}
```

If a tool you need is missing, **stop and name the exact missing tool,
command, and install hint** in your agent record. Do not silently work around
it.

## Block detection

If you hit an approval prompt that requires user action, write a one-line
status to your output folder as `BLOCKED.txt` containing the prompt verbatim
and continue with what you can do without the prompt. The manager's block
sweep will surface that file.

## Acceptance

The blind pass is accepted when:

- Your output folder exists and contains the required artifacts named in your
  assignment.
- Your agent record validates against `agent-record.schema.yaml`.
- You did not edit your partner's pane or output folder.
- You did not self-report manager-owned telemetry.
