# Bob Handoff - Skill Creation Round 1

## Assignment

Work on the existing `makerspace` skill repo for GitHub issue #15:

```bash
gh issue view 15 --repo tonykoop/claude-skills
```

## Model / lane

Use your configured `gpt-5.4` lane. This is the manufacturing/fabrication specialist lane.

## Workspaces

Primary repo:

```text
/mnt/c/Users/Tony/Documents/GitHub/makerspace
```

Related workspace Tony flagged:

```text
/mnt/c/Users/Tony/Documents/GitHub/makerspace-workspace
```

## Build requirements

- Inspect the existing makerspace repo before editing; it already has `SKILL.md`, references, examples, scripts, agents, and evals.
- Improve it toward the issue #15 specialist goal: jigs, fixtures, workholding, shop process, machine-aware planning, and make/order/buy/borrow decisions.
- Evaluate whether `makerspace-workspace` should live inside the makerspace repo. If yes, integrate it cleanly under a sensible path such as `evals/workspace/` or `benchmarks/`, preserving artifacts and avoiding deletion of the original external folder unless Tony explicitly asks.
- Keep the skill concise; move detailed checklists/templates into references.
- Do not take over acoustic design; route that to `instrument-maker-v4` or `maker-engineering`.

## Existing dirty state

The makerspace repo already has local modifications and untracked files. Work with them. Do not revert them.

## Guardrails

- You are not alone in the repo.
- Do not commit or push.
- If workspace relocation has destructive implications, ask Tony before deleting/moving anything irreversible.

## Done

Report changed files, workspace recommendation, validation performed, and blockers.
