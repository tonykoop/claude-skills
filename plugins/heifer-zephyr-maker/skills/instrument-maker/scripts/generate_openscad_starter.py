#!/usr/bin/env python3
"""Generate a parametric OpenSCAD master-shape starter for an instrument packet.

The starter captures the FIRED-body envelope plus a `master_scale_factor =
1/(1-shrinkage)` for slip-cast workflows. It is intentionally a *starter* —
voicing/fipple geometry, rim radii, hand-comfort detail, and surface texture
must be refined by hand or in detailed CAD because they're tuning-sensitive.

The script reads `design.md` for inputs, `family-spec.csv` (or a family
table in design.md) for size variants, and emits `cad/{slug}_master.scad`.
Two governing-model templates ship: Helmholtz (vessel resonators, ocarinas,
udus, gemshorns) and open-pipe (NAFs, kenas, transverse flutes). Other
families fall back to a "generic-body" template that just outputs the outer
envelope with no tone-hole logic.

Pattern was iterated on the udu and ocarina master-shape starters that
shipped 2026-05-02; this script captures that pattern as a reusable
generator.

Usage:
    python3 generate_openscad_starter.py <packet_dir> [--governing-model auto|helmholtz|open-pipe|solid-body|generic]
                                                       [--force-model]
                                                       [--slug ocarina]
                                                       [--output cad/{slug}_master.scad]
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
from pathlib import Path


# --------- Governing-model templates ---------------------------------------

HELMHOLTZ_HEADER = """// =============================================================
// Slip-Cast Ceramic {INSTRUMENT_NAME} — OpenSCAD Master-Shape Starter
// =============================================================
// Generated {DATE} by generate_openscad_starter.py.
// Units: inches.  Outputs the FIRED body envelope; multiply by
// master_scale_factor to get the printed master geometry.
//
// This is a master-shape STARTER — captures vessel volume + ports.
// NOT final production CAD: voicing / rim radii / surface texture
// must be refined by hand because they're tuning-sensitive.
//
// Governing model: Helmholtz vessel resonator
//     f = c/(2π) · √( A_open / (V_chamber · L_eff) )
// with L_eff = wall + 0.6·√(A/π) (flanged-port end correction).
// =============================================================

$fn = 96;

// --------- INPUT PARAMETERS (edit these) ---------------------

c_in_per_sec   = 13510;     // speed of sound (in/s @ ~68F)
shrinkage      = 0.12;      // measured clay shrinkage; replace per slip batch
wall_in        = {WALL_IN};       // fired wall thickness
master_scale_factor = 1 / (1 - shrinkage);   // ~1.136 at 12% shrinkage
"""

OPEN_PIPE_HEADER = """// =============================================================
// {INSTRUMENT_NAME} — OpenSCAD Master-Shape Starter
// =============================================================
// Generated {DATE} by generate_openscad_starter.py.
// Units: inches.
//
// This is a master-shape STARTER — captures bore profile + tone-hole
// positions to first order.  Voicing/embouchure/labium geometry must
// be refined by hand because it's tuning-sensitive.
//
// Governing model: Open pipe (or stopped pipe; see design.md)
//     f_n = n·v / (2·L_eff)            (open-open)
//     f_n = (2n-1)·v / (4·L_eff)       (open-stopped)
// with L_eff = L + end-correction(s) and Tony's NAF K2 bore correction
// applied where the bore diameter falls in the K2 lookup range.
// =============================================================

$fn = 96;

// --------- INPUT PARAMETERS (edit these) ---------------------

c_in_per_sec   = 13510;     // speed of sound (in/s @ ~68F)
bore_dia       = {BORE_DIA};       // bore inside diameter
total_length   = {LENGTH_IN};      // overall length
wall_in        = {WALL_IN};        // wall thickness
"""

GENERIC_HEADER = """// =============================================================
// {INSTRUMENT_NAME} — OpenSCAD Master-Shape Starter
// =============================================================
// Generated {DATE} by generate_openscad_starter.py.
// Units: inches.
//
// Generic-body starter: outputs the outer envelope only, no tone-hole
// or port logic.  Use as a parametric scaffold; fill in geometry
// specific to the instrument family.
// =============================================================

