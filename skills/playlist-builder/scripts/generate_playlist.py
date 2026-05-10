#!/usr/bin/env python3
"""
Playlist Builder v2 — generalized generator.

Reads a context profile JSON (the arc) and a categorized catalog JSON (tracks
binned into banks), produces a tracklist that follows the arc.

Usage:
    python generate_playlist.py \\
        --context ../contexts/yoga-power.json \\
        --catalog <catalog.json> \\
        --theme "aparigraha letting go" \\
        --number 37 \\
        --output playlist.md
"""

from __future__ import annotations
import argparse
import json
import random
import sys
from pathlib import Path


def load_context(path: Path) -> dict:
    return json.loads(path.read_text())


def load_catalog(path: Path) -> dict:
    return json.loads(path.read_text())


def load_preflight(path: Path | None) -> dict:
    if not path:
        return {}
    return json.loads(path.read_text())


def _track_id(track: dict) -> str:
    return (track.get("spotify_uri")
            or track.get("soundcloud_url")
            or f"{track.get('artist','')}|{track.get('title','')}")


def _duration_label(duration_ms: int | None) -> str:
    duration_ms = duration_ms or 0
    total_seconds = duration_ms // 1000
    return f"{total_seconds // 60}:{total_seconds % 60:02d}"


def _search_string(track: dict) -> str:
    title = str(track.get("title") or "").strip()
    artist = str(track.get("artist") or "").strip()
    album = str(track.get("album") or "").strip()
    return " ".join(part for part in (artist, title, album) if part)


def _platform_auth_available(preflight: dict) -> bool:
    auth = preflight.get("auth") or {}
    return bool(auth.get("spotify") or auth.get("soundcloud"))


def _resolve_honesty_mode(mode: str, preflight: dict, playlist: list[dict]) -> str:
    if mode != "auto":
        return mode
    if preflight.get("recommended_mode"):
        return str(preflight["recommended_mode"])
    total = len(playlist)
    has_ids = any(t.get("spotify_uri") or t.get("soundcloud_url") for t in playlist)
    if total >= 8 and has_ids and _platform_auth_available(preflight):
        return "verified"
    if total >= 8:
        return "search-assisted"
    if total > 0:
        return "sparse"
    return "manual-curation"


def _exact_id_status(track: dict, honesty_mode: str, platform_auth: bool) -> str:
    has_platform_id = bool(track.get("spotify_uri") or track.get("soundcloud_url"))
    if honesty_mode == "verified" and has_platform_id and platform_auth:
        return "verified"
    if has_platform_id and not platform_auth:
        return "requires_auth"
    return "unverified"


def candidate_entry(track: dict, honesty_mode: str, preflight: dict) -> dict:
    platform_auth = _platform_auth_available(preflight)
    return {
        "phase": track.get("phase", ""),
        "bank": track.get("bank", ""),
        "artist": track.get("artist", ""),
        "title": track.get("title", ""),
        "search_string": _search_string(track),
        "approx_duration": _duration_label(track.get("duration_ms")),
        "spotify_uri": track.get("spotify_uri"),
        "soundcloud_url": track.get("soundcloud_url"),
        "exact_id_status": _exact_id_status(track, honesty_mode, platform_auth),
        "verification_required": [
            "Confirm the exact platform result matches artist, title, and duration.",
            "Confirm explicit-content flags and disruptive vocals before teaching.",
            "Confirm playlist order, no shuffle, and crossfade settings in-platform.",
        ],
        "platform_auth_available": platform_auth,
    }


def score_theme_match(track: dict, theme_keywords: list) -> int:
    if not theme_keywords:
        return 0
    tags = track.get("tags") or []
    if isinstance(tags, list):
        tags_str = " ".join(str(t) for t in tags)
    else:
        tags_str = str(tags)
    text = " ".join([
        str(track.get("title", "")),
        tags_str,
        str(track.get("genre", "")),
    ]).lower()
    score = 0
    for kw in theme_keywords:
        kw_l = kw.lower()
        if kw_l in text:
            score += 2
        for word in text.split():
            if kw_l in word or word in kw_l:
                score += 1
    return score


def select_for_phase(bank_tracks, count, window_min, theme_keywords=None,
                     exclude_ids=None, prefer_theme=False):
    exclude_ids = exclude_ids or set()
    available = [
        t for t in bank_tracks
        if _track_id(t) not in exclude_ids
        and (t.get("duration_ms") or 0) > 0
    ]
    if not available:
        return []
    if prefer_theme and theme_keywords:
        available.sort(key=lambda t: score_theme_match(t, theme_keywords), reverse=True)
        return available[:count]
    random.shuffle(available)
    return available[:count]


