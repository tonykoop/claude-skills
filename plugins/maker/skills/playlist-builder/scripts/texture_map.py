"""Kinetic-texture → sonic mapping for the audio-dynamic engine.

SCHEMA_ID: playlist-builder/texture-map@1.0.0
VERSION    = "1.0.0"

Story #474 — Epic #471 (playlist-builder audio-dynamic).

See references/KINETIC_TEXTURE_MAP.md for the full vocabulary rationale.
"""
from __future__ import annotations

from typing import Any

VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Core mapping
# ---------------------------------------------------------------------------

TEXTURE_SONIC_MAP: dict[str, dict[str, list[str]]] = {
    "staccato": {
        "tags":   ["ticking", "mechanical", "staccato", "glitchy", "clipped"],
        "genres": ["minimal techno", "industrial hip-hop", "electro", "neo-soul"],
        "avoid":  ["pads", "ambient", "legato", "reverb"],
    },
    "fluid": {
        "tags":   ["pads", "legato", "ambient", "evolving", "warm", "breathable"],
        "genres": ["ambient", "neo-classical", "chill electronica", "deep house", "lo-fi"],
        "avoid":  ["staccato", "ticking", "mechanical", "clipped"],
    },
    "tutting": {
        "tags":   ["polyrhythmic", "hi-hats", "sub-bass", "syncopated", "layered"],
        "genres": ["hip-hop", "glitch-hop", "afrobeat", "polyrhythmic electronic"],
        "avoid":  ["ambient", "reverb", "legato"],
    },
    "explosive": {
        "tags":   ["peak", "drop", "high-energy", "massive", "build-release"],
        "genres": ["techno", "big-room house", "drum and bass"],
        "avoid":  ["ambient", "minimalist", "atmospheric"],
    },
    "grounded": {
        "tags":   ["bass-heavy", "stomping", "groove", "low-end", "rhythmic"],
        "genres": ["afrobeat", "cumbia", "reggaeton", "dancehall"],
        "avoid":  ["ethereal", "suspended", "drone", "space"],
    },
    "suspended": {
        "tags":   ["suspended", "drone", "ethereal", "space", "atmospheric"],
        "genres": ["ambient electronica", "cinematic", "new-age", "drone"],
        "avoid":  ["peak", "drop", "stomping", "bass-heavy"],
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def sonic_criteria_for_texture(texture: str) -> dict[str, list[str]]:
    """Return the sonic criteria dict for *texture*.

    Supports composite textures joined by '+' (e.g. 'fluid+grounded').
    For composites: union the tag/genre lists, intersect the avoid lists.

    Raises ValueError for unrecognised texture names.
    """
    parts = [t.strip() for t in texture.split("+")]
    unknown = [p for p in parts if p not in TEXTURE_SONIC_MAP]
    if unknown:
        raise ValueError(
            f"Unknown kinetic texture(s): {unknown!r}. "
            f"Recognised: {sorted(TEXTURE_SONIC_MAP)}"
        )

    if len(parts) == 1:
        return dict(TEXTURE_SONIC_MAP[parts[0]])  # shallow copy

    # Composite: union tags/genres, intersect avoid lists
    combined_tags: set[str] = set()
    combined_genres: set[str] = set()
    avoid_sets: list[set[str]] = []
    for part in parts:
        entry = TEXTURE_SONIC_MAP[part]
        combined_tags.update(entry["tags"])
        combined_genres.update(entry["genres"])
        avoid_sets.append(set(entry["avoid"]))

    # Intersection: only avoid something both textures want to avoid
    combined_avoid = set.intersection(*avoid_sets) if avoid_sets else set()

    return {
        "tags":   sorted(combined_tags),
        "genres": sorted(combined_genres),
        "avoid":  sorted(combined_avoid),
    }


def filter_tracks_by_texture(
    catalog: list[dict[str, Any]],
    texture: str,
) -> list[dict[str, Any]]:
    """Filter *catalog* to tracks compatible with *texture*.

    Steps:
    1. Hard-exclude tracks whose tags overlap with the avoid list.
    2. Score remaining tracks by tag overlap count (descending).
    3. Fall back to genre match if tag overlap yields zero results.

    Returns a ranked list (best-match first).  Empty list if nothing matches.
    """
    criteria = sonic_criteria_for_texture(texture)
    target_tags = set(criteria["tags"])
    target_genres = set(g.lower() for g in criteria["genres"])
    avoid_tags = set(criteria["avoid"])

    def _track_tags(track: dict[str, Any]) -> set[str]:
        raw = track.get("tags", [])
        return {str(t).lower() for t in raw}

    def _track_genre(track: dict[str, Any]) -> str:
        return str(track.get("genre", "")).lower()

    # Step 1: hard exclude
    filtered = [t for t in catalog if not (_track_tags(t) & avoid_tags)]

    # Step 2: score by tag overlap
    def _score(track: dict[str, Any]) -> int:
        return len(_track_tags(track) & target_tags)

    scored = [(t, _score(t)) for t in filtered]
    tag_matched = [(t, s) for t, s in scored if s > 0]

    if tag_matched:
        return [t for t, _ in sorted(tag_matched, key=lambda x: -x[1])]

    # Step 3: fall back to genre
    genre_matched = [t for t in filtered if _track_genre(t) in target_genres]
    return genre_matched
