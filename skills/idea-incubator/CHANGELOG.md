# Changelog

## 1.2.0 - 2026-05-10

- Added Promote-batch / cluster mode for ranking related capture issues before
  selecting a promotion candidate.
- Added promotion-readiness matrix guidance, recovery/import provenance fields,
  binary-asset Git LFS prompts, and `Refs` versus `Closes` handling.
- Added a Weather Balloon Camera Vessel worked example for archive-recovery
  clusters with CAD/media import risk.

## 1.1.0 - 2026-05-08

- Cross-platform compatibility pass for Claude Code, Claude Desktop, Codex,
  Codex Desktop, Gemini CLI, and mobile zip-upload.
- Added `scripts/bootstrap_labels.py` Python companion to the bash bootstrap
  script for hosts where bash is awkward (native Windows, sandboxed Codex).
- Documented a copy-pasteable `gh label create` fallback in `label-schema.md`
  for mobile and `gh`-less environments.
- Normalized trigger phrases (dropped trailing `?`) in SKILL.md and
  `agents/openai.yaml` so substring-matching agents route reliably.
- Added a Platform notes section explaining per-host behavior.

## 1.0.0 - 2026-05-08

- Initial `idea-incubator` skill.
- Added capture, intake, connect, review, and promote modes.
- Added label schema, issue template, promotion handoff reference, and
  optional GitHub label bootstrap helper.
