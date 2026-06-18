#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import py_compile
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
}


@dataclass
class CheckResult:
    name: str
    path: str
    status: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Studio Release validation and stage an approve/deploy bundle."
    )
    parser.add_argument("--source", required=True, help="Release candidate file or directory.")
    parser.add_argument(
        "--staging-root",
        default="dist/studio-release",
        help="Directory where a new staging bundle will be written.",
    )
    parser.add_argument("--ticket-title", required=True, help="Human approve/deploy ticket title.")
    parser.add_argument("--ref", default="", help="Issue, PR, branch, or sprint ref.")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Record dirty source state as a warning instead of failing.",
    )
    return parser.parse_args()


def iter_files(source: Path) -> list[Path]:
    if source.is_file():
        return [source]
    files: list[Path] = []
    for path in source.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def check_markdown(path: Path, root: Path) -> CheckResult:
    name = "markdown-lint"
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return CheckResult(name, rel(path, root), "fail", f"not valid UTF-8: {exc}")
    if not text.strip():
        return CheckResult(name, rel(path, root), "fail", "file is empty")
    for idx, line in enumerate(text.splitlines(), start=1):
        if "\t" in line:
            return CheckResult(name, rel(path, root), "fail", f"tab character on line {idx}")
        if line.rstrip(" ") != line:
            return CheckResult(name, rel(path, root), "fail", f"trailing whitespace on line {idx}")
    return CheckResult(name, rel(path, root), "pass", "markdown hygiene passed")


def check_python(path: Path, root: Path) -> CheckResult:
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as exc:
        return CheckResult("python-compile", rel(path, root), "fail", str(exc))
    return CheckResult("python-compile", rel(path, root), "pass", "py_compile passed")


def check_shell(path: Path, root: Path) -> CheckResult:
    bash = shutil.which("bash")
    if not bash:
        return CheckResult("shell-syntax", rel(path, root), "skip", "bash not found")
    result = subprocess.run(
        [bash, "-n", str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip() or f"exit {result.returncode}"
        return CheckResult("shell-syntax", rel(path, root), "fail", detail)
    return CheckResult("shell-syntax", rel(path, root), "pass", "bash -n passed")


def check_source_state(source: Path, allow_dirty: bool) -> CheckResult:
    root = source if source.is_dir() else source.parent
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--short"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return CheckResult("git-state", source.as_posix(), "skip", "not inside a git checkout")
    if result.stdout.strip():
        status = "warn" if allow_dirty else "fail"
        detail = "source checkout has uncommitted changes"
        return CheckResult("git-state", source.as_posix(), status, detail)
    return CheckResult("git-state", source.as_posix(), "pass", "source checkout clean")


def run_checks(source: Path, allow_dirty: bool) -> list[CheckResult]:
    root = source if source.is_dir() else source.parent
    checks = [check_source_state(source, allow_dirty)]
    for path in iter_files(source):
        suffix = path.suffix.lower()
        if suffix == ".md":
            checks.append(check_markdown(path, root))
        elif suffix == ".py":
            checks.append(check_python(path, root))
        elif suffix == ".sh":
            checks.append(check_shell(path, root))
    return checks


def bundle_slug(title: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in title).strip("-")
    return "-".join(part for part in slug.split("-") if part)[:80] or "studio-release"


def copy_source(source: Path, target: Path) -> None:
    if source.is_dir():
        def ignore(_dir: str, names: list[str]) -> set[str]:
            return {name for name in names if name in EXCLUDED_DIRS}

        shutil.copytree(source, target, ignore=ignore)
        return
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target / source.name)


def write_ticket(path: Path, title: str, ref: str, decision: str, checks: list[CheckResult]) -> None:
    failed = [check for check in checks if check.status == "fail"]
    warnings = [check for check in checks if check.status == "warn"]
    lines = [
        f"# {title}",
        "",
        "## Review Evidence",
        "",
        "Type: skill",
        "",
        "Changed behavior:",
        "- Staged a release candidate for human approve/deploy review.",
        "",
        "Validation run:",
        f"- Studio Release gate decision: `{decision}`.",
    ]
    if ref:
        lines.append(f"- Reference: `{ref}`.")
    for check in checks:
        lines.append(f"- {check.name} `{check.path}`: {check.status} - {check.detail}")
    lines.extend(
        [
            "",
            "Known gaps:",
            "- Human reviewer approval is still required before deploy.",
            "",
            "Reviewer should check:",
            "- Confirm the staged source is the intended release candidate.",
            "- Confirm failed or warning checks are resolved or explicitly accepted.",
            "",
            "Do not merge until:",
            "- The approve/deploy reviewer signs off on the staged bundle.",
        ]
    )
    if failed or warnings:
        lines.extend(["", "## Gate Attention"])
        for check in failed + warnings:
            lines.append(f"- {check.status}: {check.name} `{check.path}` - {check.detail}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    source = Path(args.source).resolve()
    if not source.exists():
        print(f"source does not exist: {source}", file=sys.stderr)
        return 2

    checks = run_checks(source, args.allow_dirty)
    decision = "fail" if any(check.status == "fail" for check in checks) else "pass"
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle = Path(args.staging_root).resolve() / f"{stamp}-{bundle_slug(args.ticket_title)}"
    bundle.mkdir(parents=True, exist_ok=False)
    copy_source(source, bundle / "source")

    decision_doc = {
        "schema_version": 1,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": source.as_posix(),
        "ref": args.ref,
        "decision": decision,
        "checks": [asdict(check) for check in checks],
    }
    (bundle / "qa-decision.json").write_text(
        json.dumps(decision_doc, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_ticket(bundle / "approve-deploy-ticket.md", args.ticket_title, args.ref, decision, checks)

    print(bundle.as_posix())
    return 0 if decision == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
