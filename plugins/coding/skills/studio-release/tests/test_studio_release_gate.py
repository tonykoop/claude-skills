#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "studio_release_gate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("studio_release_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["studio_release_gate"] = module
    spec.loader.exec_module(module)
    return module


gate = load_module()


class StudioReleaseGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="studio-release-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.source = self.tmp / "source"
        self.source.mkdir()
        subprocess.run(["git", "init"], cwd=self.source, check=True, stdout=subprocess.PIPE)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.source, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.source, check=True)

    def commit_source(self) -> None:
        subprocess.run(["git", "add", "."], cwd=self.source, check=True)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=self.source, check=True, stdout=subprocess.PIPE)

    def run_gate(self, *extra: str) -> tuple[int, Path, str]:
        staging = self.tmp / "staging"
        argv = [
            "studio_release_gate.py",
            "--source",
            str(self.source),
            "--staging-root",
            str(staging),
            "--ticket-title",
            "Approve Deploy Fixture",
            "--ref",
            "PR #1",
            *extra,
        ]
        old_argv, sys.argv = sys.argv, argv
        try:
            rc = gate.main()
        finally:
            sys.argv = old_argv
        bundles = sorted(staging.iterdir())
        self.assertEqual(len(bundles), 1)
        return rc, bundles[0], (bundles[0] / "approve-deploy-ticket.md").read_text(encoding="utf-8")

    def test_passes_and_stages_bundle_for_clean_source(self) -> None:
        (self.source / "SKILL.md").write_text(
            "---\nname: fixture\ndescription: fixture skill\n---\n\n# Fixture\n",
            encoding="utf-8",
        )
        (self.source / "script.py").write_text("print('ok')\n", encoding="utf-8")
        self.commit_source()

        rc, bundle, ticket = self.run_gate()
        self.assertEqual(rc, 0)
        decision = json.loads((bundle / "qa-decision.json").read_text(encoding="utf-8"))
        self.assertEqual(decision["decision"], "pass")
        self.assertEqual(decision["routing"], gate.ROUTING_AUTO)
        self.assertGreaterEqual(decision["confidence"], 0.9)
        self.assertTrue((bundle / "source" / "SKILL.md").exists())
        self.assertIn("Studio Release gate decision: `pass`", ticket)
        self.assertIn("Reference: `PR #1`", ticket)

    def test_fails_on_markdown_trailing_whitespace(self) -> None:
        (self.source / "README.md").write_text("# Bad   \n", encoding="utf-8")
        self.commit_source()

        rc, bundle, ticket = self.run_gate()
        self.assertEqual(rc, 1)
        decision = json.loads((bundle / "qa-decision.json").read_text(encoding="utf-8"))
        self.assertEqual(decision["decision"], "fail")
        self.assertEqual(decision["routing"], gate.ROUTING_BLOCKED)
        self.assertEqual(decision["confidence"], 0.0)
        self.assertIn("trailing whitespace", ticket)

    def test_publish_manifest_indexes_artifacts_with_checksums(self) -> None:
        (self.source / "SKILL.md").write_text(
            "---\nname: fixture\ndescription: fixture skill\n---\n\n# Fixture\n",
            encoding="utf-8",
        )
        self.commit_source()

        rc, bundle, _ = self.run_gate("--deploy-target", "studio-pipeline")
        self.assertEqual(rc, 0)
        manifest = json.loads((bundle / "publish-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["deploy_target"], "studio-pipeline")
        self.assertTrue(manifest["human_approval_required"])
        self.assertGreaterEqual(manifest["artifact_count"], 1)
        skill = next(a for a in manifest["artifacts"] if a["path"] == "SKILL.md")
        self.assertEqual(len(skill["sha256"]), 64)
        self.assertGreater(skill["bytes"], 0)

    def test_dirty_source_warning_escalates_for_human_review(self) -> None:
        (self.source / "SKILL.md").write_text(
            "---\nname: fixture\ndescription: fixture skill\n---\n\n# Fixture\n",
            encoding="utf-8",
        )
        self.commit_source()
        # Leave an uncommitted change so git-state reports dirty.
        (self.source / "SKILL.md").write_text(
            "---\nname: fixture\ndescription: fixture skill\n---\n\n# Fixture edited\n",
            encoding="utf-8",
        )

        rc, bundle, ticket = self.run_gate("--allow-dirty")
        self.assertEqual(rc, 0)  # warnings do not fail the gate
        decision = json.loads((bundle / "qa-decision.json").read_text(encoding="utf-8"))
        self.assertEqual(decision["decision"], "pass")
        self.assertEqual(decision["routing"], gate.ROUTING_ESCALATE)
        self.assertLess(decision["confidence"], 0.9)
        self.assertIn("escalated for human review", ticket)

    def test_auditor_skipped_without_creator_identity(self) -> None:
        (self.source / "SKILL.md").write_text(
            "---\nname: fixture\ndescription: fixture skill\n---\n\n# Fixture\n",
            encoding="utf-8",
        )
        self.commit_source()

        _, bundle, ticket = self.run_gate()
        decision = json.loads((bundle / "qa-decision.json").read_text(encoding="utf-8"))
        self.assertEqual(decision["auditor"]["status"], "skipped")
        self.assertIn("Adversarial QA auditor: skipped", ticket)

    def _write_roster(self) -> Path:
        roster_dir = self.tmp / "governance"
        roster_dir.mkdir()
        (roster_dir / "spend_guard.py").write_text(
            textwrap.dedent(
                '''
                import yaml
                def load_roster(path=None):
                    with open(path, "r", encoding="utf-8") as fh:
                        return yaml.safe_load(fh)
                '''
            ).lstrip(),
            encoding="utf-8",
        )
        # Copy the real review_router so we test against the shipped routing logic.
        real_router = Path(__file__).resolve().parents[5] / "governance" / "review_router.py"
        shutil.copy2(real_router, roster_dir / "review_router.py")
        (roster_dir / "agent-roster.yaml").write_text(
            textwrap.dedent(
                """
                schema_version: 1
                model_families:
                  claude-opus-4-8: opus
                  codex-gpt-5.5: gpt-5.5
                agents:
                  alice:
                    model: claude-opus-4-8
                    can_audit: true
                  dan:
                    model: codex-gpt-5.5
                    can_audit: true
                review_policy:
                  enabled: true
                  require_distinct_agent: true
                  require_distinct_family: true
                  on_no_auditor: block
                """
            ).lstrip(),
            encoding="utf-8",
        )
        return roster_dir

    def test_auditor_assigned_to_distinct_model_family(self) -> None:
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("pyyaml not installed")
        (self.source / "SKILL.md").write_text(
            "---\nname: fixture\ndescription: fixture skill\n---\n\n# Fixture\n",
            encoding="utf-8",
        )
        self.commit_source()
        roster_dir = self._write_roster()

        rc, bundle, ticket = self.run_gate(
            "--creator-agent",
            "alice",
            "--creator-model",
            "claude-opus-4-8",
            "--roster",
            str(roster_dir),
        )
        self.assertEqual(rc, 0)
        decision = json.loads((bundle / "qa-decision.json").read_text(encoding="utf-8"))
        self.assertEqual(decision["auditor"]["status"], "assigned")
        self.assertEqual(decision["auditor"]["auditor"], "dan")  # distinct family
        self.assertIn("Adversarial QA auditor assigned: `dan`", ticket)


if __name__ == "__main__":
    unittest.main()
