#!/usr/bin/env python3
"""
generate_drawings.py — emit DXF-first fabrication geometry plus previews.

Brainstorm Tier 1 #1: today drawing-brief.md describes the drawing the user
should make and cad/ is empty. v4 emits an opinionated "good enough for shop
floor" SVG with title block, datums, critical dimensions, and a section view.

Reads:
    - <packet>/family-spec.csv (family-aware) or design.md family table
    - <packet>/design.md governing model section (for the section view shape)

Writes:
    - <packet>/drawings/<member-id>-body.dxf (fabrication-facing authority)
    - <packet>/drawings/<member-id>-body.svg (derived preview)
    - <packet>/drawings/<member-id>-body.pdf (derived preview)
    - <packet>/drawings/family-overview.svg (combined family scale chart)
    - <packet>/visual-output-contract.json (visual artifact contract)

Usage:
    python3 scripts/generate_drawings.py ./build-packets/<slug>
    python3 scripts/generate_drawings.py ./build-packets/<slug> --dry-run
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from datetime import date


def read_family_spec(packet: Path):
    fs = packet / "family-spec.csv"
    if not fs.exists():
        return None
    with fs.open() as f:
        reader = csv.DictReader(f)
        return list(reader)


def read_design_md(packet: Path):
    md = packet / "design.md"
    if not md.exists():
        return ""
    return md.read_text()


def detect_governing_model(design_text: str) -> str:
    text = design_text.lower()
    if "helmholtz" in text:
        return "helmholtz"
    if "open-pipe" in text or "open pipe" in text:
        return "open-pipe"
    if "stopped pipe" in text or "stopped-pipe" in text:
        return "stopped-pipe"
    if "free-free beam" in text or "free free beam" in text:
        return "free-free-beam"
    if "cantilever" in text:
        return "cantilever"
    if "mersenne" in text or "string" in text:
        return "string"
    return "generic"


DXF_REQUIRED_LAYERS = [
    "OUTLINE",
    "CENTERLINE_REF",
    "SCALE_REF",
    "BRIDGE",
    "STRING_PATH",
    "NOTES_NO_CUT",
]


# --- SVG primitives ---------------------------------------------------------

def svg_doc(width, height, body):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" '
            f'font-family="Helvetica, Arial, sans-serif">\n'
            f'{body}\n</svg>\n')


def pdf_escape(text):
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def minimal_pdf(title, lines):
    """Return a small valid PDF preview without external dependencies."""
    content = ["BT", "/F1 18 Tf", "72 740 Td", f"({pdf_escape(title)}) Tj"]
    for i, line in enumerate(lines, start=1):
        size = 10 if i > 1 else 12
        content.extend([f"/F1 {size} Tf", "0 -22 Td", f"({pdf_escape(line)}) Tj"])
    content.append("ET")
    stream = "\n".join(content).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{index} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        out.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    out.extend(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return bytes(out)


def write_pdf_preview(path: Path, packet: Path, instrument: str, member_id: str,
                      model: str, dry_run: bool) -> None:
    pdf = minimal_pdf(
        f"{instrument} - {member_id} preview",
        [
            "Derived non-authoritative PDF preview.",
            "DXF files remain the fabrication-facing geometry authority.",
            f"Governing model: {model}.",
            "Use CAD/DXF and family-spec.csv for dimensions.",
        ],
    )
    if dry_run:
        print(f"  would write {path.relative_to(packet)} ({len(pdf)} bytes, PDF preview)")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pdf)
    print(f"  wrote {path.relative_to(packet)} (PDF preview)")


# --- DXF primitives ---------------------------------------------------------

def dxf_header(units="mm"):
    insunits = "4" if units == "mm" else "1"
    layer_rows = []
    colors = {
        "OUTLINE": 7,
        "CENTERLINE_REF": 8,
        "SCALE_REF": 3,
        "BRIDGE": 1,
        "STRING_PATH": 5,
        "NOTES_NO_CUT": 2,
    }
    for layer in DXF_REQUIRED_LAYERS:
        layer_rows.append(
            "\n".join([
                "0", "LAYER",
                "2", layer,
                "70", "0",
                "62", str(colors.get(layer, 7)),
                "6", "CONTINUOUS",
            ])
        )
    return "\n".join([
        "0", "SECTION",
        "2", "HEADER",
        "9", "$ACADVER",
        "1", "AC1009",
        "9", "$INSUNITS",
        "70", insunits,
        "0", "ENDSEC",
        "0", "SECTION",
        "2", "TABLES",
        "0", "TABLE",
        "2", "LAYER",
        "70", str(len(DXF_REQUIRED_LAYERS)),
        *layer_rows,
        "0", "ENDTAB",
        "0", "ENDSEC",
        "0", "SECTION",
        "2", "ENTITIES",
    ])


def dxf_footer():
    return "\n".join(["0", "ENDSEC", "0", "EOF", ""])


def dxf_line(layer, x1, y1, x2, y2):
    return "\n".join([
        "0", "LINE", "8", layer,
        "10", f"{x1:.3f}", "20", f"{y1:.3f}", "30", "0",
        "11", f"{x2:.3f}", "21", f"{y2:.3f}", "31", "0",
    ])


def dxf_text(layer, x, y, text, height=12):
    safe = str(text).replace("\n", " ")[:240]
    return "\n".join([
        "0", "TEXT", "8", layer,
        "10", f"{x:.3f}", "20", f"{y:.3f}", "30", "0",
        "40", f"{height:.3f}", "1", safe,
    ])


def rect_lines(layer, x, y, w, h):
    return [
        dxf_line(layer, x, y, x + w, y),
        dxf_line(layer, x + w, y, x + w, y + h),
        dxf_line(layer, x + w, y + h, x, y + h),
        dxf_line(layer, x, y + h, x, y),
    ]


def member_dimension_mm(member, *keys, default_mm=300.0):
    for key in keys:
        value = safe_float(member, key, 0.0)
        if value:
            return value * 25.4 if key.endswith("_in") else value
    return default_mm


def draw_member_dxf(member: dict, model: str, instrument: str) -> str:
    """R12-style DXF starter. Geometry is deliberately simple but layered."""
    member_id = (member.get("member_id") or
                 member.get("id") or
                 member.get("target_note") or "M-?")
    length_mm = member_dimension_mm(
        member, "body_length_mm", "predicted_length_mm",
        "predicted_L_geom_mm", "length_mm", "predicted_length_in",
        "length_in", default_mm=600.0,
    )
    width_mm = member_dimension_mm(
        member, "body_width_mm", "width_mm", "bore_mm",
        "predicted_width_mm", default_mm=max(80.0, length_mm * 0.18),
    )
    frame_h_mm = member_dimension_mm(
        member, "frame_height_mm", "height_mm", default_mm=width_mm * 1.4,
    )
    bridge_y = max(25.0, min(width_mm * 0.42, 110.0))
    scale_len = member_dimension_mm(
        member, "max_string_length_mm", "speaking_length_mm",
        "scale_length_mm", "predicted_length_mm", "predicted_length_in",
        "length_in", default_mm=length_mm * 0.82,
    )

    parts = [dxf_header("mm")]
    parts.append(dxf_text(
        "NOTES_NO_CUT", 0, width_mm + frame_h_mm + 60,
        f"{instrument} {member_id} - DXF-first visual contract; units=mm",
        18,
    ))
    parts.extend(rect_lines("OUTLINE", 0, 0, length_mm, width_mm))
    parts.append(dxf_line("CENTERLINE_REF", 0, width_mm / 2, length_mm, width_mm / 2))
    parts.append(dxf_line("SCALE_REF", 40, width_mm + 30, 40 + scale_len, width_mm + 30))

    if model == "string" or "string" in (member.get("strings_plan") or "").lower():
        bridge_a = width_mm / 2 - bridge_y / 2
        bridge_b = width_mm / 2 + bridge_y / 2
        parts.append(dxf_line("BRIDGE", 40, bridge_a, length_mm - 40, bridge_a))
        parts.append(dxf_line("BRIDGE", 40, bridge_b, length_mm - 40, bridge_b))
        courses = int(safe_float(member, "paired_courses", safe_float(member, "courses", 6)))
        courses = max(3, min(courses, 12))
        for i in range(courses):
            x = 60 + (length_mm - 120) * i / max(1, courses - 1)
            parts.append(dxf_line("STRING_PATH", x, bridge_a, length_mm - x, frame_h_mm))
            parts.append(dxf_line("STRING_PATH", x, bridge_b, length_mm - x, frame_h_mm))
    else:
        parts.append(dxf_line("BRIDGE", 40, width_mm / 2, length_mm - 40, width_mm / 2))
        parts.append(dxf_line("STRING_PATH", 60, width_mm / 2, 60 + scale_len, width_mm / 2))

    parts.append(dxf_text("NOTES_NO_CUT", 0, -35, "Derived SVG/PDF previews must not be edited as geometry authority.", 10))
    parts.append(dxf_footer())
    return "\n".join(parts)


def title_block(x, y, w, h, instrument, member_id, scale, units, rev, today):
    rows = [
        ("INSTRUMENT", instrument),
        ("MEMBER", member_id),
        ("SCALE", scale),
        ("UNITS", units),
        ("REV", rev),
        ("DATE", today),
        ("AUTHOR", "Tony Koop"),
        ("SHEET", "1 / 1"),
    ]
    pieces = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
              f'fill="white" stroke="black" stroke-width="1"/>']
    rh = h / len(rows)
    for i, (label, value) in enumerate(rows):
        ry = y + i * rh
        pieces.append(f'<line x1="{x}" y1="{ry}" x2="{x+w}" y2="{ry}" '
                      f'stroke="black" stroke-width="0.5"/>')
        pieces.append(f'<line x1="{x+w*0.35}" y1="{ry}" x2="{x+w*0.35}" '
                      f'y2="{ry+rh}" stroke="black" stroke-width="0.5"/>')
        pieces.append(f'<text x="{x+4}" y="{ry+rh*0.7}" font-size="9" '
                      f'fill="#444">{label}</text>')
        pieces.append(f'<text x="{x+w*0.36+4}" y="{ry+rh*0.7}" '
                      f'font-size="10" fill="black">{value}</text>')
    return "\n".join(pieces)


def datum_marker(x, y, letter):
    return (f'<circle cx="{x}" cy="{y}" r="9" fill="white" stroke="black" '
            f'stroke-width="1.5"/>\n'
            f'<text x="{x}" y="{y+4}" font-size="11" text-anchor="middle" '
            f'font-weight="bold">{letter}</text>')


def dim_horizontal(x1, x2, y, label, off=18):
    """Horizontal dimension between x1 and x2 at vertical y, label centered above."""
    arrow = (f'<line x1="{x1}" y1="{y-off}" x2="{x2}" y2="{y-off}" '
             f'stroke="black" stroke-width="1"/>'
             f'<line x1="{x1}" y1="{y}" x2="{x1}" y2="{y-off-4}" '
             f'stroke="black" stroke-width="1"/>'
             f'<line x1="{x2}" y1="{y}" x2="{x2}" y2="{y-off-4}" '
             f'stroke="black" stroke-width="1"/>'
             f'<polygon points="{x1},{y-off} {x1+5},{y-off-3} {x1+5},{y-off+3}" '
             f'fill="black"/>'
             f'<polygon points="{x2},{y-off} {x2-5},{y-off-3} {x2-5},{y-off+3}" '
             f'fill="black"/>'
             f'<text x="{(x1+x2)/2}" y="{y-off-6}" font-size="11" '
             f'text-anchor="middle">{label}</text>')
    return arrow


def dim_vertical(x, y1, y2, label, off=18):
    arrow = (f'<line x1="{x+off}" y1="{y1}" x2="{x+off}" y2="{y2}" '
             f'stroke="black" stroke-width="1"/>'
             f'<line x1="{x}" y1="{y1}" x2="{x+off+4}" y2="{y1}" '
             f'stroke="black" stroke-width="1"/>'
             f'<line x1="{x}" y1="{y2}" x2="{x+off+4}" y2="{y2}" '
             f'stroke="black" stroke-width="1"/>'
             f'<text x="{x+off+10}" y="{(y1+y2)/2+4}" font-size="11">{label}</text>')
    return arrow


# --- Drawing generators -----------------------------------------------------

def draw_open_pipe(member_id: str, length_in: float, bore_in: float,
                   instrument: str = "Flute") -> str:
    # Stage layout: title block at right, drawing centered.
    W, H = 800, 420
    pad = 24
    tb_w, tb_h = 220, 200
    tb_x = W - tb_w - pad
    tb_y = pad

    # Drawing area
    da_x = pad
    da_w = tb_x - 2 * pad
    da_h = H - 2 * pad

    # Map physical length to drawing length (preserve aspect ~ length:bore)
    # Render the pipe as a horizontal rectangle.
    pipe_len_px = da_w - 80
    bore_px = max(30.0, min(80.0, pipe_len_px * (bore_in / max(length_in, 1))))
    pipe_x = da_x + 40
    pipe_y = pad + 80
    pipe_w = pipe_len_px
    pipe_h = bore_px

    body = []
    # Frame
    body.append(f'<rect x="0" y="0" width="{W}" height="{H}" '
                f'fill="white" stroke="black" stroke-width="1"/>')
    # Pipe body
    body.append(f'<rect x="{pipe_x}" y="{pipe_y}" width="{pipe_w}" '
                f'height="{pipe_h}" fill="#fafafa" stroke="black" '
                f'stroke-width="1.5"/>')
    # Bore centerline
    body.append(f'<line x1="{pipe_x}" y1="{pipe_y+pipe_h/2}" '
                f'x2="{pipe_x+pipe_w}" y2="{pipe_y+pipe_h/2}" '
                f'stroke="#888" stroke-width="0.6" '
                f'stroke-dasharray="6 3 1 3"/>')
    # Datums
    body.append(datum_marker(pipe_x, pipe_y + pipe_h + 20, "A"))
    body.append(datum_marker(pipe_x + pipe_w, pipe_y + pipe_h + 20, "B"))
    # Length dimension below
    body.append(dim_horizontal(pipe_x, pipe_x + pipe_w,
                               pipe_y + pipe_h + 60,
                               f'{length_in:.3f}"', off=-18))
    # Bore dimension on left
    body.append(dim_vertical(pipe_x - 20, pipe_y, pipe_y + pipe_h,
                             f'⌀{bore_in:.3f}"', off=-18))
    # Caption
    body.append(f'<text x="{pipe_x}" y="{pad+24}" font-size="14" '
                f'font-weight="bold">{instrument} — {member_id}</text>')
    body.append(f'<text x="{pipe_x}" y="{pad+44}" font-size="11" fill="#444">'
                f'open-open pipe (open at both ends)</text>')
    body.append(f'<text x="{pipe_x}" y="{H-pad-10}" font-size="9" fill="#666">'
                f'Tolerances: ±0.005" unless noted. '
                f'Material/finish: see design.md.</text>')
    # Title block
    body.append(title_block(tb_x, tb_y, tb_w, tb_h,
                            instrument, member_id,
                            "1:1 (illustrative)", "inches",
                            "v4", date.today().isoformat()))
    return svg_doc(W, H, "\n".join(body))


def draw_helmholtz_vessel(member_id: str, chamber_volume_cuin: float,
                          target_hz: float,
                          instrument: str = "Vessel Flute") -> str:
    # Render a stylized vessel (oval) with chamber volume noted.
    W, H = 800, 420
    pad = 24
    tb_w, tb_h = 220, 200
    tb_x = W - tb_w - pad
    tb_y = pad

    da_x = pad
    da_w = tb_x - 2 * pad

    cx = da_x + da_w / 2
    cy = H / 2
    # Map volume to drawing scale; use cube-root for radius.
    r = max(40, min(140, (chamber_volume_cuin ** (1/3)) * 12))

    body = []
    body.append(f'<rect x="0" y="0" width="{W}" height="{H}" '
                f'fill="white" stroke="black" stroke-width="1"/>')
    # Section view of vessel
    body.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*0.7}" '
                f'fill="#fafafa" stroke="black" stroke-width="1.5"/>')
    # Section indicator (hatched interior)
    body.append(f'<defs><pattern id="hatch" width="6" height="6" '
                f'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                f'<line x1="0" y1="0" x2="0" y2="6" stroke="#bbb" '
                f'stroke-width="0.5"/></pattern></defs>')
    # Port (top)
    port_w = max(8, r * 0.18)
    body.append(f'<rect x="{cx-port_w/2}" y="{cy-r*0.7-12}" '
                f'width="{port_w}" height="14" '
                f'fill="white" stroke="black" stroke-width="1"/>')
    body.append(f'<text x="{cx-port_w/2}" y="{cy-r*0.7-18}" font-size="9">'
                f'port (mouth)</text>')
    # Datums
    body.append(datum_marker(cx, cy + r * 0.7 + 24, "A"))
    body.append(datum_marker(cx - r, cy, "B"))
    # Dimensions
    body.append(dim_horizontal(cx - r, cx + r, cy + r * 0.7 + 50,
                               f'OD {2*r/12:.2f}"'))
    body.append(dim_vertical(cx + r + 12, cy - r * 0.7, cy + r * 0.7,
                             f'H {1.4*r/12:.2f}"'))
    # Caption
    body.append(f'<text x="{da_x}" y="{pad+24}" font-size="14" '
                f'font-weight="bold">{instrument} — {member_id}</text>')
    body.append(f'<text x="{da_x}" y="{pad+44}" font-size="11" fill="#444">'
                f'Helmholtz vessel — V≈{chamber_volume_cuin:.1f} cu.in., '
                f'target f≈{target_hz:.1f} Hz</text>')
    body.append(f'<text x="{da_x}" y="{H-pad-10}" font-size="9" fill="#666">'
                f'Section view. Wall thickness per design.md. '
                f'Hatched interior = chamber.</text>')
    body.append(title_block(tb_x, tb_y, tb_w, tb_h,
                            instrument, member_id,
                            "1:1 (illustrative)", "inches",
                            "v4", date.today().isoformat()))
    return svg_doc(W, H, "\n".join(body))


def draw_beam_bar(member_id: str, length_in: float, thick_in: float,
                  width_in: float, instrument: str = "Bar") -> str:
    W, H = 800, 360
    pad = 24
    tb_w, tb_h = 220, 200
    tb_x = W - tb_w - pad
    da_x = pad
    da_w = tb_x - 2 * pad

    bar_x = da_x + 40
    bar_y = H / 2 - 30
    bar_w = da_w - 80
    bar_h = max(20, min(60, bar_w * (thick_in / max(length_in, 1)) * 8))
    body = []
    body.append(f'<rect x="0" y="0" width="{W}" height="{H}" '
                f'fill="white" stroke="black" stroke-width="1"/>')
    body.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" '
                f'height="{bar_h}" fill="#fafafa" stroke="black" '
                f'stroke-width="1.5"/>')
    body.append(datum_marker(bar_x, bar_y + bar_h + 20, "A"))
    body.append(datum_marker(bar_x + bar_w, bar_y + bar_h + 20, "B"))
    body.append(dim_horizontal(bar_x, bar_x + bar_w, bar_y + bar_h + 60,
                               f'L {length_in:.3f}"', off=-18))
    body.append(dim_vertical(bar_x - 20, bar_y, bar_y + bar_h,
                             f't {thick_in:.3f}"', off=-18))
    body.append(f'<text x="{bar_x}" y="{pad+24}" font-size="14" '
                f'font-weight="bold">{instrument} — {member_id}</text>')
    body.append(f'<text x="{bar_x}" y="{pad+44}" font-size="11" fill="#444">'
                f'free-free beam, suspended at antinodes (0.224 · L)</text>')
    body.append(title_block(tb_x, pad, tb_w, tb_h,
                            instrument, member_id, "1:1 (illustrative)",
                            "inches", "v4", date.today().isoformat()))
    return svg_doc(W, H, "\n".join(body))


def draw_generic(member_id: str, target_hz: float,
                 instrument: str = "Instrument") -> str:
    """When no governing model is detected — emit a placeholder with title block."""
    W, H = 800, 360
    pad = 24
    tb_w, tb_h = 220, 200
    body = []
    body.append(f'<rect x="0" y="0" width="{W}" height="{H}" '
                f'fill="white" stroke="black" stroke-width="1"/>')
    body.append(f'<text x="{pad}" y="{pad+24}" font-size="14" '
                f'font-weight="bold">{instrument} — {member_id}</text>')
    body.append(f'<text x="{pad}" y="{pad+44}" font-size="11" fill="#444">'
                f'target f≈{target_hz:.1f} Hz — governing model not detected</text>')
    body.append(f'<text x="{pad}" y="{H/2}" font-size="13" fill="#999" '
                f'text-anchor="start">[ section view placeholder — '
                f'add governing model section to design.md and re-run ]</text>')
    body.append(title_block(W - tb_w - pad, pad, tb_w, tb_h,
                            instrument, member_id, "1:1 (illustrative)",
                            "inches", "v4", date.today().isoformat()))
    return svg_doc(W, H, "\n".join(body))


# --- Driver ----------------------------------------------------------------

def safe_float(d, key, default=0.0):
    try:
        return float(d.get(key) or default)
    except (TypeError, ValueError):
        return default


def emit_member_drawing(packet: Path, member: dict, model: str,
                        instrument: str, dry_run: bool,
                        emit_svg: bool = True,
                        emit_dxf: bool = True,
                        emit_pdf: bool = False) -> tuple[Path | None, Path | None, Path | None]:
    member_id = (member.get("member_id") or
                 member.get("id") or
                 member.get("target_note") or "M-?")
    target_hz = safe_float(member, "target_hz")

    if model == "open-pipe":
        length_in = safe_float(member, "predicted_length_in",
                               safe_float(member, "length_in", 12.0))
        bore_in = safe_float(member, "bore_in",
                             safe_float(member, "predicted_bore_in", 0.875))
        svg = draw_open_pipe(member_id, length_in, bore_in, instrument)
    elif model == "helmholtz":
        vol = safe_float(member, "predicted_volume_cuin",
                         safe_float(member, "volume_cuin", 100.0))
        svg = draw_helmholtz_vessel(member_id, vol, target_hz, instrument)
    elif model in ("free-free-beam", "cantilever"):
        length_in = safe_float(member, "predicted_length_in",
                               safe_float(member, "length_in", 12.0))
        thick_in = safe_float(member, "predicted_thick_in",
                              safe_float(member, "thick_in", 0.5))
        width_in = safe_float(member, "predicted_width_in",
                              safe_float(member, "width_in", 1.5))
        svg = draw_beam_bar(member_id, length_in, thick_in, width_in,
                            instrument)
    else:
        svg = draw_generic(member_id, target_hz, instrument)

    svg_out = packet / "drawings" / f"{member_id}-body.svg"
    dxf_out = packet / "drawings" / f"{member_id}-body.dxf"
    pdf_out = packet / "drawings" / f"{member_id}-body.pdf"
    if emit_svg:
        if dry_run:
            print(f"  would write {svg_out.relative_to(packet)} ({len(svg)} bytes)")
        else:
            svg_out.parent.mkdir(parents=True, exist_ok=True)
            svg_out.write_text(svg, encoding="utf-8")
            print(f"  wrote {svg_out.relative_to(packet)}")
    if emit_dxf:
        dxf = draw_member_dxf(member, model, instrument)
        if dry_run:
            print(f"  would write {dxf_out.relative_to(packet)} ({len(dxf)} bytes, DXF authority)")
        else:
            dxf_out.parent.mkdir(parents=True, exist_ok=True)
            dxf_out.write_text(dxf, encoding="utf-8")
            print(f"  wrote {dxf_out.relative_to(packet)} (DXF authority)")
    if emit_pdf:
        write_pdf_preview(pdf_out, packet, instrument, member_id, model, dry_run)
    return (svg_out if emit_svg else None, dxf_out if emit_dxf else None, pdf_out if emit_pdf else None)


def write_visual_contract(packet: Path, targets: set[str], dxf_files: list[Path],
                          preview_files: list[Path], dry_run: bool) -> None:
    prompt_file = "images/image-gen-2-prompts.md"
    contract = {
        "visual_output_contract_version": "v4.3-dxf-first",
        "units": "mm",
        "visual_output_targets": sorted(targets),
        "geometry_authority": [
            str(path.relative_to(packet)).replace("\\", "/") for path in dxf_files
        ],
        "derived_previews": [
            str(path.relative_to(packet)).replace("\\", "/") for path in preview_files
        ],
        "image_gen_2_prompt_scaffolds": [prompt_file] if "image-prompts" in targets else [],
        "dxf_required_layers": DXF_REQUIRED_LAYERS,
        "rules": [
            "DXF is the fabrication-facing geometry authority for flat layouts.",
            "SVG and PDF are derived previews or documentation views.",
            "AI/image-gen-2 outputs are non-dimensional concept imagery only.",
        ],
    }
    out = packet / "visual-output-contract.json"
    if dry_run:
        print(f"  would write {out.relative_to(packet)}")
        return
    out.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    print(f"  wrote {out.relative_to(packet)}")


def write_image_prompts(packet: Path, instrument: str, dry_run: bool) -> None:
    text = f"""# Image-Gen-2 Prompt Scaffolds

