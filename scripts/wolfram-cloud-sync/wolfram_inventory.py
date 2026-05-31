#!/usr/bin/env python3
"""
wolfram_inventory.py — scan a folder of Git repos for Wolfram files and produce
a manifest (CSV + JSON) suitable for syncing to a flat Wolfram Cloud inbox.

Usage:
    python3 wolfram_inventory.py [--root DIR] [--out DIR] [--cloud-prefix NAME]

Defaults:
    --root         C:\\Users\\Tony\\Documents\\GitHub  (or current dir on Linux/macOS)
    --out          ./manifest
    --cloud-prefix GitHub-Inbox

Wolfram extensions scanned:
    .nb  .wl  .wls  .cdf  .wxf  .nbp  .paclet
    .m   — only included when content sniff matches Wolfram markers
           (BeginPackage[, (* :Title:, (* :Mathematica Version:, etc.)

Skipped paths (anywhere in the tree):
    .git/  node_modules/  _archive/  _archive-recovery-staging/
    _twingrid_archives/  _worktrees/  _ip-triage/

Flat-inbox cloud naming:
    <repo>__<rel_subpath_with_slashes_as_double_underscores>
    e.g.  cajon/wolfram-starter.wl
       -> cajon__wolfram-starter.wl
    e.g.  WSS-2019/Final Project/Drafts/FinalProjectDraft1.nb
       -> WSS-2019__Final Project__Drafts__FinalProjectDraft1.nb
    Reversible: split the basename on '__' to recover (repo, *subpath, file).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

WOLFRAM_EXTS = {".nb", ".wl", ".wls", ".cdf", ".wxf", ".nbp", ".paclet"}
AMBIGUOUS_EXTS = {".m"}  # could be Wolfram, MATLAB, or Objective-C
SKIP_DIRS = {
    ".git",
    "node_modules",
    "_archive",
    "_archive-recovery-staging",
    "_twingrid_archives",
    "_worktrees",
    "_ip-triage",
    "archive",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
}
# Path-segment substrings (anywhere in the relative path) that indicate skill
# internals or template scaffolds — exclude from inventory. These files belong
# in git, not in Wolfram Cloud.
SKIP_PATH_SEGMENTS = (
    "/skills/",
    "/assets/templates/",
    "/templates/",
    "/wolfram-cloud-sync/",
)

# Folder reorg (2026-05-25): repos regrouped under instruments/<family>/<repo>/,
# habitat/<repo>/, fabrication/<repo>/, _meta/<repo>/. Map the on-disk family
# dir to the cloud category folder (note the plural 'woodwinds' the cloud uses).
FAMILY_TO_CATEGORY = {
    "strings": "strings",
    "woodwind": "woodwinds",
    "woodwinds": "woodwinds",
    "brass": "brass",
    "percussion": "percussion",
    "idiophones": "idiophones",
}
GROUP_DIRS = {"instruments", "habitat", "fabrication", "_meta"}


def path_repo_family(rel):
    """Return (repo, family) accounting for the post-reorg nested layout.

    instruments/<family>/<repo>/...   -> (repo, family)
    habitat|fabrication/<repo>/...     -> (repo, that-group)
    _meta/<repo>/...                   -> (repo, None)
    <repo>/... (flat / WSS-2019)       -> (repo, None)
    """
    parts = rel.parts
    if not parts:
        return "<root>", None
    if parts[0] == "instruments" and len(parts) >= 3:
        return parts[2], parts[1]
    if parts[0] in ("habitat", "fabrication", "_meta") and len(parts) >= 2:
        fam = parts[0] if parts[0] != "_meta" else None
        return parts[1], fam
    return parts[0], None

# Heuristic markers — if any of these appear in the first ~8KB of a .m file we
# treat it as a Wolfram Language package, not MATLAB/Objective-C.
WOLFRAM_M_MARKERS = (
    b"(* :Title:",
    b"(* :Context:",
    b"(* :Mathematica Version:",
    b"(* :Package Version:",
    b"BeginPackage[",
    b"EndPackage[",
    b"(* ::Package:: *)",
    b"(* ::Subsection:: *)",
)


def is_wolfram_m(path: Path) -> bool:
    try:
        with path.open("rb") as fh:
            head = fh.read(8192)
    except OSError:
        return False
    return any(marker in head for marker in WOLFRAM_M_MARKERS)


def sha256_short(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()[:16]


def cloud_name(rel_path: Path,
               repo: str,
               category: str | None,
               categorized: bool,
               overrides: list[tuple[str, str, str]] | None = None) -> str:
    """Compute the cloud-side path for a local file.

    no categories: flat-inbox encoding,
        cajon/wolfram-starter.wl -> cajon__wolfram-starter.wl

    with categories: hierarchical Musical_Instruments/<category>/<repo>/<file>,
    where <repo> and <category> are resolved by the caller (reorg-aware).
        instruments/percussion/cajon/cajon-starter.wl
            -> Musical_Instruments/percussion/cajon/cajon-starter.wl

    file_overrides (from categories.yaml) win and supply their own folder:
        .../docs/build-packets/ocarina/ocarina-starter.wl
            -> Musical_Instruments/woodwinds/ocarina-family/ocarina-starter.wl

    WSS-2019 always stays under its own top-level folder.
    """
    parts = list(rel_path.parts)
    filename = parts[-1]
    if repo == "WSS-2019":
        return rel_path.as_posix() if categorized else "__".join(parts)
    if not categorized:
        return "__".join(parts)
    if overrides:
        m = match_file_override(rel_path, overrides)
        if m is not None:
            cat, inst = m
            return f"Musical_Instruments/{cat}/{inst}/{filename}"
    return f"Musical_Instruments/{category or 'unsorted'}/{repo}/{filename}"


def load_categories(yaml_path: Path):
    """Read categories.yaml.

    Returns (repo_to_cat, skip_set, file_overrides) where file_overrides is
    a list of (pattern, category, instrument) tuples.

    Recognized top-level keys:
      <category-name>: list of repo names
      skip:            list of repos to drop entirely
      file_overrides:  list of strings of the form
                       'pattern  ->  category/instrument-folder'
                       (first matching pattern wins).

    Pure-stdlib minimal parser — comments (#), blank lines, top-level keys
    ending in ':', list items prefixed with '  - ' (optionally quoted).
    """
    if not yaml_path.exists():
        return {}, set(), []
    repo_to_cat: dict[str, str] = {}
    skip: set[str] = set()
    overrides: list[tuple[str, str, str]] = []
    current: str | None = None
    with yaml_path.open(encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip()
            if not line or line.lstrip().startswith("#"):
                continue
            if line and not line.startswith(" ") and line.endswith(":"):
                current = line[:-1].strip()
                continue
            stripped = line.strip()
            if stripped.startswith("- ") and current is not None:
                value = stripped[2:].strip()
                # Strip surrounding quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                if not value:
                    continue
                if current == "skip":
                    skip.add(value)
                elif current == "file_overrides":
                    # "pattern  ->  category/instrument"
                    if "->" not in value:
                        continue
                    pattern, dest = value.split("->", 1)
                    pattern = pattern.strip()
                    dest = dest.strip()
                    if "/" in dest:
                        cat, inst = dest.split("/", 1)
                        overrides.append((pattern, cat.strip(), inst.strip()))
                else:
                    repo_to_cat[value] = current
    return repo_to_cat, skip, overrides


def match_file_override(rel_path: Path,
                        overrides: list[tuple[str, str, str]]
                        ) -> tuple[str, str] | None:
    """Return (category, instrument-folder) for the first matching override,
    or None if no override applies. Match is plain substring on the
    posix-form relative path."""
    s = rel_path.as_posix()
    for pattern, category, instrument in overrides:
        if pattern in s:
            return category, instrument
    return None


def walk(root: Path, skip_repos: set[str] | None = None):
    """Yield (rel_path, abs_path, kind) for every Wolfram file under root.

    Skips files in SKIP_DIRS, files whose relative path contains one of
    SKIP_PATH_SEGMENTS (skill internals / templates), and files in repos
    listed in skip_repos.
    """
    root = root.resolve()
    skip_repos = skip_repos or set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext in WOLFRAM_EXTS:
                kind = "wolfram"
            elif ext in AMBIGUOUS_EXTS:
                p = Path(dirpath) / fname
                if not is_wolfram_m(p):
                    continue
                kind = "wolfram-m-sniffed"
            else:
                continue
            abs_path = Path(dirpath) / fname
            rel_path = abs_path.relative_to(root)
            rel_str = "/" + rel_path.as_posix() + "/"
            if any(seg in rel_str for seg in SKIP_PATH_SEGMENTS):
                continue
            repo_name, _fam = path_repo_family(rel_path)
            if repo_name in skip_repos:
                continue
            yield rel_path, abs_path, kind


def _resolve_category(rel: Path, repo: str, family: str | None,
                      categories: dict[str, str] | None,
                      overrides: list[tuple[str, str, str]] | None) -> str | None:
    """Return the cloud category. Priority: file_overrides > explicit
    categories.yaml repo mapping > reorg family-dir mapping > 'unsorted'."""
    if categories is None:
        return None
    if overrides:
        m = match_file_override(rel, overrides)
        if m is not None:
            return m[0]
    if repo in categories:
        return categories[repo]
    if family and family in FAMILY_TO_CATEGORY:
        return FAMILY_TO_CATEGORY[family]
    return "unsorted"


def build_records(root: Path,
                  categories: dict[str, str] | None = None,
                  skip_repos: set[str] | None = None,
                  overrides: list[tuple[str, str, str]] | None = None):
    rows = []
    for rel, abs_, kind in walk(root, skip_repos=skip_repos):
        try:
            st = abs_.stat()
        except OSError:
            continue
        repo, family = path_repo_family(rel)
        category = _resolve_category(rel, repo, family, categories, overrides)
        rows.append(
            {
                "repo": repo,
                "rel_path": rel.as_posix(),
                "abs_path": str(abs_),
                "ext": rel.suffix.lower().lstrip("."),
                "kind": kind,
                "size_bytes": st.st_size,
                "mtime_iso": datetime.fromtimestamp(
                    st.st_mtime, tz=timezone.utc
                ).isoformat(),
                "sha256_16": sha256_short(abs_),
                "cloud_name": cloud_name(rel, repo, category,
                                         bool(categories), overrides),
                "category": category,
            }
        )
    rows.sort(key=lambda r: (r["repo"].lower(), r["rel_path"].lower()))
    return rows


def summarize(rows):
    by_ext: dict[str, int] = {}
    by_repo: dict[str, int] = {}
    total_bytes = 0
    for r in rows:
        by_ext[r["ext"]] = by_ext.get(r["ext"], 0) + 1
        by_repo[r["repo"]] = by_repo.get(r["repo"], 0) + 1
        total_bytes += r["size_bytes"]
    return {
        "total_files": len(rows),
        "total_bytes": total_bytes,
        "by_extension": dict(sorted(by_ext.items(), key=lambda x: -x[1])),
        "by_repo": dict(sorted(by_repo.items(), key=lambda x: -x[1])),
    }


def write_csv(rows, out_path: Path):
    fields = ["repo", "category", "rel_path", "ext", "kind", "size_bytes",
              "mtime_iso", "sha256_16", "cloud_name", "abs_path"]
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})


def write_json(rows, summary, cloud_prefix, root, out_path: Path,
               categorized: bool = False):
    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "root": str(root),
        "cloud_prefix": cloud_prefix,
        "categorized": categorized,
        "summary": summary,
        "files": rows,
    }
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)


def default_root() -> Path:
    win = Path(r"C:\Users\Tony\Documents\GitHub")
    if win.exists():
        return win
    return Path.cwd()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--root", type=Path, default=default_root())
    p.add_argument("--out", type=Path, default=Path("manifest"))
    p.add_argument("--cloud-prefix", default=None,
                   help="CloudObject prefix. Default: '' in categories mode, "
                        "else 'GitHub-Inbox'.")
    p.add_argument("--categories", type=Path, default=None,
                   help="YAML mapping category->[repos] (default: "
                        "./categories.yaml next to this script).")
    p.add_argument("--no-categories", action="store_true",
                   help="Force flat-inbox naming.")
    args = p.parse_args(argv)

    root: Path = args.root.expanduser().resolve()
    if not root.exists():
        print(f"ERROR: root does not exist: {root}", file=sys.stderr)
        return 2

    categories: dict[str, str] | None = None
    skip_repos: set[str] = set()
    overrides: list[tuple[str, str, str]] = []
    if not args.no_categories:
        cat_path = args.categories or (Path(__file__).parent / "categories.yaml")
        cat_path = cat_path.expanduser().resolve()
        if cat_path.exists():
            categories, skip_repos, overrides = load_categories(cat_path)
            print(f"Loaded categories: {cat_path}")
            print(f"  {len(categories)} repos categorized, "
                  f"{len(skip_repos)} skipped, {len(overrides)} file-overrides")
        elif args.categories is not None:
            print(f"ERROR: --categories file not found: {cat_path}", file=sys.stderr)
            return 2

    if args.cloud_prefix is not None:
        cloud_prefix = args.cloud_prefix
    elif categories:
        cloud_prefix = ""
    else:
        cloud_prefix = "GitHub-Inbox"

    out_dir: Path = args.out.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scanning {root} ...")
    rows = build_records(root, categories=categories, skip_repos=skip_repos,
                         overrides=overrides)
    summary = summarize(rows)

    csv_path = out_dir / "wolfram_manifest.csv"
    json_path = out_dir / "wolfram_manifest.json"
    write_csv(rows, csv_path)
    write_json(rows, summary, cloud_prefix, root, json_path,
               categorized=bool(categories))

    print(f"\nFound {summary['total_files']} Wolfram files "
          f"({summary['total_bytes']/1024:.1f} KiB)")
    print("\nBy extension:")
    for ext, n in summary["by_extension"].items():
        print(f"  .{ext:<8} {n}")
    print("\nTop repos:")
    for repo, n in list(summary["by_repo"].items())[:15]:
        print(f"  {n:>4}  {repo}")
    if categories:
        uncategorized = sorted({
            row["repo"] for row in rows
            if row.get("category") == "unsorted" and row["repo"] != "WSS-2019"
        })
        if uncategorized:
            print(f"\nUncategorized repos (mapped to 'unsorted/'): {len(uncategorized)}")
            for r in uncategorized:
                print(f"  {r}")
        # category breakdown
        from collections import Counter as _C
        cats = _C(row.get("category") for row in rows)
        print("\nBy cloud category:")
        for c, n in sorted(cats.items(), key=lambda x: (-x[1], str(x[0]))):
            print(f"  {n:>4}  {c}")

    print(f"\nManifest written to:\n  {csv_path}\n  {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
