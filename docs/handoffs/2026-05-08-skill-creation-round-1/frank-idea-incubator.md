# Frank Handoff - Skill Creation Round 1

## Assignment

Build the `idea-incubator` skill for GitHub issue #9:

```bash
gh issue view 9 --repo <your-username>/<your-repo>
```

## Model / lane

Use your configured `gpt-5.4-mini` lane. This issue has strong context and needs a focused skill scaffold.

## Workspace

Primary repo:

```text
<your-workspace>/claude-skills
```

Target skill path:

```text
skills/idea-incubator/
```

## Build requirements

- Use `skill-creator` guidance: concise `SKILL.md`, label schema and issue templates in references.
- Build a skill that captures, classifies, connects, reviews, and promotes ideas using GitHub issues as the durable inbox.
- Telegram Saved Messages is the capture layer; GitHub issues are the incubation layer.
- Include:
  - `SKILL.md`
  - `CHANGELOG.md`
  - references for label schema, issue template, and promotion handoff.
- The skill should work without automation by producing copy-pasteable issue drafts, but should support direct `gh`/GitHub connector creation when available.

## Guardrails

- You are not alone in the repo. Other agents may edit sibling paths under `skills/`.
- Do not revert unrelated changes.
- Do not commit or push.
- Ask the repo owner if the future `idea-incubator` repo ownership or visibility matters before hard-coding it.

## Done

Report changed files, validation performed, assumptions, and blockers.
