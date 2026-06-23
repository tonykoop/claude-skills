"""Audio-trigger sonic anchors for the audio-dynamic engine.

SCHEMA_ID: playlist-builder/sonic-anchor@1.0.0
VERSION    = "1.0.0"

Story #473 — Epic #471 (playlist-builder audio-dynamic).

See references/AUDIO_TRIGGER_ANCHORS.md for the full schema and algorithm.

Usage
-----
    from scripts.sonic_anchor import tag_track_anchors, align_timeline

    track = tag_track_anchors(track_dict, [
        {"anchor_ts_s": 62.5, "anchor_type": "drop", "confidence": 0.95, "source": "manual"},
    ])

    blocks_out = align_timeline(routine_blocks, anchored_tracks)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

VERSION = "1.0.0"

_CONFIDENCE_THRESHOLD = 0.5
_MAX_OFFSET_S = 30.0
_PREFERRED_TYPES = {"drop", "peak"}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class AnchorTag:
    anchor_ts_s: float
    anchor_type: str
    confidence: float = 1.0
    source: str = "manual"

    VALID_TYPES = frozenset({"drop", "breakdown", "build", "pause", "peak"})

    def __post_init__(self) -> None:
        if self.anchor_type not in self.VALID_TYPES:
            raise ValueError(
                f"Unknown anchor_type {self.anchor_type!r}. "
                f"Valid: {sorted(self.VALID_TYPES)}"
            )
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "AnchorTag":
        return cls(
            anchor_ts_s=float(d["anchor_ts_s"]),
            anchor_type=str(d["anchor_type"]),
            confidence=float(d.get("confidence", 1.0)),
            source=str(d.get("source", "manual")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "anchor_ts_s": self.anchor_ts_s,
            "anchor_type": self.anchor_type,
            "confidence": self.confidence,
            "source": self.source,
        }


# ---------------------------------------------------------------------------
# Tagging
# ---------------------------------------------------------------------------

def tag_track_anchors(
    track: dict[str, Any],
    anchors: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return a copy of *track* with the given *anchors* merged in.

    Existing anchors on the track are replaced by *anchors*.
    Validates each anchor via ``AnchorTag.from_dict``.
    """
    parsed = [AnchorTag.from_dict(a) for a in anchors]
    return {**track, "anchors": [a.to_dict() for a in parsed]}


# ---------------------------------------------------------------------------
# Timeline alignment
# ---------------------------------------------------------------------------

def _best_anchor(
    anchors: list[dict[str, Any]],
    peak_count_s: float,
) -> dict[str, Any] | None:
    """Pick the best anchor to align with *peak_count_s*.

    Selection priority:
    1. Preferred type (drop or peak) with confidence >= threshold.
    2. Any type with confidence >= threshold.
    3. None → fallback path.

    Tie-break within a tier: closest to peak_count_s.
    """
    reliable = [a for a in anchors if a.get("confidence", 1.0) >= _CONFIDENCE_THRESHOLD]
    if not reliable:
        return None

    preferred = [a for a in reliable if a.get("anchor_type") in _PREFERRED_TYPES]
    pool = preferred if preferred else reliable

    return min(pool, key=lambda a: abs(a["anchor_ts_s"] - peak_count_s))


def align_timeline(
    routine_blocks: list[dict[str, Any]],
    anchored_tracks: list[dict[str, Any]],
    max_offset_s: float = _MAX_OFFSET_S,
) -> list[dict[str, Any]]:
    """Align each routine block's peak count to the best anchor in its track.

    *routine_blocks* and *anchored_tracks* must be parallel lists (same length,
    same order). Each block must have a ``peak_count_s`` field (seconds into the
    block when the choreographic climax occurs).

    Each output block gains:
    - ``anchor_offset_s`` — seconds to shift track start (positive = start early)
    - ``anchor_fallback`` — True if no reliable anchor was found
    - ``anchor_warning`` — str if the offset was clamped

    Returns a list parallel to *routine_blocks*.
    """
    if len(routine_blocks) != len(anchored_tracks):
        raise ValueError(
            f"routine_blocks ({len(routine_blocks)}) and "
            f"anchored_tracks ({len(anchored_tracks)}) must have the same length"
        )

    results: list[dict[str, Any]] = []

    for block, track in zip(routine_blocks, anchored_tracks):
        peak_s = float(block.get("peak_count_s", 0.0))
        anchors = track.get("anchors") or []

        best = _best_anchor(anchors, peak_s)

        if best is None:
            results.append({
                **block,
                "anchor_offset_s": 0.0,
                "anchor_fallback": True,
            })
            continue

        raw_offset = peak_s - best["anchor_ts_s"]
        clamped = max(-max_offset_s, min(max_offset_s, raw_offset))

        entry: dict[str, Any] = {
            **block,
            "anchor_offset_s": clamped,
            "anchor_fallback": False,
            "anchor_type_used": best["anchor_type"],
        }
        if abs(raw_offset) > max_offset_s:
            entry["anchor_warning"] = (
                f"Raw offset {raw_offset:.1f}s exceeds cap {max_offset_s}s; clamped."
            )

        results.append(entry)

    return results
