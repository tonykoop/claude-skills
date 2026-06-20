"""
Repo-scaffold planner: propose a repository structure for recovered maker projects.

Design
------
plan_scaffold() accepts a project name and a list of classified ArchiveItems and
returns a ScaffoldPlan — a pure data object describing:

  * Proposed directory layout (dirs_by_kind)
  * Git LFS rules for large binary files (>100 MB)
  * Gitignore patterns
  * An evidence ledger tying every directory / LFS rule back to a source item
  * README skeleton

Nothing is written to disk.  The ScaffoldPlan is fully serialisable so it can
be stored in a CI artefact, displayed to the user, or handed to a downstream
repo-creation step.
"""

from __future__ import annotations

from typing import Sequence
from pydantic import BaseModel, Field

from .models import ArchiveItem, FileKind
from .evidence import EvidenceLedger, EvidenceEntry, EvidenceKind


# ---------------------------------------------------------------------------
# Directory layout per kind
# ---------------------------------------------------------------------------

_KIND_TO_DIR: dict[FileKind, str] = {
    FileKind.CAD:     "cad",
    FileKind.PHOTO:   "photos",
    FileKind.DOC:     "docs",
    FileKind.CODE:    "src",
    FileKind.MEDIA:   "media",
    FileKind.UNKNOWN: "misc",
}

# Gitignore lines that are always safe for a maker repo
_DEFAULT_GITIGNORE: list[str] = [
    "# OS artefacts",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    "",
    "# Build outputs",
    "*.pyc",
    "__pycache__/",
    "*.o",
    "*.obj.d",
    "",
    "# CAD scratch files",
    "*.bak",
    "*.lock",
    "",
    "# LFS-tracked large binaries are in .gitattributes",
]


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class LFSRule(BaseModel):
    """A single Git LFS tracking rule."""
    pattern:    str   # e.g. "*.stl" or "cad/big_assembly.step"
    reason:     str   # human-readable justification
    source_path: str  # the archive item that triggered this rule


class ScaffoldedDir(BaseModel):
    """One proposed directory in the repo."""
    path:       str        # e.g. "cad", "docs/datasheets"
    kind:       FileKind
    item_count: int = 0
    note:       str = ""


class ScaffoldPlan(BaseModel):
    """
    Proposed repository structure for a single recovered project.

    This is a pure data record — no I/O is performed.

    Fields
    ------
    project         : Canonical project name.
    dirs            : Proposed directories (one per FileKind present).
    lfs_rules       : LFS tracking patterns for files >100 MB.
    gitignore_lines : Lines to write into .gitignore.
    readme_skeleton : Markdown content for README.md.
    evidence_ledger : Provenance record (facts vs. inferences).
    item_count      : Total number of ArchiveItems in this plan.
    large_binary_count : Number of items that triggered LFS rules.
    """
    project:            str
    dirs:               list[ScaffoldedDir]  = Field(default_factory=list)
    lfs_rules:          list[LFSRule]        = Field(default_factory=list)
    gitignore_lines:    list[str]            = Field(default_factory=list)
    readme_skeleton:    str                  = ""
    evidence_ledger:    EvidenceLedger
    item_count:         int = 0
    large_binary_count: int = 0

    def export_dict(self) -> dict:
        """Serialisable dict for storage / display."""
        return {
            "project":            self.project,
            "item_count":         self.item_count,
            "large_binary_count": self.large_binary_count,
            "dirs":               [d.model_dump() for d in self.dirs],
            "lfs_rules":          [r.model_dump() for r in self.lfs_rules],
            "gitignore_lines":    self.gitignore_lines,
            "readme_skeleton":    self.readme_skeleton,
            "evidence_ledger":    self.evidence_ledger.export_dict(),
        }


# ---------------------------------------------------------------------------
# Planner
# ---------------------------------------------------------------------------

