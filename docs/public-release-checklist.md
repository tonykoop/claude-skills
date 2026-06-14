# Public Release Checklist

Use this before flipping any part of the repo public.

Latest sweep note: [public-release-readiness-sweep-2026-06-13.md](public-release-readiness-sweep-2026-06-13.md).

- [x] README explains the repo as a skill ecosystem, not only WRFCoin history.
- [x] Private paths are generalized or intentionally documented.
- [ ] Every shipped skill has a `manifest.yaml` entry with
      `canonical_version` and `last_updated`; every shipped `SKILL.md`
      carries top-level `version` and `last-updated` frontmatter. Do not put
      release metadata under a nested `metadata:` block. See
      `docs/skill-versioning.md`.
- [ ] Every shipped skill has a changelog source per the convention defined
      in `docs/packaging.md` (PR #37). The drift checker in
      `skills/skills-meta/scripts/skills-meta.py --mode drift --strict` (PR
      #32) confirms coverage.
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
- [ ] `skills-meta --mode controls --strict` is clean or every finding is
      documented as intentionally private/provenance-only.
