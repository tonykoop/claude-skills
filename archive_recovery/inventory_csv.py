"""
archive_recovery.inventory_csv
==============================
CSV inventory ingestion for the archive-recovery pipeline.

Story #53 — Full inventory pass of D:\\ archive.

The PowerShell inventory script produces a CSV with these columns:
  Path, Depth, FileCount, SizeBytes, Modified, Extensions

where:
  Path       — Windows-style or forward-slash relative path
  Depth      — integer depth from archive root
  FileCount  — number of files directly in this directory
  SizeBytes  — total bytes in this directory
  Modified   — ISO-8601 datetime string (e.g. "2026-05-09T14:23:00")
  Extensions — semicolon-delimited list of extensions (e.g. ".step;.stl;.pdf")

This module also supports a "flat file" CSV variant where each row is a
single file (not a directory):
  Path, SizeBytes, Modified, Extension

Both variants are supported via auto-detection (directory CSV has FileCount
column; file CSV has Extension column).

Nothing is read from disk — the caller passes the CSV content as a string.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel

from archive_recovery.models import FileKind, FileRecord


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class InventoryRow(BaseModel):
    """One row of the directory-level CSV."""
    path: str
    depth: int = 0
    file_count: int = 0
    size_bytes: int = 0
    modified: str = ""
    extensions: list[str] = []

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "InventoryRow":
        raw_path = row.get("Path", "").replace("\\", "/")
        raw_exts = row.get("Extensions", "")
        exts: list[str] = []
        if raw_exts.strip():
            for part in raw_exts.split(";"):
                part = part.strip().lstrip(".").lower()
                if part:
                    exts.append(part)
        return cls(
            path=raw_path,
            depth=int(row.get("Depth", 0) or 0),
            file_count=int(row.get("FileCount", 0) or 0),
            size_bytes=int(row.get("SizeBytes", 0) or 0),
            modified=row.get("Modified", "").strip(),
            extensions=exts,
        )


class FileInventoryRow(BaseModel):
    """One row of the flat file-level CSV."""
    path: str
    size_bytes: int = 0
    modified: str = ""
    extension: str = ""

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "FileInventoryRow":
        raw_path = row.get("Path", "").replace("\\", "/")
        raw_ext = row.get("Extension", "").strip().lstrip(".").lower()
        return cls(
            path=raw_path,
            size_bytes=int(row.get("SizeBytes", 0) or 0),
            modified=row.get("Modified", "").strip(),
            extension=raw_ext,
        )


class InventoryParseResult(BaseModel):
    """Result of parsing a CSV inventory file."""
    rows: list[InventoryRow] = []
    file_rows: list[FileInventoryRow] = []
    parse_errors: list[str] = []
    variant: str = "unknown"  # "directory" | "file" | "unknown"
    total_rows: int = 0


class ArchiveSummary(BaseModel):
    """High-level stats for an inventory."""
    total_dirs: int = 0
    total_size_bytes: int = 0
    extension_counts: dict[str, int] = {}
    max_depth: int = 0
    top_extensions: list[str] = []


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _parse_mtime(dt_str: str) -> float:
    """Parse ISO-8601 strings to a float Unix timestamp. Returns 0.0 on error."""
    if not dt_str or not dt_str.strip():
        return 0.0
    s = dt_str.strip()
    # normalise space separator to T
    s = s.replace(" ", "T")
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            continue
    return 0.0


def _normalise_path(raw: str) -> str:
    return raw.replace("\\", "/")


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def parse_directory_csv(csv_text: str) -> InventoryParseResult:
    """
    Parse CSV text (stdlib csv module) into an InventoryParseResult.

    Auto-detects variant:
      - "FileCount" in header → directory CSV
      - "Extension" in header (no "FileCount") → file CSV
      - otherwise → "unknown"
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    fieldnames = reader.fieldnames or []
    header_set = {f.strip() for f in fieldnames}

    if "FileCount" in header_set:
        variant = "directory"
    elif "Extension" in header_set:
        variant = "file"
    else:
        variant = "unknown"

    rows: list[InventoryRow] = []
    file_rows: list[FileInventoryRow] = []
    parse_errors: list[str] = []
    total_rows = 0

    for raw_row in reader:
        # Skip entirely blank rows
        values = [v for v in raw_row.values() if v and v.strip()]
        if not values:
            continue
        total_rows += 1
        try:
            if variant == "directory":
                rows.append(InventoryRow.from_row(raw_row))
            elif variant == "file":
                file_rows.append(FileInventoryRow.from_row(raw_row))
            # unknown variant: attempt neither, just count
        except Exception as exc:
            parse_errors.append(f"row {total_rows}: {exc}")

    return InventoryParseResult(
        rows=rows,
        file_rows=file_rows,
        parse_errors=parse_errors,
        variant=variant,
        total_rows=total_rows,
    )


def rows_to_file_records(
    result: InventoryParseResult,
    *,
    archive_root: str = "",
) -> list[FileRecord]:
    """
    Convert an InventoryParseResult into FileRecord objects.

    Directory variant: one FileRecord per extension per InventoryRow.
    File variant: one FileRecord per FileInventoryRow.
    """
    records: list[FileRecord] = []

    def _strip_root(p: str) -> str:
        if archive_root and p.startswith(archive_root):
            p = p[len(archive_root):]
            if p.startswith("/"):
                p = p[1:]
        return p

    if result.variant == "directory":
        for row in result.rows:
            mtime = _parse_mtime(row.modified)
            base_path = _strip_root(row.path)
            for ext in row.extensions:
                synth_path = f"{base_path}/{ext}_files.{ext}"
                records.append(FileRecord(
                    path=synth_path,
                    size_bytes=row.size_bytes,
                    mtime=mtime,
                ))
    elif result.variant == "file":
        for file_row in result.file_rows:
            mtime = _parse_mtime(file_row.modified)
            p = _strip_root(file_row.path)
            records.append(FileRecord(
                path=p,
                size_bytes=file_row.size_bytes,
                mtime=mtime,
            ))

    return records


def summarise_inventory(result: InventoryParseResult) -> ArchiveSummary:
    """Compute high-level stats from directory rows."""
    ext_counts: dict[str, int] = {}
    total_size = 0
    max_depth = 0

    for row in result.rows:
        total_size += row.size_bytes
        if row.depth > max_depth:
            max_depth = row.depth
        for ext in row.extensions:
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

    # top-5 by directory count descending
    top_exts = sorted(ext_counts, key=lambda e: -ext_counts[e])[:5]

    return ArchiveSummary(
        total_dirs=len(result.rows),
        total_size_bytes=total_size,
        extension_counts=ext_counts,
        max_depth=max_depth,
        top_extensions=top_exts,
    )
