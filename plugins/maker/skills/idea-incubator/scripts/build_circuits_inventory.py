#!/usr/bin/env python3
"""Build the circuits inventory of reusable functional primitives.

Story #248 of the Cross-Pollination Engine (epic #236). This helper walks one
or more repos and/or an Obsidian vault for ideas tagged with the
functional-tagging schema (#243), extracts the ones that qualify as reusable
functional primitives ("circuits"), and emits the inventory as Markdown and/or
JSON.

Offline-first and read-only: it never edits source ideas. It is a SKELETON -
the YAML frontmatter parser and the repo/vault walkers have clear TODOs where
project-specific wiring is needed. Dry-run is the default; nothing is written
unless --apply (or an explicit --out path) is given.

Examples:
    # Dry run: print what WOULD be written, scanning a vault and a repo clone.
    python build_circuits_inventory.py --vault ~/vault --repo-root ~/GitHub

    # Write the JSON + Markdown inventory next to this reference file.
    python build_circuits_inventory.py --vault ~/vault \\
        --out-json circuits-inventory.json --out-md circuits-inventory.md --apply
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

# Maturity levels that qualify an idea as a reusable primitive.
QUALIFYING_MATURITY = {"built", "shipped"}

# Directories never worth walking.
SKIP_DIRS = {".git", "node_modules", "target", ".venv", "__pycache__", ".obsidian"}


@dataclass(frozen=True)
class Circuit:
    """One reusable functional primitive (an inventory entry)."""

    id: str
    name: str
    functions: list[str] = field(default_factory=list)
    interfaces: list[str] = field(default_factory=list)
    materials: list[str] = field(default_factory=list)
    source: str = ""
    maturity: str = ""
    reuse_notes: str = ""
    updated: str = ""


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Extract a YAML frontmatter mapping from markdown or a fenced issue body.

    Handles both real Obsidian `---` frontmatter and a fenced ```yaml block at
    the top of a GitHub issue body.

    TODO: replace the minimal line parser below with PyYAML
    (`yaml.safe_load`) once a dependency is acceptable. The minimal parser only
    understands `key: value` and `key:` followed by `  - item` lists, which is
    all the schema (#243) requires, but it is deliberately strict.
    """
    block: list[str] = []
    lines = text.splitlines()
    # Find a leading --- ... --- block or a ```yaml ... ``` block.
    fence = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i == 0 and stripped == "---":
            fence = "---"
            continue
        if fence is None and stripped.lower() in ("```yaml", "~~~yaml"):
            fence = "```"
            continue
        if fence == "---" and stripped == "---":
            break
        if fence == "```" and stripped in ("```", "~~~"):
            break
        if fence is not None:
            block.append(line)
    if not block:
        return {}

    data: dict[str, Any] = {}
    current_key: str | None = None
    for raw in block:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.lstrip().startswith("- ") and current_key is not None:
            data.setdefault(current_key, [])
            if isinstance(data[current_key], list):
                data[current_key].append(raw.split("- ", 1)[1].strip())
            continue
        if ":" in raw:
            key, _, value = raw.partition(":")
            key = key.strip()
            value = value.strip().strip('"')
            current_key = key
            data[key] = value if value else []
    return data


def iter_idea_files(vault: Path | None, repo_root: Path | None) -> Iterable[Path]:
    """Yield candidate idea files from the vault and/or repo tree.

    TODO: tighten the globs to the project's real layout. For the vault we take
    every `.md`; for repos we currently take `.md` files too, on the assumption
    that issue bodies have been exported to markdown. If ideas live only as live
    GitHub issues, add a `--issues-json` path (mirroring
    promote_batch_readiness.py) and parse those instead.
    """
    for root in (vault, repo_root):
        if root is None or not root.exists():
            continue
        for path in root.rglob("*.md"):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            yield path


def as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if value:
        return [str(value)]
    return []


