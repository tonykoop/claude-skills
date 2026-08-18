#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
gate="$repo_root/plugins/coding/skills/sprint-supervisor/scripts/stop-gate.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

mkdir -p "$tmp/bin"
cat > "$tmp/bin/tmux" <<'SH'
#!/usr/bin/env bash
if [ "${1:-}" = "capture-pane" ]; then
  target=""
  while [ "$#" -gt 0 ]; do
    [ "$1" = "-t" ] && { shift; target="${1:-}"; }
    shift || true
  done
  printf '%s\n' "$target" >> "$FAKE_TMUX_LOG"
  cat "$FAKE_TMUX_CAPTURE"
  exit 0
fi
exit 1
SH
chmod +x "$tmp/bin/tmux"
export PATH="$tmp/bin:$PATH"
export FAKE_TMUX_LOG="$tmp/tmux.log"

cat > "$tmp/open.txt" <<'CAP'
Would you like to run the following command?
$ echo stale-command
Press enter to confirm or esc to cancel
stale-command

Would you like to run the following command?

$ git status

Press enter to confirm or esc to cancel
CAP

cat > "$tmp/answered-idle.txt" <<'CAP'
Would you like to run the following command?

$ git status

Press enter to confirm or esc to cancel

Running git status...
On branch main
nothing to commit, working tree clean

› Use /skills to list available skills
gpt-5.6-sol · Context 13% left
CAP

cat > "$tmp/active.txt" <<'CAP'
Do you want to proceed?

$ python3 -m pytest

Working on tests
esc to interrupt
CAP

cat > "$tmp/edit.txt" <<'CAP'
Would you like to make the following edits?
Edited plugins/coding/skills/sprint-supervisor/scripts/stop-gate.sh
❯ 1. Yes
  2. No
CAP

echo "==> current command prompt blocks with actionable detail"
out="$(
  FAKE_TMUX_CAPTURE="$tmp/open.txt" \
  SPRINT_SUPERVISED_PANES="1:0.0" \
  SPRINT_SUPERVISOR_STATE_ROOT="$tmp/open-state" \
  "$gate"
)"
printf '%s' "$out" | jq -e \
  '.decision == "block" and (.reason | contains("[1:0.0] $ git status"))' >/dev/null \
  || fail "open prompt was not blocked with command detail"
printf '%s' "$out" | grep -q 'stale-command' \
  && fail "block detail reported an older prompt"

echo "==> answered prompt in scrollback does not block an idle pane"
out="$(
  FAKE_TMUX_CAPTURE="$tmp/answered-idle.txt" \
  SPRINT_SUPERVISED_PANES="1:0.0" \
  SPRINT_SUPERVISOR_STATE_ROOT="$tmp/answered-state" \
  "$gate"
)"
[ -z "$out" ] || fail "answered scrollback prompt produced a false block"

echo "==> answered prompt in scrollback does not block an active pane"
out="$(
  FAKE_TMUX_CAPTURE="$tmp/active.txt" \
  SPRINT_SUPERVISED_PANES="1:0.0" \
  SPRINT_SUPERVISOR_STATE_ROOT="$tmp/active-state" \
  "$gate"
)"
[ -z "$out" ] || fail "active pane produced a false block"

echo "==> current edit prompt remains detectable"
out="$(
  FAKE_TMUX_CAPTURE="$tmp/edit.txt" \
  SPRINT_SUPERVISED_PANES="1:0.0" \
  SPRINT_SUPERVISOR_STATE_ROOT="$tmp/edit-state" \
  "$gate"
)"
printf '%s' "$out" | jq -e '.decision == "block"' >/dev/null \
  || fail "edit prompt was not blocked"

echo "==> configured bound self-releases"
for expected in 1 2; do
  out="$(
    FAKE_TMUX_CAPTURE="$tmp/open.txt" \
    SPRINT_SUPERVISED_PANES="1:0.0" \
    SPRINT_SUPERVISOR_STATE_ROOT="$tmp/bounded-state" \
    SPRINT_STOP_GATE_MAX=2 \
    "$gate"
  )"
  printf '%s' "$out" | jq -e --arg count "$expected/2" \
    '.decision == "block" and (.reason | contains($count))' >/dev/null \
    || fail "bound did not block attempt $expected"
done
out="$(
  FAKE_TMUX_CAPTURE="$tmp/open.txt" \
  SPRINT_SUPERVISED_PANES="1:0.0" \
  SPRINT_SUPERVISOR_STATE_ROOT="$tmp/bounded-state" \
  SPRINT_STOP_GATE_MAX=2 \
  "$gate"
)"
[ -z "$out" ] || fail "bound did not release after two blocks"

echo "==> malformed bound falls back to five without stderr or livelock"
for expected in 1 2 3 4 5; do
  out="$(
    FAKE_TMUX_CAPTURE="$tmp/open.txt" \
    SPRINT_SUPERVISED_PANES="1:0.0" \
    SPRINT_SUPERVISOR_STATE_ROOT="$tmp/invalid-state" \
    SPRINT_STOP_GATE_MAX=abc \
    "$gate" 2> "$tmp/invalid.err"
  )"
  printf '%s' "$out" | jq -e --arg count "$expected/5" \
    '.decision == "block" and (.reason | contains($count))' >/dev/null \
    || fail "invalid bound did not use fallback on attempt $expected"
  [ ! -s "$tmp/invalid.err" ] || fail "invalid bound emitted stderr"
done
out="$(
  FAKE_TMUX_CAPTURE="$tmp/open.txt" \
  SPRINT_SUPERVISED_PANES="1:0.0" \
  SPRINT_SUPERVISOR_STATE_ROOT="$tmp/invalid-state" \
  SPRINT_STOP_GATE_MAX=abc \
  "$gate" 2> "$tmp/invalid.err"
)"
[ -z "$out" ] || fail "invalid bound fallback did not release"
[ ! -s "$tmp/invalid.err" ] || fail "invalid bound release emitted stderr"

echo "==> empty explicit setting falls back to lockfile targets"
mkdir -p "$tmp/lock-state"
cat > "$tmp/lock-state/scope.lock" <<'JSON'
{"targets":["lock:0.7"]}
JSON
: > "$FAKE_TMUX_LOG"
out="$(
  FAKE_TMUX_CAPTURE="$tmp/open.txt" \
  SPRINT_SUPERVISED_PANES="" \
  SPRINT_SUPERVISOR_SCOPE="scope" \
  SPRINT_SUPERVISOR_STATE_ROOT="$tmp/lock-state" \
  "$gate"
)"
printf '%s' "$out" | jq -e '.decision == "block"' >/dev/null \
  || fail "lockfile fallback did not block"
grep -qx 'lock:0.7' "$FAKE_TMUX_LOG" \
  || fail "lockfile target was not captured"

echo "stop-gate tests passed"
