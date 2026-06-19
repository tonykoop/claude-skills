#!/usr/bin/env python3
"""Shared Subassemblies report — the portable, offline twin of the #244 MOC.

Story #244 shipped an Obsidian Map-of-Content whose Dataview / dataviewjs
dashboards group ideas by shared functional tag. Those dashboards only render
*inside Obsidian with the Dataview plugin* — they can't run in Codex/Gemini CLI,
CI, or a quick terminal check, and can't be unit-tested. This script reproduces
the same views deterministically from the `functions:` / `interfaces:`
frontmatter (the #243 tagging schema) so "see every idea that shares a given
mechanism in one view" works everywhere, not just in the vault.

It mirrors the MOC's four dashboards:
  1. Every function -> the ideas that perform it.
  2. **Shared subassemblies** — functions shared by >= 2 ideas (the headline view).
  3. Shared interfaces — interface tokens shared by >= 2 ideas (the Lego sockets).
  4. Cross-pollination candidate pairs — idea pairs sharing a function (+ interface bonus).

Pure stdlib (no PyYAML) so it stays runtime-portable. Reads real `---` Obsidian
frontmatter or a fenced ```yaml block (the GitHub-issue form the schema documents).

CLI:
    shared_subassemblies.py --dir path/to/notes      # markdown report
    shared_subassemblies.py --dir path/to/notes --json
Exit 0 = report produced (even if empty), 2 = bad usage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FACET_KEYS = ("functions", "interfaces", "materials")
SCALAR_KEYS = ("id", "idea")


def extract_frontmatter(text: str) -> str:
    """Return the YAML frontmatter region: leading `---...---`, or a ```yaml fence."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end]
    m = re.search(r"```(?:ya?ml)?\s*\n(.*?)\n```", text, re.DOTALL)
    return m.group(1) if m else ""


def _clean(value: str) -> str:
    # Strip an inline `# comment`, surrounding quotes, and whitespace.
    value = re.sub(r"\s+#.*$", "", value).strip()
    if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
        value = value[1:-1]
    return value.strip()


def parse_frontmatter(text: str) -> dict:
    """Minimal block/flow-list YAML parse for the documented facet schema."""
    fm = extract_frontmatter(text)
    data: dict = {k: [] for k in FACET_KEYS}
    current: str | None = None
    for raw in fm.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        list_item = re.match(r"^\s+-\s+(.*)$", line)
        if list_item and current in FACET_KEYS:
            item = _clean(list_item.group(1))
            if item:
                data[current].append(item)
            continue
        kv = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if not kv:
            continue
        key, val = kv.group(1), kv.group(2)
        current = key
        if key in FACET_KEYS:
            val = _clean(val)
            if val.startswith("[") and val.endswith("]"):  # flow list
                data[key] = [_clean(x) for x in val[1:-1].split(",") if _clean(x)]
                current = None
            # else: block list collected on following lines
        elif key in SCALAR_KEYS:
            data[key] = _clean(val)
    return data


def load_notes(directory: Path) -> list:
    notes: list = []
    for path in sorted(directory.rglob("*.md")):
        fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        label = fm.get("idea") or fm.get("id") or path.stem
        notes.append({
            "label": label,
            "functions": fm.get("functions", []),
            "interfaces": fm.get("interfaces", []),
        })
    return notes


def group_by(notes: list, facet: str) -> dict:
    """{tag: [labels]} for a facet, sorted by descending idea count then tag."""
    out: dict = {}
    for note in notes:
        for tag in note.get(facet, []):
            out.setdefault(tag, [])
            if note["label"] not in out[tag]:
                out[tag].append(note["label"])
    return dict(sorted(out.items(), key=lambda kv: (-len(kv[1]), kv[0])))


def shared(group: dict, min_count: int = 2) -> dict:
    return {tag: labels for tag, labels in group.items() if len(labels) >= min_count}


def candidate_pairs(notes: list) -> list:
    """Idea pairs sharing >=1 function; score = shared functions + interface bonus."""
    pairs: list = []
    for i in range(len(notes)):
        for j in range(i + 1, len(notes)):
            a, b = notes[i], notes[j]
            fns = sorted(set(a["functions"]) & set(b["functions"]))
            ifaces = sorted(set(a["interfaces"]) & set(b["interfaces"]))
            if not fns:
                continue
            pairs.append({
                "a": a["label"], "b": b["label"],
                "shared_functions": fns, "shared_interfaces": ifaces,
                "score": len(fns) + len(ifaces),
            })
    pairs.sort(key=lambda p: (-p["score"], p["a"], p["b"]))
    return pairs


def build_report(notes: list) -> dict:
    return {
        "by_function": group_by(notes, "functions"),
        "shared_subassemblies": shared(group_by(notes, "functions")),
        "shared_interfaces": shared(group_by(notes, "interfaces")),
        "candidate_pairs": candidate_pairs(notes),
        "untagged": [n["label"] for n in notes if not n["functions"]],
    }


def render_markdown(report: dict) -> str:
    lines = ["# Shared Subassemblies (offline)", ""]

    def table(title: str, group: dict, col: str) -> None:
        lines.append(f"## {title}")
        if not group:
            lines.append("_none_")
        else:
            lines.append(f"| {col} | # ideas | Ideas |")
            lines.append("|---|---|---|")
            for tag, labels in group.items():
                lines.append(f"| {tag} | {len(labels)} | {', '.join(labels)} |")
        lines.append("")

    table("Shared subassemblies (functions in 2+ ideas)", report["shared_subassemblies"], "Function")
    table("Shared interfaces (the Lego sockets)", report["shared_interfaces"], "Interface")
    table("Every function", report["by_function"], "Function")
    lines.append("## Cross-pollination candidate pairs")
    if not report["candidate_pairs"]:
        lines.append("_none_")
    else:
        lines.append("| A | B | Shared functions | Shared interfaces | Score |")
        lines.append("|---|---|---|---|---|")
        for p in report["candidate_pairs"]:
            lines.append(
                f"| {p['a']} | {p['b']} | {', '.join(p['shared_functions'])} | "
                f"{', '.join(p['shared_interfaces']) or '—'} | {p['score']} |"
            )
    lines.append("")
    if report["untagged"]:
        lines.append("## Untagged ideas (fix these — no `functions:`)")
        for label in report["untagged"]:
            lines.append(f"- {label}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline Shared Subassemblies report from functional tags.")
    parser.add_argument("--dir", required=True, help="Directory of markdown idea notes.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown.")
    args = parser.parse_args(argv)
    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"error: not a directory: {directory}", file=sys.stderr)
        return 2
    report = build_report(load_notes(directory))
    if args.json:
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
