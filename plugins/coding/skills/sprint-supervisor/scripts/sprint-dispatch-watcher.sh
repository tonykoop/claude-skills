#!/usr/bin/env bash
# sprint-dispatch-watcher.sh — the PC-side half of mobile cold-start (#160).
#
# The phone drops a dispatch JSON into a shared/synced folder; this watcher,
# running on the PC under a process manager, polls that folder, atomically
# claims a fresh dispatch (so a double-fire never launches two managers),
# validates it, emits the bootstrap command, and writes a status file the phone
# can poll back. See references/dispatch-patterns.md §2.
#
# It deliberately does NOT hardcode how the manager is launched: pass the launch
# command via --exec (e.g. a wrapper that runs `/sprint-supervisor`). With no
# --exec it prints the bootstrap line and writes status only — safe to run
# anywhere, and what the test suite exercises.
#
# Usage:
#   sprint-dispatch-watcher.sh --once                 # process pending, exit
#   sprint-dispatch-watcher.sh                         # loop forever
#   sprint-dispatch-watcher.sh --interval 30 --exec ./launch-sprint.sh
#
# Exit status (in --once mode): 0 dispatched or nothing to do, 2 usage error.
#
# Portable (bash 3.2 / BSD + GNU date) and fail-soft, mirroring
# notify-supervisor.sh. Source it to unit-test json_field / dispatch_is_fresh /
# process_dispatch without launching anything.

set -u

DISPATCH_DIR="${SPRINT_SUPERVISOR_DISPATCH_DIR:-/tmp/sprint-supervisor/dispatch}"
CLAIMED_DIR="$DISPATCH_DIR/claimed"
STATUS_DIR="${SPRINT_SUPERVISOR_STATUS_DIR:-/tmp/sprint-supervisor/status}"
MAX_AGE_SECONDS="${SPRINT_SUPERVISOR_MAX_AGE_SECONDS:-3600}"  # ignore dispatches older than 1h
INTERVAL=30
ONCE=0
EXEC_CMD=""

now_epoch() { # honors NOW_EPOCH_OVERRIDE for tests
  if [ -n "${NOW_EPOCH_OVERRIDE:-}" ]; then printf '%s\n' "$NOW_EPOCH_OVERRIDE"; else date -u +%s; fi
}

iso_now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# Extract a flat JSON string/number field. Dispatch files are small and flat;
# this avoids a jq dependency. Returns empty if absent.
json_field() { # json_field <key> <json>
  printf '%s' "$2" \
    | grep -oE "\"$1\"[[:space:]]*:[[:space:]]*\"?[^\",}]*\"?" \
    | head -1 \
    | sed -E "s/\"$1\"[[:space:]]*:[[:space:]]*//; s/^\"//; s/\"$//"
}

# Convert an ISO-8601 UTC timestamp (…Z) to epoch seconds, portably.
iso_to_epoch() { # iso_to_epoch <2026-06-15T22:14:00Z>
  local ts="$1" e
  e=$(date -u -d "$ts" +%s 2>/dev/null)               # GNU
  if [ -z "$e" ]; then
    e=$(date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$ts" +%s 2>/dev/null)  # BSD/macOS
  fi
  printf '%s\n' "${e:-}"
}

# dispatch_is_fresh <requested_at_iso> <max_age_seconds> -> 0 if fresh enough.
# A missing/unparseable timestamp is treated as fresh (fail open on parsing, not
# on validation) so a clock-format quirk never silently drops a real dispatch.
dispatch_is_fresh() {
  local req="$1" max="$2" req_e age
  [ -z "$req" ] && return 0
  req_e=$(iso_to_epoch "$req")
  [ -z "$req_e" ] && return 0
  age=$(( $(now_epoch) - req_e ))
  [ "$age" -lt 0 ] && age=$(( -age ))   # future-dated clock skew: treat as fresh
  [ "$age" -le "$max" ]
}

# process_dispatch <file> -> claims, validates, writes status, optionally execs.
# Echoes a one-line summary; returns 0 on dispatch, 1 on skip/invalid.
process_dispatch() {
  local file="$1"
  [ -f "$file" ] || return 1
  mkdir -p "$CLAIMED_DIR" "$STATUS_DIR" 2>/dev/null

  # Atomic claim: the first watcher to mv it wins; a racing peer's mv fails.
  local base claimed
  base="$(basename "$file")"
  claimed="$CLAIMED_DIR/$base"
  mv "$file" "$claimed" 2>/dev/null || return 1

  local json action scope queue req
  json="$(cat "$claimed" 2>/dev/null)"
  action="$(json_field action "$json")"
  scope="$(json_field scope "$json")"; scope="${scope:-default}"
  queue="$(json_field queue "$json")"
  req="$(json_field requested_at "$json")"

  if [ "$action" != "cold-start" ]; then
    echo "skip: $base — action '$action' is not cold-start"
    _write_status "$scope" "rejected" "action '$action' not supported"
    return 1
  fi
  if ! dispatch_is_fresh "$req" "$MAX_AGE_SECONDS"; then
    echo "skip: $base — stale (requested_at $req older than ${MAX_AGE_SECONDS}s)"
    _write_status "$scope" "stale" "dispatch older than ${MAX_AGE_SECONDS}s; ignored"
    return 1
  fi

  local bootstrap="/sprint-supervisor scope=${scope}${queue:+ queue=${queue}}"
  _write_status "$scope" "dispatched" "bootstrapping: $bootstrap"
  echo "dispatch: $base — $bootstrap"
  if [ -n "$EXEC_CMD" ]; then
    # Hand the launch to the configured command; never let its failure crash us.
    "$EXEC_CMD" "$scope" "$queue" "$claimed" || echo "warn: exec '$EXEC_CMD' returned $?" >&2
  fi
  return 0
}

_write_status() { # _write_status <scope> <state> <message>
  mkdir -p "$STATUS_DIR" 2>/dev/null
  printf '{"scope":"%s","state":"%s","message":"%s","updated_at":"%s"}\n' \
    "$1" "$2" "$3" "$(iso_now)" > "$STATUS_DIR/$1.status.json" 2>/dev/null || true
}

# Process every pending dispatch once. Returns 0 always (nothing-to-do is fine).
scan_once() {
  [ -d "$DISPATCH_DIR" ] || return 0
  local f found=0
  for f in "$DISPATCH_DIR"/*.json; do
    [ -e "$f" ] || continue          # no-match glob guard
    found=1
    process_dispatch "$f" || true
  done
  [ "$found" -eq 0 ] && echo "idle: no pending dispatch in $DISPATCH_DIR"
  return 0
}

run_watcher() {
  while [ "${1:-}" != "" ]; do
    case "$1" in
      --once) ONCE=1 ;;
      --interval) shift; INTERVAL="${1:-30}" ;;
      --exec) shift; EXEC_CMD="${1:-}" ;;
      --dispatch-dir) shift; DISPATCH_DIR="${1:-$DISPATCH_DIR}"; CLAIMED_DIR="$DISPATCH_DIR/claimed" ;;
      -h|--help) echo "usage: $0 [--once] [--interval N] [--exec CMD] [--dispatch-dir DIR]"; return 0 ;;
      *) echo "unknown arg: $1" >&2; return 2 ;;
    esac
    shift
  done
  mkdir -p "$DISPATCH_DIR" "$STATUS_DIR" 2>/dev/null
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
  run_watcher "$@"
  exit $?
fi
