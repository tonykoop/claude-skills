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

try:
    import yaml
except ImportError:  # pragma: no cover - exercised on hosts without PyYAML.
    yaml = None

DEFAULT_ROOTS = ("skills", "claude/skills", "codex/skills", "gemini/skills")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
OBSOLETE_STATUSES = {"deprecated", "obsolete", "retired"}


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
    changelog_path: Path | None = None
    manifest: dict[str, Any] | None = None
    planned: dict[str, Any] | None = None
    issues: list[str] = field(default_factory=list)
    duplicate_of: str | None = None  # name of the record chosen as canonical copy

    def render_status(self) -> str:
        if self.duplicate_of:
            return "duplicate"
        manifest_status = str((self.manifest or {}).get("status") or "").strip().lower()
        if manifest_status in OBSOLETE_STATUSES:
            return manifest_status
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
        "--version",
        action="store_true",
        help="Print the skills-meta version and exit. Uses manifest canonical_version when available.",
    )
    parser.add_argument(
        "--mode",
        choices=("inventory", "single", "drift", "fix", "fix-duplicates", "sync"),
        default="inventory",
    )
    parser.add_argument(
        "--skill",
        help="Skill name to focus on. In single/fix modes one skill; in sync mode "
        "a comma-separated list (default: all manifest skills).",
    )
    parser.add_argument("--manifest", default="manifest.yaml", help="Path to manifest.yaml.")
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        help="Skill root to scan. Repeatable. Defaults to repo-local roots plus SKILLS_META_ROOTS.",
    )
    parser.add_argument(
        "--target",
        help="In sync mode, the install root to copy into (e.g. ~/.codex/skills). Required for sync.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform side effects. In fix-duplicates mode, prompt y/n per stale copy "
        "and delete on confirmation. In sync mode, copy missing skills (and overwrite "
        "drifted ones when combined with --force). Without --apply, prints a dry-run only.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="In sync --apply, overwrite a target that has drifted from the canonical source. "
        "Without --force, drifted targets are reported and skipped to protect local edits.",
    )
    parser.add_argument("--strict", action="store_true", help="Exit 1 when drift or missing manifest skills are found.")
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = parse_yaml(path.read_text(encoding="utf-8"))
    return data or {}


def parse_yaml(text: str) -> dict[str, Any]:
    if yaml is not None:
        data = yaml.safe_load(text)
        return data or {}
    return parse_simple_yaml(text)


