# Elsa Handoff - Skill Creation Round 1

## Assignment

Build the `yoga-sequencer` skill for GitHub issue #13:

```bash
gh issue view 13 --repo <your-username>/<your-repo>
```

## Model / lane

Use your configured `gpt-5.4` lane. This is a structured content/design skill with a real teaching workflow.

## Workspace

Primary repo:

```text
<your-workspace>/claude-skills
```

Target skill path:

```text
skills/yoga-sequencer/
```

## Build requirements

- Use `skill-creator` guidance: concise `SKILL.md`, pose data and detailed sequencing references outside the main body.
- Build a vinyasa-focused yoga sequencing skill that pairs with `yoga-playlist-builder`.
- Include:
  - `SKILL.md`
  - `CHANGELOG.md`
  - `references/poses.yaml` starter library
  - references for sequencing principles and playlist-builder handoff.
- Modes should include theme-first, peak-pose-first, anatomical prep, counter-pose lookup, full-class generation, and playlist handoff.
- Include safety/constraining language without turning the skill into medical advice.

## Guardrails

- You are not alone in the repo. Other agents may edit sibling paths under `skills/`.
- Do not revert unrelated changes.
- Do not commit or push.
- Ask the repo owner if you need their preferred yoga style beyond vinyasa defaults.

## Done

Report changed files, validation performed, assumptions, and blockers.
