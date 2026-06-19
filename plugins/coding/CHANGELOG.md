# coding plugin — Changelog

## 2.0.0 — 2026-06-19

First-class v2.0.0 release. The coding skill set is mature and stable across 12 skills:

| Skill | Description |
|---|---|
| `tmux-sprint` | Multi-pane tmux sprint orchestration (v2.7.0): TwinGrid blind A/B, Partner Peek templates, label-aware sprint batching, model-picker routing, provider-failover contract, agy/Antigravity Gemini pane type, Codex /goal lane integration |
| `sprint-supervisor` | Overnight sprint babysitter for multi-pane tmux grids (v1.3.0): pairs with sprint-watchdog.sh, auto-approves routine permission prompts, escalates destructive prompts, morning summary, scales across twingrid/triplegrid/quadgrid via /tmp lockfile |
| `tmux-boss` | tmux session supervisor — manages boss/worker pane topology and inter-pane coordination |
| `merge-review` | Pull request review and merge readiness assessment |
| `sprint-update` | GitHub sprint Queue sync — label, model, and batch metadata, stale issue refresh, PR pressure clustering, archive follow-up checks (v1.1.1) |
| `run-swarm` | Swarm dispatch: duplicate-aware issue filing, related-issue handling, gated label creation, manager summary queues, Tony-decision queues, skill-owner routing, JSON/CSV artifacts (v1.2.1) |
| `skills-meta` | Drift auditor for installed skills vs. manifest.yaml — inventory, drift, fix, fix-duplicates, sync modes (v1.0.1) |
| `ci-triage` | CI failure triage and diagnosis routing |
| `gh-fix-ci` | Inspect failing GitHub Actions PR checks, pull run logs, extract failure snippet, scope external CI providers, draft fix plan (v1.0.0) |
| `scaffold-hygiene` | Project scaffold hygiene checks and cleanup |
| `source-citations` | Bibliography and techniques catalog for instrument repos; keyed registry from the Drive source library and a maker-demonstrations catalog with confirmed-vs-unconfirmed gates |
| `disk-cleanup` | Disk space cleanup routing with safe-delete gates |

**Maturity note:** All 12 skill directories have a `SKILL.md`. No scratch or incomplete skill directories found.

**No breaking changes.** This is a promotion milestone — all skills were stable in the 1.x line; v2.0.0 marks collective maturity.
