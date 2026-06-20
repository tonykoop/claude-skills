"""CLI for release_qa — validate, run gates, panel review, check policies, and full run."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def _load_bundle(path: str):
    from release_qa.manifest import ReleaseBundle
    with open(path, "r") as f:
        data = json.load(f)
    return ReleaseBundle.from_dict(data)


def _cmd_validate(args: argparse.Namespace) -> int:
    from release_qa.manifest import ManifestValidator

    bundle = _load_bundle(args.manifest)
    validator = ManifestValidator()
    report = validator.validate(bundle)

    if args.json:
        output = {
            "valid": report.valid,
            "errors": report.errors,
            "warnings": report.warnings,
        }
        print(json.dumps(output, indent=2))
    else:
        status = "VALID" if report.valid else "INVALID"
        print(f"Manifest validation: {status}")
        if report.errors:
            print("Errors:")
            for e in report.errors:
                print(f"  ERROR: {e}")
        if report.warnings:
            print("Warnings:")
            for w in report.warnings:
                print(f"  WARN:  {w}")

    return 0 if report.valid else 1


def _cmd_run_gates(args: argparse.Namespace) -> int:
    from release_qa.workflow import WorkflowEngine

    bundle = _load_bundle(args.manifest)
    engine = WorkflowEngine()
    results = engine.run_full(bundle)

    if args.json:
        output = []
        for sr in results:
            output.append({
                "stage": sr.stage,
                "passed": sr.passed,
                "entered_at": sr.entered_at,
                "completed_at": sr.completed_at,
                "gate_results": [
                    {
                        "gate_id": gr.gate_id,
                        "passed": gr.passed,
                        "score": gr.score,
                        "evidence": gr.evidence,
                        "blocker": gr.blocker,
                    }
                    for gr in sr.gate_results
                ],
            })
        print(json.dumps(output, indent=2))
    else:
        all_passed = all(sr.passed for sr in results)
        print(f"Gate workflow: {'PASSED' if all_passed else 'FAILED'}")
        for sr in results:
            status = "PASS" if sr.passed else "FAIL"
            print(f"  Stage [{sr.stage}]: {status}")
            for gr in sr.gate_results:
                g_status = "PASS" if gr.passed else "FAIL"
                blocker_mark = " [BLOCKER]" if gr.blocker else ""
                print(f"    Gate [{gr.gate_id}]: {g_status}{blocker_mark} — {gr.evidence}")

    overall_passed = all(sr.passed for sr in results)
    return 0 if overall_passed else 1


def _cmd_panel_review(args: argparse.Namespace) -> int:
    from release_qa.adversarial_panel import AdversarialPanel

    bundle = _load_bundle(args.manifest)
    panel = AdversarialPanel()
    report = panel.review(bundle)

    if args.json:
        output = {
            "bundle_id": report.bundle_id,
            "consensus_score": report.consensus_score,
            "recommendation": report.recommendation,
            "dissenting_reviewers": report.dissenting_reviewers,
            "critiques": [
                {
                    "reviewer_id": c.reviewer_id,
                    "lens": c.lens,
                    "finding": c.finding,
                    "severity": c.severity,
                    "score": c.score,
                }
                for c in report.critiques
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Panel Review — Bundle: {report.bundle_id}")
        print(f"  Consensus score: {report.consensus_score:.2f}")
        print(f"  Recommendation:  {report.recommendation.upper()}")
        if report.dissenting_reviewers:
            print(f"  Dissenters: {', '.join(report.dissenting_reviewers)}")
        print(f"  Critiques ({len(report.critiques)}):")
        for c in report.critiques:
            print(f"    [{c.severity.upper()}] {c.reviewer_id}: {c.finding}")

    return 0 if report.recommendation == "approve" else 1


def _cmd_check_policy(args: argparse.Namespace) -> int:
    from release_qa.policy import PolicyEngine

    bundle = _load_bundle(args.manifest)
    engine = PolicyEngine()
    engine.load_policies()
    violations = engine.evaluate(bundle)
    blocked = engine.is_release_blocked(bundle)

    if args.json:
        output = {
            "blocked": blocked,
            "violation_count": len(violations),
            "violations": [
                {
                    "policy_id": v.policy_id,
                    "policy_name": v.policy_name,
                    "severity": v.severity,
                    "detail": v.detail,
                }
                for v in violations
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        status = "BLOCKED" if blocked else "CLEAR"
        print(f"Policy check: {status} ({len(violations)} violation(s))")
        for v in violations:
            print(f"  [{v.severity.upper()}] {v.policy_id}: {v.detail}")

    return 1 if blocked else 0


def _cmd_full_run(args: argparse.Namespace) -> int:
    from release_qa.manifest import ManifestValidator
    from release_qa.workflow import WorkflowEngine
    from release_qa.adversarial_panel import AdversarialPanel
    from release_qa.policy import PolicyEngine

    bundle = _load_bundle(args.manifest)

    validator = ManifestValidator()
    manifest_report = validator.validate(bundle)

    engine = WorkflowEngine()
    gate_results = engine.run_full(bundle)

    panel = AdversarialPanel()
    panel_report = panel.review(bundle)

    policy_engine = PolicyEngine()
    policy_engine.load_policies()
    violations = policy_engine.evaluate(bundle)
    blocked = policy_engine.is_release_blocked(bundle)

    gates_passed = all(sr.passed for sr in gate_results)
    overall = manifest_report.valid and gates_passed and panel_report.recommendation == "approve" and not blocked

    if args.json:
        output = {
            "bundle_id": bundle.id,
            "overall_passed": overall,
            "manifest": {
                "valid": manifest_report.valid,
                "errors": manifest_report.errors,
                "warnings": manifest_report.warnings,
            },
            "gates": {
                "passed": gates_passed,
                "stages": [sr.stage for sr in gate_results],
                "stage_results": [
                    {"stage": sr.stage, "passed": sr.passed}
                    for sr in gate_results
                ],
            },
            "panel": {
                "consensus_score": panel_report.consensus_score,
                "recommendation": panel_report.recommendation,
            },
            "policy": {
                "blocked": blocked,
                "violation_count": len(violations),
            },
        }
        print(json.dumps(output, indent=2))
    else:
        result_str = "PASSED" if overall else "FAILED"
        print(f"=== Full Release QA Run: {result_str} ===")
        print(f"  Manifest:    {'VALID' if manifest_report.valid else 'INVALID'} ({len(manifest_report.errors)} error(s))")
        print(f"  Gates:       {'PASSED' if gates_passed else 'FAILED'} ({len(gate_results)} stage(s))")
        print(f"  Panel:       {panel_report.recommendation.upper()} (score: {panel_report.consensus_score:.2f})")
        print(f"  Policy:      {'BLOCKED' if blocked else 'CLEAR'} ({len(violations)} violation(s))")

    return 0 if overall else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="release-qa",
        description="Release QA CLI — validate, gate, review and policy-check release bundles.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate
    p_validate = subparsers.add_parser("validate", help="Validate a manifest JSON file.")
    p_validate.add_argument("manifest", help="Path to manifest JSON file.")
    p_validate.add_argument("--json", action="store_true", help="Output as JSON.")

    # run-gates
    p_gates = subparsers.add_parser("run-gates", help="Run multi-stage gate workflow.")
    p_gates.add_argument("manifest", help="Path to manifest JSON file.")
    p_gates.add_argument("--json", action="store_true", help="Output as JSON.")

    # panel-review
    p_panel = subparsers.add_parser("panel-review", help="Run adversarial panel review.")
    p_panel.add_argument("manifest", help="Path to manifest JSON file.")
    p_panel.add_argument("--json", action="store_true", help="Output as JSON.")

    # check-policy
    p_policy = subparsers.add_parser("check-policy", help="Check governance policies.")
    p_policy.add_argument("manifest", help="Path to manifest JSON file.")
    p_policy.add_argument("--json", action="store_true", help="Output as JSON.")

    # full-run
    p_full = subparsers.add_parser("full-run", help="Run all stages and print combined report.")
    p_full.add_argument("manifest", help="Path to manifest JSON file.")
    p_full.add_argument("--json", action="store_true", help="Output as JSON.")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    dispatch = {
        "validate": _cmd_validate,
        "run-gates": _cmd_run_gates,
        "panel-review": _cmd_panel_review,
        "check-policy": _cmd_check_policy,
        "full-run": _cmd_full_run,
    }

    fn = dispatch.get(args.command)
    if fn is None:
        parser.print_help()
        return 2

    try:
        return fn(args)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
