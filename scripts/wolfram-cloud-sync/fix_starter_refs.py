#!/usr/bin/env python3
"""
fix_starter_refs.py — second-pass reference fixer for the
v4.4.5 wolfram-starter / instrument-model rename. Run AFTER
rename_starters.py has moved the files.

Strategy: for every text file under a non-skipped path, look for the legacy
basenames `wolfram-starter.wl` and `instrument-model.wl`. When a match is
found, resolve it path-aware:

  bare `wolfram-starter.wl`             -> sibling `*-starter.wl`, walking up
  `<subdir>/wolfram-starter.wl`         -> resolved subdir's `*-starter.wl`
  `../wolfram-starter.wl`               -> parent-relative path resolved
  bare `instrument-model.wl`            -> sibling `*-model.wl`, walking up
  `<subdir>/instrument-model.wl`        -> resolved subdir's `*-model.wl`

If a unique `*-starter.wl` / `*-model.wl` exists in the resolved directory,
replace with that basename; otherwise leave the reference alone and report it.

Usage:
    python3 fix_starter_refs.py --root <DIR> [--apply]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

SKIP_DIR_NAMES = {
    ".git", "_worktrees", "_twingrid_archives", "_ip-triage",
    "node_modules", ".venv", "venv", "__pycache__",
}
SKIP_DIR_PREFIXES = ("_archive",)
SKIP_PATH_SEGMENTS = (
    "/skills/", "/assets/templates/", "/templates/",
)
TEXT_EXTENSIONS = {".md", ".json", ".yaml", ".yml", ".html", ".py", ".wl",
                   ".wls", ".txt", ".sh", ".ps1", ".csv", ".m"}
LEGACY_NAMES = {
    "wolfram-starter.wl": "starter",
    "instrument-model.wl": "model",
}


def is_skipped(rel: Path) -> bool:
    s = "/" + rel.as_posix() + "/"
    if any(seg in s for seg in SKIP_PATH_SEGMENTS):
        return True
    for part in rel.parts:
        if part in SKIP_DIR_NAMES or any(part.startswith(p) for p in SKIP_DIR_PREFIXES):
            return True
    return False


def walk_text_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES
                       and not any(d.startswith(p) for p in SKIP_DIR_PREFIXES)]
        for fname in filenames:
            if Path(fname).suffix.lower() not in TEXT_EXTENSIONS:
                continue
            p = Path(dirpath) / fname
            rel = p.relative_to(root)
            if is_skipped(rel):
                continue
            yield p


def find_in_dir(dir_path: Path, suffix_kind: str) -> str | None:
    """Look for a *-starter.wl or *-model.wl file in dir_path. Returns its
    basename if exactly one exists; otherwise None."""
    if not dir_path.is_dir():
        return None
    pattern = f"*-{suffix_kind}.wl"
    matches = sorted(dir_path.glob(pattern))
    if len(matches) == 1:
        return matches[0].name
    return None


def resolve_reference(file_path: Path, prefix: str, legacy_name: str,
                      suffix_kind: str) -> str | None:
    """For a reference of the form `<prefix><legacy_name>` inside file_path,
    return the replacement (basename or prefix+basename), or None if it
    can't be resolved unambiguously.

    `prefix` is the path that precedes the legacy filename in the text. It
    may be empty (bare reference) or end with '/'.
    """
    base_dir = file_path.parent
    if prefix:
        rel = prefix.rstrip("/")
        if rel.startswith("./"):
            rel = rel[2:]
        target_dir = (base_dir / rel).resolve() if rel else base_dir
        found = find_in_dir(target_dir, suffix_kind)
        if found:
            return prefix + found
        return None

    # Bare reference: try the file's own directory first, then walk up. At
    # each level, also peek one subdirectory deep for the common case of
    # `wolfram/<file>` living one level below the doc that names it.
    cursor = base_dir
    for _ in range(6):
        found = find_in_dir(cursor, suffix_kind)
        if found:
            return found
        # Look one level down: e.g. glockenspiel/capstone-deck.md mentioning
        # bare `instrument-model.wl` should resolve to glockenspiel/wolfram/*-model.wl.
        if cursor.is_dir():
            sub_matches = []
            for sub in cursor.iterdir():
                if sub.is_dir() and sub.name not in SKIP_DIR_NAMES:
                    name = find_in_dir(sub, suffix_kind)
                    if name:
                        sub_matches.append((sub.name, name))
            if len(sub_matches) == 1:
                sub_name, basename = sub_matches[0]
                return f"{sub_name}/{basename}"
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    return None


def make_pattern(legacy_name: str) -> re.Pattern:
    # Optional path prefix (./, ../, or named segments) followed by the legacy
    # filename. Captures the prefix in group 1.
    return re.compile(
        r'((?:\.{1,2}/|[A-Za-z0-9_.\-]+/)*)' + re.escape(legacy_name)
    )


def process_file(path: Path, apply: bool):
    """Return list of (legacy_ref, replacement_or_None, was_changed)."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    findings = []
    new_text = text
    changed = False

    for legacy_name, suffix_kind in LEGACY_NAMES.items():
        if legacy_name not in new_text:
            continue
        pattern = make_pattern(legacy_name)

        def repl(match):
            nonlocal changed
            prefix = match.group(1) or ""
            full = match.group(0)
            replacement = resolve_reference(path, prefix, legacy_name, suffix_kind)
            if replacement and replacement != full:
                changed = True
                findings.append((full, replacement, True))
                return replacement
            findings.append((full, replacement, False))
            return full

        new_text = pattern.sub(repl, new_text)

    if apply and changed:
        path.write_text(new_text, encoding="utf-8")
    return findings


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--apply", action="store_true",
                   help="Write changes (default is dry-run)")
    args = p.parse_args(argv)

    root: Path = args.root.expanduser().resolve()
    if not root.exists():
        print(f"ERROR: root does not exist: {root}", file=sys.stderr)
        return 2

    files_scanned = 0
    files_changed = 0
    refs_fixed = 0
    refs_skipped = 0
    skipped_details = []

    for path in walk_text_files(root):
        files_scanned += 1
        findings = process_file(path, apply=args.apply)
        if not findings:
            continue
        applied_here = [f for f in findings if f[2]]
        skipped_here = [f for f in findings if not f[2]]
        if applied_here:
            files_changed += 1
            refs_fixed += len(applied_here)
            rel = path.relative_to(root)
            print(f"  {rel}")
            for full, replacement, _ in applied_here:
                print(f"    {full!r}  ->  {replacement!r}")
        for full, _, _ in skipped_here:
            refs_skipped += 1
            skipped_details.append((path.relative_to(root), full))

    print()
    print(f"Files scanned: {files_scanned}")
    print(f"Files {'changed' if args.apply else 'with applicable changes'}: {files_changed}")
    print(f"References fixed: {refs_fixed}")
    print(f"References left alone (unresolvable): {refs_skipped}")
    if skipped_details:
        print()
        print("Skipped (no unique target file found):")
        for rel, full in skipped_details:
            print(f"  {rel}  references  {full}")

    if not args.apply:
        print()
        print("(dry-run) No files written. Pass --apply to execute.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
