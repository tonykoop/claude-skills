#!/usr/bin/env python3
"""Plant-health triage: turn observed symptoms into health_flag_added events.

Story #175 (houseplant "check-engine light"). The multimodal agent does the
*vision* pass — it looks at the uploaded photos and names what it sees. This
script is the deterministic *triage* layer that the reference
`references/health-diagnostics.md` describes in prose: it maps observed symptoms
to candidate flags, cross-references the plant's recent care events, renders the
`health_flag_added` event records (with evidence + confidence), and computes the
risk escalation into structural work.

Posture (enforced here, not optional): screen, don't diagnose; favor
inspection -> isolation -> mechanical removal -> cultural correction; never emit
a chemical-treatment instruction. Pest/rot candidates default to LOW confidence
and ask for a macro photo before naming.

Pure stdlib, no Blender, no network — so it is unit-testable and runs anywhere.

Input (JSON via --input FILE or stdin):
    {
      "observations": [
        {"symptom": "chlorosis-lower-leaves", "photo": "IMG_01.jpg", "region": "lower interior"},
        {"symptom": "webbing-suspected-spidermite", "photo": "IMG_03.jpg", "region": "leaf axils"}
      ],
      "care_events": [{"type": "repotted", "date": "2026-06-10"}],
      "today": "2026-06-18"
    }

CLI:
    health_triage.py --input obs.json
    cat obs.json | health_triage.py
Exit 0 = produced a report (even "no flags"), 2 = bad input.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from dataclasses import dataclass, field

# Symptom -> rule. category drives risk escalation; pest|rot escalate structural
# work to High. cross_ref names the care-event types that re-interpret the flag.
PEST = "pest"
ROT = "rot"
CULTURE = "culture"
STRESS = "stress"


@dataclass
class Rule:
    flag: str
    category: str
    default_confidence: str
    inspection: str
    cross_ref: list = field(default_factory=list)
    note: str = ""


SYMPTOM_RULES: dict[str, Rule] = {
    "chlorosis-lower-leaves": Rule(
        "chlorosis-lower-leaves", CULTURE, "low",
        "check light + recent fertilizer; compare older vs newer leaves",
        cross_ref=["fertilized", "repotted", "relocated"],
        note="uniform lower-leaf yellowing is often nitrogen/light or natural senescence",
    ),
    "interveinal-chlorosis": Rule(
        "interveinal-chlorosis", CULTURE, "low",
        "check substrate pH/drainage; look for waterlogging",
        cross_ref=["watered", "repotted"],
        note="green veins with yellow between -> micronutrient/iron, often pH or waterlogging linked",
    ),
    "leaf-margin-burn": Rule(
        "leaf-margin-burn", CULTURE, "low",
        "check watering cadence, humidity, and salt/fertilizer buildup",
        cross_ref=["fertilized", "watered"],
        note="brown crispy margins/tips -> underwatering, low humidity, salt, or fertilizer burn",
    ),
    "rot-risk": Rule(
        "rot-risk", ROT, "medium",
        "check soil moisture at depth and roots; improve drainage; let dry out",
        cross_ref=["watered", "repotted"],
        note="soft/mushy or base-up yellowing -> overwatering/root-rot risk",
    ),
    "sudden-leaf-drop": Rule(
        "sudden-leaf-drop", STRESS, "low",
        "record the drop pattern (whole-plant vs oldest-first vs one-side)",
        cross_ref=["repotted", "relocated"],
        note="sudden drop soon after a move/repot favors shock over disease",
    ),
    "webbing-suspected-spidermite": Rule(
        "webbing-suspected-spidermite", PEST, "low",
        "isolate; take a macro photo of leaf undersides/axils; wipe/rinse mechanically",
        note="fine webbing + stippled pale leaves; common on stressed ficus in dry heat",
    ),
    "scale-suspected": Rule(
        "scale-suspected", PEST, "low",
        "isolate; macro photo of stems/veins; mechanically remove bumps; wipe honeydew",
        note="immobile brown/tan bumps + sticky honeydew + sooty mold",
    ),
    "mealybug-suspected": Rule(
        "mealybug-suspected", PEST, "low",
        "isolate; macro photo of crotches/joints; remove cottony tufts mechanically",
        note="white cottony tufts in crotches and leaf joints",
    ),
    "thrips-suspected": Rule(
        "thrips-suspected", PEST, "low",
        "isolate; macro photo of new growth; inspect for frass specks",
        note="silvery streaking/scarring + black frass + distorted new growth",
    ),
    "fungus-gnats": Rule(
        "fungus-gnats", CULTURE, "medium",
        "let the substrate dry; bottom-water; this is usually a wet-substrate symptom",
        cross_ref=["watered"],
        note="small flies around soil -> cultural correction, not a foliar pest",
    ),
}

VALID_CONFIDENCE = ("low", "medium", "high")
RECENT_DAYS = 14  # a care event within this window re-interprets a stress/culture flag


def _parse_date(value: str):
    try:
        return _dt.date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _recent_events(care_events: list, today, kinds: list, window: int = RECENT_DAYS) -> list:
    """Return care events of the given kinds within `window` days before today."""
    today_d = _parse_date(today) if isinstance(today, str) else today
    hits = []
    for ev in care_events or []:
        if ev.get("type") not in kinds:
            continue
        ed = _parse_date(ev.get("date", ""))
        if today_d is None or ed is None:
            hits.append(ev)  # undated: surface it rather than silently dropping
            continue
        delta = (today_d - ed).days
        if 0 <= delta <= window:
            hits.append(ev)
    return hits


@dataclass
class Flag:
    flag: str
    category: str
    confidence: str
    photo: str
    region: str
    inspection: str
    cross_ref_note: str


def triage(observations: list, care_events: list, today: str) -> list:
    """Map observations -> Flag records with care-cross-referenced confidence."""
    flags: list = []
    for obs in observations or []:
        symptom = obs.get("symptom", "")
        rule = SYMPTOM_RULES.get(symptom)
        if rule is None:
            # Unknown symptom: surface as an uncited low-confidence flag rather
            # than dropping it, so nothing observed is silently lost.
            flags.append(Flag(
                flag=symptom or "unspecified", category=CULTURE, confidence="low",
                photo=obs.get("photo", ""), region=obs.get("region", ""),
                inspection="take a closer macro photo; describe the symptom for triage",
                cross_ref_note="unrecognized symptom — not in the rule table",
            ))
            continue
        confidence = rule.default_confidence
        cross_note = rule.note
        recent = _recent_events(care_events, today, rule.cross_ref) if rule.cross_ref else []
        if recent:
            evs = ", ".join(f"{e.get('type')} {e.get('date', '?')}" for e in recent)
            if rule.category in (STRESS,):
                cross_note = f"recent {evs} -> favor transplant/relocation stress over disease"
            elif rule.flag == "leaf-margin-burn" and any(e.get("type") == "fertilized" for e in recent):
                cross_note = f"recent {evs} -> favor fertilizer/salt burn over deficiency"
            else:
                cross_note = f"{rule.note}; cross-ref: recent {evs}"
        flags.append(Flag(
            flag=rule.flag, category=rule.category, confidence=confidence,
            photo=obs.get("photo", ""), region=obs.get("region", ""),
            inspection=rule.inspection, cross_ref_note=cross_note,
        ))
    return flags


def structural_risk(flags: list) -> dict:
    """Any open pest/rot flag forces structural work to High risk (#175 ↔ bonsai-module)."""
    blockers = [f for f in flags if f.category in (PEST, ROT)]
    if not blockers:
        return {"risk": "normal", "reason": "no open pest/rot flags"}
    names = ", ".join(sorted({f.flag for f in blockers}))
    return {
        "risk": "High",
        "reason": (
            f"open {names} flag(s) -> structural pruning/wiring/root/aerial-root work is "
            "High risk; downgrade to maintenance-only (remove dead material, improve "
            "culture, isolate) until resolved"
        ),
    }


def render_flag_event(flag: Flag, date: str) -> str:
    return "\n".join([
        f"### {date} — health_flag_added",
        f"- Flag: {flag.flag}",
        f"- Evidence: photo {flag.photo or '<none>'}, region {flag.region or '<unspecified>'}",
        f"- Cross-ref: {flag.cross_ref_note}",
        f"- Confidence: {flag.confidence}",
        f"- Recommended next step (inspection-first): {flag.inspection}",
        "- Chemicals: none recommended here; if needed, follow label-compliant local guidance.",
    ])


def render_report(flags: list, risk: dict, today: str) -> str:
    if not flags:
        return (
            "## Health pass — no flags\n\n"
            "No anomalies triaged from the supplied observations. Keep monitoring; "
            "re-run if the plant looks off.\n"
        )
    lines = ["## Health pass\n", f"_Screening only — not a diagnosis. {len(flags)} flag(s)._\n"]
    for f in flags:
        lines.append(render_flag_event(f, today))
        lines.append("")
    lines.append("## Structural-work risk")
    lines.append(f"- Risk: **{risk['risk']}** — {risk['reason']}")
    return "\n".join(lines) + "\n"


def _load_input(path: str | None) -> dict:
    raw = sys.stdin.read() if not path else open(path, "r", encoding="utf-8").read()
    return json.loads(raw)


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Triage plant-health observations into flags.")
    parser.add_argument("--input", help="JSON file of observations/care_events/today (else stdin).")
    args = parser.parse_args(argv)
    try:
        data = _load_input(args.input)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    today = data.get("today") or _dt.date.today().isoformat()
    flags = triage(data.get("observations", []), data.get("care_events", []), today)
    risk = structural_risk(flags)
    sys.stdout.write(render_report(flags, risk, today))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