def generate_playlist(context, catalog, theme="", extra_excludes=None):
    theme_keywords = [w.strip() for w in theme.split() if w.strip()] if theme else []
    excludes = set(catalog.get("exclusions", []))
    if extra_excludes:
        excludes.update(extra_excludes)

    playlist = []
    used_in_run = set()

    for phase in context["phases"]:
        bank = catalog["banks"].get(phase["bank"], [])
        target = (phase["min_tracks"] + phase["max_tracks"]) // 2
        picks = select_for_phase(
            bank, target, tuple(phase["window_min"]),
            theme_keywords=theme_keywords,
            exclude_ids=excludes | used_in_run,
        )
        for p in picks:
            playlist.append({**p, "phase": phase["name"], "bank": phase["bank"]})
            used_in_run.add(_track_id(p))

    anchor = context.get("theme_anchor")
    if anchor and theme_keywords:
        anchor_bank = catalog["banks"].get(anchor["bank"], [])
        anchor_picks = select_for_phase(
            anchor_bank, anchor.get("tracks", 1), tuple(anchor["window_min"]),
            theme_keywords=theme_keywords,
            exclude_ids=excludes | used_in_run,
            prefer_theme=True,
        )
        if anchor_picks:
            anchor_track = {**anchor_picks[0], "phase": "Theme Anchor", "bank": anchor["bank"]}
            cum_ms = 0
            window_start_ms = anchor["window_min"][0] * 60_000
            insert_idx = len(playlist)
            for i, t in enumerate(playlist):
                if cum_ms >= window_start_ms:
                    insert_idx = i
                    break
                cum_ms += t.get("duration_ms", 0)
            playlist.insert(insert_idx, anchor_track)
            used_in_run.add(_track_id(anchor_track))

    return playlist


def format_candidate_json(playlist, context, theme, honesty_mode, preflight):
    return {
        "context": context.get("id"),
        "theme": theme,
        "honesty_mode": honesty_mode,
        "platform_auth_available": _platform_auth_available(preflight),
        "candidate_playlist_is_paste_ready": honesty_mode == "verified",
        "verification_required": [
            "Treat search-assisted, sparse, and manual-curation outputs as useful planning aids, not paste-ready exact playlists.",
            "Only exact IDs marked verified should be bulk-pasted or automated into a platform playlist.",
            "If IDs are marked requires_auth, authenticate or verify them manually before use.",
        ],
        "tracks": [
            candidate_entry(track, honesty_mode, preflight)
            for track in playlist
        ],
    }


def _suggest_tags(context, theme):
    base = {
        "yoga-power": ["yoga", "vinyasa", "power-flow", "heated"],
        "yoga-power-sustained": ["yoga", "vinyasa", "power-flow", "sustained"],
        "yoga-sculpt": ["yoga", "sculpt", "strength", "cardio"],
        "yoga-restorative": ["yoga", "restorative", "yin", "slow"],
        "yoga-vinyasa": ["yoga", "vinyasa", "flow"],
        "spa-massage": ["spa", "massage", "ambient", "relaxation"],
        "spin-bike": ["spin", "cycling", "indoor-cycling", "intervals"],
        "party": ["party", "dance", "house"],
    }
    tags = list(base.get(context["id"], ["yoga", context["id"]]))
    if theme:
        tags.extend(t.strip().replace(" ", "-") for t in theme.split() if len(t) > 2)
    seen, out = set(), []
    for t in tags:
        k = t.lower()
        if k not in seen:
            seen.add(k); out.append(k)
    return ", ".join(out)


