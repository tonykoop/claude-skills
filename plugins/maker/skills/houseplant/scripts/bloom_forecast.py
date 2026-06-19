#!/usr/bin/env python3
"""Bloom-window forecast helper (#173 bud/bloom chrono-tracker).

The pink-marker workflow needs no new script (it reuses cut_marker.py). This is
the optional *prediction* helper the issue asks for ("build the prediction
logic ... make the forecast confidence explicit — don't oversell"). It turns the
order-of-evidence documented in `references/bud-bloom-tracker.md` into a
deterministic, testable forecast:

  1. The plant's OWN historical bud->bloom intervals win (best predictor).
  2. Species baseline range is the fallback.
  3. Current conditions (warm/cool) modulate the window.

It always returns a RANGE, never a single date, and labels confidence honestly:
own-log >=3 -> high, own-log 1-2 -> medium, species-baseline-only -> low,
unknown species with no log -> low + an explicit "provisional / confirm species"
caveat. Pure stdlib; no Blender.

Input (JSON via --input FILE or stdin):
    {
      "plant_id": "phal-01", "event": "swelling bud", "location": "spike tip",
      "stage": "swelling", "species": "phalaenopsis", "condition": "warm",
      "history_intervals_days": [16, 19],   // this plant's prior bud->open gaps
      "anchor_date": "2026-06-18"            // when the bud was observed
    }

CLI:
    bloom_forecast.py --input bud.json
    cat bud.json | bloom_forecast.py
Exit 0 = forecast produced, 2 = bad input.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import statistics
import sys

# Species baseline: (min_days, max_days) from a visibly swelling bud to open
# flower. Ranges from references/bud-bloom-tracker.md (weeks -> days). Wide on
# purpose — light/temperature dominate.
SPECIES_BASELINE_DAYS: dict[str, tuple[int, int]] = {
    "phalaenopsis": (7, 21),     # swelling bud -> open ~1-3 wk
    "hoya": (21, 42),            # peduncle/spur -> open umbel ~3-6 wk
    "jade": (14, 28),            # Crassula buds -> bloom ~2-4 wk
    "crassula": (14, 28),
    "schlumbergera": (28, 56),   # visible bud -> open ~4-8 wk
    "christmas-cactus": (28, 56),
    "citrus": (14, 35),          # bud -> open ~2-5 wk warm
    "carmona": (14, 35),
}
GENERIC_BASELINE_DAYS = (14, 42)  # unknown species: deliberately wide

# Warmth/light shortens the window; cool/dim lengthens it.
CONDITION_FACTOR = {"warm": 0.85, "neutral": 1.0, "cool": 1.15}


def species_baseline(species: str) -> tuple[int, int] | None:
    if not species:
        return None
    return SPECIES_BASELINE_DAYS.get(species.strip().lower())


def modulate(window: tuple[float, float], condition: str) -> tuple[int, int]:
    factor = CONDITION_FACTOR.get((condition or "neutral").strip().lower(), 1.0)
    lo = max(1, round(window[0] * factor))
    hi = max(lo + 1, round(window[1] * factor))  # never collapse to a single day
    return lo, hi


def _from_history(history: list) -> tuple[tuple[float, float], str]:
    """Return ((lo,hi) day-window, confidence) from this plant's own intervals."""
    vals = [float(v) for v in history if isinstance(v, (int, float)) and v > 0]
    if not vals:
        return (0.0, 0.0), "none"
    if len(vals) >= 2:
        lo, hi = min(vals), max(vals)
        if hi - lo < 2:  # tight cluster: widen slightly so it stays a range
            mean = statistics.mean(vals)
            lo, hi = mean * 0.9, mean * 1.1
        confidence = "high" if len(vals) >= 3 else "medium"
        return (lo, hi), confidence
    # single data point: ±20% band, medium-low -> medium
    v = vals[0]
    return (v * 0.8, v * 1.2), "medium"


def forecast(history: list, species: str, condition: str, anchor_date: str) -> dict:
    own, own_conf = _from_history(history or [])
    if own_conf != "none":
        base_window, confidence, basis = own, own_conf, "your-own-log"
        caveat = "based on this plant's own bloom history — the strongest predictor."
    else:
        baseline = species_baseline(species)
        if baseline is not None:
            base_window, confidence, basis = baseline, "low", "species-baseline-only"
            caveat = "species-baseline-only and provisional (no prior log for this plant); a range, not a date."
        else:
            base_window, confidence, basis = GENERIC_BASELINE_DAYS, "low", "no-log-unknown-species"
            caveat = "no prior log and unrecognized species — confirm the species; this is a very rough range."

    lo, hi = modulate(base_window, condition)
    anchor = _dt.date.fromisoformat(anchor_date)
    width = hi - lo
    cadence = max(3, min(14, round(max(lo, width) / 3)))
    return {
        "low_days": lo,
        "high_days": hi,
        "window_start": (anchor + _dt.timedelta(days=lo)).isoformat(),
        "window_end": (anchor + _dt.timedelta(days=hi)).isoformat(),
        "confidence": confidence,
        "basis": basis,
        "cadence_days": cadence,
        "caveat": caveat,
    }


def render(data: dict, fc: dict) -> str:
    plant = data.get("plant_id", "<plant_id>")
    event = data.get("event", "bud")
    today = data.get("anchor_date", _dt.date.today().isoformat())
    return "\n".join([
        f"## Bloom Forecast — {plant} — {today}",
        f"- Event: {event} at {data.get('location', '<location>')}",
        f"- Stage: {data.get('stage', '<stage>')}",
        f"- Forecast window: {fc['window_start']} … {fc['window_end']} "
        f"({fc['low_days']}–{fc['high_days']} days out)",
        f"- Confidence: {fc['confidence']} — based on {fc['basis']}. {fc['caveat']}",
        f"- Marker: pink, {plant}_bud_marker_<branch_id>_{today}",
        "- Care to protect it: stable light/temp, avoid moving it, steady moisture.",
        f"- Calendar check: \"Photograph {plant} {event} every {fc['cadence_days']} "
        "days until open.\"",
    ]) + "\n"


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Forecast a bloom window from logs + species baseline.")
    parser.add_argument("--input", help="JSON file (else stdin).")
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read() if not args.input else open(args.input, encoding="utf-8").read()
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    anchor = data.get("anchor_date") or _dt.date.today().isoformat()
    try:
        _dt.date.fromisoformat(anchor)
    except ValueError:
        print(f"error: bad anchor_date {anchor!r}", file=sys.stderr)
        return 2
    data["anchor_date"] = anchor
    fc = forecast(data.get("history_intervals_days", []), data.get("species", ""),
                  data.get("condition", "neutral"), anchor)
    sys.stdout.write(render(data, fc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
