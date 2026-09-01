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

# Regression: a supervisor that has handed work off to a BACKGROUND shell is
# idle, not busy. Its completed line reads "· done 3:04 PM · 1 shell still
# running". Treating that as busy suppressed every nudge to a supervisor that
# had armed a background watch — silently, and precisely when it needed waking.
tmp2="$(mktemp -d)"
trap 'rm -rf "$tmp" "$tmp2"' EXIT
mkdir -p "$tmp2/bin" "$tmp2/events"
cat > "$tmp2/bin/tmux" <<EOF
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
  capture-pane)
    printf '✻ Brewed for 2m 6s · done 3:04 PM · 1 shell still running\\n❯\\n[Opus 5 · Ctx:80%%]\\nauto mode on\\n'
    ;;
  send-keys) printf '%s\\n' "\$*" >> "$tmp2/send.log" ;;
esac
EOF
chmod +x "$tmp2/bin/tmux"
PATH="$tmp2/bin:$PATH" \
  SPRINT_SUPERVISOR_EVENT_ROOT="$tmp2/events" \
  SPRINT_SUPERVISOR_SCOPE="bg" \
  SPRINT_SUPERVISOR_PANE="1:0.0" \
  TMUX_PANE="%worker" \
  "$bridge" emit --scope bg --type IDLE --pane 0:0.3 --message "background shell open"

[ -f "$tmp2/send.log" ] \
  || fail "supervisor with a background shell was never nudged (is_busy_capture false positive)"
grep -q 'Resume /sprint-supervisor for scope bg' "$tmp2/send.log" \
  || fail "background-shell supervisor was classified busy and not nudged"

# Control: an actively working supervisor must still NOT be nudged.
tmp3="$(mktemp -d)"
mkdir -p "$tmp3/bin" "$tmp3/events"
sed 's|· done 3:04 PM · 1 shell still running|Running 1 shell command…|; s|'"$tmp2"'/send.log|'"$tmp3"'/send.log|' \
  "$tmp2/bin/tmux" > "$tmp3/bin/tmux"
chmod +x "$tmp3/bin/tmux"
PATH="$tmp3/bin:$PATH" \
  SPRINT_SUPERVISOR_EVENT_ROOT="$tmp3/events" \
  SPRINT_SUPERVISOR_SCOPE="busy" \
  SPRINT_SUPERVISOR_PANE="1:0.0" \
  TMUX_PANE="%worker" \
  "$bridge" emit --scope busy --type IDLE --pane 0:0.3 --message "actively working"

if [ -f "$tmp3/send.log" ] && grep -q 'Resume /sprint-supervisor' "$tmp3/send.log"; then
  fail "an actively working supervisor was interrupted — busy detection is now too weak"
fi
rm -rf "$tmp3"

echo "supervisor-event tests passed"
