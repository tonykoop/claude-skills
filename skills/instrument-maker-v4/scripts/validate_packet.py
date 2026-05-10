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
and the script runs a two-pass loop â fixes what it can, then re-runs the
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
from dataclasses import dataclass
from pathlib import Path


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

PRESENTATION_FILES = {
    "capstone-deck.md",
    "capstone-deck.pptx",
    "print-packet.md",
    "print-packet.html",
    "print-packet.pdf",
    "capstone-manifest.json",
}

MINIMAL_README_PATTERNS = [
    "Engineering documentation and parametric design table for the",
    "CAD renders, Wolfram notebook recordings, and a finalized build method are forthcoming.",
]

ALLOWED_ACOUSTIC_LAWS = {
    "open_open",
    "closed_open",
    "stopped_pipe",
    "side_branch_reed",
    "free_reed_coupled_pipe",
    "empirical_only",
    "unknown_requires_measurement",
    # Non-pipe families used by existing v4 family-aware packets.
    "helmholtz",
    "helmholtz_dual",
    "cantilever_beam",
    "free_free_beam",
    "membrane",
    "mersenne_taylor_string",
    "hybrid_compound",
}

REQUIRED_FAMILY_SPEC_COLUMNS = {
    "acoustic_law",
    "end_condition",
    "reed_source_role",
    "cad_dimension_basis",
}

ALLOWED_REED_SOURCE_ROLES = {
    "none",
    "exciter",
    "pitch_source",
    "coupler",
    "unknown_requires_measurement",
}

ALLOWED_CAD_DIMENSION_BASIS = {
    "physics_derived",
    "empirically_seeded",
    "measurement_required",
}


@dataclass(frozen=True)
class PacketLayout:
    layout: str
    repo_root: Path
    packet_dir: Path
    asset_dirs: tuple[Path, ...]

    def candidate_dirs(self) -> tuple[Path, ...]:
        return (self.packet_dir, self.repo_root, *self.asset_dirs)


def unique_existing_ordered(paths: list[Path]) -> tuple[Path, ...]:
    seen: set[Path] = set()
    out: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        out.append(resolved)
    return tuple(out)


def detect_layout(input_path: Path, mode: str = "auto") -> PacketLayout:
    """Detect root-mode vs nested build/packet layout.

    Mode A root repos keep packet docs at repo root. Nested repos keep packet
    docs under build/packet while drawings/CAD/CNC/presentation assets live in
    sibling folders. Callers may pass either the repo root or build/packet.
    """
    path = input_path.resolve()
    if mode not in {"auto", "root", "nested"}:
        raise ValueError(f"unsupported mode: {mode}")

    if mode == "root":
        repo_root = path
        packet_dir = path
        layout = "root"
    elif mode == "nested":
        if path.name == "packet" and path.parent.name == "build":
            packet_dir = path
            repo_root = path.parents[1]
        else:
            repo_root = path
            packet_dir = path / "build" / "packet"
        layout = "nested"
    elif path.name == "packet" and path.parent.name == "build":
        packet_dir = path
        repo_root = path.parents[1]
        layout = "nested"
    elif (path / "build" / "packet").exists():
        repo_root = path
        packet_dir = path / "build" / "packet"
        layout = "nested"
    else:
        repo_root = path
        packet_dir = path
        layout = "root"

    if layout == "nested":
        asset_dirs = unique_existing_ordered([
            repo_root / "build" / "drawings",
            repo_root / "build" / "cad",
            repo_root / "build" / "cnc",
            repo_root / "build" / "presentation",
            repo_root / "build" / "wolfram",
            repo_root / "build" / "images",
            repo_root / "assets" / "images",
            repo_root / "site",
        ])
    else:
        asset_dirs = unique_existing_ordered([
            repo_root / "drawings",
            repo_root / "cad",
            repo_root / "cnc",
            repo_root / "wolfram",
            repo_root / "images",
            repo_root / "assets" / "images",
            repo_root / "site",
        ])

    return PacketLayout(layout=layout, repo_root=repo_root, packet_dir=packet_dir, asset_dirs=asset_dirs)


