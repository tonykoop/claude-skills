#!/usr/bin/env python3
from __future__ import annotations

import csv
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "archive-recovery" / "betabrand-shacket-recovery.md"
INVENTORY = REPO_ROOT / "data" / "archive-inventory-2026-05-09.csv"


class BetabrandShacketRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = DOC.read_text(encoding="utf-8")
        with INVENTORY.open(newline="", encoding="utf-8") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_inventory_contains_shacket_photo_packet(self) -> None:
        paths = {row["RelativePath"] for row in self.rows}
        self.assertIn(r"to organize\Shacket Photos and Video", paths)
        self.assertIn(r"to organize\Shacket Photos and Video\Cordaround", paths)
        self.assertIn(r"to organize\Shacket Photos and Video\Herringbone", paths)

    def test_doc_recommends_existing_sewing_repo_target(self) -> None:
        self.assertIn("Use the existing `sewing` repo", self.doc)
        self.assertIn("sewing/projects/2015-betabrand-shacket/", self.doc)
        self.assertIn("Do not create a new apparel umbrella from this packet alone", self.doc)

    def test_doc_uses_repo_local_inventory_validation_not_qmd(self) -> None:
        self.assertIn("python3 scripts/validate_archive_inventory.py", self.doc)
        self.assertIn("data/archive-inventory-2026-05-09.csv", self.doc)
        self.assertNotIn("qmd search", self.doc)


if __name__ == "__main__":
    unittest.main()
