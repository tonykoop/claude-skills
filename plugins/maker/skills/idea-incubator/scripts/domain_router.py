#!/usr/bin/env python3
"""Confidence-weighted domain-label routing for HWE/maker captures.

Refs #242 (Epic #235). The pre-tune-up router (the inline `route_labels` in
`gemini_to_github.py`) applied a domain label on ANY single keyword substring
hit — so an incidental word ("bore" inside "before") confidently mislabeled a
capture, and short tokens ("app" in "happen", "mill" in "million") fired
constantly. With the export pipeline making captures hands-off, those mislabels
are the new bottleneck.

This module implements the tuned ruleset documented in
`references/domain-label-routing.md`:

* **Weighted signals.** Generic keyword = 1, strong/unambiguous signal = 3.
* **Word-boundary matching** for single-word signals (phrases stay substring),
  killing the false positives that drove the baseline's mislabels.
* **Confidence thresholds.** score >= 2 → confident (apply the label); score == 1
  → tentative (apply the label AND `needs-clarification`); score == 0 → the
  domain does not fire.
* **Hybrid umbrella.** When any hardware/maker domain fires, add `maker`.
* **Safe fallback.** An unroutable capture gets `needs-clarification`, never
  nothing — an HWE/maker capture is never left unlabeled.

The ruleset is data (`SIGNALS`) so it extends without touching logic. Keep it in
lockstep with the routing-table doc.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

CAPTURE_LABEL = "capture"
NEEDS_TRIAGE_LABEL = "needs-clarification"
UMBRELLA_LABEL = "maker"
STRONG = 3
WEAK = 1

# Domains whose firing pulls in the `maker` umbrella label (shop-floor work).
HARDWARE_DOMAINS = {"instrument", "woodworking", "sheet-metal", "electronics", "firmware", "maker"}

# (signal, weight) per domain — mirrors references/domain-label-routing.md.
# Strong (weight-3) signals are unambiguous; weak (weight-1) are generic.
SIGNALS: dict[str, list[tuple[str, int]]] = {
    "instrument": [
        ("flute", WEAK), ("didgeridoo", WEAK), ("harp", WEAK), ("drum", STRONG),
        ("reed", WEAK), ("fipple", WEAK), ("bore", WEAK), ("tuning", WEAK),
        ("acoustic", WEAK), ("soundboard", WEAK), ("string tension", WEAK),
    ],
    "woodworking": [
        ("wood", WEAK), ("plywood", WEAK), ("hardwood", WEAK), ("joinery", STRONG),
        ("dovetail", WEAK), ("lathe", WEAK), ("router table", WEAK), ("cabinet", WEAK),
        ("glue-up", WEAK), ("grain", WEAK),
    ],
    "sheet-metal": [
        ("sheet metal", STRONG), ("brake", WEAK), ("bend allowance", STRONG),
        ("flat pattern", STRONG), ("plasma", WEAK), ("shear", WEAK),
        ("slip-roll", WEAK), ("weld", WEAK), ("gauge", WEAK),
    ],
    "electronics": [
        ("pcb", STRONG), ("pcba", STRONG), ("schematic", WEAK), ("gerber", WEAK),
        ("microcontroller", STRONG), ("mcu", WEAK), ("sensor", WEAK), ("i2c", WEAK),
        ("spi", WEAK), ("voltage", WEAK), ("circuit", WEAK),
    ],
    "firmware": [
        ("firmware", STRONG), ("flash", WEAK), ("bootloader", WEAK), ("rtos", WEAK),
        ("embedded", WEAK), ("register", WEAK), ("interrupt", WEAK), ("hal", WEAK),
    ],
    "software": [
        ("app", WEAK), ("api", WEAK), ("webhook", STRONG), ("script", WEAK),
        ("cli", WEAK), ("automation", WEAK), ("database", WEAK), ("frontend", WEAK),
        ("backend", WEAK), ("service", WEAK),
    ],
    "yoga": [
        ("yoga", STRONG), ("vinyasa", STRONG), ("asana", WEAK), ("pose", WEAK),
        ("sequence", WEAK), ("peak pose", WEAK), ("savasana", WEAK),
    ],
    "maker": [
        ("jig", WEAK), ("fixture", WEAK), ("workholding", WEAK), ("mold", WEAK),
        ("cnc", WEAK), ("laser cutter", WEAK), ("3d print", WEAK), ("mill", WEAK),
        ("fabricate", WEAK),
    ],
}


@dataclass
class RouteResult:
    labels: list[str]
    scores: dict[str, int] = field(default_factory=dict)
    confident: list[str] = field(default_factory=list)
    tentative: list[str] = field(default_factory=list)
    unroutable: bool = False


def _matches(signal: str, text_low: str) -> bool:
    """Phrase signals (with a space/hyphen/digit) match as substring; single
    words match on a word boundary so 'app' does not fire inside 'happen'."""
    if re.search(r"[\s-]", signal) or any(ch.isdigit() for ch in signal):
        return signal in text_low
    return re.search(rf"\b{re.escape(signal)}\b", text_low) is not None


def score_domains(text: str) -> dict[str, int]:
    text_low = text.lower()
    scores: dict[str, int] = {}
    for domain, signals in SIGNALS.items():
        total = sum(weight for sig, weight in signals if _matches(sig, text_low))
        if total:
            scores[domain] = total
    return scores


def classify(text: str) -> RouteResult:
    scores = score_domains(text)
    # Preserve SIGNALS declaration order for deterministic, stable label output.
    order = list(SIGNALS.keys())
    confident = sorted((d for d, s in scores.items() if s >= 2), key=order.index)
    tentative = sorted((d for d, s in scores.items() if s == 1), key=order.index)

    labels = [CAPTURE_LABEL]
    labels.extend(confident)
    labels.extend(tentative)
    if any(d in HARDWARE_DOMAINS for d in confident + tentative):
        if UMBRELLA_LABEL not in labels:
            labels.append(UMBRELLA_LABEL)
    unroutable = not confident and not tentative
    if tentative or unroutable:
        labels.append(NEEDS_TRIAGE_LABEL)

    # Dedup while preserving order.
    seen: dict[str, None] = {}
    deduped = [lbl for lbl in labels if not (lbl in seen or seen.setdefault(lbl, None))]
    return RouteResult(
        labels=deduped, scores=scores, confident=confident, tentative=tentative, unroutable=unroutable
    )


def route_labels(text: str) -> list[str]:
    """Convenience: just the labels for a capture (always includes `capture`)."""
    return classify(text).labels
