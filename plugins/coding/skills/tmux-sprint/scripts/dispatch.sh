#!/usr/bin/env bash
# tmux-sprint dispatch — transactional, assignment-file-only fan-out.
#
#   dispatch.sh --round 53 --manager claude-opus-4-6 \
#     --to alice --assignment <ws>/docs/plans/2026-04-11-alice-round53.md \
#     --to bob   --assignment <ws>/docs/plans/2026-04-11-bob-round53.md
#
# Every target needs its own --assignment <md-path>. There is no inline --items
# option — the markdown file IS the contract. Each file must live under a
# docs/plans/ directory and contain the read-only preamble block from
# assets/assignment-preamble.txt verbatim.
#
# Flow per round:
#   1. preflight every target; abort on BUSY/DEAD unless --force
#   2. validate each assignment file (path + preamble)
#   3. cancel copy-mode, send text, send C-m (never the literal "Enter")
#   4. rate-limit by runtime (claude parallel-ish @2s, codex sequential @10s)
#   5. verify submission with a three-tier retry; mark SILENT_FAIL if all fail
#   6. persist the round record under ~/.claude/projects/<slug>/tmux-v2/rounds/

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"

ROUND=""
MANAGER="unknown"
FORCE=0
declare -a TO=() ASSIGN=()

usage() {
  sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --round)      ROUND="$2"; shift 2 ;;
    --manager)    MANAGER="$2"; shift 2 ;;
    --to)         TO+=("$2"); shift 2 ;;
    --assignment) ASSIGN+=("$2"); shift 2 ;;
    --project)    export TMUX_SPRINT_PROJECT="$2"; shift 2 ;;
    --force)      FORCE=1; shift ;;
    -h|--help)    usage; exit 0 ;;
    *) echo "Error: unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

ts_require tmux
ts_require jq

