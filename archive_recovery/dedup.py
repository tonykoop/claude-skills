"""
archive_recovery.dedup
======================
Duplicate and near-duplicate detection across recovered archive items.

Design
------
A large archive typically contains many duplicates:
  * Exact duplicates — identical content_hash (or identical path+size when
    no hash is available)
  * Near-duplicates — same filename in different directories (likely the same
    file copied around) with the same or similar size
  * Stale-version pairs — same stem, same extension, different mtime (the
    older one is likely superseded)

All detection is purely in-memory; no I/O.

DedupReport
-----------
The top-level result.  Contains:
  * exact_groups     : list of ExactDupGroup (2+ items share content_hash)
  * near_dup_groups  : list of NearDupGroup (2+ items share filename + similar size)
  * stale_pairs      : list of StalePair (same stem+ext, different mtime)
  * unique_items     : ArchiveItems that are not duplicated by any rule
  * summary stats

Strategies
----------
Callers can pass a DedupConfig to tune which strategies run and the
size-similarity tolerance for near-duplicate detection.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Sequence

from pydantic import BaseModel, Field

from .models import ArchiveItem


class DedupConfig(BaseModel):
    """Configuration for duplicate detection strategies."""

    run_exact: bool = True
    """Detect exact duplicates (by content_hash)."""

    run_near_dup: bool = True
    """Detect near-duplicates (same filename, size within tolerance)."""

    run_stale_versions: bool = True
    """Detect stale version pairs (same stem+ext, older mtime)."""

    size_tolerance_pct: float = Field(default=5.0, ge=0.0, le=100.0)
    """Two files are near-dups if their sizes differ by <= this percentage."""

    min_size_bytes_for_near_dup: int = 1024
    """Ignore tiny files (< 1 KB) for near-dup; they are likely config snippets."""


class ExactDupGroup(BaseModel):
    """A group of items that share an identical content_hash."""

    content_hash: str
    """The shared hash."""

    items: list[ArchiveItem]
    """2+ items with this hash."""

    keep_path: str
    """Recommended path to keep (deepest path; tie-break: alphabetical)."""

    drop_paths: list[str]
    """Paths recommended for removal."""

    @property
    def savings_bytes(self) -> int:
        """Bytes that could be reclaimed by removing the duplicate copies."""
        if not self.items:
            return 0
        return (len(self.items) - 1) * self.items[0].size_bytes


class NearDupGroup(BaseModel):
    """A group of items that share a filename and have similar sizes."""

    filename: str
    """Shared filename (case-insensitive canonical form)."""

    items: list[ArchiveItem]
    """2+ items that are considered near-duplicates."""

    note: str
    """Human-readable explanation."""


class StalePair(BaseModel):
    """Two items that share a stem+extension but differ in mtime."""

    stem: str
    """Shared stem (filename without extension)."""

    extension: str
    """Shared extension."""

    newer: ArchiveItem
    """The item with the higher mtime (more recent)."""

    older: ArchiveItem
    """The item with the lower mtime (likely superseded)."""

    mtime_diff_seconds: float
    """Absolute difference in mtime between newer and older."""


class DedupReport(BaseModel):
    """Top-level result from duplicate detection."""

    exact_groups: list[ExactDupGroup] = []
    near_dup_groups: list[NearDupGroup] = []
    stale_pairs: list[StalePair] = []
    total_items: int = 0
    duplicate_count: int = 0
    """Items flagged by any strategy."""
    potential_savings_bytes: int = 0

    @property
    def unique_item_count(self) -> int:
        """Number of items that are not duplicated."""
        return self.total_items - self.duplicate_count

    @property
    def has_duplicates(self) -> bool:
        """True when any duplicates were found."""
        return self.duplicate_count > 0


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _pick_keep_path(items: list[ArchiveItem]) -> str:
    """
    Select the recommended item to keep from a group of exact duplicates.

    Strategy: deepest path (most '/' separators).  Tie-break: alphabetical
    (lowest path string wins, i.e. min).
    """
    def _depth(item: ArchiveItem) -> int:
        return item.path.count("/")

    max_depth = max(_depth(it) for it in items)
    candidates = [it for it in items if _depth(it) == max_depth]
    return min(candidates, key=lambda it: it.path).path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_duplicates(
    items: Sequence[ArchiveItem],
    config: DedupConfig | None = None,
) -> DedupReport:
    """
    Run duplicate detection across *items* and return a DedupReport.

    Parameters
    ----------
    items:
        The archive items to analyse.
    config:
        Tuning knobs.  A default DedupConfig() is used when omitted.

    Returns
    -------
    DedupReport
        Fully populated report.  Deterministic — same input always yields the
        same output.
    """
    if config is None:
        config = DedupConfig()

    items = list(items)
    total = len(items)

    exact_groups: list[ExactDupGroup] = []
    near_dup_groups: list[NearDupGroup] = []
    stale_pairs: list[StalePair] = []

    # ------------------------------------------------------------------ #
    # 1. Exact duplicates                                                  #
    # ------------------------------------------------------------------ #
    if config.run_exact:
        by_hash: dict[str, list[ArchiveItem]] = defaultdict(list)
        for item in items:
            if item.content_hash:
                by_hash[item.content_hash].append(item)

        for content_hash, group in by_hash.items():
            if len(group) < 2:
                continue
            keep = _pick_keep_path(group)
            drop = [it.path for it in group if it.path != keep]
            exact_groups.append(ExactDupGroup(
                content_hash=content_hash,
                items=group,
                keep_path=keep,
                drop_paths=drop,
            ))

    # ------------------------------------------------------------------ #
    # 2. Near-duplicates                                                   #
    # ------------------------------------------------------------------ #
    if config.run_near_dup:
        by_filename: dict[str, list[ArchiveItem]] = defaultdict(list)
        for item in items:
            key = item.filename.lower()
            by_filename[key].append(item)

        for filename, group in by_filename.items():
            if len(group) < 2:
                continue

            # Only consider items large enough
            large_enough = [it for it in group if it.size_bytes >= config.min_size_bytes_for_near_dup]
            if len(large_enough) < 2:
                continue

            # Check size similarity across the large-enough subset
            sizes = [it.size_bytes for it in large_enough]
            max_size = max(sizes)
            min_size = min(sizes)

            if max_size == 0:
                continue

            spread_pct = (max_size - min_size) / max_size * 100.0
            if spread_pct > config.size_tolerance_pct:
                continue

            note = (
                f"same filename in {len(large_enough)} directories, "
                f"sizes within {config.size_tolerance_pct:.0f}%"
            )
            near_dup_groups.append(NearDupGroup(
                filename=filename,
                items=large_enough,
                note=note,
            ))

    # ------------------------------------------------------------------ #
    # 3. Stale version pairs                                               #
    # ------------------------------------------------------------------ #
    if config.run_stale_versions:
        # Key: (stem, extension)
        by_stem_ext: dict[tuple[str, str], list[ArchiveItem]] = defaultdict(list)
        for item in items:
            # Use the stem from the filename property (filename without extension)
            fname = item.filename
            ext = item.extension  # already lowercased
            if ext:
                stem = fname[: -(len(ext) + 1)]  # strip ".ext"
            else:
                stem = fname
            by_stem_ext[(stem, ext)].append(item)

        for (stem, ext), group in by_stem_ext.items():
            if len(group) < 2:
                continue
            # For 3+ items emit only the min/max mtime pair
            newer = max(group, key=lambda it: it.mtime)
            older = min(group, key=lambda it: it.mtime)
            if newer.path == older.path:
                # All mtimes equal — not a meaningful stale pair
                continue
            stale_pairs.append(StalePair(
                stem=stem,
                extension=ext,
                newer=newer,
                older=older,
                mtime_diff_seconds=abs(newer.mtime - older.mtime),
            ))

    # ------------------------------------------------------------------ #
    # 4. Assemble report                                                   #
    # ------------------------------------------------------------------ #
    # duplicate_count = number of drop_paths across all exact groups
    # (each exact group keeps 1 item; the rest are duplicates)
    dup_count = sum(len(g.drop_paths) for g in exact_groups)

    savings = sum(g.savings_bytes for g in exact_groups)

    return DedupReport(
        exact_groups=exact_groups,
        near_dup_groups=near_dup_groups,
        stale_pairs=stale_pairs,
        total_items=total,
        duplicate_count=dup_count,
        potential_savings_bytes=savings,
    )
