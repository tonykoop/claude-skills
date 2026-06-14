#!/usr/bin/env bash
# Unit tests for the preflight detection logic and the preflight.sh table.
# Runs without a real tmux server: a fake `tmux` is put on PATH that returns
# canned pane captures from $FAKE_PANES/<pane>.txt.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
# shellcheck source=../scripts/lib/common.sh
source "$ROOT/scripts/lib/common.sh"

fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }
eq()   { [[ "$1" == "$2" ]] || fail "expected '$2', got '$1' ($3)"; }

# --- ts_classify: one assertion per detection branch in SKILL.md -------------

eq "$(ts_classify 'frank@host:~$ codex
To continue this session, run codex resume')" CODEX_EXITED "codex exited"

eq "$(ts_classify "Update now (runs 'npm install -g @openai/codex')? [1] yes [2] no")" \
   CODEX_UPDATE_PROMPT "codex update prompt"

eq "$(ts_classify '• Working on the task (12s)')" WORKING "codex working"
eq "$(ts_classify 'Spawned dan [worker]')"        WORKING "codex spawned worker"
eq "$(ts_classify '✻ Galloping… (esc to interrupt)')" WORKING "claude working"
eq "$(ts_classify 'Processing your request')"     WORKING "claude processing"

eq "$(ts_classify '❯ ready
[Opus 4.6 · Ctx:42%]')" IDLE "claude idle"
eq "$(ts_classify 'some output here  Ctx: 63%')"  IDLE "claude ctx meter"

eq "$(ts_classify 'model gpt-5.4
5h  21%   weekly  20%')" IDLE "codex idle"

# newer codex (gpt-5.5) idles on a "model · cwd" footer without a 5h meter
eq "$(ts_classify '> Improve documentation in @filename
gpt-5.5 · /home/tony/repo')" IDLE "codex 5.5 middot footer idle"

# agy (Antigravity) panes: idle shows "? for shortcuts", working shows
# "esc to cancel" + a "Generating..." spinner
eq "$(ts_classify '>
? for shortcuts    Gemini 3.1 Pro (High)')" IDLE "agy idle"
eq "$(ts_classify '⡿  Generating...
esc to cancel      Gemini 3.1 Pro (High)')" WORKING "agy working"

eq "$(ts_classify '')"          BLANK "blank pane"
eq "$(ts_classify '
  ')"  BLANK "whitespace-only pane"
eq "$(ts_classify 'frank@host:~$ ')" DEAD "bare shell"

# --- ts_verdict --------------------------------------------------------------

eq "$(ts_verdict IDLE)"               OK   "idle->ok"
eq "$(ts_verdict BLANK)"              OK   "blank->ok"
eq "$(ts_verdict WORKING)"            BUSY "working->busy"
eq "$(ts_verdict CODEX_EXITED)"       DEAD "exited->dead"
eq "$(ts_verdict CODEX_UPDATE_PROMPT)" DEAD "update->dead"
eq "$(ts_verdict DEAD)"              DEAD  "dead->dead"

# --- metric extraction -------------------------------------------------------

eq "$(ts_metric_ctx 'foo Ctx: 42% bar')"        "42%" "ctx metric"
eq "$(ts_metric_codex5h 'x 5h  24% y')"         "24%" "5h metric"
eq "$(ts_metric_codexwk 'weekly 18% later')"    "18%" "weekly metric"

# --- preflight.sh end to end against a fake tmux -----------------------------

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export HOME="$TMP/home"; mkdir -p "$HOME"
export TMUX_SPRINT_PROJECT="pf-test"

FAKE_PANES="$TMP/panes"; mkdir -p "$FAKE_PANES"
printf '❯ ready\n[Opus 4.6 · Ctx:42%%]\n'          > "$FAKE_PANES/0.txt"  # alice IDLE
printf '✻ Galloping… (esc to interrupt)\n'         > "$FAKE_PANES/1.txt"  # bob WORKING
printf '❯ idle  Ctx: 63%%\n'                        > "$FAKE_PANES/2.txt"  # cindy IDLE
printf 'gpt-5.4\n5h  42%%  weekly 24%%\n'           > "$FAKE_PANES/3.txt"  # dan IDLE
printf 'gpt-5.4\n5h  21%%  weekly 20%%\n'           > "$FAKE_PANES/4.txt"  # elsa IDLE
printf 'To continue this session, run codex resume\n' > "$FAKE_PANES/5.txt" # frank DEAD

# Fake tmux: only needs to answer `capture-pane -p -t <sess:win.pane>`.
FAKEBIN="$TMP/bin"; mkdir -p "$FAKEBIN"
cat > "$FAKEBIN/tmux" <<'EOF'
#!/usr/bin/env bash
if [[ "$1" == "capture-pane" ]]; then
  for a in "$@"; do prev="${tgt:-}"; [[ "$a" == "-t" ]] && tgt=NEXT && continue
    [[ "${tgt:-}" == "NEXT" ]] && { target="$a"; tgt=""; }
  done
  pane="${target##*.}"
  cat "$FAKE_PANES/$pane.txt" 2>/dev/null || true
  exit 0
fi
exit 0
EOF
chmod +x "$FAKEBIN/tmux"
export FAKE_PANES
export PATH="$FAKEBIN:$PATH"

json="$(bash "$ROOT/scripts/preflight.sh" --json)"
printf '%s' "$json" | jq -e '
  (.[0].name=="alice" and .[0].state=="IDLE"   and .[0].verdict=="OK"   and .[0].ctx=="42%") and
  (.[1].name=="bob"   and .[1].state=="WORKING" and .[1].verdict=="BUSY") and
  (.[3].name=="dan"   and .[3].state=="IDLE"   and .[3].fivehour=="42%") and
  (.[5].name=="frank" and .[5].state=="CODEX_EXITED" and .[5].verdict=="DEAD")
' >/dev/null || fail "preflight --json shape"

table="$(bash "$ROOT/scripts/preflight.sh")"
[[ "$table" == *"pane 0 alice"* ]] || fail "table missing alice row"
[[ "$table" == *"[DEAD]"*       ]] || fail "table missing DEAD verdict"
[[ "$table" == *"[BUSY]"*       ]] || fail "table missing BUSY verdict"

echo "preflight tests passed"
