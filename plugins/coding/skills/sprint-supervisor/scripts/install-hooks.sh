#!/usr/bin/env bash
# Install the sprint-supervisor Claude hooks into a settings.local.json file.
# Existing settings and hooks are preserved; repeated installs are idempotent.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SETTINGS="${CLAUDE_PROJECT_DIR:-$PWD}/.claude/settings.local.json"
SUPERVISOR_PANE=""
SCOPE="default"
DRY=0

usage() {
  echo "usage: $0 [--settings PATH] --supervisor-pane SESSION:WINDOW.PANE [--scope NAME] [--dry-run]"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --settings) shift; SETTINGS="${1:-}" ;;
    --supervisor-pane) shift; SUPERVISOR_PANE="${1:-}" ;;
    --scope) shift; SCOPE="${1:-default}" ;;
    --dry-run) DRY=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

command -v jq >/dev/null 2>&1 || { echo "install-hooks: jq is required" >&2; exit 1; }
[ -n "$SETTINGS" ] || { echo "install-hooks: --settings path is empty" >&2; exit 2; }
[ -n "$SUPERVISOR_PANE" ] || { echo "install-hooks: --supervisor-pane is required" >&2; exit 2; }

mkdir -p "$(dirname "$SETTINGS")"
source_json="{}"
[ -f "$SETTINGS" ] && source_json="$(cat "$SETTINGS")"
printf '%s' "$source_json" | jq empty

permission_cmd="bash $HERE/permission-gate.sh"
event_cmd="bash $HERE/supervisor-event.sh hook"

updated="$(
  printf '%s' "$source_json" | jq \
    --arg pane "$SUPERVISOR_PANE" \
    --arg scope "$SCOPE" \
    --arg permission_cmd "$permission_cmd" \
    --arg event_cmd "$event_cmd" '
      def append_unique($item):
        . as $a | if any($a[]?; . == $item) then $a else $a + [$item] end;
      .env = (.env // {}) |
      .env.SPRINT_SUPERVISOR_PANE = $pane |
      .env.SPRINT_SUPERVISOR_SCOPE = $scope |
      .hooks = (.hooks // {}) |
      .hooks.PermissionRequest = (
        (.hooks.PermissionRequest // []) |
        append_unique({
          matcher:"Bash",
          hooks:[{type:"command",command:$permission_cmd,timeout:10}]
        })
      ) |
      .hooks.Notification = (
        (.hooks.Notification // []) |
        append_unique({
          matcher:"permission_prompt",
          hooks:[{type:"command",command:$event_cmd,timeout:10}]
        }) |
        append_unique({
          matcher:"idle_prompt",
          hooks:[{type:"command",command:$event_cmd,timeout:10}]
        })
      ) |
      .hooks.Stop = (
        (.hooks.Stop // []) |
        append_unique({
          matcher:"",
          hooks:[{type:"command",command:$event_cmd,timeout:10}]
        })
      )
    '
)"

if [ "$DRY" -eq 1 ]; then
  printf '%s\n' "$updated"
  exit 0
fi

tmp="${SETTINGS}.tmp.$$"
printf '%s\n' "$updated" > "$tmp"
if [ -f "$SETTINGS" ]; then
  cp "$SETTINGS" "${SETTINGS}.sprint-supervisor.bak"
fi
mv "$tmp" "$SETTINGS"
echo "installed sprint-supervisor hooks in $SETTINGS"
echo "supervisor pane: $SUPERVISOR_PANE; scope: $SCOPE"
