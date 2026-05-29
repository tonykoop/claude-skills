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


def _track_id(track: dict) -> str:
    return (track.get("spotify_uri")
            or track.get("soundcloud_url")
            or f"{track.get('artist','')}|{track.get('title','')}")


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


def format_markdown(playlist, context, theme, playlist_number=None):
    total_ms = sum(t.get("duration_ms", 0) for t in playlist)
    total_min = total_ms / 60_000
    title = f"{playlist_number}. {theme}" if playlist_number and theme else (theme or "Untitled")
    arc_summary = " -> ".join(p["name"] for p in context["phases"])

    lines = [
        f"# Playlist - {context.get('name','Untitled')}: {title}",
        "",
        f"**Context:** `{context['id']}` * **Total duration:** {int(total_min)}:{int((total_ms % 60000) / 1000):02d} * **Tracks:** {len(playlist)}",
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
        "| # | Time | Phase | Bank | Artist | Title | Duration |",
        "|---|------|-------|------|--------|-------|----------|",
    ]
    cum_min = 0.0
    for i, t in enumerate(playlist, 1):
        dur = (t.get("duration_ms") or 0) / 60_000
        time_str = f"{int(cum_min)}:{int((cum_min % 1) * 60):02d}"
        dur_str = f"{int(dur)}:{int((t.get('duration_ms', 0) % 60000) / 1000):02d}"
        artist = (t.get("artist") or "")[:25]
        ttl = (t.get("title") or "")[:40]
        lines.append(
            f"| {i} | {time_str} | {t.get('phase','')} | {t.get('bank','')} | {artist} | {ttl} | {dur_str} |"
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

    if sp_uris:
        lines.append("")
        lines.append("## Spotify URIs (bulk-add via desktop search bar)")
        lines.append("")
        lines.append("```")
        for u in sp_uris:
            lines.append(u)
        lines.append("```")

    return "\n".join(lines) + "\n"


CATALOG_STATES = ("auto", "verified", "search-assisted", "sparse", "manual-curation")


def emit_honesty_block(context: dict, theme: str, mode: str,
                       skill_dir: Path, preflight: dict) -> str:
    """Emit the sparse / manual-curation output instead of a numbered tracklist.

    See references/HONESTY_MODES.md for the full taxonomy. The output marks
    every row with the schema fields required by issue #72 acceptance
    criterion 4 even when rows are absent (the schema rule still holds).
    """
    title = context.get("name") or context.get("title") or "Class playlist"
    auth_avail = preflight.get("platform_auth_available", False)
    seed_total = preflight.get("seed_banks", {}).get("total_count", 0)

    lines = [
        f"# {title}",
        "",
        f"_Theme:_ {theme or '(none specified)'}",
        f"_Catalog mode:_ `{mode}` (preflight recommended; "
        f"platform_auth_available={auth_avail}, seed_total={seed_total})_",
        "",
        "## Tier 1 — Verified bundled tracks",
        "",
        "| phase | bank | search_string | approx_duration | "
        "spotify_uri | exact_id_status | verification_required |",
        "|---|---|---|---|---|---|---|",
    ]

    verified_rows = []
    banks_dir = skill_dir / "seed-banks"
    for bank_name in ("A", "B", "C", "D", "E"):
        bank_path = banks_dir / f"{bank_name}.json"
        if not bank_path.exists():
            continue
        try:
            tracks = json.loads(bank_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(tracks, list):
            continue
        for t in tracks:
            uri = t.get("spotify_uri") or t.get("soundcloud_url") or ""
            if not uri:
                continue
            dur_ms = t.get("duration_ms", 0)
            dur = f"{dur_ms // 60000}:{(dur_ms // 1000) % 60:02d}" if dur_ms else "n/a"
            search = f"{t.get('artist', '')} {t.get('title', '')}".strip()
            verified_rows.append(
                f"| (any) | {bank_name} | {search} | {dur} | {uri} | "
                f"verified | false |"
            )

    if verified_rows:
        lines.extend(verified_rows)
    else:
        lines.append("| _no verified bundled tracks available_ |  |  |  |  |  |  |")

    lines.extend([
        "",
        "## Tier 2 — Copy-paste curation prompt",
        "",
        "```text",
        f"Build a {context.get('total_minutes', 60)}-minute playlist for the "
        f"class titled '{title}'.",
        f"Theme: {theme or '(theme to be filled in by teacher)'}",
        "",
        "Strict no-explicit content filter. Slot the playlist to this energy arc:",
    ])
    for phase in context.get("phases", []):
        lines.append(
            f"  - {phase.get('start_min', '?'):>3}-"
            f"{phase.get('end_min', '?'):>3} min  "
            f"{phase.get('name', '?'):<24} "
            f"bank={phase.get('bank', '?')} "
            f"energy={phase.get('energy', '?')}"
        )
    lines.extend([
        "",
        "Return exact Spotify search strings (or URIs if available) for each "
        "slot, plus 2-line rationale per track. Mark each row with "
        "exact_id_status=verified|unverified|requires_auth.",
        "```",
        "",
    ])

    if mode == "sparse":
        lines.extend([
            "## Tier 3 — Recall-only candidate ladder",
            "",
            "_Optional. The agent MAY emit candidate tracks here, but every "
            "row must carry `exact_id_status: unverified` and "
            "`verification_required: true`. The ladder is scaffolding, not "
            "an answer; teachers verify before paste._",
            "",
        ])

    lines.extend([
        "## Verification checklist",
        "",
        "- [ ] Search each unverified track on the platform; runtime ±10 sec",
        "- [ ] Confirm `is_explicit=false` on every track",
        "- [ ] Confirm playlist totals the arc length after substitutions",
        "- [ ] Confirm Tier-1 verified URIs still resolve in your region",
        "",
    ])
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--context", required=True, type=Path)
    p.add_argument("--catalog", type=Path,
                   help="Categorized catalog JSON. Required for verified/"
                        "search-assisted modes; optional otherwise.")
    p.add_argument("--catalog-state", choices=CATALOG_STATES, default="auto",
                   help="Output mode. 'auto' runs the preflight and honors "
                        "the result. See references/HONESTY_MODES.md.")
    p.add_argument("--skill-dir", type=Path,
                   default=Path(__file__).resolve().parent.parent,
                   help="Skill root, for preflight and bundled seed lookup.")
    p.add_argument("--theme", default="")
    p.add_argument("--output", type=Path)
    p.add_argument("--seed", type=int)
    p.add_argument("--exclude-ids", default="")
    p.add_argument("--number", type=int)
    args = p.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import inspect_catalog
    preflight = inspect_catalog.build_report(
        args.skill_dir, args.catalog if args.catalog else None,
    )
    mode = args.catalog_state
    if mode == "auto":
        mode = preflight["recommended_output_mode"]
    print(f"  Catalog state: {mode} "
          f"(auth={preflight['platform_auth_available']}, "
          f"seed_total={preflight['seed_banks']['total_count']})",
          file=sys.stderr)

    context = load_context(args.context)

    if mode in ("sparse", "manual-curation"):
        md = emit_honesty_block(context, args.theme, mode,
                                args.skill_dir, preflight)
        if args.output:
            args.output.write_text(md)
            print(f"  Saved honesty-block output to {args.output}",
                  file=sys.stderr)
        else:
            print(md)
        return

    if not args.catalog:
        print("error: --catalog is required for "
              f"{mode} mode (use --catalog-state sparse "
              "or manual-curation if you have no catalog)",
              file=sys.stderr)
        sys.exit(2)

    catalog = load_catalog(args.catalog)
    extras = {x.strip() for x in args.exclude_ids.split(",") if x.strip()}

    playlist = generate_playlist(context, catalog, theme=args.theme,
                                 extra_excludes=extras)
    md = format_markdown(playlist, context, args.theme,
                         playlist_number=args.number)

    total_ms = sum(t.get("duration_ms", 0) for t in playlist)
    print(f"  Generated {len(playlist)} tracks, {total_ms/60000:.1f} min",
          file=sys.stderr)

    if args.output:
        args.output.write_text(md)
        print(f"  Saved to {args.output}", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()
