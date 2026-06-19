#!/usr/bin/env bash
# tmux-preflight.sh — verify the tmux build can run the supervisor's scripts,
# and gate gracefully instead of failing loud on an old or missing tmux. #163.
#
# The supervisor's scripts (grid-scan.sh, sprint-watchdog.sh) rely on
# `list-panes -F`, `capture-pane -p -S -N`, and `has-session`. Those flags are
# stable on tmux 3.2+, but macOS ships an older tmux by default and a missing
# tmux otherwise produces confusing empty output. This preflight turns that into
# one clear, actionable message.
#
# Usage:
#   tmux-preflight.sh            # check; print guidance on a problem
#   tmux-preflight.sh --quiet    # same, but only emit on a problem
#
# Exit status:
#   0  tmux present and >= MIN_TMUX_VERSION — safe to run the supervisor
#   3  tmux not found on PATH
#   4  tmux present but older than MIN_TMUX_VERSION (features may not work)
#
# Testable: source this file to get parse_tmux_version / version_ge / run_preflight
# without executing main. Override the probed binary/version with TMUX_BIN and
# TMUX_VERSION_OVERRIDE (used by the test suite).

MIN_TMUX_VERSION="${MIN_TMUX_VERSION:-3.2}"

# Echo the raw `tmux -V` string, or empty if tmux is unavailable. Honors
# TMUX_VERSION_OVERRIDE (test seam) and TMUX_BIN (alternate binary).
tmux_version_string() {
  if [ -n "${TMUX_VERSION_OVERRIDE:-}" ]; then
    printf '%s\n' "$TMUX_VERSION_OVERRIDE"
    return 0
  fi
  local bin="${TMUX_BIN:-tmux}"
  command -v "$bin" >/dev/null 2>&1 || return 1
  "$bin" -V 2>/dev/null
}

# Normalize a `tmux -V` string to a comparable MAJOR.MINOR number.
#   "tmux 3.4"      -> "3.4"
#   "tmux 3.2a"     -> "3.2"
#   "tmux next-3.5" -> "3.5"
#   "tmux 3"        -> "3.0"
parse_tmux_version() {
  local raw="$1" ver
  ver=$(printf '%s\n' "$raw" | grep -oE '[0-9]+\.[0-9]+' | head -1)
  if [ -z "$ver" ]; then
    ver=$(printf '%s\n' "$raw" | grep -oE '[0-9]+' | head -1)
    [ -n "$ver" ] && ver="${ver}.0"
  fi
  printf '%s\n' "$ver"
}

# version_ge A B  -> exit 0 if A >= B (numeric MAJOR then MINOR), else exit 1.
version_ge() {
  local a="$1" b="$2"
  local a_major="${a%%.*}" a_minor="${a#*.}" b_major="${b%%.*}" b_minor="${b#*.}"
  [ "$a_minor" = "$a" ] && a_minor=0
  [ "$b_minor" = "$b" ] && b_minor=0
  # Strip any stray non-digits (defensive).
  a_major=$(printf '%s' "$a_major" | grep -oE '[0-9]+' | head -1); a_major="${a_major:-0}"
  a_minor=$(printf '%s' "$a_minor" | grep -oE '[0-9]+' | head -1); a_minor="${a_minor:-0}"
  b_major=$(printf '%s' "$b_major" | grep -oE '[0-9]+' | head -1); b_major="${b_major:-0}"
  b_minor=$(printf '%s' "$b_minor" | grep -oE '[0-9]+' | head -1); b_minor="${b_minor:-0}"
  if [ "$a_major" -gt "$b_major" ]; then return 0; fi
  if [ "$a_major" -lt "$b_major" ]; then return 1; fi
  [ "$a_minor" -ge "$b_minor" ]
}

# run_preflight [--quiet] -> status per the header. Prints guidance to stderr.
run_preflight() {
  local quiet=0
  [ "${1:-}" = "--quiet" ] && quiet=1

  local raw
  if ! raw=$(tmux_version_string) || [ -z "$raw" ]; then
    echo "sprint-supervisor: tmux not found on PATH." >&2
    echo "  Install tmux >= ${MIN_TMUX_VERSION} (Linux: apt/yum; macOS: brew install tmux; Windows: use WSL2)." >&2
    echo "  The supervisor scans real tmux panes — screen and Terminal.app tabs are not supported." >&2
    return 3
  fi

  local ver
  ver=$(parse_tmux_version "$raw")
  if [ -z "$ver" ]; then
    [ "$quiet" -eq 1 ] || echo "sprint-supervisor: could not parse tmux version from '$raw'; proceeding (assuming OK)." >&2
    return 0
  fi

  if version_ge "$ver" "$MIN_TMUX_VERSION"; then
    [ "$quiet" -eq 1 ] || echo "sprint-supervisor: tmux $ver OK (>= ${MIN_TMUX_VERSION})."
    return 0
  fi

  echo "sprint-supervisor: tmux $ver is older than the supported ${MIN_TMUX_VERSION}." >&2
  echo "  Pane scanning (capture-pane -S -N, list-panes -F) may behave differently." >&2
  echo "  Upgrade (macOS: 'brew install tmux') or expect degraded scanning; the supervisor will" >&2
  echo "  continue but may miss prompts. This is a soft gate, not a hard failure." >&2
  return 4
}

# Run main only when executed directly, not when sourced (so tests can import).
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  run_preflight "${1:-}"
  exit $?
fi
