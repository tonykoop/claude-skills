# Loose-skill cleanup report — 2026-06-15 (Lane F)

Tony's rule: every Tony-authored skill must live in exactly one of three
first-class plugins — `coding`, `maker`, `studiopipeline` — none loose. This
report is the REPO-side inventory + the decisions, plus a **review-then-run**
script (`loose-skill-cleanup-2026-06-15.sh`) for the live-install copies that
this lane intentionally did **not** delete (the running supervisor depends on
installed skills).

> **Safety:** No destructive deletes were performed outside this worktree.
> Live-install dirs (`~/.claude/skills`, `~/.codex/skills`, etc.) are untouched.
> The script only *prints* what it would do unless run with `--apply`.

---

## 1. Inventory — skills outside the three plugin dirs (in this repo)

Checked top-level `skills/` and `codex/skills/`.

| Location | Skill | Decision | Action taken in this PR |
|---|---|---|---|
| `skills/source-citations` | source-citations | → **coding** | **Migrated** to `plugins/coding/skills/source-citations` (git mv); manifest `repo_path` updated; registered in marketplace + MARKETPLACE.md. |
| `codex/skills/gh-fix-ci` | gh-fix-ci (Codex-only) | → **coding** (Claude-usable port) + keep codex variant | **Ported** to `plugins/coding/skills/gh-fix-ci` as a Claude-usable skill with the missing `scripts/inspect_pr_checks.py` and a `references/codex-variant.md`. The codex copy is retained as the documented Codex-runtime variant (see §3). |
| `codex/skills/tmux-v2` | tmux-v2 | **Retired** (superseded by `coding/tmux-sprint`) | Left in place; see §3 recommendation. Manifest `tmux-v2` entry should flip to `status: retired`. |
| `codex/skills/merge-manager` | merge-manager (codex) | **Retired** (superseded by `coding/merge-review`) | Left in place; see §3. Manifest `codex-merge-manager` → `status: retired`. |
| `codex/skills/wrfcoin-sprint-dispatch` | wrfcoin-sprint-dispatch | **Retired** (WRFCoin-specific, superseded by `coding/tmux-sprint` + `sprint-update`) | Left in place; see §3. Manifest `wrfcoin-sprint-dispatch` → `status: retired`. |

Anthropic-official skills `skill-creator` and `frontend-design` are **not
Tony's** and were left untouched per the charter.

`skills/` now contains only `.gitkeep` after the source-citations migration.

---

## 2. Manifest dedup — finding

The charter expected duplicate second entries for `houseplant` and
`file-a-patent` to remove. **On `origin/main` (sprint-supervisor v1.2.0 base)
there are no such duplicates.** Verified two ways:

- `python3 -c "import yaml; yaml.safe_load(open('manifest.yaml'))"` parses
  cleanly (PyYAML errors on duplicate mapping keys would surface here).
- Grep of all skill keys → `uniq -d` returns **empty** (no repeated keys).

There was likely a duplicate-bearing manifest revision in some other lane's
base or a pre-cleanup snapshot; the current canonical manifest is already
de-duplicated. **No dedup edit was needed.** If a duplicate-bearing manifest
turns up later, the rule is: keep the entry whose `repo_path` points into a
plugin dir, drop the other.

---

## 3. Recommended live-install + codex/ cleanup (REVIEW, then run script)

The `codex/skills/` directory is a deliberate, documented Codex-CLI runtime
mirror (see `codex/README.md`), not stray loose skills. Retiring those repo
copies is a real decision with two safe-but-distinct options:

**Option A (conservative — recommended now):** flip the three superseded
manifest entries (`tmux-v2`, `codex-merge-manager`, `wrfcoin-sprint-dispatch`)
to `status: retired` and leave the files until a follow-up confirms nothing on
the codex side still loads them. Keep `codex/skills/gh-fix-ci` as the codex
variant of the now-ported coding skill.

**Option B (full removal):** delete the three retired `codex/skills/*` dirs from
the repo and remove their manifest entries entirely. Only do this once you have
confirmed the live `~/.codex/skills/` install no longer references them and no
active sprint manager is mid-run on the codex tmux-v2 driver.

This lane chose **Option A's documentation** but did not edit `status:` flags or
delete codex files, to avoid disrupting a running supervisor that may still be
on the installed copies. Apply the script below when you're ready.

### Live-install copies — DO NOT auto-delete

The retired loose copies also live in live install dirs:

- `/home/tony/.claude/skills/{tmux-v2,wrfcoin-sprint-dispatch,merge-manager}`
- `/home/tony/.codex/skills/{tmux-v2,wrfcoin-sprint-dispatch,merge-manager}`
- duplicate `skills-meta` copies across roots

The running `sprint-supervisor` depends on installed skills, so these are left
for Tony / the supervisor to clear during a quiet window. The script handles
them with `--apply` only, and backs up before removing.

---

## 4. What to run

```bash
# Dry run (default) — prints everything, changes nothing:
bash docs/plans/loose-skill-cleanup-2026-06-15.sh

# Apply (after review, during a quiet window with no live sprint):
bash docs/plans/loose-skill-cleanup-2026-06-15.sh --apply
```
