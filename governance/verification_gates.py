#!/usr/bin/env python3
"""Automated verification gates — let a runtime, not a human, pass/fail work.

Implements claude-skills#257 (Epic #254 governance layer).

The premise of the governance layer is that one human is the Chief Auditor and
verifies via automation, not eyeballs. This module is the execution-verification
arm: a headless runtime runs generated work through gates and emits a structured
verdict that attaches to the QA decision (consumed by the human-in-the-loop
circuit breaker, claude-skills#258).

Three gates ship here:

1. **Sandbox execution gate** (``sandbox_exec_gate``) — runs generated code in
   an isolated subprocess with a wall-clock timeout and a throwaway working
   directory, so an execution error (syntax error, exception, non-zero exit,
   hang) is caught by the machine instead of slipping into a PR. Cross-domain:
   any department that emits runnable code can use it.

2. **Markdown / length linter** (``markdown_length_gate``) — the *studio* domain
   gate. StudioPipeline scripts are markdown; this checks structural hygiene
   (heading present, no unterminated code fences, no tab indentation, trailing
   whitespace, over-long lines) and length bounds (a script that is too short is
   probably a stub; too long overruns the episode).

3. **URDF joint-limit test** (``urdf_joint_limit_gate``) — the *robotics* domain
   gate. Robotics CAD output is URDF; this parses the XML and asserts every
   actuated joint declares a sane ``<limit>`` (lower < upper, positive effort and
   velocity) and that any mimic/home/default position stays inside the limit.
   A humanoid joint with no limit, or a home pose outside its range, is exactly
   the kind of kinematic bug a unit test should refuse.

Every gate returns a :class:`GateResult`. :func:`run_gates` aggregates a list of
results into a :class:`GateReport` whose ``as_qa_decision()`` is the payload the
QA decision carries (acceptance: *"Gate results attach to the QA decision."*).

CLI::

    python verification_gates.py sandbox  --file solution.py [--language python]
    python verification_gates.py markdown --file episode-script.md
    python verification_gates.py urdf     --file left_leg.urdf
    python verification_gates.py report   --manifest artifacts.json

Exit 0 = all gates passed; exit 1 = at least one gate failed (the merge-gate
stop signal, same convention as spend_guard.py / review_router.py).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# --- result types -----------------------------------------------------------

# Domain tags line up with the agent-roster departments so a gate result can be
# routed/attributed back to the lane that produced the artifact.
DOMAIN_CROSS = "cross"          # any department (e.g. sandbox exec)
DOMAIN_STUDIO = "studio"        # studio-video lane (markdown scripts)
DOMAIN_ROBOTICS = "robotics"    # robotics lane (URDF / kinematics)


@dataclass
class GateResult:
    """The verdict of a single gate.

    ``passed`` is the machine pass/fail. ``findings`` are human-readable reasons
    a gate failed (or warnings on a pass). ``detail`` carries structured extras
    (exit code, line counts, joint names) for downstream tooling.
    """

    gate: str
    domain: str
    passed: bool
    summary: str
    findings: list = field(default_factory=list)
    detail: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "gate": self.gate,
            "domain": self.domain,
            "passed": self.passed,
            "summary": self.summary,
            "findings": list(self.findings),
            "detail": dict(self.detail),
        }


@dataclass
class GateReport:
    """Aggregate of several gate results — the QA-decision attachment."""

    results: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failed_gates(self) -> list:
        return [r.gate for r in self.results if not r.passed]

    def as_qa_decision(self) -> dict:
        """The payload that attaches to the QA decision (#257 acceptance).

        Shape is intentionally stable so the #258 circuit breaker can read
        ``gates_passed`` directly when deciding auto-advance vs escalate.
        """
        return {
            "gates_passed": self.passed,
            "failed_gates": self.failed_gates,
            "gate_count": len(self.results),
            "gates": [r.as_dict() for r in self.results],
        }


# --- gate 1: sandbox execution ---------------------------------------------

# Languages we are willing to execute. Default-deny: an unknown language is a
# failure, never a silent pass — the gate must not certify what it can't run.
_RUNNERS = {
    "python": [sys.executable],
    "bash": ["bash"],
    "sh": ["sh"],
}


def sandbox_exec_gate(
    code: str,
    language: str = "python",
    *,
    timeout_seconds: float = 10.0,
    label: str = "generated code",
) -> GateResult:
    """Run ``code`` in an isolated subprocess and catch execution errors.

    Isolation is deliberately lightweight but real: a fresh temp working
    directory (so the script can't read or clobber the repo by relative path), a
    hard wall-clock timeout (so an infinite loop trips instead of hanging the
    sprint), and exit-code capture (so any uncaught exception fails the gate).
    For untrusted code this should run inside a container/VM; the temp-cwd +
    timeout floor is the minimum that makes the gate meaningful headless.
    """
    gate = "sandbox-exec"
    lang = language.lower()
    if lang not in _RUNNERS:
        return GateResult(
            gate, DOMAIN_CROSS, False,
            f"unsupported language {language!r} (cannot certify un-runnable code)",
            findings=[f"no sandbox runner for {language!r}; supported: {', '.join(sorted(_RUNNERS))}"],
            detail={"language": language},
        )

    with tempfile.TemporaryDirectory(prefix="gate-sandbox-") as workdir:
        src = Path(workdir) / ("script.py" if lang == "python" else "script.sh")
        src.write_text(code, encoding="utf-8")
        cmd = _RUNNERS[lang] + [str(src)]
        try:
            proc = subprocess.run(
                cmd,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return GateResult(
                gate, DOMAIN_CROSS, False,
                f"{label} timed out after {timeout_seconds:g}s (possible infinite loop)",
                findings=[f"no exit within {timeout_seconds:g}s wall-clock"],
                detail={"language": lang, "timeout_seconds": timeout_seconds},
            )
        except FileNotFoundError:
            return GateResult(
                gate, DOMAIN_CROSS, False,
                f"sandbox runner for {language!r} not installed",
                findings=[f"interpreter {cmd[0]!r} not found on PATH"],
                detail={"language": lang},
            )

    stderr_tail = (proc.stderr or "").strip().splitlines()[-5:]
    if proc.returncode != 0:
        return GateResult(
            gate, DOMAIN_CROSS, False,
            f"{label} raised a runtime error (exit {proc.returncode})",
            findings=stderr_tail or [f"non-zero exit {proc.returncode} with no stderr"],
            detail={"language": lang, "returncode": proc.returncode},
        )
    return GateResult(
        gate, DOMAIN_CROSS, True,
        f"{label} executed cleanly (exit 0)",
        detail={"language": lang, "returncode": 0},
    )


# --- gate 2: markdown / length linter (studio) -----------------------------

def markdown_length_gate(
    text: str,
    *,
    min_words: int = 80,
    max_words: int = 2500,
    max_line_length: int = 120,
    label: str = "script",
) -> GateResult:
    """Lint a StudioPipeline markdown script for structure and length.

    Catches the failure modes that make a generated script unusable headless:
    a stub that is too short, a runaway that overruns the episode, missing
    headings (no structure), unterminated code fences (broken markdown), tab
    indentation and trailing whitespace (renders wrong), and over-long lines.
    """
    gate = "markdown-length"
    findings: list = []
    lines = text.splitlines()
    words = len(text.split())

    if words < min_words:
        findings.append(f"too short: {words} words < {min_words} (looks like a stub)")
    if words > max_words:
        findings.append(f"too long: {words} words > {max_words} (overruns episode budget)")

    if not any(ln.lstrip().startswith("#") for ln in lines):
        findings.append("no markdown heading (#) — script has no structure")

    if text.count("```") % 2 != 0:
        findings.append("unterminated code fence (odd number of ``` markers)")

    for i, ln in enumerate(lines, 1):
        if "\t" in ln:
            findings.append(f"line {i}: tab indentation (use spaces)")
        if ln != ln.rstrip():
            findings.append(f"line {i}: trailing whitespace")
        if len(ln) > max_line_length:
            findings.append(f"line {i}: {len(ln)} chars > {max_line_length}")

    # Keep the report scannable: cap repeated per-line nits.
    capped = findings[:20]
    if len(findings) > 20:
        capped.append(f"... and {len(findings) - 20} more line issues")

    passed = not findings
    summary = (
        f"{label}: {words} words, {len(lines)} lines — clean"
        if passed
        else f"{label}: {len(findings)} issue(s) ({words} words)"
    )
    return GateResult(
        gate, DOMAIN_STUDIO, passed, summary,
        findings=capped,
        detail={"words": words, "lines": len(lines)},
    )


# --- gate 3: URDF joint-limit test (robotics) ------------------------------

# Joint types that physically need a limit. continuous/fixed/floating/planar do
# not declare [lower, upper] and are intentionally exempt.
_LIMITED_JOINT_TYPES = {"revolute", "prismatic"}


def urdf_joint_limit_gate(
    urdf_xml: str,
    *,
    home_positions: Optional[dict] = None,
    label: str = "URDF",
) -> GateResult:
    """Unit-test URDF joints for sane kinematic limits.

    For every ``revolute``/``prismatic`` joint:
      * a ``<limit>`` element must exist;
      * ``lower`` and ``upper`` must be present, numeric, and ``lower < upper``;
      * ``effort`` and ``velocity`` must be present and strictly positive;
    and any provided home/default position must lie within ``[lower, upper]``.

    ``home_positions`` maps joint name -> commanded position (e.g. the rest pose
    a CAD export ships); a pose outside the joint's range is a real kinematic
    bug and fails the gate.
    """
    gate = "urdf-joint-limit"
    home_positions = home_positions or {}
    findings: list = []

    try:
        root = ET.fromstring(urdf_xml)
    except ET.ParseError as exc:
        return GateResult(
            gate, DOMAIN_ROBOTICS, False,
            f"{label}: XML parse error",
            findings=[f"invalid URDF XML: {exc}"],
            detail={},
        )

    joints = root.findall("joint")
    checked = 0
    for joint in joints:
        name = joint.get("name", "<unnamed>")
        jtype = joint.get("type", "<none>")
        if jtype not in _LIMITED_JOINT_TYPES:
            continue
        checked += 1

        limit = joint.find("limit")
        if limit is None:
            findings.append(f"joint {name!r} ({jtype}): missing <limit>")
            continue

        lower = _to_float(limit.get("lower"))
        upper = _to_float(limit.get("upper"))
        effort = _to_float(limit.get("effort"))
        velocity = _to_float(limit.get("velocity"))

        if lower is None or upper is None:
            findings.append(f"joint {name!r}: <limit> missing numeric lower/upper")
        elif lower >= upper:
            findings.append(f"joint {name!r}: lower {lower} >= upper {upper} (degenerate range)")

        if effort is None or effort <= 0:
            findings.append(f"joint {name!r}: effort must be > 0 (got {limit.get('effort')!r})")
        if velocity is None or velocity <= 0:
            findings.append(f"joint {name!r}: velocity must be > 0 (got {limit.get('velocity')!r})")

        if name in home_positions and lower is not None and upper is not None:
            pos = home_positions[name]
            if not (lower <= pos <= upper):
                findings.append(
                    f"joint {name!r}: home position {pos} outside limit [{lower}, {upper}]"
                )

    if checked == 0:
        findings.append("no actuated (revolute/prismatic) joints found to verify")

    passed = not findings
    summary = (
        f"{label}: {checked} actuated joint(s) within limits"
        if passed
        else f"{label}: {len(findings)} joint-limit issue(s) across {checked} actuated joint(s)"
    )
    return GateResult(
        gate, DOMAIN_ROBOTICS, passed, summary,
        findings=findings,
        detail={"actuated_joints": checked, "total_joints": len(joints)},
    )


def _to_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# --- aggregation ------------------------------------------------------------

def run_gates(results: list) -> GateReport:
    """Bundle gate results into the report that attaches to the QA decision."""
    return GateReport(results=list(results))


# --- CLI --------------------------------------------------------------------

def _emit(report: GateReport, as_json: bool) -> int:
    if as_json:
        print(json.dumps(report.as_qa_decision(), indent=2))
    else:
        for r in report.results:
            mark = "PASS" if r.passed else "FAIL"
            print(f"[{mark}] {r.gate} ({r.domain}): {r.summary}")
            for f in r.findings:
                print(f"        - {f}")
        print("-" * 48)
        print("ALL GATES PASSED" if report.passed else f"BLOCKED: {', '.join(report.failed_gates)}")
    return 0 if report.passed else 1


def _run_manifest(manifest: dict) -> GateReport:
    """Run gates declared in a manifest of artifacts.

    Manifest shape::

        {"artifacts": [
            {"gate": "sandbox", "language": "python", "path": "sol.py"},
            {"gate": "markdown", "path": "script.md"},
            {"gate": "urdf", "path": "leg.urdf", "home_positions": {"knee": 0.2}}
        ]}
    """
    results: list = []
    for art in manifest.get("artifacts", []):
        gate = art.get("gate")
        path = art.get("path")
        label = art.get("label") or (Path(path).name if path else gate)
        text = Path(path).read_text(encoding="utf-8") if path else art.get("content", "")
        if gate == "sandbox":
            results.append(sandbox_exec_gate(
                text, art.get("language", "python"),
                timeout_seconds=art.get("timeout_seconds", 10.0), label=label,
            ))
        elif gate == "markdown":
            results.append(markdown_length_gate(
                text,
                min_words=art.get("min_words", 80),
                max_words=art.get("max_words", 2500),
                max_line_length=art.get("max_line_length", 120),
                label=label,
            ))
        elif gate == "urdf":
            results.append(urdf_joint_limit_gate(
                text, home_positions=art.get("home_positions"), label=label,
            ))
        else:
            results.append(GateResult(
                "unknown", DOMAIN_CROSS, False,
                f"unknown gate {gate!r} in manifest",
                findings=[f"manifest artifact declared unsupported gate {gate!r}"],
            ))
    return run_gates(results)


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(description="Automated verification gates (#257)")
    sub = ap.add_subparsers(dest="mode", required=True)

    p_sand = sub.add_parser("sandbox", help="run code in a sandbox, catch runtime errors")
    p_sand.add_argument("--file", required=True)
    p_sand.add_argument("--language", default="python")
    p_sand.add_argument("--timeout", type=float, default=10.0)

    p_md = sub.add_parser("markdown", help="lint a markdown script (studio)")
    p_md.add_argument("--file", required=True)
    p_md.add_argument("--min-words", type=int, default=80)
    p_md.add_argument("--max-words", type=int, default=2500)
    p_md.add_argument("--max-line-length", type=int, default=120)

    p_urdf = sub.add_parser("urdf", help="URDF joint-limit unit test (robotics)")
    p_urdf.add_argument("--file", required=True)
    p_urdf.add_argument("--home-positions", help="JSON map of joint -> home position")

    p_rep = sub.add_parser("report", help="run gates from an artifact manifest")
    p_rep.add_argument("--manifest", required=True)

    for p in (p_sand, p_md, p_urdf, p_rep):
        p.add_argument("--json", action="store_true", help="emit the QA-decision JSON")

    args = ap.parse_args(argv)

    if args.mode == "sandbox":
        code = Path(args.file).read_text(encoding="utf-8")
        res = sandbox_exec_gate(code, args.language, timeout_seconds=args.timeout,
                                label=Path(args.file).name)
        return _emit(run_gates([res]), args.json)

    if args.mode == "markdown":
        text = Path(args.file).read_text(encoding="utf-8")
        res = markdown_length_gate(
            text, min_words=args.min_words, max_words=args.max_words,
            max_line_length=args.max_line_length, label=Path(args.file).name,
        )
        return _emit(run_gates([res]), args.json)

    if args.mode == "urdf":
        text = Path(args.file).read_text(encoding="utf-8")
        homes = json.loads(args.home_positions) if args.home_positions else None
        res = urdf_joint_limit_gate(text, home_positions=homes, label=Path(args.file).name)
        return _emit(run_gates([res]), args.json)

    if args.mode == "report":
        with open(args.manifest, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
        return _emit(_run_manifest(manifest), args.json)

    ap.error("unknown mode")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
