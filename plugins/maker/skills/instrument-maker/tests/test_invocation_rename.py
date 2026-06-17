"""Contract tests for the instrument-maker public invocation rename."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml


SKILL_DIR = Path(__file__).resolve().parents[1]


class InstrumentMakerInvocationRename(unittest.TestCase):
    def test_skill_frontmatter_uses_unversioned_public_name(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: instrument-maker", skill)
        self.assertIn("version: 4.5.0", skill)
        self.assertIn("legacy-alias: instrument-maker-v4", skill)
        self.assertIn("v4` as release lineage / implementation", skill)

    def test_manifest_keeps_legacy_alias_and_lineage(self) -> None:
        # In the packaged plugin snapshot the governing metadata is the
        # skill-local manifest.yaml (the standalone repo's root manifest is not
        # snapshotted). Validate the rename contract against what ships here.
        with (SKILL_DIR / "manifest.yaml").open(encoding="utf-8") as f:
            manifest = yaml.safe_load(f)

        self.assertEqual(manifest["name"], "instrument-maker")
        self.assertEqual(manifest["version"], "4.5.0")
        self.assertEqual(manifest["legacy_alias"], "instrument-maker-v4")
        self.assertIn("instrument-maker-v4", manifest["lineage"])
        self.assertIn("release lineage", manifest["lineage"])


if __name__ == "__main__":
    unittest.main()
