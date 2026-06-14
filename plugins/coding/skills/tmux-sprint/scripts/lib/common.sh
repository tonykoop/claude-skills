#!/usr/bin/env bash
# Shared helpers for the tmux-sprint driver scripts (preflight / dispatch /
# restart / launch). Source this; do not execute it directly.
#
#   source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
#
# Everything here is pure shell + jq so the parsing/validation logic can be
# unit-tested without a live tmux server (tests put a fake `tmux` on PATH).

set -euo pipefail

# --- locations ---------------------------------------------------------------

# SKILL_ROOT = the tmux-sprint skill directory. This file lives in scripts/lib/,
# so the skill root is two levels up.
SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
ASSETS_DIR="$SKILL_ROOT/assets"

# Project slug: stable per-checkout namespace under ~/.claude/projects.
# Override with $TMUX_SPRINT_PROJECT or --project. Falls back to the basename
# of the current working directory, sanitized to [A-Za-z0-9._-].
ts_project_slug() {
  local slug="${TMUX_SPRINT_PROJECT:-}"
  [[ -n "$slug" ]] || slug="$(basename "$PWD")"
  printf '%s' "$slug" | tr -c 'A-Za-z0-9._-' '-'
}

ts_state_dir() {
  printf '%s/.claude/projects/%s/tmux-v2' "$HOME" "$(ts_project_slug)"
}

# personas.json lives in the per-project state dir; seeded from assets on first
# run. Echoes the path to a guaranteed-present personas.json.
ts_personas_path() {
  local dir; dir="$(ts_state_dir)"
  local path="$dir/personas.json"
  if [[ ! -f "$path" ]]; then
    mkdir -p "$dir"
    cp "$ASSETS_DIR/personas.default.json" "$path"
    echo "Seeded personas.json from assets/personas.default.json -> $path" >&2
  fi
  printf '%s' "$path"
}

ts_require() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Error: '$1' is required but not found on PATH" >&2
    exit 1
  }
}

# --- persona lookups ---------------------------------------------------------
#
# All of these strip trailing CR: some jq builds (notably cygwin) emit CRLF,
# and a stray \r in a tmux target or pane index silently breaks everything.
ts_jq() { jq "$@" | tr -d '\r'; }

ts_session() { ts_jq -r '.session // "sprint"' "$(ts_personas_path)"; }
ts_window()  { ts_jq -r '.window  // "sprint"' "$(ts_personas_path)"; }

ts_rate_limit() { # ts_rate_limit <runtime>
  local rt="$1"
  ts_jq -r --arg rt "$rt" '.rate_limit_seconds[$rt] // (if $rt=="codex" then 10 else 2 end)' \
    "$(ts_personas_path)"
}

# All pane indices, space separated, in config order.
ts_all_panes() {
  ts_jq -r '.personas | sort_by(.pane) | .[].pane' "$(ts_personas_path)" | paste -sd' ' -
}

# ts_persona_field <pane> <field>  -> scalar value or empty. For array fields
# (e.g. worktrees) the elements are emitted one per line; callers wanting the
# first should pipe to `head -1`.
ts_persona_field() {
  local pane="$1" field="$2"
  ts_jq -r --argjson p "$pane" --arg f "$field" \
    '.personas[] | select(.pane == $p) | .[$f] // empty | if type=="array" then .[] else . end' \
    "$(ts_personas_path)"
}

ts_pane_for_name() { # name -> pane index (empty if unknown)
  local name="$1"
  ts_jq -r --arg n "$name" \
    '.personas[] | select(.name == ($n|ascii_downcase)) | .pane' "$(ts_personas_path)"
}

# --- tmux helpers ------------------------------------------------------------

ts_target() { # ts_target <pane>  ->  sprint:sprint.<pane>
  printf '%s:%s.%s' "$(ts_session)" "$(ts_window)" "$1"
}

