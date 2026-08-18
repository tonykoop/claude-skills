#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
installer="$repo_root/plugins/coding/skills/sprint-supervisor/scripts/install-hooks.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
settings="$tmp/.claude/settings.local.json"
mkdir -p "$(dirname "$settings")"

cat > "$settings" <<'JSON'
{
  "permissions": {"allow": ["Read"]},
  "env": {"SPRINT_SUPERVISED_PANES": "stale:0.0"},
  "hooks": {
    "Stop": [
      {"matcher":"","hooks":[{"type":"command","command":"echo existing"}]}
    ]
  }
}
JSON

"$installer" --settings "$settings" --supervisor-pane 1:0.0 --scope overnight \
  --supervised-panes "0:0.1 0:0.2"
"$installer" --settings "$settings" --supervisor-pane 1:0.0 --scope overnight \
  --supervised-panes "0:0.1 0:0.2"

jq -e '
  .permissions.allow == ["Read"] and
  .env.SPRINT_SUPERVISOR_PANE == "1:0.0" and
  .env.SPRINT_SUPERVISOR_SCOPE == "overnight" and
  .env.SPRINT_SUPERVISED_PANES == "0:0.1 0:0.2" and
  ([.hooks.PermissionRequest[] | select(.matcher=="Bash")] | length) == 1 and
  ([.hooks.Notification[] | select(.matcher=="permission_prompt")] | length) == 1 and
  ([.hooks.Notification[] | select(.matcher=="idle_prompt")] | length) == 1 and
  ([.hooks.Stop[] | select(.hooks[0].command=="echo existing")] | length) == 1 and
  ([.hooks.Stop[] | select(.hooks[0].command|contains("supervisor-event.sh hook"))] | length) == 1 and
  ([.hooks.Stop[] | select(.hooks[0].command|contains("stop-gate.sh"))] | length) == 1
' "$settings" >/dev/null

# Omitting the option restores the documented lockfile fallback instead of
# preserving a stale explicit pane list from an earlier installation.
"$installer" --settings "$settings" --supervisor-pane 1:0.0 --scope overnight
jq -e '
  .env.SPRINT_SUPERVISED_PANES == "" and
  ([.hooks.Stop[] | select(.hooks[0].command|contains("stop-gate.sh"))] | length) == 1
' "$settings" >/dev/null

[ -f "$settings.sprint-supervisor.bak" ] \
  || { echo "FAIL: backup not written" >&2; exit 1; }

echo "install-hooks tests passed"
