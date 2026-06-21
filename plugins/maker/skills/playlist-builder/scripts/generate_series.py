#!/usr/bin/env python3
"""
Playlist Series Generator — 4-week thematic progression.

Reads a series context JSON (contexts/series/*.json) and produces four
linked hour-long mix outlines, one per episode/week, with shared exclusion
tracking so no track appears more than once across the full series.

Usage:
    python generate_series.py \\
        --series ../contexts/series/4week-yoga-progression.json \\
        --catalog <catalog.json> \\
        --output-dir ./output/

Each episode is written to output-dir/week-{N}-{theme}.md
A series-summary.md is also written listing all four episodes.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers shared with generate_playlist (duplicated to stay standalone)
# ---------------------------------------------------------------------------

def _track_id(track: dict) -> str:
    return (
        track.get("spotify_uri")
        or track.get("soundcloud_url")
        or f"{track.get('artist', '')}|{track.get('title', '')}"
    )


def _select_for_phase(bank_tracks: list, count: int,
                      exclude_ids: set) -> list:
    available = [
        t for t in bank_tracks
        if _track_id(t) not in exclude_ids
        and (t.get("duration_ms") or 0) > 0
    ]
    random.shuffle(available)
    return available[:count]


def _fmt_dur(ms: int) -> str:
    return f"{ms // 60000}:{(ms // 1000) % 60:02d}"


# ---------------------------------------------------------------------------
# Series-level generation
# ---------------------------------------------------------------------------

def generate_episode(episode: dict, catalog: dict,
                     series_excludes: set) -> list:
    """Return a flat tracklist for one episode, updating series_excludes."""
    playlist: list[dict] = []
    for phase in episode["phases"]:
        bank = catalog["banks"].get(phase["bank"], [])
        target = (phase["min_tracks"] + phase["max_tracks"]) // 2
        picks = _select_for_phase(bank, target,
                                  exclude_ids=series_excludes)
        for p in picks:
            tid = _track_id(p)
            playlist.append({**p, "phase": phase["name"],
                              "bank": phase["bank"]})
            series_excludes.add(tid)
    return playlist


def format_episode_markdown(episode: dict, playlist: list,
                             week_num: int) -> str:
    total_ms = sum(t.get("duration_ms", 0) for t in playlist)
    lines = [
        f"# Week {week_num} — {episode['theme']}",
        "",
        f"_{episode['intention']}_",
        "",
        f"**Duration:** {total_ms // 60000} min {(total_ms // 1000) % 60:02d} sec  "
        f"**Tracks:** {len(playlist)}  "
        f"**BPM scale:** ×{episode['bpm_scale']:.2f}  "
        f"**Energy ceiling:** {episode['energy_ceiling']}/10",
        "",
        "| # | Phase | Bank | Artist | Title | Duration |",
        "|---|-------|------|--------|-------|----------|",
    ]
    for i, t in enumerate(playlist, 1):
        artist = (t.get("artist") or "")[:25]
        title = (t.get("title") or "")[:40]
        dur = _fmt_dur(t.get("duration_ms", 0))
        lines.append(
            f"| {i} | {t.get('phase', '')} | {t.get('bank', '')} "
            f"| {artist} | {title} | {dur} |"
        )

    sp_uris = [t.get("spotify_uri") for t in playlist if t.get("spotify_uri")]
    if sp_uris:
        lines += ["", "## Spotify URIs", "", "```"]
        lines += sp_uris
        lines.append("```")

    lines.append("")
    return "\n".join(lines)


def format_summary_markdown(series: dict, episode_metas: list) -> str:
    lines = [
        f"# {series['name']}",
        "",
        f"_{series['description']}_",
        "",
        "| Week | Theme | Tracks | Duration |",
        "|------|-------|--------|----------|",
    ]
    for m in episode_metas:
        lines.append(
            f"| {m['week']} | {m['theme']} | {m['track_count']} | {m['duration']} |"
        )
    lines.append("")
    return "\n".join(lines)


def generate_series(series_path: Path, catalog_path: Path,
                    output_dir: Path, seed: int | None = None) -> None:
    if seed is not None:
        random.seed(seed)

    series = json.loads(series_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)

    series_excludes: set[str] = set(catalog.get("exclusions", []))
    episode_metas = []

    for ep in series["episodes"]:
        week = ep["week"]
        playlist = generate_episode(ep, catalog, series_excludes)
        md = format_episode_markdown(ep, playlist, week)

        slug = ep["theme"].lower().replace(" ", "-")
        out_path = output_dir / f"week-{week:02d}-{slug}.md"
        out_path.write_text(md, encoding="utf-8")

        total_ms = sum(t.get("duration_ms", 0) for t in playlist)
        episode_metas.append({
            "week": week,
            "theme": ep["theme"],
            "track_count": len(playlist),
            "duration": f"{total_ms // 60000}:{(total_ms // 1000) % 60:02d}",
        })
        print(f"  Week {week} ({ep['theme']}): {len(playlist)} tracks, "
              f"{total_ms // 60000} min — {out_path}", file=sys.stderr)

    summary_md = format_summary_markdown(series, episode_metas)
    summary_path = output_dir / "series-summary.md"
    summary_path.write_text(summary_md, encoding="utf-8")
    print(f"  Summary: {summary_path}", file=sys.stderr)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--series", required=True, type=Path,
                   help="Series context JSON (contexts/series/*.json)")
    p.add_argument("--catalog", required=True, type=Path,
                   help="Categorized catalog JSON (banks must exist)")
    p.add_argument("--output-dir", type=Path, default=Path("output"),
                   help="Directory to write per-episode and summary markdown")
    p.add_argument("--seed", type=int, default=None,
                   help="Random seed for reproducible selection")
    args = p.parse_args()

    generate_series(args.series, args.catalog, args.output_dir, args.seed)


if __name__ == "__main__":
    main()
