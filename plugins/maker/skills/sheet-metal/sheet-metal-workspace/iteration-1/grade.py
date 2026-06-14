#!/usr/bin/env python3
"""Grade iteration-1 runs by checking each assertion against the concatenated
output content for each run. Writes grading.json per run."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_outputs_text(outputs_dir: Path):
    if not outputs_dir.exists():
        return "", []
    parts = []
    names = []
    for entry in sorted(outputs_dir.iterdir()):
        if not entry.is_file():
            continue
        names.append(entry.name)
        try:
            parts.append(entry.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            pass
    return "\n".join(parts).lower(), names


def has_any(text, needles):
    hits = [n for n in needles if n.lower() in text]
    return bool(hits), ("found: " + str(hits)) if hits else ("none of " + str(needles))


def filename_has(filenames, substring):
    matches = [f for f in filenames if substring.lower() in f.lower()]
    return bool(matches), ("file: " + str(matches)) if matches else ("no file containing '" + substring + "'")


def grade_eval_1(text, filenames):
    has_design_brief = any("design-brief" in f.lower() or "design_brief" in f.lower() for f in filenames)
    has_params_csv = any("parameters" in f.lower() and f.lower().endswith(".csv") for f in filenames)
    has_equations = any(p in text for p in ['"box_length"', '"box_width"', '"box_height"', '"material_thickness"', '"material_t"'])
    has_design_table = any(("design-table" in f.lower() or "design_table" in f.lower() or "family" in f.lower()) and f.lower().endswith(".csv") for f in filenames)
    has_table_configs = any(c in text for c in ["seed", "compact", "large"])
    has_sw_plan = any("solidworks-plan" in f.lower() or "solidworks_plan" in f.lower() or "assembly_structure" in f.lower() or "modeling_plan" in f.lower() for f in filenames)
    mlp = any(p in text for p in ["master layout", "mlp"])
    stack = any(p in text for p in ["clocking rim", "stack rim", "stack_rim", "corner cleat", "interlock", "stacking interface", "stack foot"])
    dolly_thick = any(p in text for p in ["12 ga", "12-ga", "12ga", "0.105", "1/8 in", "0.125", "14 ga"])
    bend_table = any("bend-table" in f.lower() or "bend_table" in f.lower() for f in filenames)
    bom = any("bom" in f.lower() for f in filenames)
    cut_list = any("cut-list" in f.lower() or "cut_list" in f.lower() for f in filenames)
    authority = any(p in text for p in ["not fabrication-ready", "not fabrication ready", "design and cad planning", "design planning", "planning authority", "provisional planning"])
    open_items = any(p in text for p in ["open questions", "open measurements", "before fabrication", "before flat pattern", "verify before", "next human decisions"])
    parameters_quality = has_params_csv and "thickness" in text and "bend" in text and ("k-factor" in text or "k_factor" in text)

    return [
        {"text": "Produces a design-brief.md", "passed": has_design_brief, "evidence": "design-brief file present" if has_design_brief else "no design-brief file"},
        {"text": "Produces a parameters.csv with thickness, bend radius, K-factor", "passed": parameters_quality, "evidence": "parameters CSV with required variables" if parameters_quality else "missing parameters CSV or required variables"},
        {"text": "Produces SolidWorks equations with quoted variable names", "passed": has_equations, "evidence": 'quoted vars like "Box_Length" present' if has_equations else "no quoted SW variables found"},
        {"text": "Produces a design-table CSV with seed and other configurations", "passed": has_design_table and has_table_configs, "evidence": "design table + multiple configs"},
        {"text": "Produces a SolidWorks plan with master layout part", "passed": has_sw_plan and mlp, "evidence": "SW plan + master layout"},
        {"text": "Includes stacking interface (rim/cleat/interlock)", "passed": stack, "evidence": "stacking interface mentioned"},
        {"text": "Includes dolly with thicker stock", "passed": dolly_thick, "evidence": "12ga or 1/8in dolly mentioned"},
        {"text": "Produces bend-table, BOM, and cut-list", "passed": bend_table and bom and cut_list, "evidence": f"bend-table={bend_table}, bom={bom}, cut-list={cut_list}"},
        {"text": "Marks authority as design/planning, not fabrication-ready", "passed": authority, "evidence": "explicit design-only/not-fab-ready statement"},
        {"text": "Lists open measurements before fabrication release", "passed": open_items, "evidence": "open items called out"},
    ]


def grade_eval_3(text, filenames):
    bw_class = "beetleweight" in text and any(p in text for p in ["1360", "1361", "3 lb", "3-pound"])
    weight_target = any(p in text for p in ["300 g", "300g", "350 g", "350g", "400 g", "400g", "300 to 400", "300-400", "378"])
    al_alloy = ("5052" in text or "6061" in text) and ("r >= t" in text or "r=t" in text or "r = t" in text or "coupon" in text)
    sloped = any(p in text for p in ["slope", "wedge", "30 deg", "45 deg", "30-45", "30 to 45"])
    guard = any(p in text for p in ["wheel guard", "wheel-guard", "wheel well", "guard flange", "wheel armor"])
    captured = any(p in text for p in ["pem", "nutplate", "captive nut", "captured nut", "nyloc", "socket-head", "button-head", "hex key", "m3"])
    shock = any(p in text for p in ["shock", "isolation", "rubber grommet", "lord mount", "floating tray", "vibration", "isolated"])
    script_use = any(p in text for p in ["sheet_metal_math", "combat-budget", "combat_budget"])

    return [
        {"text": "Identifies beetleweight class and 3 lb / 1360 g limit", "passed": bw_class, "evidence": "beetleweight + limit"},
        {"text": "Names chassis weight target around 300-400 g", "passed": weight_target, "evidence": "weight target mentioned"},
        {"text": "Recommends aluminum 5052 or 6061-T6 with R>=T or test coupon", "passed": al_alloy, "evidence": "aluminum + bend rule"},
        {"text": "Recommends sloped front armor (30-45 deg)", "passed": sloped, "evidence": "sloped/wedge armor mentioned"},
        {"text": "Includes wheel guards", "passed": guard, "evidence": "wheel guards mentioned"},
        {"text": "Includes captured fastener strategy", "passed": captured, "evidence": "captive/PEM/M3 mentioned"},
        {"text": "Includes shock isolation for electronics", "passed": shock, "evidence": "shock isolation mentioned"},
        {"text": "Mentions running scripts/sheet_metal_math.py", "passed": script_use, "evidence": "script usage mentioned"},
    ]


def grade_eval_5(text, filenames):
    safety_sensitive = any(p in text for p in ["safety-sensitive", "safety sensitive", "stop-work", "stop work", "safety gate", "safety-gate", "provisional", "not road-ready", "not road ready"])
    routes = any(p in text for p in ["maker-engineering", "maker engineering", "licensed engineer", "qualified engineer", "qualified review", "licensed professional", "structural engineer", "shop instructor"])
    disclaimer = any(p in text for p in ["not road-ready", "not road ready", "not fabrication-ready", "not certify", "not a certification", "not certified", "not approved for highway", "not safe for highway", "provisional planning"])
    oem = (any(p in text for p in ["oem", "factory", "manufacturer"]) and any(p in text for p in ["roof load", "load rating", "load limit"]) and "measured" in text)
    rail_mat = (any(p in text for p in ["5052", "1/8", "10 ga", "10ga", "0.102", "0.105", "0.125"]) and any(p in text for p in ["return flange", "downturned", "u-channel", "extrusion"]))
    aero_consid = sum(1 for s in ["wind lift", "fatigue", "corrosion", "anti-loosening", "loctite", "nyloc", "torque-witness", "torque witness"] if s in text) >= 3

    return [
        {"text": "Treats project as safety-sensitive vehicle work", "passed": safety_sensitive, "evidence": "safety-sensitive language present"},
        {"text": "Routes final safety gate to maker-engineering or qualified review", "passed": routes, "evidence": "routing language present"},
        {"text": "Contains explicit NOT road-ready / NOT highway-certified disclaimer", "passed": disclaimer, "evidence": "disclaimer language present"},
        {"text": "Asks for measured vehicle interface and OEM roof load rating", "passed": oem, "evidence": "OEM + load rating + measured"},
        {"text": "Provides provisional rail material with stiffener strategy", "passed": rail_mat, "evidence": "material + stiffener"},
        {"text": "Includes wind lift, fatigue, corrosion, anti-loosening (3+ of)", "passed": aero_consid, "evidence": "3+ of expected considerations"},
    ]


RUBRICS = {
    "eval-1-toolbox": grade_eval_1,
    "eval-3-beetleweight": grade_eval_3,
    "eval-5-vehicle-rack": grade_eval_5,
}


def grade_run(eval_dir, variant):
    outputs_dir = eval_dir / variant / "outputs"
    text, filenames = load_outputs_text(outputs_dir)
    rubric = RUBRICS[eval_dir.name]
    expectations = rubric(text, filenames)
    total = len(expectations)
    passed = sum(1 for e in expectations if e["passed"])
    return {
        "eval_name": eval_dir.name,
        "variant": variant,
        "files_produced": filenames,
        "passed_count": passed,
        "total_count": total,
        "pass_rate": passed / total if total > 0 else 0,
        "expectations": expectations,
    }


def main():
    rows = []
    for eval_name in ["eval-1-toolbox", "eval-3-beetleweight", "eval-5-vehicle-rack"]:
        eval_dir = ROOT / eval_name
        for variant in ["with_skill", "without_skill"]:
            result = grade_run(eval_dir, variant)
            (eval_dir / variant / "grading.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            rows.append(result)
    print("Summary:")
    for r in rows:
        n = r["eval_name"]
        v = r["variant"]
        p = r["passed_count"]
        t = r["total_count"]
        rate = r["pass_rate"]
        print(f"  {n:25s} {v:15s}  {p:>2}/{t:<2}  ({rate:.0%})")


if __name__ == "__main__":
    main()
