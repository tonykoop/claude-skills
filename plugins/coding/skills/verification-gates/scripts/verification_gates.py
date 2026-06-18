#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import shlex
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
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
    metadata: dict = field(default_factory=dict)


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
    parser.add_argument(
        "--strict-urdf-joint-types",
        action="store_true",
        help="Fail on URDF joint types outside fixed/continuous/revolute/prismatic/floating/planar.",
    )
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
        return GateResult(
            "sandbox-exec",
            command,
            "fail",
            f"cannot parse command: {exc}",
            {"argv": [], "cwd": cwd.as_posix(), "exit_code": None, "timeout_seconds": timeout},
        )
    if not argv:
        return GateResult(
            "sandbox-exec",
            command,
            "fail",
            "empty command",
            {"argv": [], "cwd": cwd.as_posix(), "exit_code": None, "timeout_seconds": timeout},
        )
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
        return GateResult(
            "sandbox-exec",
            command,
            "fail",
            f"command not found: {argv[0]}",
            {"argv": argv, "cwd": cwd.as_posix(), "exit_code": None, "timeout_seconds": timeout},
        )
    except subprocess.TimeoutExpired as exc:
        return GateResult(
            "sandbox-exec",
            command,
            "fail",
            f"timed out after {timeout:g}s",
            {
                "argv": argv,
                "cwd": cwd.as_posix(),
                "exit_code": None,
                "timeout_seconds": timeout,
                "stdout": snippet(exc.stdout or ""),
                "stderr": snippet(exc.stderr or ""),
            },
        )
    metadata = {
        "argv": argv,
        "cwd": cwd.as_posix(),
        "exit_code": result.returncode,
        "timeout_seconds": timeout,
        "stdout": snippet(result.stdout),
        "stderr": snippet(result.stderr),
    }
    if result.returncode != 0:
        output = snippet(result.stderr or result.stdout) or f"exit {result.returncode}"
        return GateResult("sandbox-exec", command, "fail", output, metadata)
    output = snippet(result.stdout or result.stderr) or "command exited 0"
    return GateResult("sandbox-exec", command, "pass", output, metadata)


def lint_markdown(path: Path, root: Path, max_line_length: int) -> list[GateResult]:
    rel_path = rel(path, root)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return [GateResult("markdown:utf8", rel_path, "fail", f"not valid UTF-8: {exc}")]

    lines = text.splitlines()
    results = [GateResult("markdown:utf8", rel_path, "pass", "valid UTF-8")]
    results.append(
        GateResult(
            "markdown:nonempty",
            rel_path,
            "pass" if text.strip() else "fail",
            "file has content" if text.strip() else "file is empty",
        )
    )

    trailing = [idx for idx, line in enumerate(lines, start=1) if line.rstrip(" ") != line]
    tabs = [idx for idx, line in enumerate(lines, start=1) if "\t" in line]
    too_long = [idx for idx, line in enumerate(lines, start=1) if len(line) > max_line_length]
    bad_heading_spacing = []
    for idx, line in enumerate(lines, start=1):
        if not line.startswith("#"):
            continue
        marker_len = len(line) - len(line.lstrip("#"))
        if 1 <= marker_len <= 6 and (len(line) == marker_len or line[marker_len] != " "):
            bad_heading_spacing.append(idx)
    fence_count = sum(1 for line in lines if line.strip().startswith("```"))

    results.extend(
        [
            GateResult(
                "markdown:trailing-whitespace",
                rel_path,
                "fail" if trailing else "pass",
                f"trailing whitespace on lines {trailing}" if trailing else "no trailing whitespace",
            ),
            GateResult(
                "markdown:tabs",
                rel_path,
                "fail" if tabs else "pass",
                f"tab character on lines {tabs}" if tabs else "no tab characters",
            ),
            GateResult(
                "markdown:max-line-length",
                rel_path,
                "fail" if too_long else "pass",
                f"lines exceed max is {max_line_length}: {too_long}" if too_long else "line lengths passed",
                {"max_line_length": max_line_length},
            ),
            GateResult(
                "markdown:heading-spacing",
                rel_path,
                "fail" if bad_heading_spacing else "pass",
                f"heading spacing issue on lines {bad_heading_spacing}"
                if bad_heading_spacing
                else "heading spacing passed",
            ),
            GateResult(
                "markdown:fenced-code-closure",
                rel_path,
                "fail" if fence_count % 2 else "pass",
                "unclosed fenced code block" if fence_count % 2 else "fenced code blocks closed",
            ),
        ]
    )
    return results


