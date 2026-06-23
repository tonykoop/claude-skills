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

failed=()
while IFS= read -r line; do
  line="${line%%#*}"                      # strip comments
  line="$(echo "$line" | xargs)"          # trim
  [ -z "$line" ] && continue
  repo="$(echo "$line" | awk '{print $1}')"
  protect="$(echo "$line" | awk '{print $2}')"
  # Per-repo isolation: one repo erroring (e.g. PAT lacks access, rate limit) must
  # NOT abort the whole sweep. Capture, print, and continue; track failures.
  if ! out="$(PROTECT_EPICS="${protect:-}" bash "$SWEEP" "$repo" "$MODE" 2>&1)"; then
    echo "  !! SKIPPED $repo — sweep error (check RECON_TOKEN access to this repo / rate limit)"
    failed+=("$repo")
    continue
  fi
  echo "$out" | grep -E '=====|TO CLOSE|EPICS TO CLOSE|>>>|FAIL'
done < "$REPOS_FILE"

if [ "${#failed[@]}" -gt 0 ]; then
  echo "WARN: ${#failed[@]} repo(s) skipped due to errors: ${failed[*]}"
fi
# Best-effort cron: completing the sweep (closing what it can) is success, even if
# some repos were skipped. Genuine script bugs still surface via set -u / earlier exits.
exit 0
