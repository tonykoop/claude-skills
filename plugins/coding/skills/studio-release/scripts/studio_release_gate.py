#!/usr/bin/env python3
"""Studio Release gate: headless lint/sandbox + staging bundle.

Implements claude-skills#255 (Epic #254 back-end release engine).

The gate is the downstream counterpart to idea-incubator. When a feature
branch reaches PR review or an agent work block ends, it:

1. runs dependency-light headless validation (markdown hygiene, ``py_compile``,
   ``bash -n``, git cleanliness);
2. scores a confidence value and routes the bundle through the human-in-the-loop
   circuit breaker (auto-eligible vs. escalate vs. blocked) so a reviewer only
   spends attention on the ambiguous minority;
3. assigns a distinct-model QA auditor via the governance adversarial-QA router
   (claude-skills#256) when creator identity is supplied, so the agent that made
   an asset never certifies it;
4. stages a copied source tree plus three machine-readable artifacts —
   ``qa-decision.json``, ``publish-manifest.json`` (publishing metadata for the
   StudioPipeline), and a single human ``approve-deploy-ticket.md``.

The gate produces evidence; a human reviewer still makes the release call.

CLI:
    python studio_release_gate.py --source <path> --ticket-title "..." \
        [--ref "PR #123"] [--staging-root dist/studio-release] \
        [--deploy-target studio-pipeline] [--allow-dirty] \
        [--creator-agent alice --creator-model claude-opus-4-8] [--roster DIR]

Exit 0 = pass, 1 = fail (failing check or blocked routing), 2 = bad usage.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import py_compile
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
}

# Routing dispositions for the human-in-the-loop circuit breaker (#258 vision).
ROUTING_AUTO = "auto_release_eligible"        # confident: gate found no issues
ROUTING_ESCALATE = "escalate_human_review"    # ambiguous ~10%: warnings present
ROUTING_BLOCKED = "blocked"                    # failing checks, do not deploy


@dataclass
class CheckResult:
    name: str
    path: str
    status: str
    detail: str


@dataclass
class AuditorAssignment:
    status: str          # "assigned" | "blocked" | "skipped"
    auditor: Optional[str]
    reason: str


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
        "--deploy-target",
        default="studio-pipeline",
        help="Publishing destination recorded in publish-manifest.json.",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Record dirty source state as a warning instead of failing.",
    )
    parser.add_argument(
        "--creator-agent",
        default="",
        help="Agent that produced the candidate (enables adversarial-QA routing).",
    )
    parser.add_argument(
        "--creator-model",
        default="",
        help="Model that produced the candidate (enables adversarial-QA routing).",
    )
    parser.add_argument(
        "--roster",
        default="",
        help="Directory holding governance review_router.py + agent-roster.yaml. "
        "Defaults to a discovered repo-root governance/ directory.",
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


def score_confidence(checks: list[CheckResult]) -> tuple[float, str]:
    """Map check results to a confidence score and a routing disposition.

    The circuit breaker escalates only the ambiguous middle: a clean pass is
    auto-eligible, a failing check is blocked, and anything in between (warnings)
    is routed to a human. A reviewer always signs the single ticket, but the
    routing tells the pipeline which bundles need real attention.
    """
    failed = sum(1 for c in checks if c.status == "fail")
    warned = sum(1 for c in checks if c.status == "warn")
    if failed:
        return 0.0, ROUTING_BLOCKED
    if warned:
        # Each warning erodes confidence; never drops below the escalate band.
        return max(0.55, 0.85 - 0.1 * warned), ROUTING_ESCALATE
    return 0.95, ROUTING_AUTO


def _import_review_router(roster_dir: Path):
    """Load the governance review_router module from ``roster_dir``.

    Returns ``(module, roster)`` or raises. Kept optional so the gate stays
    self-contained when run outside the host repo (mobile/zip/foreign host).
    """
    import importlib.util

    router_path = roster_dir / "review_router.py"
    guard_path = roster_dir / "spend_guard.py"
    if not router_path.exists():
        raise FileNotFoundError(f"review_router.py not found in {roster_dir}")
    # review_router imports spend_guard for load_roster; make the dir importable.
    sys.path.insert(0, str(roster_dir))
    try:
        if guard_path.exists() and "spend_guard" not in sys.modules:
            spec = importlib.util.spec_from_file_location("spend_guard", guard_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["spend_guard"] = mod  # register before exec so dataclasses resolve
            spec.loader.exec_module(mod)
        spec = importlib.util.spec_from_file_location("review_router", router_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["review_router"] = module  # register before exec so dataclasses resolve
        spec.loader.exec_module(module)
        roster_file = roster_dir / "agent-roster.yaml"
        roster = module.load_roster(str(roster_file) if roster_file.exists() else None)
        return module, roster
    finally:
        if sys.path and sys.path[0] == str(roster_dir):
            sys.path.pop(0)


def discover_roster_dir(explicit: str, source: Path) -> Optional[Path]:
    if explicit:
        cand = Path(explicit).resolve()
        return cand if cand.exists() else None
    # Walk up from the source and from this script looking for governance/.
    seeds = [source if source.is_dir() else source.parent, Path(__file__).resolve()]
    for seed in seeds:
        for parent in [seed, *seed.parents]:
            cand = parent / "governance"
            if (cand / "review_router.py").exists():
                return cand
    return None


def assign_auditor(creator_agent: str, creator_model: str, roster_dir: Optional[Path]) -> AuditorAssignment:
    """Route the candidate to a distinct-model auditor (adversarial QA #256).

    Skips cleanly when creator identity is absent or the governance modules are
    not on disk; blocks (fail-closed) when routing is requested but no valid
    distinct-family auditor can be certified.
    """
    if not creator_agent or not creator_model:
        return AuditorAssignment("skipped", None, "no creator identity supplied; auditor routing skipped")
    if roster_dir is None:
        return AuditorAssignment(
            "skipped", None, "governance review_router not found; auditor routing skipped"
        )
    try:
        module, roster = _import_review_router(roster_dir)
    except Exception as exc:  # pragma: no cover - defensive import guard
        return AuditorAssignment("skipped", None, f"could not load review_router: {exc}")
    asset = {"creator_agent": creator_agent, "creator_model": creator_model}
    result = module.assign_auditor(roster, asset)
    if result.ok and result.auditor:
        return AuditorAssignment("assigned", result.auditor, result.reason)
    if result.ok:
        return AuditorAssignment("skipped", None, result.reason)
    return AuditorAssignment("blocked", None, result.reason)


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


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_artifact_index(staged_source: Path) -> list[dict]:
    artifacts = []
    for path in sorted(p for p in staged_source.rglob("*") if p.is_file()):
        artifacts.append(
            {
                "path": path.relative_to(staged_source).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_of(path),
            }
        )
    return artifacts


def write_publish_manifest(
    path: Path,
    *,
    deploy_target: str,
    ref: str,
    decision: str,
    confidence: float,
    routing: str,
    auditor: AuditorAssignment,
    artifacts: list[dict],
    created_at: str,
) -> None:
    manifest = {
        "schema_version": 1,
        "kind": "studio-release-publish-manifest",
        "created_at": created_at,
        "deploy_target": deploy_target,
        "ref": ref,
        "decision": decision,
        "confidence": round(confidence, 3),
        "routing": routing,
        "human_approval_required": True,
        "auditor": asdict(auditor),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_ticket(
    path: Path,
    title: str,
    ref: str,
    decision: str,
    confidence: float,
    routing: str,
    auditor: AuditorAssignment,
    checks: list[CheckResult],
) -> None:
    failed = [check for check in checks if check.status == "fail"]
    warnings = [check for check in checks if check.status == "warn"]
    routing_line = {
        ROUTING_AUTO: "auto-release eligible — gate found no issues",
        ROUTING_ESCALATE: "escalated for human review — warnings present",
        ROUTING_BLOCKED: "blocked — at least one check failed",
    }.get(routing, routing)
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
        f"- Confidence: `{confidence:.2f}` — routing: {routing_line}.",
    ]
    if auditor.status == "assigned":
        lines.append(f"- Adversarial QA auditor assigned: `{auditor.auditor}` ({auditor.reason}).")
    elif auditor.status == "blocked":
        lines.append(f"- Adversarial QA auditor: BLOCKED — {auditor.reason}.")
    else:
        lines.append(f"- Adversarial QA auditor: skipped ({auditor.reason}).")
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
            "- Confirm the assigned auditor (if any) is a distinct model family.",
            "",
            "Do not merge until:",
            "- The approve/deploy reviewer signs off on the staged bundle.",
        ]
    )
    if auditor.status == "blocked" or failed or warnings:
        lines.extend(["", "## Gate Attention"])
        if auditor.status == "blocked":
            lines.append(f"- blocked: adversarial-QA routing - {auditor.reason}")
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
    confidence, routing = score_confidence(checks)
    roster_dir = discover_roster_dir(args.roster, source)
    auditor = assign_auditor(args.creator_agent, args.creator_model, roster_dir)

    failed = any(check.status == "fail" for check in checks)
    decision = "fail" if failed else "pass"
    if auditor.status == "blocked":
        # A requested-but-unroutable auditor is a fail-closed release blocker.
        routing = ROUTING_BLOCKED

    created_at = dt.datetime.now(dt.timezone.utc).isoformat()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle = Path(args.staging_root).resolve() / f"{stamp}-{bundle_slug(args.ticket_title)}"
    bundle.mkdir(parents=True, exist_ok=False)
    staged_source = bundle / "source"
    copy_source(source, staged_source)
    artifacts = build_artifact_index(staged_source)

    decision_doc = {
        "schema_version": 2,
        "created_at": created_at,
        "source": source.as_posix(),
        "ref": args.ref,
        "decision": decision,
        "confidence": round(confidence, 3),
        "routing": routing,
        "auditor": asdict(auditor),
        "checks": [asdict(check) for check in checks],
    }
    (bundle / "qa-decision.json").write_text(
        json.dumps(decision_doc, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_publish_manifest(
        bundle / "publish-manifest.json",
        deploy_target=args.deploy_target,
        ref=args.ref,
        decision=decision,
        confidence=confidence,
        routing=routing,
        auditor=auditor,
        artifacts=artifacts,
        created_at=created_at,
    )
    write_ticket(
        bundle / "approve-deploy-ticket.md",
        args.ticket_title,
        args.ref,
        decision,
        confidence,
        routing,
        auditor,
        checks,
    )

    print(bundle.as_posix())
    blocked = decision == "fail" or auditor.status == "blocked"
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
