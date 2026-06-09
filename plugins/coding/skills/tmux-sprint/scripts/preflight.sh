#!/usr/bin/env bash
# tmux-sprint preflight — structured pane probe.
#
#   preflight.sh                  # probe all configured panes
#   preflight.sh --pane 3         # probe one pane
#   preflight.sh --panes 0,1,2    # probe a subset
#   preflight.sh --json           # JSON output for piping (e.g. into dispatch)
#
# Captures each pane, classifies its state, and prints a one-line-per-pane
# table (or JSON). Any state other than IDLE/BLANK yields a BUSY or DEAD
# verdict. Exit code is 0 even when panes are BUSY/DEAD — callers inspect the
# verdict column / JSON, they do not rely on exit status for liveness.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"

PANES=""
AS_JSON=0

usage() {
  sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pane)    PANES="$2"; shift 2 ;;
    --panes)   PANES="${2//,/ }"; shift 2 ;;
    --project) export TMUX_SPRINT_PROJECT="$2"; shift 2 ;;
    --json)    AS_JSON=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Error: unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

ts_require tmux
ts_require jq

[[ -n "$PANES" ]] || PANES="$(ts_all_panes)"

mkdir -p "$(ts_state_dir)/logs"
LOG="$(ts_state_dir)/logs/preflight.log"

records="[]"

for pane in $PANES; do
  name="$(ts_persona_field "$pane" name)";       name="${name:-pane$pane}"
  runtime="$(ts_persona_field "$pane" runtime)"; runtime="${runtime:-unknown}"
  model="$(ts_persona_field "$pane" model)";     model="${model:-$runtime}"
  worktree="$(ts_persona_field "$pane" worktrees | head -1)"

  capture="$(ts_capture "$pane")"
  state="$(ts_classify "$capture")"
  verdict="$(ts_verdict "$state")"
  ctx="$(ts_metric_ctx "$capture")"
  c5h="$(ts_metric_codex5h "$capture")"
  cwk="$(ts_metric_codexwk "$capture")"

  {
    printf '=== pane %s %s %s @ %s ===\n' "$pane" "$name" "$state" "$(date -u +%FT%TZ 2>/dev/null || echo unknown)"
    printf '%s\n' "$capture"
  } >> "$LOG"

  records="$(jq -c \
    --argjson pane "$pane" --arg name "$name" --arg runtime "$runtime" \
    --arg model "$model" --arg state "$state" --arg verdict "$verdict" \
    --arg ctx "$ctx" --arg c5h "$c5h" --arg cwk "$cwk" --arg wt "${worktree:-}" \
    '. += [{pane:$pane,name:$name,runtime:$runtime,model:$model,state:$state,
            verdict:$verdict,ctx:$ctx,fivehour:$c5h,weekly:$cwk,worktree:$wt}]' \
    <<<"$records")"
done

if [[ "$AS_JSON" -eq 1 ]]; then
  printf '%s\n' "$records" | jq .
  exit 0
fi

# Human table, padded to roughly the SKILL.md example.
printf '%s\n' "$records" | jq -r '.[] |
  ( if .ctx != "" then "ctx=" + .ctx
    elif .fivehour != "" then "5h=" + .fivehour + (if .weekly != "" then "  weekly=" + .weekly else "" end)
    else "" end ) as $meter |
  [ "pane " + (.pane|tostring),
    (.name      | (. + "      ")[0:6]),
    (.model     | (. + "                  ")[0:18]),
    (.state     | (. + "                    ")[0:20]),
    ($meter     | (. + "                          ")[0:26]),
    (if .worktree != "" then "worktree=" + .worktree else "" end | (. + "                          ")[0:26]),
    "[" + .verdict + "]"
  ] | join(" ")'
