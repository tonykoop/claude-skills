#!/usr/bin/env bash
# Bridge Claude/Codex lifecycle events and watcher findings to a tmux supervisor.
#
# Hook mode reads Claude hook JSON from stdin (or Codex notify JSON from $2).
# Emit mode is used by sprint-watchdog.sh:
#   supervisor-event.sh emit --scope default --type PROMPT --pane 0:0.3
#
# Every event is written under /tmp. When the declared supervisor pane is an
# idle Claude/Codex TUI, a short file-reference prompt is submitted so an Opus
# supervisor can react immediately. Busy supervisors are never interrupted.

set -uo pipefail

EVENT_ROOT="${SPRINT_SUPERVISOR_EVENT_ROOT:-/tmp/sprint-supervisor}"
SCOPE="${SPRINT_SUPERVISOR_SCOPE:-default}"
TYPE=""
PANE=""
MESSAGE=""
PAYLOAD=""
MODE="${1:-hook}"
NUDGE="${SPRINT_SUPERVISOR_NUDGE:-1}"
DEDUPE_SECONDS="${SPRINT_SUPERVISOR_NUDGE_DEDUPE_SECONDS:-15}"

json_get() {
  local expr="$1" json="$2"
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$json" | jq -r "$expr // empty" 2>/dev/null || true
  fi
}

iso_now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

epoch_now() { date +%s; }

file_epoch() {
  stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null || echo 0
}

pane_address() {
  local target="${1:-${TMUX_PANE:-}}"
  [ -n "$target" ] || return 0
  tmux display-message -p -t "$target" \
    '#{session_name}:#{window_index}.#{pane_index}' 2>/dev/null || true
}

scope_lock() { printf '%s/%s.lock' "$EVENT_ROOT" "$SCOPE"; }

supervisor_pane() {
  if [ -n "${SPRINT_SUPERVISOR_PANE:-}" ]; then
    printf '%s' "$SPRINT_SUPERVISOR_PANE"
    return
  fi
  local lock
  lock="$(scope_lock)"
  if [ -f "$lock" ] && command -v jq >/dev/null 2>&1; then
    jq -r '.supervisor_pane // .manager_pane // empty' "$lock" 2>/dev/null || true
  fi
}

is_busy_capture() {
  printf '%s' "$1" | grep -qE \
    'esc to interrupt|\([0-9]+m? ?[0-9]*s .*(tokens|esc)|Running [0-9]+ shell|shells? still running|Working \(|↓ [0-9]|Compacting|thinking with|Pontificating|Processing|Generating'
}

is_idle_agent_capture() {
  local cap="$1"
  is_busy_capture "$cap" && return 1
  printf '%s' "$cap" | grep -qE \
    '(^|[[:space:]])[❯›>][[:space:]]|Ctx:[[:space:]]*[0-9]+%|gpt-5\.|auto mode on|\? for shortcuts'
}

write_event() {
  local dir="$EVENT_ROOT/$SCOPE.events" ts out payload_json
  mkdir -p "$dir" "$EVENT_ROOT" 2>/dev/null || true
  ts="$(date -u +%Y%m%dT%H%M%S)-$(epoch_now)-$$"
  out="$dir/$ts.json"
  if command -v jq >/dev/null 2>&1; then
    payload_json="${PAYLOAD:-null}"
    if ! printf '%s' "$payload_json" | jq -e . >/dev/null 2>&1; then
      payload_json="$(jq -n --arg raw "$PAYLOAD" '{invalid_json:$raw}')"
    fi
    jq -n \
      --arg received_at "$(iso_now)" \
      --arg type "$TYPE" \
      --arg pane "$PANE" \
      --arg message "$MESSAGE" \
      --argjson payload "$payload_json" \
      '{received_at:$received_at,type:$type,pane:$pane,message:$message,payload:$payload}' \
      > "$out" 2>/dev/null || true
  else
    printf '%s type=%s pane=%s message=%s\n' "$(iso_now)" "$TYPE" "$PANE" "$MESSAGE" \
      > "$out" 2>/dev/null || true
  fi
  printf '%s type=%s pane=%s message=%s\n' "$(iso_now)" "$TYPE" "$PANE" "$MESSAGE" \
    >> "$EVENT_ROOT/$SCOPE.pending" 2>/dev/null || true
  find "$dir" -type f -print 2>/dev/null | sort -r | tail -n +501 \
    | while IFS= read -r stale; do rm -f -- "$stale"; done
}

