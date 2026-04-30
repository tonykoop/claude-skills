#!/usr/bin/env bash
# PreToolUse hook — claim an advisory lock on the active sprint doc before
# Edit/Write/MultiEdit touches it. Prevents concurrent agent updates from
# overwriting each other's changes.
#
# Lock scope: any file under <workspace>/docs/plans/ whose name
# matches *[Ss]print*.md (case-insensitive). Other files pass through.
#
# Exit codes:
#   0 = allow the tool call to proceed (locked or no lock needed)
#   2 = block the tool call (another agent holds the lock)
#
# Claude Code hook protocol: tool input JSON is sent on stdin; stderr is
# surfaced to the agent when exit code is non-zero.

set -euo pipefail

LOCK_DIR="${SPRINT_DOC_LOCK_DIR:-/tmp/sprint-doc-locks}"
mkdir -p "$LOCK_DIR"

# Read tool input JSON from stdin (non-blocking fallback if none)
tool_input_json="$(cat || true)"

# Extract tool_name and file_path using python for robust JSON parsing
read -r tool_name file_path <<EOF
$(python3 - "$tool_input_json" <<'PY'
import json, sys
raw = sys.argv[1] if len(sys.argv) > 1 else ""
try:
    data = json.loads(raw) if raw else {}
except Exception:
    data = {}

tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input", {}) or {}
# Edit/Write/MultiEdit all carry file_path
file_path = tool_input.get("file_path", "") or ""
print(f"{tool_name} {file_path}")
PY
)
EOF

# If we couldn't extract a file path, let the tool proceed
if [ -z "$file_path" ]; then
  exit 0
fi

# Only lock when the target is a sprint doc under any docs/plans/ directory
if [[ ! "$file_path" =~ /docs/plans/.*[Ss]print.*\.md$ ]]; then
  exit 0
fi

# Compute a per-file holder path
basename=$(basename "$file_path")
holder_file="$LOCK_DIR/${basename}.holder"

# Check if a holder exists
if [ -f "$holder_file" ]; then
  holder_pid=$(sed -n 's/.*pid=\([0-9]*\).*/\1/p' "$holder_file" 2>/dev/null || true)
  holder_ts=$(sed -n 's/.*ts=\([^ ]*\).*/\1/p' "$holder_file" 2>/dev/null || true)
  holder_tool=$(sed -n 's/.*tool=\([^ ]*\).*/\1/p' "$holder_file" 2>/dev/null || true)

  if [ -n "$holder_pid" ] && [ -d "/proc/$holder_pid" ]; then
    # Live holder — block the tool call and explain
    cat >&2 <<ERR
[sprint-doc-lock] $file_path is locked by PID $holder_pid
                  (tool=$holder_tool ts=$holder_ts)
                  Another agent is currently editing this sprint doc.
                  Retry in a few seconds, or run:
                    cat $holder_file
                  to inspect the current holder.
ERR
    exit 2
  else
    # Stale holder (process died without releasing) — reclaim
    rm -f "$holder_file"
  fi
fi

# Claim the lock
cat > "$holder_file" <<HOLDER
pid=$PPID ts=$(date -u +%Y-%m-%dT%H:%M:%SZ) file=$file_path tool=$tool_name
HOLDER

exit 0
