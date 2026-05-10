#!/usr/bin/env python3
"""
generate_site.py — emit a static-site build log for one packet.

Brainstorm Tier 5 #18: a recruiter-grade artifact that isn't a slide deck —
"here's a working portfolio site, every instrument links to its build."

Reads:
    - <packet>/design.md, bom.csv, cut-list.csv, validation.csv,
      assembly-manual.md, risks.md, family-spec.csv, images/*,
      drawings/*, capstone-manifest.json
Writes:
    - <packet>/site/index.html
    - <packet>/site/assets/style.css
    - <packet>/site/assets/<copies of images and drawings>
    - <packet>/site/family/index.html (when family-spec has >1 row)

Usage:
    python3 scripts/generate_site.py ./build-packets/<slug>
    python3 scripts/generate_site.py ./build-packets/<slug> \\
        --output ./build-packets/<slug>/site \\
        --theme warm-wood
    python3 scripts/generate_site.py ./build-packets/<slug> --dry-run
"""

import argparse
import csv
import html
import json
import shutil
import sys
from pathlib import Path

DEFAULT_THEME = {
    "warm-wood": {"accent": "#8b4513", "bg": "#fdfbf7", "fg": "#1d1714"},
    "cool-metal": {"accent": "#2c5f7c", "bg": "#f5f8fa", "fg": "#0d1f2d"},
    "earth-ceramic": {"accent": "#a0522d", "bg": "#fbf5ec", "fg": "#2a1f12"},
}

CSS_TEMPLATE = """
:root {{
  --accent: {accent};
  --bg: {bg};
  --fg: {fg};
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: Charter, 'Iowan Old Style', Georgia, serif;
  background: var(--bg);
  color: var(--fg);
  line-height: 1.55;
}}
header.hero {{
  position: relative;
  width: 100%;
  background: var(--accent);
  color: white;
  padding: 0;
}}
header.hero .hero-img {{
  width: 100%;
  height: 360px;
  object-fit: cover;
  display: block;
  filter: brightness(0.85);
}}
header.hero .hero-text {{
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 32px;
}}
header.hero h1 {{
  margin: 0;
  font-family: Inter, system-ui, sans-serif;
  font-size: 36px;
  font-weight: 700;
}}
header.hero p {{
  margin: 8px 0 0;
  font-size: 18px;
  max-width: 720px;
}}
main {{
  max-width: 760px;
  margin: 0 auto;
  padding: 32px 20px;
}}
section {{ margin: 48px 0; }}
h2 {{
  font-family: Inter, system-ui, sans-serif;
  font-size: 22px;
  border-bottom: 2px solid var(--accent);
  padding-bottom: 6px;
}}
h3 {{ font-family: Inter, system-ui, sans-serif; font-size: 17px; }}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}}
th, td {{
  padding: 6px 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}}
tr:nth-child(even) td {{ background: rgba(0,0,0,0.02); }}
th {{
  background: var(--accent);
  color: white;
  font-family: Inter, system-ui, sans-serif;
}}
td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.process-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  margin-top: 16px;
}}
.process-grid img {{ width: 100%; height: auto; border-radius: 4px; }}
svg.drawing {{
  width: 100%;
  height: auto;
  border: 1px solid #ccc;
  background: white;
  padding: 8px;
}}
footer {{
  border-top: 1px solid #ddd;
  margin-top: 64px;
  padding: 24px 20px;
  font-size: 13px;
  color: #666;
  text-align: center;
}}
.placeholder {{
  background: #fff8e1;
  border-left: 4px solid #f9a825;
  padding: 12px 16px;
  font-size: 14px;
  color: #6b4f00;
}}
@media (max-width: 600px) {{
  header.hero .hero-img {{ height: 220px; }}
  header.hero h1 {{ font-size: 28px; }}
  header.hero p {{ font-size: 15px; }}
  main {{ padding: 16px; }}
}}
"""


def slug_from(packet: Path) -> str:
    return packet.name


def read_text(p: Path) -> str:
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")


def first_paragraph(md: str) -> str:
    for para in md.split("\n\n"):
        para = para.strip()
        if not para or para.startswith("#") or para.startswith("```"):
            continue
        return para
    return ""


def section_after_heading(md: str, heading_prefix: str) -> str:
    """Pull body of '## Heading' until the next '## '."""
    lines = md.splitlines()
    in_section = False
    body = []
    for line in lines:
        if line.startswith("## "):
            if in_section:
                break
            if heading_prefix.lower() in line.lower():
                in_section = True
                continue
        elif in_section:
            body.append(line)
    return "\n".join(body).strip()


