#!/usr/bin/env python3
"""cli.py — Command-line interface for the bigthink capture KB.

Usage examples::

    python -m bigthink.cli add --id koops-law --thesis "..." --domain scaling_law
    python -m bigthink.cli list --domain scaling_law --maturity seed
    python -m bigthink.cli query "planetary element"
    python -m bigthink.cli show koops-law
    python -m bigthink.cli connect koops-law planetary-index --kind supports
    python -m bigthink.cli suggest koops-law
    python -m bigthink.cli validate koops-law
    python -m bigthink.cli promote koops-law
    python -m bigthink.cli dump registry.json
    python -m bigthink.cli load registry.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bigthink.connections import ConnectionFinder
from bigthink.maturity import MaturityModel
from bigthink.registry import CaptureRegistry, RegistryError
from bigthink.schema import (
    CaptureConnection,
    ConnectionKind,
    Domain,
    ManufacturingTheoryCapture,
    MaturityLevel,
)
from bigthink.validator import CaptureValidator


# ---------------------------------------------------------------------------
# Registry singleton (in-process; replaced by load for persistent state)
# ---------------------------------------------------------------------------

_REGISTRY = CaptureRegistry()
_MODEL    = MaturityModel()
_FINDER   = ConnectionFinder()
_VALIDATOR = CaptureValidator()

# Default persist path
_DEFAULT_PATH = Path("bigthink_registry.json")


def _load_registry(path: Path) -> CaptureRegistry:
    if path.exists():
        return CaptureRegistry.load(path)
    return CaptureRegistry()


def _save_registry(reg: CaptureRegistry, path: Path) -> None:
    reg.dump(path)


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------

def cmd_add(args: argparse.Namespace) -> None:
    reg = _load_registry(Path(args.registry))
    cap = ManufacturingTheoryCapture(
        id=args.id,
        thesis=args.thesis,
        domain=Domain(args.domain),
        evidence_refs=args.evidence_refs or [],
        maturity=MaturityLevel(args.maturity),
        source=args.source or "",
        tags=args.tags or [],
        promotion_target=args.promotion_target or "",
    )
    result = _VALIDATOR.validate_against(cap, reg)
    if not result.valid:
        print(str(result), file=sys.stderr)
        sys.exit(1)
    for w in result.warnings:
        print(f"WARN: {w}", file=sys.stderr)
    reg.add(cap)
    _save_registry(reg, Path(args.registry))
    print(f"Added capture {cap.id!r} (maturity={cap.maturity.value})")


def cmd_list(args: argparse.Namespace) -> None:
    reg = _load_registry(Path(args.registry))
    captures = reg.filter(
        domain=args.domain or None,
        maturity=args.maturity or None,
        tag=args.tag or None,
    )
    if not captures:
        print("No captures found.")
        return
    for cap in captures:
        conn_count = len(cap.connections)
        print(
            f"  {cap.id:40s}  {cap.domain.value:15s}  "
            f"{cap.maturity.value:12s}  "
            f"edges={conn_count}"
        )


def cmd_query(args: argparse.Namespace) -> None:
    reg = _load_registry(Path(args.registry))
    captures = reg.query(args.text)
    if not captures:
        print(f"No captures matching {args.text!r}")
        return
    print(f"{len(captures)} result(s):")
    for cap in captures:
        print(f"  [{cap.id}] {cap.thesis[:100]}…")


def cmd_show(args: argparse.Namespace) -> None:
    reg = _load_registry(Path(args.registry))
    try:
        cap = reg.get(args.id)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    print(json.dumps(cap.to_dict(), indent=2))
    ms = _MODEL.score(cap)
    print(f"\nMaturity score: {ms.score:.0%}  next={ms.next_level.value if ms.next_level else '—'}")
    if ms.gap:
        print("Gap: " + "; ".join(ms.gap))


def cmd_connect(args: argparse.Namespace) -> None:
    reg = _load_registry(Path(args.registry))
    try:
        conn = reg.connect(
            args.from_id, args.to_id,
            ConnectionKind(args.kind),
            note=args.note or "",
            bidirectional=args.bidirectional,
        )
    except (RegistryError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    _save_registry(reg, Path(args.registry))
    print(f"Connected {conn.from_id!r} → {conn.to_id!r} ({conn.kind.value})")


def cmd_suggest(args: argparse.Namespace) -> None:
    reg = _load_registry(Path(args.registry))
    suggestions = _FINDER.suggest_for(args.id, reg, top_k=args.top_k)
    if not suggestions:
        print("No suggestions found.")
        return
    print(f"{len(suggestions)} suggestion(s) for {args.id!r}:")
    for s in suggestions:
        print(f"  {s.score:.0%}  {s.from_id} → {s.to_id}  [{s.kind.value}]  {', '.join(s.reasons)}")


def cmd_suggest_all(args: argparse.Namespace) -> None:
    reg = _load_registry(Path(args.registry))
    suggestions = _FINDER.suggest_all_pairs(reg, top_k=args.top_k)
    if not suggestions:
        print("No suggestions found.")
        return
    print(f"{len(suggestions)} cross-registry suggestion(s):")
    for s in suggestions:
        print(f"  {s.score:.0%}  {s.from_id} → {s.to_id}  [{s.kind.value}]  {', '.join(s.reasons)}")


def cmd_validate(args: argparse.Namespace) -> None:
    reg = _load_registry(Path(args.registry))
    if args.id:
        try:
            cap = reg.get(args.id)
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)
        result = _VALIDATOR.validate(cap)
        print(str(result))
        sys.exit(0 if result.valid else 1)
    else:
        results = _VALIDATOR.validate_registry(reg)
        any_invalid = False
        for r in results:
            print(str(r))
            if not r.valid:
                any_invalid = True
        sys.exit(1 if any_invalid else 0)


def cmd_promote(args: argparse.Namespace) -> None:
    reg = _load_registry(Path(args.registry))
    try:
        cap = reg.get(args.id)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    try:
        advanced = _MODEL.advance(cap)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    # Replace in registry
    reg.remove(cap.id)
    reg.add(advanced)
    _save_registry(reg, Path(args.registry))
    print(f"Promoted {cap.id!r}: {cap.maturity.value} → {advanced.maturity.value}")


def cmd_dump(args: argparse.Namespace) -> None:
    reg = _load_registry(Path(args.registry))
    _save_registry(reg, Path(args.output))
    print(f"Registry saved to {args.output} ({len(reg)} captures)")


def cmd_load(args: argparse.Namespace) -> None:
    reg = CaptureRegistry.load(Path(args.input))
    _save_registry(reg, Path(args.registry))
    print(f"Loaded {len(reg)} captures from {args.input} → {args.registry}")


def cmd_summary(args: argparse.Namespace) -> None:
    reg = _load_registry(Path(args.registry))
    print(reg.summary())
    by_maturity: dict[str, int] = {}
    for cap in reg:
        by_maturity[cap.maturity.value] = by_maturity.get(cap.maturity.value, 0) + 1
    for level, count in sorted(by_maturity.items()):
        print(f"  {level:12s} {count}")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bigthink",
        description="Manufacturing theory capture KB engine",
    )
    p.add_argument(
        "--registry", default=str(_DEFAULT_PATH),
        help="Path to the JSON registry file (default: bigthink_registry.json)"
    )
    sub = p.add_subparsers(dest="command", required=True)

    # add
    a = sub.add_parser("add", help="Add a new capture")
    a.add_argument("--id",        required=True)
    a.add_argument("--thesis",    required=True)
    a.add_argument("--domain",    required=True, choices=[d.value for d in Domain])
    a.add_argument("--evidence-refs", nargs="*", dest="evidence_refs")
    a.add_argument("--maturity",  default="seed", choices=[m.value for m in MaturityLevel])
    a.add_argument("--source",    default="")
    a.add_argument("--tags",      nargs="*")
    a.add_argument("--promotion-target", dest="promotion_target", default="")

    # list
    ls = sub.add_parser("list", help="List captures with optional filters")
    ls.add_argument("--domain",   choices=[d.value for d in Domain])
    ls.add_argument("--maturity", choices=[m.value for m in MaturityLevel])
    ls.add_argument("--tag")

    # query
    q = sub.add_parser("query", help="Full-text search across thesis and tags")
    q.add_argument("text")

    # show
    sh = sub.add_parser("show", help="Show full JSON for one capture")
    sh.add_argument("id")

    # connect
    c = sub.add_parser("connect", help="Add a typed edge between two captures")
    c.add_argument("from_id")
    c.add_argument("to_id")
    c.add_argument("--kind", required=True, choices=[k.value for k in ConnectionKind])
    c.add_argument("--note", default="")
    c.add_argument("--bidirectional", action="store_true")

    # suggest
    sg = sub.add_parser("suggest", help="Suggest connections for one capture")
    sg.add_argument("id")
    sg.add_argument("--top-k", type=int, default=10, dest="top_k")

    # suggest-all
    sga = sub.add_parser("suggest-all", help="Suggest top connections across whole registry")
    sga.add_argument("--top-k", type=int, default=20, dest="top_k")

    # validate
    v = sub.add_parser("validate", help="Validate one or all captures")
    v.add_argument("id", nargs="?", help="Capture id (omit to validate all)")

    # promote
    pr = sub.add_parser("promote", help="Advance capture maturity one level")
    pr.add_argument("id")

    # dump
    d = sub.add_parser("dump", help="Save registry to a JSON file")
    d.add_argument("output")

    # load
    lo = sub.add_parser("load", help="Load registry from a JSON file")
    lo.add_argument("input")

    # summary
    sub.add_parser("summary", help="Print registry summary statistics")

    return p


COMMAND_MAP = {
    "add":         cmd_add,
    "list":        cmd_list,
    "query":       cmd_query,
    "show":        cmd_show,
    "connect":     cmd_connect,
    "suggest":     cmd_suggest,
    "suggest-all": cmd_suggest_all,
    "validate":    cmd_validate,
    "promote":     cmd_promote,
    "dump":        cmd_dump,
    "load":        cmd_load,
    "summary":     cmd_summary,
}


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = COMMAND_MAP.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)
    handler(args)


if __name__ == "__main__":
    main()
