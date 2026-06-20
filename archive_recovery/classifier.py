"""
Archive classifier: infer FileKind and project grouping from FileRecords.

Design principles
-----------------
* Every classification decision is traceable — callers can inspect
  `kind_is_inferred` and `project_is_inferred` per item.
* No filesystem I/O; operates entirely on in-memory FileRecord lists.
* Extension lookup is the primary signal (archive fact via well-known mappings).
  Path/name heuristics are the secondary signal (always flagged as inferred).
* Project grouping: use the *first meaningful directory component* after
  stripping common archive top-level prefixes (backup/, archive/, exports/, etc.).
"""

from __future__ import annotations

import re
from typing import Sequence

from .models import ArchiveItem, FileKind, FileRecord

# ---------------------------------------------------------------------------
# Extension → FileKind mapping  (archive fact — not inferred)
# ---------------------------------------------------------------------------

_EXT_TO_KIND: dict[str, FileKind] = {
    # CAD / 3-D
    "step": FileKind.CAD,   "stp":  FileKind.CAD,
    "stl":  FileKind.CAD,   "obj":  FileKind.CAD,
    "3mf":  FileKind.CAD,   "ply":  FileKind.CAD,
    "f3d":  FileKind.CAD,   "f3z":  FileKind.CAD,
    "dxf":  FileKind.CAD,   "dwg":  FileKind.CAD,
    "sldprt": FileKind.CAD, "sldasm": FileKind.CAD,
    "iges": FileKind.CAD,   "igs":  FileKind.CAD,
    "scad": FileKind.CAD,
    "kicad_pcb": FileKind.CAD,  "kicad_sch": FileKind.CAD,
    "sch":  FileKind.CAD,   "brd":  FileKind.CAD,
    "gerber": FileKind.CAD, "gbr":  FileKind.CAD,
    # PHOTO / raster
    "jpg":  FileKind.PHOTO, "jpeg": FileKind.PHOTO,
    "png":  FileKind.PHOTO, "tiff": FileKind.PHOTO,
    "tif":  FileKind.PHOTO, "raw":  FileKind.PHOTO,
    "cr2":  FileKind.PHOTO, "cr3":  FileKind.PHOTO,
    "nef":  FileKind.PHOTO, "arw":  FileKind.PHOTO,
    "heic": FileKind.PHOTO, "bmp":  FileKind.PHOTO,
    "gif":  FileKind.PHOTO, "webp": FileKind.PHOTO,
    # DOCUMENT
    "pdf":  FileKind.DOC,   "docx": FileKind.DOC,
    "doc":  FileKind.DOC,   "odt":  FileKind.DOC,
    "txt":  FileKind.DOC,   "md":   FileKind.DOC,
    "rst":  FileKind.DOC,   "tex":  FileKind.DOC,
    "xlsx": FileKind.DOC,   "xls":  FileKind.DOC,
    "csv":  FileKind.DOC,   "json": FileKind.DOC,
    "yaml": FileKind.DOC,   "yml":  FileKind.DOC,
    "toml": FileKind.DOC,   "xml":  FileKind.DOC,
    # CODE
    "py":   FileKind.CODE,  "pyw":  FileKind.CODE,
    "cpp":  FileKind.CODE,  "cc":   FileKind.CODE,
    "cxx":  FileKind.CODE,  "c":    FileKind.CODE,
    "h":    FileKind.CODE,  "hpp":  FileKind.CODE,
    "js":   FileKind.CODE,  "ts":   FileKind.CODE,
    "jsx":  FileKind.CODE,  "tsx":  FileKind.CODE,
    "rs":   FileKind.CODE,  "go":   FileKind.CODE,
    "rb":   FileKind.CODE,  "java": FileKind.CODE,
    "kt":   FileKind.CODE,  "swift":FileKind.CODE,
    "ino":  FileKind.CODE,  "sh":   FileKind.CODE,
    "bash": FileKind.CODE,  "zsh":  FileKind.CODE,
    "lua":  FileKind.CODE,  "r":    FileKind.CODE,
    "m":    FileKind.CODE,  "mat":  FileKind.CODE,
    # MEDIA / audio-video
    "mp4":  FileKind.MEDIA, "mov":  FileKind.MEDIA,
    "avi":  FileKind.MEDIA, "mkv":  FileKind.MEDIA,
    "webm": FileKind.MEDIA, "wmv":  FileKind.MEDIA,
    "mp3":  FileKind.MEDIA, "wav":  FileKind.MEDIA,
    "flac": FileKind.MEDIA, "aac":  FileKind.MEDIA,
    "ogg":  FileKind.MEDIA, "m4a":  FileKind.MEDIA,
}

