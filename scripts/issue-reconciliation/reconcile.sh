#!/usr/bin/env bash
# Weekly issue-reconciliation runner.
# Closes open issues whose deliverable already merged (the Refs-not-Closes backlog),
# across the software-epic repos listed in repos.txt. Idempotent + safe to re-run.
#
# Usage:
#   ./reconcile.sh dry     # report only (default)
#   ./reconcile.sh exec    # actually close issues
#
# Requires: gh (authenticated, or GH_TOKEN env with repo/issues:write on the targets),
#           python3. Run from anywhere; paths resolve relative to this script.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-dry}"
REPOS_FILE="$HERE/repos.txt"
SWEEP="$HERE/issue-sweep.sh"

[ -f "$REPOS_FILE" ] || { echo "missing $REPOS_FILE" >&2; exit 1; }

while IFS= read -r line; do
  line="${line%%#*}"                      # strip comments
  line="$(echo "$line" | xargs)"          # trim
  [ -z "$line" ] && continue
  repo="$(echo "$line" | awk '{print $1}')"
  protect="$(echo "$line" | awk '{print $2}')"
  PROTECT_EPICS="${protect:-}" bash "$SWEEP" "$repo" "$MODE" \
    2>&1 | grep -E '=====|TO CLOSE|EPICS TO CLOSE|>>>|FAIL'
done < "$REPOS_FILE"
