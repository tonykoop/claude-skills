# Public Release Checklist

Use this before flipping any part of the repo public.

- [x] README explains the repo as a skill ecosystem, not only WRFCoin history.
- [x] Private paths are generalized or intentionally documented.
- [ ] Every shipped skill has a `manifest.yaml` entry with
      `canonical_version` and `last_updated`. (`SKILL.md` frontmatter mirrors
      these fields only once the bundled `skill-creator` validator accepts
      them — see `docs/skill-versioning.md`.)
- [ ] Every shipped skill has a changelog source — either a per-skill
      `CHANGELOG.md` kept outside validator-checked skill files, or a `notes`
      entry on the manifest record summarizing the latest release.
- [ ] `manifest.yaml` `last_updated` is current and matches the shipped skill set.
- [ ] Bundled scripts referenced by `SKILL.md` are present.
- [x] Runtime-specific assumptions are marked as Claude, Codex, or Gemini.
- [x] Example prompts do not expose private credentials or sensitive repos.
- [ ] Benchmarks or smoke tests exist for high-risk skills.
- [ ] Agentic-skill PRs include the review evidence contract from `docs/review-gates/pr-evidence-contract.md`.
- [ ] Skill, adapter, hook, command, and benchmark changes pass the static, behavior, runtime, and regression gates in `docs/review-gates/agentic-skill.md`.
- [ ] Tags exist for release artifacts (`<skill-name>/v<X.Y.Z>`).
- [ ] Description includes a `Do not use for ...` clause when adjacent specialists exist.
- [ ] Deprecated skills carry `superseded_by` and a `Deprecated: prefer <successor>` clause in their description.
- [ ] Runtime adapters reference the portable canonical name and document any divergence.
- [ ] Project-specific examples are clearly labeled "Example, illustrative:" or generalized.
