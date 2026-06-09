#!/usr/bin/env bash
# Tests for dispatch.sh: assignment validation (path + preamble), preflight
# gating, and round-record persistence. Uses a fake `tmux` that echoes sent
# text back through capture-pane so the verify step can confirm a "landing".

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
export HOME="$TMP/home"; mkdir -p "$HOME"
export TMUX_SPRINT_PROJECT="disp-test"

# Fake tmux: capture-pane reads STATE/<pane>.txt; send-keys -l overwrites it
# (simulating the prompt echoing into the pane). Seed all panes IDLE.
STATE="$TMP/state"; mkdir -p "$STATE"; export STATE
for p in 0 1 2 3 4 5; do printf '❯ idle  Ctx: 50%%\n' > "$STATE/$p.txt"; done
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
  send-keys)    [[ "$haslit" -eq 1 ]] && printf '%s\n' "$lit" > "$STATE/$pane.txt";;
esac
exit 0
EOF
chmod +x "$BIN/tmux"; export PATH="$BIN:$PATH"

PLANS="$TMP/ws/docs/plans"; mkdir -p "$PLANS"
PREAMBLE="$(cat "$ROOT/assets/assignment-preamble.txt")"

good="$PLANS/alice-r1.md"
{ echo "# Alice round 1"; echo; printf '%s\n' "$PREAMBLE"; echo; echo "Do the thing."; } > "$good"

nopre="$PLANS/bob-r1.md"
{ echo "# Bob round 1"; echo "Do the thing (no preamble)."; } > "$nopre"

badpath="$TMP/ws/notes/cindy-r1.md"; mkdir -p "$(dirname "$badpath")"
{ printf '%s\n' "$PREAMBLE"; } > "$badpath"

D() { bash "$ROOT/scripts/dispatch.sh" "$@"; }

# 1. missing preamble -> abort, nothing sent
if D --round 1 --to bob --assignment "$nopre" >/dev/null 2>&1; then
  fail "dispatch should abort when preamble is missing"
fi

# 2. assignment outside docs/plans/ -> abort
if D --round 1 --to cindy --assignment "$badpath" >/dev/null 2>&1; then
  fail "dispatch should abort when assignment is outside docs/plans/"
fi

# 3. mismatched --to / --assignment counts -> abort
if D --round 1 --to alice --to bob --assignment "$good" >/dev/null 2>&1; then
  fail "dispatch should abort on uneven --to/--assignment counts"
fi

# 4. unknown persona -> abort
if D --round 1 --to nobody --assignment "$good" >/dev/null 2>&1; then
  fail "dispatch should abort on unknown persona"
fi

# 5. valid dispatch -> succeeds and writes a round record
out="$(D --round 7 --manager claude-opus-4-6 --to alice --assignment "$good" 2>&1)" \
  || fail "valid dispatch should succeed; output: $out"
[[ "$out" == *"✓ alice"* ]] || fail "expected success line for alice; got: $out"

rec="$HOME/.claude/projects/disp-test/tmux-v2/rounds/round-7.json"
[[ -f "$rec" ]] || fail "round record not written: $rec"
jq -e '
  .round == 7 and .manager == "claude-opus-4-6" and
  (.dispatches | length) == 1 and
  .dispatches[0].persona == "alice" and
  .dispatches[0].status == "OK"
' "$rec" >/dev/null || fail "round record shape wrong: $(cat "$rec")"

echo "dispatch tests passed"
