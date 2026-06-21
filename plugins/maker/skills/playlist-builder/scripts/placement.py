#!/usr/bin/env python3
"""
Anchor phase placement rules — story #423.

`PlacementRule` encodes priority-ordered preferred phases for an anchor
artist, derived from the series context's `anchor_rules` blocks (or the
default table in ANCHOR_PLACEMENT_RULES.md).

`resolve_phase(playlist, episode, artist)` returns the phase name to use
for an anchor injection, following the resolution order:
  1. Episode anchor_rules for this artist (if present)
  2. Artist default preferences
  3. First phase in the playlist (fallback)

This module is a pure helper — it does not mutate playlists. Callers
(anchor.py's inject_anchors) use the resolved phase to pick an insert
position.
"""
from __future__ import annotations

from dataclasses import dataclass, field

ANCHOR_DEFAULT_PHASES: dict[str, list[str]] = {
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
class PlacementRule:
    artist: str
    preferred_phases: list[str] = field(default_factory=list)

    @classmethod
    def from_context(cls, artist: str,
                     episode: dict) -> "PlacementRule":
        """Build a PlacementRule from an episode's anchor_rules block."""
        artist_key = artist.lower().replace(" ", "_")
        ep_prefs: list[str] = (
            episode.get("anchor_rules", {}).get(artist_key, [])
        )
        if ep_prefs:
            return cls(artist=artist, preferred_phases=list(ep_prefs))
        return cls(
            artist=artist,
            preferred_phases=list(ANCHOR_DEFAULT_PHASES.get(artist, [])),
        )

    def resolve_phase(self, playlist: list[dict]) -> str:
        """Return the best available phase for this artist given the playlist."""
        existing_phases = {t.get("phase", "") for t in playlist}
        for pref in self.preferred_phases:
            if pref in existing_phases:
                return pref
        # Fallback: first phase in playlist order
        if playlist:
            return playlist[0].get("phase", "")
        return ""


def build_placement_rules(
    artists: list[str], episode: dict
) -> dict[str, PlacementRule]:
    """Return a {artist: PlacementRule} map for the given episode."""
    return {a: PlacementRule.from_context(a, episode) for a in artists}