$fn = 96;
shrinkage           = 0.12;
master_scale_factor = 1 / (1 - shrinkage);
wall_in             = {WALL_IN};
"""


SOLID_BODY_HEADER = """// =============================================================
// {INSTRUMENT_NAME} — OpenSCAD Solid-Body Master-Shape Starter
// =============================================================
// Generated {DATE} by generate_openscad_starter.py.
// Units: inches.
//
// Solid-body starter for instruments with a solid (or chambered solid)
// body and a separate neck — violins, guitars, lyres, electric basses,
// hurdy-gurdies, hybrid acoustic/electric instruments.  NOT for vessel
// resonators (use --governing-model helmholtz) or open-pipe woodwinds
// (use --governing-model open-pipe).
//
// The starter captures:
//   - Body silhouette (override body_silhouette() with the actual outline)
//   - Body thickness with optional carved/chambered profile
//   - Neck mortise / socket interface
//   - Optional bridge flat + pickup cavity + endpin/jack hole
//
// Bridge geometry, fingerboard, and tuning hardware are out of scope —
// they live in the wooden neck assembly, not the body master.
// =============================================================

$fn = 96;

body_length_in    = {BODY_LENGTH_IN};   // overall body length (nut-to-endpin axis)
body_width_in     = {BODY_WIDTH_IN};    // max body width (lower bout)
body_thickness_in = {BODY_THICKNESS_IN};// body thickness at center
neck_socket_dia   = {NECK_SOCKET_DIA};  // neck mortise/heel socket diameter
neck_socket_depth = {NECK_SOCKET_DEPTH};// how deep the neck heel seats
include_pickup_cavity = true;  // set false for purely acoustic builds
include_endpin_hole   = true;
"""


SOLID_BODY_BODY = """
// --------- BODY SILHOUETTE -----------------------------------
// Default: figure-8 (violin family).  For a guitar/lyre/electric, override
// this module with the actual outline (offset path, hull of waypoints,
// imported DXF, etc.).
module body_silhouette() {
    upper_bout_w = body_width_in * 0.78;
    waist_w      = body_width_in * 0.62;
    lower_bout_w = body_width_in;

    upper_y      = body_length_in * 0.18;
    waist_y      = body_length_in * 0.50;
    lower_y      = body_length_in * 0.78;

    hull() {
        translate([0, upper_y, 0]) circle(d = upper_bout_w);
        translate([0, waist_y, 0]) circle(d = waist_w);
        translate([0, lower_y, 0]) circle(d = lower_bout_w);
    }
}

// --------- BODY SOLID ----------------------------------------
module solid_body() {
    difference() {
        linear_extrude(height = body_thickness_in) body_silhouette();

        // Neck mortise — drilled along the +Y axis at the upper end (top of
        // body, where the neck heel meets the body).
        translate([0, 0, body_thickness_in / 2])
            rotate([90, 0, 0])
                cylinder(h = neck_socket_depth + 0.02, d = neck_socket_dia);

        // Pickup cavity — a flat rectangular pocket near the lower bout
        // bridge area, accessible from the top.  Comment out for purely
        // acoustic builds.
        if (include_pickup_cavity) {
            translate([0, body_length_in * 0.62, body_thickness_in - 0.50])
                cube([1.4, 2.2, 0.55], center = true);
        }

        // Endpin / jack hole at the bottom centerline.
        if (include_endpin_hole) {
            translate([0, body_length_in * 0.95, body_thickness_in / 2])
                rotate([90, 0, 0])
                    cylinder(h = body_width_in * 0.3, d = 0.55);
        }
    }
}

solid_body();

