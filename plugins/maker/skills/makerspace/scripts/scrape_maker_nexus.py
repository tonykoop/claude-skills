#!/usr/bin/env python3
"""
scrape_maker_nexus.py
=====================

Scrape the Maker Nexus DokuWiki equipment pages and emit / merge them
into spaces/maker-nexus/.

This is a v0.1 STUB. The hard part — DokuWiki page parsing — is sketched
but not implemented. The scaffolding is here so that adding the parser
later is a focused task, not a rewrite.

Usage:
    python3 scripts/scrape_maker_nexus.py --output ./spaces/maker-nexus/
    python3 scripts/scrape_maker_nexus.py --output ./spaces/maker-nexus/ --merge
    python3 scripts/scrape_maker_nexus.py --dry-run

Roadmap:
    [ ] Parse the equipment-list landing page.
    [ ] Walk into each per-tool subpage.
    [ ] Extract tool name, location, specs, allowed/banned materials,
        cert required, reservation rules.
    [ ] Merge into existing profile.yaml without overwriting hand-curated
        sections (preserve `# Hand-curated` blocks).
    [ ] Emit a diff report so the user knows what changed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from textwrap import dedent


WIKI_BASE = "https://wiki.makernexus.org"
EQUIPMENT_PATH = "/equipment"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Scrape Maker Nexus DokuWiki into a space profile.",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path("./spaces/maker-nexus/"),
        help="Output directory for the scraped profile (default: "
        "./spaces/maker-nexus/).",
    )
    p.add_argument(
        "--merge",
        action="store_true",
        help="Merge with existing profile.yaml, preserving hand-curated "
        "sections marked '# Hand-curated' or '# notes'.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write any files; print what would be done.",
    )
    p.add_argument(
        "--wiki-base",
        default=WIKI_BASE,
        help=f"Base URL of the wiki (default: {WIKI_BASE}).",
    )
    return p.parse_args(argv)


def scrape_equipment_list(wiki_base: str) -> list[dict]:
    """Scrape the equipment landing page and return per-tool dicts.

    NOT IMPLEMENTED in v0.1. Returns an empty list with a friendly
    message about how to populate the profile manually.
    """
    print(
        dedent(
            f"""\
            ⚠ Scraper stub — v0.1 doesn't actually scrape yet.

            To populate spaces/maker-nexus/ for now:
              1. Visit {wiki_base}{EQUIPMENT_PATH}
              2. Hand-fill the entries in profile.yaml (or the example
                 in spaces/maker-nexus/tools.md).
              3. Add per-tool details to tools.md with anchor headings
                 matching the YAML id (e.g., `### #cnc-onsrud-1`).

            When the parser is implemented, this script will:
              - Walk every linked equipment page
              - Extract tool name, specs, materials, certs
              - Merge into profile.yaml with conflict markers
              - Emit a diff so you can review changes before committing
            """
        ),
        file=sys.stderr,
    )
    return []


def merge_into_profile(
    output_dir: Path,
    scraped: list[dict],
    *,
    dry_run: bool = False,
) -> None:
    """Merge scraped data into output_dir/profile.yaml.

    Preserves hand-curated sections in `tools.md` marked
    `# Hand-curated` or any heading the user explicitly tags.
    """
    profile_path = output_dir / "profile.yaml"
    tools_md = output_dir / "tools.md"

    if not scraped:
        print(
            "Nothing scraped (stub mode). Profile and tools.md unchanged.",
            file=sys.stderr,
        )
        return

    # When the parser is implemented, the merge logic goes here.
    # Sketch:
    #   1. Load existing profile.yaml as a YAML dict.
    #   2. For each scraped tool: if id exists, update non-curated
    #      fields; if id doesn't exist, append.
    #   3. Write profile.yaml back.
    #   4. For tools.md, append a `## Scraped <date>` section with the
    #      new entries; leave existing `# Hand-curated` and other
    #      sections untouched.
    if dry_run:
        print(f"DRY RUN: would update {profile_path} and {tools_md}")
    else:
        print(
            "Merge logic not yet implemented — see roadmap in this "
            "script's docstring.",
            file=sys.stderr,
        )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.output.exists() and not args.dry_run:
        args.output.mkdir(parents=True, exist_ok=True)

    scraped = scrape_equipment_list(args.wiki_base)
    merge_into_profile(args.output, scraped, dry_run=args.dry_run)

    if not scraped:
        return 0  # Stub mode is intentional, not an error.

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