def csv_to_table(path: Path, max_rows: int = 200) -> str:
    if not path.exists():
        return '<p class="placeholder">No data file at <code>' \
               f'{html.escape(str(path.name))}</code>.</p>'
    with path.open(newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return f'<p class="placeholder">{html.escape(path.name)} is empty.</p>'
    header, body = rows[0], rows[1:]
    body = body[:max_rows]
    th = "".join(f"<th>{html.escape(c)}</th>" for c in header)
    trs = []
    for r in body:
        cells = []
        for c in r:
            cls = ' class="num"' if c.replace(".", "").replace(
                "-", "").replace(",", "").isdigit() else ""
            cells.append(f"<td{cls}>{html.escape(c)}</td>")
        trs.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{th}</tr></thead><tbody>" + \
           "\n".join(trs) + "</tbody></table>"


def md_to_simple_html(md: str) -> str:
    """Crude paragraph + heading conversion. Scoped to keep the script
    dependency-free; for full CommonMark compliance, run pandoc separately."""
    if not md.strip():
        return '<p class="placeholder">(section missing in design.md)</p>'
    out = []
    for para in md.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        if para.startswith("### "):
            out.append(f"<h3>{html.escape(para[4:].strip())}</h3>")
        elif para.startswith("## "):
            out.append(f"<h3>{html.escape(para[3:].strip())}</h3>")
        elif para.startswith("# "):
            out.append(f"<h2>{html.escape(para[2:].strip())}</h2>")
        elif para.startswith("- ") or para.startswith("* "):
            items = []
            for line in para.splitlines():
                line = line.strip()
                if line.startswith(("-", "*")):
                    items.append(f"<li>{html.escape(line[1:].strip())}</li>")
            out.append("<ul>" + "".join(items) + "</ul>")
        else:
            out.append(f"<p>{html.escape(para)}</p>")
    return "\n".join(out)


def collect_images(packet: Path):
    img_dir = packet / "images"
    if not img_dir.exists():
        return None, []
    images = sorted([p for p in img_dir.iterdir()
                     if p.suffix.lower() in (".jpg", ".jpeg", ".png",
                                              ".webp")])
    hero = next((p for p in images if "hero" in p.stem.lower()), None)
    if hero is None and images:
        hero = images[0]
    process = [p for p in images if p != hero]
    return hero, process


def collect_drawings(packet: Path):
    d = packet / "drawings"
    if not d.exists():
        return []
    return sorted([p for p in d.iterdir() if p.suffix.lower() == ".svg"])


def render_hero_section(hero_rel, instrument, intent):
    if hero_rel:
        hero_html = (f'<img class="hero-img" src="{hero_rel}" '
                     f'alt="{html.escape(instrument)}">')
    else:
        hero_html = ('<div class="hero-img" '
                     'style="background:linear-gradient(135deg,#5c3517,#a0522d);'
                     'height:360px;"></div>')
    return (f'<header class="hero">'
            f'{hero_html}'
            f'<div class="hero-text">'
            f'<h1>{html.escape(instrument)}</h1>'
            f'<p>{html.escape(intent)}</p>'
            f'</div></header>')


def render_drawings_section(drawings_rel):
    if not drawings_rel:
        return '<p class="placeholder">No drawings found in ' \
               '<code>drawings/</code>. Run <code>generate_drawings.py</code>.</p>'
    parts = []
    for d in drawings_rel:
        parts.append(f'<figure><object data="{d}" type="image/svg+xml" '
                     f'class="drawing"></object>'
                     f'<figcaption>{html.escape(Path(d).stem)}</figcaption>'
                     f'</figure>')
    return "\n".join(parts)


def render_process_section(process_rel):
    if not process_rel:
        return '<p class="placeholder">No process photos in ' \
               '<code>images/</code>. Add at least one to populate this section.</p>'
    return ('<div class="process-grid">'
            + "".join(f'<img src="{p}" alt="">' for p in process_rel)
            + '</div>')


def render_family_section(packet: Path):
    fs = packet / "family-spec.csv"
    if not fs.exists():
        return ""
    with fs.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) <= 1:
        return ""
    items = []
    for r in rows:
        mid = r.get("member_id") or r.get("target_note") or "?"
        note = r.get("target_note") or ""
        items.append(f"<li><a href=\"family/{html.escape(mid)}.html\">"
                     f"{html.escape(mid)} — {html.escape(note)}</a></li>")
    return "<ul>" + "".join(items) + "</ul>"


