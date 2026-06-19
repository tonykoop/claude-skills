# Changelog — skills-meta

## v1.0.2 — 2026-06-19 (structured evals + bidirectional drift detection)

Added `evals/evals.json` — the skill's first machine-runnable eval suite
(five cases covering the full behavioral surface):

- **eval 1** `drift-check-summary`: inventory + drift report with mobile-friendly
  summary counts, per-skill issue tags, unreadable-root reporting, and
  read-only enforcement.
- **eval 2** `single-skill-version-probe`: `--mode single` version check;
  falls back to `python scripts/skills-meta.py --version` when no PATH shim.
- **eval 3** `manifest-last-updated-stale-detection`: exercises the new
  `manifest-last-updated-stale:<date>` flag (bidirectional drift: SKILL.md
  newer than manifest) introduced in v1.0.2 on the drift branch.
- **eval 4** `cross-install-sync-dry-run`: sync dry-run with transitive
  `requires` expansion, per-skill `+copy`/`=keep`/`!drift` output, and
  `--apply` gate.
- **eval 5** `fix-duplicates-dry-run`: deterministic keep/remove plan with
  symlink annotation; no deletions without `--apply`.

## 1.0.1 - 2026-06-15

- Added `references/resync-note-2026-06-15.md`: a dated, read-only drift
  reconciliation note (Agent-infra round 2). Documents the three-way
  install-vs-manifest-vs-repo drift on tmux-sprint and sprint-supervisor and
  the deliberate `--mode sync` re-sync plan, without touching live installs.

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
