#!/usr/bin/env python3
"""Grade iteration-N outputs against eval assertions.

Usage:
    python3 grade_iteration.py iteration-1
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


# ─────────── Per-eval assertion logic ───────────

# Tier 2 file set
TIER_2_FILES = [
    "design.md", "bom.csv", "cut-list.csv", "op-sequence.md",
    "safety-notes.md", "assembly-manual.md", "sourcing.csv",
    "validation.csv", "risks.md", "README.md",
]

# Tier 1 file set
TIER_1_FILES = [
    "design.md", "bom.csv", "cut-list.csv", "op-sequence.md",
    "safety-notes.md",
]

# Tier 2/3-only files that should NOT be present in Tier 1 packet
TIER_2_PLUS_FILES = [
    "README.md", "drawings", "drawing-brief.md", "deck.pptx",
    "sourcing.csv", "validation.csv", "risks.md",
    "assembly-manual.md", "site",
]


def find_files(outputs_dir: Path) -> dict[str, Path]:
    """Map filename → absolute path for everything under outputs_dir."""
    found = {}
    if not outputs_dir.exists():
        return found
    for path in outputs_dir.rglob("*"):
        if path.is_file() or path.is_dir():
            name = path.name
            # Use first occurrence
            if name not in found:
                found[name] = path
    return found


def file_has(outputs_dir: Path, name: str) -> Path | None:
    """Find a file by name (or directory by name)."""
    if not outputs_dir.exists():
        return None
    for path in outputs_dir.rglob(name):
        return path
    return None


def read_text_safely(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except (OSError, UnicodeError):
        return ""


def read_all_text(outputs_dir: Path) -> str:
    """Concatenate the text of all .md/.csv/.txt files for combined search."""
    if not outputs_dir.exists():
        return ""
    bits = []
    for path in outputs_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".md", ".csv", ".txt", ".json", ".yaml", ".yml"}:
            bits.append(read_text_safely(path))
    return "\n".join(bits)


# ─────────── Eval-1 grader: maker-nexus-cnc-sign-tier-2 ───────────

def grade_eval_1(outputs_dir: Path) -> list[dict]:
    results = []
    found_files = set()
    if outputs_dir.exists():
        for p in outputs_dir.rglob("*"):
            if p.is_file():
                found_files.add(p.name)
            elif p.is_dir():
                found_files.add(p.name + "/")

    # 1. Tier 2 file set complete
    missing = [f for f in TIER_2_FILES if f not in found_files]
    results.append({
        "text": "Tier 2 file set complete: design.md, bom.csv, cut-list.csv, op-sequence.md, safety-notes.md, assembly-manual.md, sourcing.csv, validation.csv, risks.md, README.md all present",
        "passed": len(missing) == 0,
        "evidence": "all present" if not missing else f"missing: {missing}",
    })

    # 2. Drawing artifact present
    has_brief = "drawing-brief.md" in found_files
    drawings_dir = outputs_dir / "drawings"
    if not drawings_dir.exists():
        for p in (outputs_dir.rglob("drawings")):
            if p.is_dir():
                drawings_dir = p
                break
    has_drawings_dir = drawings_dir.exists() and any(drawings_dir.iterdir()) if drawings_dir.exists() else False
    # Also accept any svg/dxf/pdf drawings in any folder
    has_any_drawing = any(
        outputs_dir.rglob(ext) for ext in ["*.svg", "*.dxf"]
    ) if outputs_dir.exists() else False
    drawing_present = has_brief or has_drawings_dir or has_any_drawing
    evidence = []
    if has_brief: evidence.append("drawing-brief.md")
    if has_drawings_dir: evidence.append(f"drawings/ has files")
    if has_any_drawing and not has_drawings_dir: evidence.append("svg/dxf files present")
    results.append({
        "text": "Drawing artifact present: either drawing-brief.md or non-empty drawings/ directory",
        "passed": drawing_present,
        "evidence": ", ".join(evidence) if evidence else "no drawing artifact found",
    })

    # 3. design.md contains parametric formulas
    design_path = file_has(outputs_dir, "design.md")
    if design_path:
        text = read_text_safely(design_path)
        # Look for derivation patterns like "= 0.4 ×", "= W /", "= L *", "formula"
        has_formula = bool(
            re.search(r"=\s*[0-9.]+\s*[×*/+\-]", text) or
            re.search(r"=\s*[A-Za-z_]\w*\s*[×*/+\-]", text) or
            "formula" in text.lower() or
            "derived" in text.lower()
        )
        results.append({
            "text": "design.md contains parametric formulas (a `=` in a derivation, not just static numbers)",
            "passed": has_formula,
            "evidence": "found derivation patterns" if has_formula else "no formula patterns found in design.md",
        })
    else:
        results.append({
            "text": "design.md contains parametric formulas (a `=` in a derivation, not just static numbers)",
            "passed": False,
            "evidence": "design.md missing",
        })

    # 4. op-sequence.md does NOT cite laser ops
    op_path = file_has(outputs_dir, "op-sequence.md")
    if op_path:
        text = read_text_safely(op_path).lower()
        # negative regex: laser as a tool/op (not "no laser" or "without laser")
        has_laser_op = bool(
            re.search(r"\[tool:\s*laser", text) or
            re.search(r"\bop\s*\d.*?laser\b", text) or
            re.search(r"laser.cut|laser.engrav", text)
        )
        results.append({
            "text": "op-sequence.md does NOT cite laser ops (user is not laser-cleared)",
            "passed": not has_laser_op,
            "evidence": "no laser ops" if not has_laser_op else "laser operation referenced",
        })
    else:
        results.append({
            "text": "op-sequence.md does NOT cite laser ops",
            "passed": False,
            "evidence": "op-sequence.md missing",
        })

    # 5. BOM references baltic birch
    bom_path = file_has(outputs_dir, "bom.csv")
    if bom_path:
        text = read_text_safely(bom_path).lower()
        has_birch = "baltic birch" in text or "baltic-birch" in text or "birch" in text
        results.append({
            "text": "BOM references baltic birch (or similar plywood callout)",
            "passed": has_birch,
            "evidence": "found 'birch'" if has_birch else "no birch mention",
        })
    else:
        results.append({
            "text": "BOM references baltic birch",
            "passed": False,
            "evidence": "bom.csv missing",
        })

    # 6. README mentions Maker Nexus
    readme_path = file_has(outputs_dir, "README.md")
    if readme_path:
        text = read_text_safely(readme_path).lower()
        has_mn = "maker nexus" in text or "makernexus" in text
        results.append({
            "text": "README mentions Maker Nexus",
            "passed": has_mn,
            "evidence": "found 'maker nexus'" if has_mn else "no Maker Nexus mention",
        })
    else:
        results.append({
            "text": "README mentions Maker Nexus",
            "passed": False,
            "evidence": "README.md missing",
        })

    # 7. risks.md contains at least one *Test* line
    risks_path = file_has(outputs_dir, "risks.md")
    if risks_path:
        text = read_text_safely(risks_path)
        has_test = bool(re.search(r"\*\*Test:\*\*|^Test:|\bTest:\s+\w", text, re.MULTILINE))
        results.append({
            "text": "risks.md contains at least one *Test* line attached to a risk",
            "passed": has_test,
            "evidence": "found Test: line" if has_test else "no Test: lines found",
        })
    else:
        results.append({
            "text": "risks.md contains at least one *Test* line",
            "passed": False,
            "evidence": "risks.md missing",
        })

    return results


# ─────────── Eval-2 grader: canoe paddle cert gap ───────────

def grade_eval_2(outputs_dir: Path) -> list[dict]:
    results = []
    text = read_all_text(outputs_dir).lower()

    # 1. Addresses bandsaw cert gap
    has_gap = "bandsaw" in text and ("cert" in text or "clear" in text or "qualif" in text or "trained" in text or "class" in text)
    results.append({
        "text": "Response addresses the bandsaw cert gap explicitly",
        "passed": has_gap,
        "evidence": "mentions bandsaw + cert/class context" if has_gap else "no bandsaw+cert linkage",
    })

    # 2. Names the specific class
    has_class = bool(re.search(r"woodshop[\s-]?intro|intro\s+to\s+woodshop|woodshop[\s-]?cert|class-woodshop", text))
    # Baseline gets credit for naming a generic equivalent
    if not has_class:
        has_class = bool(re.search(r"bandsaw\s+(class|cert|orientation|training)", text))
    results.append({
        "text": "Response names the specific class that grants bandsaw access (woodshop-intro or equivalent)",
        "passed": has_class,
        "evidence": "named woodshop-intro / bandsaw class" if has_class else "no specific class named",
    })

    # 3. References class schedule URL
    has_url = "makernexus.org/classes" in text or "makernexus.org" in text
    results.append({
        "text": "Response references the Maker Nexus class schedule URL",
        "passed": has_url,
        "evidence": "URL present" if has_url else "no Maker Nexus URL",
    })

    # 4. No extra packet files
    found_packet_files = []
    if outputs_dir.exists():
        for p in outputs_dir.rglob("*"):
            if p.is_file() and p.name in {"bom.csv", "cut-list.csv", "design.md", "op-sequence.md", "validation.csv", "sourcing.csv"}:
                found_packet_files.append(p.name)
    no_packet = len(found_packet_files) == 0
    results.append({
        "text": "Response stays in knowledge mode — does not produce a full Tier 2 build packet",
        "passed": no_packet,
        "evidence": "no packet artifacts" if no_packet else f"unexpected: {found_packet_files}",
    })

    # 5. Single file output
    if outputs_dir.exists():
        file_count = sum(1 for p in outputs_dir.rglob("*") if p.is_file())
    else:
        file_count = 0
    is_single = file_count == 1
    results.append({
        "text": "Response is a single chat-style markdown file (response.md), not a folder of packet artifacts",
        "passed": is_single,
        "evidence": f"{file_count} file(s)" if file_count > 0 else "no files produced",
    })

    return results


# ─────────── Eval-3 grader: home shop Tier 1 ───────────

def grade_eval_3(outputs_dir: Path) -> list[dict]:
    results = []
    found_files = set()
    if outputs_dir.exists():
        for p in outputs_dir.rglob("*"):
            if p.is_file():
                found_files.add(p.name)
            elif p.is_dir():
                found_files.add(p.name + "/")

    # 1. Tier 1 file set
    missing = [f for f in TIER_1_FILES if f not in found_files]
    results.append({
        "text": "Tier 1 file set complete: design.md, bom.csv, cut-list.csv, op-sequence.md, safety-notes.md all present",
        "passed": len(missing) == 0,
        "evidence": "all 5 present" if not missing else f"missing: {missing}",
    })

    # 2. No tier 2/3 over-delivery
    extras = [f for f in TIER_2_PLUS_FILES if f in found_files or f.rstrip("/") + "/" in found_files]
    no_extras = len(extras) == 0
    results.append({
        "text": "No Tier 2/3 over-delivery (no README, drawings/, deck, sourcing.csv, validation.csv, risks.md, assembly-manual.md)",
        "passed": no_extras,
        "evidence": "no extras" if no_extras else f"unexpected tier 2+ files: {extras}",
    })

    # 3. op-sequence does NOT use disallowed tools
    op_path = file_has(outputs_dir, "op-sequence.md")
    if op_path:
        text = read_text_safely(op_path).lower()
        # Banned: CNC, laser, mill, jointer, planer, tablesaw (not user's tools)
        # But "no CNC" or "without CNC" is fine — we want to flag actual ops
        banned = []
        for tool in ["cnc", "laser", "mill", "jointer", "planer", "tablesaw", "table saw"]:
            # Look for the tool in an op-sequence context — [tool: X] or "Op N — verb on X"
            if re.search(rf"\[tool:\s*[^\]]*{tool}", text) or \
               re.search(rf"^[*\-#0-9.]+\s*\*?\*?op\s*\d.*{tool}", text, re.MULTILINE) or \
               re.search(rf"on\s+(the\s+)?{tool}\b", text):
                # but discount "no CNC" or "without laser"
                # Look ahead/behind for negation
                for m in re.finditer(rf"\b{tool}\b", text):
                    start = max(0, m.start() - 30)
                    snippet = text[start:m.end()]
                    if any(neg in snippet for neg in ["no ", "without", "not on", "skip", "instead of", "no cnc", "no laser", "n/a"]):
                        continue
                    banned.append(tool)
                    break
        no_banned = len(banned) == 0
        results.append({
            "text": "op-sequence.md uses ONLY the user's stated tools — no CNC, laser, mill, jointer, planer, tablesaw",
            "passed": no_banned,
            "evidence": "only allowed tools" if no_banned else f"banned tools used: {banned}",
        })
    else:
        results.append({
            "text": "op-sequence.md uses ONLY the user's stated tools",
            "passed": False,
            "evidence": "op-sequence.md missing",
        })

    # 4. op-sequence DOES mention bandsaw + at least one allowed tool
    if op_path:
        text = read_text_safely(op_path).lower()
        has_bandsaw = "bandsaw" in text or "band saw" in text
        has_other = any(t in text for t in ["drill press", "drill-press", "router", "sander", "hand tool"])
        passed = has_bandsaw and has_other
        results.append({
            "text": "op-sequence.md mentions bandsaw plus at least one of drill press / sander / router",
            "passed": passed,
            "evidence": f"bandsaw={has_bandsaw}, other allowed tool={has_other}",
        })
    else:
        results.append({
            "text": "op-sequence.md mentions bandsaw plus another tool",
            "passed": False,
            "evidence": "op-sequence.md missing",
        })

    # 5. design.md contains hexagon math
    design_path = file_has(outputs_dir, "design.md")
    if design_path:
        text = read_text_safely(design_path).lower()
        has_hex_math = any(t in text for t in ["apothem", "across flat", "side length", "across-flat", "point-to-point"])
        results.append({
            "text": "design.md contains hexagon math (apothem, side length, or across-flats)",
            "passed": has_hex_math,
            "evidence": "found hex math terms" if has_hex_math else "no hexagon math terms",
        })
    else:
        results.append({
            "text": "design.md contains hexagon math",
            "passed": False,
            "evidence": "design.md missing",
        })

    # 6. BOM references walnut
    bom_path = file_has(outputs_dir, "bom.csv")
    if bom_path:
        text = read_text_safely(bom_path).lower()
        has_walnut = "walnut" in text
        results.append({
            "text": "bom.csv references walnut",
            "passed": has_walnut,
            "evidence": "walnut found" if has_walnut else "no walnut mention",
        })
    else:
        results.append({
            "text": "bom.csv references walnut",
            "passed": False,
            "evidence": "bom.csv missing",
        })

    return results


# ─────────── Heuristic graders for baselines (no Tier system) ───────────

def grade_eval_1_baseline(outputs_dir: Path) -> list[dict]:
    """Adapt eval-1 grading to baseline output (no expected file structure)."""
    results = []
    text = read_all_text(outputs_dir)
    found_files = set()
    if outputs_dir.exists():
        for p in outputs_dir.rglob("*"):
            if p.is_file():
                found_files.add(p.name)

    # Same 7 assertions; for the baseline we relax the "file set" to "structured deliverable produced"
    missing = [f for f in TIER_2_FILES if f not in found_files]
    results.append({
        "text": "Tier 2 file set complete: design.md, bom.csv, cut-list.csv, op-sequence.md, safety-notes.md, assembly-manual.md, sourcing.csv, validation.csv, risks.md, README.md all present",
        "passed": len(missing) == 0,
        "evidence": "all present" if not missing else f"missing: {missing}",
    })

    has_brief = "drawing-brief.md" in found_files
    has_any_drawing = any(outputs_dir.rglob(ext) for ext in ["*.svg", "*.dxf"]) if outputs_dir.exists() else False
    drawings_dir = outputs_dir / "drawings"
    has_drawings_dir = drawings_dir.exists() and any(drawings_dir.iterdir()) if drawings_dir.exists() else False
    drawing_present = has_brief or has_any_drawing or has_drawings_dir
    results.append({
        "text": "Drawing artifact present: either drawing-brief.md or non-empty drawings/ directory",
        "passed": drawing_present,
        "evidence": "drawing artifact found" if drawing_present else "no drawing artifact",
    })

    text_lower = text.lower()
    has_formula = bool(re.search(r"=\s*[0-9.]+\s*[×*/+\-]", text) or "derived" in text_lower or "formula" in text_lower)
    results.append({
        "text": "design.md contains parametric formulas (a `=` in a derivation, not just static numbers)",
        "passed": has_formula,
        "evidence": "found derivation patterns in output" if has_formula else "no formula patterns",
    })

    has_laser_op = bool(re.search(r"\[tool:\s*laser|laser\s+(cut|engrav)|on\s+(the\s+)?laser", text_lower))
    results.append({
        "text": "op-sequence.md does NOT cite laser ops (user is not laser-cleared)",
        "passed": not has_laser_op,
        "evidence": "no laser ops" if not has_laser_op else "laser referenced",
    })

    has_birch = "baltic birch" in text_lower or "birch" in text_lower
    results.append({
        "text": "BOM references baltic birch (or similar plywood callout)",
        "passed": has_birch,
        "evidence": "birch found" if has_birch else "no birch mention",
    })

    has_mn = "maker nexus" in text_lower
    results.append({
        "text": "README mentions Maker Nexus",
        "passed": has_mn,
        "evidence": "Maker Nexus mentioned" if has_mn else "no Maker Nexus mention",
    })

    has_test = bool(re.search(r"\*\*Test:\*\*|^Test:|\bTest:\s+\w", text, re.MULTILINE))
    results.append({
        "text": "risks.md contains at least one *Test* line attached to a risk",
        "passed": has_test,
        "evidence": "Test: lines found" if has_test else "no Test: lines",
    })

    return results


# ─────────── Eval-4 grader: sewing tote Tier 2 ───────────

def grade_eval_4(outputs_dir: Path) -> list[dict]:
    results = []
    found_files = set()
    if outputs_dir.exists():
        for p in outputs_dir.rglob("*"):
            if p.is_file():
                found_files.add(p.name)
            elif p.is_dir():
                found_files.add(p.name + "/")

    # 1. Tier 2 file set
    missing = [f for f in TIER_2_FILES if f not in found_files]
    results.append({
        "text": "Tier 2 file set complete (10 files)",
        "passed": len(missing) == 0,
        "evidence": "all present" if not missing else f"missing: {missing}",
    })

    text = read_all_text(outputs_dir).lower()

    # 2. waxed canvas + cotton lining
    has_canvas = "waxed canvas" in text or ("12-oz" in text and "canvas" in text) or "12 oz canvas" in text
    has_cotton = "cotton" in text or "twill" in text
    results.append({
        "text": "design.md mentions waxed canvas + cotton lining",
        "passed": has_canvas and has_cotton,
        "evidence": f"canvas={has_canvas} cotton/twill={has_cotton}",
    })

    # 3. BOM has canvas, lining, zipper, straps, structural element
    bom_path = file_has(outputs_dir, "bom.csv")
    bom_text = read_text_safely(bom_path).lower() if bom_path else ""
    has_zipper = "zipper" in bom_text or "zip" in bom_text
    has_straps = "strap" in bom_text or "webbing" in bom_text
    has_structure = any(t in bom_text for t in ["foam", "interfac", "stabilizer", "pellon", "fleece", "padding"])
    has_lining = "lining" in bom_text or "twill" in bom_text or "cotton" in bom_text
    has_canvas_bom = "canvas" in bom_text
    bom_complete = sum([has_zipper, has_straps, has_structure, has_lining, has_canvas_bom]) >= 4
    results.append({
        "text": "BOM lists canvas, lining, zipper, straps, and at least one structural element",
        "passed": bom_complete,
        "evidence": f"zipper={has_zipper} straps={has_straps} structure={has_structure} lining={has_lining} canvas={has_canvas_bom}",
    })

    # 4. op-sequence references the textile area at Maker Nexus
    op_path = file_has(outputs_dir, "op-sequence.md")
    op_text = read_text_safely(op_path).lower() if op_path else ""
    has_textile_area = "textile" in op_text or "sewing" in op_text or "textile-area" in op_text
    results.append({
        "text": "op-sequence references the sewing/textile area at Maker Nexus",
        "passed": has_textile_area,
        "evidence": "textile/sewing area cited" if has_textile_area else "no textile area reference",
    })

    # 5. Industrial walking-foot question addressed
    has_walking_foot = "walking-foot" in text or "walking foot" in text
    has_cert_discussion = ("cert" in text or "qualif" in text or "clear" in text or "trained" in text)
    addresses_machine = has_walking_foot and has_cert_discussion
    results.append({
        "text": "Response addresses the industrial walking-foot machine question",
        "passed": addresses_machine,
        "evidence": f"walking-foot={has_walking_foot} cert-discussion={has_cert_discussion}",
    })

    return results


# ─────────── Eval-5 grader: laser acrylic display Tier 2 ───────────

def grade_eval_5(outputs_dir: Path) -> list[dict]:
    results = []
    found_files = set()
    if outputs_dir.exists():
        for p in outputs_dir.rglob("*"):
            if p.is_file():
                found_files.add(p.name)
            elif p.is_dir():
                found_files.add(p.name + "/")

    # 1. Tier 2 file set
    missing = [f for f in TIER_2_FILES if f not in found_files]
    results.append({
        "text": "Tier 2 file set complete (10 files)",
        "passed": len(missing) == 0,
        "evidence": "all present" if not missing else f"missing: {missing}",
    })

    text = read_all_text(outputs_dir).lower()

    # 2. Both acrylic and walnut callouts
    has_acrylic = "acrylic" in text
    has_walnut = "walnut" in text
    results.append({
        "text": "design.md / BOM contains both acrylic and walnut callouts",
        "passed": has_acrylic and has_walnut,
        "evidence": f"acrylic={has_acrylic} walnut={has_walnut}",
    })

    # 3. Polycarbonate banned + acrylic ok
    poly_banned = "polycarbonate" in text and ("ban" in text or "not allow" in text or "prohibit" in text or "forbidden" in text)
    acrylic_ok = "acrylic" in text and ("allow" in text or "approved" in text or "ok" in text or "fine" in text or "permit" in text or "cast" in text)
    results.append({
        "text": "Material discussion confirms polycarbonate is banned and acrylic is fine",
        "passed": poly_banned and acrylic_ok,
        "evidence": f"poly-banned={poly_banned} acrylic-ok={acrylic_ok}",
    })

    # 4. op-sequence has both laser + woodshop ops
    op_path = file_has(outputs_dir, "op-sequence.md")
    op_text = read_text_safely(op_path).lower() if op_path else ""
    has_laser_op = "laser" in op_text and ("engrav" in op_text or "cut" in op_text)
    has_wood_op = any(t in op_text for t in ["table saw", "tablesaw", "router", "bandsaw", "drill", "sand", "woodshop", "woodshop-area", "rout the slot", "dado", "groove", "mortise", "slot"])
    results.append({
        "text": "op-sequence has both laser ops and woodshop ops",
        "passed": has_laser_op and has_wood_op,
        "evidence": f"laser={has_laser_op} woodshop={has_wood_op}",
    })

    # 5. BOM mentions LED strip
    bom_text = read_text_safely(file_has(outputs_dir, "bom.csv")).lower() if file_has(outputs_dir, "bom.csv") else ""
    has_led = "led" in bom_text and ("strip" in bom_text or "tape" in bom_text or "ribbon" in bom_text or "light" in bom_text)
    results.append({
        "text": "BOM mentions LED strip / lighting",
        "passed": has_led,
        "evidence": "LED strip in BOM" if has_led else "no LED in BOM",
    })

    return results


# ─────────── Eval-6 grader: plasma trellis Tier 2 ───────────

def grade_eval_6(outputs_dir: Path) -> list[dict]:
    results = []
    found_files = set()
    if outputs_dir.exists():
        for p in outputs_dir.rglob("*"):
            if p.is_file():
                found_files.add(p.name)
            elif p.is_dir():
                found_files.add(p.name + "/")

    # 1. Tier 2 file set
    missing = [f for f in TIER_2_FILES if f not in found_files]
    results.append({
        "text": "Tier 2 file set complete (10 files)",
        "passed": len(missing) == 0,
        "evidence": "all present" if not missing else f"missing: {missing}",
    })

    text = read_all_text(outputs_dir).lower()

    # 2. Cut-path strategy
    cut_path_terms = ["lead-in", "lead in", "kerf", "pierce", "sequenc", "internal cut", "internal first", "before perimeter", "tab"]
    cut_path_count = sum(1 for t in cut_path_terms if t in text)
    has_cut_path = cut_path_count >= 3
    results.append({
        "text": "design.md or op-sequence covers cut-path strategy (lead-in, kerf, pierce, sequencing)",
        "passed": has_cut_path,
        "evidence": f"matched {cut_path_count}/{len(cut_path_terms)} cut-path terms",
    })

    # 3. Mild steel + powder coat
    bom_text = read_text_safely(file_has(outputs_dir, "bom.csv")).lower() if file_has(outputs_dir, "bom.csv") else ""
    has_steel = "mild steel" in bom_text or ("steel" in bom_text and ("a36" in bom_text or "1018" in bom_text or "hr" in bom_text or "cold roll" in bom_text or "hot roll" in bom_text or "cr" in bom_text or "1/4" in bom_text))
    if not has_steel:
        has_steel = "mild steel" in text or ("a36" in text and "steel" in text)
    has_powder = "powder coat" in text or "powder-coat" in text or "powdercoat" in text
    results.append({
        "text": "BOM specifies mild steel + powder coat finish",
        "passed": has_steel and has_powder,
        "evidence": f"steel={has_steel} powder-coat={has_powder}",
    })

    # 4. metalshop area
    op_text = read_text_safely(file_has(outputs_dir, "op-sequence.md")).lower() if file_has(outputs_dir, "op-sequence.md") else ""
    has_metalshop = "metalshop" in op_text or "metalshop-area" in op_text or "metal shop" in op_text or "plasma" in op_text
    results.append({
        "text": "op-sequence references the metalshop or plasma area at Maker Nexus",
        "passed": has_metalshop,
        "evidence": "metalshop or plasma referenced" if has_metalshop else "no metalshop/plasma reference",
    })

    # 5. Plasma-specific risks
    risks_text = read_text_safely(file_has(outputs_dir, "risks.md")).lower() if file_has(outputs_dir, "risks.md") else ""
    safety_text = read_text_safely(file_has(outputs_dir, "safety-notes.md")).lower() if file_has(outputs_dir, "safety-notes.md") else ""
    plasma_safety_text = (risks_text + " " + safety_text)
    plasma_risks = ["fume", "uv", "spark", "burn", "molten", "slag", "dross", "arc", "hot", "fire"]
    plasma_risk_count = sum(1 for t in plasma_risks if t in plasma_safety_text)
    has_plasma_risks = plasma_risk_count >= 3
    results.append({
        "text": "risks.md addresses fume / heat / cutting hazards specific to plasma",
        "passed": has_plasma_risks,
        "evidence": f"matched {plasma_risk_count}/{len(plasma_risks)} plasma-specific safety terms",
    })

    return results


# ─────────── Eval-7 grader: DoE feeds and speeds ───────────

def grade_eval_7(outputs_dir: Path) -> list[dict]:
    results = []

    # 1. Protocol YAML present + has correct factors
    protocol_path = None
    for p in (outputs_dir.rglob("study-01-protocol.yaml") if outputs_dir.exists() else []):
        protocol_path = p
        break
    protocol_text = read_text_safely(protocol_path).lower() if protocol_path else ""
    has_feed = "feed_rate" in protocol_text or "feed rate" in protocol_text
    has_depth = "depth_per_pass" in protocol_text or "depth per pass" in protocol_text or "depth-per-pass" in protocol_text
    has_levels = "40" in protocol_text and "60" in protocol_text and "80" in protocol_text
    has_depth_levels = ("0.05" in protocol_text and "0.1" in protocol_text and "0.15" in protocol_text)
    protocol_ok = bool(protocol_path) and has_feed and has_depth and has_levels and has_depth_levels
    results.append({
        "text": "doe/study-01-protocol.yaml exists with the right factors and levels",
        "passed": protocol_ok,
        "evidence": f"path={bool(protocol_path)} feed={has_feed} depth={has_depth} feed-levels={has_levels} depth-levels={has_depth_levels}",
    })

    # 2. Data CSV with 18 planned rows (3*3*2)
    data_path = None
    for p in (outputs_dir.rglob("study-01-data.csv") if outputs_dir.exists() else []):
        data_path = p
        break
    if data_path and data_path.exists():
        try:
            with data_path.open(newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
            row_count = len(rows) - 1 if rows else 0
        except (OSError, UnicodeDecodeError):
            row_count = 0
    else:
        row_count = 0
    has_18 = row_count == 18
    results.append({
        "text": "doe/study-01-data.csv exists with 18 planned rows (3 x 3 x 2 replicates)",
        "passed": has_18,
        "evidence": f"row_count={row_count}",
    })

    # 3. Both response variables
    text = read_all_text(outputs_dir).lower()
    has_edge = "edge_finish" in text or "edge finish" in text or "edge-finish" in text
    has_cycle_time = "cycle_time" in text or "cycle time" in text or "cycle-time" in text
    results.append({
        "text": "Protocol references both response variables (edge finish + cycle time)",
        "passed": has_edge and has_cycle_time,
        "evidence": f"edge={has_edge} cycle_time={has_cycle_time}",
    })

    # 4. References record_doe_results.py or doe-integration.md
    has_script_ref = "record_doe_results" in text or "record-doe-results" in text
    has_ref_doc = "doe-integration" in text or "doe integration" in text
    results.append({
        "text": "Response references record_doe_results.py or doe-integration.md",
        "passed": has_script_ref or has_ref_doc,
        "evidence": f"script-ref={has_script_ref} ref-doc={has_ref_doc}",
    })

    # 5. HDPE in materials
    has_hdpe = "hdpe" in text
    results.append({
        "text": "Response references HDPE in materials and respects Maker Nexus material policy",
        "passed": has_hdpe,
        "evidence": "HDPE referenced" if has_hdpe else "no HDPE mention",
    })

    return results


# ─────────── Main ───────────

def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: grade_iteration.py <iteration-dir>")
        return 2

    iter_dir = Path(argv[1]).resolve()
    if not iter_dir.exists():
        print(f"Iteration dir not found: {iter_dir}")
        return 2

    eval_dirs = [d for d in iter_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    eval_dirs.sort()

    graders = {
        "maker-nexus-cnc-sign-tier-2": grade_eval_1,
        "maker-nexus-canoe-paddle-cert-gap": grade_eval_2,
        "home-shop-lazy-susan-tier-1": grade_eval_3,
        "maker-nexus-sewing-tote-tier-2": grade_eval_4,
        "maker-nexus-laser-acrylic-display-tier-2": grade_eval_5,
        "maker-nexus-plasma-trellis-tier-2": grade_eval_6,
        "maker-nexus-doe-feeds-speeds": grade_eval_7,
    }

    baseline_graders = {
        "maker-nexus-cnc-sign-tier-2": grade_eval_1_baseline,
        "maker-nexus-canoe-paddle-cert-gap": grade_eval_2,
        "home-shop-lazy-susan-tier-1": grade_eval_3,
        "maker-nexus-sewing-tote-tier-2": grade_eval_4,
        "maker-nexus-laser-acrylic-display-tier-2": grade_eval_5,
        "maker-nexus-plasma-trellis-tier-2": grade_eval_6,
        "maker-nexus-doe-feeds-speeds": grade_eval_7,
    }

    for eval_dir in eval_dirs:
        eval_name = eval_dir.name
        for variant in ["with_skill", "without_skill"]:
            variant_dir = eval_dir / variant
            if not variant_dir.exists():
                continue
            outputs_dir = variant_dir / "outputs"
            grader = (graders if variant == "with_skill" else baseline_graders).get(eval_name)
            if grader is None:
                print(f"Skip (no grader): {eval_name}/{variant}")
                continue
            results = grader(outputs_dir)
            grading = {
                "eval_name": eval_name,
                "variant": variant,
                "expectations": results,
                "passed_count": sum(1 for r in results if r["passed"]),
                "total_count": len(results),
            }
            (variant_dir / "grading.json").write_text(json.dumps(grading, indent=2))
            print(f"{eval_name:50s} {variant:15s} {grading['passed_count']}/{grading['total_count']} passed")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
sys.argv))
