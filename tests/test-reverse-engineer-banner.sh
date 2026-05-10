#!/usr/bin/env bash
# tests/test-reverse-engineer-banner.sh
#
# Smoke test for scripts/check-reverse-engineer-banner.sh. Confirms the
# validator passes on the pass/ fixtures and fails on the fail/ fixtures.

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

validator="scripts/check-reverse-engineer-banner.sh"
pass_dir="tests/fixtures/reverse-engineer-banner/pass"
fail_dir="tests/fixtures/reverse-engineer-banner/fail"

errors=0

echo "==> validator must exit 0 on pass fixtures"
if bash "$validator" "$pass_dir"/*.md; then
    echo "    PASS"
else
    echo "    FAIL: validator rejected a pass fixture" >&2
    errors=$((errors + 1))
fi

echo ""
echo "==> validator must exit 1 on fail fixtures"
if bash "$validator" "$fail_dir"/*.md; then
    echo "    FAIL: validator accepted a fail fixture" >&2
    errors=$((errors + 1))
else
    echo "    PASS"
fi

echo ""
if [[ "$errors" -gt 0 ]]; then
    echo "test-reverse-engineer-banner.sh: $errors failure(s)" >&2
    exit 1
fi
echo "test-reverse-engineer-banner.sh: all checks passed"
