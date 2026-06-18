#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import shlex
import subprocess
import sys
import xml.etree.ElementTree as ET
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
LIMITED_JOINT_TYPES = {"revolute", "prismatic"}


@dataclass
class GateResult:
    gate: str
    path: str
    status: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run automated verification gates.")
    parser.add_argument("--path", required=True, help="File or directory to verify.")
    parser.add_argument("--qa-output", default="qa-decision.json", help="JSON decision path.")
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help="Command to execute as a sandbox/runtime gate. Repeatable.",
    )
    parser.add_argument("--timeout", type=float, default=30.0, help="Seconds per command.")
    parser.add_argument("--max-line-length", type=int, default=120)
    return parser.parse_args()


def iter_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    files: list[Path] = []
    for child in path.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in child.parts):
            continue
        if child.is_file():
            files.append(child)
    return sorted(files)


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def snippet(text: str, limit: int = 500) -> str:
    clean = text.strip()
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3] + "..."


def run_command(command: str, cwd: Path, timeout: float) -> GateResult:
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        return GateResult("sandbox-exec", command, "fail", f"cannot parse command: {exc}")
    if not argv:
        return GateResult("sandbox-exec", command, "fail", "empty command")
    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return GateResult("sandbox-exec", command, "fail", f"command not found: {argv[0]}")
    except subprocess.TimeoutExpired:
        return GateResult("sandbox-exec", command, "fail", f"timed out after {timeout:g}s")
    if result.returncode != 0:
        output = snippet(result.stderr or result.stdout) or f"exit {result.returncode}"
        return GateResult("sandbox-exec", command, "fail", output)
    output = snippet(result.stdout or result.stderr) or "command exited 0"
    return GateResult("sandbox-exec", command, "pass", output)


def lint_markdown(path: Path, root: Path, max_line_length: int) -> GateResult:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return GateResult("markdown-length", rel(path, root), "fail", f"not valid UTF-8: {exc}")
    if not text.strip():
        return GateResult("markdown-length", rel(path, root), "fail", "file is empty")
    for idx, line in enumerate(text.splitlines(), start=1):
        if "\t" in line:
            return GateResult("markdown-length", rel(path, root), "fail", f"tab character on line {idx}")
        if line.rstrip(" ") != line:
            return GateResult("markdown-length", rel(path, root), "fail", f"trailing whitespace on line {idx}")
        if len(line) > max_line_length:
            return GateResult(
                "markdown-length",
                rel(path, root),
                "fail",
                f"line {idx} is {len(line)} chars; max is {max_line_length}",
            )
    return GateResult("markdown-length", rel(path, root), "pass", "markdown lint passed")


def parse_float(value: str | None, field: str, joint_name: str) -> tuple[float | None, str | None]:
    if value is None:
        return None, None
    try:
        return float(value), None
    except ValueError:
        return None, f"joint {joint_name} has nonnumeric {field}: {value}"


def check_urdf(path: Path, root: Path) -> list[GateResult]:
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        return [GateResult("urdf-joint-limits", rel(path, root), "fail", f"XML parse error: {exc}")]

    results: list[GateResult] = []
    for joint in tree.findall(".//joint"):
        joint_type = joint.attrib.get("type", "")
        if joint_type not in LIMITED_JOINT_TYPES:
            continue
        name = joint.attrib.get("name", "<unnamed>")
        limit = joint.find("limit")
        if limit is None:
            results.append(
                GateResult("urdf-joint-limits", rel(path, root), "fail", f"joint {name} missing <limit>")
            )
            continue

        lower, lower_error = parse_float(limit.attrib.get("lower"), "lower", name)
        upper, upper_error = parse_float(limit.attrib.get("upper"), "upper", name)
        effort, effort_error = parse_float(limit.attrib.get("effort"), "effort", name)
        velocity, velocity_error = parse_float(limit.attrib.get("velocity"), "velocity", name)
        for error in (lower_error, upper_error, effort_error, velocity_error):
            if error:
                results.append(GateResult("urdf-joint-limits", rel(path, root), "fail", error))
        if lower is None or upper is None:
            results.append(
                GateResult("urdf-joint-limits", rel(path, root), "fail", f"joint {name} requires lower and upper")
            )
            continue
        if lower > upper:
            results.append(
                GateResult(
                    "urdf-joint-limits",
                    rel(path, root),
                    "fail",
                    f"joint {name} lower {lower:g} exceeds upper {upper:g}",
                )
            )
        if effort is not None and effort < 0:
            results.append(GateResult("urdf-joint-limits", rel(path, root), "fail", f"joint {name} has negative effort"))
        if velocity is not None and velocity < 0:
            results.append(
                GateResult("urdf-joint-limits", rel(path, root), "fail", f"joint {name} has negative velocity")
            )

    if not results:
        results.append(GateResult("urdf-joint-limits", rel(path, root), "pass", "URDF joint limits passed"))
    return results


def run_gates(path: Path, commands: list[str], timeout: float, max_line_length: int) -> list[GateResult]:
    root = path if path.is_dir() else path.parent
    results: list[GateResult] = []
    for command in commands:
        results.append(run_command(command, root, timeout))

    files = iter_files(path)
    markdown_files = [file for file in files if file.suffix.lower() == ".md"]
    urdf_files = [file for file in files if file.suffix.lower() == ".urdf"]
    if not commands:
        results.append(GateResult("sandbox-exec", root.as_posix(), "skip", "no --command provided"))
    if not markdown_files:
        results.append(GateResult("markdown-length", root.as_posix(), "skip", "no markdown files found"))
    if not urdf_files:
        results.append(GateResult("urdf-joint-limits", root.as_posix(), "skip", "no URDF files found"))

    for file in markdown_files:
        results.append(lint_markdown(file, root, max_line_length))
    for file in urdf_files:
        results.extend(check_urdf(file, root))
    return results


def main() -> int:
    args = parse_args()
    path = Path(args.path).resolve()
    if not path.exists():
        print(f"path does not exist: {path}", file=sys.stderr)
        return 2

    checks = run_gates(path, args.command, args.timeout, args.max_line_length)
    decision = "fail" if any(check.status == "fail" for check in checks) else "pass"
    doc = {
        "schema_version": 1,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "path": path.as_posix(),
        "decision": decision,
        "checks": [asdict(check) for check in checks],
    }
    output = Path(args.qa_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{decision}: {output.as_posix()}")
    return 0 if decision == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
