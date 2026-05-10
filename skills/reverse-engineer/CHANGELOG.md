# Changelog — reverse-engineer

## v1.1.0 — 2026-05-10

- Add mandatory image-access preflight (workflow step 0) with five `image_access_mode` values: `direct`, `file-path`, `description-only`, `missing`, `partial` (plus `named-object` for prose-only object identification).
- Add standardized **degraded-mode banner** required at the top of every artifact when image access is not `direct`; banner pattern is parseable by tooling.
- Add required `intake:` YAML block to `references/observation-template.md` and `references/builder-handoff-template.md` carrying `image_access_mode`, source qualifiers, recovery path, and confidence ceiling.
- Add **provisional-by-default** rule for builder handoffs derived from degraded intake.
- Add dimensional-confidence cap to `references/confidence-language.md`: absolute dimensions and specific materials are capped at `low` confidence under degraded intake.
- New `references/image-access-recovery.md` with per-runtime recovery prompts (Claude Code, Codex CLI, web vision, Gemini CLI text mode, mobile zip-upload).
- New `scripts/check-reverse-engineer-banner.sh` validator (shellcheck-clean) and pass/fail fixtures under `tests/fixtures/reverse-engineer-banner/`.
- New `tests/test-reverse-engineer-banner.sh` smoke test driver.
- Closes acceptance criteria from issue #70.

## v1.0.0 — 2026-05-09

- Initial skill: structured reverse-engineering analysis for unknown artifacts.
- Cross-platform intake fallback and sync doc added.
- Public-scrub pass: private names and paths removed.