def parse_float(value: str | None, field: str, joint_name: str) -> tuple[float | None, str | None]:
    if value is None:
        return None, None
    try:
        return float(value), None
    except ValueError:
        return None, f"joint {joint_name} has nonnumeric {field}: {value}"


def check_urdf(path: Path, root: Path, strict_joint_types: bool = False) -> list[GateResult]:
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        return [GateResult("urdf-joint-limits", rel(path, root), "fail", f"XML parse error: {exc}")]

    results: list[GateResult] = []
    rel_path = rel(path, root)
    allowed_joint_types = {"fixed", "continuous", "revolute", "prismatic", "floating", "planar"}
    joints = tree.findall(".//joint")
    joint_names: set[str] = set()
    for joint in joints:
        name = joint.attrib.get("name", "")
        if not name:
            results.append(GateResult("urdf:joint-shape", rel_path, "fail", "joint missing name"))
            continue
        if name in joint_names:
            results.append(GateResult("urdf:joint-shape", rel_path, "fail", f"duplicate joint name {name}"))
        joint_names.add(name)

    for joint in joints:
        joint_type = joint.attrib.get("type", "")
        name = joint.attrib.get("name", "<unnamed>")
        if strict_joint_types and joint_type not in allowed_joint_types:
            results.append(GateResult("urdf:joint-type", rel_path, "fail", f"joint {name} has unsupported type {joint_type}"))
        if joint.find("parent") is None or joint.find("child") is None:
            results.append(GateResult("urdf:joint-shape", rel_path, "fail", f"joint {name} requires parent and child"))

        mimic = joint.find("mimic")
        if mimic is not None and mimic.attrib.get("joint") not in joint_names:
            results.append(
                GateResult("urdf:mimic", rel_path, "fail", f"joint {name} mimics missing joint {mimic.attrib.get('joint')}")
            )

        if joint_type == "continuous" and joint.find("limit") is not None:
            results.append(GateResult("urdf:continuous", rel_path, "fail", f"continuous joint {name} must not define <limit>"))
        if joint_type not in LIMITED_JOINT_TYPES:
            continue
        if joint.find("axis") is None:
            results.append(GateResult("urdf:axis", rel_path, "fail", f"joint {name} requires <axis>"))
        limit = joint.find("limit")
        if limit is None:
            results.append(
                GateResult("urdf-joint-limits", rel_path, "fail", f"joint {name} missing <limit>")
            )
            continue

        lower, lower_error = parse_float(limit.attrib.get("lower"), "lower", name)
        upper, upper_error = parse_float(limit.attrib.get("upper"), "upper", name)
        effort, effort_error = parse_float(limit.attrib.get("effort"), "effort", name)
        velocity, velocity_error = parse_float(limit.attrib.get("velocity"), "velocity", name)
        for error in (lower_error, upper_error, effort_error, velocity_error):
            if error:
                results.append(GateResult("urdf-joint-limits", rel_path, "fail", error))
        if lower is None or upper is None:
            results.append(
                GateResult("urdf-joint-limits", rel_path, "fail", f"joint {name} requires lower and upper")
            )
            continue
        if lower > upper:
            results.append(
                GateResult(
                    "urdf-joint-limits",
                    rel_path,
                    "fail",
                    f"joint {name} lower {lower:g} exceeds upper {upper:g}",
                )
            )
        if effort is not None and effort < 0:
            results.append(GateResult("urdf-joint-limits", rel_path, "fail", f"joint {name} has negative effort"))
        if velocity is not None and velocity < 0:
            results.append(
                GateResult("urdf-joint-limits", rel_path, "fail", f"joint {name} has negative velocity")
            )

    if not results:
        results.append(GateResult("urdf-joint-limits", rel_path, "pass", "URDF joint limits passed"))
    return results


def run_gates(
    path: Path,
    commands: list[str],
    timeout: float,
    max_line_length: int,
    strict_urdf_joint_types: bool = False,
) -> list[GateResult]:
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
        results.extend(lint_markdown(file, root, max_line_length))
    for file in urdf_files:
        results.extend(check_urdf(file, root, strict_urdf_joint_types))
    return results


def main() -> int:
    args = parse_args()
    path = Path(args.path).resolve()
    if not path.exists():
        print(f"path does not exist: {path}", file=sys.stderr)
        return 2

    checks = run_gates(path, args.command, args.timeout, args.max_line_length, args.strict_urdf_joint_types)
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
