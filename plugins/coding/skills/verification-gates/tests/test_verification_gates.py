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
    <parent link="base"/>
    <child link="arm"/>
    <axis xyz="0 0 1"/>
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
        self.assertIn("markdown:max-line-length", gates_seen)
        self.assertIn("urdf-joint-limits", gates_seen)
        command_check = next(check for check in doc["checks"] if check["gate"] == "sandbox-exec")
        self.assertEqual(command_check["metadata"]["exit_code"], 0)
        self.assertIn("-c", command_check["metadata"]["argv"])

    def test_fails_runtime_error_and_bad_urdf_limit(self) -> None:
        (self.artifact / "README.md").write_text("# Robot\n", encoding="utf-8")
        (self.artifact / "robot.urdf").write_text(
            """<robot name="fixture">
  <joint name="slide" type="prismatic">
    <parent link="base"/>
    <child link="carriage"/>
    <axis xyz="1 0 0"/>
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
        command_check = next(check for check in doc["checks"] if check["gate"] == "sandbox-exec")
        self.assertEqual(command_check["metadata"]["exit_code"], 7)

    def test_fails_markdown_length(self) -> None:
        (self.artifact / "README.md").write_text("# " + ("x" * 30) + "\n", encoding="utf-8")
        rc, doc = self.run_cli("--max-line-length", "10")
        self.assertEqual(rc, 1)
        self.assertEqual(doc["decision"], "fail")
        self.assertIn("max is 10", "\n".join(check["detail"] for check in doc["checks"]))
        failed = {check["gate"] for check in doc["checks"] if check["status"] == "fail"}
        self.assertEqual(failed, {"markdown:max-line-length"})

    def test_markdown_matrix_reports_multiple_rules(self) -> None:
        (self.artifact / "README.md").write_text("#Bad\n\n```python\nprint('open')\n", encoding="utf-8")
        rc, doc = self.run_cli()
        self.assertEqual(rc, 1)
        failed = {check["gate"] for check in doc["checks"] if check["status"] == "fail"}
        self.assertIn("markdown:heading-spacing", failed)
        self.assertIn("markdown:fenced-code-closure", failed)

    def test_fails_urdf_mimic_axis_parent_child_and_continuous_limit(self) -> None:
        (self.artifact / "robot.urdf").write_text(
            """<robot name="fixture">
  <joint name="bad_revolute" type="revolute">
    <limit lower="-1" upper="1" effort="1" velocity="1"/>
    <mimic joint="missing_joint"/>
  </joint>
  <joint name="spin" type="continuous">
    <parent link="base"/>
    <child link="wheel"/>
    <limit lower="-3" upper="3"/>
  </joint>
</robot>
""",
            encoding="utf-8",
        )
        rc, doc = self.run_cli()
        self.assertEqual(rc, 1)
        details = "\n".join(check["detail"] for check in doc["checks"])
        self.assertIn("requires parent and child", details)
        self.assertIn("requires <axis>", details)
        self.assertIn("mimics missing joint", details)
        self.assertIn("continuous joint spin must not define <limit>", details)

    def test_fails_missing_command_with_metadata(self) -> None:
        rc, doc = self.run_cli("--command", "definitely-not-a-real-command")
        self.assertEqual(rc, 1)
        check = next(item for item in doc["checks"] if item["gate"] == "sandbox-exec")
        self.assertEqual(check["metadata"]["argv"], ["definitely-not-a-real-command"])
        self.assertIsNone(check["metadata"]["exit_code"])


if __name__ == "__main__":
    unittest.main()
