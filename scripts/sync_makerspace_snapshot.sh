#!/usr/bin/env bash
# Sync the portable skills/makerspace/ snapshot from the standalone
# tonykoop/makerspace repo. Idempotent; safe to re-run before every
# release cut.
#
# Usage:
#   scripts/sync_makerspace_snapshot.sh /path/to/standalone/makerspace
#
# After running, hand-edit skills/makerspace/SOURCE_COMMIT.md with the
# new standalone SHA (printed at the end) and any working-tree drift.

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <path-to-standalone-makerspace-repo>" >&2
  exit 2
fi

SRC="${1%/}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${REPO_ROOT}/skills/makerspace"

if [[ ! -d "$SRC" ]] || [[ ! -f "$SRC/SKILL.md" ]]; then
  echo "Error: $SRC does not look like a makerspace repo (missing SKILL.md)." >&2
  exit 2
fi

if [[ ! -d "$DEST" ]]; then
  echo "Error: $DEST does not exist." >&2
  exit 2
fi

# Whitelist of entries that ship in the portable snapshot. Anything
# outside this list (LICENSE, README.md, getting-started.md, catalog.sqlite,
# dream-log.md, etc.) lives only in the standalone repo and should not be
# copied into the skill package.
DIRS=(SKILL.md manifest.yaml agents references assets spaces scripts examples evals)

echo "Syncing from $SRC -> $DEST"

for entry in "${DIRS[@]}"; do
  src_path="$SRC/$entry"
  if [[ ! -e "$src_path" ]]; then
    echo "  skip $entry (not in source)"
    continue
  fi
  if [[ -d "$src_path" ]]; then
    rsync -a --delete \
      --exclude='__pycache__' \
      --exclude='*.pyc' \
      --exclude='workspace/' \
      "$src_path/" "$DEST/$entry/"
    echo "  dir  $entry"
  else
    rsync -a "$src_path" "$DEST/$entry"
    echo "  file $entry"
  fi
done

# Drop sqlite + journal if they were copied via evals or anywhere else.
find "$DEST" -name 'catalog.sqlite*' -delete
find "$DEST" -name 'dream-log.md' -delete

# Re-create the moved-out evals/workspace as an empty shim so SKILL.md
# pointers stay valid and the round-1-eval doc keeps its sibling layout.
mkdir -p "$DEST/evals/round-1-outputs"

SIZE=$(du -sh "$DEST" | cut -f1)
SHA=$(cd "$SRC" && git rev-parse HEAD 2>/dev/null || echo "unknown")
DIRTY=$(cd "$SRC" && git status --porcelain 2>/dev/null | wc -l)

cat <<EOF

Done.
  snapshot size:   $SIZE
  standalone SHA:  $SHA
  dirty files:     $DIRTY (in standalone working tree)

Now hand-edit skills/makerspace/SOURCE_COMMIT.md with that SHA and any
working-tree drift before committing.
EOF
