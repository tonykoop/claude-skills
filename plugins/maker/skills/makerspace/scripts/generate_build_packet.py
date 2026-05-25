#!/usr/bin/env python3
"""
generate_build_packet.py
========================

Generate a tier-aware build packet scaffold for a project.

This script writes the *scaffold* — file skeletons with frontmatter,
section headers, and TBDs in the right places. The actual design
content is filled in by the orchestrator + specialists during a
session, not by this script.

Usage:
    # Tier 1 (shop-ready)
    python3 scripts/generate_build_packet.py \\
        --project ./projects/cnc-welcome-sign \\
        --space maker-nexus \\
        --tier 1 \\
        --name "CNC Welcome Sign"

    # Tier 2 (portfolio-ready)
    python3 scripts/generate_build_packet.py \\
        --project ./projects/canoe-paddle \\
        --space home-shop-default \\
        --tier 2 \\
        --name "Steam-bent ash canoe paddle"

    # Tier 3 (capstone-ready)
    python3 scripts/generate_build_packet.py \\
        --project ./projects/lazy-susan \\
        --space maker-nexus \\
        --tier 3 \\
        --name "Hexagonal lazy susan"
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from textwrap import dedent


# ─────────────────── Tier file lists ──────────────────────────

TIER_1_FILES = [
    "design.md",
    "bom.csv",
    "cut-list.csv",
    "op-sequence.md",
    "safety-notes.md",
]

TIER_2_FILES = TIER_1_FILES + [
    "drawings/.gitkeep",
    "drawing-brief.md",
    "assembly-manual.md",
    "sourcing.csv",
    "validation.csv",
    "risks.md",
    "README.md",
    "images/.gitkeep",
    "cad/.gitkeep",
    "cnc/.gitkeep",
    "data/.gitkeep",
]

TIER_3_FILES = TIER_2_FILES + [
    "deck.pptx.placeholder",   # Replaced by build_deck.py / pptx skill
    "print-packet.pdf.placeholder",
    "site/index.html",
    "photo-shotlist.md",
]


# ─────────────────── Templates ─────────────────────────────────

DESIGN_MD = """\
# {name}

## Parameters
| Name | Symbol | Value | Unit | Source |
|------|--------|-------|------|--------|
| TBD | TBD | TBD | TBD | input |

## Critical dimensions
- TBD

## Derived dimensions
- TBD = formula(parameters)

## Open questions
- TBD

## Notes
- Generated {today} for `{space}`. Tier {tier}.
"""

BOM_CSV = """\
item_id,item_name,qty,unit,vendor,sku,unit_cost_usd,line_cost_usd,lead_time_days,notes
b001,TBD,1,each,TBD,TBD,TBD,TBD,0,
"""

CUT_LIST_CSV = """\
part_id,part_name,qty,material,stock_id,length_in,width_in,thickness_in,grain_dir,kerf_in,notes
p001,TBD,1,TBD,b001,TBD,TBD,TBD,length,0.0625,
"""

OP_SEQUENCE_MD = """\
# Operation sequence — {name}

## Space: {space}
## Tier: {tier}
## User certs claimed: TBD
## Estimated total shop time: TBD

## Feasibility summary
- TBD

## Operations
1. **Op 1 — TBD** [tool: TBD, time: ~TBD]
   - Material: TBD
   - Fixture: TBD
   - Tooling: TBD
   - Cleared on this tool: TBD
   - Go/no-go check before proceeding: TBD

## Prep checklist (before shop time)
- T-Nd: TBD

## Open questions
- TBD
"""

SAFETY_NOTES_MD = """\
# Safety notes — {name}

## PPE for this build
- TBD

## Tool-specific risks
- TBD

## Material-specific risks
- TBD

## Process-specific risks
- TBD

## Emergency / fire / fume notes
- TBD
"""

DRAWING_BRIEF_MD = """\
# Drawing brief — {name}

## Views needed
- TBD

## Critical dimensions
- TBD

## Datums
- TBD

## Tolerances
- General ±TBD
- Critical ±TBD

## Material/finish callouts
- Material: TBD
- Finish: TBD
- Edge treatment: TBD

## Tool/access notes
- TBD
"""

ASSEMBLY_MANUAL_MD = """\
# Assembly manual — {name}

## Estimated total time: TBD
## Tools needed: TBD
## Materials at this stage: TBD

### Step 1 — TBD
- **What you're doing:** TBD
- **Tool:** TBD
- **Time:** TBD
- **Photo placeholder:** `images/step-01-tbd.jpg`
- **Watch for:** TBD
"""

SOURCING_CSV = """\
item_id,primary_vendor,primary_url,primary_unit_cost_usd,alt_vendor,alt_url,alt_unit_cost_usd,lead_time_days,shipping_usd,rfq_sent,rfq_quoted,notes
b001,TBD,TBD,TBD,TBD,TBD,TBD,0,TBD,false,false,
"""

VALIDATION_CSV = """\
check_id,check_name,target,tolerance,method,when_to_check,pass_fail,notes
v001,TBD,TBD,TBD,TBD,TBD,pending,
"""

RISKS_MD = """\
# Risks — {name}

For each risk: severity (low/med/high), description, root cause,
mitigation, *test* (how you verify the mitigation worked).

## High severity
(none yet)

## Medium severity
(none yet)

## Low severity
(none yet)

## Risks considered and dismissed
- TBD
"""

README_MD = """\
# {name}

> One-sentence pitch — TBD.

## Hero image
![hero](images/hero.jpg)  *(placeholder — TBD)*

## What it is
TBD

## Where it was built
{space}

## Tools and certifications
- TBD

