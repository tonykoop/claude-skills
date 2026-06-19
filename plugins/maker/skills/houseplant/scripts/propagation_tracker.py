#!/usr/bin/env python3
"""Propagation tracker: lineage, lifecycle, and rooting-window forecast (#177).

The propagation reference (`references/propagation.md`) defines the lifecycle
(started -> rooted -> potted_up -> independent, or -> failed), the parent/child
lineage model (every propagule carries a `parent_plant_id`, child ids derived
from the parent), and a rooting-time estimate. This script makes the two
computable parts deterministic and testable:

  * **Lineage** — build the collection's family tree from `parent_plant_id`
    links; query a plant's ancestors and descendants; render an indented tree so
    "lineage across the collection" is actually visible (the issue's headline
    hand-off cue).
  * **Lifecycle** — validate/advance the propagule state machine.
  * **Rooting forecast** — estimate a rooting *window* (a range, never a single
    date) with explicit confidence from method + species + conditions, mirroring
    bloom_forecast.py / wire_window.py.

Pure stdlib; no Blender.

Input (JSON via --input FILE or stdin); either or both blocks:
    {
      "records": [
        {"plant_id": "ficus-01", "state": "independent"},
        {"plant_id": "ficus-01-c01", "parent_plant_id": "ficus-01", "state": "rooted"}
      ],
      "propagation": {"method": "tip-cutting", "species": "ficus", "condition": "warm",
                      "started_date": "2026-06-18"}
    }

CLI:
    propagation_tracker.py --input prop.json
Exit 0 = rendered, 2 = bad input.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys

LIFECYCLE = ["started", "rooted", "potted_up", "independent"]
TERMINAL = {"failed"}

# Rooting baselines (min_days, max_days) by method. Tip cuttings of ficus root in
# ~3-6 weeks warm; air-layering holds longer before separation.
ROOTING_BASELINE_DAYS: dict[str, tuple[int, int]] = {
    "tip-cutting": (21, 42),
    "stem-cutting": (21, 49),
    "water-propagation": (14, 35),
    "air-layering": (42, 84),
}
# Ficus roots a touch faster than the generic cutting baseline.
SPECIES_TUNING: dict[str, float] = {"ficus": 0.85}
CONDITION_FACTOR = {"warm": 0.85, "neutral": 1.0, "cool": 1.2}


# --- lifecycle --------------------------------------------------------------
def is_terminal(state: str) -> bool:
    return state in TERMINAL or state == LIFECYCLE[-1]


def next_state(state: str) -> str:
    if state in TERMINAL:
        raise ValueError(f"{state!r} is terminal; no next state")
    if state not in LIFECYCLE:
        raise ValueError(f"unknown state {state!r}")
    idx = LIFECYCLE.index(state)
    if idx == len(LIFECYCLE) - 1:
        raise ValueError(f"{state!r} is already the final state")
    return LIFECYCLE[idx + 1]


def valid_transition(src: str, dst: str) -> bool:
    if dst == "failed":
        return src in LIFECYCLE and src != "independent"  # can fail until independent
    try:
        return next_state(src) == dst
    except ValueError:
        return False


# --- lineage ----------------------------------------------------------------
def derive_child_id(parent_id: str, n: int) -> str:
    return f"{parent_id}-c{n:02d}"


def _by_id(records: list) -> dict:
    return {r["plant_id"]: r for r in records if r.get("plant_id")}


def ancestors(records: list, plant_id: str) -> list:
    """Parent chain from the immediate parent up to the root (excludes self)."""
    index = _by_id(records)
    chain: list = []
    seen = {plant_id}
    cur = index.get(plant_id, {}).get("parent_plant_id")
    while cur and cur not in seen:
        chain.append(cur)
        seen.add(cur)
        cur = index.get(cur, {}).get("parent_plant_id")
    return chain


def descendants(records: list, plant_id: str) -> list:
    """All transitive children of plant_id, breadth-first, deduped."""
    children_of: dict = {}
    for r in records:
        p = r.get("parent_plant_id")
        if p:
            children_of.setdefault(p, []).append(r["plant_id"])
    out: list = []
    seen = {plant_id}
    queue = list(children_of.get(plant_id, []))
    while queue:
        node = queue.pop(0)
        if node in seen:
            continue
        seen.add(node)
        out.append(node)
        queue.extend(children_of.get(node, []))
    return out


def build_forest(records: list) -> dict:
    """Return {root_id: nested-children-dict}. A parent_plant_id not present in
    records is treated as an external root so nothing is dropped."""
    index = _by_id(records)
    children_of: dict = {}
    roots: list = []
    for r in records:
        pid = r["plant_id"]
        parent = r.get("parent_plant_id")
        if parent and parent in index:
            children_of.setdefault(parent, []).append(pid)
        else:
            roots.append(pid)  # no parent, or parent is external/missing

    def subtree(node: str, seen: set) -> dict:
        if node in seen:
            return {}
        seen.add(node)
        return {c: subtree(c, seen) for c in sorted(children_of.get(node, []))}

    seen: set = set()
    return {r: subtree(r, seen) for r in sorted(dict.fromkeys(roots))}


def render_tree(records: list) -> str:
    index = _by_id(records)
    lines: list = ["## Propagation lineage"]

    def walk(tree: dict, depth: int) -> None:
        for node, kids in tree.items():
            state = index.get(node, {}).get("state", "?")
            lines.append(f"{'  ' * depth}- {node} [{state}]")
            walk(kids, depth + 1)

    forest = build_forest(records)
    if not forest:
        lines.append("- (no records)")
    else:
        walk(forest, 0)
    return "\n".join(lines) + "\n"


# --- rooting forecast -------------------------------------------------------
def rooting_forecast(method: str, species: str, condition: str, started_date: str) -> dict:
    base = ROOTING_BASELINE_DAYS.get((method or "").strip().lower())
    if base is None:
        base, confidence, note = (21, 49), "low", f"unknown method {method!r}; using a generic cutting range"
    else:
        confidence, note = "medium", "species/method baseline; warmth and humidity dominate the real time"
    factor = CONDITION_FACTOR.get((condition or "neutral").strip().lower(), 1.0)
    factor *= SPECIES_TUNING.get((species or "").strip().lower(), 1.0)
    lo = max(1, round(base[0] * factor))
    hi = max(lo + 1, round(base[1] * factor))
    anchor = _dt.date.fromisoformat(started_date)
    cadence = max(5, min(14, round(lo / 3)))
    return {
        "low_days": lo, "high_days": hi,
        "window_start": (anchor + _dt.timedelta(days=lo)).isoformat(),
        "window_end": (anchor + _dt.timedelta(days=hi)).isoformat(),
        "confidence": confidence, "note": note, "check_cadence_days": cadence,
    }


def render_rooting(prop: dict, fc: dict) -> str:
    return "\n".join([
        "## Rooting forecast",
        f"- Method: {prop.get('method', '?')} · Species: {prop.get('species', '?')} · "
        f"Conditions: {prop.get('condition', 'neutral')}",
        f"- Expected rooting: {fc['window_start']} … {fc['window_end']} "
        f"({fc['low_days']}–{fc['high_days']} days), confidence {fc['confidence']}",
        f"- Note: {fc['note']}",
        f"- Follow-up checks: inspect for roots every {fc['check_cadence_days']} days; "
        "keep warm + humid; do not tug the cutting.",
    ]) + "\n"


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Propagation lineage + rooting forecast.")
    parser.add_argument("--input", help="JSON file (else stdin).")
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read() if not args.input else open(args.input, encoding="utf-8").read()
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    out: list = []
    if data.get("records"):
        out.append(render_tree(data["records"]))
    prop = data.get("propagation")
    if prop:
        started = prop.get("started_date") or _dt.date.today().isoformat()
        try:
            _dt.date.fromisoformat(started)
        except ValueError:
            print(f"error: bad started_date {started!r}", file=sys.stderr)
            return 2
        out.append(render_rooting(prop, rooting_forecast(
            prop.get("method", ""), prop.get("species", ""), prop.get("condition", "neutral"), started)))
    if not out:
        print("error: provide 'records' and/or 'propagation' in the input", file=sys.stderr)
        return 2
    sys.stdout.write("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
