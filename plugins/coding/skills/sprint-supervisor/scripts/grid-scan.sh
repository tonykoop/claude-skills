#!/usr/bin/env bash
# grid-scan.sh — scan tmux panes in given sessions for open codex prompts.
#
# Usage:
#   grid-scan.sh <target1> [target2] ...
#
# Targets can be:
#   - session names (e.g. twingrid-a)        → scans every pane in the session
#   - session:window.pane IDs (e.g. 0:0)     → scans just that pane
#
# Output: for each pane with an open prompt, prints
#     === <pane_id> ===
#     <last 10 lines of captured output>
#
# Exit status: 0 always (a clean grid still exits 0).
#
# Used by the /sprint-supervisor skill on every wakeup cycle.

set -u

if [ "$#" -lt 1 ]; then
  echo "usage: $0 <target> [target ...]" >&2
  exit 2
fi

PROMPT_REGEX='Press enter to confirm|Yes, proceed|Approaching rate limits|Would you like to (make|run)'

for target in "$@"; do
  # If the target looks like a session:window.pane id, scan it directly.
  # Otherwise, treat it as a session name and enumerate its panes.
  if echo "$target" | grep -qE '^[^:]+:[0-9]+(\.[0-9]+)?$'; then
    panes=("$target")
  else
    mapfile -t panes < <(tmux list-panes -t "$target" -F '#{pane_id}' 2>/dev/null)
  fi

  for id in "${panes[@]:-}"; do
    [ -z "${id:-}" ] && continue
    out=$(tmux capture-pane -p -t "$id" 2>/dev/null | tail -12)
    if echo "$out" | grep -qE "$PROMPT_REGEX"; then
      echo "=== $id ==="
      echo "$out" | tail -10
      echo ""
    fi
  done
done
