#!/usr/bin/env python3
"""Savasana-backward planning engine — design the stillness first, earn it second.

Class design starts from a SavasanaSpec (the somatic quality of rest the students
should land in) and subtracts toward the minimum disturbance: the smallest set of
movements whose absence would leave the stillness unearned.  The default
peak-pose arc is inverted — savasana is the design target, everything else is
justified only by how precisely it produces that specific rest.

Usage::

    python3 savasana_backward.py spec.json --reviewer tk
    python3 savasana_backward.py spec.json --json   # machine-readable output
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Minimum-disturbance catalog
#
# Each release maps to a ranked list of movements that address it.  The first
# entry is the minimum — the engine prefers it unless a higher-ranked movement
# already covers a second release (combinatorial economy).
# ---------------------------------------------------------------------------
_RELEASE_CATALOG: dict[str, list[dict[str, Any]]] = {
    "hip_flexors": [
        {
            "token": "CL",
            "name": "Crescent Lunge",
            "also_addresses": [],
            "min_duration_min": 1,
            "bilateral": True,
        },
        {
            "token": "LL",
            "name": "Low Lunge",
            "also_addresses": ["quad_top"],
            "min_duration_min": 1,
            "bilateral": True,
        },
    ],
    "hamstrings": [
        {
            "token": "FF",
            "name": "Forward Fold",
            "also_addresses": ["low_back_traction"],
            "min_duration_min": 1,
            "bilateral": False,
        },
        {
            "token": "PT",
            "name": "Pyramid",
            "also_addresses": ["hip_flexors"],
            "min_duration_min": 1,
            "bilateral": True,
        },
    ],
    "thoracic_spine": [
        {
            "token": "CC",
            "name": "Cat-Cow",
            "also_addresses": ["low_back_traction"],
            "min_duration_min": 1,
            "bilateral": False,
        },
        {
            "token": "TN",
            "name": "Thread the Needle",
            "also_addresses": ["shoulder_girdle"],
            "min_duration_min": 1,
            "bilateral": True,
        },
    ],
    "hip_external_rotation": [
        {
            "token": "RF4",
            "name": "Reclined Figure Four",
            "also_addresses": ["low_back_traction"],
            "min_duration_min": 2,
            "bilateral": True,
        },
        {
            "token": "MAL",
            "name": "Malasana",
            "also_addresses": ["hip_flexors"],
            "min_duration_min": 1,
            "bilateral": False,
        },
    ],
    "shoulder_girdle": [
        {
            "token": "EAG",
            "name": "Eagle Arms",
            "also_addresses": [],
            "min_duration_min": 1,
            "bilateral": True,
        },
        {
            "token": "TN",
            "name": "Thread the Needle",
            "also_addresses": ["thoracic_spine"],
            "min_duration_min": 1,
            "bilateral": True,
        },
    ],
    "low_back_traction": [
        {
            "token": "HB",
            "name": "Happy Baby",
            "also_addresses": ["hip_external_rotation"],
            "min_duration_min": 2,
            "bilateral": False,
        },
        {
            "token": "KTC",
            "name": "Knees-to-Chest",
            "also_addresses": [],
            "min_duration_min": 1,
            "bilateral": False,
        },
    ],
    "quad_top": [
        {
            "token": "LL",
            "name": "Low Lunge",
            "also_addresses": ["hip_flexors"],
            "min_duration_min": 1,
            "bilateral": True,
        },
    ],
    "wrists": [
        {
            "token": "WW",
            "name": "Wrist Warm-up",
            "also_addresses": [],
            "min_duration_min": 1,
            "bilateral": False,
        },
    ],
}

# Movements whose warm-up is required before the primary release work.
_WARM_UP_REQUIREMENTS: dict[str, list[str]] = {
    "hip_flexors": ["CC"],
    "hamstrings": ["CC", "DD"],
    "thoracic_spine": ["CC"],
    "hip_external_rotation": ["CC", "DD"],
    "shoulder_girdle": ["CC"],
    "low_back_traction": [],
    "quad_top": ["CC"],
    "wrists": [],
}

# Ordering weight for phase assignment — lower = earlier in the class arc.
_PHASE_ORDER: dict[str, int] = {
    "CC": 1, "DD": 1, "WW": 1,
    "TN": 2,
    "EAG": 2,
    "MAL": 3, "CL": 3, "LL": 3,
    "FF": 3, "PT": 3,
    "RF4": 4, "HB": 4, "KTC": 4,
}


class SavasanaBackwardError(ValueError):
    """Raised when the spec cannot produce a valid class plan."""


@dataclass
class SavasanaSpec:
    """The somatic target a class is reverse-engineered to produce.

    Attributes:
        target_releases: Named release categories the savasana landing should
            include, e.g. ``["hip_flexors", "hamstrings"]``.
        rest_quality: Somatic descriptors the body should carry into final rest,
            e.g. ``["symmetric_weight", "breath_below_ribs"]``.
        emotional_landing: One phrase capturing the felt sense at arrival,
            e.g. ``"earned ease"`` or ``"quiet awareness"``.
        duration_min: Minutes in savasana (excluded from the working class).
        class_length_min: Total class length.
        level: Student level — used in quality-gate and output metadata.
        reviewer: Named human reviewer who approved this spec for teaching.
    """

    target_releases: list[str]
    rest_quality: list[str]
    emotional_landing: str
    duration_min: int = 4
    class_length_min: int = 60
    level: str = "mixed-level"
    reviewer: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SavasanaSpec":
        return cls(
            target_releases=data["target_releases"],
            rest_quality=data.get("rest_quality", []),
            emotional_landing=data.get("emotional_landing", "earned ease"),
            duration_min=int(data.get("duration_min", 4)),
            class_length_min=int(data.get("class_length_min", 60)),
            level=data.get("level", "mixed-level"),
            reviewer=data.get("reviewer", ""),
        )


@dataclass
class PlannedMovement:
    token: str
    name: str
    justification: str
    bilateral: bool
    min_duration_min: int
    addresses: list[str] = field(default_factory=list)
    phase_order: int = 0


class SavasanaBackwardEngine:
    """Reverse-engineer a class from a savasana spec.

    The engine:
    1. Resolves the minimum-disturbance set — the fewest movements that address
       every requested release.
    2. Adds required warm-up movements.
    3. Orders movements by phase weight.
    4. Assigns phase timing.
    5. Applies a justification filter — every movement must state why its
       absence would leave the stillness unearned.
    6. Runs quality gates and emits the class plan.
    """

    def generate(self, spec: SavasanaSpec) -> dict[str, Any]:
        if not spec.target_releases:
            raise SavasanaBackwardError("SavasanaSpec must name at least one target_release.")
        unknown = [r for r in spec.target_releases if r not in _RELEASE_CATALOG]
        if unknown:
            raise SavasanaBackwardError(
                f"Unknown release categories: {unknown}. "
                f"Available: {sorted(_RELEASE_CATALOG)}"
            )

        movements = self._minimum_disturbance_set(spec)
        movements = self._add_warm_up(movements, spec)
        movements = sorted(movements, key=lambda m: m.phase_order)
        phases = self._assign_phases(movements, spec)
        findings = self._quality_gate_findings(movements, phases, spec)

        return {
            "mode": "savasana_backward",
            "savasana_spec": {
                "target_releases": spec.target_releases,
                "rest_quality": spec.rest_quality,
                "emotional_landing": spec.emotional_landing,
                "duration_min": spec.duration_min,
            },
            "class_summary": {
                "length_min": spec.class_length_min,
                "level": spec.level,
                "design_principle": (
                    "Every movement is justified only by its contribution to the "
                    f"savasana landing: {spec.emotional_landing}."
                ),
            },
            "minimum_disturbance_set": [
                {
                    "token": m.token,
                    "name": m.name,
                    "bilateral": m.bilateral,
                    "addresses": m.addresses,
                    "justification": m.justification,
                }
                for m in movements
            ],
            "phases": phases,
            "playlist_phase_map": [
                {
                    "phase": p["name"],
                    "start_min": p["start_min"],
                    "end_min": p["end_min"],
                    "energy": p["energy"],
                    "cue_density": p["cue_density"],
                }
                for p in phases
            ],
            "quality_gate": {
                "trusted_for_teaching": not findings,
                "status": "approved" if not findings else "needs_human_review",
                "findings": findings,
            },
        }

    # ------------------------------------------------------------------
    # Core algorithm
    # ------------------------------------------------------------------

    def _minimum_disturbance_set(self, spec: SavasanaSpec) -> list[PlannedMovement]:
        """Pick the fewest movements that address every requested release.

        Greedy economy pass: prefer movements that address multiple releases
        (combinatorial gain).  A second movement covering an already-addressed
        release is suppressed unless it is the only option for another release.
        """
        addressed: set[str] = set()
        chosen: dict[str, PlannedMovement] = {}  # keyed by token to avoid duplicates

        # Sort releases by how many candidates can double-cover them (rarest first).
        def coverage_count(release: str) -> int:
            return sum(
                1
                for m in _RELEASE_CATALOG.get(release, [])
                if any(r not in addressed for r in [release] + m["also_addresses"])
            )

        remaining = list(spec.target_releases)
        while remaining:
            remaining.sort(key=coverage_count)
            release = remaining.pop(0)
            if release in addressed:
                continue
            candidates = _RELEASE_CATALOG[release]
            # Pick the candidate that covers the most un-addressed releases.
            best = max(
                candidates,
                key=lambda m: len(
                    {release} | {r for r in m["also_addresses"] if r in spec.target_releases}
                    - addressed
                ),
            )
            token = best["token"]
            if token not in chosen:
                all_covered = {release} | {
                    r for r in best["also_addresses"] if r in spec.target_releases
                }
                chosen[token] = PlannedMovement(
                    token=token,
                    name=best["name"],
                    justification=self._justification(all_covered, spec),
                    bilateral=best["bilateral"],
                    min_duration_min=best["min_duration_min"],
                    addresses=sorted(all_covered),
                    phase_order=_PHASE_ORDER.get(token, 3),
                )
                addressed |= all_covered
            else:
                # Token already chosen for another release — mark it as also addressing this.
                existing = chosen[token]
                if release not in existing.addresses:
                    existing.addresses.append(release)
                    existing.justification = self._justification(
                        set(existing.addresses), spec
                    )
                addressed.add(release)

        return list(chosen.values())

    def _add_warm_up(
        self, movements: list[PlannedMovement], spec: SavasanaSpec
    ) -> list[PlannedMovement]:
        """Prepend essential warm-up tokens not already in the set."""
        existing_tokens = {m.token for m in movements}
        required_tokens: set[str] = set()
        for release in spec.target_releases:
            required_tokens.update(_WARM_UP_REQUIREMENTS.get(release, []))
        extra: list[PlannedMovement] = []
        for token in sorted(required_tokens - existing_tokens):
            name = {
                "CC": "Cat-Cow",
                "DD": "Downward Dog",
                "WW": "Wrist Warm-up",
            }.get(token, token)
            extra.append(
                PlannedMovement(
                    token=token,
                    name=name,
                    justification=(
                        "Warm-up prerequisite: without this the joints are cold "
                        "and the primary release work is unsafe or ineffective."
                    ),
                    bilateral=False,
                    min_duration_min=1,
                    addresses=["warm_up"],
                    phase_order=_PHASE_ORDER.get(token, 1),
                )
            )
        return movements + extra

    def _assign_phases(
        self, movements: list[PlannedMovement], spec: SavasanaSpec
    ) -> list[dict[str, Any]]:
        """Distribute movements across a 4-phase arc ending in savasana."""
        work_min = spec.class_length_min - spec.duration_min
        # Phase boundaries (proportional to a 60-min arc, scaled to actual length).
        phase_defs = [
            ("arrival_warm_up", 0, 0.20, "low", "sparse"),
            ("release_work", 0.20, 0.60, "medium", "moderate"),
            ("integration_cooldown", 0.60, 0.90, "low", "sparse"),
            ("savasana", 0.90, 1.00, "rest", "minimal"),
        ]
        # Override the savasana boundary so it always fills the spec duration.
        savasana_start = work_min
        results: list[dict[str, Any]] = []
        for i, (name, frac_start, frac_end, energy, cue_density) in enumerate(phase_defs):
            if name == "savasana":
                start_min = savasana_start
                end_min = spec.class_length_min
            else:
                start_min = round(work_min * frac_start)
                end_min = round(work_min * frac_end)
            # Assign movements to phases by phase_order bucket.
            buckets = {
                "arrival_warm_up": {1},
                "release_work": {2, 3},
                "integration_cooldown": {4},
                "savasana": set(),
            }
            phase_movements = [m for m in movements if m.phase_order in buckets.get(name, set())]
            pose_names = [m.name for m in phase_movements]
            if name == "savasana":
                pose_names = ["Savasana"]
            results.append(
                {
                    "name": name,
                    "start_min": start_min,
                    "end_min": end_min,
                    "energy": energy,
                    "cue_density": cue_density,
                    "intent": self._phase_intent(name, spec),
                    "poses": pose_names,
                }
            )
        return results

    def _justification(self, releases: set[str], spec: SavasanaSpec) -> str:
        landing = spec.emotional_landing
        names = " and ".join(sorted(releases))
        return (
            f"Addresses {names}. Without this, the body arrives at savasana "
            f"with residual tension that prevents '{landing}'."
        )

    def _phase_intent(self, name: str, spec: SavasanaSpec) -> str:
        intents = {
            "arrival_warm_up": (
                "Mobilise joints and wake up the breath. "
                "No disturbance yet — only the minimum heat required to make release work safe."
            ),
            "release_work": (
                f"Address the target releases ({', '.join(spec.target_releases)}) "
                f"with the minimum number of movements. "
                "Each pose is present because its absence would leave the stillness unearned."
            ),
            "integration_cooldown": (
                "Let the release work settle. "
                "Cues become scarcer — the body needs silence to integrate."
            ),
            "savasana": (
                f"Final rest: {spec.emotional_landing}. "
                f"Qualities to carry in: {', '.join(spec.rest_quality) or 'open'}."
            ),
        }
        return intents[name]

    # ------------------------------------------------------------------
    # Quality gate
    # ------------------------------------------------------------------

    def _quality_gate_findings(
        self,
        movements: list[PlannedMovement],
        phases: list[dict[str, Any]],
        spec: SavasanaSpec,
    ) -> list[str]:
        findings: list[str] = []
        if not spec.reviewer:
            findings.append("named human reviewer approval required before teaching")
        if not spec.rest_quality:
            findings.append(
                "rest_quality is empty — specify at least one somatic descriptor "
                "so the savasana cue has concrete language"
            )
        # Bilateral symmetry: bilateral movements must appear once (the engine
        # treats one entry as covering both sides — the teacher cues both).
        bilateral_names = [m.name for m in movements if m.bilateral]
        if bilateral_names and len(set(bilateral_names)) < len(bilateral_names):
            findings.append("duplicate bilateral movement detected — check the spec")
        # Every release must be addressed.
        addressed = {r for m in movements for r in m.addresses if r != "warm_up"}
        unaddressed = set(spec.target_releases) - addressed
        if unaddressed:
            findings.append(f"releases not covered by any movement: {sorted(unaddressed)}")
        # Phase map must cover the full class length.
        if phases and phases[-1]["end_min"] != spec.class_length_min:
            findings.append("phase map does not sum to class_length_min")
        return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Savasana-backward class planner: design the stillness first."
    )
    parser.add_argument(
        "spec_file",
        type=Path,
        help="JSON file containing a SavasanaSpec (see references/savasana-backward.md).",
    )
    parser.add_argument("--reviewer", default="", help="Named human reviewer.")
    parser.add_argument(
        "--json", dest="json_out", action="store_true", help="Emit raw JSON."
    )
    args = parser.parse_args(argv)

    data = json.loads(args.spec_file.read_text(encoding="utf-8"))
    if args.reviewer:
        data["reviewer"] = args.reviewer

    spec = SavasanaSpec.from_dict(data)
    result = SavasanaBackwardEngine().generate(spec)

    if args.json_out:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Mode: {result['mode']}")
        print(f"Level: {result['class_summary']['level']}")
        print(f"Design principle: {result['class_summary']['design_principle']}")
        print(f"\nSavasana target: {spec.emotional_landing}")
        print(f"Rest qualities:   {', '.join(spec.rest_quality) or '(none specified)'}")
        print(f"\nMinimum disturbance set ({len(result['minimum_disturbance_set'])} movements):")
        for m in result["minimum_disturbance_set"]:
            sides = " (bilateral)" if m["bilateral"] else ""
            print(f"  [{m['token']}] {m['name']}{sides}")
            print(f"       → {m['justification']}")
        print("\nPhases:")
        for p in result["phases"]:
            poses = ", ".join(p["poses"]) if p["poses"] else "—"
            print(
                f"  {p['start_min']:02d}-{p['end_min']:02d}  {p['name']:<25}  "
                f"cue:{p['cue_density']:<8}  {poses}"
            )
        gate = result["quality_gate"]
        print(f"\nQuality gate: {gate['status']}")
        if gate["findings"]:
            for f in gate["findings"]:
                print(f"  ! {f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
