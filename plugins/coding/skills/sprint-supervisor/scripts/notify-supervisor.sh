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

# GNU `date` supports %3N (ms); BSD/macOS does not. Probe once and fall back to
# epoch seconds, which is unique enough alongside the PID for a fast event file.
TS="$(date -u +%Y%m%dT%H%M%S.%3N 2>/dev/null)"
case "$TS" in
  *%3N|"") TS="$(date -u +%Y%m%dT%H%M%S)-$(date +%s)" ;;
esac
PID="$$"
OUT="$EVENT_DIR/${TS}-${PID}.json"

# Portable ISO-8601-ish UTC timestamp: GNU has `date -Iseconds`, BSD does not.
RECEIVED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Wrap codex's payload with our own envelope so the supervisor has stable
# metadata even if codex's schema changes.
{
  printf '{"received_at":"%s","codex_payload":' "$RECEIVED_AT"
  printf '%s' "$PAYLOAD"
  printf '}\n'
} > "$OUT" 2>/dev/null || true

# Best-effort: keep the dir from growing unbounded. Keep last 500 events.
ls -1t "$EVENT_DIR"/*.json 2>/dev/null | tail -n +501 | xargs -r rm -f 2>/dev/null || true

exit 0
