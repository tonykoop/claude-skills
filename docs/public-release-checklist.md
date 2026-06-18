# Public Release Checklist

Use this before flipping any part of the repo public.

- [x] README explains the repo as a skill ecosystem, not only WRFCoin history.
- [x] Private paths are generalized or intentionally documented.
      Scan 2026-06-15 (`docs/release-readiness/public-content-scan-2026-06-15.md`)
      found ~88 private-home-path lines across 38 files still to generalize
      outside `manifest.yaml`; treat as a blocker before public flip.
- [ ] Every shipped skill has a `manifest.yaml` entry with
      `canonical_version` and `last_updated`. `SKILL.md` frontmatter may
      additionally carry version data nested under `metadata` (the bundled
      `skill-creator` validator already accepts this); see
      `docs/skill-versioning.md` and `docs/release-hygiene-followups.md`.
- [ ] Every shipped skill has a changelog source per the convention defined
      in `docs/packaging.md` (PR #37). The drift checker in
      `skills/skills-meta/scripts/skills-meta.py --mode drift --strict` (PR
      #32) confirms coverage.
- [ ] `manifest.yaml` `last_updated` is current and matches the shipped skill set.
- [ ] Bundled scripts referenced by `SKILL.md` are present.
- [x] Runtime-specific assumptions are marked as Claude, Codex, or Gemini.
- [x] Example prompts do not expose private credentials or sensitive repos.
- [x] No secrets, tokens, private keys, or inline passwords. Verified clean by
      scan 2026-06-15 (`docs/release-readiness/public-content-scan-2026-06-15.md`).
- [ ] Private home paths (`/home/tony`, `/mnt/c/Users/Tony`, `C:\Users\Tony`)
      are generalized to placeholders, except annotated `manifest.yaml`
      install_roots. See scan 2026-06-15.
- [ ] No stray personal emails beyond the intentional `author` email. Scan
      2026-06-15 flagged `wrfcoin@gmx.com` in `scripts/wolfram-cloud-sync/wolfram_sync.wls`.
- [ ] Benchmarks or smoke tests exist for high-risk skills.
- [ ] Agentic-skill PRs include the review evidence contract from `docs/review-gates/pr-evidence-contract.md`.
- [ ] Skill, adapter, hook, command, and benchmark changes pass the static, behavior, runtime, and regression gates in `docs/review-gates/agentic-skill.md`.
- [ ] Tags exist for release artifacts (`<skill-name>/v<X.Y.Z>`).
- [ ] Description includes a `Do not use for ...` clause when adjacent specialists exist.
- [ ] Deprecated skills carry `superseded_by` and a `Deprecated: prefer <successor>` clause in their description.
- [ ] Runtime adapters reference the portable canonical name and document any divergence.
- [ ] Project-specific examples are clearly labeled "Example, illustrative:" or generalized.
- [ ] Umbrella skills document which specialists they route to, and specialists
      document adjacent skills they intentionally do not own.
- [ ] Trigger-overlap changes include a behavior fixture, benchmark prompt, or
      PR note naming the intended winner.
- [ ] Deprecated or archived skills have removal evidence from the cross-device
      sync workflow before any repo copy is deleted.
