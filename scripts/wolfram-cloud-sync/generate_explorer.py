#!/usr/bin/env python3
"""
generate_explorer.py — clean, self-contained explorer.html generator.

Reconstruction of the lost instrument-maker explorer generator. Renders a
single static explorer.html per instrument repo: title + design summary +
packet file list + a LIVE interactive Wolfram embed (direct iframe to the
CloudDeploy[Manipulate] public URL).

Usage:
    python3 generate_explorer.py <repo_dir> \
        --embed-urls <interactive_urls.json> [--output <path>]

--embed-urls JSON is a list of {repo, cloud_url, ...}; the entry whose `repo`
matches <repo_dir>'s basename supplies the interactive iframe URL. If no match,
the Wolfram section renders a 'pending publish' note instead of an iframe.
"""
from __future__ import annotations
import argparse, html, json, re
from pathlib import Path

PACKET_FILES = ["design.md", "decision-record.md", "bom.csv", "cut-list.csv",
                "visual-output-register.csv", "validation.csv", "sourcing.csv",
                "family-spec.csv", "risks.md"]

def md_first_para(text: str) -> str:
    for block in re.split(r"\n\s*\n", text):
        b = block.strip()
        if b and not b.startswith("#") and not b.startswith("|") and not b.startswith("Status:"):
            return re.sub(r"\s+", " ", b)
    return ""

def title_from(repo: str, readme: str) -> str:
    m = re.search(r"^#\s+(.+)", readme, re.M)
    return m.group(1).strip() if m else repo.replace("-", " ").title()

def status_line(readme: str) -> str:
    m = re.search(r"^Status:\s*(.+)", readme, re.M)
    return m.group(1).strip() if m else "concept packet"

def render(repo_dir: Path, embed_url: str | None) -> str:
    repo = repo_dir.name
    readme = (repo_dir / "README.md").read_text(encoding="utf-8", errors="replace") if (repo_dir / "README.md").exists() else ""
    design = (repo_dir / "design.md").read_text(encoding="utf-8", errors="replace") if (repo_dir / "design.md").exists() else ""
    title = title_from(repo, readme)
    status = status_line(readme)
    intro = md_first_para(design) or md_first_para(readme)
    files = [f for f in PACKET_FILES if (repo_dir / f).exists()]
    # wolfram section
    if embed_url:
        wolfram = (
            '<div class="wf-actions">'
            f'<a class="btn primary" href="{html.escape(embed_url)}" target="_blank" rel="noopener">&#8599; Open full interactive model</a>'
            '</div>'
            f'<iframe class="wf-frame" src="{html.escape(embed_url)}" title="Interactive Wolfram model" loading="lazy"></iframe>'
            '<p class="muted">Live interactive acoustic model (Wolfram Cloud, Public-Execute). '
            'Drag the sliders; every value is computed from <strong>estimate placeholders</strong> — pending measurement, not fabrication authority.</p>'
        )
    else:
        wolfram = ('<p class="muted">Interactive Wolfram model not yet published for this instrument. '
                   'Deploy via <code>wolfram-cloud-sync</code> (CloudDeploy the model\'s Manipulate) to embed it here.</p>')
    file_rows = "".join(
        f'<li><a href="{f}" target="_blank">{html.escape(f)}</a></li>' for f in files
    ) or "<li class='muted'>No packet files detected.</li>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — Explorer</title>
<style>
:root{{--ink:#2a2018;--walnut:#5b3a29;--accent:#a64b2a;--rule:#e7ddcc;--paper:#fcfaf5;--muted:#8a7d6b;--mono:ui-monospace,Menlo,monospace;--serif:Georgia,'Times New Roman',serif}}
*{{box-sizing:border-box}}body{{margin:0;font-family:var(--serif);color:var(--ink);background:var(--paper);line-height:1.55}}
.wrap{{max-width:920px;margin:0 auto;padding:32px 20px 64px}}
header h1{{font-size:30px;margin:.2em 0 .1em}}.eyebrow{{font-family:var(--mono);font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);display:block;margin-bottom:6px}}
.status{{font-family:var(--mono);font-size:12px;color:var(--muted);margin:0 0 18px}}
section{{margin:30px 0;padding-top:18px;border-top:1px solid var(--rule)}}
section h2{{font-size:20px;color:var(--walnut);margin:.2em 0 .6em}}
p.intro{{font-size:17px}}
.wf-frame{{width:100%;height:660px;border:1px solid var(--rule);border-radius:8px;background:#fff;margin:6px 0}}
.wf-actions{{margin:6px 0}}
.btn{{display:inline-block;padding:7px 14px;border-radius:6px;text-decoration:none;font-family:var(--mono);font-size:13px;background:#efe7d8;color:var(--walnut)}}
.btn.primary{{background:var(--accent);color:#fff}}
ul.files{{font-family:var(--mono);font-size:14px;columns:2;gap:24px}}
ul.files a{{color:var(--walnut)}}
.muted{{color:var(--muted);font-size:13px}}
footer{{margin-top:44px;color:var(--muted);font-size:12px;font-family:var(--mono)}}
</style></head>
<body><div class="wrap">
<header><span class="eyebrow">Instrument Explorer</span><h1>{html.escape(title)}</h1>
<p class="status">Status: {html.escape(status)}</p></header>
{f'<p class="intro">{html.escape(intro)}</p>' if intro else ''}
<section id="wolfram"><h2><span class="eyebrow">Run it — Wolfram Cloud</span>Interactive acoustic model</h2>
{wolfram}
</section>
<section id="files"><h2>Build packet</h2>
<ul class="files">{file_rows}</ul></section>
<footer>Generated by wolfram-cloud-sync/generate_explorer.py · {html.escape(repo)}</footer>
</div></body></html>
"""

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("repo_dir", type=Path)
    p.add_argument("--embed-urls", type=Path, required=True)
    p.add_argument("--output", type=Path, default=None)
    a = p.parse_args(argv)
    repo = a.repo_dir.resolve()
    repo_name = repo.name
    embed_url = None
    if a.embed_urls.exists():
        data = json.loads(a.embed_urls.read_text())
        rows = data if isinstance(data, list) else data.get("files", [])
        for r in rows:
            if r.get("repo") == repo_name and r.get("cloud_url"):
                embed_url = r["cloud_url"]; break
    out = a.output or (repo / "explorer.html")
    out.write_text(render(repo, embed_url), encoding="utf-8")
    print(f"{repo_name}: explorer.html {'(live embed)' if embed_url else '(pending)'} -> {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
