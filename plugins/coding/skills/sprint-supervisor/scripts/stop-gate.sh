#!/usr/bin/env bash
# Stop hook for sprint-supervisor: do not go idle while an agent is waiting.
#
# The wake nudge in supervisor-event.sh only fires when the supervisor pane is
# IDLE — it deliberately refuses to interrupt a busy supervisor. That leaves one
# uncovered window: a permission prompt raised while the supervisor is mid-turn
# waits until the supervisor next goes idle, which is precisely when it is about
# to stop. Observed cost on 2026-08-11: a Codex manager sat blocked for minutes
# while the supervisor was busy elsewhere, and the user had to intervene by hand.
#
# This gate closes that window. On Stop it captures each supervised pane and, if
# any has an unanswered permission prompt, emits
#   {"decision":"block","reason":...}
# which returns control to the supervisor instead of ending the turn.
#
# Panes come from SPRINT_SUPERVISED_PANES ("0:0.0 2:0.0"), falling back to the
# scope lockfile's targets. Bounded by SPRINT_STOP_GATE_MAX consecutive blocks so
# a prompt the supervisor cannot answer (a refusal-shape awaiting the owner)
# cannot livelock the session.

set -uo pipefail

SCOPE="${SPRINT_SUPERVISOR_SCOPE:-default}"
STATE_DIR="${SPRINT_SUPERVISOR_STATE_ROOT:-/tmp/sprint-supervisor}"
STATE="$STATE_DIR/$SCOPE.stop-gate.count"
MAX="${SPRINT_STOP_GATE_MAX:-5}"

mkdir -p "$STATE_DIR" 2>/dev/null || true
command -v tmux >/dev/null 2>&1 || exit 0
command -v jq   >/dev/null 2>&1 || exit 0

panes_from_lock() {
  local lock="$STATE_DIR/$SCOPE.lock"
  [ -f "$lock" ] || return 0
  jq -r '(.supervised_panes // .targets // [])[]?' "$lock" 2>/dev/null || true
}

PANES="${SPRINT_SUPERVISED_PANES:-}"
[ -n "$PANES" ] || PANES="$(panes_from_lock | tr '\n' ' ')"
[ -n "${PANES// /}" ] || exit 0

pending=""
for p in $PANES; do
  cap="$(tmux capture-pane -p -t "$p" -S -40 2>/dev/null)" || continue
  [ -n "$cap" ] || continue

  # An open prompt still awaiting an answer. Covers claude / codex / gemini
  # phrasings by matching the confirmation footer as well as the question.
  printf '%s' "$cap" | grep -qE \
    'Press enter to confirm or esc to cancel|Would you like to (make|run) the following|Do you want to proceed\?|Requesting permission for:' \
    || continue

  # Skip a pane that is actively working: the prompt was already answered and
  # this is just scrollback. The activity marker is the reliable signal, not a
  # verb list (the spinner verb is unbounded and whimsical).
  printf '%s' "$cap" | tail -3 | grep -qE 'esc to interrupt' && continue

  detail="$(printf '%s' "$cap" | grep -E '^[[:space:]]*(Reason:|\$ )' | head -2 \
            | tr '\n' ' ' | cut -c1-300)"
  pending="${pending}[$p] ${detail}
"
done

if [ -z "$pending" ]; then
  rm -f "$STATE"
  exit 0
fi

n=0
[ -f "$STATE" ] && n="$(cat "$STATE" 2>/dev/null || echo 0)"
case "$n" in ''|*[!0-9]*) n=0 ;; esac
n=$((n + 1))
printf '%s' "$n" > "$STATE"

if [ "$n" -gt "$MAX" ]; then
  # Stop fighting it. A prompt this persistent needs the owner, not another
  # loop; let the turn end so the supervisor can surface it.
  rm -f "$STATE"
  exit 0
fi

reason="SUPERVISOR STOP GATE ($n/$MAX): a supervised agent pane is WAITING on a permission prompt. Do not end your turn. Answer it now using the approval rubric (benign read-only/test/build => approve; refusal-shape => leave the prompt open and escalate to the owner). Pending:
${pending}"

jq -cn --arg r "$reason" '{decision:"block", reason:$r}'
exit 0
