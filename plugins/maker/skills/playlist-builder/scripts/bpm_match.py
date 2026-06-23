"""BPM matching to choreography blocks for the audio-dynamic engine.

SCHEMA_ID: playlist-builder/bpm-match@1.0.0
VERSION    = "1.0.0"

Story #472 — Epic #471 (playlist-builder audio-dynamic).

Usage
-----
    from scripts.bpm_match import bpm_candidates, match_blocks

    # single-block lookup
    candidates = bpm_candidates(catalog, bpm_target=97, bpm_range=(90, 105))

    # full routine pass
    mix_blocks = match_blocks(routine_blocks, catalog)
"""
from __future__ import annotations

from typing import Any

VERSION = "1.0.0"

# Score weight constants
_BPM_WEIGHT = 0.7
_ENERGY_WEIGHT = 0.3


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def bpm_candidates(
    catalog: list[dict[str, Any]],
    bpm_target: float,
    bpm_range: tuple[float, float] | None = None,
    energy_target: float | None = None,
    top_n: int = 5,
) -> list[dict[str, Any]]:
    """Return the *top_n* tracks from *catalog* closest to *bpm_target*.

    Args:
        catalog:       List of track dicts. Each must have a numeric ``bpm`` field.
        bpm_target:    Ideal BPM for the block (e.g. 97).
        bpm_range:     (min_bpm, max_bpm) inclusive.  Tracks outside are excluded.
                       Defaults to (bpm_target - 10, bpm_target + 10).
        energy_target: Optional 0–1 energy target.  Tracks are scored on combined
                       BPM closeness (70 %) + energy closeness (30 %).
        top_n:         Maximum number of candidates to return.

    Returns:
        Ranked list of track dicts (best match first).  May be shorter than *top_n*
        if fewer tracks satisfy the range filter.
    """
    if bpm_range is None:
        bpm_range = (bpm_target - 10, bpm_target + 10)

    lo, hi = bpm_range

    # Filter: must be in range and have a numeric BPM
    in_range = [
        t for t in catalog
        if isinstance(t.get("bpm"), (int, float)) and lo <= t["bpm"] <= hi
    ]

    if not in_range:
        return []

    def _score(track: dict[str, Any]) -> float:
        bpm_delta = abs(track["bpm"] - bpm_target)
        bpm_score = 1.0 - min(bpm_delta / max(hi - lo, 1), 1.0)

        energy_score = 0.0
        if energy_target is not None:
            af = track.get("audio_features") or {}
            e = af.get("energy")
            if isinstance(e, (int, float)):
                energy_score = 1.0 - abs(e - energy_target)

        if energy_target is not None:
            return _BPM_WEIGHT * bpm_score + _ENERGY_WEIGHT * energy_score
        return bpm_score  # pure BPM rank when no energy target

    ranked = sorted(in_range, key=_score, reverse=True)
    return ranked[:top_n]


def match_blocks(
    routine_blocks: list[dict[str, Any]],
    catalog: list[dict[str, Any]],
    top_n: int = 5,
) -> list[dict[str, Any]]:
    """Match each choreography block to its BPM candidates.

    Each block dict must have:
        ``bpm_target``  (float) — ideal tempo
        ``bpm_range``   (list[float, float], optional) — [min, max] BPM
        ``energy``      (float, optional) — 0–1 energy target

    Returns a list parallel to *routine_blocks*; each element is the input
    block augmented with a ``candidates`` list of matching tracks.
    """
    results = []
    for block in routine_blocks:
        target = float(block["bpm_target"])
        rng_raw = block.get("bpm_range")
        rng: tuple[float, float] | None = (
            (float(rng_raw[0]), float(rng_raw[1])) if rng_raw else None
        )
        energy = block.get("energy")

        candidates = bpm_candidates(
            catalog,
            bpm_target=target,
            bpm_range=rng,
            energy_target=energy,
            top_n=top_n,
        )
        results.append({**block, "candidates": candidates})

    return results
