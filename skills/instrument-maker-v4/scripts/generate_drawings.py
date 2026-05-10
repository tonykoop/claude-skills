#!/usr/bin/env python3
"""
generate_drawings.py — emit dimensioned SVG drawings per family member.

Brainstorm Tier 1 #1: today drawing-brief.md describes the drawing the user
should make and cad/ is empty. v4 emits an opinionated "good enough for shop
floor" SVG with title block, datums, critical dimensions, and a section view.

Reads:
    - <packet>/family-spec.csv (family-aware) or design.md family table
    - <packet>/design.md governing model section (for the section view shape)

Writes:
    - <packet>/drawings/<member-id>-body.svg (one per family member)
    - <packet>/drawings/family-overview.svg (combined family scale chart)

Usage:
    python3 scripts/generate_drawings.py ./build-packets/<slug>
    python3 scripts/generate_drawings.py ./build-packets/<slug> --dry-run
"""

import argparse
import csv
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


# --- SVG primitives ---------------------------------------------------------

def svg_doc(width, height, body):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" '
            f'font-family="Helvetica, Arial, sans-serif">\n'
            f'{body}\n</svg>\n')


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
                        instrument: str, dry_run: bool) -> Path:
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

    out = packet / "drawings" / f"{member_id}-body.svg"
    if dry_run:
        print(f"  would write {out.relative_to(packet)} ({len(svg)} bytes)")
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg, encoding="utf-8")
        print(f"  wrote {out.relative_to(packet)}")
    return out


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

    body.append('<text x="32" y="{0}" font-size="9" fill="#666">Generated by instrument-maker-v4 generate_drawings.py. Scale: {1:.1f} px/inch.</text>'.format(H - 20, chart_w / max_dim))
    return svg_doc(W, H, "\n".join(body))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("packet", help="path to build-packets/<slug>")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--legacy-drawings", action="store_true",
                    help="Use simpler v4.0 drawing style")
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
            if args.dry_run:
                print("  would write {0} ({1} bytes, v4.1 style)".format(out.relative_to(packet), len(svg)))
            else:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(svg, encoding="utf-8")
                print("  wrote {0} (v4.1 style)".format(out.relative_to(packet)))
        else:
            emit_member_drawing(packet, m, model, instrument, args.dry_run)

    if len(members) > 1:
        svg = draw_family_overview(members, model, instrument)
        out = packet / "drawings" / "family-overview.svg"
        if args.dry_run:
            print("  would write {0} ({1} bytes)".format(out.relative_to(packet), len(svg)))
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(svg, encoding="utf-8")
            print("  wrote {0}".format(out.relative_to(packet)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
