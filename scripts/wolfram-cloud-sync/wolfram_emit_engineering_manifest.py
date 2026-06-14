#!/usr/bin/env python3
"""
wolfram_emit_engineering_manifest.py — write the `engineering.wolfram[]`
contract block into each per-instrument `capstone-manifest.json`.

This is the bridge between wolfram-cloud-sync (writer) and the explorer.html
generator inside instrument-maker-v4 (reader). After uploading and
publishing, run this to populate each repo's capstone-manifest.json so the
explorer can iterate the list and emit one embed wrapper per notebook.

Schema written per file:

    {
      "source_file": "wolfram/sambuca-acoustics-starter.wl",
      "cloud_path":  "GitHub-Inbox/sambuca__wolfram__sambuca-acoustics-starter.wl",
      "cloud_url":   "https://www.wolframcloud.com/obj/.../sambuca__wolfram__sambuca-acoustics-starter.wl",
      "permission":  "Public-Execute",
      "kind":        "acoustics-starter"   // or "geometry-model" or "other"
    }

The list lives at `engineering.wolfram` in capstone-manifest.json. If
`engineering` already exists, its other keys are preserved. If
capstone-manifest.json doesn't exist for a repo, the script logs and skips.

Usage:
    python3 wolfram_emit_engineering_manifest.py \\
        --manifest manifest/wolfram_manifest.json \\
        --embed-urls manifest/wolfram_embed_urls.json \\
        [--workspace-root /path/to/GitHub] \\
        [--apply]

Default is dry-run; pass --apply to write.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def classify_kind(rel_path: str) -> str:
    name = Path(rel_path).name.lower()
    if name.endswith("-model.wl") or name == "instrument-model.wl":
        return "geometry-model"
    if name.endswith("-starter.wl") or name == "wolfram-starter.wl":
        return "acoustics-starter"
    return "other"


def load_manifest(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_embed_urls(path: Path) -> dict[str, dict]:
    """Returns {cloud_path: {url, permission}}."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        records = json.load(fh)
    out = {}
    for r in records:
        cp = r.get("cloud_path")
        if cp:
            out[cp] = r
    return out


def group_by_repo(files: list[dict]) -> dict[str, list[dict]]:
    by_repo = defaultdict(list)
    for f in files:
        repo = f.get("repo") or f["rel_path"].split("/")[0]
        by_repo[repo].append(f)
    return by_repo


def build_entries(files: list[dict], embed_lookup: dict[str, dict],
                  cloud_prefix: str) -> list[dict]:
    entries = []
    for f in files:
        # When cloud_prefix is empty (categories mode) the cloud_name is
        # already the full path. Otherwise prepend the prefix.
        if cloud_prefix:
            cloud_path = f"{cloud_prefix}/{f['cloud_name']}"
        else:
            cloud_path = f["cloud_name"]
        published = embed_lookup.get(cloud_path, {})
        # rel_path inside the repo (strip leading "<repo>/")
        rel_path = f["rel_path"]
        repo_prefix = rel_path.split("/", 1)[0] + "/"
        repo_rel = rel_path[len(repo_prefix):] if rel_path.startswith(repo_prefix) else rel_path
        # Default permission is "Private" (file uploaded but not yet public).
        # publish.wls writes "Public-Execute", "failed", "missing", or
        # "would-publish" depending on what happened to each file.
        entries.append({
            "source_file": repo_rel,
            "cloud_path": cloud_path,
            "cloud_url": published.get("cloud_url"),
            "permission": published.get("permission", "Private"),
            "kind": classify_kind(rel_path),
        })
    return entries


def update_capstone(capstone_path: Path, entries: list[dict], apply: bool):
    """Merge entries into capstone-manifest.json's engineering.wolfram list."""
    if capstone_path.exists():
        with capstone_path.open(encoding="utf-8") as fh:
            try:
                data = json.load(fh)
            except json.JSONDecodeError as e:
                print(f"    ERROR: invalid JSON in {capstone_path}: {e}",
                      file=sys.stderr)
                return False, "json-error"
    else:
        data = {}

    engineering = data.setdefault("engineering", {})
    if not isinstance(engineering, dict):
        # Existing schema has `engineering` as something else (rare); rather
        # than overwrite, nest under `engineering_wolfram` at the root.
        data["engineering_wolfram"] = entries
        action = "side-channel"
    else:
        engineering["wolfram"] = entries
        action = "merged"

    if apply:
        with capstone_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    return True, action


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--manifest", type=Path, required=True,
                   help="Path to wolfram_manifest.json")
    p.add_argument("--embed-urls", type=Path,
                   help="Path to wolfram_embed_urls.json (optional; without "
                        "it, cloud_url stays null and permission stays 'pending')")
    p.add_argument("--workspace-root", type=Path,
                   help="Override workspace root (default: from manifest)")
    p.add_argument("--apply", action="store_true",
                   help="Write changes (default is dry-run)")
    args = p.parse_args(argv)

    if not args.manifest.exists():
        print(f"ERROR: manifest not found: {args.manifest}", file=sys.stderr)
        return 2

    manifest = load_manifest(args.manifest)
    cloud_prefix = manifest.get("cloud_prefix", "GitHub-Inbox")
    workspace_root = (args.workspace_root or Path(manifest.get("root", ""))).resolve()
    if not workspace_root.exists():
        print(f"ERROR: workspace root not found: {workspace_root}", file=sys.stderr)
        return 2

    embed_lookup = load_embed_urls(args.embed_urls) if args.embed_urls else {}
    if args.embed_urls and not embed_lookup:
        print(f"WARN: embed-urls file empty or missing: {args.embed_urls}")

    files = manifest.get("files", [])
    by_repo = group_by_repo(files)
    print(f"Workspace root: {workspace_root}")
    print(f"Cloud prefix:   {cloud_prefix}")
    print(f"Repos with Wolfram files: {len(by_repo)}")
    print(f"Embed URLs available:     {len(embed_lookup)}")
    print()

    written = 0
    missing_capstone = 0
    json_errors = 0
    side_channel = 0

    for repo, rows in sorted(by_repo.items()):
        capstone = workspace_root / repo / "capstone-manifest.json"
        entries = build_entries(rows, embed_lookup, cloud_prefix)

        if not capstone.exists():
            # Some repos (WSS-2019, claude-skills, instrument-maker) don't carry
            # a per-repo capstone-manifest.json. That's expected.
            print(f"  {repo}: no capstone-manifest.json (skipped, {len(entries)} entries dropped)")
            missing_capstone += 1
            continue

        ok, action = update_capstone(capstone, entries, apply=args.apply)
        if not ok:
            json_errors += 1
            continue
        if action == "side-channel":
            side_channel += 1
        written += 1
        urls_present = sum(1 for e in entries if e["cloud_url"])
        print(f"  {repo}: {len(entries)} entries ({urls_present} with URLs, action={action})")

    print()
    print(f"Repos updated:           {written}")
    print(f"Repos w/o capstone-mfst: {missing_capstone}")
    print(f"Repos w/ JSON errors:    {json_errors}")
    if side_channel:
        print(f"Repos with side-channel: {side_channel}")
    if not args.apply:
        print()
        print("(dry-run) No files written. Pass --apply to execute.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
