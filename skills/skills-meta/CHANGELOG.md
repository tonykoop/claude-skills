# Changelog — skills-meta

## Unreleased

- Added manifest `requires` dependency audit and sync expansion support.
- Added `--version` to the skills-meta helper so sprint panes have a
  deterministic fallback when no `skills-meta` PATH shim is installed.
- Resolved sync `repo_path` values relative to the manifest file instead of the caller's cwd.
- Added runtime direction labels to sync drift plans and JSON output.
- Deduped scan roots by resolved path so explicit roots do not double-count repo defaults.
- Added cleanup reporting for manifest-marked deprecated, obsolete, and retired skills.
- Added duplicate warning details that explain why the kept copy was selected.
- Fixed local skill frontmatter to use top-level version metadata.

## v1.0.0 — 2026-05-09

- Stable release: drift audit, inventory, sync, and fix-duplicates modes.
- Cross-platform root handling: Windows, WSL, and macOS install roots.
- Unreadable root reporting with provenance tracking.
- Duplicate detection with canonical-copy selection.
- `--strict` flag: exits 1 when drift or missing manifest skills are found.
- `changelog_path` tracking: surfaces `missing-changelog` and `changelog-missing-version` issues.
- PyYAML fallback parser for hosts without site packages.
- Manifest drift test fixtures (pass/fail) and `docs/manifest-drift-checks.md`.
