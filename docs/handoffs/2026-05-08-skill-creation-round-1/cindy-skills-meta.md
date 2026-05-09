# Cindy Handoff - Skill Creation Round 1

## Assignment

Build the `skills-meta` skill for GitHub issue #18, using issue #4 as supporting infrastructure requirements:

```bash
gh issue view 18 --repo <your-username>/<your-repo>
gh issue view 4 --repo <your-username>/<your-repo>
```

## Model / lane

Use your configured `gpt-5.4-mini` lane. This is a focused metadata/audit skill.

## Workspace

Primary repo:

```text
<your-workspace>/claude-skills
```

Target skill path:

```text
skills/skills-meta/
```

## Build requirements

- Use `skill-creator` guidance: small trigger-focused `SKILL.md`, references for schema/output examples, scripts only if they add deterministic value.
- The skill should inventory installed skills, report versions, check drift against `manifest.yaml`, and suggest frontmatter fixes.
- Behavior should be read-only by default: report and suggest, do not rewrite installed skills automatically.
- Output must be mobile-friendly.
- Include support for Claude, Codex, Gemini, and desktop counterparts where paths are known or can be configured.

## Guardrails

- You are not alone in the repo. Other agents may edit sibling paths under `skills/`.
- Do not revert unrelated changes.
- Do not commit or push.
- Ask the repo owner if a runtime path is ambiguous and the answer materially affects implementation.

## Done

Report changed files, validation performed, assumptions, and blockers.
