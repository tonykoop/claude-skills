# PR Evidence Contract

Use this template for agent-authored PRs. It is intentionally short so agents
can paste it into every PR body and reviewers can scan it in under a minute.

```markdown
## Review Evidence

Type: skill | runtime-adapter | command | hook | benchmark | hardware | docs | script | mixed

Changed behavior:
- What behavior, artifact shape, or review surface changed?

Validation run:
- Exact commands, fixture prompts, screenshots, or manual checks.

Known gaps:
- Untested runtimes, skipped commands, stale fixtures, missing hardware proof, or none.

Reviewer should check:
- Files, claims, edge cases, permissions, generated artifacts, or live smoke paths.

Do not merge until:
- The agent's own merge bar. Use `none beyond normal review` only when true.
```

Evidence quality rules:

- Prefer exact commands and fixture names over prose.
- For docs-only PRs, say why runtime tests were not applicable.
- For scripts/hooks/commands, include syntax checks and at least one failure-path
  check.
- For runtime adapters, name the runtime and whether behavior is deterministic,
  prompt-staging, or observe-only.
- For hardware or manufacturing work, use the instrument-maker hardware gate
  before claiming a packet is build-ready.