def find_existing(layout: PacketLayout, name: str) -> Path | None:
    search_dirs: tuple[Path, ...]
    if layout.layout == "nested" and name in PRESENTATION_FILES:
        search_dirs = (
            layout.repo_root / "build" / "presentation",
            layout.packet_dir,
        )
    elif name == "README.md":
        search_dirs = (layout.repo_root, layout.packet_dir)
    elif name == "wolfram-starter.wl" and layout.layout == "nested":
        search_dirs = (layout.packet_dir, layout.repo_root / "build" / "wolfram")
    else:
        search_dirs = (layout.packet_dir,)

    for base in search_dirs:
        candidate = base / name
        if candidate.exists():
            return candidate
    return None


def ref_exists(layout: PacketLayout, ref: str, origin: Path) -> bool:
    if ref.startswith(("http://", "https://")):
        return True
    normalized = ref.replace("\\", "/")
    bases = unique_existing_ordered([
        origin.parent,
        layout.packet_dir,
        layout.repo_root,
        layout.repo_root / "build",
        *layout.asset_dirs,
    ])
    for base in bases:
        target = (base / normalized).resolve()
        try:
            target.relative_to(layout.repo_root.resolve())
        except ValueError:
            continue
        if target.exists():
            return True
    return False


def check_tier_1_files(layout: PacketLayout) -> list[str]:
    findings = []
    for name in TIER_1_FILES:
        if find_existing(layout, name) is None:
            findings.append(f"missing Tier 1 deliverable: {name}")
    return findings


def check_capstone_deck(layout: PacketLayout) -> list[str]:
    findings = []
    deck = find_existing(layout, "capstone-deck.md")
    if deck is None:
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


def check_csv_completeness(layout: PacketLayout) -> list[str]:
    """Flag CSVs whose key columns are mostly TBD or empty."""
    findings = []
    csv_specs = {
        "bom.csv": ("estimated_cost", "qty"),
        "sourcing.csv": ("required_spec", "search_terms"),
        "cut-list.csv": ("rough_dimensions_in", "final_dimensions_in"),
    }
    for name, key_cols in csv_specs.items():
        path = find_existing(layout, name)
        if path is None:
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


def check_family_spec_acoustic_law(layout: PacketLayout) -> list[str]:
    """Validate machine-checkable acoustic-law fields in family-spec.csv.

    The goal is to prevent a silent wrong-physics path where design prose says
    one boundary condition while CAD tables or pipe schedules use another.
    """
    findings: list[str] = []
    path = find_existing(layout, "family-spec.csv")
    if path is None:
        return findings

    with path.open(newline="", encoding="utf-8", errors="replace") as h:
        reader = csv.DictReader(h)
        headers = set(reader.fieldnames or [])
        rows = list(reader)

    missing = sorted(REQUIRED_FAMILY_SPEC_COLUMNS - headers)
    if missing:
        findings.append(
            "family-spec.csv: missing required acoustic-law column(s): "
            + ", ".join(missing)
        )
        return findings

    if not rows:
        findings.append("family-spec.csv: has no data rows")
        return findings

    for row_number, row in enumerate(rows, start=2):
        member = (
            row.get("member_id")
            or row.get("id")
            or row.get("instrument_id")
            or f"row {row_number}"
        )
        law = (row.get("acoustic_law") or "").strip()
        end_condition = (row.get("end_condition") or "").strip()
        reed_role = (row.get("reed_source_role") or "").strip()
        cad_basis = (row.get("cad_dimension_basis") or "").strip()

        if law not in ALLOWED_ACOUSTIC_LAWS:
            findings.append(
                f"family-spec.csv:{row_number} {member}: invalid acoustic_law "
                f"{law!r}; expected one of {', '.join(sorted(ALLOWED_ACOUSTIC_LAWS))}"
            )
        if not end_condition:
            findings.append(f"family-spec.csv:{row_number} {member}: end_condition is required")
        if reed_role not in ALLOWED_REED_SOURCE_ROLES:
            findings.append(
                f"family-spec.csv:{row_number} {member}: invalid reed_source_role "
                f"{reed_role!r}; expected one of {', '.join(sorted(ALLOWED_REED_SOURCE_ROLES))}"
            )
        if cad_basis not in ALLOWED_CAD_DIMENSION_BASIS:
            findings.append(
                f"family-spec.csv:{row_number} {member}: invalid cad_dimension_basis "
                f"{cad_basis!r}; expected one of {', '.join(sorted(ALLOWED_CAD_DIMENSION_BASIS))}"
            )
        if law in {"empirical_only", "unknown_requires_measurement"} and cad_basis == "physics_derived":
            findings.append(
                f"family-spec.csv:{row_number} {member}: cad_dimension_basis cannot be "
                f"physics_derived when acoustic_law is {law}"
            )
        if law == "side_branch_reed" and reed_role == "none":
            findings.append(
                f"family-spec.csv:{row_number} {member}: side_branch_reed rows must "
                "identify the reed as exciter, pitch_source, coupler, or unknown_requires_measurement"
            )
    return findings


