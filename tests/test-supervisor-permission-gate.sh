#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
gate="$repo_root/plugins/coding/skills/sprint-supervisor/scripts/permission-gate.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }
assert_allow() { printf '%s' "$1" | jq -e '.hookSpecificOutput.decision.behavior=="allow"' >/dev/null || fail "$2"; }
assert_empty() { [ -z "$1" ] || fail "$2: unexpected output $1"; }

mkdir -p "$tmp/bin" "$tmp/events"
cat > "$tmp/bin/tmux" <<'EOF'
#!/usr/bin/env bash
case "$1" in
  display-message)
    target=""
    while [ "$#" -gt 0 ]; do
      [ "$1" = "-t" ] && { shift; target="$1"; }
      shift || true
    done
    case "$target" in
      %supervisor|1:0.0) echo "1:0.0" ;;
      *) echo "0:0.7" ;;
    esac
    ;;
  capture-pane) echo "• Working (5s • esc to interrupt)" ;;
esac
EOF
chmod +x "$tmp/bin/tmux"
export PATH="$tmp/bin:$PATH"
export SPRINT_SUPERVISOR_EVENT_ROOT="$tmp/events"
export SPRINT_SUPERVISOR_SCOPE="test"
export SPRINT_SUPERVISOR_PANE="1:0.0"

request() {
  local command="$1"
  jq -n --arg command "$command" \
    '{hook_event_name:"PermissionRequest",tool_name:"Bash",tool_input:{command:$command}}' \
    | "$gate"
}

echo "==> read-only single commands are auto-allowed"
out="$(TMUX_PANE=%worker request 'gh pr view 123 --json headRefOid')"
assert_allow "$out" "gh pr view should be allowed"

echo "==> shell composition is not auto-allowed"
out="$(TMUX_PANE=%worker request 'cd /tmp && gh pr view 123')"
assert_empty "$out" "compound command should stay ask"
out="$(TMUX_PANE=%worker request 'gh pr view 123 | sh')"
assert_empty "$out" "piped command should stay ask"
out="$(TMUX_PANE=%worker request $'gh pr view 123\nwhoami')"
assert_empty "$out" "multiline command should stay ask"

echo "==> supervisor tmux send-keys is auto-allowed"
out="$(TMUX_PANE=%supervisor request 'tmux send-keys -t 0:0.2 C-m')"
assert_allow "$out" "declared supervisor send-keys should be allowed"

echo "==> supervisor tmux shell composition is not auto-allowed"
out="$(TMUX_PANE=%supervisor request 'tmux capture-pane -p -t 0:0.2; whoami')"
assert_empty "$out" "compound supervisor tmux command should stay ask"
out="$(TMUX_PANE=%supervisor request 'tmux capture-pane -p -t 0:0.2 | sh')"
assert_empty "$out" "piped supervisor tmux command should stay ask"

echo "==> worker tmux send-keys is not auto-allowed"
out="$(TMUX_PANE=%worker request 'tmux send-keys -t 0:0.2 C-m')"
assert_empty "$out" "worker send-keys should stay ask"

echo "==> refusal shapes stay ask and emit an event"
out="$(TMUX_PANE=%worker request 'git reset --hard HEAD')"
assert_empty "$out" "refusal should not be auto-allowed"
find "$tmp/events/test.events" -type f -name '*.json' | grep -q . \
  || fail "refusal event was not written"
grep -q 'REFUSAL_PROMPT' "$tmp/events/test.pending" \
  || fail "refusal was not recorded in pending marker"

echo "permission-gate tests passed"
