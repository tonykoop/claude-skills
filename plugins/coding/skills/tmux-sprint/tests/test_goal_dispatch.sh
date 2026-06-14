#!/usr/bin/env bash
# Tests for dispatch.sh --goal flag:
#   - goal is sent to codex panes before the assignment one-liner
#   - goal is NOT sent to claude/agy panes
#   - mixed dispatch (claude + codex): only codex panes get the goal
#   - round record carries goal at top level; dispatches carry it per codex entry

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
export HOME="$TMP/home"; mkdir -p "$HOME"
export TMUX_SPRINT_PROJECT="goal-test"

# Fake tmux: capture-pane reads STATE/<pane>.txt.
# send-keys -l *appends* each sent line to STATE/<pane>.log (for goal tests)
# and overwrites STATE/<pane>.txt (so ts_landed can find the assignment).
STATE="$TMP/state"; mkdir -p "$STATE"; export STATE
for p in 0 1 2 3 4 5; do
  printf '❯ idle  Ctx: 50%%\n' > "$STATE/$p.txt"
  : > "$STATE/$p.log"
done

BIN="$TMP/bin"; mkdir -p "$BIN"
cat > "$BIN/tmux" <<'EOF'
#!/usr/bin/env bash
cmd="$1"; shift || true
target=""; lit=""; haslit=0
args=("$@")
for ((i=0; i<${#args[@]}; i++)); do
  case "${args[$i]}" in
    -t) target="${args[$((i+1))]}";;
    -l) lit="${args[$((i+1))]}"; haslit=1;;
  esac
done
pane="${target##*.}"
case "$cmd" in
  capture-pane) cat "$STATE/$pane.txt" 2>/dev/null || true;;
  send-keys)
    if [[ "$haslit" -eq 1 ]]; then
      printf '%s\n' "$lit" >> "$STATE/$pane.log"
      printf '%s\n' "$lit" > "$STATE/$pane.txt"
    fi
    ;;
esac
exit 0
EOF
chmod +x "$BIN/tmux"; export PATH="$BIN:$PATH"

PLANS="$TMP/ws/docs/plans"; mkdir -p "$PLANS"
PREAMBLE="$(cat "$ROOT/assets/assignment-preamble.txt")"

make_plan() {  # make_plan <path> <title>
  { echo "# $2"; echo; printf '%s\n' "$PREAMBLE"; echo; echo "Do the thing."; } > "$1"
}

alice_plan="$PLANS/alice-r20.md"; make_plan "$alice_plan" "Alice round 20"
dan_plan="$PLANS/dan-r20.md";     make_plan "$dan_plan"   "Dan round 20"
elsa_plan="$PLANS/elsa-r20.md";   make_plan "$elsa_plan"  "Elsa round 20"

D() { bash "$ROOT/scripts/dispatch.sh" "$@"; }
GOAL_TEXT="Complete the WRF-20 burn mechanic without stopping until tests pass and a draft PR is open"

# ── test 1: --goal sent to codex pane (dan, pane 3) ─────────────────────────
out="$(D --round 20 --goal "$GOAL_TEXT" --to dan --assignment "$dan_plan" 2>&1)" \
  || fail "codex goal dispatch should succeed; got: $out"
[[ "$out" == *"✓ dan"* ]] || fail "expected success for dan; got: $out"

log="$STATE/3.log"
grep -qF "/goal $GOAL_TEXT" "$log" \
  || fail "goal line not found in codex pane 3 log; log: $(cat "$log")"

# goal must appear BEFORE the assignment one-liner
goal_line="$(grep -n "/goal " "$log" | head -1 | cut -d: -f1)"
assign_line="$(grep -n "Round 20" "$log" | head -1 | cut -d: -f1)"
[[ -n "$goal_line" && -n "$assign_line" && "$goal_line" -lt "$assign_line" ]] \
  || fail "goal must appear before the assignment one-liner; log:\n$(cat "$log")"

# round record: top-level goal field
rec="$HOME/.claude/projects/goal-test/tmux-v2/rounds/round-20.json"
[[ -f "$rec" ]] || fail "round record not written: $rec"
jq -e --arg g "$GOAL_TEXT" '.goal == $g' "$rec" >/dev/null \
  || fail "round record missing top-level goal; record: $(cat "$rec")"

# dispatch entry: goal field on codex entry
jq -e --arg g "$GOAL_TEXT" '.dispatches[0].goal == $g' "$rec" >/dev/null \
  || fail "dan dispatch entry missing goal field; record: $(cat "$rec")"

# ── test 2: --goal NOT sent to claude pane (alice, pane 0) ──────────────────
# Reset state
for p in 0 1 2 3 4 5; do
  printf '❯ idle  Ctx: 50%%\n' > "$STATE/$p.txt"
  : > "$STATE/$p.log"
done
export TMUX_SPRINT_PROJECT="goal-claude-test"

out="$(D --round 21 --goal "$GOAL_TEXT" --to alice --assignment "$alice_plan" 2>&1)" \
  || fail "claude goal dispatch should succeed; got: $out"
[[ "$out" == *"✓ alice"* ]] || fail "expected success for alice; got: $out"

log="$STATE/0.log"
grep -qF "/goal " "$log" && fail "goal line should NOT appear in claude pane 0 log"

# dispatch entry: goal should be null for claude pane
rec="$HOME/.claude/projects/goal-claude-test/tmux-v2/rounds/round-21.json"
jq -e '.dispatches[0].goal == null' "$rec" >/dev/null \
  || fail "alice dispatch entry should have null goal; record: $(cat "$rec")"

# ── test 3: mixed dispatch — goal only for codex panes ──────────────────────
for p in 0 1 2 3 4 5; do
  printf '❯ idle  Ctx: 50%%\n' > "$STATE/$p.txt"
  : > "$STATE/$p.log"
done
export TMUX_SPRINT_PROJECT="goal-mixed-test"

out="$(D --round 22 --goal "$GOAL_TEXT" \
  --to alice --assignment "$alice_plan" \
  --to dan   --assignment "$dan_plan" \
  2>&1)" || fail "mixed goal dispatch should succeed; got: $out"

[[ "$out" == *"✓ alice"* ]] || fail "expected success for alice in mixed; got: $out"
[[ "$out" == *"✓ dan"*   ]] || fail "expected success for dan in mixed; got: $out"

grep -qF "/goal " "$STATE/0.log" && fail "goal should NOT appear in alice (pane 0) log"
grep -qF "/goal " "$STATE/3.log" \
  || fail "goal should appear in dan (pane 3) log; log: $(cat "$STATE/3.log")"

# ── test 4: no --goal flag -> no goal lines anywhere ────────────────────────
for p in 0 1 2 3 4 5; do
  printf '❯ idle  Ctx: 50%%\n' > "$STATE/$p.txt"
  : > "$STATE/$p.log"
done
export TMUX_SPRINT_PROJECT="no-goal-test"

out="$(D --round 23 --to dan --assignment "$dan_plan" 2>&1)" \
  || fail "dispatch without --goal should succeed; got: $out"

grep -qF "/goal " "$STATE/3.log" && fail "goal line should NOT appear when --goal not set"

rec="$HOME/.claude/projects/no-goal-test/tmux-v2/rounds/round-23.json"
jq -e '.goal == null' "$rec" >/dev/null \
  || fail "round record goal should be null when --goal not set; record: $(cat "$rec")"

echo "goal dispatch tests passed"
