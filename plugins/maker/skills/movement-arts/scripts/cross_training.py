"""
Movement Arts — hybrid cross-training generator.

CrossTrainingGenerator(domains, weights, duration_min) → CrossTrainingRoutine

Interleaves blocks from 2+ domain sequencers under a shared tracker and
state machine so weight/facing rules are respected across domain boundaries.

Named presets (loaded from references/cross-training-presets.json or inline):
  "vinyasa-capoeira" : 50/50 breath clock, breath_alignment objective
  "martial-beats"    : hip_hop + kata, beat clock, force_output objective
"""

from __future__ import annotations
import json
import math
import os
import sys
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

_HERE = os.path.dirname(__file__)
sys.path.insert(0, _HERE)

from tracker import MovementTracker, BreathClock, BeatClock, clock_for_domain
from sequencer import MovementSequencer, Block, sigmoid_intensity, intensity_to_cue_density
from state_machine import ValidTransitionMachine


# ---------------------------------------------------------------------------
# Built-in presets
# ---------------------------------------------------------------------------

_PRESETS: Dict[str, dict] = {
    "vinyasa-capoeira": {
        "domains": ["vinyasa", "capoeira"],
        "weights": {"vinyasa": 0.5, "capoeira": 0.5},
        "clock": "breath",
        "objective": "breath_alignment",
        "description": "Flowing yoga + capoeira esquivas on a shared breath arc",
    },
    "martial-beats": {
        "domains": ["hip_hop", "kata"],
        "weights": {"hip_hop": 0.6, "kata": 0.4},
        "clock": "beat",
        "objective": "force_output",
        "description": "Hip-hop groove with kata kime bursts — beat clock, force objective",
    },
}


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------

@dataclass
class CrossBlock:
    domain: str
    primitive_id: str
    primitive_name: str
    duration_s: float
    energy: float
    cue_density: str
    weight_shift: str
    facing: str


