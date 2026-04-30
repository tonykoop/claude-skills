#!/usr/bin/env bash
# PostToolUse hook — release the advisory lock on the sprint doc after
# Edit/Write/MultiEdit completes (whether success or failure).
#
# Paired with sprint-doc-lock.sh. Always exits 0 — unlock is best-effort and
# must not block the tool call completion.

set -u

LOCK_DIR="${SPRINT_DOC_LOCK_DIR:-/tmp/sprint-doc-locks}"
[ -d "$LOCK_DIR" ] || exit 0

tool_input_json="$(cat || true)"

file_path="$(python3 - "$tool_input_json" <<'PY'
import json, sys
raw = sys.argv[1] if len(sys.argv) > 1 else ""
try:
    data = json.loads(raw) if raw else {}
except Exception:
    data = {}
tool_input = data.get("tool_input", {}) or {}
print(tool_input.get("file_path", "") or "")
PY
)"

[ -z "$file_path" ] && exit 0

# Only unlock if this was a sprint doc
if [[ ! "$file_path" =~ /docs/plans/.*[Ss]print.*\.md$ ]]; then
  exit 0
fi

basename=$(basename "$file_path")
holder_file="$LOCK_DIR/${basename}.holder"

# Only remove the holder if WE own it (same PPID). This prevents unrelated
# agents from removing each other's locks if the PreToolUse/PostToolUse
# pairing drifts.
if [ -f "$holder_file" ]; then
  holder_pid=$(sed -n 's/.*pid=\([0-9]*\).*/\1/p' "$holder_file" 2>/dev/null || true)
  if [ "$holder_pid" = "$PPID" ]; then
    rm -f "$holder_file"
  fi
fi

exit 0
