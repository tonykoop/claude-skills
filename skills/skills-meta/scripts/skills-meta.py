#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
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
class RootSpec:
    """A root to scan, plus where it came from. Origin matters because a missing
    repo-local default is normal, but a missing manifest/env/--root entry is a
    signal worth surfacing (mobile install, unmounted drive, stale config)."""

    path: Path
    origin: str  # "default", "manifest", "env", "cli"


@dataclass
class UnreadableRoot:
    path: Path
    origin: str
    reason: str  # "missing", "not-a-directory", "no-skills-found", "permission-denied"


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
    duplicate_of: str | None = None  # name of the record chosen as canonical copy

    def render_status(self) -> str:
        if self.duplicate_of:
            return "duplicate"
        if self.issues:
            if "missing-from-manifest" in self.issues:
                return "unknown"
            return "drift"
        if self.planned and not self.manifest:
            return "planned"
        return "ok"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit installed skills against manifest.yaml.")
    parser.add_argument(
        "--mode",
        choices=("inventory", "single", "drift", "fix", "fix-duplicates"),
        default="inventory",
    )
    parser.add_argument("--skill", help="Skill name to focus on in single/fix mode.")
    parser.add_argument("--manifest", default="manifest.yaml", help="Path to manifest.yaml.")
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        help="Skill root to scan. Repeatable. Defaults to repo-local roots plus SKILLS_META_ROOTS.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="In fix-duplicates mode, prompt y/n per stale copy and delete on confirmation. "
        "Without --apply, prints a dry-run checklist only.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def flatten_roots(value: Any) -> list[Path]:
    roots: list[Path] = []
    if isinstance(value, dict):
        for subvalue in value.values():
            roots.extend(flatten_roots(subvalue))
    elif isinstance(value, list):
        for item in value:
            roots.extend(flatten_roots(item))
    elif isinstance(value, str):
        roots.append(Path(value).expanduser())
    return roots


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


def collect_root_specs(repo_root: Path, manifest_path: Path, explicit_roots: list[str]) -> list[RootSpec]:
    """Gather every root the user has told us about, tagged with provenance.

    We keep all four origins distinct so the report can call out manifest/env/cli
    paths that don't exist on this machine — those are the ones a user most
    wants to see (e.g. a mobile install, an unmounted drive, a stale config).
    Missing repo-local defaults are normal and stay quiet.
    """
    specs: list[RootSpec] = []
    for rel in DEFAULT_ROOTS:
        specs.append(RootSpec(path=(repo_root / rel), origin="default"))

    manifest = load_yaml(manifest_path)
    for path in flatten_roots(manifest.get("install_roots", {})):
        specs.append(RootSpec(path=path, origin="manifest"))

    env_roots = os.environ.get("SKILLS_META_ROOTS", "").strip()
    if env_roots:
        for chunk in env_roots.split(os.pathsep):
            chunk = chunk.strip()
            if chunk:
                specs.append(RootSpec(path=Path(chunk).expanduser(), origin="env"))

    for root in explicit_roots:
        specs.append(RootSpec(path=Path(root).expanduser(), origin="cli"))

    return dedupe_specs(specs)


def dedupe_specs(specs: list[RootSpec]) -> list[RootSpec]:
    """Dedupe by resolved path; keep the highest-priority origin (cli > env > manifest > default)."""
    priority = {"cli": 3, "env": 2, "manifest": 1, "default": 0}
    by_path: dict[str, RootSpec] = {}
    for spec in specs:
        key = str(spec.path.expanduser())
        existing = by_path.get(key)
        if existing is None or priority[spec.origin] > priority[existing.origin]:
            by_path[key] = RootSpec(path=Path(key), origin=spec.origin)
    return list(by_path.values())


def resolve_skill_dirs(specs: list[RootSpec]) -> tuple[list[tuple[Path, RootSpec]], list[UnreadableRoot]]:
    """Walk each root and return (skill_dir, originating_spec) pairs.

    Roots may be (a) a skill directory containing SKILL.md, (b) a container
    with a `skills/` subdir, or (c) a container whose direct children are
    skill directories. Anything we can't read or that yields zero skills gets
    an UnreadableRoot record — but only if the user opted in (manifest/env/cli).
    Missing default repo roots stay silent.
    """
    resolved: list[tuple[Path, RootSpec]] = []
    unreadable: list[UnreadableRoot] = []
    seen_dirs: set[str] = set()

    def add(path: Path, spec: RootSpec) -> None:
        key = str(path.expanduser())
        if key in seen_dirs:
            return
        seen_dirs.add(key)
        resolved.append((Path(key), spec))

    for spec in specs:
        root = spec.path
        try:
            exists = root.exists()
        except PermissionError:
            if spec.origin != "default":
                unreadable.append(UnreadableRoot(root, spec.origin, "permission-denied"))
            continue

        if not exists:
            if spec.origin != "default":
                unreadable.append(UnreadableRoot(root, spec.origin, "missing"))
            continue

        if not root.is_dir():
            if spec.origin != "default":
                unreadable.append(UnreadableRoot(root, spec.origin, "not-a-directory"))
            continue

        # Case (a): root itself is a skill.
        if (root / "SKILL.md").exists():
            add(root, spec)
            continue

        # Case (b)/(c): walk the container.
        container = root / "skills" if (root / "skills").exists() else root
        try:
            children = sorted(container.iterdir())
        except PermissionError:
            if spec.origin != "default":
                unreadable.append(UnreadableRoot(root, spec.origin, "permission-denied"))
            continue

        added_any = False
        for child in children:
            if child.is_dir() and (child / "SKILL.md").exists():
                add(child, spec)
                added_any = True

        if not added_any and spec.origin != "default":
            unreadable.append(UnreadableRoot(root, spec.origin, "no-skills-found"))

    return resolved, unreadable


