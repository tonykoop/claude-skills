#!/usr/bin/env python3
"""Inspect playlist-builder catalog, seed-bank, auth, and exclusion state."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

BANKS = tuple("ABCDE")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return None


def _count_track_ids(tracks: list[dict[str, Any]]) -> dict[str, int]:
    spotify = sum(1 for track in tracks if track.get("spotify_uri"))
    soundcloud = sum(1 for track in tracks if track.get("soundcloud_url"))
    return {
        "spotify_uri": spotify,
        "soundcloud_url": soundcloud,
        "any_platform_id": sum(
            1
            for track in tracks
            if track.get("spotify_uri") or track.get("soundcloud_url")
        ),
    }


def inspect_seed_banks(seed_bank_dir: Path) -> dict[str, Any]:
    counts: dict[str, int] = {}
    id_counts = {"spotify_uri": 0, "soundcloud_url": 0, "any_platform_id": 0}
    missing: list[str] = []
    for bank in BANKS:
        path = seed_bank_dir / f"{bank}.json"
        data = _load_json(path)
        if data is None:
            missing.append(bank)
            counts[bank] = 0
            continue
        if not isinstance(data, list):
            raise SystemExit(f"{path} must contain a JSON array of tracks.")
        counts[bank] = len(data)
        bank_id_counts = _count_track_ids(data)
        for key, value in bank_id_counts.items():
            id_counts[key] += value
    return {
        "path": str(seed_bank_dir),
        "counts_by_bank": counts,
        "total_tracks": sum(counts.values()),
        "platform_id_counts": id_counts,
        "missing_banks": missing,
    }


def inspect_catalog(catalog_path: Path | None) -> dict[str, Any]:
    if not catalog_path:
        return {
            "path": None,
            "present": False,
            "counts_by_bank": {bank: 0 for bank in BANKS},
            "total_tracks": 0,
            "platform_id_counts": {
                "spotify_uri": 0,
                "soundcloud_url": 0,
                "any_platform_id": 0,
            },
        }

    data = _load_json(catalog_path)
    if data is None:
        raise SystemExit(f"Catalog not found: {catalog_path}")
    banks = data.get("banks") or {}
    counts: dict[str, int] = {}
    id_counts = {"spotify_uri": 0, "soundcloud_url": 0, "any_platform_id": 0}
    for bank in BANKS:
        tracks = banks.get(bank, [])
        if not isinstance(tracks, list):
            raise SystemExit(f"Catalog bank {bank} must be a JSON array.")
        counts[bank] = len(tracks)
        bank_id_counts = _count_track_ids(tracks)
        for key, value in bank_id_counts.items():
            id_counts[key] += value
    return {
        "path": str(catalog_path),
        "present": True,
        "source": data.get("source"),
        "counts_by_bank": counts,
        "total_tracks": sum(counts.values()),
        "platform_id_counts": id_counts,
        "exclusions_count": len(data.get("exclusions") or []),
    }


def inspect_auth() -> dict[str, bool]:
    spotify = bool(
        os.getenv("SPOTIFY_ACCESS_TOKEN")
        or (
            os.getenv("SPOTIFY_CLIENT_ID")
            and os.getenv("SPOTIFY_CLIENT_SECRET")
        )
    )
    soundcloud = bool(
        os.getenv("SOUNDCLOUD_ACCESS_TOKEN")
        or os.getenv("SOUNDCLOUD_CLIENT_ID")
    )
    return {
        "spotify": spotify,
        "soundcloud": soundcloud,
    }


def default_exclusion_paths() -> list[Path]:
    paths = [Path.home() / ".playlist-builder" / "used_tracks.json"]
    appdata = os.getenv("APPDATA")
    if appdata:
        paths.append(Path(appdata) / "playlist-builder" / "used_tracks.json")
    return paths


def inspect_exclusions(paths: list[Path]) -> dict[str, Any]:
    found = []
    for path in paths:
        data = _load_json(path)
        if data is None:
            continue
        count = len(data) if isinstance(data, list) else len(data.get("tracks", []))
        found.append({"path": str(path), "entries": count})
    return {
        "checked_paths": [str(path) for path in paths],
        "found": found,
        "present": bool(found),
    }


def recommend_mode(catalog: dict[str, Any], seed_banks: dict[str, Any],
                   auth: dict[str, bool], min_tracks: int) -> str:
    source = catalog if catalog.get("present") else seed_banks
    total_tracks = int(source.get("total_tracks") or 0)
    platform_ids = source.get("platform_id_counts", {}).get("any_platform_id", 0)
    platform_auth = auth.get("spotify") or auth.get("soundcloud")
    if total_tracks >= min_tracks and platform_ids >= min_tracks and platform_auth:
        return "verified"
    if total_tracks >= min_tracks:
        return "search-assisted"
    if total_tracks > 0:
        return "sparse"
    return "manual-curation"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path)
    parser.add_argument(
        "--seed-bank-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "seed-banks",
    )
    parser.add_argument(
        "--tony-catalog",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "references"
        / "TonyKoop_Yoga_Playlists.xlsx",
    )
    parser.add_argument("--min-tracks", type=int, default=8)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    seed_banks = inspect_seed_banks(args.seed_bank_dir)
    catalog = inspect_catalog(args.catalog)
    auth = inspect_auth()
    exclusions = inspect_exclusions(default_exclusion_paths())
    report = {
        "schema_version": 1,
        "seed_banks": seed_banks,
        "catalog": catalog,
        "auth": auth,
        "tony_catalog": {
            "path": str(args.tony_catalog),
            "present": args.tony_catalog.exists(),
        },
        "exclusions": exclusions,
        "recommended_mode": recommend_mode(
            catalog,
            seed_banks,
            auth,
            args.min_tracks,
        ),
        "mode_definitions": {
            "verified": "Enough tracks, exact IDs, and auth are available.",
            "search-assisted": "Enough tracks exist, but exact platform readiness is not verified.",
            "sparse": "Some catalog material exists, but not enough for a complete playlist.",
            "manual-curation": "No usable catalog material was found.",
        },
    }

    payload = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
