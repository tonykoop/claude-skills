#!/usr/bin/env bash
# tmux-sprint restart — codex-aware session revival.
#
#   restart.sh frank          # by persona name
#   restart.sh --pane 5       # by pane index
#   restart.sh frank --force  # revive even a WORKING pane
#
# Walks the codex pane state machine without user interaction (unless the codex
# binary itself prompts for auth):
#   CODEX_EXITED       -> C-c, C-c, wait for shell, run launch cmd
#   CODEX_UPDATE_PROMPT-> send "2" to skip the update, then re-probe
#   DEAD (bare shell)  -> run launch cmd
#   IDLE               -> no-op, report
#   WORKING            -> refuse unless --force

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"

PANE=""
FORCE=0

usage() { sed -n '2,16p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pane)    PANE="$2"; shift 2 ;;
    --project) export TMUX_SPRINT_PROJECT="$2"; shift 2 ;;
    --force)   FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "Error: unknown arg: $1" >&2; usage >&2; exit 2 ;;
    *) # bare arg = persona name
       PANE="$(ts_pane_for_name "$1")"
       [[ -n "$PANE" ]] || { echo "Error: unknown persona: $1" >&2; exit 2; }
       shift ;;
  esac
done

[[ -n "$PANE" ]] || { echo "Error: pass a persona name or --pane N" >&2; usage >&2; exit 2; }

ts_require tmux
ts_require jq

name="$(ts_persona_field "$PANE" name)"; name="${name:-pane$PANE}"
launch="$(ts_persona_field "$PANE" launch)"; launch="${launch:-codex}"
target="$(ts_target "$PANE")"

probe() { ts_classify "$(ts_capture "$PANE")"; }

state="$(probe)"
echo "$name (pane $PANE): state = $state"

ts_cancel_copy_mode "$PANE"

case "$state" in
  IDLE)
    echo "$name already live — nothing to do."
    exit 0 ;;
  WORKING)
    if [[ "$FORCE" -ne 1 ]]; then
      echo "$name is WORKING — refusing to restart. Use --force to override." >&2
      exit 1
    fi
    echo "--force set: interrupting working pane."
    tmux send-keys -t "$target" C-c; sleep 1
    tmux send-keys -t "$target" C-c; sleep 2
    tmux send-keys -t "$target" -l "$launch"; tmux send-keys -t "$target" C-m ;;
  CODEX_EXITED)
    echo "At codex resume prompt — clearing and relaunching."
    tmux send-keys -t "$target" C-c; sleep 1
    tmux send-keys -t "$target" C-c; sleep 2
    tmux send-keys -t "$target" -l "$launch"; tmux send-keys -t "$target" C-m ;;
  CODEX_UPDATE_PROMPT)
    echo "At codex update prompt — skipping update (sending 2)."
    tmux send-keys -t "$target" -l "2"; tmux send-keys -t "$target" C-m; sleep 2
    # after skipping, codex usually drops to shell or resumes; relaunch if shell
    if [[ "$(probe)" == "DEAD" ]]; then
      tmux send-keys -t "$target" -l "$launch"; tmux send-keys -t "$target" C-m
    fi ;;
  DEAD|BLANK)
    echo "Bare shell — launching: $launch"
    tmux send-keys -t "$target" -l "$launch"; tmux send-keys -t "$target" C-m ;;
  *)
    echo "Unhandled state: $state" >&2; exit 1 ;;
esac

# Wait up to 15s for the codex banner (or any live signature) to come up.
deadline=$(( $(date +%s 2>/dev/null || echo 0) + 15 ))
while :; do
  cap="$(ts_capture "$PANE")"
  if printf '%s' "$cap" | grep -qiE 'OpenAI Codex \(v[0-9]'; then
    echo "✓ $name: codex banner up."; break
  fi
  new_state="$(ts_classify "$cap")"
  if [[ "$new_state" == "IDLE" || "$new_state" == "WORKING" ]]; then
    echo "✓ $name: now $new_state."; break
  fi
  now=$(date +%s 2>/dev/null || echo "$deadline")
  if [[ "$now" -ge "$deadline" ]]; then
    echo "⚠️  $name: still $new_state after 15s — may need manual auth/attention." >&2
    exit 1
  fi
  sleep 1
done

echo "$name (pane $PANE): final state = $(probe)"
exit 0
