"""Rule-based health assessment for houseplant and bonsai specimens.

assess_health() is a pure function over Observations — no side effects, no I/O.
The rules are ordered from most-severe to least-severe so the returned status
reflects the worst condition observed.
"""
from __future__ import annotations

from .models import HealthState, Observations, Specimen


def assess_health(specimen: Specimen, observations: Observations) -> HealthState:
    """Assess specimen health from a set of visual observations.

    Rules (evaluated in order; first match wins for status):
      - DECLINING: pests present, OR (yellowing AND drooping), OR leaf_drop
      - NEEDS-ATTENTION: yellowing, OR drooping, OR dry_soil, OR mold
      - HEALTHY: none of the above

    Args:
        specimen:      The target plant (available for future per-species rule
                       overrides; not yet used in v1 rule set).
        observations:  Boolean flags from a visual inspection pass.

    Returns:
        HealthState with status, a list of triggered flag names, and a
        human-readable notes string.
    """
    flags: list[str] = []
    status = "healthy"

    # Collect all triggered observation flags first.
    if observations.pests:
        flags.append("pests")
    if observations.yellowing:
        flags.append("yellowing")
    if observations.drooping:
        flags.append("drooping")
    if observations.dry_soil:
        flags.append("dry_soil")
    if observations.leaf_drop:
        flags.append("leaf_drop")
    if observations.mold:
        flags.append("mold")

    # Determine status from the collected flags (most-severe wins).
    if (
        observations.pests
        or (observations.yellowing and observations.drooping)
        or observations.leaf_drop
    ):
        status = "declining"
    elif (
        observations.yellowing
        or observations.drooping
        or observations.dry_soil
        or observations.mold
    ):
        status = "needs-attention"
    else:
        status = "healthy"

    if status == "declining":
        notes = (
            "Specimen shows signs of active decline. "
            "Isolate if pests are suspected; address root cause before styling work."
        )
    elif status == "needs-attention":
        notes = (
            "Specimen needs attention. "
            "Monitor closely and correct cultural conditions before invasive action."
        )
    else:
        notes = "No concerning observations. Continue routine care."

    return HealthState(status=status, flags=flags, notes=notes)
