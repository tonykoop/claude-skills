"""
Core data models for the archive-recovery pipeline.

ArchiveItem — the canonical record for a single recovered file.
FileRecord  — lightweight raw input (path, mtime, size_bytes).
FileKind    — enumeration of recognised content categories.
"""

from __future__ import annotations

import hashlib
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class FileKind(str, Enum):
    """Content category inferred from file extension or path heuristics."""
    CAD     = "cad"       # .step, .stl, .f3d, .dxf, .sldprt, .iges, .ply, .3mf …
    PHOTO   = "photo"     # .jpg, .jpeg, .png, .tiff, .raw, .heic, .bmp …
    DOC     = "doc"       # .pdf, .docx, .md, .txt, .odt, .xlsx, .csv …
    CODE    = "code"      # .py, .cpp, .c, .h, .js, .ts, .ino, .rs, .go, .sh …
    MEDIA   = "media"     # .mp4, .mov, .avi, .mp3, .wav, .flac …
    UNKNOWN = "unknown"   # fallback when no rule matches


class FileRecord(BaseModel):
    """
    Raw input record — supplied by the caller (no filesystem reads).

    Fields
    ------
    path        : Forward-slash relative path, e.g. "projects/synth_v2/pcb.kicad_pcb"
    mtime       : Unix timestamp (float) of the file's modification time.
    size_bytes  : File size in bytes; 0 if unknown.
    content_hash: Optional pre-computed SHA-256 hex digest.
    """
    path:         str
    mtime:        float  = 0.0
    size_bytes:   int    = 0
    content_hash: Optional[str] = None

    def compute_hash_stub(self) -> str:
        """
        Derive a deterministic stub hash from the path when a real hash is absent.
        Useful for testing without real filesystem access.
        """
        return hashlib.sha256(self.path.encode()).hexdigest()


class ArchiveItem(BaseModel):
    """
    Enriched record produced by the classifier for a single recovered file.

    Provenance fields
    -----------------
    provenance_note : Human-readable explanation of every claim.
    kind_is_inferred: True when kind came from heuristics (not a definitive signal).
    project_is_inferred: True when the project name was guessed from path/name.
    """
    # --- identity ---
    path:         str
    size_bytes:   int   = 0
    mtime:        float = 0.0
    content_hash: str   = ""

    # --- classification ---
    kind:             FileKind = FileKind.UNKNOWN
    kind_is_inferred: bool     = True   # False only when extension is unambiguous

    # --- project grouping ---
    inferred_project:    str  = "unknown_project"
    project_is_inferred: bool = True    # False only when metadata confirms project

    # --- provenance ---
    provenance_note: str = ""

    @model_validator(mode="after")
    def _fill_hash(self) -> "ArchiveItem":
        if not self.content_hash:
            self.content_hash = hashlib.sha256(self.path.encode()).hexdigest()
        return self

    # --- helpers ---
    @property
    def filename(self) -> str:
        return self.path.split("/")[-1]

    @property
    def extension(self) -> str:
        parts = self.filename.rsplit(".", 1)
        return parts[-1].lower() if len(parts) == 2 else ""

    @property
    def is_large_binary(self) -> bool:
        """True when the file is >100 MB — a Git-LFS candidate."""
        return self.size_bytes > 100 * 1024 * 1024

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ArchiveItem(path={self.path!r}, kind={self.kind.value}, "
            f"project={self.inferred_project!r})"
        )
