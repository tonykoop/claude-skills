#!/usr/bin/env python3
"""Grade houseplant skill eval outputs against per-eval assertions."""
import json
import re
import pathlib

WS = pathlib.Path("/sessions/charming-intelligent-cerf/mnt/claude-skills/skills/houseplant-workspace/iteration-1")


def grade_eval_1(text: str):
    t = text.lower()
    checks = [
        # 0
        ("Routes capture intake through the lazy-susan / ruler workflow (mentions capture-pipeline.md OR explicitly handles Mode D lazy-susan capture)",
         any(k in t for k in ["capture-pipeline.md", "mode d", "lazy susan", "lazy-susan"])),
        # 1
        ("Names the Plant_<plant_id>/ scene contract and the 00_source_scan/...05_simulations/ child collections",
         re.search(r"plant_ficus[-_]benjamina[-_]01", t) is not None and "00_source_scan" in t and "05_simulations" in t),
        # 2
        ("Uses or references scene_scaffold.py for building the collection hierarchy",
         "scene_scaffold.py" in t),
        # 3
        ("Calibrates scene scale from the 10 cm ruler segment (mentions scale_from_ruler.py OR shows equivalent scale-factor math with the two ruler endpoints)",
         "scale_from_ruler.py" in t or ("0 cm" in t and "10 cm" in t and ("scale_factor" in t or "scale factor" in t or "real_distance" in t))),
        # 4
        ("Generates a wire coil via wire_coil.py OR shows an equivalent helical curve construction around the target branch",
         "wire_coil.py" in t or ("helix" in t or "helical" in t) and ("coil" in t)),
        # 5
        ("Places cut and wire markers in a sim_<scenario>_<date> sub-collection rather than mutating the current-state twin (uses sim_collection.py OR explicit sim collection creation)",
         "sim_collection.py" in t or re.search(r"sim_[a-z_\-]+_20\d\d[-_]\d\d[-_]\d\d", t) is not None),
        # 6
        ("Calls get_objects_summary or get_blendfile_summary_* BEFORE execute_blender_code (orient before write)",
         ("get_objects_summary" in t or "get_blendfile_summary" in t)),
        # 7
        ("Produces a pruning plan table with at minimum Id, Action, Why, Risk, Verify, Aftercare, Follow-up columns",
         all(col in t for col in ["action", "risk", "aftercare", "follow"]) and "|" in text and ("verify" in t)),
        # 8
        ("Uses correct color semantics (red for cut, blue for wire)",
         ("red" in t and "cut" in t) and ("blue" in t and "wire" in t)),
        # 9
        ("Includes Ficus-specific note about fast cambium / short wire-removal window (e.g. inspect every 1-2 weeks during active growth)",
         ("cambium" in t or "bite-in" in t or "bite in" in t) and ("week" in t)),
        # 10
        ("Ends with a Digital twin sync log entry in the markdown template format",
         ("digital twin sync" in t or "digital-twin sync" in t) and ("changed objects" in t or "simulations created" in t or "follow-up" in t)),
    ]
    return [(text_, bool(ok)) for text_, ok in checks]


def grade_eval_2(text: str):
    t = text.lower()
    blender_heavy = (
        ("execute_blender_code" in t and "scaffold" in t and "import" in t)  # multi-stage MCP plan
        or ("scene_scaffold.py" in t)
        or (("plant_" in t) and t.count("execute_blender_code") > 2)
    )
    checks = [
        ("Does NOT initiate a sprawling Blender digital-twin session for what is a simple record update",
         not blender_heavy),
        ("Appends a wire_removed event to the plant record with date, evidence, and aftercare",
         "wire_removed" in t and ("event" in t or "timeline" in t)),
        ("Directly answers whether the wire impression will scar — fades on healthy bark without bite-in, with caveats",
         ("fade" in t or "fading" in t) and ("scar" in t or "permanent" in t)),
        ("Recommends inspection cadence for the bend setting and bark recovery",
         any(k in t for k in ["1-2 weeks", "1–2 weeks", "2 weeks", "4 weeks", "every week", "weekly", "next check"])),
        ("Produces a calendar-ready reminder using the skill's reminder format",
         ("reminder" in t) and ("title" in t or "checklist" in t or "priority" in t or "trigger" in t)),
        ("Stays scoped to what was asked (record + bark question + next checks); no generic care lecture",
         not blender_heavy and len(text) < 12000),
    ]
    return [(text_, bool(ok)) for text_, ok in checks]


