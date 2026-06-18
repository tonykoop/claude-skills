#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
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
        self.assertIn("trailing whitespace", ticket)


if __name__ == "__main__":
    unittest.main()
