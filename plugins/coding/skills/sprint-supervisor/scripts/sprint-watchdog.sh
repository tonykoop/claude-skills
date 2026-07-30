#!/usr/bin/env bash
# Continuous prompt + liveness watcher for mixed tmux agent grids.
#
# Detects:
#   PROMPT          permission dialog requiring supervisor judgment
#   IDLE            two consecutive idle observations
#   QUEUED_UNSENT   a dispatch/PROCEED prompt left in the composer
#
# It auto-approves only mechanical edits and narrow single-command read-only
# diagnostics. All other prompts are signaled to the supervisor event bridge.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SCOPE="${SPRINT_SUPERVISOR_SCOPE:-default}"
TARGETS="${SPRINT_TARGETS:-${SPRINT_SESSIONS:-}}"
INTERVAL="${SPRINT_WATCHDOG_INTERVAL:-20}"
STRIKES_REQUIRED="${SPRINT_WATCHDOG_IDLE_STRIKES:-2}"
DRY=0
ONCE=0
LOG="${SPRINT_WATCHDOG_LOG:-/tmp/sprint-supervisor/watchdog.log}"
STATE_ROOT="${SPRINT_SUPERVISOR_STATE_ROOT:-/tmp/sprint-supervisor/watchdog-state}"

usage() {
  echo "usage: $0 [--scope NAME] [--targets 'SESSION ...'] [--interval N] [--once] [--dry-run]"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --scope) shift; SCOPE="${1:-default}" ;;
    --targets) shift; TARGETS="${1:-}" ;;
    --interval) shift; INTERVAL="${1:-20}" ;;
    --once) ONCE=1 ;;
    --dry-run) DRY=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

log() {
  mkdir -p "$(dirname "$LOG")" 2>/dev/null || true
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$LOG"
}

lock_path() { printf '/tmp/sprint-supervisor/%s.lock' "$SCOPE"; }

targets_from_lock() {
  local lock
  lock="$(lock_path)"
  [ -f "$lock" ] || return 0
  jq -r '.targets[]? // empty' "$lock" 2>/dev/null | paste -sd' ' -
}

enumerate_panes() {
  local target
  for target in $TARGETS; do
    if printf '%s' "$target" | grep -qE '^[^:]+:[0-9]+\.[0-9]+$'; then
      printf '%s\n' "$target"
    else
      tmux list-panes -t "$target" \
        -F '#{session_name}:#{window_index}.#{pane_index}' 2>/dev/null || true
    fi
  done | awk '!seen[$0]++'
}

pane_capture() {
  tmux capture-pane -p -t "$1" -S -20 2>/dev/null \
    | grep -v '^$' | tail -12
}

is_busy() {
  printf '%s' "$1" | grep -qE \
    'esc to interrupt|\([0-9]+m? ?[0-9]*s .*(tokens|esc)|Running [0-9]+ shell|shells? still running|Working \(|↓ [0-9]|Compacting|thinking with|Pontificating|Processing|Generating'
}

is_agent() {
  printf '%s' "$1" | grep -qE \
    'Ctx:[[:space:]]*[0-9]+%|gpt-5\.|weekly[[:space:]]+[0-9]+%|auto mode on|\? for shortcuts|[❯›>][[:space:]]'
}

is_queued_unsent() {
  local cap="$1"
  is_busy "$cap" && return 1
  printf '%s' "$cap" | grep -q 'Press up to edit queued messages' && return 0
  # Bounded fallback for manager dispatches observed composed in Codex without
  # the queued-message footer. Default suggestion text intentionally does not
  # match this manager-language regex.
  printf '%s' "$cap" | tail -8 | grep -qE \
    '^[[:space:]]*[›❯][[:space:]]+(PROCEED|Round[[:space:]]+[0-9]+:|Read[[:space:]]+/|read[[:space:]]+/|continue([[:space:]]|$)|execute([[:space:]]|$)|post the verdict)'
}

has_permission_prompt() {
  printf '%s' "$1" | grep -qE \
    'Would you like to (make|run)|Press enter to confirm or esc to cancel|Requesting permission for:|Do you want to proceed\?'
}

is_edit_prompt() {
  printf '%s' "$1" | grep -qE 'Would you like to make the following edits\?|edit files|Apply this change'
}

is_refusal_prompt() {
  printf '%s' "$1" | grep -qiE \
    'rm[[:space:]]+-rf|git[[:space:]]+push[[:space:]]+--force([^ -]|$)|git[[:space:]]+reset[[:space:]]+--hard|git[[:space:]]+clean|DROP[[:space:]]+(TABLE|DATABASE)|FLUSHALL|docker[[:space:]]+push|npm[[:space:]]+publish|systemctl|shutdown|reboot|crontab|chmod[[:space:]]+777|\.ssh/|(^|[[:space:]])sudo([[:space:]]|$)|--dangerously-skip-permissions|bypassPermissions|skipPermissions'
}

is_safe_readonly_prompt() {
  local block="$1"
  is_refusal_prompt "$block" && return 1
  # Fail closed on obvious composition/mutation. Read-only commands embedded in
  # a compound shell line stay with the model supervisor.
  printf '%s' "$block" | grep -qE '[$][(]|[;]|[|]|&&|>>|(^|[^<])>([^>]|$)' && return 1
  printf '%s' "$block" | grep -qE \
    '[$][[:space:]]*(git[[:space:]]+(status|diff|log|show|rev-parse|merge-base|ls-remote)|gh[[:space:]]+(pr[[:space:]]+(view|list|diff|checks)|issue[[:space:]]+(view|list))|rg|grep|ls|cat|head|tail|wc|jq|pwd|df|du|ps|pgrep|tmux[[:space:]]+(capture-pane|list-panes|list-sessions|has-session|display-message|show-options|show-environment))([[:space:]]|$)'
}

