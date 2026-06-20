"""release_qa — adversarial release-QA gate engine.

Provides deterministic, offline gate evaluation for agent-produced release
bundles. Import the two key symbols::

    from release_qa import evaluate_release, ReleaseBundleManifest

    manifest = ReleaseBundleManifest(
        bundle_id="my-bundle-001",
        version="1.2.0",
        changelog_entry="Add the adversarial QA gate.",
        artifacts=[ArtifactDeclaration(name="gate", path="release_qa/rules.py")],
        test_runs=[
            TestRunRecord(
                suite_name="unit",
                claimed_passed=8,
                claimed_failed=0,
                evidence_url="https://ci.example.com/runs/42",
                self_certified=False,
            )
        ],
        claimed_status="green",
        adversarial_review_present=True,
        declared_files=["release_qa/rules.py"],
    )

    result = evaluate_release(manifest)
    print(result.overall_passed)          # True
    for r in result.rule_results:
        print(r.rule_id, r.passed)
"""

from release_qa.models import (
    ArtifactDeclaration,
    ReleaseBundleManifest,
    TestRunRecord,
)
from release_qa.rules import GateResult, RuleResult, evaluate_release

__all__ = [
    "ArtifactDeclaration",
    "ReleaseBundleManifest",
    "TestRunRecord",
    "RuleResult",
    "GateResult",
    "evaluate_release",
]