def format_markdown(playlist, context, theme, playlist_number=None,
                    honesty_mode="verified", preflight=None):
    preflight = preflight or {}
    total_ms = sum(t.get("duration_ms", 0) for t in playlist)
    total_min = total_ms / 60_000
    title = f"{playlist_number}. {theme}" if playlist_number and theme else (theme or "Untitled")
    arc_summary = " -> ".join(p["name"] for p in context["phases"])
    paste_ready = honesty_mode == "verified"

    lines = [
        f"# Playlist - {context.get('name','Untitled')}: {title}",
        "",
        f"**Context:** `{context['id']}` * **Total duration:** {int(total_min)}:{int((total_ms % 60000) / 1000):02d} * **Tracks:** {len(playlist)}",
        f"**Honesty mode:** `{honesty_mode}` * **Paste-ready exact IDs:** {'yes' if paste_ready else 'no'}",
        "",
        "## Suggested description (copy-paste into SoundCloud / Spotify / Apple Music)",
        "",
        "```",
        f"{int(total_min)}-min {context.get('name','yoga')} class * Theme: {theme or '(none)'}",
        f"Energy arc: {arc_summary}",
        f"Built with playlist-builder * github.com/tonykoop/playlist-builder",
        "```",
        "",
        "## Suggested tags",
        "",
        "```",
        _suggest_tags(context, theme),
        "```",
        "",
        "## Tracklist",
        "",
        "| # | Time | Phase | Bank | Artist | Title | Duration | Exact ID status |",
        "|---|------|-------|------|--------|-------|----------|-----------------|",
    ]
    cum_min = 0.0
    for i, t in enumerate(playlist, 1):
        dur = (t.get("duration_ms") or 0) / 60_000
        time_str = f"{int(cum_min)}:{int((cum_min % 1) * 60):02d}"
        dur_str = f"{int(dur)}:{int((t.get('duration_ms', 0) % 60000) / 1000):02d}"
        artist = (t.get("artist") or "")[:25]
        ttl = (t.get("title") or "")[:40]
        exact_id_status = _exact_id_status(
            t,
            honesty_mode,
            _platform_auth_available(preflight),
        )
        lines.append(
            f"| {i} | {time_str} | {t.get('phase','')} | {t.get('bank','')} | {artist} | {ttl} | {dur_str} | {exact_id_status} |"
        )
        cum_min += dur

    sc_links = [t.get("soundcloud_url") for t in playlist if t.get("soundcloud_url")]
    sp_uris = [t.get("spotify_uri") for t in playlist if t.get("spotify_uri")]

    if sc_links:
        lines.append("")
        lines.append("## SoundCloud links")
        lines.append("")
        for i, t in enumerate(playlist, 1):
            if t.get("soundcloud_url"):
                lines.append(f"{i}. [{t.get('artist','')} - {(t.get('title') or '')[:50]}]({t['soundcloud_url']})")

    if sp_uris and paste_ready:
        lines.append("")
        lines.append("## Spotify URIs (bulk-add via desktop search bar)")
        lines.append("")
        lines.append("```")
        for u in sp_uris:
            lines.append(u)
        lines.append("```")
    elif sp_uris:
        lines.append("")
        lines.append("## Spotify URI candidates")
        lines.append("")
        lines.append(
            "These IDs are present in the catalog but are not marked verified "
            "for this run. Authenticate or manually confirm exact track/version "
            "before bulk-adding."
        )
        lines.append("")
        lines.append("```")
        for u in sp_uris:
            lines.append(u)
        lines.append("```")

    if honesty_mode != "verified":
        lines.append("")
        lines.append("## Candidate playlist verification")
        lines.append("")
        lines.append(
            "This output is useful for curation, phase timing, and search, but "
            "it is not paste-ready until exact platform IDs are verified."
        )
        lines.append("")
        lines.append("| # | Search string | Approx duration | Status |")
        lines.append("|---|---------------|-----------------|--------|")
        for i, t in enumerate(playlist, 1):
            candidate = candidate_entry(t, honesty_mode, preflight)
            lines.append(
                f"| {i} | {candidate['search_string']} | {candidate['approx_duration']} | {candidate['exact_id_status']} |"
            )

    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--context", required=True, type=Path)
    p.add_argument("--catalog", required=True, type=Path)
    p.add_argument("--theme", default="")
    p.add_argument("--output", type=Path)
    p.add_argument("--candidate-json", type=Path)
    p.add_argument("--preflight", type=Path)
    p.add_argument(
        "--honesty-mode",
        choices=[
            "auto",
            "verified",
            "search-assisted",
            "sparse",
            "manual-curation",
        ],
        default="auto",
        help="Controls whether exact IDs are treated as verified or candidates.",
    )
    p.add_argument("--seed", type=int)
    p.add_argument("--exclude-ids", default="")
    p.add_argument("--number", type=int)
    args = p.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    context = load_context(args.context)
    catalog = load_catalog(args.catalog)
    preflight = load_preflight(args.preflight)
    extras = {x.strip() for x in args.exclude_ids.split(",") if x.strip()}

    playlist = generate_playlist(context, catalog, theme=args.theme, extra_excludes=extras)
    honesty_mode = _resolve_honesty_mode(args.honesty_mode, preflight, playlist)
    md = format_markdown(
        playlist,
        context,
        args.theme,
        playlist_number=args.number,
        honesty_mode=honesty_mode,
        preflight=preflight,
    )
    candidate_json = format_candidate_json(
        playlist,
        context,
        args.theme,
        honesty_mode,
        preflight,
    )

    total_ms = sum(t.get("duration_ms", 0) for t in playlist)
    print(
        f"  Generated {len(playlist)} tracks, {total_ms/60000:.1f} min "
        f"({honesty_mode})",
        file=sys.stderr,
    )

    if args.output:
        args.output.write_text(md)
        print(f"  Saved to {args.output}", file=sys.stderr)
    else:
        print(md)

    if args.candidate_json:
        args.candidate_json.write_text(json.dumps(candidate_json, indent=2) + "\n")
        print(f"  Saved candidate schema to {args.candidate_json}", file=sys.stderr)


if __name__ == "__main__":
    main()
