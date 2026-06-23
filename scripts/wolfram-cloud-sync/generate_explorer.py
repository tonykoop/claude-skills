#!/usr/bin/env python3
"""
generate_explorer.py — additive explorer.html generator for instrument repos.

Renders a single static explorer.html per instrument repo: title + design
summary + a LIVE interactive Wolfram embed (direct iframe to the
CloudDeploy[Manipulate] public URL) + a concept-image grid + packet file list.

ADDITIVE BY DESIGN (this is the whole point — see the "dual-generator clobber"
lesson). A re-run must never regress what already landed:

  * If explorer.html already EXISTS, we PATCH the live Wolfram URL in place
    (the `data-cloud-url` slot, the iframe `src`, and the "open" anchor `href`)
    and leave everything else — image gallery, any hand edits, an alternate
    V5/hero layout — untouched.
  * If we have NO fresh URL for an existing explorer, we KEEP its current embed.
    We never downgrade a live embed back to a "pending" note.
  * A full template render happens ONLY for a greenfield repo (no explorer.html
    yet) or when you pass --force.

Usage:
    python3 generate_explorer.py <repo_dir> \
        --embed-urls <interactive_urls.json> [--output <path>] [--force]

--embed-urls JSON is a list of {repo, cloud_url, ...} (the manifest written by
deploy_interactive.sh); the entry whose `repo` matches <repo_dir>'s basename
supplies the interactive iframe URL.
"""
from __future__ import annotations
import argparse, html, json, re
from pathlib import Path

PACKET_FILES = ["design.md", "decision-record.md", "bom.csv", "cut-list.csv",
                "visual-output-register.csv", "validation.csv", "sourcing.csv",
                "family-spec.csv", "risks.md"]

# Any wolframcloud object URL anywhere in the doc (src/href/data-cloud-url).
CLOUD_URL_RE = re.compile(r'https://www\.wolframcloud\.com/obj/[^\s"\'<>]+')
DATA_SLOT_RE = re.compile(r'data-cloud-url="[^"]*"')
GENERATED_MARKER = "wolfram-cloud-sync/generate_explorer.py"


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


IMAGE_ORDER = ["images/hero-render.png", "images/family-group.png", "images/exploded-diagram.png"]


def collect_images(repo_dir: Path) -> list[str]:
    """Canonical concept images that exist, in display order (hero, family, exploded, macros)."""
    found = [p for p in IMAGE_ORDER if (repo_dir / p).exists()]
    macro = repo_dir / "images" / "macro"
    if macro.is_dir():
        found += sorted(f"images/macro/{m.name}" for m in macro.glob("*.png"))
    return found


