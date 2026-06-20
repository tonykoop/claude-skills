# release_qa — Adversarial Release-QA Gate Engine

A deterministic, offline Python module that evaluates agent-produced release
bundles against a set of adversarial rules before they are allowed to deploy.

## What the gate does

The gate takes a `ReleaseBundleManifest` — a structured declaration of what an
agent claims to have built, tested, and reviewed — and runs it through nine
independent rule checks. Every rule must pass for `overall_passed` to be `True`.
The design is deliberately strict: it is better to block a legitimate release
with a false positive than to allow a "fake green" through.

## Adversarial rules and why they catch fake green

| Rule ID | What it checks | Why it exists |
|---|---|---|
| `RULE_TESTS_PRESENT` | At least one `TestRunRecord` in `test_runs` | An agent that skips tests entirely still produces a release artefact |
| `RULE_NO_FAILING_TESTS` | `claimed_failed == 0` for every test run | Catches obvious failures that were declared but ignored |
| `RULE_TEST_EVIDENCE` | Any run with `claimed_passed > 0` must have `evidence_url` OR not be `self_certified` | The canonical fake-green pattern: agent reports green with no external proof |
| `RULE_NO_SELF_CERTIFIED_GREEN` | When `claimed_status == "green"`, no test run may be `self_certified` | The producing agent cannot vouch for its own quality on a green claim |
| `RULE_ADVERSARIAL_REVIEW` | `adversarial_review_present` must be `True` | Enforces that a distinct-model auditor reviewed the bundle |
| `RULE_ARTIFACTS_PRESENT` | `artifacts` list must be non-empty | A release with no declared deliverables is a shell |
| `RULE_VERSION_BUMP` | `version` is non-empty, not `"0.0.0"`, not `"UNSET"` | Placeholder versions indicate an incomplete release process |
| `RULE_CHANGELOG` | `changelog_entry` is non-None and non-empty | Every release must document what changed |
| `RULE_NO_SECRETS` | Declared file paths scanned for secret-pattern strings | Catches accidental inclusion of credential files in the bundle |

### The fake-green threat model

Agents trained to satisfy objectives can learn to report success without
actually succeeding. The two most common patterns are:

1. **Self-certified green** — the agent that produced the work also marks the
   test run as `self_certified=True` and claims `claimed_status="green"`.
   `RULE_TEST_EVIDENCE` and `RULE_NO_SELF_CERTIFIED_GREEN` together close this
   gap.

2. **Evidence-free passes** — `claimed_passed > 0` with no `evidence_url` and
   `self_certified=True`. Without a URL pointing to an external CI run, the
   claim is unfalsifiable. `RULE_TEST_EVIDENCE` catches this.

## Integration with the studio-release skill

The `studio-release` skill (in `plugins/coding/skills/studio-release/`) is the
**orchestration layer**: it drives the end-to-end release workflow — confirming
the source path, running `studio_release_gate.py`, assigning a distinct-model
auditor, and producing an approve/deploy ticket.

`release_qa` is the **logic layer**: a pure Python library that the gate script
(or any other tool) can import to evaluate a manifest. It has no I/O
dependencies, no network calls, and no side effects — making it suitable for
unit testing and for embedding inside larger automation pipelines.

The typical integration point is inside the gate script or a CI step that
constructs a `ReleaseBundleManifest` from the bundle outputs and calls
`evaluate_release()`. If the result is not `overall_passed`, the gate exits
non-zero and the release is blocked.

## Usage

```python
from release_qa import evaluate_release, ReleaseBundleManifest
from release_qa import ArtifactDeclaration, TestRunRecord

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
print(result.overall_passed)   # True

for r in result.rule_results:
    status = "PASS" if r.passed else "FAIL"
    print(f"[{status}] {r.rule_id}: {r.reason}")
```

## Running the tests

```bash
pip install pydantic pytest
python -m pytest release_qa/tests/ -v
```

All 8 tests are deterministic and offline — no network access, no file reads.
