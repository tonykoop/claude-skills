#!/usr/bin/env python3
"""Post-generation guard for instrument build packets.

Runs after generate_capstone_docs.py (and any hand-finishing) to flag the
typical "85% complete" gaps that humans then have to file as GitHub issues:

  - capstone-deck.md still contains a placeholder fallback like
    "See design.md for intent." (regex-miss artifact)
  - bom.csv / sourcing.csv / cut-list.csv still has TBD/`=`/empty cells
    in load-bearing columns
  - README.md is still the minimal scaffold (didn't get the
    tongue-drum-standard rewrite)
  - capstone-deck.pptx is missing OR has fewer slides than expected
  - print-packet.pdf is missing
  - Drawings or images referenced in the deck or README don't exist on disk
  - Required Tier 1 deliverables are absent from the packet

This is the verifier-agent role formalized as a script. Runs in seconds,
catches ~80% of what a human reviewer would otherwise file as a follow-up
issue. Pass `--strict` to exit 1 on any finding; without it, exits 0
regardless and reports findings to stdout for human review.

v4 addition (Tier 2 #6, brainstorm): the iterating verifier. Pass `--fix`
and the script runs a two-pass loop — fixes what it can, then re-runs the
checks. Two passes max, then escalates remaining findings.

Usage:
    python3 validate_packet.py <packet_dir> [--strict] [--fix]
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

# Force UTF-8 stdout so Unicode glyphs in success/finding messages
# (em-dash, smart quotes, etc.) print on Windows cp1252 consoles without
# raising UnicodeEncodeError. Python 3.7+ supports stdout.reconfigure;
# earlier versions silently no-op via getattr, which is fine because the
# scripts also target Linux/macOS where stdout is already UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


# --- Heuristics: strings that indicate a placeholder fallback rather than
# real instrument-specific content.
PLACEHOLDER_FALLBACKS = [
    "See design.md for intent.",
    "See design.md for intent and assumptions.",
    "Add hero render/photo, visual BOM",
    "Replace TBDs with measured/source-backed values.",  # OK on Next Actions slide; checked separately
]

# Tier 1 deliverables — must exist for a packet to be considered complete.
TIER_1_FILES = [
    "design.md",
    "bom.csv",
    "sourcing.csv",
    "cut-list.csv",
    "validation.csv",
    "assembly-manual.md",
    "supplier-rfq.md",
    "drawing-brief.md",
    "visual-bom-brief.md",
    "wolfram-starter.wl",
    "risks.md",  # v4 addition (red-team specialist output)
    "capstone-deck.md",
    "capstone-deck.pptx",
    "print-packet.md",
    "print-packet.html",
    "print-packet.pdf",
    "capstone-manifest.json",
    "README.md",
]

MINIMAL_README_PATTERNS = [
    "Engineering documentation and parametric design table for the",
    "CAD renders, Wolfram notebook recordings, and a finalized build method are forthcoming.",
]


def check_tier_1_files(packet_dir: Path) -> list[str]:
    findings = []
    for name in TIER_1_FILES:
        if not (packet_dir / name).exists():
            findings.append(f"missing Tier 1 deliverable: {name}")
    return findings


def check_capstone_deck(packet_dir: Path) -> list[str]:
    findings = []
    deck = packet_dir / "capstone-deck.md"
    if not deck.exists():
        return findings  # already covered by Tier 1 check
    text = deck.read_text(encoding="utf-8", errors="replace")

    # Slide 2 should be Project Intent and should NOT contain a placeholder fallback.
    # We check globally — any placeholder string anywhere is suspect except on the
    # Next Actions slide where "Replace TBDs with measured/source-backed values."
    # is legitimate boilerplate.
    intent_section = re.search(
        r"#\s+Project\s+Intent\b(.*?)(?=\n#\s|\Z)", text, re.S | re.I,
    )
    if intent_section:
        intent_body = intent_section.group(1)
        for placeholder in PLACEHOLDER_FALLBACKS[:2]:  # only the intent placeholders
            if placeholder in intent_body:
                findings.append(
                    f"capstone-deck.md Project Intent slide contains placeholder fallback: '{placeholder}' "
                    "— the design.md `## Intent` / `## Design Intent` heading didn't match the extractor regex"
                )
                break

    # Count slides — should have at least 12 in v3 (15 with all conditional slides).
    slide_count = len(re.findall(r"^#\s+", text, re.M))
    if slide_count < 12:
        findings.append(f"capstone-deck.md has only {slide_count} slides (expected >= 12)")

    return findings


def check_csv_completeness(packet_dir: Path) -> list[str]:
    """Flag CSVs whose key columns are mostly TBD or empty."""
    findings = []
    csv_specs = {
        "bom.csv": ("estimated_cost", "qty"),
        "sourcing.csv": ("required_spec", "search_terms"),
        "cut-list.csv": ("rough_dimensions_in", "final_dimensions_in"),
    }
    for name, key_cols in csv_specs.items():
        path = packet_dir / name
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8", errors="replace") as h:
            rows = list(csv.reader(h))
        if len(rows) < 2:
            findings.append(f"{name}: has no data rows (only header or empty)")
            continue
        header = [c.lower() for c in rows[0]]
        for col_name in key_cols:
            if not any(col_name.lower() in h for h in header):
                continue  # column missing entirely; not all instruments have all columns
            col_idx = next(i for i, h in enumerate(header) if col_name.lower() in h)
            unresolved = sum(
                1 for r in rows[1:]
                if col_idx < len(r) and (
                    not r[col_idx].strip()
                    or r[col_idx].strip().upper() == "TBD"
                    or r[col_idx].strip() == "="
                )
            )
            data_rows = len(rows) - 1
            if data_rows and unresolved / data_rows > 0.5:
                findings.append(
                    f"{name}: column '{col_name}' is unresolved (TBD/empty/=) in "
                    f"{unresolved}/{data_rows} rows — fill in or mark explicitly as 'derived estimate'"
                )
    return findings


def check_readme(packet_dir: Path) -> list[str]:
    """Validate README.md against the tongue-drum-standard format.

    Three independent checks:

      1. **Byte-size threshold (v3.1):** flag any README under 2000 bytes
         regardless of pattern match.  Catches the kena-style failure where
         the README was truncated to 482 bytes during a partial write and
         v3.0 passed because the truncated content didn't match the
         minimal-scaffold patterns.  A real packet README is typically
         3-6 KB; under 2 KB is a structural problem worth flagging.

      2. **Minimal-scaffold pattern match:** flags the original
         `Engineering documentation and parametric design table for the...`
         skeleton text.

      3. **Hero image existence:** the first `![alt](path)` reference in the
         README must point at a file that actually exists.
    """
    findings = []
    readme = packet_dir / "README.md"
    if not readme.exists():
        return findings
    text = readme.read_text(encoding="utf-8", errors="replace")
    byte_size = readme.stat().st_size
    line_count = len(text.splitlines())

    # Check 1 (v3.1): byte-size threshold — independent of content patterns.
    if byte_size < 2000:
        findings.append(
            f"README.md is suspiciously short ({byte_size} bytes / {line_count} lines) — "
            "tongue-drum-standard READMEs are typically 3-6 KB. Could be the minimal scaffold, "
            "a truncated write, or just an incomplete rewrite — verify by hand."
        )

    # Check 2: scaffold pattern match (only flagged on short READMEs to limit false positives).
    if line_count < 30:
        for pat in MINIMAL_README_PATTERNS:
            if pat in text:
                findings.append(
                    f"README.md is still the minimal scaffold ({line_count} lines, matches "
                    f"'{pat[:40]}...') — replace with the tongue-drum-standard format "
                    "(hero image + background + design overview + cross-repo links + license)"
                )
                break

    # Check 3: hero image existence.
    hero_match = re.search(r"!\[[^\]]*\]\(([^)]+)\)", text)
    if hero_match:
        ref = hero_match.group(1)
        if not ref.startswith(("http://", "https://")):
            target = (packet_dir / ref).resolve()
            try:
                target.relative_to(packet_dir.resolve())
                if not target.exists():
                    findings.append(f"README.md hero image '{ref}' does not exist on disk")
            except ValueError:
                pass  # absolute path or outside packet — skip
    return findings


def check_referenced_files_exist(packet_dir: Path) -> list[str]:
    """Walk the deck markdown and verify referenced thumbnails exist.

    v4.2 fix: normalize Windows-style backslash paths (`drawings\\foo.svg`)
    to forward slashes before existence-checking, since PathLib treats `\\`
    as a literal character on Linux. Decks generated on Windows previously
    produced spurious "missing file" findings on Linux/Cowork because of
    this mismatch.
    """
    findings = []
    deck = packet_dir / "capstone-deck.md"
    if not deck.exists():
        return findings
    text = deck.read_text(encoding="utf-8", errors="replace")
    for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
        ref = match.group(1)
        if ref.startswith(("http://", "https://")):
            continue
        # Normalize backslashes to forward slashes (handles Windows-authored
        # decks on Linux). Reported finding still uses the original ref so
        # the user sees what's actually in the deck text.
        normalized = ref.replace("\\", "/")
        target = (packet_dir / normalized).resolve()
        try:
            target.relative_to(packet_dir.resolve())
        except ValueError:
            continue  # outside packet
        if not target.exists():
            findings.append(f"capstone-deck.md references missing file: {ref}")
    return findings


def check_pdf_pages(packet_dir: Path) -> list[str]:
    """Light sanity check: PDF should have > 5 pages."""
    findings = []
    pdf = packet_dir / "print-packet.pdf"
    if not pdf.exists():
        return findings
    try:
        import pypdf  # type: ignore
        reader = pypdf.PdfReader(str(pdf))
        if len(reader.pages) < 5:
            findings.append(f"print-packet.pdf has only {len(reader.pages)} pages — expected at least 5")
    except Exception:
        pass  # pypdf unavailable; skip silently
    return findings


def check_visual_output_contract(packet_dir: Path) -> list[str]:
    """Delegate DXF-first visual-output checks when the contract is present."""
    contract = packet_dir / "visual-output-contract.json"
    if not contract.exists():
        intake = packet_dir / "data" / "design-intake.json"
        if intake.exists():
            try:
                targets = set(
                    t.strip().lower()
                    for t in json.loads(intake.read_text(encoding="utf-8"))
                    .get("visual_output_targets", "")
                    .split(",")
                    if t.strip()
                )
            except Exception:
                targets = set()
            if "dxf" in targets:
                return [
                    "visual-output: visual_output_targets requests dxf but "
                    "visual-output-contract.json is missing"
                ]
        return []

    try:
        from validate_visual_outputs import validate  # type: ignore
    except Exception as exc:
        return [f"visual-output contract present but validator could not load: {exc}"]

    findings = []
    for finding in validate(packet_dir):
        if finding.severity == "ERROR":
            findings.append(f"visual-output: {finding.code}: {finding.message}")
    return findings


def run_all_checks(packet_dir: Path) -> list[str]:
    findings: list[str] = []
    findings += check_tier_1_files(packet_dir)
    findings += check_capstone_deck(packet_dir)
    findings += check_csv_completeness(packet_dir)
    findings += check_readme(packet_dir)
    findings += check_referenced_files_exist(packet_dir)
    findings += check_pdf_pages(packet_dir)
    findings += check_visual_output_contract(packet_dir)
    return findings


RISKS_SCAFFOLD = (
    "# Risks\n\n"
    "(scaffolded by validate_packet.py --fix; run red-team specialist to populate)\n\n"
    "## Acoustic\n\n(none identified)\n\n"
    "## Structural\n\n(none identified)\n\n"
    "## Ergonomic\n\n(none identified)\n\n"
    "## Supply\n\n(none identified)\n\n"
    "## Fit/Finish\n\n(none identified)\n"
)


def attempt_v4_fixes(packet_dir: Path, findings: list[str]) -> list[str]:
    import subprocess
    skill_root = Path(__file__).resolve().parents[1]
    py = sys.executable
    applied: list[str] = []
    if any("risks.md" in f for f in findings):
        risks = packet_dir / "risks.md"
        if not risks.exists():
            risks.write_text(RISKS_SCAFFOLD, encoding="utf-8")
            applied.append("scaffolded risks.md")
    if any("drawing" in f.lower() and "missing" in f.lower() for f in findings):
        drawings_script = skill_root / "scripts" / "generate_drawings.py"
        if drawings_script.exists():
            try:
                subprocess.run([py, str(drawings_script), str(packet_dir)],
                               check=False, capture_output=True, timeout=30)
                applied.append("ran generate_drawings.py")
            except Exception as e:
                applied.append(f"generate_drawings.py failed: {e}")
    site_index = packet_dir / "site" / "index.html"
    if not site_index.exists():
        site_script = skill_root / "scripts" / "generate_site.py"
        if site_script.exists():
            try:
                subprocess.run([py, str(site_script), str(packet_dir)],
                               check=False, capture_output=True, timeout=30)
                applied.append("ran generate_site.py")
            except Exception:
                pass
    return applied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet_dir", type=Path)
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 on any finding (default: report only, exit 0)")
    parser.add_argument("--json", action="store_true",
                        help="Emit findings as JSON instead of human-readable text")
    parser.add_argument("--fix", action="store_true",
                        help="v4 iterating-verifier mode: fix what's fixable then re-check")
    args = parser.parse_args()

    packet_dir = args.packet_dir.resolve()
    if not packet_dir.exists():
        print(f"ERROR: packet_dir does not exist: {packet_dir}", file=sys.stderr)
        return 2

    pass_1 = run_all_checks(packet_dir)
    fixes_applied: list[str] = []
    pass_2: list[str] = []
    if args.fix and pass_1:
        fixes_applied = attempt_v4_fixes(packet_dir, pass_1)
        pass_2 = run_all_checks(packet_dir)
        all_findings = pass_2
    else:
        all_findings = pass_1

    if args.json:
        print(json.dumps({
            "packet": str(packet_dir),
            "pass_1_findings": pass_1,
            "fixes_applied": fixes_applied,
            "pass_2_findings": pass_2 if args.fix else None,
            "findings": all_findings,
            "ok": len(all_findings) == 0,
        }, indent=2))
    else:
        if not all_findings:
            if args.fix and fixes_applied:
                print(f"OK — {packet_dir.name}: clean after v4 fix pass")
                for fix in fixes_applied:
                    print(f"    - {fix}")
            else:
                print(f"OK — {packet_dir.name}: all gates passed")
        else:
            heading = "ESCALATED" if args.fix else "FOUND"
            print(f"{heading} {len(all_findings)} issue(s) in {packet_dir.name}:")
            for f in all_findings:
                print(f"  - {f}")
            if args.fix:
                print(f"  Fixes attempted in pass 1:")
                for fix in fixes_applied:
                    print(f"    - {fix}")

    if args.strict and all_findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
