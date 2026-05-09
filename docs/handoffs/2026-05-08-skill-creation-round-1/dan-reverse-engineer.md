# Dan Handoff - Skill Creation Round 1

## Assignment

Build the `reverse-engineer` analysis skill in Tony's existing reverse-engineering repo for GitHub issue #17:

```bash
gh issue view 17 --repo tonykoop/claude-skills
```

## Model / lane

Use your configured `gpt-5.5` lane. This skill needs careful uncertainty handling and technical analysis design.

## Workspace

Primary repo:

```text
/mnt/c/Users/Tony/Documents/GitHub/reverse-engineering
```

## Build requirements

- Inspect the repo first; it is currently sparse.
- Build a skill from scratch using `skill-creator` guidance.
- Target behavior: analyze existing objects, photos, mechanisms, instruments, and artifacts into structured observations, inferred dimensions, unknowns, confidence notes, and builder handoffs.
- Include:
  - `SKILL.md`
  - `CHANGELOG.md`
  - references/templates for observation, measurement requests, confidence language, and builder handoff.
- Preserve uncertainty. The skill must distinguish observed facts, inferred facts, assumptions, and unknowns.
- It should pair with `maker-engineering`, `makerspace`, and `instrument-maker-v4`.

## Existing dirty state

The repo already has local modifications in `.gitignore` and `LICENSE`. Do not revert them.

## Guardrails

- You are not alone in the wider workspace.
- Do not commit or push.
- Ask Tony if a legal/product boundary needs a decision.

## Done

Report changed files, validation performed, assumptions, and blockers.
