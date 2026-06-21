#!/usr/bin/env python3
"""
Track source mode toggle — story #424.

Controls whether the series generator and single-mix generator draw tracks
from the local seed library (default) or emit an API-search prompt block
that a caller can use to query Spotify / SoundCloud.

Two modes:
  "library"  — default; uses seed-banks/*.json exactly as the existing
               generate_playlist.py does.
  "api"      — skips local bank lookup; returns an anchor_search_prompt()
               string that callers paste into the Spotify search bar or
               pass to the Spotify MCP tool.

The mode is a Literal type hint ("library" | "api") and is validated at
runtime via validate_source_mode().
"""
from __future__ import annotations

from typing import Literal

SourceMode = Literal["library", "api"]

_VALID_MODES: tuple[str, ...] = ("library", "api")


def validate_source_mode(mode: str) -> SourceMode:
    """Raise ValueError for unknown modes; return the validated mode."""
    if mode not in _VALID_MODES:
        raise ValueError(
            f"Unknown source_mode {mode!r}. Valid: {_VALID_MODES}"
        )
    return mode  # type: ignore[return-value]


def anchor_search_prompt(artist: str, phase: str, week: int,
                         theme: str, bpm_min: float | None = None,
                         bpm_max: float | None = None) -> str:
    """Return a Spotify/SoundCloud search string for an anchor artist slot.

    Used in "api" mode when the caller does not have a local catalog and
    needs to query the platform directly.

    Args:
        artist:   Anchor artist name (e.g. "Lane 8", "Tinlicker").
        phase:    Phase to fill (e.g. "Sun B (Peak)").
        week:     Episode number 1–4.
        theme:    Episode theme (e.g. "Rooting").
        bpm_min:  Optional lower BPM bound from BlueprintConfig.
        bpm_max:  Optional upper BPM bound from BlueprintConfig.

    Returns:
        A search string suitable for pasting into Spotify or passing to
        the spotify.search MCP tool.
    """
    bpm_clause = ""
    if bpm_min is not None and bpm_max is not None:
        bpm_clause = f" BPM:{bpm_min:.0f}-{bpm_max:.0f}"
    return (
        f'artist:"{artist}"'
        f" theme:{theme.lower().replace(' ', '-')}"
        f" phase:{phase.lower().replace(' ', '-').replace('(', '').replace(')', '')}"
        f" week:{week}"
        f"{bpm_clause}"
    )


def emit_api_search_block(
    episode: dict,
    anchor_artists: list[str],
    bpm_phases: list[dict] | None = None,
) -> str:
    """Return a markdown block with copy-paste Spotify search strings.

    Called by generate_series.py when source_mode="api". One row per
    anchor artist per episode.

    Args:
        episode:         Episode dict from the series context.
        anchor_artists:  List of anchor artist names.
        bpm_phases:      Optional scaled phase list from BlueprintConfig.apply();
                         used to extract BPM bounds per phase.
    """
    week = episode.get("week", "?")
    theme = episode.get("theme", "")
    anchor_rules: dict = episode.get("anchor_rules", {})

    bpm_by_phase: dict[str, tuple[float, float]] = {}
    if bpm_phases:
        for p in bpm_phases:
            name = p.get("name", "")
            if "bpm_min" in p and "bpm_max" in p:
                bpm_by_phase[name] = (p["bpm_min"], p["bpm_max"])

    lines = [
        f"### Week {week} ({theme}) — API search strings",
        "",
        "| Artist | Phase | Search string |",
        "|--------|-------|---------------|",
    ]
    for artist in anchor_artists:
        artist_key = artist.lower().replace(" ", "_")
        prefs: list[str] = anchor_rules.get(artist_key, [])
        phase = prefs[0] if prefs else "(any)"
        bpm_range = bpm_by_phase.get(phase)
        bpm_min, bpm_max = (bpm_range if bpm_range else (None, None))
        prompt = anchor_search_prompt(
            artist, phase, week, theme, bpm_min, bpm_max
        )
        lines.append(f"| {artist} | {phase} | `{prompt}` |")

    lines.append("")
    return "\n".join(lines)