nudge_supervisor() {
  [ "$NUDGE" = "1" ] || return 0
  local supervisor origin cap runtime key stamp now last_nudge prompt
  supervisor="$(supervisor_pane)"
  [ -n "$supervisor" ] || return 0
  origin="$(pane_address "${TMUX_PANE:-}")"
  [ "$origin" != "$supervisor" ] || return 0

  cap="$(tmux capture-pane -p -t "$supervisor" -S -30 2>/dev/null || true)"
  is_idle_agent_capture "$cap" || return 0

  key="$(printf '%s-%s' "$TYPE" "$PANE" | tr -c 'A-Za-z0-9._-' '_')"
  stamp="$EVENT_ROOT/$SCOPE.nudge.$key"
  now="$(epoch_now)"
  last_nudge=0
  [ -e "$stamp" ] && last_nudge="$(file_epoch "$stamp")"
  [ $((now - last_nudge)) -ge "$DEDUPE_SECONDS" ] || return 0
  : > "$stamp" 2>/dev/null || true

  prompt="Resume /sprint-supervisor for scope $SCOPE. Event $TYPE in pane ${PANE:-unknown}; read $EVENT_ROOT/$SCOPE.pending."
  runtime="$(tmux display-message -p -t "$supervisor" '#{pane_current_command}' 2>/dev/null || true)"
  tmux send-keys -t "$supervisor" -l "$prompt" 2>/dev/null || return 0
  tmux send-keys -t "$supervisor" C-m 2>/dev/null || true

  # Codex sometimes leaves a multiline/file-reference prompt composed after the
  # first carriage return. Verify activity; a second C-m is the bounded remedy.
  if printf '%s\n%s' "$runtime" "$cap" | grep -qiE 'codex|gpt-5\.'; then
    sleep 1
    cap="$(tmux capture-pane -p -t "$supervisor" -S -12 2>/dev/null || true)"
    if ! is_busy_capture "$cap"; then
      tmux send-keys -t "$supervisor" C-m 2>/dev/null || true
    fi
  fi
}

parse_hook() {
  PAYLOAD="${2:-}"
  if [ -z "$PAYLOAD" ] && [ ! -t 0 ]; then
    PAYLOAD="$(cat 2>/dev/null || true)"
  fi
  [ -n "$PAYLOAD" ] || PAYLOAD='{}'

  local event notification
  event="$(json_get '.hook_event_name' "$PAYLOAD")"
  notification="$(json_get '.notification_type' "$PAYLOAD")"
  PANE="$(pane_address "${TMUX_PANE:-}")"
  MESSAGE="$(json_get '.message' "$PAYLOAD")"

  case "$event:$notification" in
    PermissionRequest:*) TYPE="PERMISSION_REQUEST" ;;
    Notification:permission_prompt) TYPE="PERMISSION_REQUEST" ;;
    Notification:idle_prompt) TYPE="IDLE" ;;
    Stop:*) TYPE="IDLE" ;;
    *) TYPE="${event:-AGENT_EVENT}" ;;
  esac
}

parse_emit() {
  shift
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --scope) shift; SCOPE="${1:-default}" ;;
      --type) shift; TYPE="${1:-EVENT}" ;;
      --pane) shift; PANE="${1:-}" ;;
      --message) shift; MESSAGE="${1:-}" ;;
      --no-nudge) NUDGE=0 ;;
      *) ;;
    esac
    shift
  done
  [ -n "$TYPE" ] || TYPE="EVENT"
}

case "$MODE" in
  emit) parse_emit "$@" ;;
  hook|codex) parse_hook "$@" ;;
  *) echo "usage: $0 hook|codex|emit [options]" >&2; exit 2 ;;
esac

write_event
nudge_supervisor
exit 0
