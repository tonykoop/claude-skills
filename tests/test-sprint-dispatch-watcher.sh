#!/usr/bin/env bash
# tests/test-sprint-dispatch-watcher.sh
#
# Unit + behavior test for sprint-dispatch-watcher.sh (#160): JSON field
# extraction, staleness gating, atomic claim, status write-back, and the
# invalid-action / no-double-launch guards. Sources the script so its functions
# can be called directly, and drives --once against a temp dispatch dir.

set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
watcher="$repo_root/plugins/coding/skills/sprint-supervisor/scripts/sprint-dispatch-watcher.sh"

errors=0
check() { # check <desc> <expected> <actual>
  if [ "$2" = "$3" ]; then echo "    PASS: $1"
  else echo "    FAIL: $1 (expected '$2', got '$3')" >&2; errors=$((errors + 1)); fi
}
checkf() { # checkf <desc> <file-that-should-exist>
  if [ -e "$2" ]; then echo "    PASS: $1"
  else echo "    FAIL: $1 (missing $2)" >&2; errors=$((errors + 1)); fi
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
export SPRINT_SUPERVISOR_DISPATCH_DIR="$tmp/dispatch"
export SPRINT_SUPERVISOR_STATUS_DIR="$tmp/status"
mkdir -p "$SPRINT_SUPERVISOR_DISPATCH_DIR"

# shellcheck source=/dev/null
. "$watcher"
# Re-point dirs the sourced script computed at load time from defaults.
DISPATCH_DIR="$SPRINT_SUPERVISOR_DISPATCH_DIR"
CLAIMED_DIR="$DISPATCH_DIR/claimed"
STATUS_DIR="$SPRINT_SUPERVISOR_STATUS_DIR"

echo "==> json_field extracts flat fields"
J='{"action":"cold-start","scope":"default","queue":"wrfcoin","requested_at":"2026-06-15T22:14:00Z"}'
check "action" "cold-start" "$(json_field action "$J")"
check "scope"  "default"    "$(json_field scope "$J")"
check "queue"  "wrfcoin"    "$(json_field queue "$J")"

echo ""
echo "==> dispatch_is_fresh gates on age"
# requested 100s ago, max 3600 -> fresh
NOW_EPOCH_OVERRIDE=$(( $(date -u -d "2026-06-15T22:14:00Z" +%s 2>/dev/null || date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "2026-06-15T22:14:00Z" +%s) + 100 ))
export NOW_EPOCH_OVERRIDE
dispatch_is_fresh "2026-06-15T22:14:00Z" 3600 && r=fresh || r=stale; check "100s old < 3600 -> fresh" "fresh" "$r"
dispatch_is_fresh "2026-06-15T22:14:00Z" 50   && r=fresh || r=stale; check "100s old > 50  -> stale" "stale" "$r"
unset NOW_EPOCH_OVERRIDE

echo ""
echo "==> process_dispatch claims a valid cold-start and writes status"
printf '%s\n' "$J" > "$DISPATCH_DIR/d1.json"
out="$(MAX_AGE_SECONDS=999999999999 process_dispatch "$DISPATCH_DIR/d1.json")"
case "$out" in *"/sprint-supervisor scope=default queue=wrfcoin"*) r=ok ;; *) r="$out" ;; esac
check "emits bootstrap line" "ok" "$r"
checkf "dispatch claimed (moved)" "$CLAIMED_DIR/d1.json"
check "original removed" "gone" "$([ -e "$DISPATCH_DIR/d1.json" ] && echo present || echo gone)"
checkf "status written" "$STATUS_DIR/default.status.json"
case "$(cat "$STATUS_DIR/default.status.json")" in *'"state":"dispatched"'*) r=ok ;; *) r=bad ;; esac
check "status state=dispatched" "ok" "$r"

echo ""
echo "==> double-fire: re-processing the already-claimed file does not re-dispatch"
process_dispatch "$DISPATCH_DIR/d1.json"; check "second call returns skip" "1" "$?"

echo ""
echo "==> invalid action is rejected"
printf '%s\n' '{"action":"shutdown","scope":"x"}' > "$DISPATCH_DIR/bad.json"
MAX_AGE_SECONDS=999999999999 process_dispatch "$DISPATCH_DIR/bad.json"; check "rejected returns 1" "1" "$?"
case "$(cat "$STATUS_DIR/x.status.json")" in *'"state":"rejected"'*) r=ok ;; *) r=bad ;; esac
check "status state=rejected" "ok" "$r"

echo ""
echo "==> --once on an empty dir is idle and clean"
rm -f "$DISPATCH_DIR"/*.json 2>/dev/null
out="$(bash "$watcher" --once --dispatch-dir "$tmp/empty")"
case "$out" in *"idle: no pending dispatch"*) r=ok ;; *) r="$out" ;; esac
check "idle message" "ok" "$r"

echo ""
if [ "$errors" -gt 0 ]; then
  echo "test-sprint-dispatch-watcher.sh: $errors failure(s)" >&2
  exit 1
fi
echo "test-sprint-dispatch-watcher.sh: all checks passed"