## Quick file map
- `design.md` — parametric design
- `bom.csv` — bill of materials
- `cut-list.csv` — cut layout
- `op-sequence.md` — manufacturing sequence
- `assembly-manual.md` — step-by-step build
- `validation.csv` — how to verify it came out right
- `risks.md` — known failure modes + mitigations
- `drawings/` — dimensioned drawings
- `images/` — process and finished photos

## License
MIT (or your choice).
"""

PHOTO_SHOTLIST_MD = """\
# Photo shotlist — {name}

## Hero (one)
- Finished piece in context, raking light, golden hour OK.
- Filename target: `images/hero.jpg`

## Process (5-10)
- TBD: `images/process-01-tbd.jpg`

## Detail (3-5)
- TBD: `images/detail-01-tbd.jpg`

## Maker (1, optional)
- Maker holding finished piece: `images/maker-portrait.jpg`
"""

SITE_INDEX_HTML = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name}</title>
<style>
  :root {{ --fg: #111; --bg: #fff; --muted: #666; --link: #0044cc; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
          Roboto, sans-serif; max-width: 720px; margin: 2rem auto;
          padding: 0 1rem; color: var(--fg); background: var(--bg);
          line-height: 1.6; }}
  header {{ margin-bottom: 2rem; }}
  h1 {{ margin: 0; }}
  .meta {{ color: var(--muted); }}
  img {{ max-width: 100%; height: auto; }}
  a {{ color: var(--link); }}
  section {{ margin-bottom: 2rem; }}
</style>
</head>
<body>
<header>
  <h1>{name}</h1>
  <p class="meta">Built at {space} · {today}</p>
  <img src="images/hero.jpg" alt="Hero image — TBD">
</header>

<section id="intent">
  <h2>What this is</h2>
  <p>TBD</p>
</section>

<section id="workflow">
  <h2>Build workflow</h2>
  <p>TBD</p>
</section>

<section id="finished">
  <h2>Final piece</h2>
  <p>TBD</p>
</section>

<section id="links">
  <h2>Links</h2>
  <ul>
    <li><a href="../README.md">Project README</a></li>
    <li><a href="../print-packet.pdf">Printable shop packet (PDF)</a></li>
    <li><a href="../deck.pptx">Capstone slide deck (.pptx)</a></li>
  </ul>
</section>

<footer>
  <p class="meta">MIT licensed. Generated by the makerspace skill.</p>
</footer>
</body>
</html>
"""


TEMPLATES = {
    "design.md": DESIGN_MD,
    "bom.csv": BOM_CSV,
    "cut-list.csv": CUT_LIST_CSV,
    "op-sequence.md": OP_SEQUENCE_MD,
    "safety-notes.md": SAFETY_NOTES_MD,
    "drawing-brief.md": DRAWING_BRIEF_MD,
    "assembly-manual.md": ASSEMBLY_MANUAL_MD,
    "sourcing.csv": SOURCING_CSV,
    "validation.csv": VALIDATION_CSV,
    "risks.md": RISKS_MD,
    "README.md": README_MD,
    "photo-shotlist.md": PHOTO_SHOTLIST_MD,
    "site/index.html": SITE_INDEX_HTML,
}


# ─────────────────── Main ─────────────────────────────────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate a tier-aware build packet scaffold.",
    )
    p.add_argument(
        "--project",
        type=Path,
        required=True,
        help="Project directory to write into (created if missing).",
    )
    p.add_argument(
        "--space",
        default="home-shop-default",
        help="Space slug (default: home-shop-default).",
    )
    p.add_argument(
        "--tier",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help="Polish tier (1: shop-ready, 2: portfolio, 3: capstone).",
    )
    p.add_argument(
        "--name",
        default="Untitled project",
        help="Human-readable project name.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write files; print what would be created.",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite files that already exist.",
    )
    return p.parse_args(argv)


def files_for_tier(tier: int) -> list[str]:
    return {1: TIER_1_FILES, 2: TIER_2_FILES, 3: TIER_3_FILES}[tier]


def write_file(
    path: Path,
    content: str,
    *,
    force: bool,
    dry_run: bool,
) -> str:
    """Write content to path, returning a status string."""
    if path.exists() and not force:
        return f"skip   (exists): {path}"
    if dry_run:
        return f"dry    (would write {len(content)} bytes): {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return f"wrote  {len(content):>5} bytes: {path}"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project = args.project.resolve()
    today = date.today().isoformat()

    fmt_kwargs = {
        "name": args.name,
        "space": args.space,
        "tier": args.tier,
        "today": today,
    }

    print(f"Generating Tier {args.tier} packet for: {args.name}")
    print(f"  Project dir: {project}")
    print(f"  Space:       {args.space}")
    print(f"  Mode:        {'DRY RUN' if args.dry_run else 'write'}")
    print()

    for rel in files_for_tier(args.tier):
        rel_path = project / rel
        if rel.endswith(".gitkeep"):
            status = write_file(
                rel_path, "", force=args.force, dry_run=args.dry_run,
            )
        elif rel.endswith(".placeholder"):
            content = dedent(
                f"""\
                Placeholder for {rel.replace('.placeholder', '')}.

                Tier 3 deliverables: replace this file with the actual
                .pptx (capstone deck) or .pdf (printable shop packet)
                produced by the documentarian specialist or the
                build_deck.py / build_print_packet.py scripts (when
                they ship).
                """
            )
            status = write_file(
                rel_path, content,
                force=args.force, dry_run=args.dry_run,
            )
        elif rel in TEMPLATES:
            content = TEMPLATES[rel].format(**fmt_kwargs)
            status = write_file(
                rel_path, content,
                force=args.force, dry_run=args.dry_run,
            )
        else:
            status = f"skip   (no template): {rel_path}"
        print(f"  {status}")

    print()
    print(
        f"Done. Open {project}/README.md (or design.md for Tier 1) "
        f"and start filling in the TBDs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
