"""
book_layout.cli
===============
Command-line interface for the book layout engine.

Usage
-----
    python -m book_layout plan   --chapters 3,10,5 [--format photo-book] [--size letter]
    python -m book_layout album  --eras "2000s:12,2010s:18,2020s:8"
    python -m book_layout year   --instruments "handpan:10,barrel-organ:8"
    python -m book_layout validate --json-file book.json
    python -m book_layout export   --json-file book.json [--manifest-out manifest.json]
    python -m book_layout themes
    python -m book_layout templates

All commands are offline and deterministic.  No real images are read or
written.

Refs: claude-skills#210
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional


def _import() -> None:
    """Lazy-import guard: ensures the package is on sys.path."""
    pkg = Path(__file__).resolve().parents[1]
    if str(pkg) not in sys.path:
        sys.path.insert(0, str(pkg))


# ── sub-commands ──────────────────────────────────────────────────────────────

def cmd_plan(args: argparse.Namespace) -> int:
    """Plan a generic book from chapter item-count list."""
    from book_layout.planner import ChapterSpec, plan_book
    from book_layout.schema import BookFormat, PageSize
    from book_layout.export import to_json

    counts = [int(x.strip()) for x in args.chapters.split(",")]
    specs = [ChapterSpec(title=f"Chapter {i+1}", item_count=n)
             for i, n in enumerate(counts)]

    fmt = BookFormat(args.format)
    size = PageSize(args.size)

    book = plan_book(
        specs,
        book_title=args.title or "Untitled Book",
        book_format=fmt,
        page_size=size,
    )
    json_str = to_json(book, indent=2)
    if args.out:
        Path(args.out).write_text(json_str)
        print(f"Wrote {args.out}")
    else:
        print(json_str)
    _print_summary(book)
    return 0


def cmd_album(args: argparse.Namespace) -> int:
    """Build a family photo album from era specs."""
    from book_layout.album import EraSpec, AlbumConfig, build_album
    from book_layout.export import to_json

    eras: List[EraSpec] = []
    for token in args.eras.split(","):
        token = token.strip()
        if ":" in token:
            label, count_str = token.rsplit(":", 1)
            eras.append(EraSpec(title=label.strip(), item_count=int(count_str.strip())))
        else:
            eras.append(EraSpec(title=token, item_count=10))

    config = AlbumConfig(
        album_title=args.title or "Photo Album",
        include_cover=not args.no_cover,
    )
    book = build_album(eras, config=config)
    json_str = to_json(book, indent=2)
    if args.out:
        Path(args.out).write_text(json_str)
        print(f"Wrote {args.out}")
    else:
        print(json_str)
    _print_summary(book)
    return 0


def cmd_year(args: argparse.Namespace) -> int:
    """Build a yearbook from instrument specs."""
    from book_layout.yearbook import (
        InstrumentChapterSpec, InstrumentContentSpec,
        YearbookConfig, build_yearbook, GateStatus,
    )
    from book_layout.export import to_json

    specs: List[InstrumentChapterSpec] = []
    for token in args.instruments.split(","):
        token = token.strip()
        if ":" in token:
            name, count_str = token.rsplit(":", 1)
            n = int(count_str.strip())
        else:
            name = token
            n = 14   # default total spread across sections
        # Distribute n items across sections
        cover = 1
        detail = max(1, n // 4)
        lab = max(1, n // 6)
        gallery = max(0, n - cover - detail - lab)
        specs.append(InstrumentChapterSpec(
            repo_name=name.strip(),
            display_name=name.strip().replace("-", " ").title(),
            gate_status=GateStatus.PASSED,
            content=InstrumentContentSpec(
                cover_items=cover,
                build_gallery_items=gallery,
                experiment_lab_items=lab,
                detail_shot_items=detail,
            ),
        ))

    config = YearbookConfig(
        title=args.title or "Instrument Design Yearbook",
        edition=args.edition or "",
    )
    book = build_yearbook(specs, config=config)
    json_str = to_json(book, indent=2)
    if args.out:
        Path(args.out).write_text(json_str)
        print(f"Wrote {args.out}")
    else:
        print(json_str)
    _print_summary(book)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a serialised Book JSON file."""
    from book_layout.export import from_json
    from book_layout.validator import validate_book

    data = Path(args.json_file).read_text()
    book = from_json(data)
    result = validate_book(book)

    if result.errors:
        print(f"ERRORS ({len(result.errors)}):")
        for e in result.errors:
            print(f"  ✗ {e}")
    if result.warnings:
        print(f"WARNINGS ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  ⚠ {w}")
    if result.ok:
        print(f"✓ PASS — {book.total_pages} pages, {book.total_slots} slots, "
              f"{book.filled_slots} filled")
        return 0
    else:
        print(f"✗ FAIL — {len(result.errors)} error(s)")
        return 1