@dataclass
class CrossTrainingRoutine:
    preset: Optional[str]
    domains: List[str]
    weights: Dict[str, float]
    duration_min: float
    clock_type: str
    objective: str
    blocks: List[CrossBlock]
    tracker_final_state: dict

    def to_dict(self) -> dict:
        d = asdict(self)
        d["blocks"] = [asdict(b) for b in self.blocks]
        return d


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class CrossTrainingGenerator:
    """
    Compose a routine from 2+ movement domains.

    Parameters
    ----------
    domains : list[dict]
        Parsed domain JSON dicts.
    weights : dict[str, float]
        {domain_name: relative_weight}.  Will be normalised.
    duration_min : float
        Total class duration.
    clock : optional
        Shared clock override.  If None, derived from the highest-weight domain.
    objective_fn : optional
        Shared selection function.  If None, derived from the highest-weight domain.
    preset_name : str | None
        Stored for bookkeeping in the output.
    """

    def __init__(
        self,
        domains: List[dict],
        weights: Optional[Dict[str, float]] = None,
        duration_min: float = 45.0,
        clock=None,
        objective_fn=None,
        preset_name: Optional[str] = None,
    ) -> None:
        if len(domains) < 2:
            raise ValueError("CrossTrainingGenerator requires at least 2 domains")

        self._domains = {d["domain"]: d for d in domains}
        domain_names = list(self._domains)

        raw_weights = weights or {n: 1.0 for n in domain_names}
        total = sum(raw_weights.values()) or 1.0
        self._weights = {k: v / total for k, v in raw_weights.items()}

        self._duration_min = duration_min
        self._preset_name = preset_name

        # shared state
        self._tracker = MovementTracker()
        self._all_primitives = [p for d in domains for p in d.get("primitives", [])]
        self._machine = ValidTransitionMachine(self._all_primitives)

        # clock: use highest-weight domain's clock unless overridden
        dominant = max(self._weights, key=self._weights.get)
        self._clock = clock or clock_for_domain(self._domains[dominant])

        # objective: reuse MovementSequencer's auto-loading
        top_domain = self._domains[dominant]
        seq = MovementSequencer(domain=top_domain, objective_fn=objective_fn, clock=self._clock)
        self._objective_fn = seq._objective_fn

    def compile(self, safety_acknowledged: bool = False) -> CrossTrainingRoutine:
        """
        Build an interleaved cross-training routine.

        Raises
        ------
        PermissionError
            If any domain requires clinical review and safety_acknowledged is False.
        """
        for name, domain in self._domains.items():
            if domain.get("requires_clinical_review") and not safety_acknowledged:
                raise PermissionError(
                    f"Domain '{name}' requires safety_acknowledged=True."
                )

        total_s = self._duration_min * 60.0
        elapsed_s = 0.0
        blocks: List[CrossBlock] = []
        prim_map = {p["id"]: p for p in self._all_primitives}

        current_prim = self._all_primitives[0]

        while elapsed_s < total_s:
            t_norm = elapsed_s / total_s
            target_intensity = sigmoid_intensity(t_norm)
            self._objective_fn.__dict__.setdefault("_intensity_target", None)
            if hasattr(self._tracker, "_intensity_target"):
                self._tracker._intensity_target = target_intensity

            block_s = max(30.0, min(120.0, 90.0 - target_intensity * 60.0))
            if elapsed_s + block_s > total_s:
                block_s = total_s - elapsed_s
            if block_s < 5.0:
                break

            # Choose which domain to draw from this block
            chosen_domain_name = self._choose_domain(elapsed_s, total_s)
            chosen_domain = self._domains[chosen_domain_name]
            domain_prims = {p["id"]: p for p in chosen_domain.get("primitives", [])}

            # Valid transitions within cross-domain space
            valid_next_ids = current_prim.get("valid_next", [])
            if valid_next_ids:
                # Prefer same-domain transitions; fall back to any domain
                domain_valid = [prim_map[i] for i in valid_next_ids
                                if i in prim_map and i in domain_prims]
                global_valid = [prim_map[i] for i in valid_next_ids if i in prim_map]
                valid_next = domain_valid or global_valid or list(domain_prims.values())
            else:
                valid_next = list(domain_prims.values())

            # Apply state-machine filter
            state = self._tracker.current_state
            valid_next = self._machine.valid_next_maneuvers(state, current_prim.get("id"))
            if not valid_next:
                valid_next = list(domain_prims.values()) or self._all_primitives

            next_prim = self._objective_fn(valid_next, self._tracker)
            if next_prim is None:
                break

            beats = self._clock.tick(block_s)
            prim_with_beats = dict(next_prim)
            prim_with_beats["duration_beats"] = beats
            tracker_state = self._tracker.apply_primitive(prim_with_beats)

            energy = tracker_state["intensity"]
            block = CrossBlock(
                domain=next_prim.get("domain", chosen_domain_name) or chosen_domain_name,
                primitive_id=next_prim["id"],
                primitive_name=next_prim.get("name", next_prim["id"]),
                duration_s=round(block_s, 1),
                energy=round(energy, 3),
                cue_density=intensity_to_cue_density(energy),
                weight_shift=next_prim.get("weight_shift", "bilateral"),
                facing=next_prim.get("facing", "any"),
            )
            blocks.append(block)
            elapsed_s += block_s
            current_prim = next_prim

        return CrossTrainingRoutine(
            preset=self._preset_name,
            domains=list(self._domains),
            weights=dict(self._weights),
            duration_min=self._duration_min,
            clock_type=type(self._clock).__name__,
            objective=getattr(self._objective_fn, "__class__", type(None)).__name__,
            blocks=blocks,
            tracker_final_state=self._tracker.current_state,
        )

    def _choose_domain(self, elapsed_s: float, total_s: float) -> str:
        """
        Round-robin domain selection proportional to weights.
        Uses block index (derived from elapsed time) to interleave fairly.
        """
        cum = 0.0
        bucket = (elapsed_s / max(total_s, 1.0)) % 1.0
        # Deterministic selection based on weight boundaries
        for name, w in self._weights.items():
            cum += w
            if bucket < cum:
                return name
        return list(self._weights)[-1]


# ---------------------------------------------------------------------------
# Preset loader
# ---------------------------------------------------------------------------

def list_presets() -> List[str]:
    return sorted(_PRESETS)


def load_preset(name: str) -> dict:
    preset = _PRESETS.get(name)
    if preset is None:
        raise ValueError(f"Unknown preset '{name}'. Valid: {sorted(_PRESETS)}")
    return dict(preset)


def make_generator_from_preset(name: str, domain_lookup: Dict[str, dict], duration_min: float = 45.0) -> CrossTrainingGenerator:
    """
    Build a CrossTrainingGenerator from a named preset.

    Parameters
    ----------
    name : str
        Preset name (e.g. "vinyasa-capoeira").
    domain_lookup : dict
        {domain_name: parsed_domain_dict} for the domains listed in the preset.
    duration_min : float
        Routine duration.
    """
    preset = load_preset(name)
    domains = [domain_lookup[dn] for dn in preset["domains"]]
    weights = {dn: preset["weights"].get(dn, 1.0) for dn in preset["domains"]}
    return CrossTrainingGenerator(
        domains=domains,
        weights=weights,
        duration_min=duration_min,
        preset_name=name,
    )
