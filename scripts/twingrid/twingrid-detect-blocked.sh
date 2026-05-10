#!/usr/bin/env bash
# twingrid-detect-blocked.sh
#
# Read-only manager helper: scans tmux pane buffers and per-lane output
# folders for indicators that a pane is blocked on user input, missing
# tooling, or a long-running validator.
#
# Two modes:
#   --tmux      Capture each pane in the named session/window via
#               `tmux capture-pane -p -t <session>:<window>.<pane>` and
#               grep the buffer for known prompt patterns.
#   --folders   Scan /tmp/twingrid-r<N>-* folders for BLOCKED.txt markers
#               agents may have dropped per the blind-handoff template.
#
# Both modes can be combined.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: twingrid-detect-blocked.sh [--tmux SESSION:WINDOW] [--panes LIST]
                                  [--folders /tmp --round N]
                                  [--quiet]

Options:
  --tmux TARGET       tmux target (e.g., sprint:0). Required for --tmux mode.
  --panes LIST        Comma-separated pane indexes (default: 0,1,2,3,4,5).
  --folders DIR       Scan DIR for twingrid round folders. Requires --round.
  --round N           Round number to scan when --folders is set.
  --quiet             Suppress per-pane "OK" lines; only print blocked.
  -h, --help          Show this help.

Exit codes:
  0   No blocks detected.
  1   At least one block detected.
  2   Argument error.

Patterns considered "blocked":
  - "Do you want" / "Allow this command" / "(y/n)" / "[y/N]" / "Continue?"
  - "command not found" / "No such file or directory:" (in pane buffer)
  - "Press Enter to continue"
  - "Approve" / "approval required"
  - BLOCKED.txt present in a per-lane folder.
USAGE
}

target=""
panes="0,1,2,3,4,5"
folders=""
round=""
quiet=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tmux)    [[ $# -ge 2 ]] || { echo "--tmux requires SESSION:WINDOW" >&2; exit 2; }
               target="$2"; shift 2 ;;
    --panes)   [[ $# -ge 2 ]] || { echo "--panes requires LIST" >&2; exit 2; }
               panes="$2"; shift 2 ;;
    --folders) [[ $# -ge 2 ]] || { echo "--folders requires DIR" >&2; exit 2; }
               folders="$2"; shift 2 ;;
    --round)   [[ $# -ge 2 ]] || { echo "--round requires N" >&2; exit 2; }
               round="$2"; shift 2 ;;
    --quiet)   quiet=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$target" && -z "$folders" ]]; then
  echo "must supply --tmux TARGET and/or --folders DIR" >&2
  usage >&2
  exit 2
fi

if [[ -n "$folders" && -z "$round" ]]; then
  echo "--folders requires --round" >&2
  exit 2
fi

# Patterns matched case-insensitively against the last 200 lines of each pane.
blocked_patterns='Do you want|Allow this command|\(y/n\)|\[y/N\]|Continue\?|Press Enter to continue|approval required|^Approve |command not found|No such file or directory'

any_blocked=0

# --- tmux mode ---
if [[ -n "$target" ]]; then
  if ! command -v tmux >/dev/null 2>&1; then
    echo "tmux not on PATH; cannot run --tmux mode" >&2
    exit 2
  fi
  IFS=',' read -r -a pane_list <<< "$panes"
  for p in "${pane_list[@]}"; do
    pane_target="${target}.${p}"
    # Capture last 200 lines; -p prints to stdout; -S -200 starts 200 lines
    # back. If pane is missing, capture-pane will write to stderr; we ignore
    # that and treat the pane as unknown.
    buf="$(tmux capture-pane -p -S -200 -t "$pane_target" 2>/dev/null || true)"
    if [[ -z "$buf" ]]; then
      [[ "$quiet" -eq 1 ]] || echo "pane $pane_target: NO_BUFFER (pane missing or empty)"
      continue
    fi
    if printf '%s' "$buf" | grep -E -i -q -- "$blocked_patterns"; then
      hit="$(printf '%s' "$buf" | grep -E -i -- "$blocked_patterns" | tail -1)"
      echo "pane $pane_target: BLOCKED -> $hit"
      any_blocked=1
    else
      [[ "$quiet" -eq 1 ]] || echo "pane $pane_target: OK"
    fi
  done
fi

# --- folders mode ---
if [[ -n "$folders" ]]; then
  shopt -s nullglob
  for d in "$folders"/twingrid-r"${round}"-*; do
    [[ -d "$d" ]] || continue
    if [[ -f "$d/BLOCKED.txt" ]]; then
      hit="$(head -1 "$d/BLOCKED.txt")"
      echo "folder $d: BLOCKED -> $hit"
      any_blocked=1
    else
      [[ "$quiet" -eq 1 ]] || echo "folder $d: OK"
    fi
  done
  shopt -u nullglob
fi

exit "$any_blocked"
