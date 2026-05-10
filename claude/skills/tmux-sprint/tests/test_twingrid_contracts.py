from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import tempfile
import unittest


SCRIPT = (
    pathlib.Path(__file__).resolve().parents[1]
    / "scripts"
    / "twingrid_contracts.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("twingrid_contracts", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TwinGridContractsTests(unittest.TestCase):
    def test_freeze_record_includes_manifest_paths_and_receipts(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp)
            (folder / "agent_record.json").write_text(
                json.dumps(
                    {
                        "lane": "dan",
                        "side": "A",
                        "runtime": "gpt55",
                        "task": "contract helpers",
                    }
                ),
                encoding="utf-8",
            )
            (folder / "artifact_summary.md").write_text("# summary\n", encoding="utf-8")
            (folder / "skill_findings.md").write_text("# findings\n", encoding="utf-8")

            data = module.freeze_record(
                argparse.Namespace(
                    output_folder=str(folder),
                    round=9,
                    lane="",
                    side="",
                    runtime="",
                    task="",
                )
            )

        self.assertEqual(data["state"], "BLIND_FROZEN")
        self.assertEqual(data["lane"], "dan")
        self.assertEqual(data["side"], "A")
        self.assertEqual(data["runtime"], "gpt55")
        self.assertEqual(data["task"], "contract helpers")
        self.assertEqual(data["canonical_skill_findings"], "skill_findings.md")
        self.assertFalse(data["partner_output_read"])
        self.assertFalse(data["existing_blind_artifacts_modified"])
        self.assertIn("agent_record.json", data["blind_artifact_sha256"])
        self.assertIn("artifact_summary.md", data["blind_artifact_sha256"])
        self.assertTrue(data["paths"]["artifact_summary"].endswith("artifact_summary.md"))
        self.assertTrue(data["paths"]["skill_findings"].endswith("skill_findings.md"))


if __name__ == "__main__":
    unittest.main()