def circuit_from_frontmatter(fm: dict[str, Any], path: Path) -> Circuit | None:
    """Convert one idea's frontmatter into a Circuit if it qualifies.

    Qualifying = has >=1 function AND maturity in QUALIFYING_MATURITY AND a
    source link (solved-in / source). Returns None otherwise.
    """
    functions = as_list(fm.get("functions"))
    maturity = str(fm.get("maturity", "")).strip()
    source = str(fm.get("solved-in") or fm.get("source") or "").strip()
    if not functions or maturity not in QUALIFYING_MATURITY or not source:
        return None

    # TODO: derive a stable id per #245 naming (<domain>-<function>-<variant>)
    # when an explicit id is absent; for now fall back to the existing id field.
    primitive_id = str(fm.get("id") or path.stem).strip()
    return Circuit(
        id=primitive_id,
        name=str(fm.get("idea") or path.stem).strip(),
        functions=functions,
        interfaces=as_list(fm.get("interfaces")),
        materials=as_list(fm.get("materials")),
        source=source,
        maturity=maturity,
        reuse_notes=str(fm.get("reuse-notes") or "TODO: add reuse notes").strip(),
        updated=str(fm.get("captured") or fm.get("updated") or "").strip(),
    )


def dedup_circuits(circuits: list[Circuit]) -> list[Circuit]:
    """Collapse duplicate ids, keeping the most mature source.

    TODO: when two ids tie on maturity, prefer the one with the more recent
    `updated` date; for now first-seen wins on a tie.
    """
    order = ["concept", "sketch", "proto", "built", "shipped"]
    rank = {m: i for i, m in enumerate(order)}
    best: dict[str, Circuit] = {}
    for c in circuits:
        prev = best.get(c.id)
        if prev is None or rank.get(c.maturity, 0) > rank.get(prev.maturity, 0):
            best[c.id] = c
    return sorted(best.values(), key=lambda c: (c.functions[:1], -rank.get(c.maturity, 0)))


def render_markdown(circuits: list[Circuit]) -> str:
    header = (
        "| id | name | functions | interfaces | source | maturity | reuse-notes | updated |\n"
        "|---|---|---|---|---|---|---|---|\n"
    )
    rows = []
    for c in circuits:
        rows.append(
            "| `{id}` | {name} | {fns} | {ifaces} | {src} | {mat} | {notes} | {upd} |".format(
                id=c.id,
                name=c.name.replace("|", "\\|"),
                fns=", ".join(f"`{f}`" for f in c.functions),
                ifaces=", ".join(f"`{i}`" for i in c.interfaces),
                src=c.source,
                mat=c.maturity,
                notes=c.reuse_notes.replace("|", "\\|"),
                upd=c.updated,
            )
        )
    return header + "\n".join(rows) + "\n"


def render_json(circuits: list[Circuit]) -> str:
    payload = [
        {("reuse-notes" if k == "reuse_notes" else k): v for k, v in asdict(c).items()}
        for c in circuits
    ]
    return json.dumps(payload, indent=2) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--vault", type=Path, default=None, help="Obsidian vault root to scan.")
    parser.add_argument("--repo-root", type=Path, default=None, help="Directory of repo clones to scan.")
    parser.add_argument("--out-json", type=Path, default=None, help="Where to write the JSON inventory.")
    parser.add_argument("--out-md", type=Path, default=None, help="Where to write the Markdown table.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write output files. Default is a dry run that prints to stdout.",
    )
    args = parser.parse_args(argv[1:])

    if args.vault is None and args.repo_root is None:
        parser.error("provide at least one of --vault or --repo-root")

    circuits: list[Circuit] = []
    for path in iter_idea_files(args.vault, args.repo_root):
        try:
            fm = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        circuit = circuit_from_frontmatter(fm, path)
        if circuit is not None:
            circuits.append(circuit)

    circuits = dedup_circuits(circuits)
    markdown = render_markdown(circuits)
    js = render_json(circuits)

    dry_run = not args.apply
    if dry_run:
        sys.stdout.write(f"# DRY RUN - found {len(circuits)} qualifying circuit(s). "
                         f"Re-run with --apply to write.\n\n")
        sys.stdout.write(markdown)
        sys.stdout.write("\n--- JSON ---\n")
        sys.stdout.write(js)
        return 0

    if args.out_md:
        args.out_md.write_text(markdown, encoding="utf-8")
        sys.stdout.write(f"wrote {args.out_md}\n")
    if args.out_json:
        args.out_json.write_text(js, encoding="utf-8")
        sys.stdout.write(f"wrote {args.out_json}\n")
    if not args.out_md and not args.out_json:
        sys.stdout.write("--apply set but no --out-md/--out-json given; nothing written.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
