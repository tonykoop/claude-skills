#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
watchdog="$repo_root/plugins/coding/skills/sprint-supervisor/scripts/sprint-watchdog.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

export SPRINT_SUPERVISOR_STATE_ROOT="$tmp/state"
export SPRINT_WATCHDOG_LOG="$tmp/watchdog.log"
export SPRINT_SUPERVISOR_EVENT_ROOT="$tmp/events"

# shellcheck source=/dev/null
. "$watchdog"

fail() { echo "FAIL: $*" >&2; exit 1; }
yesno() { if "$@"; then echo yes; else echo no; fi; }

[ "$(yesno is_busy '• Working (23s • esc to interrupt)')" = yes ] \
  || fail "codex working marker not detected"
[ "$(yesno is_busy '✻ Transmuting… (2m 36s · ↓ 8.9k tokens)')" = yes ] \
  || fail "Claude spinner not detected"
[ "$(yesno is_queued_unsent '› PROCEED with the reviewed plan.
gpt-5.6 · weekly 50%')" = yes ] || fail "composed PROCEED not detected"
[ "$(yesno is_queued_unsent '› Implement {feature}
gpt-5.6 · weekly 50%')" = no ] || fail "default suggestion misdetected as queued"
[ "$(yesno is_safe_readonly_prompt 'Would you like to run?
$ gh pr view 12 --json headRefOid
Press enter to confirm')" = yes ] || fail "safe read-only prompt not classified"
[ "$(yesno is_safe_readonly_prompt 'Would you like to run?
$ cd /tmp && gh pr view 12
Press enter to confirm')" = no ] || fail "compound command should not auto-approve"
[ "$(yesno is_safe_readonly_prompt 'Would you like to run?
$ gh pr view 12 | sh
Press enter to confirm')" = no ] || fail "piped command should not auto-approve"
[ "$(yesno is_refusal_prompt '$ git reset --hard HEAD')" = yes ] \
  || fail "refusal prompt not detected"

export SCOPE=test
[ "$(idle_strikes 0:0.1 0)" = 1 ] || fail "first idle strike"
[ "$(idle_strikes 0:0.1 0)" = 2 ] || fail "second idle strike"
[ "$(idle_strikes 0:0.1 1)" = 0 ] || fail "busy observation should reset strikes"

echo "sprint-watchdog tests passed"