These prompts are non-dimensional concept imagery. They must not override DXF,
CAD, family-spec.csv, measured drawings, or validation data.

## Family Hero

```text
High-quality studio concept image of {instrument}, full instrument visible,
accurate-looking material palette from the packet, clear string or resonator
layout, neutral background, no impossible hidden geometry, no extra hardware,
non-dimensional concept render.
```

## Workshop Reference

```text
Documentary luthier-workshop concept image of {instrument} in prototype build,
visible unfinished materials, bridge or datum layout visible where applicable,
realistic shop lighting, non-dimensional concept render, do not include
measurement labels.
```
"""
    out = packet / "images" / "image-gen-2-prompts.md"
    if dry_run:
        print(f"  would write {out.relative_to(packet)}")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"  wrote {out.relative_to(packet)}")


def datum_chain_horizontal(start_x, end_x, baseline_y, segments, off=22):
    """Strat-style chained dimensions: ticks at each segment break, dimensions
    given between consecutive ticks rather than always to the left datum."""
    parts = []
    for x, _ in segments:
        parts.append('<line x1="{0}" y1="{1}" x2="{0}" y2="{2}" stroke="black" stroke-width="0.5" stroke-dasharray="3 2"/>'.format(x, baseline_y, baseline_y + off + 8))
    parts.append('<line x1="{0}" y1="{2}" x2="{1}" y2="{2}" stroke="black" stroke-width="1"/>'.format(start_x, end_x, baseline_y + off))
    for i in range(len(segments) - 1):
        x1, _ = segments[i]
        x2, label = segments[i + 1]
        mid = (x1 + x2) / 2
        parts.append('<polygon points="{x1},{y} {x1p},{ym} {x1p},{yp}" fill="black"/>'.format(x1=x1, y=baseline_y + off, x1p=x1 + 4, ym=baseline_y + off - 3, yp=baseline_y + off + 3))
        parts.append('<polygon points="{x2},{y} {x2m},{ym} {x2m},{yp}" fill="black"/>'.format(x2=x2, y=baseline_y + off, x2m=x2 - 4, ym=baseline_y + off - 3, yp=baseline_y + off + 3))
        parts.append('<text x="{0}" y="{1}" font-size="9" text-anchor="middle">{2}</text>'.format(mid, baseline_y + off - 4, label))
    return "\n".join(parts)


def section_view_open_pipe(x, y, length_px, bore_px, label="A-A"):
    """Section view: hatched bore interior, walls drawn solid."""
    pid = "hatch_" + label.replace("-", "_")
    parts = []
    parts.append('<defs><pattern id="{0}" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#bbb" stroke-width="0.6"/></pattern></defs>'.format(pid))
    wall = bore_px * 0.4
    parts.append('<rect x="{0}" y="{1}" width="{2}" height="{3}" fill="white" stroke="black" stroke-width="1.5"/>'.format(x, y, length_px, bore_px + wall * 2))
    parts.append('<rect x="{0}" y="{1}" width="{2}" height="{3}" fill="url(#{4})" stroke="black" stroke-width="1"/>'.format(x, y + wall, length_px, bore_px, pid))
    parts.append('<text x="{0}" y="{1}" font-size="10" fill="#444">SECTION {2} - bore ID hatched</text>'.format(x, y - 6, label))
    return "\n".join(parts)


def draw_open_pipe_v2(member_id, length_in, bore_in, hole_positions, instrument="Flute"):
    """v4.1 enhanced open-pipe with datum chain + section view."""
    W, H = 880, 560
    pad = 24
    tb_w, tb_h = 220, 200
    tb_x = W - tb_w - pad
    pipe_len_px = tb_x - 3 * pad - 40
    bore_px = max(28, min(70, pipe_len_px * (bore_in / max(length_in, 1))))
    pipe_x = pad + 40
    pipe_y = pad + 70
    pipe_w = pipe_len_px

    body = []
    body.append('<rect x="0" y="0" width="{0}" height="{1}" fill="white" stroke="black" stroke-width="1"/>'.format(W, H))
    body.append('<text x="{0}" y="{1}" font-size="14" font-weight="bold">{2} - {3}</text>'.format(pipe_x, pad + 24, instrument, member_id))
    body.append('<text x="{0}" y="{1}" font-size="11" fill="#444">Front view (top) and section A-A (bottom)</text>'.format(pipe_x, pad + 44))
    body.append('<rect x="{0}" y="{1}" width="{2}" height="{3}" fill="#fafafa" stroke="black" stroke-width="1.5"/>'.format(pipe_x, pipe_y, pipe_w, bore_px))
    body.append('<line x1="{0}" y1="{1}" x2="{2}" y2="{1}" stroke="#888" stroke-width="0.6" stroke-dasharray="6 3 1 3"/>'.format(pipe_x, pipe_y + bore_px / 2, pipe_x + pipe_w))

    body.append(datum_marker(pipe_x, pipe_y + bore_px + 18, "A"))
    body.append(datum_marker(pipe_x + pipe_w, pipe_y + bore_px + 18, "B"))

    segments = [(pipe_x, "FOOT")]
    for label, pos in hole_positions or []:
        x = pipe_x + pipe_w * (pos / max(length_in, 1))
        body.append('<circle cx="{0}" cy="{1}" r="3" fill="black"/>'.format(x, pipe_y + bore_px / 2))
        body.append('<text x="{0}" y="{1}" font-size="9" text-anchor="middle">{2}</text>'.format(x, pipe_y - 6, label))
        segments.append((x, '{0:.2f}"'.format(pos)))
    segments.append((pipe_x + pipe_w, '{0:.3f}"'.format(length_in)))

    body.append(datum_chain_horizontal(pipe_x, pipe_x + pipe_w, pipe_y + bore_px, segments, off=44))

    section_y = pipe_y + bore_px + 130
    body.append(section_view_open_pipe(pipe_x, section_y, pipe_w, bore_px, label="A-A"))
    body.append(dim_vertical(pipe_x - 20, section_y + bore_px * 0.4, section_y + bore_px * 1.4, '\u2300{0:.3f}"'.format(bore_in), off=-18))

    body.append(title_block(tb_x, pad, tb_w, tb_h, instrument, member_id, "1:1 (illustrative)", "inches", "v4", date.today().isoformat()))
    body.append('<text x="{0}" y="{1}" font-size="9" fill="#666">Tolerances: \u00b10.005" unless noted. Hole position datum: measured from FOOT (datum A). Material/finish: see design.md.</text>'.format(pad, H - pad - 6))

    return svg_doc(W, H, "\n".join(body))


def draw_family_overview(members, model, instrument="Family"):
    n = len(members)
    if n == 0:
        return draw_generic("FAMILY", 440.0, instrument)
    W = 1100
    row_h = 100
    H = 80 + n * row_h + 100
    max_dim = max(safe_float(m, "predicted_length_in", safe_float(m, "length_in", 12.0)) for m in members) or 12.0

    chart_x = 200
    chart_w = W - chart_x - 80

    body = []
    body.append('<rect x="0" y="0" width="{0}" height="{1}" fill="white" stroke="black" stroke-width="1"/>'.format(W, H))
    body.append('<text x="32" y="36" font-size="18" font-weight="bold">{0} - Family overview</text>'.format(instrument))
    body.append('<text x="32" y="56" font-size="11" fill="#444">{0} members. Drawn to relative scale; longest member = {1:.2f}". Governing model: {2}.</text>'.format(n, max_dim, model))

    for i, m in enumerate(members):
        y = 80 + i * row_h
        member_id = m.get("member_id") or m.get("target_note") or m.get("id") or "M-{0}".format(i + 1)
        note = m.get("target_note") or ""
        target_hz = safe_float(m, "target_hz")
        length_in = safe_float(m, "predicted_length_in", safe_float(m, "length_in", 12.0))

        body.append('<text x="32" y="{0}" font-size="13" font-weight="bold">{1}</text>'.format(y + 30, member_id))
        body.append('<text x="32" y="{0}" font-size="10" fill="#666">{1} ({2:.1f} Hz)</text>'.format(y + 50, note, target_hz))
        body.append('<text x="32" y="{0}" font-size="10" fill="#666">L = {1:.3f}"</text>'.format(y + 66, length_in))

        scaled_w = chart_w * (length_in / max_dim)
        if model == "open-pipe":
            bore_px = 22
            body.append('<rect x="{0}" y="{1}" width="{2}" height="{3}" fill="#fafafa" stroke="black" stroke-width="1.2"/>'.format(chart_x, y + 24, scaled_w, bore_px))
            body.append('<line x1="{0}" y1="{1}" x2="{2}" y2="{1}" stroke="#888" stroke-width="0.6" stroke-dasharray="4 2 1 2"/>'.format(chart_x, y + 24 + bore_px / 2, chart_x + scaled_w))
        elif model in ("free-free-beam", "cantilever"):
            bar_h = 18
            body.append('<rect x="{0}" y="{1}" width="{2}" height="{3}" fill="#fafafa" stroke="black" stroke-width="1.2"/>'.format(chart_x, y + 28, scaled_w, bar_h))
        else:
            body.append('<rect x="{0}" y="{1}" width="{2}" height="22" fill="#fafafa" stroke="black" stroke-width="1.2"/>'.format(chart_x, y + 24, scaled_w))
        body.append('<text x="{0}" y="{1}" font-size="9" fill="#444">{2:.2f}"</text>'.format(chart_x + scaled_w + 8, y + 38, length_in))

    body.append('<text x="32" y="{0}" font-size="9" fill="#666">Generated by instrument-maker generate_drawings.py. Scale: {1:.1f} px/inch.</text>'.format(H - 20, chart_w / max_dim))
    return svg_doc(W, H, "\n".join(body))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("packet", help="path to build-packets/<slug>")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--legacy-drawings", action="store_true",
                    help="Use simpler v4.0 drawing style")
    ap.add_argument(
        "--visual-output-targets",
        default="dxf,preview-svg,image-prompts",
        help=(
            "Comma-separated targets: dxf, preview-svg, preview-pdf, "
            "image-prompts. SVG/PDF are previews; DXF is geometry authority."
        ),
    )
    args = ap.parse_args()

    packet = Path(args.packet)
    if not packet.exists():
        print("packet not found: {0}".format(packet), file=sys.stderr)
        return 1

    members = read_family_spec(packet) or []
    design_text = read_design_md(packet)
    model = detect_governing_model(design_text)

    instrument = packet.name
    for line in design_text.splitlines():
        if line.startswith("# "):
            instrument = line[2:].strip()
            break

    print("packet: {0}".format(packet))
    print("governing model (detected): {0}".format(model))
    print("family members: {0}".format(len(members)))
    targets = {t.strip().lower() for t in args.visual_output_targets.split(",") if t.strip()}
    emit_dxf = "dxf" in targets
    emit_svg = "preview-svg" in targets or "svg" in targets
    emit_pdf = "preview-pdf" in targets or "pdf" in targets
    svg_files = []
    dxf_files = []
    preview_files = []

    if not members:
        members = [{"member_id": instrument.replace(" ", "-")[:24], "target_hz": 440.0}]
        print("(no family-spec.csv - emitting single drawing)")

    for m in members:
        if not args.legacy_drawings and model == "open-pipe":
            member_id = m.get("member_id") or m.get("target_note") or "M"
            length_in = safe_float(m, "predicted_length_in", safe_float(m, "length_in", 12.0))
            bore_in = safe_float(m, "bore_in", safe_float(m, "predicted_bore_in", 0.875))
            svg = draw_open_pipe_v2(member_id, length_in, bore_in, [], instrument)
            out = packet / "drawings" / "{0}-body.svg".format(member_id)
            if emit_svg and args.dry_run:
                print("  would write {0} ({1} bytes, v4.1 style)".format(out.relative_to(packet), len(svg)))
            elif emit_svg:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(svg, encoding="utf-8")
                print("  wrote {0} (v4.1 style)".format(out.relative_to(packet)))
            if emit_svg:
                svg_files.append(out)
                preview_files.append(out)
            if emit_dxf:
                dxf = draw_member_dxf(m, model, instrument)
                dxf_out = packet / "drawings" / "{0}-body.dxf".format(member_id)
                if args.dry_run:
                    print("  would write {0} ({1} bytes, DXF authority)".format(dxf_out.relative_to(packet), len(dxf)))
                else:
                    dxf_out.parent.mkdir(parents=True, exist_ok=True)
                    dxf_out.write_text(dxf, encoding="utf-8")
                    print("  wrote {0} (DXF authority)".format(dxf_out.relative_to(packet)))
                dxf_files.append(dxf_out)
            if emit_pdf:
                pdf_out = packet / "drawings" / "{0}-body.pdf".format(member_id)
                write_pdf_preview(pdf_out, packet, instrument, member_id, model, args.dry_run)
                preview_files.append(pdf_out)
        else:
            svg_out, dxf_out, pdf_out = emit_member_drawing(
                packet, m, model, instrument, args.dry_run,
                emit_svg=emit_svg, emit_dxf=emit_dxf, emit_pdf=emit_pdf,
            )
            if svg_out:
                svg_files.append(svg_out)
                preview_files.append(svg_out)
            if dxf_out:
                dxf_files.append(dxf_out)
            if pdf_out:
                preview_files.append(pdf_out)

    if len(members) > 1:
        svg = draw_family_overview(members, model, instrument)
        out = packet / "drawings" / "family-overview.svg"
        if emit_svg and args.dry_run:
            print("  would write {0} ({1} bytes)".format(out.relative_to(packet), len(svg)))
        elif emit_svg:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(svg, encoding="utf-8")
            print("  wrote {0}".format(out.relative_to(packet)))
        if emit_svg:
            svg_files.append(out)
            preview_files.append(out)
        if emit_pdf:
            pdf_out = packet / "drawings" / "family-overview.pdf"
            write_pdf_preview(pdf_out, packet, instrument, "family-overview", model, args.dry_run)
            preview_files.append(pdf_out)

    write_visual_contract(packet, targets, dxf_files, preview_files, args.dry_run)
    if "image-prompts" in targets:
        write_image_prompts(packet, instrument, args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