emit_event() {
  local type="$1" pane="$2" message="$3"
  local nudge=()
  [ "$DRY" -eq 1 ] && nudge=(--no-nudge)
  "$HERE/supervisor-event.sh" emit \
    --scope "$SCOPE" --type "$type" --pane "$pane" --message "$message" \
    "${nudge[@]}" >/dev/null 2>&1 || true
  log "$type pane=$pane $message"
}

send_keys() {
  [ "$DRY" -eq 1 ] && return 0
  tmux send-keys -t "$1" "${@:2}" 2>/dev/null || true
}

handle_prompt() {
  local pane="$1" cap="$2"
  if is_refusal_prompt "$cap"; then
    emit_event "REFUSAL_PROMPT" "$pane" "left for user decision"
  elif is_edit_prompt "$cap"; then
    if printf '%s' "$cap" | grep -qE "don't ask again for these files|Always allow"; then
      send_keys "$pane" a C-m
      log "APPROVED_EDIT_ALWAYS pane=$pane"
    else
      send_keys "$pane" y C-m
      log "APPROVED_EDIT_ONCE pane=$pane"
    fi
  elif is_safe_readonly_prompt "$cap"; then
    # One-shot only. Codex can offer a dangerously broad persistent prefix such
    # as `cd /worktree`; the hook is the durable policy, not that prefix.
    send_keys "$pane" 1 C-m
    log "APPROVED_READONLY_ONCE pane=$pane"
  else
    emit_event "PERMISSION_REQUEST" "$pane" "command requires supervisor judgment"
  fi
}

flush_queued() {
  local pane="$1" cap
  if [ "$DRY" -eq 1 ]; then
    emit_event "QUEUED_UNSENT" "$pane" "dry-run: would send C-m and verify"
    return
  fi
  send_keys "$pane" C-m
  sleep 1
  cap="$(pane_capture "$pane")"
  if is_queued_unsent "$cap"; then
    send_keys "$pane" C-m
    sleep 1
    cap="$(pane_capture "$pane")"
  fi
  if is_queued_unsent "$cap"; then
    emit_event "QUEUED_STUCK" "$pane" "two submission nudges failed"
  elif is_busy "$cap" || printf '%s' "$cap" | grep -qE \
    '^[[:space:]]*(•|●)[[:space:]]|^[[:space:]]*(Ran|Explored|Edited|Created|Updated)[[:space:]]|Worked for [0-9]|─ Worked for'; then
    emit_event "QUEUED_FLUSHED" "$pane" "submitted with activity evidence"
  else
    emit_event "QUEUED_UNVERIFIED" "$pane" "composer cleared without activity evidence"
  fi
}

state_key() { printf '%s' "$1" | tr -c 'A-Za-z0-9._-' '_'; }

idle_strikes() {
  local pane="$1" busy="$2" key file n
  key="$(state_key "$pane")"
  file="$STATE_ROOT/$SCOPE/$key.idle"
  mkdir -p "$(dirname "$file")" 2>/dev/null || true
  n=0
  [ -f "$file" ] && n="$(cat "$file" 2>/dev/null || echo 0)"
  if [ "$busy" -eq 1 ]; then n=0; else n=$((n + 1)); fi
  printf '%s\n' "$n" > "$file"
  printf '%s' "$n"
}

scan_once() {
  local pane cap strikes count=0
  while IFS= read -r pane; do
    [ -n "$pane" ] || continue
    count=$((count + 1))
    cap="$(pane_capture "$pane")"
    [ -n "$cap" ] || continue

    if has_permission_prompt "$cap"; then
      handle_prompt "$pane" "$cap"
      continue
    fi
    if is_queued_unsent "$cap"; then
      flush_queued "$pane"
      continue
    fi
    if is_busy "$cap"; then
      idle_strikes "$pane" 1 >/dev/null
      continue
    fi
    if is_agent "$cap"; then
      strikes="$(idle_strikes "$pane" 0)"
      if [ "$strikes" -eq "$STRIKES_REQUIRED" ]; then
        emit_event "IDLE" "$pane" "$strikes consecutive idle observations"
      fi
    fi
  done < <(enumerate_panes)
  log "SCAN panes=$count dry=$DRY"
}

run_watchdog() {
  [ -n "$TARGETS" ] || TARGETS="$(targets_from_lock)"
  [ -n "$TARGETS" ] || { echo "sprint-watchdog: no targets; use --targets or lockfile targets" >&2; return 2; }

  if [ -f "$HERE/tmux-preflight.sh" ]; then
    # shellcheck source=/dev/null
    . "$HERE/tmux-preflight.sh"
    run_preflight --quiet; pf=$?
    [ "$pf" -eq 3 ] && return 0
  fi

  log "START scope=$SCOPE targets='$TARGETS' interval=$INTERVAL dry=$DRY"
  if [ "$ONCE" -eq 1 ]; then
    scan_once
    return 0
  fi
  while true; do
    scan_once
    sleep "$INTERVAL"
  done
}

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  run_watchdog
  exit $?
fi
