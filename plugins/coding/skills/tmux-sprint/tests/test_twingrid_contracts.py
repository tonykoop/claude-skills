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

    def test_freeze_record_reads_markdown_agent_record(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp)
            (folder / "agent_record.md").write_text(
                "\n".join(
                    [
                        "# Agent Record",
                        "",
                        "- Lane: elsa",
                        "- Side: B",
                        "- Runtime: gpt54-window-12",
                        "- Task: Yaybahar resonance test rig",
                    ]
                ),
                encoding="utf-8",
            )

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

        self.assertEqual(data["lane"], "elsa")
        self.assertEqual(data["side"], "B")
        self.assertEqual(data["runtime"], "gpt54-window-12")
        self.assertEqual(data["task"], "Yaybahar resonance test rig")

    def test_freeze_record_recurses_nested_artifacts(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp)
            nested = folder / "drawings"
            nested.mkdir()
            (nested / "plate.svg").write_text("<svg />\n", encoding="utf-8")

            data = module.freeze_record(
                argparse.Namespace(
                    output_folder=str(folder),
                    round=9,
                    lane="dan",
                    side="A",
                    runtime="gpt55",
                    task="nested manifest",
                )
            )

        self.assertIn("drawings/plate.svg", data["blind_artifact_sha256"])
        self.assertEqual(
            [entry["name"] for entry in data["blind_artifact_manifest"]],
            ["drawings/plate.svg"],
        )

    def test_peek_record_includes_combine_recommendation_schema(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            own = root / "own"
            partner = root / "partner"
            own.mkdir()
            partner.mkdir()
            (partner / "ready_for_peek.json").write_text(
                json.dumps({"state": "BLIND_FROZEN"}),
                encoding="utf-8",
            )
            (own / "combine_recommendation.md").write_text("# combine\n", encoding="utf-8")

            exit_code = module.cmd_peek_record(
                argparse.Namespace(
                    output_folder=str(own),
                    partner_folder=str(partner),
                    round=9,
                    lane="dan",
                    side="A",
                    runtime="gpt55",
                    task="peek schema",
                    force=False,
                )
            )
            data = json.loads((own / "partner-peek-record.json").read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertIn("combine_recommendation", data)
        self.assertEqual(data["combine_recommendation"], "")
        self.assertIn("combine_recommendation.md", data["files_added_or_changed"])


if __name__ == "__main__":
    unittest.main()
