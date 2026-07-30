#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
bridge="$repo_root/plugins/coding/skills/sprint-supervisor/scripts/supervisor-event.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

mkdir -p "$tmp/bin" "$tmp/events"
cat > "$tmp/bin/tmux" <<EOF
#!/usr/bin/env bash
case "\$1" in
  display-message)
    if printf '%s' "\$*" | grep -q pane_current_command; then
      echo claude
    elif printf '%s' "\$*" | grep -q '%worker'; then
      echo "0:0.7"
    else
      echo "1:0.0"
    fi
    ;;
  capture-pane) printf '❯\\n[Opus 5 · Ctx:80%%]\\nauto mode on\\n' ;;
  send-keys) printf '%s\\n' "\$*" >> "$tmp/send.log" ;;
esac
EOF
chmod +x "$tmp/bin/tmux"
export PATH="$tmp/bin:$PATH"
export SPRINT_SUPERVISOR_EVENT_ROOT="$tmp/events"
export SPRINT_SUPERVISOR_SCOPE="test"
export SPRINT_SUPERVISOR_PANE="1:0.0"
export TMUX_PANE="%worker"

"$bridge" emit --scope test --type PERMISSION_REQUEST --pane 0:0.3 --message "needs judgment"

find "$tmp/events/test.events" -type f -name '*.json' | grep -q . \
  || fail "event JSON not written"
grep -q 'PERMISSION_REQUEST' "$tmp/events/test.pending" \
  || fail "pending marker not written"
grep -q 'Resume /sprint-supervisor for scope test' "$tmp/send.log" \
  || fail "idle supervisor was not nudged"
grep -q 'C-m' "$tmp/send.log" || fail "nudge was not submitted"

before="$(wc -l < "$tmp/send.log")"
"$bridge" emit --scope test --type PERMISSION_REQUEST --pane 0:0.3 --message "duplicate"
after="$(wc -l < "$tmp/send.log")"
[ "$before" = "$after" ] || fail "dedupe did not suppress duplicate nudge"

SPRINT_SUPERVISOR_NUDGE=0 "$bridge" hook '{not-json'
newest="$(find "$tmp/events/test.events" -type f -name '*.json' -printf '%T@ %p\n' \
  | sort -nr | head -1 | cut -d' ' -f2-)"
jq -e '.payload.invalid_json == "{not-json"' "$newest" >/dev/null \
  || fail "invalid hook payload was not preserved safely"

echo "supervisor-event tests passed"
