#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "validate_archive_inventory.py"
INVENTORY = REPO_ROOT / "data" / "archive-inventory-2026-05-09.csv"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_archive_inventory", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_archive_inventory"] = module
    spec.loader.exec_module(module)
    return module


validator = load_module()


class ArchiveInventoryValidationTests(unittest.TestCase):
    def test_committed_inventory_passes_contract(self) -> None:
        self.assertEqual(validator.validate(INVENTORY), [])

    def test_committed_inventory_has_expected_header_and_full_pass_row_count(self) -> None:
        text = INVENTORY.read_text(encoding="utf-8").splitlines()
        self.assertEqual(text[0], ",".join(validator.REQUIRED_COLUMNS))
        self.assertGreaterEqual(len(text) - 1, 140)

    def test_bad_numeric_field_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text(
                "RelativePath,Depth,FileCount,TotalSizeMB,LastModified,Extensions\n"
                "folder,nope,1,0,2026-01-01,.txt\n",
                encoding="utf-8",
            )
            findings = validator.validate(path, min_rows=1)
        self.assertTrue(any("numeric fields" in finding for finding in findings))

    def test_main_passes_for_committed_inventory(self) -> None:
        self.assertEqual(validator.main([str(INVENTORY)]), 0)


if __name__ == "__main__":
    unittest.main()
