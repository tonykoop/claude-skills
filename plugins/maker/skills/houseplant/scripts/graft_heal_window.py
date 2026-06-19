#!/usr/bin/env python3
"""Graft heal-window + risk estimator for the virtual grafting sandbox (#176).

`grafting_sim.py` builds the fused *silhouette* in Blender, but the reference
(`references/grafting-sandbox.md`) also asks every graft preview to state two
things the geometry can't:

  - **Heal expectation** — "real fusion takes <range> of warm-season growth"
    (the multi-year heal window the silhouette is the end-state of); and
  - **Risk** — Medium on a healthy vigorous fusing species, High on a weak /
    pest-flagged plant or a species that does not fuse readily.

This pure-Python helper computes both deterministically so the preview's
narration and calendar follow-ups are consistent and testable. It does NOT
simulate biology — it returns conservative ranges with explicit confidence.

Input (JSON via --input FILE or stdin):
    {
      "graft_type": "approach",           // approach | trunk-patch | multi-tree-fusion
      "species_fusion": "readily",        // readily | moderate | poorly
      "condition": "warm",                // warm | neutral | cool
      "health": "healthy",                // healthy | weak | pest-flagged
      "grafted_date": "2026-06-18",
      "plant_id": "ficus-benjamina-01"
    }

CLI:
    graft_heal_window.py --input graft.json
Exit 0 = rendered, 2 = bad input.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys

DAYS_PER_MONTH = 30.44

# Base heal window (min_months, max_months) of warm-season growth by graft type,
# for a readily-fusing species. Approach grafts (both partners stay alive) unite
# fastest; multi-tree fusion of several trunks is the slowest, longest project.
GRAFT_TYPE_MONTHS: dict[str, tuple[int, int]] = {
    "approach": (12, 24),
    "trunk-patch": (18, 36),
    "multi-tree-fusion": (24, 48),
}
# How readily the species fuses scales the window (and gates risk).
FUSION_FACTOR = {"readily": 1.0, "moderate": 1.5, "poorly": 2.5}
# Fusion only advances in warm, active growth; cool/short seasons stretch it.
CONDITION_FACTOR = {"warm": 0.85, "neutral": 1.0, "cool": 1.25}

WEAK_HEALTH = {"weak", "pest-flagged", "stressed"}


def heal_window(graft_type: str, species_fusion: str, condition: str, grafted_date: str) -> dict:
    base = GRAFT_TYPE_MONTHS.get((graft_type or "").strip().lower())
    if base is None:
        base, confidence, note = (18, 36), "low", f"unknown graft type {graft_type!r}; using a generic range"
    else:
        confidence, note = "medium", "conservative range; real fusion is driven by warm-season vigor"
    fusion = (species_fusion or "readily").strip().lower()
    factor = FUSION_FACTOR.get(fusion, 1.5) * CONDITION_FACTOR.get((condition or "neutral").strip().lower(), 1.0)
    if fusion == "poorly":
        confidence = "low"
        note = "species fuses poorly — treat the preview as aspirational; fusion may never complete"
    lo = max(1, round(base[0] * factor))
    hi = max(lo + 1, round(base[1] * factor))
    anchor = _dt.date.fromisoformat(grafted_date)
    return {
        "low_months": lo, "high_months": hi,
        "window_start": (anchor + _dt.timedelta(days=round(lo * DAYS_PER_MONTH))).isoformat(),
        "window_end": (anchor + _dt.timedelta(days=round(hi * DAYS_PER_MONTH))).isoformat(),
        "confidence": confidence, "note": note,
    }


def risk_verdict(species_fusion: str, health: str) -> dict:
    fusion = (species_fusion or "readily").strip().lower()
    h = (health or "healthy").strip().lower()
    if h in WEAK_HEALTH:
        return {"risk": "High", "reason": (
            f"plant is {h}: fusion grafting on a weak/pest-flagged plant is High risk — "
            "resolve health first and defer the cut (preview only for now)")}
    if fusion == "poorly":
        return {"risk": "High", "reason": (
            "species does not fuse readily: High risk of a failed/visible union — "
            "preview the silhouette but do not commit the cut")}
    return {"risk": "Medium", "reason": "healthy vigorous, readily/moderately fusing species: Medium risk"}


def render(data: dict, hw: dict, risk: dict) -> str:
    plant = data.get("plant_id", "<plant_id>")
    today = data.get("grafted_date", _dt.date.today().isoformat())
    return "\n".join([
        f"## Graft Heal Window — {plant} — {today}",
        f"- Graft type: {data.get('graft_type', '<type>')} · "
        f"Species fusion: {data.get('species_fusion', 'readily')} · "
        f"Conditions: {data.get('condition', 'neutral')}",
        f"- Heal expectation: silhouette is the multi-year end-state; real fusion takes "
        f"~{hw['low_months']}–{hw['high_months']} months of warm-season growth "
        f"({hw['window_start']} … {hw['window_end']}), confidence {hw['confidence']}",
        f"- Note: {hw['note']}",
        f"- Risk: {risk['risk']} — {risk['reason']}",
        "- Reminder: this is a simulation-only preview in 05_simulations/; "
        "it never touches the current-state twin.",
    ]) + "\n"


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Estimate a graft heal window + risk.")
    parser.add_argument("--input", help="JSON file (else stdin).")
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read() if not args.input else open(args.input, encoding="utf-8").read()
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    grafted = data.get("grafted_date") or _dt.date.today().isoformat()
    try:
        _dt.date.fromisoformat(grafted)
    except ValueError:
        print(f"error: bad grafted_date {grafted!r}", file=sys.stderr)
        return 2
    data["grafted_date"] = grafted
    hw = heal_window(data.get("graft_type", ""), data.get("species_fusion", "readily"),
                     data.get("condition", "neutral"), grafted)
    risk = risk_verdict(data.get("species_fusion", "readily"), data.get("health", "healthy"))
    sys.stdout.write(render(data, hw, risk))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
