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
PROMPT_FOOTER_RE='Press enter to confirm or esc to cancel'
PROMPT_QUESTION_RE='Would you like to (make|run) the following|Do you want to proceed[?]|Requesting permission for:'

# The bound is a safety valve, so a typo must not silently turn it off. Keep the
# accepted range deliberately small: more than 100 forced turns is not useful.
case "$MAX" in ''|*[!0-9]*) MAX=5 ;; esac
if [ "${#MAX}" -gt 3 ] || [ "$MAX" -lt 1 ] || [ "$MAX" -gt 100 ]; then
  MAX=5
fi

mkdir -p "$STATE_DIR" 2>/dev/null || true
command -v tmux >/dev/null 2>&1 || exit 0
command -v jq   >/dev/null 2>&1 || exit 0

panes_from_lock() {
  local lock="$STATE_DIR/$SCOPE.lock"
  [ -f "$lock" ] || return 0
  jq -r '(.supervised_panes // .targets // [])[]?' "$lock" 2>/dev/null || true
}

latest_prompt() {
  awk -v footer="$PROMPT_FOOTER_RE" -v question="$PROMPT_QUESTION_RE" '
    $0 ~ question { start = NR; line = NR; kind = "question" }
    $0 ~ footer { line = NR; kind = "footer" }
    END { if (line) print line, kind, (start ? start : line) }
  '
}

PANES="${SPRINT_SUPERVISED_PANES:-}"
[ -n "$PANES" ] || PANES="$(panes_from_lock | tr '\n' ' ')"
[ -n "${PANES// /}" ] || exit 0

pending=""
for p in $PANES; do
  cap="$(tmux capture-pane -p -t "$p" -S -40 2>/dev/null)" || continue
  [ -n "$cap" ] || continue

  # Find the most recent prompt marker. Covers claude / codex / gemini
  # phrasings by matching the confirmation footer as well as the question.
  prompt_meta="$(printf '%s\n' "$cap" | latest_prompt)"
  [ -n "$prompt_meta" ] || continue
  read -r prompt_line prompt_kind prompt_start <<< "$prompt_meta"
  after_prompt="$(printf '%s\n' "$cap" | tail -n "+$((prompt_line + 1))")"
  prompt_block="$(printf '%s\n' "$cap" | tail -n "+$prompt_start")"

  # A newer agent input cursor or activity marker proves the matching prompt is
  # scrollback from an already-answered request, not the current pane state. A
  # footer is the end of a permission dialog, so any later input cursor is new;
  # question-only edit dialogs retain numbered choice cursors and need the
  # narrower empty/default-input match.
  if [ "$prompt_kind" = "footer" ]; then
    printf '%s\n' "$after_prompt" \
      | grep -qE '^[[:space:]]*[❯›>]([[:space:]]|$)' && continue
  else
    printf '%s\n' "$after_prompt" \
      | grep -qE '^[[:space:]]*[❯›>][[:space:]]*($|Use /skills([[:space:]]|$))' && continue
  fi
  printf '%s\n' "$after_prompt" | tail -5 | grep -qE 'esc to interrupt' && continue

  # Command prompts carry a Reason:/$ line. Edit prompts carry neither, so fall
  # back to the question and the edited path — a bare pane id tells the
  # supervisor nothing about what it is being sent back to answer.
  detail="$(printf '%s' "$prompt_block" | grep -E '^[[:space:]]*(Reason:|\$ )' | head -2 \
            | tr '\n' ' ' | cut -c1-300)"
  if [ -z "${detail// /}" ]; then
    detail="$(printf '%s' "$prompt_block" \
              | grep -E 'Would you like to|Requesting permission for:|Edited |Edit file' \
              | tail -2 | tr '\n' ' ' | tr -s '[:space:]' ' ' | cut -c1-300)"
  fi
  [ -n "${detail// /}" ] || detail="(prompt open; capture the pane to see it)"
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
[ "${#n}" -le 3 ] || n=0
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
