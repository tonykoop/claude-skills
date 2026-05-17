#!/usr/bin/env bash
# check-reverse-engineer-banner.sh
#
# Validate that a reverse-engineer analysis artifact follows the
# image-access-mode rules from skills/reverse-engineer/SKILL.md (v1.1.0+):
#
#   1. Every artifact must contain an `intake:` YAML block with an
#      `image_access_mode:` field.
#   2. If image_access_mode != direct, the standardized degraded-mode
#      banner must appear in the artifact (the leading "> **Image-access
#      mode: <mode>.**" line).
#
# Usage:
#   scripts/check-reverse-engineer-banner.sh <file> [<file>...]
#
# Exit codes:
#   0  all files pass
#   1  one or more files fail validation
#   2  usage error / unreadable file

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "usage: $0 <file> [<file>...]" >&2
    exit 2
fi

DEGRADED_MODES_RE='description-only|missing|partial|named-object|file-path'
fail_count=0

for f in "$@"; do
    if [[ ! -r "$f" ]]; then
        echo "ERROR: cannot read $f" >&2
        exit 2
    fi

    if ! grep -qE '^[[:space:]]*image_access_mode:[[:space:]]*' "$f"; then
        echo "FAIL $f: no \`image_access_mode:\` field in intake YAML"
        fail_count=$((fail_count + 1))
        continue
    fi

    mode=$(grep -E '^[[:space:]]*image_access_mode:[[:space:]]*' "$f" \
        | head -n1 \
        | sed -E 's/^[[:space:]]*image_access_mode:[[:space:]]*([A-Za-z-]+).*/\1/')

    if [[ "$mode" == "direct" ]]; then
        echo "OK   $f: direct mode, no banner required"
        continue
    fi

    if [[ ! "$mode" =~ ^(${DEGRADED_MODES_RE})$ ]]; then
        echo "FAIL $f: unknown image_access_mode '$mode'"
        fail_count=$((fail_count + 1))
        continue
    fi

    if grep -qE '^>[[:space:]]*\*\*Image-access mode:[[:space:]]*('"${DEGRADED_MODES_RE}"')\.' "$f"; then
        echo "OK   $f: degraded mode '$mode' with banner"
    else
        echo "FAIL $f: degraded mode '$mode' but no banner found"
        fail_count=$((fail_count + 1))
    fi
done

if [[ "$fail_count" -gt 0 ]]; then
    echo ""
    echo "$fail_count file(s) failed validation" >&2
    exit 1
fi