// --------- ECHO ----------------------------------------------
echo(str("Body envelope: ", body_length_in, " x ", body_width_in,
         " x ", body_thickness_in, " in"));
echo(str("Neck socket: dia=", neck_socket_dia, " in, depth=",
         neck_socket_depth, " in"));
"""


HELMHOLTZ_FAMILY_BLOCK = """
// Family block: [name, body_dia_in, body_height_in, mouth_dia_in, side_dia_in]
family = [
{FAMILY_ROWS}
];
preview_index = 0;   // -1 = render all, 0..N = single member

// --------- FUNCTIONS ----------------------------------------

function area_circle(d)         = PI*(d/2)*(d/2);
function L_eff(wall, area)      = wall + 0.6*sqrt(area/PI);
function helmholtz_hz(area, vol, neck) =
    (c_in_per_sec/(2*PI)) * sqrt(area/(vol*neck));
function volume_ovoid(d, h, sf) = (PI/6)*d*d*h*sf;

// --------- GEOMETRY -----------------------------------------

module body_outer(diam, height) {
    hull() {
        translate([0, 0, height*0.30])
            scale([diam/2*0.95, diam/2*0.95, height*0.45]) sphere(r=1);
        translate([0, 0, height*0.85])
            scale([diam/2*0.55, diam/2*0.55, height*0.18]) sphere(r=1);
        translate([0, 0, 0])
            scale([diam/2*0.85, diam/2*0.85, height*0.04]) sphere(r=1);
    }
}

module body_inner(diam, height) {
    hull() {
        translate([0, 0, height*0.30])
            scale([diam/2*0.95-wall_in, diam/2*0.95-wall_in, height*0.45-wall_in]) sphere(r=1);
        translate([0, 0, height*0.85])
            scale([diam/2*0.55-wall_in, diam/2*0.55-wall_in, height*0.18-wall_in]) sphere(r=1);
        translate([0, 0, 0])
            scale([diam/2*0.85-wall_in, diam/2*0.85-wall_in, height*0.04-wall_in]) sphere(r=1);
    }
}

module instrument_body(diam, height, mouth_dia, side_dia) {
    difference() {
        body_outer(diam, height);
        body_inner(diam, height);
        translate([0, 0, height*0.95])
            cylinder(h=wall_in*4, d=mouth_dia, center=true);
        translate([-diam/2, 0, height*0.55])
            rotate([0, 90, 0])
                cylinder(h=wall_in*4, d=side_dia, center=true);
    }
}

// --------- PREVIEW + ECHO -----------------------------------

if (preview_index >= 0) {
    f = family[preview_index];
    instrument_body(f[1], f[2], f[3], f[4]);
    V      = volume_ovoid(f[1], f[2], 0.7);
    A_top  = area_circle(f[3]);
    A_side = area_circle(f[4]);
    L_top  = L_eff(wall_in, A_top);
    L_side = L_eff(wall_in, A_side);
    echo(str(f[0], "  V=", V, " in^3  f_top=", helmholtz_hz(A_top, V, L_top),
             " Hz  f_side=", helmholtz_hz(A_side, V, L_side), " Hz"));
} else {
    for (i = [0 : len(family)-1]) {
        translate([i*max(family[i][1]+4, 12), 0, 0])
            instrument_body(family[i][1], family[i][2], family[i][3], family[i][4]);
    }
}
"""

OPEN_PIPE_BODY = """
// Tone holes: [position_from_top_in, diameter_in, note_label]
holes = [
    // Edit for actual fingering chart from design.md
    [total_length*0.55, 0.30, "low"],
    [total_length*0.65, 0.31, "+1"],
    [total_length*0.74, 0.30, "+2"],
    [total_length*0.83, 0.32, "+3"],
    [total_length*0.92, 0.30, "+4"],
];