ts_capture() { # ts_capture <pane>  -> last screenful of pane text
  tmux capture-pane -p -t "$(ts_target "$1")" 2>/dev/null || true
}

ts_cancel_copy_mode() { # send-keys -X cancel is a no-op outside copy-mode
  tmux send-keys -t "$(ts_target "$1")" -X cancel 2>/dev/null || true
}

# --- pane state detection ----------------------------------------------------
#
# ts_classify <capture-text> -> one STATE token on stdout.
# Ordered most-specific-first so a working codex pane isn't misread as idle.
#
# STATE tokens: WORKING IDLE BLANK DEAD CODEX_EXITED CODEX_UPDATE_PROMPT
ts_classify() {
  local text="$1"
  local trimmed; trimmed="$(printf '%s' "$text" | tr -d '[:space:]')"

  if printf '%s' "$text" | grep -qiE 'codex resume'; then
    echo CODEX_EXITED; return
  fi
  if printf '%s' "$text" | grep -qiE "Update now \(runs 'npm install -g @openai/codex'\)"; then
    echo CODEX_UPDATE_PROMPT; return
  fi
  # codex working
  if printf '%s' "$text" | grep -qiE '(•|◦) (Working|Booting)|Spawned .*\[worker\]'; then
    echo WORKING; return
  fi
  # claude + agy working sentinels (agy/Antigravity shows "esc to cancel" and a
  # "Generating..." spinner, mirroring claude's "esc to interrupt").
  if printf '%s' "$text" | grep -qiE 'Cooked|Leavening|Galloping|thinking…|Processing|esc to interrupt|esc to cancel|Generating\.\.\.'; then
    echo WORKING; return
  fi
  # claude live (idle): context meter, model bracket, or prompt glyph
  if printf '%s' "$text" | grep -qiE 'Ctx:[[:space:]]*[0-9]+%|\[(Opus|Haiku|Sonnet) [0-9]|❯'; then
    echo IDLE; return
  fi
  # agy (Antigravity) live (idle): the shortcuts footer under the prompt box.
  if printf '%s' "$text" | grep -qiE '\? for shortcuts'; then
    echo IDLE; return
  fi
  # codex live (idle): model line + usage meters, OR the "model · path" footer.
  # Newer codex (e.g. gpt-5.5) shows the "gpt-5.5 · <cwd>" footer at idle without
  # a 5h meter until quota is consumed, so accept the middot footer too.
  if printf '%s' "$text" | grep -qiE 'gpt-5(\.[0-9]+)?' \
     && printf '%s' "$text" | grep -qE '5h[[:space:]]+[0-9]+%|·'; then
    echo IDLE; return
  fi
  # truly empty tail -> compacted claude pane
  if [[ -z "$trimmed" ]]; then
    echo BLANK; return
  fi
  # something there, but no live agent signature -> bare shell
  echo DEAD
}

# Map a STATE to a coarse verdict the dispatcher gates on: OK | BUSY | DEAD.
ts_verdict() {
  case "$1" in
    IDLE|BLANK) echo OK ;;
    WORKING)    echo BUSY ;;
    *)          echo DEAD ;;  # DEAD, CODEX_EXITED, CODEX_UPDATE_PROMPT
  esac
}

# Pull a metric out of capture text; empty if absent. Tolerant of no-match
# (grep returns 1) so callers can run under `set -e`.
ts_metric_ctx()    { printf '%s' "$1" | grep -oiE 'Ctx:[[:space:]]*[0-9]+%' | head -1 | grep -oE '[0-9]+%' || true; }
ts_metric_codex5h(){ printf '%s' "$1" | grep -oiE '5h[[:space:]]+[0-9]+%'    | head -1 | grep -oE '[0-9]+%' || true; }
ts_metric_codexwk(){ printf '%s' "$1" | grep -oiE 'weekly[[:space:]]+[0-9]+%'| head -1 | grep -oE '[0-9]+%' || true; }
