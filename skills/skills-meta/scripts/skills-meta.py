#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

DEFAULT_ROOTS = ("skills", "claude/skills", "codex/skills", "gemini/skills")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


@dataclass
class SkillRecord:
    name: str
    path: Path
    root: Path
    runtime: str
    version: str | None
    last_updated: str | None
    description: str | None
    manifest: dict[str, Any] | None = None
    planned: dict[str, Any] | None = None
    issues: list[str] = field(default_factory=list)

    def render_status(self) -> str:
        if self.issues:
            if "missing-from-manifest" in self.issues:
                return "unknown"
            return "drift"
        if self.planned and not self.manifest:
            return "planned"
        return "ok"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit installed skills against manifest.yaml.")
    parser.add_argument("--mode", choices=("inventory", "single", "drift", "fix"), default="inventory")
    parser.add_argument("--skill", help="Skill name to focus on in single/fix mode.")
    parser.add_argument("--manifest", default="manifest.yaml", help="Path to manifest.yaml.")
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        help="Skill root to scan. Repeatable. Defaults to repo-local roots plus SKILLS_META_ROOTS.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def read_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    raw = text[4:end]
    data = yaml.safe_load(raw)
    return data or {}


def split_roots(repo_root: Path, explicit_roots: list[str]) -> list[Path]:
    roots: list[Path] = [root for root in (repo_root / rel for rel in DEFAULT_ROOTS) if root.exists()]
    env_roots = os.environ.get("SKILLS_META_ROOTS", "").strip()
    if env_roots:
        for chunk in env_roots.split(os.pathsep):
            chunk = chunk.strip()
            if chunk:
                roots.append(Path(chunk).expanduser())

    for root in explicit_roots:
        roots.append(Path(root).expanduser())

    return dedupe_paths(roots)


def dedupe_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    result: list[Path] = []
    for path in paths:
        resolved = str(path.expanduser())
        if resolved not in seen:
            seen.add(resolved)
            result.append(path.expanduser())
    return result


def infer_runtime(repo_root: Path, root: Path) -> str:
    try:
        rel = root.resolve().relative_to(repo_root.resolve())
    except Exception:
        return "configured"
    first = rel.parts[0] if rel.parts else ""
    if first in {"claude", "codex", "gemini", "skills"}:
        return "portable" if first == "skills" else first
    return "configured"


