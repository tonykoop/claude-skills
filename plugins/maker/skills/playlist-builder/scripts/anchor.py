#!/usr/bin/env python3
"""
Anchor-artist injection for the 4-week yoga series.

An "anchor" is a single track by a designated artist (Lane 8 or Tinlicker)
that is placed in a specific phase position for each weekly episode. Rules:
  - Exactly one Lane 8 track per episode
  - Exactly one Tinlicker track per episode
  - Neither artist repeats across all four episodes (series-global constraint)

Usage as a module:
    from anchor import AnchorConfig, inject_anchors

Usage from the CLI:
    python anchor.py \\
        --episode-json week-01.json \\
        --series-exclude-ids ids.txt \\
        --output week-01-anchored.json
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

ANCHOR_ARTISTS = ("Lane 8", "Tinlicker")

# Which phases each anchor artist prefers, ordered by priority.
# Series context may override these via episode["anchor_rules"].
_DEFAULT_PHASE_PREFS: dict[str, list[str]] = {
    "Lane 8": [
        "Sun A (Rising)",
        "Sun B (Peak)",
        "Heart Opener",
        "Balance Series",
        "Cool Down (Descent)",
    ],
    "Tinlicker": [
        "Cool Down (Descent)",
        "Savasana",
        "Savasana (Extended)",
        "Sun B (Peak)",
    ],
}


@dataclass
class AnchorConfig:
    artist: str
    phase_preferences: list[str]
    used_track_ids: set[str] = field(default_factory=set)


def _track_id(track: dict) -> str:
    return (
        track.get("spotify_uri")
        or track.get("soundcloud_url")
        or f"{track.get('artist', '')}|{track.get('title', '')}"
    )


def _is_anchor_artist(track: dict, artist: str) -> bool:
    return artist.lower() in (track.get("artist") or "").lower()


def _find_anchor_track(catalog_banks: dict, config: AnchorConfig,
                       series_used_ids: set) -> dict | None:
    """Search all catalog banks for an unused anchor track by this artist."""
    combined_exclude = config.used_track_ids | series_used_ids
    for bank_tracks in catalog_banks.values():
        for t in bank_tracks:
            if not _is_anchor_artist(t, config.artist):
                continue
            tid = _track_id(t)
            if tid in combined_exclude:
                continue
            return t
    return None


def inject_anchors(
    playlist: list[dict],
    episode: dict,
    catalog: dict,
    anchor_configs: dict[str, AnchorConfig],
    series_used_ids: set,
) -> list[dict]:
    """Inject one Lane 8 track and one Tinlicker track into playlist.

    Modifies playlist in-place; also marks the injected track IDs in
    anchor_configs[artist].used_track_ids AND series_used_ids.
    Returns the modified playlist.
    """
    phase_names = [t.get("phase", "") for t in playlist]

    for artist, config in anchor_configs.items():
        track = _find_anchor_track(catalog["banks"], config, series_used_ids)
        if track is None:
            print(
                f"  [anchor] WARNING: no unused {artist} track found in catalog",
                file=sys.stderr,
            )
            continue

        # Pick preferred phase from episode anchor_rules or config defaults
        ep_rules: dict = episode.get("anchor_rules", {})
        artist_key = artist.lower().replace(" ", "_")
        prefs: list[str] = ep_rules.get(artist_key, config.phase_preferences)

        insert_phase: str | None = None
        for pref in prefs:
            if pref in phase_names:
                insert_phase = pref
                break

        if insert_phase is None:
            insert_phase = phase_names[0] if phase_names else ""

        # Insert after the LAST track in the preferred phase
        insert_idx = len(playlist)
        for i, t in enumerate(playlist):
            if t.get("phase") == insert_phase:
                insert_idx = i + 1

        tid = _track_id(track)
        playlist.insert(
            insert_idx,
            {**track, "phase": insert_phase, "bank": "anchor",
             "anchor_artist": artist},
        )
        config.used_track_ids.add(tid)
        series_used_ids.add(tid)
        print(
            f"  [anchor] {artist} → \"{track.get('title', '?')}\" "
            f"injected at position {insert_idx} (phase: {insert_phase})",
            file=sys.stderr,
        )

    return playlist


def build_anchor_configs(
    episodes: list[dict],
    catalog: dict,
) -> dict[str, AnchorConfig]:
    """Build AnchorConfig objects from series context, using defaults."""
    configs = {}
    for artist in ANCHOR_ARTISTS:
        artist_key = artist.lower().replace(" ", "_")
        # Collect phase prefs from all episodes (union, ordered by first seen)
        seen: set[str] = set()
        prefs: list[str] = []
        for ep in episodes:
            for phase in ep.get("anchor_rules", {}).get(artist_key, []):
                if phase not in seen:
                    seen.add(phase)
                    prefs.append(phase)
        # Fall back to hard-coded defaults
        if not prefs:
            prefs = _DEFAULT_PHASE_PREFS.get(artist, [])
        configs[artist] = AnchorConfig(artist=artist, phase_preferences=prefs)
    return configs
