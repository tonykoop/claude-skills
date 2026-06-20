#!/usr/bin/env python3
"""Tests for bigthink.batch_import — BatchImporter and related result types."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigthink.batch_import import BatchImporter, BatchImportResult
from bigthink.registry import CaptureRegistry
from bigthink.schema import Domain, ManufacturingTheoryCapture, MaturityLevel


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_T1 = (
    "Physical manufacturing capability scales with evaluated spatial complexity "
    "in a power-law relationship driven by learning-rate coefficients."
)
_T2 = (
    "Planetary element inventory tracks crustal abundance to enable "
    "resource-aware AI hardware design and scarcity-penalty triage."
)

_VALID_RECORDS = [
    {
        "id":     "import-cap-01",
        "thesis": _T1,
        "domain": "scaling_law",
    },
    {
        "id":     "import-cap-02",
        "thesis": _T2,
        "domain": "materials",
        "tags":   ["elements", "scarcity"],
        "source": "github.com/tonykoop/claude-skills/issues/205",
    },
]

_INVALID_RECORDS = [
    {
        "id":     "Bad ID",  # invalid slug
        "thesis": _T1,
        "domain": "scaling_law",
    },
    {
        "id":     "ok-cap",
        "thesis": "short",  # too short
        "domain": "materials",
    },
]


class TestBatchImporterDicts(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = CaptureRegistry()
        self.importer = BatchImporter()

    def test_valid_batch_adds_captures(self) -> None:
        result = self.importer.import_dicts(self.reg, _VALID_RECORDS)
        self.assertTrue(result.success)
        self.assertEqual(result.added, 2)
        self.assertIn("import-cap-01", self.reg)
        self.assertIn("import-cap-02", self.reg)

    def test_total_count_matches(self) -> None:
        result = self.importer.import_dicts(self.reg, _VALID_RECORDS)
        self.assertEqual(result.total, 2)

    def test_failed_count_zero_on_valid(self) -> None:
        result = self.importer.import_dicts(self.reg, _VALID_RECORDS)
        self.assertEqual(result.failed, 0)

    def test_invalid_batch_adds_nothing(self) -> None:
        # Batch is all-or-nothing: if any record fails, none are committed
        result = self.importer.import_dicts(self.reg, _INVALID_RECORDS)
        self.assertFalse(result.success)
        self.assertEqual(result.added, 0)
        self.assertEqual(len(self.reg), 0)

    def test_dry_run_does_not_modify_registry(self) -> None:
        result = self.importer.import_dicts(self.reg, _VALID_RECORDS, dry_run=True)
        self.assertTrue(result.dry_run)
        self.assertEqual(len(self.reg), 0)

    def test_dry_run_reports_valid_records(self) -> None:
        result = self.importer.import_dicts(self.reg, _VALID_RECORDS, dry_run=True)
        self.assertEqual(result.failed, 0)

    def test_dry_run_reports_invalid_records(self) -> None:
        result = self.importer.import_dicts(self.reg, _INVALID_RECORDS, dry_run=True)
        self.assertFalse(result.success)

    def test_duplicate_id_detected(self) -> None:
        self.reg.add(ManufacturingTheoryCapture(
            id="import-cap-01", thesis=_T1, domain=Domain.SCALING_LAW
        ))
        result = self.importer.import_dicts(self.reg, _VALID_RECORDS)
        self.assertFalse(result.success)
        errors_text = result.errors_report()
        self.assertIn("import-cap-01", errors_text)

    def test_errors_report_not_empty_on_failure(self) -> None:
        result = self.importer.import_dicts(self.reg, _INVALID_RECORDS)
        report = result.errors_report()
        self.assertIn("ERROR", report)

    def test_summary_contains_source_label(self) -> None:
        result = self.importer.import_dicts(
            self.reg, _VALID_RECORDS, source_label="unit-test"
        )
        self.assertIn("unit-test", result.summary())

    def test_summary_contains_mode(self) -> None:
        r1 = self.importer.import_dicts(self.reg, _VALID_RECORDS, dry_run=True)
        self.assertIn("DRY-RUN", r1.summary())
        r2 = self.importer.import_dicts(CaptureRegistry(), _VALID_RECORDS)
        self.assertIn("IMPORT", r2.summary())

    def test_parse_error_captured_in_record(self) -> None:
        bad = [{"id": "ok-cap", "thesis": _T1, "domain": "INVALID_DOMAIN"}]
        result = self.importer.import_dicts(self.reg, bad)
        self.assertFalse(result.success)
        self.assertIn("Parse error", result.errors_report())

    def test_empty_batch_succeeds(self) -> None:
        result = self.importer.import_dicts(self.reg, [])
        self.assertTrue(result.success)
        self.assertEqual(result.total, 0)
        self.assertEqual(result.added, 0)


class TestBatchImporterFiles(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = CaptureRegistry()
        self.importer = BatchImporter()
        self.tmpdir = tempfile.mkdtemp()

    def _write_json(self, records, *, wrap: bool = False) -> Path:
        path = Path(self.tmpdir) / "caps.json"
        payload = {"captures": records} if wrap else records
        path.write_text(json.dumps(payload))
        return path

    def _write_yaml(self, records) -> Path:
        try:
            import yaml  # type: ignore
        except ImportError:
            return None  # skip if not installed
        path = Path(self.tmpdir) / "caps.yaml"
        path.write_text(yaml.dump(records))
        return path

    def test_import_json_bare_list(self) -> None:
        path = self._write_json(_VALID_RECORDS)
        result = self.importer.import_file(self.reg, path)
        self.assertTrue(result.success)
        self.assertEqual(result.added, 2)

    def test_import_json_wrapped(self) -> None:
        path = self._write_json(_VALID_RECORDS, wrap=True)
        result = self.importer.import_file(self.reg, path)
        self.assertTrue(result.success)

    def test_import_yaml_if_available(self) -> None:
        path = self._write_yaml(_VALID_RECORDS)
        if path is None:
            self.skipTest("PyYAML not installed")
        result = self.importer.import_file(self.reg, path)
        self.assertTrue(result.success)
        self.assertEqual(result.added, 2)

    def test_import_unsupported_extension_raises(self) -> None:
        path = Path(self.tmpdir) / "caps.csv"
        path.write_text("id,thesis\n")
        with self.assertRaises(ValueError):
            self.importer.import_file(self.reg, path)

    def test_dry_run_does_not_modify_registry_file(self) -> None:
        path = self._write_json(_VALID_RECORDS)
        self.importer.import_file(self.reg, path, dry_run=True)
        self.assertEqual(len(self.reg), 0)


class TestBatchImportResult(unittest.TestCase):
    def test_success_false_when_any_error(self) -> None:
        from bigthink.batch_import import ImportRecord
        rec = ImportRecord(index=0, capture_id="x", added=False, errors=["oops"])
        result = BatchImportResult(records=[rec], dry_run=False, source_path="<t>")
        self.assertFalse(result.success)

    def test_success_true_when_no_errors(self) -> None:
        from bigthink.batch_import import ImportRecord
        rec = ImportRecord(index=0, capture_id="x", added=True)
        result = BatchImportResult(records=[rec], dry_run=False, source_path="<t>")
        self.assertTrue(result.success)

    def test_errors_report_no_issues(self) -> None:
        from bigthink.batch_import import ImportRecord
        rec = ImportRecord(index=0, capture_id="x", added=True)
        result = BatchImportResult(records=[rec], dry_run=False, source_path="<t>")
        self.assertIn("No issues", result.errors_report())


if __name__ == "__main__":
    unittest.main()