def plan_scaffold(
    project: str,
    items: Sequence[ArchiveItem],
) -> ScaffoldPlan:
    """
    Produce a ScaffoldPlan for *project* given its classified ArchiveItems.

    Parameters
    ----------
    project
        Canonical project name (typically from ArchiveItem.inferred_project).
    items
        All ArchiveItems that belong to this project.

    Returns
    -------
    ScaffoldPlan
        Fully populated plan with dirs, LFS rules, gitignore, readme, and ledger.

    Notes
    -----
    * Always deterministic — same input → same output.
    * Dirs are created for every FileKind represented in *items*.
    * A LFS rule is emitted for every item with size_bytes > 100 MB, using
      an exact-path pattern so other small files of the same type are unaffected.
    * The evidence ledger records a FACT for each source item and an INFERRED
      entry for every dir/LFS decision derived from heuristics.
    """
    items = list(items)

    # ------------------------------------------------------------------
    # 1. Group items by kind → collect into proposed dirs
    # ------------------------------------------------------------------
    kind_to_items: dict[FileKind, list[ArchiveItem]] = {}
    for item in items:
        kind_to_items.setdefault(item.kind, []).append(item)

    dirs: list[ScaffoldedDir] = []
    for kind, kind_items in sorted(kind_to_items.items(), key=lambda kv: kv[0].value):
        proposed_dir = _KIND_TO_DIR[kind]
        dirs.append(ScaffoldedDir(
            path=proposed_dir,
            kind=kind,
            item_count=len(kind_items),
            note=f"Recovered {len(kind_items)} {kind.value} file(s) from archive.",
        ))

    # ------------------------------------------------------------------
    # 2. LFS rules for large binaries (>100 MB)
    # ------------------------------------------------------------------
    lfs_rules: list[LFSRule] = []
    large_count = 0
    for item in items:
        if item.is_large_binary:
            large_count += 1
            target_dir = _KIND_TO_DIR[item.kind]
            # Use file-specific path pattern rather than a glob so only this
            # exact file is LFS-tracked (avoids accidentally LFS-ing small files
            # with the same extension)
            filename = item.filename
            lfs_rules.append(LFSRule(
                pattern=f"{target_dir}/{filename}",
                reason=(
                    f"Binary file exceeds 100 MB "
                    f"({item.size_bytes / (1024**2):.1f} MB) — "
                    "Git LFS recommended to avoid repo bloat."
                ),
                source_path=item.path,
            ))

    # ------------------------------------------------------------------
    # 3. Gitignore
    # ------------------------------------------------------------------
    gitignore = list(_DEFAULT_GITIGNORE)

    # ------------------------------------------------------------------
    # 4. README skeleton
    # ------------------------------------------------------------------
    dir_list = "\n".join(f"  {d.path}/   — {d.note}" for d in dirs)
    lfs_note = (
        f"\n## Git LFS\n\n"
        f"{large_count} file(s) exceed 100 MB and are tracked via Git LFS.\n"
        f"Run `git lfs install && git lfs pull` after cloning.\n"
        if lfs_rules else ""
    )
    readme = f"""\
# {project}

> Recovered from maker archive. Provenance details in `evidence-ledger.json`.

## Directory layout

{dir_list}
{lfs_note}
## Provenance discipline

This repository was scaffolded by the **archive-recovery** tool.
Every claim in `evidence-ledger.json` is tagged as either:

* **fact** — verifiable from the archive byte-stream (path, extension, hash)
* **inferred** — derived from heuristics (project grouping, kind from context)

Review `evidence-ledger.json` before treating inferred fields as authoritative.

## Recovery workflow

1. Run `classify_archive(file_records)` over a list of `FileRecord` objects.
2. Group the returned `ArchiveItem` list by `inferred_project`.
3. Call `plan_scaffold(project, items)` for each group.
4. Inspect the `ScaffoldPlan` and `evidence_ledger` before committing anything.
5. Run `git lfs track` for each pattern in `lfs_rules` before adding large files.
"""

    # ------------------------------------------------------------------
    # 5. Evidence ledger
    # ------------------------------------------------------------------
    ledger = EvidenceLedger.from_archive_items(project, items)

    # Record scaffold decisions as inferred claims
    for d in dirs:
        ledger.add(EvidenceEntry(
            kind=EvidenceKind.INFERRED,
            subject=d.path,
            claim=(
                f"directory '{d.path}/' proposed for "
                f"{d.item_count} {d.kind.value} file(s)"
            ),
            source="kind-to-directory mapping heuristic",
            confidence="high",
        ))
    for rule in lfs_rules:
        ledger.add(EvidenceEntry(
            kind=EvidenceKind.INFERRED,
            subject=rule.source_path,
            claim=f"Git LFS rule '{rule.pattern}' — file is >100 MB",
            source="size threshold heuristic (>100 MB → LFS)",
            confidence="high",
        ))

    return ScaffoldPlan(
        project=project,
        dirs=dirs,
        lfs_rules=lfs_rules,
        gitignore_lines=gitignore,
        readme_skeleton=readme,
        evidence_ledger=ledger,
        item_count=len(items),
        large_binary_count=large_count,
    )
