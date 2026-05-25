#!/usr/bin/env python3
"""
dream.py
========

The "dreaming" job — overnight context consolidation for the
makerspace skill. Designed to run as a scheduled background task
(via the `schedule` skill in Cowork, cron locally, or any task
runner). Idempotent: re-derives everything from the source-of-truth
sources every time, so a botched run never corrupts state.

What it does
------------

1. Rebuilds the catalog SQLite database from current YAML profiles +
   project packets + raw measurement logs.
2. Recomputes corrections (rolling deltas per tool/material/op).
3. Per shop, emits a `corrections/summary.md` with:
   - Top-N most material biases (mean delta, sample size, stddev)
   - New corrections that crossed sample-size thresholds since last run
   - Suggestions for which corrections are stable enough to apply
4. Per project, emits an updated `<packet>/dream-summary.md` that
   highlights what's been measured, what's still TBD, what changed.
5. Optionally writes a top-level `dream-log.md` aggregating across
   shops — handy as your morning briefing.

This is the makerspace skill's analog of overnight memory
consolidation: the raw events are sparse and immediate; the
consolidated rollups are the form the skill consults during a
working session.

Usage
-----

    # Default — consolidate everything found
    python3 scripts/dream.py

    # Limit to one shop
    python3 scripts/dream.py --space maker-nexus

    # Quiet — no top-level dream log, just per-shop summaries
    python3 scripts/dream.py --no-top-level

    # See what would change without writing anything
    python3 scripts/dream.py --dry-run

Scheduling
----------

In Cowork, point the `schedule` skill at this script. A nightly
3am run is the default contract. The job is idempotent and side-
effect-free if there's no new data, so a missed run isn't a problem.

Locally:

    # crontab
    0 3 * * * cd /path/to/makerspace && python3 scripts/dream.py
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, pstdev


SAMPLE_THRESHOLDS = (3, 5, 10, 20)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Overnight context consolidation for the makerspace skill.",
    )
    p.add_argument("--root", type=Path, default=Path("."),
                   help="Skill root (default: current dir).")
    p.add_argument("--space", default=None,
                   help="Limit consolidation to this slug.")
    p.add_argument("--no-top-level", action="store_true",
                   help="Skip writing the top-level dream-log.md.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print actions; don't write files.")
    p.add_argument("--catalog-output", type=Path, default=None,
                   help="Override catalog DB path (default: <root>/catalog.sqlite).")
    return p.parse_args(argv)


def call_catalog_builder(root: Path, output: Path, dry_run: bool) -> bool:
    builder = root / "scripts" / "build_catalog_db.py"
    if not builder.exists():
        print(f"⚠ build_catalog_db.py not found at {builder}", file=sys.stderr)
        return False
    cmd = [
        sys.executable, str(builder),
        "--spaces", str(root / "spaces"),
        "--projects", str(root / "examples"),  # examples count as projects
        "--output", str(output),
    ]
    if dry_run:
        print("DRY RUN: would run:", " ".join(cmd))
        return True
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠ catalog builder failed:\n{result.stderr}", file=sys.stderr)
        return False
    print(result.stdout.strip())
    return True


def load_corrections(catalog_path: Path) -> list[dict]:
    if not catalog_path.exists():
        return []
    conn = sqlite3.connect(catalog_path)
    rows = conn.execute(
        "SELECT space_slug, tool_id, material_id, op_kind, "
        "dimension_axis, mean_delta, stddev_delta, sample_size "
        "FROM corrections"
    ).fetchall()
    conn.close()
    return [
        {
            "space_slug": r[0], "tool_id": r[1], "material_id": r[2],
            "op_kind": r[3], "dimension_axis": r[4],
            "mean_delta": r[5], "stddev_delta": r[6],
            "sample_size": r[7],
        }
        for r in rows
    ]


def crossing_threshold(prev: int, curr: int) -> int | None:
    """Return the threshold value that was just crossed, if any."""
    for t in SAMPLE_THRESHOLDS:
        if prev < t <= curr:
            return t
    return None


def load_previous_sample_sizes(summary_path: Path) -> dict[tuple, int]:
    """Read a previous summary's "## Corrections" table to learn what
    sample sizes were last time. Best-effort; missing → 0."""
    if not summary_path.exists():
        return {}
    out: dict[tuple, int] = {}
    in_table = False
    for line in summary_path.read_text().splitlines():
        if line.startswith("| tool_id"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|") or set(line.strip("| ")) <= {"-", " "}:
                continue
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) < 6:
                continue
            try:
                key = (parts[0], parts[1], parts[2], parts[3])
                out[key] = int(parts[5])
            except (ValueError, IndexError):
                continue
    return out


def write_space_summary(
    space_dir: Path,
    space_slug: str,
    corrections: list[dict],
    *,
    dry_run: bool,
) -> Path:
    summary_path = space_dir / "corrections" / "summary.md"
    previous = load_previous_sample_sizes(summary_path)
    space_corr = [c for c in corrections if c["space_slug"] == space_slug]
    space_corr.sort(key=lambda c: abs(c["mean_delta"]), reverse=True)

    lines = []
    lines.append(f"# Dream summary — {space_slug}")
    lines.append(f"_Generated {datetime.utcnow().isoformat()}Z_")
    lines.append("")
    lines.append(f"Total corrections: {len(space_corr)}")
    lines.append("")

    # Newly-crossed thresholds
    crossed = []
    for c in space_corr:
        key = (c["tool_id"] or "", c["material_id"] or "",
               c["op_kind"] or "", c["dimension_axis"] or "")
        prev = previous.get(key, 0)
        threshold = crossing_threshold(prev, c["sample_size"])
        if threshold:
            crossed.append((threshold, c))

    if crossed:
        lines.append("## Newly stable (crossed a sample-size threshold)")
        lines.append("")
        for threshold, c in sorted(crossed, key=lambda x: -x[0]):
            lines.append(
                f"- **n={threshold}** crossed: "
                f"`{c['tool_id']}` × `{c['material_id']}` × `{c['op_kind']}` "
                f"× `{c['dimension_axis']}` "
                f"→ mean Δ {c['mean_delta']:+.4f} ± {c['stddev_delta']:.4f}"
            )
        lines.append("")

    # Top biases
    if space_corr:
        lines.append("## Top biases (by absolute mean delta)")
        lines.append("")
        lines.append("| tool_id | material_id | op_kind | dimension_axis "
                     "| mean_delta | sample_size | stddev |")
        lines.append("|---|---|---|---|---|---|---|")
        for c in space_corr[:20]:
            lines.append(
                f"| {c['tool_id'] or ''} | {c['material_id'] or ''} | "
                f"{c['op_kind'] or ''} | {c['dimension_axis'] or ''} | "
                f"{c['mean_delta']:+.4f} | {c['sample_size']} | "
                f"{c['stddev_delta']:.4f} |"
            )
        lines.append("")

    # Recommendations
    stable = [
        c for c in space_corr
        if c["sample_size"] >= 5 and c["stddev_delta"] < abs(c["mean_delta"])
    ]
    if stable:
        lines.append("## Recommended to apply")
        lines.append(
            "_Sample size ≥ 5 and stddev < |mean delta| — the bias is "
            "consistent enough to bias future packets._"
        )
        lines.append("")
        for c in stable[:10]:
            lines.append(
                f"- `{c['tool_id']}` × `{c['material_id']}` × "
                f"`{c['op_kind']}`: shift `{c['dimension_axis']}` by "
                f"`{-c['mean_delta']:+.4f}` to land on target."
            )
        lines.append("")

    if dry_run:
        print(f"DRY RUN: would write {summary_path} ({len(lines)} lines)")
    else:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text("\n".join(lines) + "\n")
    return summary_path


def write_top_level_log(
    root: Path,
    corrections: list[dict],
    *,
    dry_run: bool,
) -> Path | None:
    log_path = root / "dream-log.md"
    by_space = defaultdict(list)
    for c in corrections:
        by_space[c["space_slug"]].append(c)

    lines = [
        "# Dream log — morning briefing",
        f"_Generated {datetime.utcnow().isoformat()}Z_",
        "",
    ]
    if not corrections:
        lines.append("No corrections in the catalog yet. Build something, "
                     "measure it, and `record_measurement.py` will start "
                     "feeding this loop.")
    else:
        lines.append(f"**Total corrections across all spaces:** {len(corrections)}")
        lines.append("")
        for space_slug, cs in sorted(by_space.items()):
            lines.append(f"## {space_slug}")
            lines.append(f"- Corrections: {len(cs)}")
            biggest = sorted(cs, key=lambda c: abs(c["mean_delta"]), reverse=True)[:3]
            for c in biggest:
                lines.append(
                    f"- Top bias: `{c['tool_id'] or '?'}` × "
                    f"`{c['material_id'] or '?'}` × `{c['op_kind'] or '?'}` "
                    f"on `{c['dimension_axis'] or '?'}`: "
                    f"mean Δ {c['mean_delta']:+.4f} (n={c['sample_size']})"
                )
            lines.append("")

    if dry_run:
        print(f"DRY RUN: would write {log_path} ({len(lines)} lines)")
        return log_path
    log_path.write_text("\n".join(lines) + "\n")
    return log_path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    catalog_output = args.catalog_output or (root / "catalog.sqlite")

    print(f"Dreaming over {root} → {catalog_output}")

    # 1. Rebuild the catalog DB
    if not call_catalog_builder(root, catalog_output, args.dry_run):
        return 1

    # 2. Load corrections
    if args.dry_run and not catalog_output.exists():
        corrections = []
    else:
        corrections = load_corrections(catalog_output)
    print(f"  Loaded {len(corrections)} corrections")

    # 3. Per-shop summaries
    spaces_dir = root / "spaces"
    if spaces_dir.exists():
        for profile in spaces_dir.glob("*/profile.yaml"):
            slug = profile.parent.name
            if slug.startswith("_"):
                continue  # skip _template
            if args.space and slug != args.space:
                continue
            path = write_space_summary(
                profile.parent, slug, corrections, dry_run=args.dry_run,
            )
            print(f"  Wrote {path}")

    # 4. Top-level dream log
    if not args.no_top_level:
        log = write_top_level_log(root, corrections, dry_run=args.dry_run)
        if log:
            print(f"  Wrote {log}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