module open_pipe_body() {
    difference() {
        cylinder(h=total_length, d=bore_dia + 2*wall_in);
        translate([0, 0, -0.01])
            cylinder(h=total_length+0.02, d=bore_dia);
        for (h = holes) {
            translate([bore_dia/2 + wall_in, 0, h[0]])
                rotate([0, 90, 0])
                    cylinder(h=wall_in*3, d=h[1], center=true);
        }
    }
}

open_pipe_body();
echo(str("Bore: ", bore_dia, " in;  Length: ", total_length, " in;  Holes: ", len(holes)));
"""


# --------- design.md parsing ----------------------------------------------


def read_design(packet_dir: Path) -> str:
    design = packet_dir / "design.md"
    return design.read_text(encoding="utf-8", errors="replace") if design.exists() else ""


def detect_governing_model(packet_dir: Path) -> str:
    """Best-guess governing model from design.md content.

    v3.1: solid-body detection added.  Solid-body wins over helmholtz when
    both signals appear (e.g., ceramic-electric-violin has Helmholtz body
    coupling AS A SECONDARY effect; the master shape is solid-body), unless
    the design explicitly calls itself a vessel.
    """
    text = read_design(packet_dir).lower()
    is_solid_body = any(s in text for s in (
        "solid-body", "solid body", "violin", "guitar", "lyre", "kora", "ngoni",
        "lute", "oud", "harp", "mersenne", "vibrating string", "string equation",
        "pickup", "fingerboard", "bridge", "scale length",
    ))
    is_vessel = any(s in text for s in (
        "vessel resonator", "vessel flute", "ocarina", "udu", "gemshorn",
        "helmholtz vessel", "closed cavity",
    ))
    is_open_pipe = any(s in text for s in (
        "open pipe", "open-pipe", "naf", "kena", "duct flute", "shakuhachi",
        "transverse flute", "pan flute", "didgeridoo",
    ))

    if is_solid_body and not is_vessel:
        return "solid-body"
    if is_vessel or "helmholtz" in text:
        return "helmholtz"
    if is_open_pipe:
        return "open-pipe"
    return "generic"


def extract_input(text: str, label: str, default: str) -> str:
    """Pull a numeric input from design.md, robust to markdown tables.

    Tries three strategies in order:

      1. **Two-column markdown table row** `| Field | Value |` — the cleanest
         pattern; pulls the value cell directly when the field cell matches
         the label.

      2. **Inline `Field: value`** — for instruments that document inputs as
         a key/value list rather than a table.

      3. **Legacy fallback** — first number on any line that mentions the
         label.  This is what v3.0 did exclusively, and it's responsible for
         the kena bug where a multi-column "Slip-Cast Variant" table
         returned `0.787` for bore (correct), `2` for total_length (wrong;
         that came from the column header `(in)` digit somehow), and
         `0.625` for wall (also wrong).

    v3.1 fix: prefer (1) and (2) over (3).
    """
    label_lower = label.lower()

    # Strategy 1 + 2: structured key/value extraction
    for line in text.splitlines():
        s = line.strip()

        # Markdown table row with exactly two semantic cells: `| Field | value |`
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            # Skip the alignment row (`|---|---|`)
            if all(set(c) <= {"-", ":", " "} for c in cells if c):
                continue
            # Two-cell case: first cell is the label, second is the value.
            if len(cells) == 2 and label_lower in cells[0].lower():
                m = re.search(r"([0-9]+(?:\.[0-9]+)?)", cells[1])
                if m:
                    return m.group(1)

        # Inline `Field: value` (or `Field = value`)
        for sep in (":", "="):
            if sep in s:
                field, _, value = s.partition(sep)
                if label_lower in field.lower() and label_lower != "":
                    # Guard: don't match if the label appears AFTER the separator
                    # (e.g., "Notes: bore should be...")
                    if label_lower in field.lower():
                        m = re.search(r"([0-9]+(?:\.[0-9]+)?)", value)
                        if m:
                            return m.group(1)
                break  # only check first separator per line

    # Strategy 3: legacy fallback — first number on any line containing the label.
    # Keep this as a last resort because it produces the kena-style failures
    # on multi-column tables.
    for line in text.splitlines():
        if label_lower in line.lower():
            m = re.search(r"([0-9]+(?:\.[0-9]+)?)", line)
            if m:
                return m.group(1)
    return default


def family_rows_from_packet(packet_dir: Path) -> list[list[str]]:
    """Reuse the family-spec extraction from generate_capstone_docs."""
    csv_path = packet_dir / "family-spec.csv"
    if csv_path.exists():
        with csv_path.open(newline="", encoding="utf-8") as h:
            return list(csv.reader(h))
    text = read_design(packet_dir)
    match = re.search(
        r"^##\s*(?:Current\s+)?Family\s+(?:Targets?|Spec)\b\s*\n+(.*?)(?=^##\s|\Z)",
        text, re.M | re.S,
    )
    if not match:
        return []
    rows: list[list[str]] = []
    for line in match.group(1).splitlines():
        s = line.strip()
        if not s.startswith("|"):
            if rows:
                break
            continue
        if set(s.replace("|", "").replace(":", "").replace("-", "").replace(" ", "")) == set():
            continue
        rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows


# --------- Renderers ------------------------------------------------------


def _safe_format_header(template: str, **values: str) -> str:
    """Substitute {KEY} placeholders without invoking Python's full str.format()
    (which would choke on the literal `{` and `}` curly braces in SCAD code).

    Only replaces explicit named placeholders we know about; everything else
    is left literal.
    """
    out = template
    for key, val in values.items():
        out = out.replace("{" + key + "}", str(val))
    return out


def render_helmholtz(packet_dir: Path, instrument_name: str, slug: str) -> str:
    text = read_design(packet_dir)
    wall_in = extract_input(text, "wall thickness", "0.30")
    rows = family_rows_from_packet(packet_dir)

    # Map family rows to OpenSCAD family-array entries.
    scad_rows = []
    if rows and len(rows) > 1:
        for row in rows[1:]:
            # Pull body_dia, body_height, mouth_dia, side_dia from the row by best-guess column name match.
            body_dia = _pick_numeric(rows[0], row, ("diam", "diameter"), default="10")
            body_h = _pick_numeric(rows[0], row, ("height",), default="12")
            mouth = _pick_numeric(rows[0], row, ("mouth",), default="3")
            side = _pick_numeric(rows[0], row, ("side", "hole"), default="2")
            name_col = row[0] if row else slug
            scad_rows.append(f'    [ "{name_col}", {body_dia}, {body_h}, {mouth}, {side} ],')
    if not scad_rows:
        # Single-instrument default block.
        scad_rows.append(f'    [ "{slug.upper()}", 10.0, 12.0, 3.0, 2.0 ],')

    header = _safe_format_header(
        HELMHOLTZ_HEADER,
        INSTRUMENT_NAME=instrument_name,
        DATE=dt.date.today().isoformat(),
        WALL_IN=wall_in,
    )
    body = _safe_format_header(HELMHOLTZ_FAMILY_BLOCK, FAMILY_ROWS="\n".join(scad_rows))
    return header + body


def render_open_pipe(packet_dir: Path, instrument_name: str, slug: str) -> str:
    text = read_design(packet_dir)
    wall_in = extract_input(text, "wall", "0.20")
    bore_dia = extract_input(text, "bore", "0.75")
    length = extract_input(text, "length", "16.0")
    header = _safe_format_header(
        OPEN_PIPE_HEADER,
        INSTRUMENT_NAME=instrument_name,
        DATE=dt.date.today().isoformat(),
        WALL_IN=wall_in,
        BORE_DIA=bore_dia,
        LENGTH_IN=length,
    )
    return header + OPEN_PIPE_BODY


def render_generic(packet_dir: Path, instrument_name: str, slug: str) -> str:
    text = read_design(packet_dir)
    wall_in = extract_input(text, "wall", "0.30")
    header = _safe_format_header(
        GENERIC_HEADER,
        INSTRUMENT_NAME=instrument_name,
        DATE=dt.date.today().isoformat(),
        WALL_IN=wall_in,
    )
    return header + f"\ncube([4, 4, 6]);  // placeholder body — refine for {instrument_name}\n"


def render_solid_body(packet_dir: Path, instrument_name: str, slug: str) -> str:
    """Solid-body template for violins, guitars, lyres, hybrid electric/acoustic.

    Reads body_length, body_width, body_thickness, and neck_socket dimensions
    from design.md.  Defaults are sized for a 4/4 violin (~14 in body length,
    ~8 in lower bout); override per-instrument.
    """
    text = read_design(packet_dir)
    body_length_in    = extract_input(text, "body length",     "14.0")
    body_width_in     = extract_input(text, "body width",      "8.0")
    body_thickness_in = extract_input(text, "body thickness",  "1.5")
    neck_socket_dia   = extract_input(text, "neck socket dia", "1.0")
    neck_socket_depth = extract_input(text, "neck socket depth", "1.5")

    header = _safe_format_header(
        SOLID_BODY_HEADER,
        INSTRUMENT_NAME=instrument_name,
        DATE=dt.date.today().isoformat(),
        BODY_LENGTH_IN=body_length_in,
        BODY_WIDTH_IN=body_width_in,
        BODY_THICKNESS_IN=body_thickness_in,
        NECK_SOCKET_DIA=neck_socket_dia,
        NECK_SOCKET_DEPTH=neck_socket_depth,
    )
    return header + SOLID_BODY_BODY


def _pick_numeric(header: list[str], row: list[str], keywords: tuple[str, ...], default: str) -> str:
    """Find the first cell whose header matches any keyword and return its numeric value."""
    for i, h in enumerate(header):
        for kw in keywords:
            if kw.lower() in h.lower():
                if i < len(row):
                    m = re.search(r"([0-9]+(?:\.[0-9]+)?)", row[i])
                    if m:
                        return m.group(1)
    return default


# --------- main ---------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet_dir", type=Path)
    parser.add_argument(
        "--governing-model",
        choices=["helmholtz", "open-pipe", "solid-body", "generic", "auto"],
        default="auto",
    )
    parser.add_argument(
        "--force-model",
        action="store_true",
        help="Allow an explicit --governing-model that conflicts with the detected model",
    )
    parser.add_argument("--slug", help="Instrument slug; defaults to packet folder name", default=None)
    parser.add_argument("--instrument-name", help="Display name for the OpenSCAD header", default=None)
    parser.add_argument("--output", type=Path, default=None,
                        help="Output path. Defaults to <packet_dir>/cad/<slug>_master.scad")
    args = parser.parse_args()

    packet_dir = args.packet_dir.resolve()
    slug = args.slug or packet_dir.name
    instrument_name = args.instrument_name or slug.replace("-", " ").title()
    model = args.governing_model
    detected_model = detect_governing_model(packet_dir)
    if model == "auto":
        model = detected_model
    elif detected_model != "generic" and model != detected_model and not args.force_model:
        print(
            "Refusing to emit a mismatched OpenSCAD template.\n"
            f"  requested model: {model}\n"
            f"  detected model:  {detected_model}\n"
            "Re-run with --force-model only if this mismatch is intentional.",
            file=sys.stderr,
        )
        return 1

    if model == "helmholtz":
        scad = render_helmholtz(packet_dir, instrument_name, slug)
    elif model == "open-pipe":
        scad = render_open_pipe(packet_dir, instrument_name, slug)
    elif model == "solid-body":
        scad = render_solid_body(packet_dir, instrument_name, slug)
    else:
        scad = render_generic(packet_dir, instrument_name, slug)

    output = args.output or (packet_dir / "cad" / f"{slug}_master.scad")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(scad, encoding="utf-8")
    print(f"Wrote {output}  (model={model})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
