#!/usr/bin/env python3
"""
rename_starters.py — apply the v4.4.5 unique-name scheme to existing
`wolfram-starter.wl` and `instrument-model.wl` files across the GitHub
workspace, and update README / capstone-manifest references in lockstep.

Scheme:
    wolfram-starter.wl  -> {slug}-starter.wl
    instrument-model.wl -> {slug}-model.wl
where {slug} is normally the top-level repo or build-packet folder name.

Within-repo basename collisions resolved by prepending subpath segments:
    duduk/wolfram-starter.wl          -> duduk-starter.wl
    duduk/wolfram/wolfram-starter.wl  -> duduk-wolfram-starter.wl

Files NOT renamed (frozen / template / skill-internal):
    - any path under .git/, _worktrees/, _archive*/, _twingrid_archives/
    - any path containing /skills/ or /assets/templates/ or /templates/
    - already-uniquely-named files (`helmholtz-cavity-explorer.wl` etc.)
    - the 15 .nb files (WSS-2019, flutes research) — already unique

Usage:
    python3 rename_starters.py --root <DIR> [--dry-run] [--apply]

Default is --dry-run. Pass --apply to actually move files and rewrite
references. The script never commits to git — review the working tree first.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

SKIP_DIR_NAMES = {
    ".git",
    "_worktrees",
    "_twingrid_archives",
    "_ip-triage",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
}
SKIP_DIR_PREFIXES = ("_archive",)  # _archive, _archive-recovery-staging
# Path-segment substrings that indicate skill source or templates — leave alone.
SKIP_PATH_SEGMENTS = (
    "/skills/",
    "/assets/templates/",
    "/templates/",
)
RENAME_SOURCE_NAMES = {
    "wolfram-starter.wl": "starter",
    "instrument-model.wl": "model",
}
REFERENCE_FILE_GLOBS = ("README.md", "capstone-manifest.json", "print-packet.md",
                        "INSTRUMENT-MAKER-PROMPT.md", "CHANGELOG.md")


def walk_targets(root: Path):
    """Yield Path for each candidate file under root."""
    for dirpath, dirnames, filenames in os.walk(root):
        # prune skipped dirs in place
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES
                       and not any(d.startswith(p) for p in SKIP_DIR_PREFIXES)]
        for fname in filenames:
            if fname in RENAME_SOURCE_NAMES:
                yield Path(dirpath) / fname


def is_skipped_path(rel: Path) -> bool:
    rel_str = "/" + rel.as_posix() + "/"
    return any(seg in rel_str for seg in SKIP_PATH_SEGMENTS)


def slugify_segment(seg: str) -> str:
    """Convert a path segment to a filename-safe kebab-case slug."""
    s = re.sub(r"[^A-Za-z0-9]+", "-", seg).strip("-").lower()
    return s or "x"


def compute_new_name(rel: Path, suffix_kind: str, all_rels: list[Path]) -> str:
    """Compute the new filename for `rel` given the manifest of all targets.

    rel is relative to root, e.g. Path('duduk/wolfram/wolfram-starter.wl').
    suffix_kind is 'starter' or 'model'.
    """
    parts = list(rel.parts)
    # parts[-1] is the old filename. Post-2026-05-25 reorg, repos live under
    # instruments/<family>/<repo>/, habitat|fabrication|_meta/<repo>/ — strip
    # that grouping prefix so the slug is the repo, not "instruments".
    if parts[0] == "instruments" and len(parts) >= 3:
        repo, subdirs = parts[2], parts[3:-1]
    elif parts[0] in ("habitat", "fabrication", "_meta") and len(parts) >= 2:
        repo, subdirs = parts[1], parts[2:-1]
    else:
        repo, subdirs = parts[0], parts[1:-1]  # flat / WSS-2019 / loose

    # Slug components
    if not subdirs:
        # File at the repo root
        slug_parts = [repo]
    else:
        # Special case: instrument-maker/docs/build-packets/<family>/...
        # The packet "family" name is what we want as the slug.
        if (len(subdirs) >= 2
                and subdirs[0] == "docs"
                and subdirs[1] == "build-packets"
                and len(subdirs) >= 3):
            slug_parts = [subdirs[2]]
        else:
            # Default: repo + meaningful intermediate dirs
            ignore = {"build", "wolfram", "docs", "src"}
            meaningful = [d for d in subdirs if d.lower() not in ignore]
            if meaningful:
                slug_parts = [repo] + meaningful
            else:
                # Subdir chain was all-generic (e.g. duduk/wolfram/);
                # bring back the last dir as the disambiguator
                slug_parts = [repo, subdirs[-1]]

    slug = "-".join(slugify_segment(p) for p in slug_parts)
    return f"{slug}-{suffix_kind}.wl"


def build_plan(root: Path):
    """Return a list of (old_path, new_path, old_basename, new_basename) tuples,
    skipping anything in a skipped path or already-correct."""
    candidates = []
    for abs_ in walk_targets(root):
        rel = abs_.relative_to(root)
        if is_skipped_path(rel):
            continue
        candidates.append(rel)

    plan = []
    # Group by parent dir so we can detect a clash inside one directory.
    for rel in candidates:
        suffix_kind = RENAME_SOURCE_NAMES[rel.name]
        new_name = compute_new_name(rel, suffix_kind, candidates)
        if new_name == rel.name:
            continue
        old_path = root / rel
        new_path = old_path.with_name(new_name)
        plan.append((old_path, new_path, rel.name, new_name, rel))

    # Sanity check: no two new_paths collide
    seen = defaultdict(list)
    for old, new, _, _, rel in plan:
        seen[new].append(rel.as_posix())
    collisions = {k: v for k, v in seen.items() if len(v) > 1}
    if collisions:
        print("ERROR: rename plan has collisions:", file=sys.stderr)
        for k, v in collisions.items():
            print(f"  {k} <-- " + ", ".join(v), file=sys.stderr)
        raise SystemExit(2)
    return plan


def update_references_in_repo(repo_dir: Path, old_basename: str, new_basename: str,
                              apply: bool):
    """Search a repo for textual references to old_basename and replace with
    new_basename. Returns a list of (file, count) tuples."""
    edits = []
    for dirpath, dirnames, filenames in os.walk(repo_dir):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES
                       and not any(d.startswith(p) for p in SKIP_DIR_PREFIXES)]
        for fname in filenames:
            if not any(fname == g or fname.endswith(g) for g in REFERENCE_FILE_GLOBS):
                # Only touch a curated set of doc files to limit blast radius.
                continue
            path = Path(dirpath) / fname
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if old_basename not in text:
                continue
            count = text.count(old_basename)
            new_text = text.replace(old_basename, new_basename)
            if apply:
                path.write_text(new_text, encoding="utf-8")
            edits.append((path, count))
    return edits


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--root", type=Path, required=True,
                   help="Workspace root (parent folder of all the repos)")
    p.add_argument("--apply", action="store_true",
                   help="Actually perform renames and edits (default is dry-run)")
    p.add_argument("--no-refs", action="store_true",
                   help="Skip the reference-rewrite pass; only rename files")
    args = p.parse_args(argv)

    root: Path = args.root.expanduser().resolve()
    if not root.exists():
        print(f"ERROR: root does not exist: {root}", file=sys.stderr)
        return 2

    plan = build_plan(root)
    print(f"Workspace root: {root}")
    print(f"Planned renames: {len(plan)}\n")

    # Print plan grouped by repo
    by_repo = defaultdict(list)
    for old, new, old_basename, new_basename, rel in plan:
        by_repo[rel.parts[0]].append((rel, new_basename))
    for repo in sorted(by_repo):
        print(f"--- {repo}")
        for rel, new_basename in by_repo[repo]:
            print(f"   {rel.as_posix():<70} -> {new_basename}")
    print()

    if not args.apply:
        print("(dry-run) No files were moved. Pass --apply to execute.")
        return 0

    # Execute renames
    print("Applying renames...")
    moves = 0
    ref_edits = 0
    seen_repo_edits: set[tuple[str, str, str]] = set()
    for old, new, old_basename, new_basename, rel in plan:
        if new.exists():
            print(f"  SKIP (target exists): {new}", file=sys.stderr)
            continue
        old.rename(new)
        moves += 1

        if args.no_refs:
            continue

        # Update references inside the repo (idempotent per (repo,old,new))
        repo_dir = root / rel.parts[0]
        key = (rel.parts[0], old_basename, new_basename)
        if key in seen_repo_edits:
            continue
        seen_repo_edits.add(key)
        edits = update_references_in_repo(repo_dir, old_basename, new_basename, apply=True)
        for path, count in edits:
            print(f"   ref: {path.relative_to(root)} ({count}x {old_basename} -> {new_basename})")
            ref_edits += count

    print(f"\nDone. Files renamed: {moves}. Reference edits: {ref_edits}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