def cmd_export(args: argparse.Namespace) -> int:
    """Export a Book JSON file to a BookManifest."""
    from book_layout.export import from_json, export_book, manifest_to_json

    data = Path(args.json_file).read_text()
    book = from_json(data)
    manifest = export_book(book)
    manifest_json = manifest_to_json(manifest, indent=2)

    out_path = args.manifest_out or args.json_file.replace(".json", "-manifest.json")
    Path(out_path).write_text(manifest_json)
    print(f"Manifest written to {out_path}")
    print(f"  {manifest.total_pages} pages | {manifest.total_slots} slots | "
          f"fill rate {manifest.fill_rate:.0%} | theme: {manifest.theme_name}")
    return 0


def cmd_themes(_args: argparse.Namespace) -> int:
    """List available themes."""
    from book_layout.themes import list_themes, get_theme

    themes = list_themes()
    print(f"{'NAME':<35} DESCRIPTION")
    print("-" * 70)
    for name in themes:
        t = get_theme(name)
        desc = t.description[:45] + "…" if len(t.description) > 45 else t.description
        print(f"{name:<35} {desc}")
    return 0


def cmd_templates(_args: argparse.Namespace) -> int:
    """List available page templates."""
    from book_layout.templates import list_templates, get_template

    templates = list_templates()
    print(f"{'NAME':<20} {'SLOTS':>6}  {'TEXT BLOCKS':>12}")
    print("-" * 45)
    for name in templates:
        t = get_template(name)
        print(f"{name:<20} {t.slot_count:>6}  {t.text_block_count:>12}")
    return 0


# ── helper ────────────────────────────────────────────────────────────────────

def _print_summary(book) -> None:
    print(
        f"\n── summary ──────────────────────\n"
        f"  title:    {book.title}\n"
        f"  format:   {book.book_format.value}\n"
        f"  chapters: {len(book.chapters)}\n"
        f"  pages:    {book.total_pages}\n"
        f"  slots:    {book.total_slots} total, {book.filled_slots} filled\n",
        file=sys.stderr,
    )


# ── argument parser ───────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m book_layout",
        description="Photo-book / yearbook / design-chapter layout engine.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # plan
    sp = sub.add_parser("plan", help="Plan a generic book from chapter item counts")
    sp.add_argument("--chapters", required=True,
                    help="Comma-separated item counts, e.g. '4,12,8'")
    sp.add_argument("--title", default="")
    sp.add_argument("--format", default="photo-book",
                    choices=["yearbook", "photo-book", "design-chapter"])
    sp.add_argument("--size", default="letter",
                    choices=["letter", "a4", "square", "spread"])
    sp.add_argument("--out", default="", help="Write JSON to this file")

    # album
    sp = sub.add_parser("album", help="Build a family photo album")
    sp.add_argument("--eras", required=True,
                    help="Comma-separated 'era-name:item-count', e.g. '2000s:12,2010s:18'")
    sp.add_argument("--title", default="")
    sp.add_argument("--no-cover", action="store_true")
    sp.add_argument("--out", default="")

    # year
    sp = sub.add_parser("year", help="Build a yearbook from instrument specs")
    sp.add_argument("--instruments", required=True,
                    help="Comma-separated 'repo-name:total-items', e.g. 'handpan:14,barrel-organ:10'")
    sp.add_argument("--title", default="")
    sp.add_argument("--edition", default="")
    sp.add_argument("--out", default="")

    # validate
    sp = sub.add_parser("validate", help="Validate a serialised Book JSON file")
    sp.add_argument("json_file")

    # export
    sp = sub.add_parser("export", help="Export a Book JSON file to a manifest")
    sp.add_argument("json_file")
    sp.add_argument("--manifest-out", default="", dest="manifest_out")

    # themes
    sub.add_parser("themes", help="List available design themes")

    # templates
    sub.add_parser("templates", help="List available page templates")

    return p


def main(argv: Optional[List[str]] = None) -> int:
    _import()
    parser = build_parser()
    args = parser.parse_args(argv)

    dispatch = {
        "plan": cmd_plan,
        "album": cmd_album,
        "year": cmd_year,
        "validate": cmd_validate,
        "export": cmd_export,
        "themes": cmd_themes,
        "templates": cmd_templates,
    }
    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