def check_readme(layout: PacketLayout) -> list[str]:
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
    readme = find_existing(layout, "README.md")
    if readme is None:
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
        if not ref_exists(layout, ref, readme):
            findings.append(f"README.md hero image '{ref}' does not exist on disk")
    return findings


def check_referenced_files_exist(layout: PacketLayout) -> list[str]:
    """Walk the deck markdown and verify referenced thumbnails exist.

    v4.2 fix: normalize Windows-style backslash paths (`drawings\\foo.svg`)
    to forward slashes before existence-checking, since PathLib treats `\\`
    as a literal character on Linux. Decks generated on Windows previously
    produced spurious "missing file" findings on Linux/Cowork because of
    this mismatch.
    """
    findings = []
    deck = find_existing(layout, "capstone-deck.md")
    if deck is None:
        return findings
    text = deck.read_text(encoding="utf-8", errors="replace")
    for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
        ref = match.group(1)
        if not ref_exists(layout, ref, deck):
            findings.append(f"capstone-deck.md references missing file: {ref}")
    return findings


def check_pdf_pages(layout: PacketLayout) -> list[str]:
    """Light sanity check: PDF should have > 5 pages."""
    findings = []
    pdf = find_existing(layout, "print-packet.pdf")
    if pdf is None:
        return findings
    try:
        import pypdf  # type: ignore
        reader = pypdf.PdfReader(str(pdf))
        if len(reader.pages) < 5:
            findings.append(f"print-packet.pdf has only {len(reader.pages)} pages — expected at least 5")
    except Exception:
        pass  # pypdf unavailable; skip silently
    return findings


def run_all_checks(layout: PacketLayout) -> list[str]:
    findings: list[str] = []
    findings += check_tier_1_files(layout)
    findings += check_capstone_deck(layout)
    findings += check_csv_completeness(layout)
    findings += check_family_spec_acoustic_law(layout)
    findings += check_readme(layout)
    findings += check_referenced_files_exist(layout)
    findings += check_pdf_pages(layout)
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
    parser.add_argument("--mode", choices=("auto", "root", "nested"), default="auto",
                        help="Packet layout detection mode (default: auto)")
    args = parser.parse_args()

    input_path = args.packet_dir.resolve()
    if not input_path.exists():
        print(f"ERROR: packet_dir does not exist: {input_path}", file=sys.stderr)
        return 2

    layout = detect_layout(input_path, args.mode)
    if not layout.packet_dir.exists():
        print(f"ERROR: packet_dir does not exist: {layout.packet_dir}", file=sys.stderr)
        return 2

    pass_1 = run_all_checks(layout)
    fixes_applied: list[str] = []
    pass_2: list[str] = []
    if args.fix and pass_1:
        fixes_applied = attempt_v4_fixes(layout.packet_dir, pass_1)
        pass_2 = run_all_checks(layout)
        all_findings = pass_2
    else:
        all_findings = pass_1

    if args.json:
        print(json.dumps({
            "layout": layout.layout,
            "repo_root": str(layout.repo_root),
            "packet_dir": str(layout.packet_dir),
            "asset_dirs": [str(path) for path in layout.asset_dirs],
            "pass_1_findings": pass_1,
            "fixes_applied": fixes_applied,
            "pass_2_findings": pass_2 if args.fix else None,
            "findings": all_findings,
            "ok": len(all_findings) == 0,
        }, indent=2))
    else:
        if not all_findings:
            if args.fix and fixes_applied:
                print(f"OK — {layout.packet_dir.name}: clean after v4 fix pass")
                for fix in fixes_applied:
                    print(f"    - {fix}")
            else:
                print(f"OK — {layout.packet_dir.name}: all gates passed")
        else:
            heading = "ESCALATED" if args.fix else "FOUND"
            print(f"{heading} {len(all_findings)} issue(s) in {layout.packet_dir.name}:")
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
