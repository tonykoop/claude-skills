#!/usr/bin/env bash
# Focused smoke tests for scripts/plan-label-batches.sh.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
PLANNER="$ROOT/scripts/plan-label-batches.sh"

assert_contains() {
  local haystack="$1"
  local needle="$2"
  if [[ "$haystack" != *"$needle"* ]]; then
    printf 'Expected output to contain: %s\n' "$needle" >&2
    printf 'Actual output:\n%s\n' "$haystack" >&2
    exit 1
  fi
}

markdown_output="$(
  printf '%s\n' '{"number":47,"title":"Label-aware","url":"https://github.com/tonykoop/tmux-sprint/issues/47","labels":[{"name":"skill:tmux-sprint"},{"name":"artifact:validation-loop"},{"name":"model:gpt-5.5"},{"name":"batch:needs-review"}]}' \
    | bash "$PLANNER"
)"

assert_contains "$markdown_output" "skill:tmux-sprint"
assert_contains "$markdown_output" "| needs-review | gpt-5.5 |"
assert_contains "$markdown_output" "artifact validation-loop"
assert_contains "$markdown_output" "needs review before merge"

default_output="$(
  printf '%s\n' '[{"number":1,"title":"Plain issue","labels":[]}]' \
    | bash "$PLANNER" --default-model gpt-5.4-mini
)"

assert_contains "$default_output" "| (none) | general | gpt-5.4-mini | no routing labels |"

conflict_output="$(
  printf '%s\n' '{"number":48,"title":"Conflicting models","labels":["model:gpt-5.5","model:gpt-5.4-mini","skill:tmux-sprint"]}' \
    | bash "$PLANNER" --format json
)"

printf '%s\n' "$conflict_output" | jq -e '
  length == 1
  and .[0].suggested_model == "manager-review"
  and (.[0].batch_notes | contains("model conflict requires manager review"))
' >/dev/null

echo "plan-label-batches smoke tests passed"