def parse_simple_yaml(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    data, _ = parse_mapping(lines, 0, 0)
    return data


def parse_mapping(lines: list[str], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped == "---":
            index += 1
            continue
        current_indent = len(raw_line) - len(raw_line.lstrip(" "))
        if current_indent < indent:
            break
        if current_indent > indent:
            index += 1
            continue
        if ":" not in stripped:
            index += 1
            continue

        key, raw_value = stripped.split(":", 1)
        value = raw_value.strip()
        if not value:
            next_item = next_content_line(lines, index + 1)
            if next_item and next_item[1] >= indent + 2 and next_item[2].startswith("-"):
                child, index = parse_sequence(lines, index + 1, indent + 2)
            else:
                child, index = parse_mapping(lines, index + 1, indent + 2)
            result[key.strip()] = child
            continue
        if value.startswith((">", "|")):
            block, index = parse_block_scalar(lines, index + 1, current_indent)
            result[key.strip()] = block
            continue
        result[key.strip()] = parse_scalar(value)
        index += 1
    return result, index


def next_content_line(lines: list[str], index: int) -> tuple[int, int, str] | None:
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        if stripped and not stripped.startswith("#") and stripped != "---":
            return index, len(raw_line) - len(raw_line.lstrip(" ")), stripped
        index += 1
    return None


def parse_sequence(lines: list[str], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped == "---":
            index += 1
            continue
        current_indent = len(raw_line) - len(raw_line.lstrip(" "))
        if current_indent < indent:
            break
        if current_indent > indent:
            index += 1
            continue
        if not stripped.startswith("-"):
            break

        value = stripped[1:].strip()
        if not value:
            child, index = parse_mapping(lines, index + 1, indent + 2)
            result.append(child)
            continue
        result.append(parse_scalar(value))
        index += 1
    return result, index


def parse_block_scalar(lines: list[str], index: int, parent_indent: int) -> tuple[str, int]:
    chunks: list[str] = []
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        current_indent = len(raw_line) - len(raw_line.lstrip(" "))
        if stripped and current_indent <= parent_indent:
            break
        chunks.append(stripped)
        index += 1
    return " ".join(chunk for chunk in chunks if chunk), index


def parse_scalar(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(chunk.strip()) for chunk in inner.split(",")]
    if len(value) >= 2 and value[0] in {"'", '"'} and value[-1] == value[0]:
        return value[1:-1]
    return value


def normalize_requires(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        if raw.startswith("[") and raw.endswith("]"):
            raw = raw[1:-1].strip()
        if not raw:
            return []
        return [chunk.strip().strip("'\"") for chunk in raw.split(",") if chunk.strip()]
    return [str(value).strip()] if str(value).strip() else []


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
    data = parse_yaml(raw)
    return data or {}


def installed_skill_frontmatter() -> dict[str, Any]:
    """Read this helper's bundled SKILL.md without depending on cwd."""
    skill_md = Path(__file__).resolve().parents[1] / "SKILL.md"
    try:
        return read_frontmatter(skill_md)
    except OSError:
        return {}


def render_version(manifest: dict[str, Any]) -> str:
    """Render a stable version probe for sprint-manager preflight checks."""
    frontmatter = installed_skill_frontmatter()
    name = str(frontmatter.get("name") or "skills-meta")
    installed = str(frontmatter.get("version") or "unknown")
    manifest_entry = (manifest.get("skills", {}) or {}).get(name) or {}
    canonical = manifest_entry.get("canonical_version")
    if canonical:
        return f"{name} {canonical} (installed {installed})"
    return f"{name} {installed}"


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
        key = str(spec.path.expanduser().resolve(strict=False))
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


def changelog_for(skill_md: Path) -> Path | None:
    path = skill_md.parent / "CHANGELOG.md"
    return path if path.exists() else None


def changelog_mentions_version(path: Path, version: str | None) -> bool:
    if not version:
        return True
    text = path.read_text(encoding="utf-8")
    return version in text or f"v{version}" in text


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
        changelog_path = changelog_for(skill_md)
        records.append(
            SkillRecord(
                name=name,
                path=skill_md,
                root=spec.path,
                runtime=runtime,
                version=str(version) if version is not None else None,
                last_updated=str(last_updated) if last_updated is not None else None,
                description=str(description) if description is not None else None,
                changelog_path=changelog_path,
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
    return str(key)


def append_issue(record: SkillRecord, issue: str) -> bool:
    if issue in record.issues:
        return False
    record.issues.append(issue)
    return True


def annotate_records(records: list[SkillRecord], manifest: dict[str, Any]) -> tuple[list[SkillRecord], list[str]]:
    active = manifest.get("skills", {}) or {}
    planned = manifest.get("planned_skills", {}) or {}
    active_lookup: dict[str, dict[str, Any]] = {}
    canonical_lookup: dict[str, dict[str, Any]] = {}
    dependency_lookup: dict[str, str] = {}
    canonical_active: list[str] = []
    for key, entry in active.items():
        canonical = canonical_name(str(key), entry or {})
        canonical_active.append(canonical)
        canonical_lookup[canonical] = entry or {}
        for alias in entry_aliases(str(key), entry or {}):
            active_lookup[alias] = entry
            dependency_lookup[alias] = canonical
    missing: list[str] = []

    for record in records:
        record.manifest = active_lookup.get(record.name)
        record.planned = planned.get(record.name)
        if record.manifest:
            manifest_status = str(record.manifest.get("status") or "").strip().lower()
            if manifest_status in OBSOLETE_STATUSES:
                append_issue(record, f"cleanup-candidate:{manifest_status}")
            canonical = str(record.manifest.get("canonical_version") or "")
            if not record.version:
                append_issue(record, "missing-version")
            else:
                cmp = compare_semver(record.version, canonical)
                if cmp is None:
                    append_issue(record, "unparseable-version")
                elif cmp < 0:
                    append_issue(record, f"behind-canonical:{canonical}")
                elif cmp > 0:
                    append_issue(record, f"ahead-of-canonical:{canonical}")

            manifest_updated = str(record.manifest.get("last_updated") or "")
            if not record.last_updated:
                append_issue(record, "missing-last-updated")
            elif not is_date(record.last_updated):
                append_issue(record, "unparseable-last-updated")
            elif manifest_updated and record.last_updated < manifest_updated:
                append_issue(record, f"stale-last-updated:{manifest_updated}")
            elif manifest_updated and record.last_updated > manifest_updated:
                append_issue(record, f"manifest-last-updated-stale:{record.last_updated}")

            if not record.changelog_path:
                append_issue(record, "missing-changelog")
            elif not changelog_mentions_version(record.changelog_path, canonical):
                append_issue(record, f"changelog-missing-version:{canonical}")
        else:
            if record.planned:
                append_issue(record, "planned-only")
            else:
                append_issue(record, "missing-from-manifest")

    installed_by_name: dict[str, list[SkillRecord]] = {}
    for record in records:
        installed_by_name.setdefault(record.name, []).append(record)
        path_canonical = dependency_lookup.get(record.path.parent.name)
        if path_canonical and path_canonical != record.name:
            installed_by_name.setdefault(path_canonical, []).append(record)

    while True:
        changed = False
        for record in records:
            if not record.manifest:
                continue
            for required in normalize_requires(record.manifest.get("requires")):
                required_name = dependency_lookup.get(required)
                if required_name is None or required_name not in canonical_lookup:
                    changed |= append_issue(record, f"unknown-required:{required}")
                    continue
                required_records = installed_by_name.get(required_name, [])
                if not required_records:
                    changed |= append_issue(record, f"missing-required:{required_name}")
                    continue
                if not any(not required_record.issues for required_record in required_records):
                    changed |= append_issue(record, f"required-drift:{required_name}")
        if not changed:
            break

    seen = {record.name for record in records}
    for name in canonical_active:
        if name not in seen:
            entry = active_lookup.get(name) or {}
            status = str(entry.get("status") or "").strip().lower()
            if status not in OBSOLETE_STATUSES:
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


def canonicalness_key(repo_root: Path, group: list[SkillRecord]) -> "callable[[SkillRecord], tuple]":
    """Return a sort key (descending) that mirrors pick_canonical_copy's
    precedence: manifest repo_path match > highest semver > newest
    last-updated > path string. Path string is the final tiebreaker so
    the order is fully deterministic across runs and machines.
    """
    manifest_entry = next((r.manifest for r in group if r.manifest), None)
    repo_path_hint: str | None = None
    if manifest_entry:
        repo_path = manifest_entry.get("repo_path")
        if repo_path:
            try:
                repo_path_hint = str((repo_root / str(repo_path)).resolve())
            except OSError:
                repo_path_hint = None

    def key(record: SkillRecord) -> tuple:
        try:
            is_repo_path = repo_path_hint is not None and str(record.path.parent.resolve()) == repo_path_hint
        except OSError:
            is_repo_path = False
        sv = semver_tuple(record.version) or (-1, -1, -1)
        date_val = record.last_updated if is_date(record.last_updated) else ""
        return (1 if is_repo_path else 0, sv, date_val, str(record.path))

    return key


def pick_canonical_copy(repo_root: Path, group: list[SkillRecord]) -> SkillRecord:
    return max(group, key=canonicalness_key(repo_root, group))


def canonical_copy_reason(repo_root: Path, canonical: SkillRecord, group: list[SkillRecord]) -> str:
    """Explain why this copy wins, using the same precedence as the picker."""
    manifest_entry = next((r.manifest for r in group if r.manifest), None)
    repo_path = manifest_entry.get("repo_path") if manifest_entry else None
    if repo_path:
        try:
            if canonical.path.parent.resolve() == (repo_root / str(repo_path)).resolve():
                return "manifest repo_path"
        except OSError:
            pass

    versions = [semver_tuple(r.version) for r in group]
    canonical_version = semver_tuple(canonical.version)
    if canonical_version is not None and canonical_version == max((v for v in versions if v is not None), default=None):
        return "highest semver"

    dates = [r.last_updated for r in group if is_date(r.last_updated)]
    if canonical.last_updated and dates and canonical.last_updated == max(dates):
        return "newest last-updated"

    return "stable first-seen fallback"


def sort_canonical_first(repo_root: Path, records: list[SkillRecord]) -> list[SkillRecord]:
    """Stable sort with the canonical copy first; used so single-mode
    output is deterministic in duplicate-heavy installs."""
    if len(records) <= 1:
        return list(records)
    key = canonicalness_key(repo_root, records)
    return sorted(records, key=key, reverse=True)


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


def render_duplicate_warnings(repo_root: Path, duplicates: dict[str, list[SkillRecord]]) -> list[str]:
    if not duplicates:
        return []
    lines = ["", f"duplicate warnings: {len(duplicates)}"]
    for name, group in sorted(duplicates.items())[:8]:
        canonical = next((r for r in group if not r.duplicate_of), group[0])
        reason = canonical_copy_reason(repo_root, canonical, group)
        lines.append(f"- {name}: keep {canonical.path.parent} ({reason}); cleanup candidates: {len(group) - 1}")
    if len(duplicates) > 8:
        lines.append(f"- ... {len(duplicates) - 8} more")
    return lines


def text_output(
    repo_root: Path,
    records: list[SkillRecord],
    missing: list[str],
    unreadable: list[UnreadableRoot],
    duplicates: dict[str, list[SkillRecord]],
    mode: str,
    skill: str | None,
) -> str:
    lines: list[str] = []
    if mode == "single" and records:
        # records is already sorted canonical-first by filter_and_sort, so
        # records[0] is deterministic across runs even when the same skill
        # name appears at multiple roots. The remaining copies surface in
        # an "other copies" block so a duplicate-heavy install isn't
        # silently collapsed to a single arbitrary path.
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
        if record.changelog_path:
            lines.append(f"changelog: {record.changelog_path}")
        else:
            lines.append("changelog: missing")
        if len(records) > 1:
            lines.append("")
            lines.append(f"other copies: {len(records) - 1}")
            for extra in records[1:]:
                lines.append(
                    f"- {extra.render_status():<9} v{extra.version or 'missing':<10} "
                    f"{extra.runtime:<10} {extra.path}"
                )
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
        issues = f"  issues: {', '.join(record.issues)}" if record.issues else ""
        lines.append(
            f"{status:<9} {record.name:<18} v{record.version or 'missing'}  {updated}  {record.path}{canonical}{issues}"
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
    lines.extend(render_duplicate_warnings(repo_root, duplicates))

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
                "changelog_path": str(record.changelog_path) if record.changelog_path else None,
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


def filter_and_sort(repo_root: Path, records: list[SkillRecord], skill: str | None) -> list[SkillRecord]:
    matches = filter_records(records, skill)
    return sort_canonical_first(repo_root, matches)


def render_fix_duplicates_plan(repo_root: Path, duplicates: dict[str, list[SkillRecord]]) -> str:
    """Print a human-readable plan: which copy stays, which get removed."""
    if not duplicates:
        return "No duplicates detected."
    lines = ["fix-duplicates plan (dry run)", ""]
    for name, group in sorted(duplicates.items()):
        canonical = next((r for r in group if not r.duplicate_of), group[0])
        reason = canonical_copy_reason(repo_root, canonical, group)
        lines.append(f"# {name}")
        lines.append(
            f"keep:   {canonical.path.parent}  "
            f"(v{canonical.version or 'missing'}, {canonical.runtime}; kept because {reason})"
        )
        for record in group:
            if record is canonical:
                continue
            lines.append(
                f"remove: {record.path.parent}  (v{record.version or 'missing'}, {record.runtime})"
            )
        lines.append("")
    lines.append("Warning: duplicate skill copies can shadow the canonical skill until cleaned up.")
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
            is_link = target.is_symlink()
            link_note = f" (symlink to {os.readlink(target)})" if is_link else ""
            answer = input(f"remove {target}{link_note} ? [y/N] ").strip().lower()
            if answer == "y":
                try:
                    # If the duplicate path is itself a symlink, only
                    # unlink the symlink — never rmtree through it. That
                    # protects the shared source the user pointed it at.
                    if is_link:
                        target.unlink()
                        print(f"  unlinked {target}")
                    else:
                        shutil.rmtree(target)
                        print(f"  removed {target}")
                    removed += 1
                except OSError as exc:
                    print(f"  failed: {exc}", file=sys.stderr)
            else:
                print("  skipped")
    print(f"\nremoved {removed} stale copies")
    return removed


@dataclass
class SyncEntry:
    """One row in a sync plan: copy a canonical skill into a target install root.

    State explains what would happen: `missing` (target absent — safe to copy),
    `in-sync` (byte-for-byte match — skip), `drift` (target has its own edits —
    skip unless --force is set), `source-missing` (manifest entry has no
    repo_path on disk — can't sync).

    `symlink_target` is set when the install path is itself a symlink. We
    refuse to mutate symlinked targets without --force because the user may
    have linked the install path into a working tree on purpose, and a naive
    rmtree would either error out or — worse, in older Pythons — follow the
    link and delete the source.
    """

    name: str
    source: Path
    target: Path
    state: str
    source_runtime: str
    target_runtime: str
    note: str = ""
    symlink_target: Path | None = None


def hash_dir(path: Path) -> str | None:
    """Hash every file under path so we can detect drift cheaply.

    File contents matter; mtimes don't. Returns None if the directory is missing.
    Symlinks are ignored — we never want to follow a symlink into another tree
    during a sync diff.
    """
    import hashlib

    if not path.exists():
        return None
    h = hashlib.sha256()
    for file in sorted(path.rglob("*")):
        if file.is_symlink() or not file.is_file():
            continue
        rel = file.relative_to(path).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        try:
            h.update(file.read_bytes())
        except OSError:
            return None
        h.update(b"\0")
    return h.hexdigest()


def resolve_manifest_repo_path(manifest_dir: Path, repo_path: str) -> Path:
    """Resolve a manifest repo_path from the manifest file's directory."""
    path = Path(repo_path).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (manifest_dir / path).resolve()


def build_sync_plan(
    repo_root: Path,
    manifest_dir_or_manifest: Path | dict[str, Any],
    manifest_or_target: dict[str, Any] | Path,
    target_or_filter: Path | list[str] | None,
    skill_filter: list[str] | None = None,
) -> list[SyncEntry]:
    """For each manifest skill we're asked to sync, classify the target state."""
    if isinstance(manifest_dir_or_manifest, dict):
        manifest_dir = repo_root
        manifest = manifest_dir_or_manifest
        target = manifest_or_target
        skill_filter = target_or_filter  # type: ignore[assignment]
    else:
        manifest_dir = manifest_dir_or_manifest
        manifest = manifest_or_target
        target = target_or_filter

    active = manifest.get("skills", {}) or {}
    expanded_filter = expand_sync_skill_filter(active, skill_filter)
    entries: list[SyncEntry] = []
    for key, raw in active.items():
        entry = raw or {}
        name = canonical_name(str(key), entry)
        aliases = entry_aliases(str(key), entry)
        if expanded_filter and name not in expanded_filter and aliases.isdisjoint(expanded_filter):
            continue
        repo_path = entry.get("repo_path")
        if not repo_path:
            entries.append(
                SyncEntry(
                    name,
                    manifest_dir / str(key),
                    target / name,
                    "source-missing",
                    "configured",
                    infer_runtime(repo_root, target),
                    "no repo_path in manifest",
                )
            )
            continue
        source = resolve_manifest_repo_path(manifest_dir, str(repo_path))
        dest = target / name
        source_runtime = infer_runtime(manifest_dir, source)
        target_runtime = infer_runtime(repo_root, target)
        if not source.exists():
            entries.append(
                SyncEntry(
                    name,
                    source,
                    dest,
                    "source-missing",
                    source_runtime,
                    target_runtime,
                    f"{source} not on disk",
                )
            )
            continue
        symlink_target: Path | None = None
        if dest.is_symlink():
            try:
                symlink_target = Path(os.readlink(dest))
            except OSError:
                symlink_target = Path("?")
        source_hash = hash_dir(source)
        dest_hash = hash_dir(dest)
        if dest_hash is None and not dest.is_symlink():
            entries.append(SyncEntry(name, source, dest, "missing", source_runtime, target_runtime))
        elif source_hash == dest_hash:
            note = f"symlinked to {symlink_target}" if symlink_target else ""
            entries.append(
                SyncEntry(
                    name,
                    source,
                    dest,
                    "in-sync",
                    source_runtime,
                    target_runtime,
                    note,
                    symlink_target=symlink_target,
                )
            )
        else:
            note = (
                f"target is a symlink to {symlink_target}"
                if symlink_target
                else "target has local changes"
            )
            entries.append(
                SyncEntry(
                    name,
                    source,
                    dest,
                    "drift",
                    source_runtime,
                    target_runtime,
                    note,
                    symlink_target=symlink_target,
                )
            )
    return entries


def expand_sync_skill_filter(
    active: dict[str, Any],
    skill_filter: list[str] | None,
) -> set[str] | None:
    """Return requested skills plus transitive manifest `requires` entries.

    A missing filter means "all skills", so there is nothing to expand. When
    the user asks for one skill, sync should carry along its declared
    dependencies instead of silently installing a broken partial set.
    """
    if not skill_filter:
        return None

    alias_to_canonical: dict[str, str] = {}
    entries_by_canonical: dict[str, dict[str, Any]] = {}
    for key, raw in active.items():
        entry = raw or {}
        canonical = canonical_name(str(key), entry)
        entries_by_canonical[canonical] = entry
        for alias in entry_aliases(str(key), entry):
            alias_to_canonical[alias] = canonical

    selected: set[str] = set()
    pending: list[str] = list(skill_filter)
    while pending:
        requested = pending.pop()
        canonical = alias_to_canonical.get(requested, requested)
        if canonical in selected:
            continue
        selected.add(canonical)
        entry = entries_by_canonical.get(canonical)
        if not entry:
            continue
        for required in normalize_requires(entry.get("requires")):
            required_canonical = alias_to_canonical.get(required, required)
            if required_canonical not in selected:
                pending.append(required_canonical)
    return selected


def render_sync_plan(plan: list[SyncEntry], target: Path, apply: bool, force: bool) -> str:
    """One line per skill so it scrolls on a phone."""
    if not plan:
        return f"sync: no manifest skills matched (target {target})"
    lines = [f"sync plan -> {target}", ""]
    counts: dict[str, int] = {}
    for entry in plan:
        counts[entry.state] = counts.get(entry.state, 0) + 1
        marker = {
            "missing": "+ copy   ",
            "in-sync": "= keep   ",
            "drift": "! drift  ",
            "source-missing": "? skip   ",
        }.get(entry.state, "  ?      ")
        suffix = f"  ({entry.note})" if entry.note else ""
        runtime_flow = f"[{entry.source_runtime} -> {entry.target_runtime}]"
        lines.append(
            f"{marker} {entry.name:<22} {runtime_flow:<24} {entry.source}  ->  {entry.target}{suffix}"
        )
    lines.append("")
    summary = ", ".join(f"{state}: {n}" for state, n in sorted(counts.items()))
    lines.append(f"summary: {summary}")
    if not apply:
        lines.append("dry run. Pass --apply to copy missing skills.")
        if any(e.state == "drift" for e in plan):
            lines.append("Drifted targets need --apply --force to overwrite local edits.")
    elif not force and any(e.state == "drift" for e in plan):
        lines.append("--force not set; drifted targets were skipped.")
    return "\n".join(lines)


def _remove_target_path(path: Path) -> None:
    """Remove a path safely without following symlinks.

    `shutil.rmtree` raises on a symlink, and even when it doesn't it would
    descend into whatever the link points at. For sync overwrites we want
    to peel off only the install entry, never the directory it might link
    into. So: if the path is a symlink, unlink it; otherwise rmtree.
    """
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def apply_sync(plan: list[SyncEntry], force: bool) -> tuple[int, int, int]:
    """Returns (copied, overwritten, skipped). Drifted or symlinked
    targets need --force; even with --force we only remove the link
    (not its target) before laying down the fresh copy.
    """
    copied = overwritten = skipped = 0
    for entry in plan:
        if entry.state == "in-sync":
            skipped += 1
            continue
        if entry.state == "source-missing":
            print(f"skip {entry.name}: {entry.note}", file=sys.stderr)
            skipped += 1
            continue
        if entry.symlink_target is not None and not force:
            print(
                f"skip {entry.name}: target is a symlink to {entry.symlink_target} "
                f"(pass --force to replace the link with a real copy)",
                file=sys.stderr,
            )
            skipped += 1
            continue
        if entry.state == "drift" and not force:
            print(f"skip {entry.name}: drifted (pass --force to overwrite)", file=sys.stderr)
            skipped += 1
            continue
        try:
            entry.target.parent.mkdir(parents=True, exist_ok=True)
            existed = entry.target.exists() or entry.target.is_symlink()
            _remove_target_path(entry.target)
            # symlinks=True so source-side symlinks are preserved as
            # symlinks in the install. Flattening them with symlinks=False
            # would silently turn a curated layout into a copy and break
            # any user who symlinks bundled scripts to a shared cache.
            shutil.copytree(entry.source, entry.target, symlinks=True)
            if existed:
                print(f"overwrote {entry.target}")
                overwritten += 1
            else:
                print(f"copied   {entry.target}")
                copied += 1
        except (OSError, shutil.Error) as exc:
            print(f"failed   {entry.name}: {exc}", file=sys.stderr)
            skipped += 1
    print(f"\ncopied {copied}, overwrote {overwritten}, skipped {skipped}")
    return copied, overwritten, skipped


def main() -> int:
    args = parse_args()
    cwd = Path.cwd()
    manifest_path = (cwd / args.manifest).resolve()
    repo_root = manifest_path.parent
    manifest = load_yaml(manifest_path)

    if args.version:
        print(render_version(manifest))
        return 0

    if args.mode == "sync":
        if not args.target:
            print("--target is required for sync mode", file=sys.stderr)
            return 2
        target = Path(args.target).expanduser().resolve()
        skill_filter: list[str] | None = None
        if args.skill:
            skill_filter = [s.strip() for s in args.skill.split(",") if s.strip()]
        plan = build_sync_plan(repo_root, manifest_path.parent, manifest, target, skill_filter)
        if args.json:
            payload = {
                "mode": "sync",
                "target": str(target),
                "force": args.force,
                "apply": args.apply,
                "plan": [
                    {
                        "name": e.name,
                        "source": str(e.source),
                        "target": str(e.target),
                        "source_runtime": e.source_runtime,
                        "target_runtime": e.target_runtime,
                        "state": e.state,
                        "note": e.note,
                    }
                    for e in plan
                ],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0
        print(render_sync_plan(plan, target, args.apply, args.force))
        if args.apply:
            print()
            apply_sync(plan, args.force)
        return 0

    specs = collect_root_specs(repo_root, manifest_path, args.root)
    resolved, unreadable = resolve_skill_dirs(specs)
    records = scan_roots(repo_root, resolved)
    records, missing = annotate_records(records, manifest)
    duplicates = detect_duplicates(repo_root, records)
    records = filter_and_sort(repo_root, records, args.skill)

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
            print(render_fix_duplicates_plan(repo_root, duplicates))
        return 0

    if args.json:
        print(json_output(records, missing, unreadable, duplicates, args.mode))
    else:
        print(text_output(repo_root, records, missing, unreadable, duplicates, args.mode, args.skill))
    if args.strict and (any(record.render_status() != "ok" for record in records) or missing):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
