from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile
import unittest


SCRIPT = (
    pathlib.Path(__file__).resolve().parents[1]
    / "scripts"
    / "twingrid_matrix.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("twingrid_matrix", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TwinGridMatrixTests(unittest.TestCase):
    def test_collects_partner_peek_record_and_v2_artifacts(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            out = root / "twingrid-r7-codex-henry-pack-basket"
            out.mkdir()
            (out / "agent_record.json").write_text(
                json.dumps(
                    {
                        "lane": "henry",
                        "side": "B",
                        "runtime": "codex",
                        "artifacts_produced": ["reverse_engineering_report.md"],
                        "validation_run": ["jq . agent_record.json"],
                    }
                ),
                encoding="utf-8",
            )
            (out / "partner-peek-record.json").write_text(
                json.dumps(
                    {
                        "lane": "henry",
                        "side": "B",
                        "runtime": "codex",
                        "validation_run": ["yamllint v2-validation-gates.yaml"],
                        "skill_improvement_recommendation": "Add image preflight",
                        "pr_or_issues_opened": "None",
                    }
                ),
                encoding="utf-8",
            )
            (out / "partner-peek-improvements.md").write_text("# memo\n", encoding="utf-8")
            (out / "v2-validation-gates.yaml").write_text("---\nok: true\n", encoding="utf-8")

            lanes = module.scan_outputs(str(root / "twingrid-r7-*"))
            pairs = module.build_lane_pairs(lanes)

        self.assertEqual(len(lanes), 1)
        self.assertEqual(len(pairs), 1)
        lane = lanes[0]
        self.assertEqual(lane["lane"], "henry")
        self.assertEqual(lane["side"], "B")
        self.assertEqual(lane["runtime"], "codex")
        self.assertIn("partner-peek-improvements.md", lane["v2_artifacts"])
        self.assertIn("v2-validation-gates.yaml", lane["v2_artifacts"])
        self.assertEqual(lane["skill_recommendation"], "Add image preflight")
        self.assertEqual(len(lane["validation_run"]), 2)
        self.assertEqual(
            pairs[0]["sides"]["B"]["output_folder"],
            str(out),
        )

    def test_detects_approval_and_missing_tool_blocks(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "pane-1.txt").write_text(
                "Do you want to allow npm install?\n", encoding="utf-8"
            )
            (root / "pane-2.txt").write_text(
                "yamllint: command not found\n", encoding="utf-8"
            )

            findings = module.scan_blocked(str(root))

        self.assertEqual([item["block_type"] for item in findings], [
            "approval_prompt",
            "missing_tool",
        ])


if __name__ == "__main__":
    unittest.main()
