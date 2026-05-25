#!/usr/bin/env python3
"""
Catalog/auth-state preflight for playlist-builder.

Reports the state of every catalog source the skill knows about, then picks
an output mode that the generator can honor.

The four modes are:

  - verified         every slot can be filled from auth'd library or rich
                     bundled banks; exact platform IDs are safe to emit.
  - search-assisted  some slots verified, others must be search strings;
                     output marks each row's exact_id_status.
  - sparse           bundled banks are mostly empty AND no auth/Mode B is
                     reachable; generator must emit a tiered honesty block,
                     not a numbered tracklist.
  - manual-curation  no usable catalog at all (banks empty, no auth, no
                     Mode B); generator emits the curation prompt only.

Usage:
    python inspect_catalog.py [--skill-dir DIR] [--catalog PATH]
                              [--quiet]

Output: JSON to stdout. Exit 0 always (it's a preflight, not a gate). Pipe
into the generator with --catalog-state auto to honor the recommendation.

Acceptance criteria covered: issue #72, criterion 2 (helper exists) and
issue #72, criterion 4 (output schema fields).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


SEED_BANK_NAMES = ["A", "B", "C", "D", "E"]
RICH_BANK_THRESHOLD = 8


def count_seed_bank(path: Path) -> int:
    """Return the track count for a single seed-bank JSON file.

    The seed-bank schema is a top-level array of track objects. Empty
    file or missing file returns 0. Malformed JSON returns -1 so the
    caller can flag it without crashing the whole preflight.
    """
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return -1
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict) and "tracks" in data and isinstance(data["tracks"], list):
        return len(data["tracks"])
    return -1


def inspect_seed_banks(skill_dir: Path) -> dict[str, Any]:
    banks_dir = skill_dir / "seed-banks"
    counts = {}
    malformed = []
    for name in SEED_BANK_NAMES:
        n = count_seed_bank(banks_dir / f"{name}.json")
        if n == -1:
            malformed.append(name)
            counts[name] = 0
        else:
            counts[name] = n
    total = sum(counts.values())
    return {
        "counts": counts,
        "total_count": total,
        "rich_bank_threshold": RICH_BANK_THRESHOLD,
        "any_bank_rich": any(c >= RICH_BANK_THRESHOLD for c in counts.values()),
        "all_banks_empty": total == 0,
        "malformed_files": malformed,
    }


def inspect_mode_b(skill_dir: Path) -> dict[str, Any]:
    """Tony Koop catalog presence (Mode B in the SKILL.md taxonomy)."""
    candidates = [
        skill_dir / "references" / "CATALOG_TONY_KOOP.md",
        skill_dir / "references" / "TonyKoop_Yoga_Playlists.xlsx",
    ]
    present = [str(p.relative_to(skill_dir)) for p in candidates if p.exists()]
    return {
        "loaded": bool(present),
        "files_present": present,
    }


def inspect_auth() -> dict[str, Any]:
    """Best-effort auth detection.

    The MCP connectors are runtime-attached, not env-detectable from a
    plain Python process. We treat env variables, well-known token files,
    and a couple of standard cache paths as evidence. False negatives are
    expected; the preflight is allowed to recommend a more conservative
    mode than is strictly necessary.
    """
    spotify_signals = []
    soundcloud_signals = []

    for env in ("SPOTIFY_ACCESS_TOKEN", "SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET"):
        if os.environ.get(env):
            spotify_signals.append(f"env:{env}")
    for env in ("SOUNDCLOUD_OAUTH_TOKEN", "SOUNDCLOUD_CLIENT_ID"):
        if os.environ.get(env):
            soundcloud_signals.append(f"env:{env}")

    home = Path(os.path.expanduser("~"))
    for cand in (home / ".cache" / "spotipy", home / ".spotify_cache"):
        if cand.exists():
            spotify_signals.append(f"cache:{cand}")

    return {
        "spotify_reachable": bool(spotify_signals),
        "soundcloud_reachable": bool(soundcloud_signals),
        "any_platform_auth_available": bool(spotify_signals or soundcloud_signals),
        "spotify_signals": spotify_signals,
        "soundcloud_signals": soundcloud_signals,
    }


def inspect_user_catalog(catalog_path: Path | None) -> dict[str, Any]:
    """User-supplied categorized catalog JSON (Mode A output)."""
    if catalog_path is None:
        return {"loaded": False, "path": None, "track_count": 0}
    if not catalog_path.exists():
        return {"loaded": False, "path": str(catalog_path), "track_count": 0}
    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "loaded": False,
            "path": str(catalog_path),
            "track_count": 0,
            "error": "malformed-json",
        }
    count = 0
    if isinstance(data, dict):
        for bank in SEED_BANK_NAMES:
            tracks = data.get(bank) or data.get(bank.lower())
            if isinstance(tracks, list):
                count += len(tracks)
        if count == 0 and isinstance(data.get("tracks"), list):
            count = len(data["tracks"])
    elif isinstance(data, list):
        count = len(data)
    return {"loaded": count > 0, "path": str(catalog_path), "track_count": count}


def pick_mode(seed: dict, mode_b: dict, auth: dict, user_catalog: dict) -> str:
    """Select an output mode honoring the four-tier taxonomy.

    Order matters: verified > search-assisted > sparse > manual-curation.
    The generator can override with --catalog-state if the caller wants.
    """
    if user_catalog.get("loaded") and user_catalog.get("track_count", 0) >= 30:
        return "verified"
    if auth.get("any_platform_auth_available"):
        return "verified"
    if seed.get("any_bank_rich"):
        return "verified"
    if mode_b.get("loaded"):
        return "search-assisted"
    if seed.get("total_count", 0) > 0:
        return "sparse"
    return "manual-curation"


def explain_mode(mode: str) -> str:
    return {
        "verified": (
            "Every slot can be filled with a verified platform ID. Generator "
            "may emit exact tracklists with exact_id_status=verified."
        ),
        "search-assisted": (
            "Some slots have verified IDs from bundled or Mode B; others "
            "are search strings. Generator marks each row's "
            "exact_id_status=verified|unverified|requires_auth."
        ),
        "sparse": (
            "Bundled seeds insufficient and no auth or Mode B is reachable. "
            "Generator MUST emit the three-tier honesty block (verified "
            "bundled + curation prompt + recall-only candidate ladder) "
            "instead of a numbered tracklist."
        ),
        "manual-curation": (
            "No usable catalog. Generator emits only the copy-paste "
            "curation prompt and leaves the tracklist for the user to "
            "produce externally."
        ),
    }[mode]


def build_report(skill_dir: Path, catalog_path: Path | None) -> dict[str, Any]:
    seed = inspect_seed_banks(skill_dir)
    mode_b = inspect_mode_b(skill_dir)
    auth = inspect_auth()
    user_catalog = inspect_user_catalog(catalog_path)
    mode = pick_mode(seed, mode_b, auth, user_catalog)
    return {
        "schema_version": 1,
        "skill_dir": str(skill_dir),
        "seed_banks": seed,
        "mode_b_tony_catalog": mode_b,
        "auth": auth,
        "user_catalog": user_catalog,
        "recommended_output_mode": mode,
        "mode_explanation": explain_mode(mode),
        "platform_auth_available": auth["any_platform_auth_available"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--skill-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Skill root (defaults to the parent of this script).",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help="Optional path to a categorized user catalog JSON.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress the human-readable summary on stderr.",
    )
    args = parser.parse_args()

    if not args.skill_dir.exists():
        print(f"error: skill-dir does not exist: {args.skill_dir}",
              file=sys.stderr)
        return 2

    report = build_report(args.skill_dir, args.catalog)
    print(json.dumps(report, indent=2, sort_keys=True))

    if not args.quiet:
        print("", file=sys.stderr)
        print(f"recommended_output_mode: {report['recommended_output_mode']}",
              file=sys.stderr)
        print(report["mode_explanation"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
