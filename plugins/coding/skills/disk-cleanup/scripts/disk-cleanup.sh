#!/usr/bin/env bash
# disk-cleanup — weekly recovery for a multi-worktree dev setup.
#
# SAFE BY DEFAULT: --dry-run is the default. Reports what would be cleaned
# and estimated bytes freed without actually deleting anything. Destructive
# operations require --apply.
#
# Usage:
#   ./disk-cleanup.sh                          # dry-run, full report
#   ./disk-cleanup.sh --apply                  # actually clean (excludes docker)
#   ./disk-cleanup.sh --apply --include-docker --confirm   # also docker prune
#   ./disk-cleanup.sh --worktree core4-alice --apply       # one worktree only
#   ./disk-cleanup.sh --apply --skip-branches              # skip branch cleanup
#   ./disk-cleanup.sh --json                   # JSON output

set -uo pipefail

# ---- defaults --------------------------------------------------------------

WORKSPACE_DIR="${WORKSPACE_DIR:-$(cd "$(dirname "$0")/../../../.." && pwd)}"
WORKTREES_DIR="${WORKTREES_DIR:-$WORKSPACE_DIR/worktrees}"

APPLY=0
INCLUDE_DOCKER=0
CONFIRM_DOCKER=0
SKIP_BRANCHES=0
TARGET_WORKTREE=""
JSON_OUTPUT=0
FORCE=0

# Branch-naming patterns to treat as live (never delete)
LIVE_PATTERNS=("lane*" "*/round*-current" "*/wip-*")

# ---- parse flags -----------------------------------------------------------

while [ $# -gt 0 ]; do
    case "$1" in
        --apply)            APPLY=1; shift ;;
        --include-docker)   INCLUDE_DOCKER=1; shift ;;
        --confirm)          CONFIRM_DOCKER=1; shift ;;
        --skip-branches)    SKIP_BRANCHES=1; shift ;;
        --worktree)         shift; TARGET_WORKTREE="$1"; shift ;;
        --json)             JSON_OUTPUT=1; shift ;;
        --force)            FORCE=1; shift ;;
        --help|-h)
            sed -n '2,15p' "$0"
            exit 0
            ;;
        *)
            echo "Unknown flag: $1 (use --help)" >&2
            exit 1
            ;;
    esac
done

# ---- helpers ---------------------------------------------------------------

bytes_to_human() {
    local b=$1
    if [ "$b" -gt 1073741824 ]; then printf "%.1f GB" "$(echo "scale=1; $b/1073741824" | bc)"
    elif [ "$b" -gt 1048576 ]; then printf "%.0f MB" "$(echo "scale=0; $b/1048576" | bc)"
    elif [ "$b" -gt 1024 ]; then printf "%.0f KB" "$(echo "scale=0; $b/1024" | bc)"
    else echo "$b B"; fi
}

dir_size_bytes() {
    local d=$1
    [ -d "$d" ] || { echo 0; return; }
    du -sb "$d" 2>/dev/null | awk '{print $1}'
}

is_live_branch() {
    local branch=$1
    # Pattern match against live patterns
    for p in "${LIVE_PATTERNS[@]}"; do
        case "$branch" in $p) return 0 ;; esac
    done
    return 1
}

# ---- 1. Worktree cargo clean ----------------------------------------------

echo "=== disk-cleanup ==="
echo "Mode: $([ $APPLY -eq 1 ] && echo "APPLY" || echo "DRY-RUN")"
echo "Workspace: $WORKSPACE_DIR"
echo

total_freed=0
declare -A wt_freed