def grade_eval_3(text: str):
    t = text.lower()
    checks = [
        ("Calls get_objects_summary or get_blendfile_summary_* before execute_blender_code (verify the named objects exist)",
         "get_objects_summary" in t or "get_blendfile_summary" in t),
        ("Creates a new sim_<scenario>_<date> collection under 05_simulations/ (uses sim_collection.py OR equivalent)",
         "sim_collection.py" in t or re.search(r"sim_[a-z_0-9\-]+", t) is not None and "05_simulations" in t),
        ("Generates a wire coil around R02 (uses wire_coil.py OR equivalent helical curve)",
         "wire_coil.py" in t or ("r02" in t and ("helix" in t or "helical" in t or "coil" in t))),
        ("Ghosts/hides L03 in the sim WITHOUT mutating the canonical current-state object",
         "l03" in t and ("hide" in t or "ghost" in t or "single_user" in t or "single user" in t or "duplicat" in t)),
        ("Captures a viewport screenshot or render via mcp__Blender__get_screenshot_of_window_as_image or render_thumbnail_to_path / render_viewport_to_path",
         "get_screenshot_of_window_as_image" in t or "render_viewport_to_path" in t or "render_thumbnail_to_path" in t),
        ("Describes the silhouette change concretely (apex/right-side weight/canopy asymmetry)",
         "silhouette" in t and any(k in t for k in ["apex", "right", "asymmetr", "weight", "tier"])),
        ("Includes a pruning plan table or equivalent risk-leveled action list",
         "|" in text and "risk" in t and ("action" in t or "verify" in t)),
        ("Ends with a Digital twin sync log entry",
         "digital twin sync" in t or "digital-twin sync" in t),
    ]
    return [(text_, bool(ok)) for text_, ok in checks]


GRADERS = {
    "eval-1-ficus-scan-to-prune-plan": grade_eval_1,
    "eval-2-wire-removal-physical-log": grade_eval_2,
    "eval-3-sim-before-cutting": grade_eval_3,
}


def find_evidence(text: str, assertion: str, ok: bool) -> str:
    """Pull a short snippet near a relevant keyword for the viewer."""
    if not ok:
        return ""
    # Pick first interesting keyword from the assertion and find it.
    kws = re.findall(r"`([^`]+)`|\b([A-Za-z_][A-Za-z0-9_.\-]+\.py)\b", assertion)
    flat = [w for tup in kws for w in tup if w]
    for kw in flat[:5]:
        idx = text.lower().find(kw.lower())
        if idx >= 0:
            start = max(0, idx - 40)
            end = min(len(text), idx + 80)
            return text[start:end].replace("\n", " ").strip()
    return ""


for eval_dir in sorted(WS.iterdir()):
    if not eval_dir.is_dir() or not eval_dir.name.startswith("eval-"):
        continue
    grader = GRADERS[eval_dir.name]
    for variant in ["with_skill", "old_skill"]:
        response_path = eval_dir / variant / "outputs" / "response.md"
        if not response_path.exists():
            print(f"MISSING: {response_path}")
            continue
        text = response_path.read_text(encoding="utf-8", errors="replace")
        results = grader(text)
        expectations = [
            {
                "text": assertion,
                "passed": ok,
                "evidence": find_evidence(text, assertion, ok),
            }
            for assertion, ok in results
        ]
        passed = sum(1 for _, ok in results if ok)
        total = len(results)
        grading_path = eval_dir / variant / "grading.json"
        grading_path.write_text(json.dumps({
            "expectations": expectations,
            "pass_rate": passed / total,
            "passed": passed,
            "total": total,
        }, indent=2), encoding="utf-8")
        print(f"{eval_dir.name} / {variant}: {passed}/{total} passed")
