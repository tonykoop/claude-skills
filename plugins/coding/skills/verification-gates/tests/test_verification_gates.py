#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "verification_gates.py"


def load_module():
    spec = importlib.util.spec_from_file_location("verification_gates", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["verification_gates"] = module
    spec.loader.exec_module(module)
    return module


gates = load_module()


class VerificationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="verification-gates-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.artifact = self.tmp / "artifact"
        self.artifact.mkdir()

    def run_cli(self, *extra: str) -> tuple[int, dict]:
        output = self.tmp / "qa-decision.json"
        argv = [
            "verification_gates.py",
            "--path",
            str(self.artifact),
            "--qa-output",
            str(output),
            *extra,
        ]
        old_argv, sys.argv = sys.argv, argv
        try:
            rc = gates.main()
        finally:
            sys.argv = old_argv
        return rc, json.loads(output.read_text(encoding="utf-8"))

    def test_passes_markdown_urdf_and_command(self) -> None:
        (self.artifact / "README.md").write_text("# Robot\n\nClean text.\n", encoding="utf-8")
        (self.artifact / "robot.urdf").write_text(
            """<robot name="fixture">
  <joint name="elbow" type="revolute">
    <limit lower="-1.57" upper="1.57" effort="10" velocity="2"/>
  </joint>
</robot>
""",
            encoding="utf-8",
        )
        rc, doc = self.run_cli("--command", f"{sys.executable} -c print(42)")
        self.assertEqual(rc, 0)
        self.assertEqual(doc["decision"], "pass")
        gates_seen = {check["gate"] for check in doc["checks"] if check["status"] == "pass"}
        self.assertIn("sandbox-exec", gates_seen)
        self.assertIn("markdown-length", gates_seen)
        self.assertIn("urdf-joint-limits", gates_seen)

    def test_fails_runtime_error_and_bad_urdf_limit(self) -> None:
        (self.artifact / "README.md").write_text("# Robot\n", encoding="utf-8")
        (self.artifact / "robot.urdf").write_text(
            """<robot name="fixture">
  <joint name="slide" type="prismatic">
    <limit lower="5" upper="1" effort="10" velocity="2"/>
  </joint>
</robot>
""",
            encoding="utf-8",
        )
        rc, doc = self.run_cli("--command", f"{sys.executable} -c \"raise SystemExit(7)\"")
        self.assertEqual(rc, 1)
        self.assertEqual(doc["decision"], "fail")
        details = "\n".join(check["detail"] for check in doc["checks"])
        self.assertIn("exit 7", details)
        self.assertIn("lower 5 exceeds upper 1", details)

    def test_fails_markdown_length(self) -> None:
        (self.artifact / "README.md").write_text("# " + ("x" * 30) + "\n", encoding="utf-8")
        rc, doc = self.run_cli("--max-line-length", "10")
        self.assertEqual(rc, 1)
        self.assertEqual(doc["decision"], "fail")
        self.assertIn("max is 10", "\n".join(check["detail"] for check in doc["checks"]))


if __name__ == "__main__":
    unittest.main()