echo "--- Worktree cleanup ---"
for wt in "$WORKTREES_DIR"/*/; do
    [ -d "$wt" ] || continue
    name=$(basename "$wt")
    [ -n "$TARGET_WORKTREE" ] && [ "$name" != "$TARGET_WORKTREE" ] && continue

    target_dir="$wt/target/debug"
    if [ ! -d "$target_dir" ]; then
        printf "  %-30s no target/debug — skip\n" "$name"
        continue
    fi

    # Safety: refuse cargo clean if uncommitted work exists, unless --force
    if [ "$FORCE" -ne 1 ]; then
        dirty=$(git -C "$wt" status --porcelain 2>/dev/null | wc -l)
        if [ "$dirty" -gt 0 ]; then
            printf "  %-30s SKIP (uncommitted: %d files; use --force to override)\n" "$name" "$dirty"
            continue
        fi
    fi

    size=$(dir_size_bytes "$target_dir")
    if [ "$APPLY" -eq 1 ]; then
        (cd "$wt" && cargo clean --target-dir target/debug 2>/dev/null) || true
        printf "  %-30s freed %s (target/debug/)\n" "$name" "$(bytes_to_human "$size")"
    else
        printf "  %-30s would free %s (target/debug/)\n" "$name" "$(bytes_to_human "$size")"
    fi

    wt_freed["$name"]=$size
    total_freed=$((total_freed + size))
done

# ---- 2. Merged-branch cleanup ---------------------------------------------

if [ "$SKIP_BRANCHES" -eq 0 ]; then
    echo
    echo "--- Merged branches ---"
    deleted=0
    skipped=0
    deleted_names=()
    skipped_names=()

    for repo_dir in "$WORKSPACE_DIR"/*/; do
        [ -d "$repo_dir/.git" ] || continue
        repo_name=$(basename "$repo_dir")

        # Get merged branches (excluding main + current)
        git -C "$repo_dir" fetch origin --prune --quiet 2>/dev/null || continue
        merged=$(git -C "$repo_dir" branch --merged origin/main 2>/dev/null \
            | sed 's/^[* ] //' \
            | grep -vE '^(main|master|HEAD)$' || true)

        # Worktrees-list — branches in active worktrees should never be deleted
        wt_branches=$(git -C "$repo_dir" worktree list --porcelain 2>/dev/null \
            | awk '/^branch /{sub(/refs\/heads\//,"",$2); print $2}' || true)

        for branch in $merged; do
            # Skip if in active worktree
            if echo "$wt_branches" | grep -qFx "$branch"; then
                skipped_names+=("$repo_name:$branch (active worktree)")
                skipped=$((skipped + 1))
                continue
            fi

            # Skip if matches a live pattern
            if is_live_branch "$branch"; then
                skipped_names+=("$repo_name:$branch (live pattern)")
                skipped=$((skipped + 1))
                continue
            fi

            # Confirm no commits ahead of main (defensive — branch --merged should already guarantee this)
            ahead=$(git -C "$repo_dir" rev-list --count "origin/main..$branch" 2>/dev/null || echo "?")
            if [ "$ahead" != "0" ]; then
                skipped_names+=("$repo_name:$branch (ahead by $ahead)")
                skipped=$((skipped + 1))
                continue
            fi

            if [ "$APPLY" -eq 1 ]; then
                git -C "$repo_dir" branch -d "$branch" >/dev/null 2>&1 \
                    && deleted=$((deleted + 1)) \
                    && deleted_names+=("$repo_name:$branch") \
                    || skipped_names+=("$repo_name:$branch (delete failed)")
            else
                deleted=$((deleted + 1))
                deleted_names+=("$repo_name:$branch (would delete)")
            fi
        done
    done

    echo "  Deleted: $deleted, Skipped: $skipped"
    [ "$deleted" -gt 0 ] && for n in "${deleted_names[@]}"; do echo "    $n"; done
    [ "$skipped" -gt 0 ] && echo "  Skipped:" && for n in "${skipped_names[@]}"; do echo "    $n"; done
fi

# ---- 3. npm / pnpm caches (TODO) ------------------------------------------

# TODO: implement npm cache clean --force + pnpm store prune
# Gated on --apply, with size measurement before and after.

# ---- 4. Docker prune (opt-in) ---------------------------------------------

if [ "$INCLUDE_DOCKER" -eq 1 ]; then
    echo
    echo "--- Docker prune ---"
    if [ "$APPLY" -eq 1 ] && [ "$CONFIRM_DOCKER" -eq 1 ]; then
        echo "  Running docker system prune --volumes -f"
        docker system prune --volumes -f 2>&1 | tail -5
    else
        cat <<EOF
  WARNING: docker system prune --volumes will delete:
    - All stopped containers
    - All networks not used by containers
    - All volumes not used by at least one container
    - All dangling images and build caches

  Reclaim is typically 20–80GB but may invalidate hours of recent builds.

  To proceed, re-run with: --apply --include-docker --confirm
EOF
    fi
fi

# ---- 5. WSL VHD shrink (manual command print) -----------------------------

if grep -q "microsoft" /proc/version 2>/dev/null; then
    echo
    echo "--- WSL VHD shrink (manual step) ---"
    distro=$(cat /etc/os-release 2>/dev/null | grep '^ID=' | cut -d= -f2 | tr -d '"' || echo "unknown")
    cat <<EOF
  Your WSL2 distro is '$distro'.

  WSL cannot shrink its own backing VHDX while running. To reclaim Windows
  filesystem space, exit this skill and run from an ELEVATED PowerShell
  window on Windows:

    wsl --shutdown
    \$vhd = Get-ChildItem -Path "\$env:LOCALAPPDATA\\Packages" -Recurse -Filter "ext4.vhdx" -ErrorAction SilentlyContinue | Select-Object -First 1
    Optimize-VHD -Path \$vhd.FullName -Mode Full

  This may take 10–30 minutes for a 100+ GB VHDX. Don't interrupt it.
EOF
fi

# ---- Summary --------------------------------------------------------------

echo
echo "=== Summary ==="
if [ "$APPLY" -eq 1 ]; then
    echo "  Worktree cleanup freed: $(bytes_to_human "$total_freed")"
    [ "$SKIP_BRANCHES" -eq 0 ] && echo "  Branches deleted: ${deleted:-0} (${skipped:-0} skipped)"
else
    echo "  Would free: $(bytes_to_human "$total_freed") from worktrees"
    [ "$SKIP_BRANCHES" -eq 0 ] && echo "  Would delete: ${deleted:-0} branches (${skipped:-0} skipped)"
    echo "  Re-run with --apply to actually clean."
fi

exit 0