def semver_tuple(value: str | None) -> tuple[int, int, int] | None:
    if not value:
        return None
    match = SEMVER_RE.match(str(value).strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def compare_semver(left: str | None, right: str | None) -> int | None:
    lval = semver_tuple(left)
    rval = semver_tuple(right)
    if lval is None or rval is None:
        return None
    if lval < rval:
        return -1
    if lval > rval:
        return 1
    return 0


def is_date(value: str | None) -> bool:
    return bool(value and DATE_RE.match(value))


def scan_roots(repo_root: Path, roots: list[Path]) -> list[SkillRecord]:
    records: list[SkillRecord] = []
    for root in roots:
        if not root.exists():
            continue
        runtime = infer_runtime(repo_root, root)
        for skill_md in root.rglob("SKILL.md"):
            frontmatter = read_frontmatter(skill_md)
            name = str(frontmatter.get("name") or skill_md.parent.name)
            version = frontmatter.get("version")
            last_updated = frontmatter.get("last-updated")
            description = frontmatter.get("description")
            records.append(
                SkillRecord(
                    name=name,
                    path=skill_md,
                    root=root,
                    runtime=runtime,
                    version=str(version) if version is not None else None,
                    last_updated=str(last_updated) if last_updated is not None else None,
                    description=str(description) if description is not None else None,
                )
            )
    return records


def entry_aliases(key: str, entry: dict[str, Any]) -> set[str]:
    aliases = {str(key)}
    repo_path = entry.get("repo_path")
    if repo_path:
        aliases.add(Path(str(repo_path)).name)
    return {alias for alias in aliases if alias}


def canonical_name(key: str, entry: dict[str, Any]) -> str:
    repo_path = entry.get("repo_path")
    if repo_path:
        return Path(str(repo_path)).name
    return str(key)


def annotate_records(records: list[SkillRecord], manifest: dict[str, Any]) -> tuple[list[SkillRecord], list[str]]:
    active = manifest.get("skills", {}) or {}
    planned = manifest.get("planned_skills", {}) or {}
    active_lookup: dict[str, dict[str, Any]] = {}
    canonical_active: list[str] = []
    for key, entry in active.items():
        canonical = canonical_name(str(key), entry or {})
        canonical_active.append(canonical)
        for alias in entry_aliases(str(key), entry or {}):
            active_lookup[alias] = entry
    missing: list[str] = []

    for record in records:
        record.manifest = active_lookup.get(record.name)
        record.planned = planned.get(record.name)
        if record.manifest:
            canonical = str(record.manifest.get("canonical_version") or "")
            if not record.version:
                record.issues.append("missing-version")
            else:
                cmp = compare_semver(record.version, canonical)
                if cmp is None:
                    record.issues.append("unparseable-version")
                elif cmp < 0:
                    record.issues.append(f"behind-canonical:{canonical}")
                elif cmp > 0:
                    record.issues.append(f"ahead-of-canonical:{canonical}")

            manifest_updated = str(record.manifest.get("last_updated") or "")
            if not record.last_updated:
                record.issues.append("missing-last-updated")
            elif is_date(record.last_updated) and manifest_updated and record.last_updated < manifest_updated:
                record.issues.append(f"stale-last-updated:{manifest_updated}")
            elif not is_date(record.last_updated):
                record.issues.append("unparseable-last-updated")
        else:
            if record.planned:
                record.issues.append("planned-only")
            else:
                record.issues.append("missing-from-manifest")

    seen = {record.name for record in records}
    for name in canonical_active:
        if name not in seen:
            missing.append(name)

    return records, missing


def render_fix(record: SkillRecord) -> str:
    canonical_version = record.version
    if record.manifest:
        canonical_version = str(record.manifest.get("canonical_version") or record.version or "")
    fixed = {
        "name": record.name,
        "version": canonical_version or record.version or "1.0.0",
        "last-updated": date.today().isoformat(),
        "description": record.description or "Short description.",
    }
    return "\n".join(
        [
            "Suggested frontmatter",
            "---",
            f"name: {fixed['name']}",
            f"version: {fixed['version']}",
            f"last-updated: {fixed['last-updated']}",
            f"description: {fixed['description']}",
            "---",
        ]
    )


def text_output(records: list[SkillRecord], missing: list[str], mode: str, skill: str | None) -> str:
    lines: list[str] = []
    if mode == "single" and records:
        record = records[0]
        lines.append(f"{record.name}")
        lines.append(f"path: {record.path}")
        lines.append(f"installed: v{record.version or 'missing'}")
        if record.manifest:
            lines.append(f"canonical:  v{record.manifest.get('canonical_version')}")
            lines.append(f"runtime:    {record.manifest.get('runtime', record.runtime)}")
        else:
            lines.append("canonical:  not in manifest.skills")
            if record.planned:
                lines.append("manifest:   planned only")
        lines.append(f"last-updated: {record.last_updated or 'missing'}")
        lines.append(f"status: {record.render_status()}")
        if record.issues:
            lines.append("issues: " + ", ".join(record.issues))
        return "\n".join(lines)

    total = len(records)
    drifted = sum(1 for record in records if record.render_status() != "ok")
    lines.append(f"skills-meta {mode}")
    lines.append(f"skills scanned: {total}")
    lines.append(f"drifted: {drifted}")
    if missing:
        lines.append(f"manifest missing locally: {len(missing)}")
    lines.append("")

    shown = 0
    for record in records:
        if mode == "drift" and record.render_status() == "ok":
            continue
        if mode == "inventory" and shown >= 12:
            break
        if mode == "fix" and record.render_status() == "ok":
            continue
        status = record.render_status()
        canonical = f"  canonical {record.manifest.get('canonical_version')}" if record.manifest else ""
        updated = record.last_updated or "missing"
        lines.append(
            f"{status:<7} {record.name:<18} v{record.version or 'missing'}  {updated}  {record.path}{canonical}"
        )
        shown += 1

    omitted = total - shown if mode == "inventory" else 0
    if omitted > 0:
        lines.append(f"... {omitted} more")

    if missing:
        lines.append("")
        lines.append("missing locally:")
        for name in missing[:12]:
            lines.append(f"- {name}")
        if len(missing) > 12:
            lines.append(f"- ... {len(missing) - 12} more")

    if mode == "fix" and records:
        lines.append("")
        lines.append(render_fix(records[0]))

    return "\n".join(lines)


def json_output(records: list[SkillRecord], missing: list[str], mode: str) -> str:
    payload = {
        "mode": mode,
        "records": [
            {
                "name": record.name,
                "path": str(record.path),
                "root": str(record.root),
                "runtime": record.runtime,
                "version": record.version,
                "last_updated": record.last_updated,
                "status": record.render_status(),
                "issues": record.issues,
                "manifest": record.manifest,
                "planned": record.planned,
            }
            for record in records
        ],
        "missing": missing,
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def filter_records(records: list[SkillRecord], skill: str | None) -> list[SkillRecord]:
    if not skill:
        return records
    matches = [record for record in records if record.name == skill or record.path.parent.name == skill]
    return matches


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    manifest = load_yaml((repo_root / args.manifest).resolve())
    roots = split_roots(repo_root, args.root)
    records = scan_roots(repo_root, roots)
    records, missing = annotate_records(records, manifest)
    records = filter_records(records, args.skill)

    if args.mode in {"single", "fix"} and not args.skill:
        print("--skill is required for single and fix mode", file=sys.stderr)
        return 2
    if args.skill and not records:
        print(f"skill not found: {args.skill}", file=sys.stderr)
        return 1
    if args.json:
        print(json_output(records, missing, args.mode))
    else:
        print(text_output(records, missing, args.mode, args.skill))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