# Strip these leading path components before inferring project name
_ARCHIVE_PREFIXES = frozenset({
    "archive", "archives", "backup", "backups", "export", "exports",
    "old", "misc", "dump", "recovery", "recovered", "projects",
})

# Regex to normalise project-name candidates (collapse non-alnum runs)
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _infer_kind(record: FileRecord) -> tuple[FileKind, bool, str]:
    """
    Return (kind, is_inferred, provenance_note).

    is_inferred=False → extension was in our explicit lookup table (archive fact).
    is_inferred=True  → no extension match; kind is a heuristic guess or UNKNOWN.
    """
    filename = record.path.split("/")[-1]
    parts = filename.rsplit(".", 1)
    if len(parts) == 2:
        ext = parts[-1].lower()
        kind = _EXT_TO_KIND.get(ext)
        if kind is not None:
            note = f"kind={kind.value!r} from extension '.{ext}' (archive fact)"
            return kind, False, note

    # Fallback: check for dotfiles / no-extension executables as code
    if filename.startswith(".") or "." not in filename:
        note = "kind=code inferred from no-extension / dotfile pattern (heuristic)"
        return FileKind.CODE, True, note

    note = f"kind=unknown — no rule matched extension in '{filename}'"
    return FileKind.UNKNOWN, True, note


def _infer_project(record: FileRecord) -> tuple[str, bool, str]:
    """
    Return (project_name, is_inferred, provenance_note).

    Strategy (all flagged as inferred — no external metadata is available):
    1. Strip known archive-prefix directories.
    2. Take the first remaining path component as the project name.
    3. Slug-normalise (lower, collapse punctuation → underscore).
    """
    parts = [p for p in record.path.split("/") if p]
    # Drop the filename itself
    dirs = parts[:-1] if len(parts) > 1 else []

    # Strip common archive prefixes
    while dirs and dirs[0].lower() in _ARCHIVE_PREFIXES:
        dirs = dirs[1:]

    if dirs:
        raw = dirs[0]
        slug = _SLUG_RE.sub("_", raw.lower()).strip("_") or "unknown_project"
        note = (
            f"project={slug!r} inferred from first directory component '{raw}'"
            " after stripping archive prefixes (heuristic)"
        )
        return slug, True, note

    # No directory → use filename stem as project
    stem = parts[-1].rsplit(".", 1)[0] if parts else "unknown_project"
    slug = _SLUG_RE.sub("_", stem.lower()).strip("_") or "unknown_project"
    note = (
        f"project={slug!r} inferred from filename stem (no parent directories)"
        " (heuristic)"
    )
    return slug, True, note


def _classify_one(record: FileRecord) -> ArchiveItem:
    """Classify a single FileRecord into an ArchiveItem."""
    kind, kind_inferred, kind_note = _infer_kind(record)
    project, proj_inferred, proj_note = _infer_project(record)

    return ArchiveItem(
        path=record.path,
        size_bytes=record.size_bytes,
        mtime=record.mtime,
        content_hash=record.content_hash or "",
        kind=kind,
        kind_is_inferred=kind_inferred,
        inferred_project=project,
        project_is_inferred=proj_inferred,
        provenance_note=f"{kind_note} | {proj_note}",
    )


def classify_archive(file_records: Sequence[FileRecord]) -> list[ArchiveItem]:
    """
    Classify a list of FileRecords into ArchiveItems.

    Parameters
    ----------
    file_records
        In-memory list of raw file records (no filesystem access required).

    Returns
    -------
    list[ArchiveItem]
        One ArchiveItem per input record, in the same order.
        Items are stable (deterministic) — calling with the same input always
        produces identical output.

    Notes
    -----
    * kind_is_inferred=False  → extension was in the explicit lookup table
      (treated as an archive fact).
    * project_is_inferred=True → project name was derived from path heuristics
      (always true for this classifier; a future metadata-aware version could
      set it to False when project identity is confirmed externally).
    """
    return [_classify_one(r) for r in file_records]
