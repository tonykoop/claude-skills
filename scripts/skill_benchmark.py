#!/usr/bin/env python3
"""Run deterministic skill benchmark assertions from JSON fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PASS = "pass"
FAIL = "fail"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a lightweight skill benchmark suite and emit a reviewable run log."
    )
    parser.add_argument("suite", help="Path to a benchmark suite JSON file.")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root for resolving fixture and output paths. Defaults to cwd.",
    )
    parser.add_argument(
        "--out",
        help="Optional path for the JSON run log. Parent directories are created if needed.",
    )
    parser.add_argument(
        "--run-id",
        default="local-sample",
        help="Stable run identifier recorded in the run log.",
    )
    parser.add_argument(
        "--runtime",
        default="codex-cli",
        help="Runtime label recorded in the run log.",
    )
    parser.add_argument(
        "--created-at",
        default="not-recorded",
        help="Timestamp or date recorded in the run log. Pass an ISO-8601 value for archived runs.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Expected {path} to contain a JSON object.")
    return data


def resolve_path(repo_root: Path, candidate_root: Path, raw_path: str | None) -> Path:
    if not raw_path:
        return candidate_root
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return candidate_root / path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")


def normalize(text: str, case_sensitive: bool) -> str:
    return text if case_sensitive else text.lower()


def normalize_terms(terms: list[str], case_sensitive: bool) -> list[str]:
    return terms if case_sensitive else [term.lower() for term in terms]


def assertion_result(
    assertion: dict[str, Any], repo_root: Path, candidate_root: Path
) -> dict[str, Any]:
    assertion_id = str(assertion.get("id") or assertion.get("kind") or "assertion")
    kind = assertion.get("kind")
    target = resolve_path(repo_root, candidate_root, assertion.get("path"))
    result: dict[str, Any] = {
        "id": assertion_id,
        "kind": kind,
        "path": str(target.relative_to(repo_root)) if target.is_relative_to(repo_root) else str(target),
    }

    if kind == "file_exists":
        exists = target.exists()
        result["status"] = PASS if exists else FAIL
        result["evidence"] = "found" if exists else "missing"
        return result

    if kind in {"contains_all", "contains_any", "not_contains_any"}:
        if not target.exists() or not target.is_file():
            result["status"] = FAIL
            result["evidence"] = "target file missing"
            return result
        terms = assertion.get("terms") or []
        if not isinstance(terms, list) or not all(isinstance(term, str) for term in terms):
            result["status"] = FAIL
            result["evidence"] = "terms must be a list of strings"
            return result
        case_sensitive = bool(assertion.get("case_sensitive", False))
        text = normalize(read_text(target), case_sensitive)
        normalized_terms = normalize_terms(terms, case_sensitive)
        found = [term for term, needle in zip(terms, normalized_terms) if needle in text]
        missing = [term for term, needle in zip(terms, normalized_terms) if needle not in text]

        if kind == "contains_all":
            passed = not missing
            result["status"] = PASS if passed else FAIL
            result["evidence"] = {"found": found, "missing": missing}
            return result

        if kind == "contains_any":
            passed = bool(found)
            result["status"] = PASS if passed else FAIL
            result["evidence"] = {"found": found, "missing": missing}
            return result

        passed = not found
        result["status"] = PASS if passed else FAIL
        result["evidence"] = {"unexpected": found}
        return result

    result["status"] = FAIL
    result["evidence"] = f"unsupported assertion kind: {kind}"
    return result


def run_case(case: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    candidate = case.get("candidate") or {}
    if not isinstance(candidate, dict):
        raise SystemExit(f"Case {case.get('id', '<unknown>')} candidate must be an object.")

    raw_candidate_path = candidate.get("path")
    if not raw_candidate_path:
        raise SystemExit(f"Case {case.get('id', '<unknown>')} is missing candidate.path.")
    candidate_root = Path(raw_candidate_path)
    if not candidate_root.is_absolute():
        candidate_root = repo_root / candidate_root

    assertions = case.get("assertions") or []
    if not isinstance(assertions, list):
        raise SystemExit(f"Case {case.get('id', '<unknown>')} assertions must be a list.")

    assertion_results = [
        assertion_result(assertion, repo_root, candidate_root) for assertion in assertions
    ]
    passed = sum(1 for result in assertion_results if result["status"] == PASS)
    failed = len(assertion_results) - passed
    return {
        "id": case.get("id"),
        "title": case.get("title"),
        "skill_name": case.get("skill_name"),
        "runtime_targets": case.get("runtime_targets", []),
        "prompt_fixture": case.get("prompt_fixture"),
        "expected_mode": case.get("expected_mode"),
        "expected_artifacts": case.get("expected_artifacts", []),
        "candidate": {
            "kind": candidate.get("kind", "local_artifact"),
            "path": str(candidate_root.relative_to(repo_root))
            if candidate_root.is_relative_to(repo_root)
            else str(candidate_root),
        },
        "watch_points": case.get("watch_points", []),
        "status": PASS if failed == 0 else FAIL,
        "passed_count": passed,
        "failed_count": failed,
        "assertions": assertion_results,
    }


def build_run_log(suite: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    cases = suite.get("cases") or []
    if not isinstance(cases, list) or not cases:
        raise SystemExit("Benchmark suite must define at least one case.")

    case_results = [run_case(case, repo_root) for case in cases]
    passed_assertions = sum(case["passed_count"] for case in case_results)
    failed_assertions = sum(case["failed_count"] for case in case_results)
    passed_cases = sum(1 for case in case_results if case["status"] == PASS)
    failed_cases = len(case_results) - passed_cases

    return {
        "schema_version": 1,
        "suite_id": suite.get("suite_id"),
        "skill_name": suite.get("skill_name"),
        "skill_version": suite.get("skill_version"),
        "runtime_targets": suite.get("runtime_targets", []),
        "runtime": args.runtime,
        "run_id": args.run_id,
        "created_at": args.created_at,
        "status": PASS if failed_assertions == 0 else FAIL,
        "totals": {
            "cases": len(case_results),
            "cases_passed": passed_cases,
            "cases_failed": failed_cases,
            "assertions": passed_assertions + failed_assertions,
            "assertions_passed": passed_assertions,
            "assertions_failed": failed_assertions,
        },
        "cases": case_results,
        "archive_notes": suite.get("archive_notes", []),
    }


def main() -> int:
    args = parse_args()
    suite = load_json(Path(args.suite))
    run_log = build_run_log(suite, args)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(run_log, indent=2) + "\n", encoding="utf-8")

    totals = run_log["totals"]
    print(
        f"{run_log['status'].upper()} {run_log['suite_id']}: "
        f"{totals['assertions_passed']}/{totals['assertions']} assertions "
        f"across {totals['cases']} case(s)"
    )
    if args.out:
        print(f"Wrote {args.out}")
    return 0 if run_log["status"] == PASS else 1


if __name__ == "__main__":
    sys.exit(main())
