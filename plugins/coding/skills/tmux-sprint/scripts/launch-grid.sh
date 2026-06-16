#!/usr/bin/env bash
# tmux-sprint launch-grid — create the persona grid the driver dispatches to.
#
# The preflight/dispatch/restart scripts DRIVE a grid; they assume one exists.
# This is the missing launch step: it builds the clean two-session topology
# described in SKILL.md (a "manager" session + a "sprint" session whose single
# window holds one pane per persona) and starts each persona's runtime.
#
#   launch-grid.sh                 # build sprint grid from personas.json
#   launch-grid.sh --with-manager  # also create the manager session
#   launch-grid.sh --no-start      # build panes but don't launch claude/codex
#   launch-grid.sh --kill          # tear down sprint (+ manager with --with-manager)
#
# Seeds personas.json from assets/personas.default.json on first run. Edit that
# file to remap panes, change models, or add personas before launching.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"

WITH_MANAGER=0
START=1
KILL=0

usage() { sed -n '2,16p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-manager) WITH_MANAGER=1; shift ;;
    --no-start)     START=0; shift ;;
    --kill)         KILL=1; shift ;;
    --project)      export TMUX_SPRINT_PROJECT="$2"; shift 2 ;;
    -h|--help)      usage; exit 0 ;;
    *) echo "Error: unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

ts_require tmux
ts_require jq

SESSION="$(ts_session)"
WINDOW="$(ts_window)"

if [[ "$KILL" -eq 1 ]]; then
  tmux kill-session -t "$SESSION" 2>/dev/null && echo "killed session: $SESSION" || echo "no session: $SESSION"
  if [[ "$WITH_MANAGER" -eq 1 ]]; then
    tmux kill-session -t manager 2>/dev/null && echo "killed session: manager" || echo "no session: manager"
  fi
  exit 0
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Error: session '$SESSION' already exists. Tear it down first:" >&2
  echo "  bash $HERE/launch-grid.sh --kill" >&2
  exit 1
fi

# Pane indices in config order; count drives the split layout.
# Stock macOS ships bash 3.2, which has no `mapfile`/`readarray`; read portably.
PANES=()
while IFS= read -r _pane; do PANES+=("$_pane"); done \
  < <(ts_jq -r '.personas | sort_by(.pane) | .[].pane' "$(ts_personas_path)")
n="${#PANES[@]}"
[[ "$n" -gt 0 ]] || { echo "Error: no personas in $(ts_personas_path)" >&2; exit 1; }

# Warn early if the grid fans out a lot of interactive agy/Antigravity panes —
# Gemini quota drains fast on the individual plan (#191).
agy_n=0
for p in "${PANES[@]}"; do
  [[ "$(ts_persona_field "$p" runtime)" == "agy" ]] && agy_n=$((agy_n + 1))
done
ts_agy_grid_warn "$agy_n"

# --- optional manager session ------------------------------------------------

if [[ "$WITH_MANAGER" -eq 1 ]]; then
  if tmux has-session -t manager 2>/dev/null; then
    echo "manager session already exists — leaving it."
  else
    tmux new-session -d -s manager -n manager
    echo "created session: manager (attach with: tmux attach -t manager)"
  fi
fi

# --- sprint session ----------------------------------------------------------

tmux new-session -d -s "$SESSION" -n "$WINDOW"
# remain-on-exit so a crashed agent stays visible instead of vanishing.
tmux set-option -t "${SESSION}:${WINDOW}" remain-on-exit on

# Create n panes total. Split into two rows (top half / bottom half), then tile
# so dispatch's sprint:WINDOW.<pane> indices line up left-to-right, top-to-bottom.
for ((k = 1; k < n; k++)); do
  tmux split-window -t "${SESSION}:${WINDOW}" >/dev/null
  tmux select-layout -t "${SESSION}:${WINDOW}" tiled >/dev/null
done
tmux select-layout -t "${SESSION}:${WINDOW}" tiled >/dev/null

echo "created session: $SESSION ($n panes)"

# --- title + start each persona ----------------------------------------------

for pane in "${PANES[@]}"; do
  name="$(ts_persona_field "$pane" name)"
  runtime="$(ts_persona_field "$pane" runtime)"
  launch="$(ts_persona_field "$pane" launch)"; launch="${launch:-$runtime}"
  target="$(ts_target "$pane")"

  # Best-effort pane title (shows in the border with pane-border-status on).
  tmux select-pane -t "$target" -T "$name/$runtime" 2>/dev/null || true

  if [[ "$START" -eq 1 ]]; then
    tmux send-keys -t "$target" -l "$launch"; tmux send-keys -t "$target" C-m
    echo "  pane $pane $name -> $launch"
    # codex panes share a backend and agy/Antigravity shares Gemini quota;
    # stagger their cold starts by the per-runtime rate limit. claude panes
    # are independent processes, so a flat 1s is enough.
    case "$runtime" in
      codex|agy) sleep "$(ts_rate_limit "$runtime")" ;;
      *)         sleep 1 ;;
    esac
  else
    echo "  pane $pane $name (not started; --no-start)"
  fi
done

cat <<EOF

Grid is up. Next steps:
  tmux attach -t $SESSION          # watch the personas (terminal #2)
$( [[ "$WITH_MANAGER" -eq 1 ]] && echo "  tmux attach -t manager           # run the manager here (terminal #1)" )
  bash $HERE/preflight.sh          # confirm panes are live before dispatching
EOF
