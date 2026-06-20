"""batch_import.py — Bulk-ingest captures from YAML or JSON files.

Supports two file formats:

YAML (list of capture dicts)::

    - id: koops-law-v1
      thesis: "..."
      domain: scaling_law
      maturity: seed
      ...

JSON (object with a ``captures`` list, or a bare list)::

    {"captures": [{...}, {...}]}
    [{...}, {...}]

The importer validates each record *before* writing and reports all
errors at the end (fail-all-or-commit-all within a batch).  With
``dry_run=True`` it validates and reports without touching the registry.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from bigthink.registry import CaptureRegistry
from bigthink.schema import ManufacturingTheoryCapture
from bigthink.validator import CaptureValidator


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class ImportRecord:
    """Outcome for a single record in the batch."""
    index:      int
    capture_id: str | None
    added:      bool
    errors:     list[str] = field(default_factory=list)
    warnings:   list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0


@dataclass
class BatchImportResult:
    """Aggregate result of a batch import operation."""
    records:    list[ImportRecord]
    dry_run:    bool
    source_path: str

    @property
    def total(self) -> int:
        return len(self.records)

    @property
    def added(self) -> int:
        return sum(1 for r in self.records if r.added)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.records if not r.valid)

    @property
    def success(self) -> bool:
        return self.failed == 0

    def summary(self) -> str:
        mode = "DRY-RUN" if self.dry_run else "IMPORT"
        return (
            f"[{mode}] {self.source_path}: "
            f"{self.total} records — {self.added} added, {self.failed} failed"
        )

    def errors_report(self) -> str:
        lines: list[str] = []
        for rec in self.records:
            if rec.errors:
                label = rec.capture_id or f"record[{rec.index}]"
                for e in rec.errors:
                    lines.append(f"  {label}: ERROR — {e}")
            for w in rec.warnings:
                label = rec.capture_id or f"record[{rec.index}]"
                lines.append(f"  {label}: WARN  — {w}")
        return "\n".join(lines) if lines else "No issues found."


# ---------------------------------------------------------------------------
# BatchImporter
# ---------------------------------------------------------------------------

class BatchImporter:
    """Validates and ingests a list of capture dicts into a CaptureRegistry.

    Usage::

        importer = BatchImporter()
        result = importer.import_file(registry, "captures.yaml")
        print(result.summary())
        if not result.success:
            print(result.errors_report())
    """

    def __init__(self) -> None:
        self._validator = CaptureValidator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def import_file(
        self,
        registry: CaptureRegistry,
        path: str | Path,
        *,
        dry_run: bool = False,
    ) -> BatchImportResult:
        """Load captures from a YAML or JSON file and ingest into ``registry``."""
        path = Path(path)
        raw_records = self._parse_file(path)
        return self._process(registry, raw_records, dry_run=dry_run,
                              source_path=str(path))

    def import_dicts(
        self,
        registry: CaptureRegistry,
        records: list[dict[str, Any]],
        *,
        dry_run: bool = False,
        source_label: str = "<inline>",
    ) -> BatchImportResult:
        """Ingest captures from a list of raw dicts (for programmatic use)."""
        return self._process(registry, records, dry_run=dry_run,
                              source_path=source_label)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _parse_file(self, path: Path) -> list[dict[str, Any]]:
        """Read and parse a YAML or JSON file into a list of raw dicts."""
        suffix = path.suffix.lower()

        if suffix in (".yaml", ".yml"):
            try:
                import yaml  # type: ignore[import-untyped]
            except ImportError:
                raise ImportError(
                    "PyYAML is required for YAML import: pip install pyyaml"
                )
            data = yaml.safe_load(path.read_text())
        elif suffix == ".json":
            data = json.loads(path.read_text())
        else:
            raise ValueError(
                f"Unsupported file extension {suffix!r}. Use .yaml, .yml, or .json."
            )

        # Normalise: accept bare list or {"captures": [...]}
        if isinstance(data, dict):
            data = data.get("captures", [])
        if not isinstance(data, list):
            raise ValueError(f"File must contain a list of captures; got {type(data).__name__}")
        return data

    def _process(
        self,
        registry: CaptureRegistry,
        raw_records: list[dict[str, Any]],
        *,
        dry_run: bool,
        source_path: str,
    ) -> BatchImportResult:
        """Validate all records, then commit if none failed."""
        records: list[ImportRecord] = []
        valid_captures: list[ManufacturingTheoryCapture] = []

        for i, raw in enumerate(raw_records):
            rec = ImportRecord(index=i, capture_id=raw.get("id"), added=False)
            try:
                cap = ManufacturingTheoryCapture.from_dict(raw)
                vr  = self._validator.validate_against(cap, registry)
                rec.errors.extend(vr.errors)
                rec.warnings.extend(vr.warnings)
                if vr.valid:
                    valid_captures.append(cap)
            except (ValueError, KeyError, TypeError) as exc:
                rec.errors.append(f"Parse error: {exc}")
            records.append(rec)

        # Only commit if ALL records are valid and not a dry run
        if not dry_run and all(r.valid for r in records):
            for cap in valid_captures:
                registry.add(cap)
            for r in records:
                r.added = True

        return BatchImportResult(
            records=records,
            dry_run=dry_run,
            source_path=source_path,
        )
