#!/usr/bin/env python3
"""Validate that no machine-loaded value inside a packaged skill points
outside the package.

Why: portable skill packages (zip uploads, mobile installs, foreign-host
sideloads) cannot rely on sibling host-repo directories existing on disk.
A YAML or JSON value that resolves to `../../../docs/something/` will
silently break in those environments.

Scope: walks the given skill directory, parses every `.yaml`/`.yml`/`.json`
file, and flags any string value that looks like a path escaping the
package (starts with `../`, or is an absolute path that does not point
inside the skill).

Out of scope: prose pointers in `*.md` files. Those are documentation,
not load instructions, and may legitimately reference host-repo locations
like `docs/benchmarks/...` for context. Document such references with
clearly human-language framing (e.g., "lives at ... in the host repo")
rather than machine-loadable paths.

Usage:
    scripts/validate_packaged_paths.py path/to/skill

Exit codes:
    0 — clean
    1 — at least one out-of-package path found
    2 — invalid usage / missing dependency
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
from typing import Iterable, Iterator

try:
    import yaml
except ImportError:
    print("error: pyyaml is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)


# A path-like string is something that contains a path separator and
# either an extension, a known segment, or the parent-dir marker. We
# intentionally keep this narrow so we don't false-positive on prose-like
# strings that happen to live in JSON/YAML descriptions.
PATH_HINT = re.compile(r"^(\.{1,2}/|/|[A-Za-z]:[\\/])|/")


def iter_strings(node) -> Iterator[str]:
    if isinstance(node, str):
        yield node
    elif isinstance(node, list):
        for item in node:
            yield from iter_strings(item)
    elif isinstance(node, dict):
        for value in node.values():
            yield from iter_strings(value)


def looks_like_path(value: str) -> bool:
    """Heuristic: does this string look like a filesystem path the model
    or a script would resolve at runtime? We err on the side of
    flagging things rather than silently passing them."""
    if "\n" in value or len(value) > 400:
        return False
    if not PATH_HINT.search(value):
        return False
    # Reject obvious URLs and email addresses.
    if value.startswith(("http://", "https://", "git@", "mailto:")):
        return False
    # Require at least one extension or directory segment that looks
    # filesystem-y, to drop sentences like "do this/that".
    return bool(re.search(r"\.[A-Za-z0-9]{1,8}(?:$|[/\s])", value)
                or value.startswith("../")
                or value.endswith("/"))


def escapes_package(value: str, skill_root: pathlib.Path,
                    file_dir: pathlib.Path) -> bool:
    if value.startswith("../"):
        # Resolve relative to the file containing the value.
        resolved = (file_dir / value).resolve()
        try:
            resolved.relative_to(skill_root.resolve())
            return False
        except ValueError:
            return True
    if value.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", value):
        # Absolute path. Allowed only if it points inside the skill.
        try:
            pathlib.Path(value).resolve().relative_to(skill_root.resolve())
            return False
        except (ValueError, OSError):
            return True
    return False


def validate(skill_root: pathlib.Path) -> list[str]:
    findings: list[str] = []
    yaml_files = list(skill_root.rglob("*.yaml")) + list(skill_root.rglob("*.yml"))
    json_files = list(skill_root.rglob("*.json"))

    for path in sorted(yaml_files + json_files):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            findings.append(f"{path}: cannot read ({exc})")
            continue

        try:
            if path.suffix == ".json":
                data = json.loads(text)
            else:
                data = yaml.safe_load(text)
        except (json.JSONDecodeError, yaml.YAMLError) as exc:
            findings.append(f"{path}: cannot parse ({exc})")
            continue

        if data is None:
            continue

        for value in iter_strings(data):
            if not looks_like_path(value):
                continue
            if escapes_package(value, skill_root, path.parent):
                rel = path.relative_to(skill_root)
                findings.append(
                    f"{rel}: value escapes package -> {value!r}"
                )

    return findings


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_packaged_paths.py <path-to-skill>", file=sys.stderr)
        return 2
    skill_root = pathlib.Path(argv[1])
    if not skill_root.is_dir() or not (skill_root / "SKILL.md").is_file():
        print(f"error: {skill_root} is not a skill directory", file=sys.stderr)
        return 2

    findings = validate(skill_root)
    if not findings:
        print(f"validate_packaged_paths: ok ({skill_root})")
        return 0

    print(f"validate_packaged_paths: {len(findings)} issue(s) in {skill_root}")
    for line in findings:
        print(f"  - {line}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
