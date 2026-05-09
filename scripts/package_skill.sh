#!/usr/bin/env bash
# Package one skill from this repo into a deployable zip artifact.
#
# Usage:
#   ./scripts/package_skill.sh <skill-name> [options]
#
# Options:
#   --dry-run       Print what would be done without creating the zip.
#   --from-tag TAG  Check out TAG, build the zip, then restore HEAD.
#   --allow-dirty   Skip the dirty-tree check (use with caution).
#   --out DIR       Output directory (default: dist/).
#
# Output: <out>/<skill-name>-v<version>.zip
#
# Requires: git, python3 (with PyYAML), zip
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
  sed -n '/^# Usage/,/^$/p' "$0" | sed 's/^# \?//'
  exit 1
}

die() { echo "error: $*" >&2; exit 1; }
info() { echo "==> $*"; }

# --- argument parsing ---
SKILL_NAME=""
DRY_RUN=0
FROM_TAG=""
ALLOW_DIRTY=0
OUT_DIR="$REPO_ROOT/dist"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)       DRY_RUN=1; shift ;;
    --from-tag)      FROM_TAG="$2"; shift 2 ;;
    --allow-dirty)   ALLOW_DIRTY=1; shift ;;
    --out)           OUT_DIR="$2"; shift 2 ;;
    -h|--help)       usage ;;
    -*)              die "unknown option: $1" ;;
    *)               [[ -z "$SKILL_NAME" ]] && SKILL_NAME="$1" || die "unexpected argument: $1"; shift ;;
  esac
done

[[ -n "$SKILL_NAME" ]] || die "skill name is required. Usage: $0 <skill-name> [options]"

# --- read manifest.yaml ---
MANIFEST="$REPO_ROOT/manifest.yaml"
[[ -f "$MANIFEST" ]] || die "manifest.yaml not found at $REPO_ROOT"

read_manifest() {
  python3 - "$MANIFEST" "$SKILL_NAME" <<'EOF'
import sys, yaml
manifest_path, skill_name = sys.argv[1], sys.argv[2]
with open(manifest_path) as f:
    data = yaml.safe_load(f)
active = data.get("skills", {}) or {}
entry = active.get(skill_name)
if not entry:
    print(f"NOTFOUND", end="")
    sys.exit(1)
version = entry.get("canonical_version", "")
repo_path = entry.get("repo_path", "")
print(f"{version}|{repo_path}", end="")
EOF
}

MANIFEST_OUT=$(read_manifest) || die "skill '$SKILL_NAME' not found in manifest.yaml"
VERSION="${MANIFEST_OUT%%|*}"
REPO_PATH="${MANIFEST_OUT##*|}"

[[ -n "$VERSION"   ]] || die "canonical_version missing for '$SKILL_NAME' in manifest.yaml"
[[ -n "$REPO_PATH" ]] || die "repo_path missing for '$SKILL_NAME' in manifest.yaml"

SKILL_DIR="$REPO_ROOT/$REPO_PATH"
[[ -d "$SKILL_DIR" ]] || die "skill directory not found: $SKILL_DIR"

ZIP_NAME="${SKILL_NAME}-v${VERSION}.zip"
ZIP_PATH="$OUT_DIR/$ZIP_NAME"

# --- summary ---
info "skill:   $SKILL_NAME"
info "version: $VERSION"
info "source:  $SKILL_DIR"
info "output:  $ZIP_PATH"
[[ -n "$FROM_TAG" ]] && info "from-tag: $FROM_TAG"
[[ $DRY_RUN -eq 1 ]] && { echo "(dry run — no files written)"; exit 0; }

# --- dirty-tree check ---
cd "$REPO_ROOT"
if [[ $ALLOW_DIRTY -eq 0 ]]; then
  if [[ -n "$(git status --short 2>/dev/null)" ]]; then
    die "working tree is dirty. Commit or stash changes before packaging, or use --allow-dirty"
  fi
fi

# --- optional: check out a specific tag ---
SAVED_HEAD=""
if [[ -n "$FROM_TAG" ]]; then
  git fetch --tags --quiet
  git tag | grep -qx "$FROM_TAG" || die "tag not found: $FROM_TAG"
  SAVED_HEAD=$(git rev-parse --abbrev-ref HEAD)
  info "checking out $FROM_TAG"
  git checkout --quiet "$FROM_TAG"
  # Recompute SKILL_DIR in case the checkout moved things (unlikely but safe)
  SKILL_DIR="$REPO_ROOT/$REPO_PATH"
fi

restore_head() {
  if [[ -n "$SAVED_HEAD" ]]; then
    git checkout --quiet "$SAVED_HEAD" 2>/dev/null || true
  fi
}
trap restore_head EXIT

# --- build zip ---
mkdir -p "$OUT_DIR"

# zip from the parent directory so the archive contains <repo_path>/...
PARENT_DIR="$(dirname "$SKILL_DIR")"
LEAF_DIR="$(basename "$SKILL_DIR")"

cd "$PARENT_DIR"
info "creating $ZIP_PATH"
zip -r "$ZIP_PATH" "$LEAF_DIR" --quiet

info "done: $(du -sh "$ZIP_PATH" | cut -f1) written to $ZIP_PATH"