[[ -n "$ROUND" ]]            || { echo "Error: --round is required" >&2; exit 2; }
[[ ${#TO[@]} -gt 0 ]]        || { echo "Error: at least one --to is required" >&2; exit 2; }
[[ ${#TO[@]} -eq ${#ASSIGN[@]} ]] || {
  echo "Error: every --to needs a matching --assignment (got ${#TO[@]} to / ${#ASSIGN[@]} assignment)" >&2
  exit 2
}

PREAMBLE="$(cat "$ASSETS_DIR/assignment-preamble.txt")"

# --- resolve + validate every target up front (fail closed before sending) ---

declare -a PANE=() NAME=() RUNTIME=()
abort=0

for i in "${!TO[@]}"; do
  who="${TO[$i]}"; file="${ASSIGN[$i]}"
  pane="$(ts_pane_for_name "$who")"
  if [[ -z "$pane" ]]; then
    echo "✖ unknown persona: $who (not in personas.json)" >&2; abort=1; continue
  fi
  PANE[$i]="$pane"
  NAME[$i]="$who"
  RUNTIME[$i]="$(ts_persona_field "$pane" runtime)"

  # assignment file: exists, under a docs/plans/ dir, carries the preamble.
  if [[ ! -f "$file" ]]; then
    echo "✖ $who: assignment file not found: $file" >&2; abort=1; continue
  fi
  if [[ "$file" != *"/docs/plans/"* ]]; then
    echo "✖ $who: assignment must live under a docs/plans/ directory: $file" >&2; abort=1; continue
  fi
  if ! grep -qF "$PREAMBLE" "$file"; then
    echo "✖ $who: assignment is missing the read-only preamble block" >&2
    echo "    (copy it from $ASSETS_DIR/assignment-preamble.txt)" >&2
    abort=1; continue
  fi
done

[[ "$abort" -eq 0 ]] || { echo "Aborting: fix the issues above and rerun." >&2; exit 1; }

# --- preflight gate ----------------------------------------------------------

panes_csv="$(IFS=,; echo "${PANE[*]}")"
pf="$(bash "$HERE/preflight.sh" --panes "$panes_csv" --json)"

blocked="$(jq -r '.[] | select(.verdict != "OK") | "  " + .name + " (pane " + (.pane|tostring) + "): " + .state' <<<"$pf")"
if [[ -n "$blocked" ]]; then
  echo "Preflight found non-OK targets:" >&2
  echo "$blocked" >&2
  if [[ "$FORCE" -ne 1 ]]; then
    echo "Refusing to dispatch. Rerun with --force to override, or restart the panes." >&2
    exit 1
  fi
  echo "--force set: dispatching anyway." >&2
fi

# --- send + verify -----------------------------------------------------------

ts_send_one() { # ts_send_one <pane> <text>
  local pane="$1" text="$2"
  ts_cancel_copy_mode "$pane"
  tmux send-keys -t "$(ts_target "$pane")" -l "$text"
  tmux send-keys -t "$(ts_target "$pane")" C-m
}

# Did the prompt land? prompt text echoed OR a working/tool indicator appeared.
ts_landed() { # ts_landed <pane> <needle>
  local cap; cap="$(ts_capture "$1")"
  printf '%s' "$cap" | grep -qF "$2" && return 0
  printf '%s' "$cap" | grep -qiE '(•|◦) (Working|Booting)|Cooked|Leavening|Galloping|Processing|esc to interrupt|tool' && return 0
  return 1
}

records="[]"
ts_dt() { date -u +%FT%TZ 2>/dev/null || echo unknown; }

for i in "${!TO[@]}"; do
  pane="${PANE[$i]}"; who="${NAME[$i]}"; rt="${RUNTIME[$i]}"; file="${ASSIGN[$i]}"
  oneliner="Round ${ROUND}: read ${file} and execute. This file is a contract — do not edit it."

  status="SILENT_FAIL"; tier=0

  # tier 1: send + verify
  ts_send_one "$pane" "$oneliner"; tier=1
  sleep 3
  if ts_landed "$pane" "$oneliner"; then
    status="OK"
  else
    # tier 2: nudge with a fresh C-m
    tmux send-keys -t "$(ts_target "$pane")" C-m; tier=2
    sleep 3
    if ts_landed "$pane" "$oneliner"; then
      status="OK"
    else
      # tier 3: full re-send (catches the post-/clear absorb race)
      ts_send_one "$pane" "$oneliner"; tier=3
      sleep 6
      ts_landed "$pane" "$oneliner" && status="OK"
    fi
  fi

  if [[ "$status" == "OK" ]]; then
    echo "✓ $who (pane $pane, $rt) dispatched [tier $tier]"
  else
    echo "⚠️  $who (pane $pane, $rt) SILENT_FAIL after 3 tiers — verify by hand" >&2
  fi

  records="$(jq -c \
    --arg who "$who" --argjson pane "$pane" --arg rt "$rt" --arg file "$file" \
    --arg status "$status" --argjson tier "$tier" --arg at "$(ts_dt)" \
    '. += [{persona:$who,pane:$pane,runtime:$rt,assignment:$file,status:$status,tier:$tier,sent_at:$at}]' \
    <<<"$records")"

  # rate-limit before the next target, by THIS pane's runtime
  if [[ $((i + 1)) -lt ${#TO[@]} ]]; then
    sleep "$(ts_rate_limit "$rt")"
  fi
done

# --- persist -----------------------------------------------------------------

state_dir="$(ts_state_dir)"
mkdir -p "$state_dir/rounds" "$state_dir/dispatches"
round_file="$state_dir/rounds/round-${ROUND}.json"
ts_epoch="$(date +%s 2>/dev/null || echo 0)"
txn_file="$state_dir/dispatches/${ts_epoch}.json"

round_json="$(jq -n \
  --argjson round "$(printf '%s' "$ROUND" | jq -R 'tonumber? // .')" \
  --arg manager "$MANAGER" --arg at "$(ts_dt)" --argjson disp "$records" \
  '{round:$round, manager:$manager, dispatched_at:$at, dispatches:$disp}')"

printf '%s\n' "$round_json" | jq . > "$round_file"
printf '%s\n' "$round_json" | jq . > "$txn_file"

fails="$(jq '[.dispatches[] | select(.status != "OK")] | length' <<<"$round_json")"
echo "Round ${ROUND} record -> $round_file"
[[ "$fails" -eq 0 ]] || echo "⚠️  $fails dispatch(es) marked SILENT_FAIL — see ⚠️ lines above." >&2
exit 0
