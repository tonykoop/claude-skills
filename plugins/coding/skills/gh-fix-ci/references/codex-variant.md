# gh-fix-ci — Codex CLI variant note

This skill was ported from the Codex-only `codex/skills/gh-fix-ci` so the
`coding` plugin has a Claude-usable copy. The two are behaviorally identical;
only the plan-drafting step differs by runtime:

- **Claude Code (this skill):** draft a concise fix plan inline (or via a
  plan-drafting skill if one is loaded), then request approval before editing.
- **Codex CLI variant:** prefers Codex's bundled `create-plan` skill to draft
  the plan, falling back to an inline plan if it is unavailable.

Both use the same `scripts/inspect_pr_checks.py` and the same scope rule:
GitHub Actions checks are inspected; external providers (e.g. Buildkite) are
reported by URL only and never driven.

The Codex CLI marketplace continues to ship its own copy under
`codex/skills/gh-fix-ci`; keep the two in sync when the workflow changes.
