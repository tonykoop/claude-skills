#!/usr/bin/env bash
# tests/test-tmux-preflight.sh
#
# Unit test for sprint-supervisor/scripts/tmux-preflight.sh version parsing,
# comparison, and the soft-gate exit codes (#163). Sources the script so the
# functions can be called directly, and uses TMUX_VERSION_OVERRIDE / a missing
# binary to exercise every branch without a real tmux.

set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
preflight="$repo_root/plugins/coding/skills/sprint-supervisor/scripts/tmux-preflight.sh"

errors=0
check() { # check <description> <expected> <actual>
  if [ "$2" = "$3" ]; then
    echo "    PASS: $1"
  else
    echo "    FAIL: $1 (expected '$2', got '$3')" >&2
    errors=$((errors + 1))
  fi
}

# shellcheck source=/dev/null
. "$preflight"

echo "==> parse_tmux_version normalizes assorted -V strings"
check "tmux 3.4"      "3.4" "$(parse_tmux_version 'tmux 3.4')"
check "tmux 3.2a"     "3.2" "$(parse_tmux_version 'tmux 3.2a')"
check "tmux next-3.5" "3.5" "$(parse_tmux_version 'tmux next-3.5')"
check "tmux 3 only"   "3.0" "$(parse_tmux_version 'tmux 3')"

echo ""
echo "==> version_ge compares major then minor"
version_ge 3.4 3.2 && r=ge || r=lt; check "3.4 >= 3.2" "ge" "$r"
version_ge 3.2 3.2 && r=ge || r=lt; check "3.2 >= 3.2" "ge" "$r"
version_ge 3.1 3.2 && r=ge || r=lt; check "3.1 <  3.2" "lt" "$r"
version_ge 2.9 3.2 && r=ge || r=lt; check "2.9 <  3.2" "lt" "$r"
version_ge 4.0 3.9 && r=ge || r=lt; check "4.0 >= 3.9" "ge" "$r"

echo ""
echo "==> run_preflight returns 0 for a supported tmux"
TMUX_VERSION_OVERRIDE="tmux 3.4" run_preflight --quiet; check "tmux 3.4 -> 0" "0" "$?"

echo ""
echo "==> run_preflight returns 4 (soft gate) for an old tmux"
TMUX_VERSION_OVERRIDE="tmux 2.9a" run_preflight --quiet >/dev/null 2>&1; check "tmux 2.9 -> 4" "4" "$?"

echo ""
echo "==> run_preflight returns 3 when tmux is absent"
# Point TMUX_BIN at a definitely-missing binary and clear the override.
( unset TMUX_VERSION_OVERRIDE; TMUX_BIN="tmux-does-not-exist-$$" run_preflight --quiet >/dev/null 2>&1 )
check "missing tmux -> 3" "3" "$?"

echo ""
if [ "$errors" -gt 0 ]; then
  echo "test-tmux-preflight.sh: $errors failure(s)" >&2
  exit 1
fi
echo "test-tmux-preflight.sh: all checks passed"
