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

# Host-only annotations that exist in the snapshot but not in the standalone
# repo. They live alongside the synced material because they are about this
# specific snapshot (cross-platform-review eval docs, packaging metadata)
# and protecting them by name keeps the rsync layer dumb. Filenames must
# match the per-directory rsync invocation below.
#
# Convention for new host-only annotations:
#   - eval-style notes: name them round-N-cross-platform-*.md and put them
#     in evals/.
#   - packaging metadata at the skill root (SOURCE_COMMIT.md) is handled by
#     the per-entry whitelist above (it is not in DIRS, so it is never
#     touched by rsync).
PROTECT_EVALS=(
  '/round-*-cross-platform-*.md'
)

build_filter_args() {
  # Print rsync --filter=... args for the protect list passed in.
  for pattern in "$@"; do
    printf -- '--filter=protect %s\n' "$pattern"
  done
}

echo "Syncing from $SRC -> $DEST"

for entry in "${DIRS[@]}"; do
  src_path="$SRC/$entry"
  if [[ ! -e "$src_path" ]]; then
    echo "  skip $entry (not in source)"
    continue
  fi
  if [[ -d "$src_path" ]]; then
    extra_filters=()
    if [[ "$entry" == "evals" ]]; then
      mapfile -t extra_filters < <(build_filter_args "${PROTECT_EVALS[@]}")
    fi
    rsync -a --delete \
      --exclude='__pycache__' \
      --exclude='*.pyc' \
      --exclude='workspace/' \
      "${extra_filters[@]}" \
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

# Run the packaged-paths validator so a sync that introduces an
# out-of-package pointer fails loud rather than silently corrupting the
# snapshot's metadata.
if [[ -x "$REPO_ROOT/scripts/validate_packaged_paths.py" ]]; then
  "$REPO_ROOT/scripts/validate_packaged_paths.py" "$DEST"
fi

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
