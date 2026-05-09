# Public Release Checklist

Use this before flipping any part of the repo public.

- [ ] README explains the repo as a skill ecosystem, not only WRFCoin history.
- [ ] Private paths are generalized or intentionally documented.
- [ ] Every shipped skill has `version` and `last-updated` frontmatter.
- [ ] Every shipped skill has a changelog entry.
- [ ] `manifest.yaml` matches the shipped skill set.
- [ ] Bundled scripts referenced by `SKILL.md` are present.
- [ ] Runtime-specific assumptions are marked as Claude, Codex, or Gemini.
- [ ] Example prompts do not expose private credentials or sensitive repos.
- [ ] Benchmarks or smoke tests exist for high-risk skills.
- [ ] Tags exist for release artifacts.
- [ ] Description includes a `Do not use for ...` clause when adjacent specialists exist.
- [ ] Deprecated skills carry `superseded_by` and a `Deprecated: prefer <successor>` clause in their description.
- [ ] Runtime adapters reference the portable canonical name and document any divergence.
- [ ] Project-specific examples are clearly labeled "Example, illustrative:" or generalized.

