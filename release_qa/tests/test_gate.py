"""Pytest tests for the adversarial release-QA gate engine.

Tests are deterministic and fully offline — no network calls, no file I/O.
Each fixture exercises one failure mode; ``clean_bundle`` is the only fixture
expected to pass overall.
"""
from __future__ import annotations

import pytest

from release_qa import (
    ArtifactDeclaration,
    ReleaseBundleManifest,
    TestRunRecord,
    evaluate_release,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _artifact() -> ArtifactDeclaration:
    return ArtifactDeclaration(name="gate-module", path="release_qa/rules.py")


def _passing_test_run(
    *,
    suite_name: str = "unit",
    self_certified: bool = False,
    evidence_url: str = "https://ci.example.com/runs/1",
) -> TestRunRecord:
    return TestRunRecord(
        suite_name=suite_name,
        claimed_passed=8,
        claimed_failed=0,
        evidence_url=evidence_url,
        self_certified=self_certified,
    )


def clean_bundle() -> ReleaseBundleManifest:
    """All rules pass: tests with evidence, no failures, adversarial review,
    artifacts, a real version, a changelog entry, no secrets in paths."""
    return ReleaseBundleManifest(
        bundle_id="clean-bundle-001",
        version="1.0.0",
        changelog_entry="Initial adversarial QA gate implementation.",
        artifacts=[_artifact()],
        test_runs=[_passing_test_run()],
        claimed_status="green",
        adversarial_review_present=True,
        declared_files=["release_qa/rules.py", "release_qa/models.py"],
    )


def fake_green_bundle() -> ReleaseBundleManifest:
    """claimed_status=green, self_certified=True on a test run with
    claimed_passed>0 but no evidence_url — the canonical fake-green pattern."""
    return ReleaseBundleManifest(
        bundle_id="fake-green-bundle-001",
        version="1.0.0",
        changelog_entry="Some changes.",
        artifacts=[_artifact()],
        test_runs=[
            TestRunRecord(
                suite_name="unit",
                claimed_passed=5,
                claimed_failed=0,
                evidence_url=None,   # no evidence
                self_certified=True,  # producer vouches for self
            )
        ],
        claimed_status="green",
        adversarial_review_present=True,
        declared_files=[],
    )


def missing_artifact_bundle() -> ReleaseBundleManifest:
    """artifacts=[] — bundle declares no deliverables."""
    return ReleaseBundleManifest(
        bundle_id="no-artifacts-bundle-001",
        version="1.0.0",
        changelog_entry="Some changes.",
        artifacts=[],
        test_runs=[_passing_test_run()],
        claimed_status="green",
        adversarial_review_present=True,
        declared_files=[],
    )


def self_certified_bundle() -> ReleaseBundleManifest:
    """claimed_status='green', test run is self_certified — triggers
    RULE_NO_SELF_CERTIFIED_GREEN regardless of evidence URL."""
    return ReleaseBundleManifest(
        bundle_id="self-certified-bundle-001",
        version="1.0.0",
        changelog_entry="Some changes.",
        artifacts=[_artifact()],
        test_runs=[
            _passing_test_run(self_certified=True, evidence_url="https://ci.example.com/runs/2")
        ],
        claimed_status="green",
        adversarial_review_present=True,
        declared_files=[],
    )


def secret_in_bundle() -> ReleaseBundleManifest:
    """declared_files contains a path matching a secret pattern."""
    return ReleaseBundleManifest(
        bundle_id="secret-bundle-001",
        version="1.0.0",
        changelog_entry="Some changes.",
        artifacts=[_artifact()],
        test_runs=[_passing_test_run()],
        claimed_status="green",
        adversarial_review_present=True,
        declared_files=["config/AWS_SECRET_KEY.env", "release_qa/rules.py"],
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_clean_bundle_passes() -> None:
    result = evaluate_release(clean_bundle())
    assert result.overall_passed is True, (
        "Expected clean bundle to pass all rules. "
        f"Failed: {[r for r in result.rule_results if not r.passed]}"
    )


def test_fake_green_fails() -> None:
    result = evaluate_release(fake_green_bundle())
    assert result.overall_passed is False

    failed_ids = {r.rule_id for r in result.rule_results if not r.passed}
    # Must fail at least one of the fake-green detection rules
    assert failed_ids & {"RULE_TEST_EVIDENCE", "RULE_NO_SELF_CERTIFIED_GREEN"}, (
        f"Expected RULE_TEST_EVIDENCE or RULE_NO_SELF_CERTIFIED_GREEN to fail. "
        f"Actually failed: {failed_ids}"
    )


def test_missing_artifact_fails() -> None:
    result = evaluate_release(missing_artifact_bundle())
    assert result.overall_passed is False

    failed_ids = {r.rule_id for r in result.rule_results if not r.passed}
    assert "RULE_ARTIFACTS_PRESENT" in failed_ids, (
        f"Expected RULE_ARTIFACTS_PRESENT to fail. Actually failed: {failed_ids}"
    )


def test_self_certified_status_flagged() -> None:
    result = evaluate_release(self_certified_bundle())
    assert result.overall_passed is False

    failed_ids = {r.rule_id for r in result.rule_results if not r.passed}
    assert "RULE_NO_SELF_CERTIFIED_GREEN" in failed_ids, (
        f"Expected RULE_NO_SELF_CERTIFIED_GREEN to fail. Actually failed: {failed_ids}"
    )


def test_secret_in_bundle_flagged() -> None:
    result = evaluate_release(secret_in_bundle())
    assert result.overall_passed is False

    failed_ids = {r.rule_id for r in result.rule_results if not r.passed}
    assert "RULE_NO_SECRETS" in failed_ids, (
        f"Expected RULE_NO_SECRETS to fail. Actually failed: {failed_ids}"
    )


def test_no_tests_fails() -> None:
    bundle = ReleaseBundleManifest(
        bundle_id="no-tests-bundle-001",
        version="1.0.0",
        changelog_entry="Some changes.",
        artifacts=[_artifact()],
        test_runs=[],
        claimed_status="yellow",
        adversarial_review_present=True,
        declared_files=[],
    )
    result = evaluate_release(bundle)
    assert result.overall_passed is False

    failed_ids = {r.rule_id for r in result.rule_results if not r.passed}
    assert "RULE_TESTS_PRESENT" in failed_ids, (
        f"Expected RULE_TESTS_PRESENT to fail. Actually failed: {failed_ids}"
    )


def test_missing_changelog_fails() -> None:
    bundle = ReleaseBundleManifest(
        bundle_id="no-changelog-bundle-001",
        version="1.0.0",
        changelog_entry=None,
        artifacts=[_artifact()],
        test_runs=[_passing_test_run()],
        claimed_status="green",
        adversarial_review_present=True,
        declared_files=[],
    )
    result = evaluate_release(bundle)
    assert result.overall_passed is False

    failed_ids = {r.rule_id for r in result.rule_results if not r.passed}
    assert "RULE_CHANGELOG" in failed_ids, (
        f"Expected RULE_CHANGELOG to fail. Actually failed: {failed_ids}"
    )


def test_adversarial_review_required() -> None:
    bundle = ReleaseBundleManifest(
        bundle_id="no-review-bundle-001",
        version="1.0.0",
        changelog_entry="Some changes.",
        artifacts=[_artifact()],
        test_runs=[_passing_test_run()],
        claimed_status="green",
        adversarial_review_present=False,
        declared_files=[],
    )
    result = evaluate_release(bundle)
    assert result.overall_passed is False

    failed_ids = {r.rule_id for r in result.rule_results if not r.passed}
    assert "RULE_ADVERSARIAL_REVIEW" in failed_ids, (
        f"Expected RULE_ADVERSARIAL_REVIEW to fail. Actually failed: {failed_ids}"
    )
