#!/usr/bin/env bash
# loose-skill-cleanup-2026-06-15.sh
#
# Review-then-run cleanup for the "no loose skills" consolidation (Lane F).
# DRY RUN by default — prints what it would do and changes NOTHING.
# Pass --apply to actually act. Backs up each removed dir to a timestamped
# tarball under ~/.skill-cleanup-backups/ before deleting.
#
# Scope:
#   1. Flip superseded codex/ manifest entries to status: retired (repo edit).
#   2. Remove retired codex/skills/* repo copies (tmux-v2, merge-manager,
#      wrfcoin-sprint-dispatch).
#   3. Remove duplicate / retired live-install copies — only with --apply,
#      and only after backing them up. The running supervisor depends on
#      installed skills, so run this during a quiet window.
#
# This script never touches: plugins/{coding,maker}, studiopipeline,
# skill-creator, frontend-design, or any currently-active skill.

set -euo pipefail

APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
BACKUP_DIR="$HOME/.skill-cleanup-backups"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

say()  { printf '%s\n' "$*"; }
do_or_show() {
  if [[ "$APPLY" -eq 1 ]]; then
    say "  RUN: $*"; eval "$@"
  else
    say "  DRY: $*"
  fi
}

backup_then_rm() { # backup_then_rm <dir>
  local dir="$1"
  [[ -e "$dir" ]] || { say "  skip (absent): $dir"; return 0; }
  local safe; safe="$(printf '%s' "$dir" | tr '/ ' '__')"
  local tarball="$BACKUP_DIR/${STAMP}${safe}.tgz"
  if [[ "$APPLY" -eq 1 ]]; then
    mkdir -p "$BACKUP_DIR"
    say "  BACKUP: $dir -> $tarball"
    tar czf "$tarball" -C "$(dirname "$dir")" "$(basename "$dir")"
    say "  REMOVE: $dir"
    rm -rf "$dir"
  else
    say "  DRY: would back up $dir -> $tarball then remove it"
  fi
}

say "=== loose-skill cleanup ($([[ $APPLY -eq 1 ]] && echo APPLY || echo DRY-RUN)) ==="
say "repo: $REPO_ROOT"
say ""

# --- 1. Repo: retired codex/skills copies -----------------------------------
say "[1] Retired codex/skills/* repo copies (superseded by coding plugin):"
for s in tmux-v2 merge-manager wrfcoin-sprint-dispatch; do
  d="$REPO_ROOT/codex/skills/$s"
  if [[ -d "$d" ]]; then
    do_or_show "rm -rf '$d'"
  else
    say "  skip (absent): $d"
  fi
done
say ""
say "  NOTE: also set these manifest entries to 'status: retired' (or delete):"
say "        tmux-v2, codex-merge-manager, wrfcoin-sprint-dispatch."
say "        (Left as a manual edit — verify nothing on the codex side loads them first.)"
say ""

# --- 2. Live-install duplicate / retired copies -----------------------------
say "[2] Live-install copies (backed up before removal; --apply only):"
LIVE_ROOTS=(
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
)
RETIRED_SKILLS=(tmux-v2 merge-manager wrfcoin-sprint-dispatch)
for root in "${LIVE_ROOTS[@]}"; do
  [[ -d "$root" ]] || { say "  skip (root absent): $root"; continue; }
  for s in "${RETIRED_SKILLS[@]}"; do
    backup_then_rm "$root/$s"
  done
done
say ""

# --- 3. Duplicate skills-meta copies (report only) --------------------------
say "[3] Duplicate skills-meta copies across roots (REPORT ONLY — manual decision):"
for root in "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.gemini/skills"; do
  [[ -d "$root/skills-meta" ]] && say "  found: $root/skills-meta"
done
say "  Canonical lives at plugins/coding/skills/skills-meta. Use the skills-meta"
say "  skill itself (--apply) to reconcile duplicates rather than this script."
say ""

say "=== done ($([[ $APPLY -eq 1 ]] && echo applied || echo dry-run)) ==="
[[ "$APPLY" -eq 0 ]] && say "Re-run with --apply during a quiet window (no live sprint) to act."
exit 0
