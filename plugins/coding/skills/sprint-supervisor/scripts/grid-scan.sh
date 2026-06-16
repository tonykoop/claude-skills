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

# Prompt families across codex, claude, agy/gemini. The trailing catch-all
# (generic confirmation shapes) means a new CLI's phrasing surfaces to the
# supervisor for judgment instead of being silently missed.
PROMPT_REGEX='Press enter to confirm|Yes, proceed|Approaching rate limits|Would you like to (make|run)|Allow .*command|run_shell_command|\[y/N\]|\[Y/n\]|Press any key|Enter to confirm'

for target in "$@"; do
  # If the target looks like a session:window.pane id, scan it directly.
  # Otherwise, treat it as a session name and enumerate its panes.
  # Read panes with a portable loop (macOS default bash 3.2 has no `mapfile`).
  if echo "$target" | grep -qE '^[^:]+:[0-9]+(\.[0-9]+)?$'; then
    panes=("$target")
  else
    panes=()
    while IFS= read -r _pid; do
      [ -n "$_pid" ] && panes+=("$_pid")
    done < <(tmux list-panes -t "$target" -F '#{pane_id}' 2>/dev/null)
  fi

  for id in "${panes[@]:-}"; do
    [ -z "${id:-}" ] && continue
    # Capture with an explicit scrollback window instead of `tail`-ing a raw
    # capture: trailing blank pane rows otherwise push the visible prompt out
    # of a short tail window (observed on tmux 3.4, WSL2 + macOS). #163
    out=$(tmux capture-pane -p -t "$id" -S -40 2>/dev/null)
    if echo "$out" | grep -qE "$PROMPT_REGEX"; then
      echo "=== $id ==="
      echo "$out" | grep -nE "$PROMPT_REGEX" | tail -10
      echo ""
    fi
  done
done
