#!/usr/bin/env bash
# Claude PermissionRequest hook for sprint supervision.
#
# Auto-allows only:
#   1. narrow, single-command read-only diagnostics; and
#   2. tmux inspection/send-keys commands issued by the declared supervisor pane.
#
# Everything else remains an ordinary Claude permission prompt and emits an
# event for the supervisor. This script never enables bypassPermissions and
# never persists broad permission rules.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
INPUT="$(cat 2>/dev/null || true)"
[ -n "$INPUT" ] || INPUT='{}'

json_get() {
  printf '%s' "$INPUT" | jq -r "$1 // empty" 2>/dev/null || true
}

current_pane_address() {
  [ -n "${TMUX_PANE:-}" ] || return 0
  tmux display-message -p -t "$TMUX_PANE" \
    '#{session_name}:#{window_index}.#{pane_index}' 2>/dev/null || true
}

declared_supervisor_pane() {
  if [ -n "${SPRINT_SUPERVISOR_PANE:-}" ]; then
    printf '%s' "$SPRINT_SUPERVISOR_PANE"
    return
  fi
  local scope="${SPRINT_SUPERVISOR_SCOPE:-default}"
  local lock="/tmp/sprint-supervisor/$scope.lock"
  [ -f "$lock" ] || return 0
  jq -r '.supervisor_pane // .manager_pane // empty' "$lock" 2>/dev/null || true
}

is_declared_supervisor() {
  local here expected
  here="$(current_pane_address)"
  expected="$(declared_supervisor_pane)"
  [ -n "$here" ] && [ "$here" = "$expected" ]
}

is_refusal_shape() {
  printf '%s' "$1" | grep -qiE \
    '(^|[;&|[:space:]])rm[[:space:]]+-rf|git[[:space:]]+push[[:space:]]+--force([^ -]|$)|git[[:space:]]+reset[[:space:]]+--hard|git[[:space:]]+clean|DROP[[:space:]]+(TABLE|DATABASE)|FLUSHALL|docker[[:space:]]+push|npm[[:space:]]+publish|systemctl|shutdown|reboot|crontab|chmod[[:space:]]+777|\.ssh/|(^|[[:space:]])sudo([[:space:]]|$)|--dangerously-skip-permissions|bypassPermissions|skipPermissions'
}

is_single_command() {
  # Reject shell composition, redirection, substitutions, and newlines. The
  # narrow read-only allowlist below is intended for one command only.
  case "$1" in
    *$'\n'*|*$'\r'*) return 1 ;;
  esac
  ! printf '%s' "$1" | grep -qE '[;&|<>`]|[$][(]'
}

is_safe_readonly() {
  local command="$1"
  is_single_command "$command" || return 1
  printf '%s' "$command" | grep -qE \
    '^[[:space:]]*(git[[:space:]]+(status|diff|log|show|rev-parse|merge-base|ls-remote)([[:space:]]|$)|gh[[:space:]]+(pr[[:space:]]+(view|list|diff|checks)|issue[[:space:]]+(view|list))([[:space:]]|$)|rg([[:space:]]|$)|grep([[:space:]]|$)|ls([[:space:]]|$)|cat([[:space:]]|$)|head([[:space:]]|$)|tail([[:space:]]|$)|wc([[:space:]]|$)|jq([[:space:]]|$)|pwd([[:space:]]|$)|df([[:space:]]|$)|du([[:space:]]|$)|ps([[:space:]]|$)|pgrep([[:space:]]|$)|tmux[[:space:]]+(capture-pane|list-panes|list-sessions|has-session|display-message|show-options|show-environment)([[:space:]]|$))'
}

is_supervisor_tmux() {
  is_declared_supervisor || return 1
  is_single_command "$1" || return 1
  is_refusal_shape "$1" && return 1
  printf '%s' "$1" | grep -qE \
    '^[[:space:]]*tmux[[:space:]]+(capture-pane|send-keys|list-panes|list-sessions|has-session|display-message|show-options|show-environment)([[:space:]]|$)'
}

emit_allow() {
  printf '%s\n' \
    '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}'
}

signal_supervisor() {
  local kind="$1"
  SPRINT_SUPERVISOR_NUDGE=1 \
    "$HERE/supervisor-event.sh" emit \
      --scope "${SPRINT_SUPERVISOR_SCOPE:-default}" \
      --type "$kind" \
      --pane "$(current_pane_address)" \
      --message "Claude permission requires supervisor judgment" \
      >/dev/null 2>&1 || true
}

tool="$(json_get '.tool_name')"
command="$(json_get '.tool_input.command')"

[ "$tool" = "Bash" ] || exit 0

if is_refusal_shape "$command"; then
  signal_supervisor "REFUSAL_PROMPT"
  exit 0
fi
if is_supervisor_tmux "$command" || is_safe_readonly "$command"; then
  emit_allow
  exit 0
fi

signal_supervisor "PERMISSION_REQUEST"
exit 0