def render(repo_dir: Path, embed_url: str | None) -> str:
    """Full greenfield render. Used only when no explorer.html exists yet (or --force)."""
    repo = repo_dir.name
    readme = (repo_dir / "README.md").read_text(encoding="utf-8", errors="replace") if (repo_dir / "README.md").exists() else ""
    design = (repo_dir / "design.md").read_text(encoding="utf-8", errors="replace") if (repo_dir / "design.md").exists() else ""
    title = title_from(repo, readme)
    status = status_line(readme)
    intro = md_first_para(design) or md_first_para(readme)
    files = [f for f in PACKET_FILES if (repo_dir / f).exists()]
    # wolfram section — `data-cloud-url` on the <section> is the stable patch slot.
    if embed_url:
        slot = html.escape(embed_url)
        wolfram = (
            '<div class="wf-actions">'
            f'<a class="btn primary wf-open" href="{slot}" target="_blank" rel="noopener">&#8599; Open full interactive model</a>'
            '</div>'
            f'<iframe class="wf-frame" src="{slot}" title="Interactive Wolfram model" loading="lazy"></iframe>'
            '<p class="muted">Live interactive acoustic model (Wolfram Cloud, Public-Execute). '
            'Drag the sliders; every value is computed from <strong>estimate placeholders</strong> — pending measurement, not fabrication authority.</p>'
        )
    else:
        slot = ""
        wolfram = ('<p class="muted">Interactive Wolfram model not yet published for this instrument. '
                   'Deploy via <code>wolfram-cloud-sync</code> (CloudDeploy the model\'s Manipulate) to embed it here.</p>')
    file_rows = "".join(
        f'<li><a href="{f}" target="_blank">{html.escape(f)}</a></li>' for f in files
    ) or "<li class='muted'>No packet files detected.</li>"
    # images section (canonical concept renders)
    imgs = collect_images(repo_dir)
    if imgs:
        cells = "".join(
            f'<figure class="img-cell"><img src="{html.escape(p)}" alt="{html.escape(repo)} — {html.escape(p.split("/")[-1])}" loading="lazy"><figcaption>{html.escape(p.split("/")[-1])}</figcaption></figure>'
            for p in imgs)
        images_html = f'<div class="img-grid">{cells}</div><p class="muted">Concept renders — not fabrication authority.</p>'
    else:
        images_html = ('<p class="muted">Concept renders pending. Prompt set in '
                       '<code>docs/image-gen-prompt.md</code>; render into <code>images/</code> '
                       '(hero-render.png, macro/, etc.) via the image pipeline.</p>')
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
.img-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;margin:8px 0}}
.img-cell{{margin:0}}.img-cell img{{width:100%;border:1px solid var(--rule);border-radius:6px;display:block;background:#fff}}
.img-cell figcaption{{font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:4px}}
.muted{{color:var(--muted);font-size:13px}}
footer{{margin-top:44px;color:var(--muted);font-size:12px;font-family:var(--mono)}}
</style></head>
<body><div class="wrap">
<header><span class="eyebrow">Instrument Explorer</span><h1>{html.escape(title)}</h1>
<p class="status">Status: {html.escape(status)}</p></header>
{f'<p class="intro">{html.escape(intro)}</p>' if intro else ''}
<section id="wolfram" data-cloud-url="{slot}"><h2><span class="eyebrow">Run it — Wolfram Cloud</span>Interactive acoustic model</h2>
{wolfram}
</section>
<section id="images"><h2>Concept images</h2>
{images_html}
</section>
<section id="files"><h2>Build packet</h2>
<ul class="files">{file_rows}</ul></section>
<footer>Generated by {GENERATED_MARKER} · {html.escape(repo)}</footer>
</div></body></html>
"""


def patch_embed(text: str, embed_url: str) -> tuple[str, int]:
    """Patch the live Wolfram URL into an existing explorer.html in place.

    Updates the `data-cloud-url` slot and every wolframcloud object URL (iframe
    src + open-anchor href). Everything else in the document is preserved.
    Returns (new_text, replacements_made).
    """
    esc = html.escape(embed_url)
    n = 0
    text, c = DATA_SLOT_RE.subn(f'data-cloud-url="{esc}"', text)
    n += c
    text, c = CLOUD_URL_RE.subn(esc, text)
    n += c
    return text, n


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("repo_dir", type=Path)
    p.add_argument("--embed-urls", type=Path, required=True)
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--force", action="store_true",
                   help="Regenerate the whole explorer.html from the template even if one exists "
                        "(WARNING: discards any non-template content such as a V5/hero layout).")
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

    # Greenfield (or explicit --force): full template render.
    if a.force or not out.exists():
        out.write_text(render(repo, embed_url), encoding="utf-8")
        state = "(live embed)" if embed_url else "(pending)"
        how = "force-regenerated" if (a.force and out.exists()) else "created"
        print(f"{repo_name}: explorer.html {state} {how} -> {out}")
        return 0

    # Additive path: an explorer.html already exists — never clobber it.
    existing = out.read_text(encoding="utf-8", errors="replace")
    if not embed_url:
        had = bool(CLOUD_URL_RE.search(existing) or DATA_SLOT_RE.search(existing))
        print(f"{repo_name}: no fresh cloud URL; kept existing explorer.html "
              f"({'live embed preserved' if had else 'unchanged'}).")
        return 0

    patched, n = patch_embed(existing, embed_url)
    if n == 0:
        # Existing explorer has no recognizable embed slot to patch. Don't guess —
        # leave it untouched and tell the operator how to opt into a full render.
        print(f"{repo_name}: existing explorer.html has no Wolfram embed slot to patch; "
              f"left unchanged. Re-run with --force to regenerate from the template.")
        return 0
    if patched != existing:
        out.write_text(patched, encoding="utf-8")
        print(f"{repo_name}: patched live Wolfram URL in place ({n} ref(s)) -> {out}")
    else:
        print(f"{repo_name}: live Wolfram URL already current; no change.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
