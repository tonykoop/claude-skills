#!/usr/bin/env bash
# Pull all git repositories in the workspace from their current branch's remote,
# then update all semi-permanent persona worktrees to match their repo's latest main.
# Usage: ./pull-all.sh

set -uo pipefail

WORKSPACE_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
WORKTREES_DIR="$WORKSPACE_DIR/worktrees"
PERSONA_MANIFEST="$WORKSPACE_DIR/docs/plans/persona-launch.generated.tsv"
failures=0

declare -A PROTECTED_WORKTREES=()

protect_worktree() {
    local path="$1"
    [ -n "$path" ] || return 0
    PROTECTED_WORKTREES["$path"]=1
}

if [ -f "$PERSONA_MANIFEST" ]; then
    while IFS=$'\t' read -r persona runtime work_dir team model effort prompt_file; do
        [ -n "${persona:-}" ] || continue
        case "$persona" in
            \#*) continue ;;
        esac
        [ -n "${work_dir:-}" ] || continue
        protect_worktree "${work_dir%/}"
    done < "$PERSONA_MANIFEST"
fi

echo "=== Pulling repos ==="
for dir in "$WORKSPACE_DIR"/*/; do
    [ -d "$dir/.git" ] || continue
    name=$(basename "$dir")
    printf "%-20s " "$name"
    if output=$(git -C "$dir" pull 2>&1); then
        echo "$output"
    else
        echo "FAILED: $output"
        failures=$((failures + 1))
    fi
done

echo ""
echo "=== Updating persona worktrees ==="
updated=0
skipped=0

for wt in "$WORKTREES_DIR"/*/; do
    [ -d "$wt" ] || continue
    wt="${wt%/}"
    name=$(basename "$wt")
    # Only process persona worktrees (skip old lane-style names)
    case "$name" in
        *-alice|*-bob|*-cindy|*-dan|*-elsa) ;;
        *) continue ;;
    esac

    if [ -n "${PROTECTED_WORKTREES["$wt"]+x}" ]; then
        printf "%-30s SKIPPED (listed in persona-launch.generated.tsv)\n" "$name"
        skipped=$((skipped + 1))
        continue
    fi

    if [ -e "$wt/.sprint-active" ]; then
        printf "%-30s SKIPPED (.sprint-active marker)\n" "$name"
        skipped=$((skipped + 1))
        continue
    fi

    # Fetch latest from origin
    if ! git -C "$wt" fetch origin 2>/dev/null; then
        printf "%-30s FETCH FAILED\n" "$name"
        failures=$((failures + 1))
        continue
    fi

    # Check if worktree is on a persona branch (active work) or detached/main
    branch=$(git -C "$wt" branch --show-current 2>/dev/null || true)
    dirty=$(git -C "$wt" status --porcelain 2>/dev/null | wc -l)

    if [ "$dirty" -gt 0 ]; then
        # Has uncommitted changes — don't touch it
        printf "%-30s SKIPPED (dirty: %d files on %s)\n" "$name" "$dirty" "${branch:-(detached)}"
        skipped=$((skipped + 1))
    elif [ -z "$branch" ]; then
        # Detached HEAD (idle worktree) — advance to latest main
        main_sha=$(git -C "$wt" rev-parse origin/main 2>/dev/null)
        head_sha=$(git -C "$wt" rev-parse HEAD 2>/dev/null)
        if [ "$main_sha" = "$head_sha" ]; then
            printf "%-30s up to date\n" "$name"
        else
            git -C "$wt" checkout --detach origin/main 2>/dev/null
            printf "%-30s updated to %s\n" "$name" "$(echo "$main_sha" | cut -c1-7)"
            updated=$((updated + 1))
        fi
    elif [ "$branch" = "main" ]; then
        # On main branch — pull
        if output=$(git -C "$wt" pull 2>&1); then
            printf "%-30s %s\n" "$name" "$output"
            updated=$((updated + 1))
        else
            printf "%-30s PULL FAILED: %s\n" "$name" "$output"
            failures=$((failures + 1))
        fi
    else
        # On a persona feature branch — skip (active work)
        printf "%-30s SKIPPED (on branch: %s)\n" "$name" "$branch"
        skipped=$((skipped + 1))
    fi
done

echo ""
echo "=== Summary ==="
echo "Worktrees updated: $updated, skipped: $skipped, failures: $failures"

if [ "$failures" -gt 0 ]; then
    exit 1
fi
