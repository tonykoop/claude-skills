# Skills re-sync note — 2026-06-15 (Agent-infra round 2)

> **Read-only reconciliation.** This note documents install-vs-repo drift
> found by running `skills-meta --mode drift`. It does **not** modify or
> delete any live install. The re-sync commands below are for the user to
> run deliberately after the round-2 PRs merge.

## Three-way drift on the two sprint skills

| Skill             | Repo SKILL.md (truth) | Manifest canonical | Live `~/.claude` & `~/.codex` | `~/wrfcoin/.{claude,codex}` |
|-------------------|-----------------------|--------------------|-------------------------------|-----------------------------|
| tmux-sprint       | 2.5.0 → **2.6.0** (PR #222) | 2.5.0 → **2.6.0** | **2.3.1** (behind)            | **2.3.0** (further behind)  |
| sprint-supervisor | 1.3.0 → **1.3.1** (PR #220) | 1.3.0 → **1.3.1** | **1.1.0** (behind)            | **1.0.0** (further behind)  |

Notes:

- **Repo SKILL.md is the source of truth**, not the live installs and not the
  brief's assumption. The round-2 task brief estimated installs lagged at
  "tmux-sprint 2.5.0 / sprint-supervisor 1.3.0" — that is the *repo* version;
  the actual *installed* copies are older (2.3.1 / 1.1.0 in the primary roots,
  2.3.0 / 1.0.0 under wrfcoin).
- **Manifest canonical_version was already current on origin/main** at the
  start of this round (2.5.0 / 1.3.0). An earlier drift scan that read 2.4.1 /
  1.1.0 was an artifact of a *dirty main working tree* (the local
  `add-connectors-to-maker-skills` branch) plus the live-install snapshot — not
  origin/main. After round-2 PRs merge, canonical advances to 2.6.0 / 1.3.1.
- The #117 Codex `/goal` work had been committed only to a local feature
  branch and was **never on main** until PR #222. That is why a live scan saw
  no `/goal` content even though the dirty working tree did.

## Other repo-side drift (informational, low priority)

`skills-meta --mode drift` also flagged these on the canonical repo copies —
all are `missing-changelog` on skills that predate the CHANGELOG convention,
not version mismatches. Not in this round's scope; listed for backlog:

- `disk-cleanup`, `gh-fix-ci`, `scaffold-hygiene`, `merge-review`, `ci-triage`
  (coding) — missing CHANGELOG.
- `maker-engineering`, `habitat-maker`, `sheet-music`, `laser-art` (maker) —
  missing CHANGELOG.
- 63 duplicate records across 31 skills are **expected**: each canonical skill
  also has portable copies installed under `~/.claude`, `~/.codex`, `~/.gemini`.
  These are not errors; they are the install copies the sync step below
  refreshes.
- A cluster of `wrfcoin-*` skills under `~/wrfcoin/core4/.claude` and
  `~/wrfcoin/.codex` are `missing-from-manifest` (project-local, intentionally
  unmanaged). Leave them alone.

## Re-sync plan (run after PRs #220, #222 merge — do NOT run before)

The canonical re-sync uses `skills-meta --mode sync`, which is dry-run by
default and **never deletes**; `--force` only overwrites copies that have
drifted *behind* canonical (local edits without `--force` are reported and
skipped). Live installs are never removed by this note.

```bash
# From the claude-skills repo root.
SM=plugins/coding/skills/skills-meta/scripts/skills-meta.py

# 1. Preview (dry-run) — confirm only tmux-sprint + sprint-supervisor move.
python3 $SM --mode sync --target ~/.claude/skills --skill tmux-sprint,sprint-supervisor
python3 $SM --mode sync --target ~/.codex/skills  --skill tmux-sprint,sprint-supervisor

# 2. Land the refresh (overwrites the behind-canonical installed copies).
python3 $SM --mode sync --target ~/.claude/skills --skill tmux-sprint,sprint-supervisor --apply --force
python3 $SM --mode sync --target ~/.codex/skills  --skill tmux-sprint,sprint-supervisor --apply --force

# 3. wrfcoin project roots (further behind) — same pattern, separate roots.
python3 $SM --mode sync --target ~/wrfcoin/.claude/skills --skill tmux-sprint,sprint-supervisor --apply --force
python3 $SM --mode sync --target ~/wrfcoin/.codex/skills  --skill tmux-sprint,sprint-supervisor --apply --force

# 4. Re-verify: drift on these two skills should clear.
python3 $SM --mode drift | grep -E 'tmux-sprint|sprint-supervisor'
```

`sprint-supervisor` declares a `sprint-manager` dependency in the manifest;
focused sync auto-expands to include it, so the dependency rides along.

## Why this is documented, not auto-applied

Per the round-2 invariant and the no-delete rule for live installs: this round
produces the **re-sync note**, not the re-sync action. Tony runs the commands
above when he wants the installed copies refreshed, after the PRs land and the
canonical versions are final (2.6.0 / 1.3.1).