def build_index_html(packet: Path, theme_name: str):
    design_md = read_text(packet / "design.md")
    risks_md = read_text(packet / "risks.md")
    assembly_md = read_text(packet / "assembly-manual.md")

    instrument = packet.name.replace("-", " ").title()
    for line in design_md.splitlines():
        if line.startswith("# "):
            instrument = line[2:].strip()
            break

    intent = first_paragraph(section_after_heading(design_md,
                                                   "Project Intent"))
    if not intent:
        intent = first_paragraph(design_md)
    if not intent:
        intent = "An instrument from Tony Koop's portfolio."

    hero, process = collect_images(packet)
    drawings = collect_drawings(packet)

    # Asset copying happens in main(); here we just produce relative paths.
    hero_rel = f"assets/{hero.name}" if hero else None
    process_rel = [f"assets/{p.name}" for p in process]
    drawings_rel = [f"assets/drawings/{d.name}" for d in drawings]

    sections = []
    sections.append(("What this is",
                     md_to_simple_html(section_after_heading(design_md,
                                                             "Project Intent"))))
    sections.append(("The design",
                     md_to_simple_html(
                         section_after_heading(design_md, "Governing Model"))
                     + render_drawings_section(drawings_rel)))
    sections.append(("The build",
                     md_to_simple_html(assembly_md)
                     + render_process_section(process_rel)))
    sections.append(("The numbers",
                     "<h3>BOM</h3>"
                     + csv_to_table(packet / "bom.csv")
                     + "<h3>Cut list</h3>"
                     + csv_to_table(packet / "cut-list.csv")))
    sections.append(("Tuning &amp; validation",
                     csv_to_table(packet / "validation.csv")))
    sections.append(("Known risks",
                     md_to_simple_html(risks_md)))
    family_html = render_family_section(packet)
    if family_html:
        sections.append(("Family overview", family_html))
    sections.append(("Resources",
                     "<ul>"
                     "<li><a href=\"../README.md\">Project README</a></li>"
                     "<li><a href=\"../capstone-deck.pptx\">Capstone deck (.pptx)</a></li>"
                     "<li><a href=\"../print-packet.pdf\">Printable shop packet (.pdf)</a></li>"
                     "<li><a href=\"https://github.com/tonykoop\">Tony's GitHub</a></li>"
                     "</ul>"))

    sections_html = "\n".join(
        f'<section><h2>{title}</h2>{body}</section>'
        for title, body in sections)

    css_inline = CSS_TEMPLATE.format(
        **DEFAULT_THEME.get(theme_name, DEFAULT_THEME["warm-wood"]))

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(instrument)} — Tony Koop's Build Log</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
{render_hero_section(hero_rel, instrument, intent)}
<main>
{sections_html}
</main>
<footer>
Built by Tony Koop · CC-BY 4.0 · <a href="https://github.com/tonykoop">github.com/tonykoop</a>
</footer>
</body>
</html>
"""
    return page, css_inline, hero, process, drawings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("packet")
    ap.add_argument("--output", default=None)
    ap.add_argument("--theme", default="warm-wood",
                    choices=list(DEFAULT_THEME.keys()))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    packet = Path(args.packet)
    if not packet.exists():
        print(f"packet not found: {packet}", file=sys.stderr)
        return 1

    out = Path(args.output) if args.output else (packet / "site")

    page, css, hero, process, drawings = build_index_html(packet,
                                                          args.theme)

    if args.dry_run:
        print(f"--dry-run: would write {out}/index.html ({len(page)} bytes)")
        print(f"--dry-run: would write {out}/assets/style.css "
              f"({len(css)} bytes)")
        print(f"--dry-run: would copy hero={hero}, "
              f"process={len(process)} files, drawings={len(drawings)} files")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    (out / "assets").mkdir(parents=True, exist_ok=True)
    (out / "assets/drawings").mkdir(parents=True, exist_ok=True)

    (out / "index.html").write_text(page, encoding="utf-8")
    (out / "assets/style.css").write_text(css, encoding="utf-8")

    if hero:
        shutil.copy2(hero, out / "assets" / hero.name)
    for p in process:
        shutil.copy2(p, out / "assets" / p.name)
    for d in drawings:
        shutil.copy2(d, out / "assets/drawings" / d.name)

    print(f"wrote {out}/index.html")
    print(f"wrote {out}/assets/style.css")
    if hero:
        print(f"copied hero {hero.name}")
    print(f"copied {len(process)} process images")
    print(f"copied {len(drawings)} drawings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
