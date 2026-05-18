"""Contract tests for the instrument-maker public invocation rename."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]


class InstrumentMakerInvocationRename(unittest.TestCase):
    def test_skill_frontmatter_uses_unversioned_public_name(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: instrument-maker", skill)
        self.assertIn("version: 4.4.7", skill)
        self.assertIn("legacy-alias: instrument-maker-v4", skill)
        self.assertIn("v4` as release lineage / implementation", skill)

    def test_manifest_keeps_legacy_repo_path_as_alias(self) -> None:
        with (REPO_ROOT / "manifest.yaml").open(encoding="utf-8") as f:
            manifest = yaml.safe_load(f)

        skills = manifest["skills"]
        self.assertIn("instrument-maker", skills)
        self.assertNotIn("instrument-maker-v4", skills)
        entry = skills["instrument-maker"]
        self.assertEqual(entry["canonical_version"], "4.4.7")
        self.assertEqual(entry["repo_path"], "skills/instrument-maker-v4")
        self.assertIn("instrument-maker-v4", entry["notes"])
        self.assertIn("release lineage", entry["notes"])


if __name__ == "__main__":
    unittest.main()
