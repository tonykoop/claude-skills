"""Adversarial gate rules engine for release-QA.

Each rule is a deterministic, offline check on a :class:`ReleaseBundleManifest`.
Rules are intentionally strict to catch common "fake green" patterns where an
agent self-certifies success without real evidence.

Usage::

    from release_qa import evaluate_release, ReleaseBundleManifest

    manifest = ReleaseBundleManifest(...)
    result = evaluate_release(manifest)
    if not result.overall_passed:
        for r in result.rule_results:
            if not r.passed:
                print(f"FAIL [{r.rule_id}]: {r.reason}")
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from release_qa.models import ReleaseBundleManifest

# ---------------------------------------------------------------------------
# Secret-pattern keywords scanned against declared file paths
# ---------------------------------------------------------------------------
_SECRET_PATTERNS = [
    "aws_secret",
    "api_key",
    ".env",
    "id_rsa",
    "credentials.json",
]


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class RuleResult:
    """Result of a single gate rule evaluation."""

    rule_id: str
    passed: bool
    reason: str


@dataclass
class GateResult:
    """Aggregated result of evaluating all rules against a bundle."""

    bundle_id: str
    overall_passed: bool
    rule_results: List[RuleResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Individual rule implementations
# ---------------------------------------------------------------------------


def _rule_tests_present(bundle: ReleaseBundleManifest) -> RuleResult:
    passed = len(bundle.test_runs) > 0
    return RuleResult(
        rule_id="RULE_TESTS_PRESENT",
        passed=passed,
        reason=(
            "At least one test run is declared."
            if passed
            else "No test runs declared in bundle — cannot assess test coverage."
        ),
    )


def _rule_no_failing_tests(bundle: ReleaseBundleManifest) -> RuleResult:
    failures = [tr for tr in bundle.test_runs if tr.claimed_failed != 0]
    passed = len(failures) == 0
    if passed:
        reason = "All declared test runs report zero failures."
    else:
        names = ", ".join(tr.suite_name for tr in failures)
        reason = f"Test run(s) with claimed failures: {names}."
    return RuleResult(rule_id="RULE_NO_FAILING_TESTS", passed=passed, reason=reason)


def _rule_test_evidence(bundle: ReleaseBundleManifest) -> RuleResult:
    """Any test run with claimed_passed > 0 must have evidence_url OR must not
    be self_certified — catches fake green where an agent claims passes with no
    external proof and marks it self-certified."""
    violators = [
        tr
        for tr in bundle.test_runs
        if tr.claimed_passed > 0
        and tr.self_certified
        and not tr.evidence_url
    ]
    passed = len(violators) == 0
    if passed:
        reason = "All test runs with claimed passes either have evidence URLs or are not self-certified."
    else:
        names = ", ".join(tr.suite_name for tr in violators)
        reason = (
            f"Self-certified test run(s) claim passes but provide no evidence URL "
            f"(fake-green risk): {names}."
        )
    return RuleResult(rule_id="RULE_TEST_EVIDENCE", passed=passed, reason=reason)


def _rule_no_self_certified_green(bundle: ReleaseBundleManifest) -> RuleResult:
    """If overall status is 'green', no individual test run may be self-certified.
    Self-certification by the producing agent on a green claim is an adversarial
    risk — the same entity that produced the work is vouching for its own quality."""
    if bundle.claimed_status != "green":
        return RuleResult(
            rule_id="RULE_NO_SELF_CERTIFIED_GREEN",
            passed=True,
            reason="Claimed status is not 'green'; self-certification check skipped.",
        )
    self_certified_runs = [tr for tr in bundle.test_runs if tr.self_certified]
    passed = len(self_certified_runs) == 0
    if passed:
        reason = "Green status claimed and no test runs are self-certified."
    else:
        names = ", ".join(tr.suite_name for tr in self_certified_runs)
        reason = (
            f"Claimed status is 'green' but test run(s) are self-certified "
            f"(adversarial risk — producer cannot certify own release): {names}."
        )
    return RuleResult(
        rule_id="RULE_NO_SELF_CERTIFIED_GREEN", passed=passed, reason=reason
    )


def _rule_adversarial_review(bundle: ReleaseBundleManifest) -> RuleResult:
    passed = bundle.adversarial_review_present
    return RuleResult(
        rule_id="RULE_ADVERSARIAL_REVIEW",
        passed=passed,
        reason=(
            "Adversarial review is marked present."
            if passed
            else (
                "No adversarial review present — a distinct-model auditor must "
                "sign off before release (adversarial_review_present=False)."
            )
        ),
    )


def _rule_artifacts_present(bundle: ReleaseBundleManifest) -> RuleResult:
    passed = len(bundle.artifacts) > 0
    return RuleResult(
        rule_id="RULE_ARTIFACTS_PRESENT",
        passed=passed,
        reason=(
            f"{len(bundle.artifacts)} artifact(s) declared."
            if passed
            else "No artifacts declared — release bundle is empty."
        ),
    )


def _rule_version_bump(bundle: ReleaseBundleManifest) -> RuleResult:
    blocked = {"0.0.0", "UNSET", ""}
    stripped = bundle.version.strip()
    passed = stripped not in blocked
    return RuleResult(
        rule_id="RULE_VERSION_BUMP",
        passed=passed,
        reason=(
            f"Version '{bundle.version}' is set and non-trivial."
            if passed
            else (
                f"Version '{bundle.version}' is a placeholder or empty — "
                "increment the version before release."
            )
        ),
    )


def _rule_changelog(bundle: ReleaseBundleManifest) -> RuleResult:
    passed = bool(bundle.changelog_entry and bundle.changelog_entry.strip())
    return RuleResult(
        rule_id="RULE_CHANGELOG",
        passed=passed,
        reason=(
            "Changelog entry is present and non-empty."
            if passed
            else "changelog_entry is missing or empty — document what changed."
        ),
    )


def _rule_no_secrets(bundle: ReleaseBundleManifest) -> RuleResult:
    """Scan declared file paths for common secret-pattern strings.

    This is a path-level heuristic — it catches cases where a developer has
    declared a secrets file as part of the bundle without realising it (e.g.,
    ``config/AWS_SECRET_KEY.env``). Full content scanning is out of scope here.
    """
    flagged = []
    for path in bundle.declared_files:
        path_lower = path.lower()
        for pattern in _SECRET_PATTERNS:
            if pattern in path_lower:
                flagged.append(path)
                break  # one match per path is enough

    passed = len(flagged) == 0
    if passed:
        reason = "No secret-pattern strings detected in declared file paths."
    else:
        reason = (
            f"Declared file path(s) match secret patterns "
            f"({', '.join(flagged)}) — remove or exclude before release."
        )
    return RuleResult(rule_id="RULE_NO_SECRETS", passed=passed, reason=reason)


# ---------------------------------------------------------------------------
# Public evaluator
# ---------------------------------------------------------------------------

_RULES = [
    _rule_tests_present,
    _rule_no_failing_tests,
    _rule_test_evidence,
    _rule_no_self_certified_green,
    _rule_adversarial_review,
    _rule_artifacts_present,
    _rule_version_bump,
    _rule_changelog,
    _rule_no_secrets,
]


def evaluate_release(bundle: ReleaseBundleManifest) -> GateResult:
    """Evaluate a :class:`ReleaseBundleManifest` against all adversarial rules.

    Returns a :class:`GateResult` with ``overall_passed=True`` only when every
    rule passes. Designed to be deterministic and fully offline — no network
    calls, no file reads beyond what the bundle explicitly declares.

    Args:
        bundle: The release bundle manifest to evaluate.

    Returns:
        A :class:`GateResult` containing per-rule results and the aggregate verdict.
    """
    rule_results = [rule(bundle) for rule in _RULES]
    overall_passed = all(r.passed for r in rule_results)
    return GateResult(
        bundle_id=bundle.bundle_id,
        overall_passed=overall_passed,
        rule_results=rule_results,
    )
