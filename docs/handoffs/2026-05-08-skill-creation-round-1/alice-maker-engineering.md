# Alice Handoff - Skill Creation Round 1

## Assignment

Build the `maker-engineering` umbrella routing skill for GitHub issue #14:

```bash
gh issue view 14 --repo tonykoop/claude-skills
```

## Model / lane

Use your configured `gpt-5.5` lane. This is an architecture-heavy routing skill.

## Workspace

Primary repo:

```text
/mnt/c/Users/Tony/Documents/GitHub/claude-skills
```

Target skill path:

```text
skills/maker-engineering/
```

## Build requirements

- Use the `skill-creator` guidance: concise `SKILL.md`, progressive disclosure, references for detailed templates.
- Create a new skill from scratch with:
  - `SKILL.md`
  - `CHANGELOG.md`
  - useful `references/` files for routing, DoE, and specialist registry if needed.
- This skill is an umbrella/router. It should not generate full instrument packets, CNC toolpaths, acoustic calculations, or shop drawings.
- It should route to `instrument-maker-v4`, `makerspace`, `reverse-engineer`, `idea-incubator`, and future specialist skills.
- It should support project intake, routing, DoE scaffolding, cross-project pattern search, and multi-specialist orchestration.

## Guardrails

- You are not alone in the repo. Other agents may edit sibling paths under `skills/`.
- Do not revert unrelated changes.
- Do not commit or push.
- If you need Tony to decide a product direction, ask in your pane before building that part.

## Done

Report changed files, any validation performed, and any questions/blockers.