def infer_runtime(repo_root: Path, root: Path) -> str:
    lowered_parts = {part.lower() for part in root.parts}
    if ".claude" in lowered_parts:
        return "claude"
    if ".codex" in lowered_parts:
        return "codex"
    if ".gemini" in lowered_parts:
        return "gemini"
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


def scan_roots(repo_root: Path, resolved: list[tuple[Path, RootSpec]]) -> list[SkillRecord]:
    records: list[SkillRecord] = []
    for skill_dir, spec in resolved:
        runtime = infer_runtime(repo_root, skill_dir)
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        try:
            frontmatter = read_frontmatter(skill_md)
        except (PermissionError, OSError):
            continue
        name = str(frontmatter.get("name") or skill_md.parent.name)
        version = frontmatter.get("version")
        last_updated = frontmatter.get("last-updated")
        description = frontmatter.get("description")
        records.append(
            SkillRecord(
                name=name,
                path=skill_md,
                root=spec.path,
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


def detect_duplicates(repo_root: Path, records: list[SkillRecord]) -> dict[str, list[SkillRecord]]:
    """Group records by skill name; return groups with more than one entry.

    For each duplicate group, pick a "canonical copy" — the install we'd
    keep if the user ran fix-duplicates. Order of preference:
      1. The path matching the manifest's repo_path (the source of truth).
      2. The highest installed semver.
      3. The newest last-updated date.
      4. The first record (stable fallback).

    We mark every other record in the group with `duplicate_of = canonical.name`
    and append a `duplicate-of-<path>` issue tag so reports stay readable.
    """
    groups: dict[str, list[SkillRecord]] = {}
    for record in records:
        groups.setdefault(record.name, []).append(record)

    dup_groups: dict[str, list[SkillRecord]] = {}
    for name, group in groups.items():
        if len(group) < 2:
            continue
        canonical = pick_canonical_copy(repo_root, group)
        for record in group:
            if record is canonical:
                continue
            record.duplicate_of = name
            record.issues.append(f"duplicate-of:{canonical.path}")
        dup_groups[name] = group
    return dup_groups


def pick_canonical_copy(repo_root: Path, group: list[SkillRecord]) -> SkillRecord:
    manifest_entry = next((r.manifest for r in group if r.manifest), None)
    repo_path_hint: str | None = None
    if manifest_entry:
        repo_path = manifest_entry.get("repo_path")
        if repo_path:
            repo_path_hint = str((repo_root / str(repo_path)).resolve())

    if repo_path_hint:
        for record in group:
            try:
                if str(record.path.parent.resolve()) == repo_path_hint:
                    return record
            except OSError:
                continue

    def sort_key(record: SkillRecord) -> tuple:
        sv = semver_tuple(record.version) or (-1, -1, -1)
        date_val = record.last_updated if is_date(record.last_updated) else ""
        return (sv, date_val)

    return max(group, key=sort_key)


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


def render_unreadable(unreadable: list[UnreadableRoot]) -> list[str]:
    if not unreadable:
        return []
    lines = ["", f"unreadable roots: {len(unreadable)}"]
    for entry in unreadable[:12]:
        lines.append(f"- {entry.origin:<8} {entry.reason:<18} {entry.path}")
    if len(unreadable) > 12:
        lines.append(f"- ... {len(unreadable) - 12} more")
    return lines


def text_output(
    records: list[SkillRecord],
    missing: list[str],
    unreadable: list[UnreadableRoot],
    duplicates: dict[str, list[SkillRecord]],
    mode: str,
    skill: str | None,
) -> str:
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
    drifted = sum(1 for record in records if record.render_status() not in {"ok", "duplicate"})
    dup_count = sum(1 for record in records if record.duplicate_of)
    lines.append(f"skills-meta {mode}")
    lines.append(f"skills scanned: {total}")
    lines.append(f"drifted: {drifted}")
    if dup_count:
        lines.append(f"duplicates: {dup_count} (across {len(duplicates)} skills)")
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
            f"{status:<9} {record.name:<18} v{record.version or 'missing'}  {updated}  {record.path}{canonical}"
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

    lines.extend(render_unreadable(unreadable))

    if mode == "fix" and records:
        lines.append("")
        lines.append(render_fix(records[0]))

    return "\n".join(lines)


def _json_safe(value: Any) -> Any:
    """Coerce values that survive yaml.safe_load (date, datetime, Path)
    into JSON-serializable forms. The manifest's `last_updated: 2026-05-08`
    parses as a datetime.date and would otherwise blow up json.dumps."""
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, (Path,)):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def json_output(
    records: list[SkillRecord],
    missing: list[str],
    unreadable: list[UnreadableRoot],
    duplicates: dict[str, list[SkillRecord]],
    mode: str,
) -> str:
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
                "manifest": _json_safe(record.manifest),
                "planned": _json_safe(record.planned),
                "duplicate_of": record.duplicate_of,
            }
            for record in records
        ],
        "missing": missing,
        "unreadable": [
            {"path": str(u.path), "origin": u.origin, "reason": u.reason}
            for u in unreadable
        ],
        "duplicate_groups": {
            name: [str(r.path) for r in group]
            for name, group in duplicates.items()
        },
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def filter_records(records: list[SkillRecord], skill: str | None) -> list[SkillRecord]:
    if not skill:
        return records
    matches = [record for record in records if record.name == skill or record.path.parent.name == skill]
    return matches


