"""
archive_recovery.migration
==========================
Provenance-aware migration planner.

Given a RepoManifest (what we WANT the repo to look like) and an existing
repo tree (what's ALREADY in the repo — represented as a dict of
repo-relative paths → file hashes), produce a MigrationPlan describing:

  * Files to ADD (new, not in existing tree)
  * Files to UPDATE (same dest_path, different content — archive version wins)
  * Files to SKIP (already in repo, same content — hash match)
  * CONFLICTS (same dest_path, different content AND manually flagged)
  * Files to REMOVE (in existing tree but not in manifest — orphans)

The caller decides what to do with conflicts. This module only surfaces them.

Nothing is written to disk.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from .manifest import RepoManifest


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class MigrationAction(str, Enum):
    ADD      = "ADD"
    UPDATE   = "UPDATE"
    SKIP     = "SKIP"
    CONFLICT = "CONFLICT"
    REMOVE   = "REMOVE"


class MigrationItem(BaseModel):
    """A single file decision in a MigrationPlan."""
    action: MigrationAction
    dest_path: str
    source_path: str = ""
    existing_hash: str = ""
    incoming_hash: str = ""
    size_bytes: int = 0
    note: str = ""


class MigrationPlan(BaseModel):
    """Complete migration plan for a single project repo."""
    project: str
    items: list[MigrationItem] = Field(default_factory=list)

    # ------------------------------------------------------------------
    # Filtered views
    # ------------------------------------------------------------------

    @property
    def adds(self) -> list[MigrationItem]:
        return [i for i in self.items if i.action == MigrationAction.ADD]

    @property
    def updates(self) -> list[MigrationItem]:
        return [i for i in self.items if i.action == MigrationAction.UPDATE]

    @property
    def skips(self) -> list[MigrationItem]:
        return [i for i in self.items if i.action == MigrationAction.SKIP]

    @property
    def conflicts(self) -> list[MigrationItem]:
        return [i for i in self.items if i.action == MigrationAction.CONFLICT]

    @property
    def removes(self) -> list[MigrationItem]:
        return [i for i in self.items if i.action == MigrationAction.REMOVE]

    @property
    def total_bytes_to_add(self) -> int:
        return sum(
            i.size_bytes
            for i in self.items
            if i.action in (MigrationAction.ADD, MigrationAction.UPDATE)
        )

    @property
    def has_conflicts(self) -> bool:
        return any(i.action == MigrationAction.CONFLICT for i in self.items)

    def summary_lines(self) -> list[str]:
        return [
            (
                f"ADD {len(self.adds)},"
                f" UPDATE {len(self.updates)},"
                f" SKIP {len(self.skips)},"
                f" CONFLICT {len(self.conflicts)},"
                f" REMOVE {len(self.removes)}"
            )
        ]


# ---------------------------------------------------------------------------
# Planner
# ---------------------------------------------------------------------------

def plan_migration(
    manifest: RepoManifest,
    existing_tree: dict[str, str],
    *,
    flag_conflicts: bool = True,
) -> MigrationPlan:
    """
    Produce a MigrationPlan by comparing a RepoManifest against the existing repo.

    Parameters
    ----------
    manifest
        The RepoManifest describing the desired end-state.
    existing_tree
        Maps repo-relative ``dest_path`` → ``content_hash`` for files already
        present in the repo.
    flag_conflicts
        When True (default), a file whose dest_path already exists in the repo
        with different content AND whose manifest entry has
        ``provenance_confidence == "low"`` is flagged as CONFLICT rather than
        UPDATE, leaving the resolution to the caller.

    Returns
    -------
    MigrationPlan
        All migration items, sorted by action priority (ADD → UPDATE → SKIP →
        CONFLICT → REMOVE) is not guaranteed; items appear in manifest order
        followed by REMOVEs.
    """
    items: list[MigrationItem] = []

    # Track which dest_paths appear in the manifest (for REMOVE detection)
    manifest_dest_paths: set[str] = set()

    for section in manifest.sections:
        for entry in section.entries:
            manifest_dest_paths.add(entry.dest_path)

            if entry.dest_path not in existing_tree:
                items.append(MigrationItem(
                    action=MigrationAction.ADD,
                    dest_path=entry.dest_path,
                    source_path=entry.source_path,
                    incoming_hash=entry.content_hash,
                    size_bytes=entry.size_bytes,
                    note="new file — not present in existing repo",
                ))
            else:
                repo_hash = existing_tree[entry.dest_path]
                hashes_match = (
                    entry.content_hash == repo_hash
                    or (not entry.content_hash and not repo_hash)
                )
                if hashes_match:
                    items.append(MigrationItem(
                        action=MigrationAction.SKIP,
                        dest_path=entry.dest_path,
                        source_path=entry.source_path,
                        existing_hash=repo_hash,
                        incoming_hash=entry.content_hash,
                        size_bytes=entry.size_bytes,
                        note="content hash matches — no change needed",
                    ))
                elif flag_conflicts and entry.provenance_confidence == "low":
                    items.append(MigrationItem(
                        action=MigrationAction.CONFLICT,
                        dest_path=entry.dest_path,
                        source_path=entry.source_path,
                        existing_hash=repo_hash,
                        incoming_hash=entry.content_hash,
                        size_bytes=entry.size_bytes,
                        note=(
                            "low-confidence provenance — content differs;"
                            " manual resolution required"
                        ),
                    ))
                else:
                    items.append(MigrationItem(
                        action=MigrationAction.UPDATE,
                        dest_path=entry.dest_path,
                        source_path=entry.source_path,
                        existing_hash=repo_hash,
                        incoming_hash=entry.content_hash,
                        size_bytes=entry.size_bytes,
                        note="archive version replaces existing file",
                    ))

    # Files in existing_tree not covered by the manifest → REMOVE
    for dest_path, existing_hash in existing_tree.items():
        if dest_path not in manifest_dest_paths:
            items.append(MigrationItem(
                action=MigrationAction.REMOVE,
                dest_path=dest_path,
                existing_hash=existing_hash,
                note="orphan — present in repo but absent from manifest",
            ))

    return MigrationPlan(project=manifest.project, items=items)
