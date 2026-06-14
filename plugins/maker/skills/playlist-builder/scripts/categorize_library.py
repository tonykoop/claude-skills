#!/usr/bin/env python3
"""
Auto-categorize a Spotify library into A–E banks using audio features.

STATUS: stub. Outline of the logic is here; OAuth + Web API calls are not yet
implemented. See ../platforms/spotify.md for the full flow design.

Inputs: a list of Spotify track objects with audio-features attached.
Output: a categorized catalog JSON conforming to the schema in
generate_playlist.py's load_catalog() docstring.

Bank rules (from DESIGN.md):
    A  — energy < 0.30, tempo < 80 BPM, high acousticness/instrumentalness
    B  — energy 0.30–0.60, valence 0.30–0.70, tempo 90–115 BPM
    C  — energy 0.40–0.80, high valence, HIGH SPEECHINESS / vocals
    D  — energy > 0.70, valence > 0.50, tempo 115–135 BPM, low acousticness
    E  — energy 0.30–0.60, valence mid, tempo 80–110 BPM
"""

from __future__ import annotations
import json
import sys
from pathlib import Path


def categorize_track(features: dict) -> str:
    """Return the bank letter A/B/C/D/E for a Spotify audio-features dict."""
    e = features.get("energy", 0.0)
    v = features.get("valence", 0.5)
    t = features.get("tempo", 100.0)
    a = features.get("acousticness", 0.0)
    sp = features.get("speechiness", 0.0)
    inst = features.get("instrumentalness", 0.0)

    # A: ambient / opening / closing
    if e < 0.30 and t < 80 and (a > 0.4 or inst > 0.4):
        return "A"

    # C: theme anchor — strong vocals/lyrics
    if 0.40 <= e <= 0.80 and v > 0.45 and sp > 0.07:
        return "C"

    # D: peak
    if e > 0.70 and v > 0.50 and 115 <= t <= 140 and a < 0.3:
        return "D"

    # B: rising
    if 0.30 <= e <= 0.60 and 0.30 <= v <= 0.70 and 90 <= t <= 115:
        return "B"

    # E: descent (default for mid-energy mellow stuff)
    if 0.30 <= e <= 0.60 and 80 <= t <= 110:
        return "E"

    # Fallback: if energy is very high, push to D; if very low, push to A; else E
    if e > 0.70:
        return "D"
    if e < 0.30:
        return "A"
    return "E"


def categorize_catalog(tracks_with_features: list[dict],
                       source: str = "spotify",
                       user: str = "") -> dict:
    """Categorize a list of {track, features} dicts into a catalog JSON."""
    banks = {k: [] for k in "ABCDE"}
    for entry in tracks_with_features:
        track = entry.get("track", {})
        features = entry.get("features", {})
        if not features:
            continue
        bank = categorize_track(features)
        banks[bank].append({
            "title": track.get("name") or track.get("title"),
            "artist": ", ".join(a.get("name") for a in track.get("artists", [])) if track.get("artists") else track.get("artist"),
            "duration_ms": track.get("duration_ms") or features.get("duration_ms"),
            "spotify_uri": track.get("uri"),
            "soundcloud_url": track.get("soundcloud_url"),  # optional cross-link
            "genre": track.get("genre"),
            "bpm": features.get("tempo"),
            "tags": [],
            "audio_features": features,
        })
    return {
        "version": 1,
        "source": source,
        "user": user,
        "banks": banks,
        "exclusions": [],
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: categorize_library.py <input_tracks.json> <output_catalog.json>", file=sys.stderr)
        print("\nThis is a stub. The OAuth + library-pull step is not yet implemented.", file=sys.stderr)
        print("Provide a JSON file containing a list of {track, features} entries.", file=sys.stderr)
        sys.exit(1)

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])

    data = json.loads(src.read_text())
    catalog = categorize_catalog(data, source="spotify")
    dst.write_text(json.dumps(catalog, indent=2))

    counts = {k: len(v) for k, v in catalog["banks"].items()}
    print(f"Categorized {sum(counts.values())} tracks: {counts}", file=sys.stderr)


if __name__ == "__main__":
    main()
