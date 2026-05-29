#!/usr/bin/env bash
# Codex notify hook → drops a turn-event JSON file the sprint-supervisor reads
# on its next loop iteration. Invoked by codex with the event payload as $1
# (codex passes a JSON string). Must be fast and must never fail loudly —
# codex blocks for the duration of this script.

set -u

EVENT_DIR="${SPRINT_SUPERVISOR_EVENT_DIR:-/tmp/sprint-supervisor/manager-events}"
mkdir -p "$EVENT_DIR" 2>/dev/null

# Payload: codex passes the event JSON as $1. If empty, fall back to stdin.
PAYLOAD="${1:-}"
if [ -z "$PAYLOAD" ] && [ ! -t 0 ]; then
  PAYLOAD="$(cat)"
fi
[ -z "$PAYLOAD" ] && PAYLOAD='{}'

TS="$(date -u +%Y%m%dT%H%M%S.%3N)"
PID="$$"
OUT="$EVENT_DIR/${TS}-${PID}.json"

# Wrap codex's payload with our own envelope so the supervisor has stable
# metadata even if codex's schema changes.
{
  printf '{"received_at":"%s","codex_payload":' "$(date -Iseconds)"
  printf '%s' "$PAYLOAD"
  printf '}\n'
} > "$OUT" 2>/dev/null || true

# Best-effort: keep the dir from growing unbounded. Keep last 500 events.
ls -1t "$EVENT_DIR"/*.json 2>/dev/null | tail -n +501 | xargs -r rm -f 2>/dev/null || true

exit 0
