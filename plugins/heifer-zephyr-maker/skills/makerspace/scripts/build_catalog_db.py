#!/usr/bin/env python3
"""
build_catalog_db.py
===================

Promote the YAML space profiles, project packets, and raw measurement
logs into a queryable SQLite database. The DB is a *read replica* —
edit the YAML / markdown sources; never edit the DB.

Usage:
    python3 scripts/build_catalog_db.py \\
        --spaces ./spaces/ \\
        --projects ./projects/ \\
        --output ./catalog.sqlite

    # Skip private profiles
    python3 scripts/build_catalog_db.py \\
        --spaces ./spaces/ \\
        --output ./catalog.sqlite \\
        --public-only

    # Use the included examples as projects too
    python3 scripts/build_catalog_db.py \\
        --spaces ./spaces/ \\
        --projects ./examples/ \\
        --output ./catalog.sqlite

Schema reference: references/catalog-database.md
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean, pstdev


def parse_yaml_simple(text: str) -> dict:
    """Tiny YAML reader for our flat profile shape.

    Avoids a PyYAML dependency. Handles:
      - top-level scalars (str, int, float, bool)
      - lists of scalars
      - lists of dicts (one level deep)
      - nested dicts (one level deep)

    Doesn't handle anchors, multi-line scalars, or arbitrary nesting.
    Profile.yaml stays inside this envelope.
    """
    # Try real PyYAML first; fall back to the mini-parser.
    try:
        import yaml  # type: ignore[import-not-found]
        return yaml.safe_load(text) or {}
    except ImportError:
        pass

    out: dict = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.split("#", 1)[0].rstrip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        # Top-level key: value
        if not line.startswith(" ") and ":" in line:
            key, _, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "":
                # multi-line: list or dict follows
                child_lines = []
                i += 1
                while i < len(lines) and (
                    lines[i].startswith(" ") or lines[i].strip() == ""
                ):
                    child_lines.append(lines[i])
                    i += 1
                out[key] = _parse_block(child_lines)
                continue
            out[key] = _coerce_scalar(value)
        i += 1
    return out


def _parse_block(lines: list[str]):
    """Parse a YAML block (indented). Returns list or dict."""
    # Strip empty lines at the end
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return None
    # Detect list (starts with `- `)
    first = next((l for l in lines if l.strip()), "")
    if first.lstrip().startswith("- "):
        return _parse_list(lines)
    return _parse_dict(lines)


def _parse_list(lines: list[str]) -> list:
    items: list = []
    current_lines: list[str] | None = None
    for line in lines:
        if not line.strip():
            continue
        stripped = line.lstrip()
        if stripped.startswith("- "):
            if current_lines is not None:
                items.append(_parse_dict(current_lines))
            rest = stripped[2:]
            if ":" in rest:
                indent = len(line) - len(stripped)
                # Convert "- key: value" to "  key: value" for sub-parser
                current_lines = [(" " * (indent + 2)) + rest]
            else:
                items.append(_coerce_scalar(rest))
                current_lines = None
        else:
            if current_lines is not None:
                current_lines.append(line)
    if current_lines is not None:
        items.append(_parse_dict(current_lines))
    return items


def _parse_dict(lines: list[str]) -> dict:
    out: dict = {}
    if not lines:
        return out
    base_indent = min(
        (len(l) - len(l.lstrip()) for l in lines if l.strip()),
        default=0,
    )
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if indent < base_indent:
            i += 1
            continue
        # Strip base indent
        key_line = line[base_indent:]
        if ":" in key_line:
            key, _, value = key_line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "":
                # Nested
                child_lines: list[str] = []
                i += 1
                while i < len(lines) and (
                    not lines[i].strip()
                    or (len(lines[i]) - len(lines[i].lstrip())) > base_indent
                ):
                    child_lines.append(lines[i])
                    i += 1
                out[key] = _parse_block(child_lines)
                continue
            out[key] = _coerce_scalar(value)
        i += 1
    return out


def _coerce_scalar(s: str):
    s = s.strip()
    if s == "" or s.lower() in {"null", "~"}:
        return None
    if s.lower() in {"true", "yes"}:
        return True
    if s.lower() in {"false", "no"}:
        return False
    if (s.startswith('"') and s.endswith('"')) or (
        s.startswith("'") and s.endswith("'")
    ):
        return s[1:-1]
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_coerce_scalar(p) for p in inner.split(",")]
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


# ─────────── Schema ───────────

SCHEMA = """
CREATE TABLE spaces (
    slug TEXT PRIMARY KEY,
    name TEXT,
    city TEXT, state TEXT, country TEXT,
    url TEXT,
    notebooklm_url TEXT,
    visibility TEXT,
    last_updated TEXT,
    last_updated_by TEXT
);
CREATE TABLE tools (
    id TEXT PRIMARY KEY,
    space_slug TEXT REFERENCES spaces(slug),
    name TEXT, category TEXT, location TEXT,
    cert_required TEXT,
    bed_x_in REAL, bed_y_in REAL, max_z_in REAL,
    power_w REAL, spindle_hp REAL,
    reservation TEXT
);
CREATE TABLE materials (
    id TEXT,
    space_slug TEXT REFERENCES spaces(slug),
    name TEXT, category TEXT,
    sheet_x_in REAL, sheet_y_in REAL, thickness_in REAL,
    typical_cost_usd REAL,
    available_in_shop INTEGER,
    PRIMARY KEY (id, space_slug)
);
CREATE TABLE tool_materials (
    tool_id TEXT REFERENCES tools(id),
    material_id TEXT,
    space_slug TEXT,
    allowed INTEGER
);
CREATE TABLE certifications (
    id TEXT,
    space_slug TEXT REFERENCES spaces(slug),
    name TEXT,
    granted_by_class TEXT,
    duration_hours REAL, cost_usd REAL,
    PRIMARY KEY (id, space_slug)
);
CREATE TABLE classes (
    id TEXT,
    space_slug TEXT REFERENCES spaces(slug),
    name TEXT,
    duration_hours REAL, cost_usd REAL,
    schedule_url TEXT,
    PRIMARY KEY (id, space_slug)
);
CREATE TABLE class_certs (
    class_id TEXT,
    cert_id TEXT,
    space_slug TEXT
);
CREATE TABLE projects (
    slug TEXT PRIMARY KEY,
    space_slug TEXT,
    name TEXT,
    tier INTEGER,
    path TEXT,
    status TEXT,
    created_at TEXT,
    shipped_at TEXT
);
CREATE TABLE project_tools (
    project_slug TEXT REFERENCES projects(slug),
    tool_id TEXT,
    op_count INTEGER
);
CREATE TABLE measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_slug TEXT,
    space_slug TEXT,
    check_id TEXT, check_name TEXT,
    target REAL, tolerance REAL, unit TEXT,
    measured REAL, delta REAL, in_tolerance INTEGER,
    measured_at TEXT, measured_by TEXT, notes TEXT,
    tool_id TEXT, material_id TEXT,
    op_kind TEXT, dimension_axis TEXT
);
CREATE TABLE corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    space_slug TEXT, tool_id TEXT, material_id TEXT,
    op_kind TEXT, dimension_axis TEXT,
    mean_delta REAL, stddev_delta REAL, sample_size INTEGER,
    last_recomputed_at TEXT
);
CREATE TABLE doe_studies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_slug TEXT,
    factor_a_name TEXT, factor_a_levels TEXT,
    factor_b_name TEXT, factor_b_levels TEXT,
    replicates INTEGER,
    response_variable TEXT,
    protocol_path TEXT, data_path TEXT,
    status TEXT
);
CREATE TABLE doe_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    study_id INTEGER REFERENCES doe_studies(id),
    factor_a_value TEXT, factor_b_value TEXT,
    replicate_index INTEGER,
    response_value REAL,
    notes TEXT,
    recorded_at TEXT
);
"""


# ─────────── Loaders ───────────

def load_space(profile_path: Path, public_only: bool) -> dict | None:
    text = profile_path.read_text()
    profile = parse_yaml_simple(text)
    if public_only and profile.get("visibility") == "private":
        return None
    return profile


def insert_space(conn: sqlite3.Connection, p: dict) -> None:
    loc = p.get("location", {}) or {}
    conn.execute(
        "INSERT OR REPLACE INTO spaces VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            p.get("slug"),
            p.get("name"),
            loc.get("city"),
            loc.get("state"),
            loc.get("country"),
            p.get("url"),
            p.get("notebooklm_url"),
            p.get("visibility", "public"),
            str(p.get("last_updated", "")),
            p.get("last_updated_by"),
        ),
    )

    for tool in p.get("tools") or []:
        if not isinstance(tool, dict):
            continue
        specs = tool.get("specs", {}) or {}
        bed = specs.get("bed_size_in") or [None, None]
        if not isinstance(bed, list) or len(bed) < 2:
            bed = [None, None]
        conn.execute(
            "INSERT OR REPLACE INTO tools VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                tool.get("id"),
                p.get("slug"),
                tool.get("name"),
                tool.get("category"),
                tool.get("location"),
                tool.get("cert_required"),
                _to_real(bed[0]),
                _to_real(bed[1]),
                _to_real(specs.get("max_z_in")),
                _to_real(specs.get("power_w")),
                _to_real(specs.get("spindle_hp")),
                tool.get("reservation"),
            ),
        )
        for m in tool.get("allowed_materials") or []:
            conn.execute(
                "INSERT INTO tool_materials VALUES (?,?,?,?)",
                (tool.get("id"), m, p.get("slug"), 1),
            )
        for m in tool.get("banned_materials") or []:
            conn.execute(
                "INSERT INTO tool_materials VALUES (?,?,?,?)",
                (tool.get("id"), m, p.get("slug"), 0),
            )

    for mat in p.get("materials") or []:
        if not isinstance(mat, dict):
            continue
        sz = mat.get("sheet_size_in") or [None, None]
        if not isinstance(sz, list) or len(sz) < 2:
            sz = [None, None]
        conn.execute(
            "INSERT OR REPLACE INTO materials VALUES (?,?,?,?,?,?,?,?,?)",
            (
                mat.get("id"),
                p.get("slug"),
                mat.get("name"),
                mat.get("category"),
                _to_real(sz[0]),
                _to_real(sz[1]),
                _to_real(mat.get("thickness_in")),
                _to_real(mat.get("typical_cost_usd")),
                1 if mat.get("available_in_shop") else 0,
            ),
        )

    for c in p.get("certifications") or []:
        if not isinstance(c, dict):
            continue
        conn.execute(
            "INSERT OR REPLACE INTO certifications VALUES (?,?,?,?,?,?)",
            (
                c.get("id"),
                p.get("slug"),
                c.get("name"),
                c.get("granted_by_class"),
                _to_real(c.get("duration_hours")),
                _to_real(c.get("cost_usd")),
            ),
        )

    for cls in p.get("classes") or []:
        if not isinstance(cls, dict):
            continue
        conn.execute(
            "INSERT OR REPLACE INTO classes VALUES (?,?,?,?,?,?)",
            (
                cls.get("id"),
                p.get("slug"),
                cls.get("name"),
                _to_real(cls.get("duration_hours")),
                _to_real(cls.get("cost_usd")),
                cls.get("schedule_url"),
            ),
        )
        for cert in cls.get("grants_certs") or []:
            conn.execute(
                "INSERT INTO class_certs VALUES (?,?,?)",
                (cls.get("id"), cert, p.get("slug")),
            )


def _to_real(x):
    if x is None or x == "" or (isinstance(x, str) and x.upper() == "TBD"):
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_project(packet_dir: Path) -> dict | None:
    design_md = packet_dir / "design.md"
    if not design_md.exists():
        return None
    name = packet_dir.name
    text = design_md.read_text(errors="ignore")
    # Title from first H1
    for line in text.splitlines():
        if line.startswith("# "):
            name = line[2:].strip().split("—")[0].strip()
            break
    return {"slug": packet_dir.name, "name": name, "path": str(packet_dir.resolve())}


def insert_project(
    conn: sqlite3.Connection,
    project: dict,
    tier: int,
    space_slug: str | None,
) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO projects VALUES (?,?,?,?,?,?,?,?)",
        (
            project["slug"],
            space_slug,
            project["name"],
            tier,
            project["path"],
            "in_progress",
            datetime.utcnow().isoformat(),
            None,
        ),
    )


def detect_tier(packet_dir: Path) -> int:
    if (packet_dir / "site" / "index.html").exists():
        return 3
    if (packet_dir / "README.md").exists():
        return 2
    return 1


def load_measurements(
    conn: sqlite3.Connection,
    space_slug: str,
    space_dir: Path,
) -> int:
    log = space_dir / "corrections" / "raw-measurements.jsonl"
    if not log.exists():
        return 0
    count = 0
    for line in log.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Derive project_slug from packet path
        packet = Path(event.get("packet", ""))
        project_slug = packet.name if packet.parts else None
        in_tol = event.get("in_tolerance")
        in_tol_int = 1 if in_tol == "yes" else 0 if in_tol == "no" else None
        conn.execute(
            "INSERT INTO measurements "
            "(project_slug, space_slug, check_id, check_name, target, "
            "tolerance, unit, measured, delta, in_tolerance, "
            "measured_at, measured_by, notes, "
            "tool_id, material_id, op_kind, dimension_axis) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                project_slug,
                space_slug,
                event.get("check_id"),
                event.get("check_name"),
                event.get("target"),
                event.get("tolerance"),
                event.get("unit"),
                event.get("measured"),
                event.get("delta"),
                in_tol_int,
                event.get("timestamp"),
                event.get("measured_by"),
                event.get("notes"),
                event.get("tool_id"),
                event.get("material_id"),
                event.get("op_kind"),
                event.get("dimension_axis"),
            ),
        )
        count += 1
    return count


def recompute_corrections(conn: sqlite3.Connection) -> int:
    """Roll up measurements into corrections."""
    rows = conn.execute(
        "SELECT space_slug, tool_id, material_id, op_kind, dimension_axis, "
        "delta FROM measurements "
        "WHERE delta IS NOT NULL"
    ).fetchall()
    grouped: dict[tuple, list[float]] = {}
    for r in rows:
        key = (r[0], r[1], r[2], r[3], r[4])
        grouped.setdefault(key, []).append(r[5])
    now = datetime.utcnow().isoformat()
    for key, deltas in grouped.items():
        if len(deltas) < 1:
            continue
        m = mean(deltas)
        sd = pstdev(deltas) if len(deltas) > 1 else 0.0
        conn.execute(
            "INSERT INTO corrections (space_slug, tool_id, material_id, "
            "op_kind, dimension_axis, mean_delta, stddev_delta, "
            "sample_size, last_recomputed_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (key[0], key[1], key[2], key[3], key[4],
             round(m, 6), round(sd, 6), len(deltas), now),
        )
    return len(grouped)


# ─────────── Main ───────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build the makerspace catalog SQLite db.",
    )
    p.add_argument(
        "--spaces", type=Path, default=Path("./spaces/"),
        help="Directory containing space profiles.",
    )
    p.add_argument(
        "--projects", type=Path, default=Path("./projects/"),
        help="Directory containing project packets.",
    )
    p.add_argument(
        "--output", type=Path, default=Path("./catalog.sqlite"),
        help="Output SQLite path.",
    )
    p.add_argument(
        "--public-only", action="store_true",
        help="Skip spaces with visibility: private.",
    )
    p.add_argument(
        "--include-corrections", action="store_true",
        help="Include the corrections table in the output (default: yes).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.output.exists():
        args.output.unlink()
    conn = sqlite3.connect(args.output)
    conn.executescript(SCHEMA)

    # Load spaces
    space_count = 0
    measurement_count = 0
    for profile_path in args.spaces.glob("*/profile.yaml"):
        try:
            profile = load_space(profile_path, args.public_only)
        except Exception as e:
            print(f"  ⚠ Failed to parse {profile_path}: {e}", file=sys.stderr)
            continue
        if profile is None:
            continue
        slug = profile.get("slug") or profile_path.parent.name
        profile["slug"] = slug
        insert_space(conn, profile)
        space_count += 1
        measurement_count += load_measurements(
            conn, slug, profile_path.parent
        )

    # Load projects (look for design.md)
    project_count = 0
    if args.projects.exists():
        for design_md in args.projects.glob("*/design.md"):
            packet_dir = design_md.parent
            project = load_project(packet_dir)
            if project is None:
                continue
            tier = detect_tier(packet_dir)
            # Derive space from notes in design.md (best effort)
            text = design_md.read_text(errors="ignore").lower()
            space_slug = None
            for slug_candidate in ("maker-nexus", "home-shop-default"):
                if slug_candidate in text:
                    space_slug = slug_candidate
                    break
            insert_project(conn, project, tier, space_slug)
            project_count += 1

    # Recompute corrections
    correction_count = recompute_corrections(conn)

    conn.commit()
    conn.close()

    print(f"Built {args.output}")
    print(f"  Spaces:       {space_count}")
    print(f"  Projects:     {project_count}")
    print(f"  Measurements: {measurement_count}")
    print(f"  Corrections:  {correction_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