def render_fix_duplicates_plan(duplicates: dict[str, list[SkillRecord]]) -> str:
    """Print a human-readable plan: which copy stays, which get removed."""
    if not duplicates:
        return "No duplicates detected."
    lines = ["fix-duplicates plan (dry run)", ""]
    for name, group in sorted(duplicates.items()):
        canonical = next((r for r in group if not r.duplicate_of), group[0])
        lines.append(f"# {name}")
        lines.append(f"keep:   {canonical.path.parent}  (v{canonical.version or 'missing'}, {canonical.runtime})")
        for record in group:
            if record is canonical:
                continue
            lines.append(
                f"remove: {record.path.parent}  (v{record.version or 'missing'}, {record.runtime})"
            )
        lines.append("")
    lines.append("Run with --apply to confirm each removal interactively.")
    return "\n".join(lines)


def apply_fix_duplicates(duplicates: dict[str, list[SkillRecord]]) -> int:
    """Interactive y/n per stale copy; rmtree on yes. Returns number removed."""
    if not duplicates:
        print("No duplicates detected.")
        return 0
    if not sys.stdin.isatty():
        print(
            "fix-duplicates --apply needs an interactive terminal. "
            "Run from a real shell, not a script.",
            file=sys.stderr,
        )
        return 0
    removed = 0
    for name, group in sorted(duplicates.items()):
        canonical = next((r for r in group if not r.duplicate_of), group[0])
        print(f"\n# {name}")
        print(f"keep: {canonical.path.parent}")
        for record in group:
            if record is canonical:
                continue
            target = record.path.parent
            answer = input(f"remove {target} ? [y/N] ").strip().lower()
            if answer == "y":
                try:
                    shutil.rmtree(target)
                    print(f"  removed {target}")
                    removed += 1
                except OSError as exc:
                    print(f"  failed: {exc}", file=sys.stderr)
            else:
                print("  skipped")
    print(f"\nremoved {removed} stale copies")
    return removed


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    manifest_path = (repo_root / args.manifest).resolve()
    manifest = load_yaml(manifest_path)
    specs = collect_root_specs(repo_root, manifest_path, args.root)
    resolved, unreadable = resolve_skill_dirs(specs)
    records = scan_roots(repo_root, resolved)
    records, missing = annotate_records(records, manifest)
    duplicates = detect_duplicates(repo_root, records)
    records = filter_records(records, args.skill)

    if args.mode in {"single", "fix"} and not args.skill:
        print("--skill is required for single and fix mode", file=sys.stderr)
        return 2
    if args.skill and not records:
        print(f"skill not found: {args.skill}", file=sys.stderr)
        return 1

    if args.mode == "fix-duplicates":
        if args.json:
            print(json_output(records, missing, unreadable, duplicates, args.mode))
            return 0
        if args.apply:
            apply_fix_duplicates(duplicates)
        else:
            print(render_fix_duplicates_plan(duplicates))
        return 0

    if args.json:
        print(json_output(records, missing, unreadable, duplicates, args.mode))
    else:
        print(text_output(records, missing, unreadable, duplicates, args.mode, args.skill))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
