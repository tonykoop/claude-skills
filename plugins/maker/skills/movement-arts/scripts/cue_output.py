"""
Movement Arts — multi-modal instructional cue output.

CueFormatter(compiled_routine, domain) → formats a CompiledRoutine for different consumers:

  "verbal"           — instructor script (count/cue text per block)
  "audio_energy"     — playlist-builder handoff ({block_id, energy_level, bpm_target, cue_density})
  "pt_biomechanical" — compensation cues (velocity, asymmetry flags, ROM targets)

Select output type with format= kwarg; defaults to "verbal".
"""

from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional


_FORMAT_TYPES = {"verbal", "audio_energy", "pt_biomechanical"}

_COUNT_VERBAL = {
    "breath": lambda beats: f"over {beats} breaths",
    "beat":   lambda beats: f"for {beats} counts",
}

_ENERGY_LABELS = [
    (0.0,  0.2,  "rest"),
    (0.2,  0.4,  "low"),
    (0.4,  0.6,  "moderate"),
    (0.6,  0.8,  "high"),
    (0.8,  1.01, "peak"),
]

_WEIGHT_CUE = {
    "left":       "settle weight into your left foot",
    "right":      "settle weight into your right foot",
    "bilateral":  "distribute weight evenly through both feet",
    "unweighted": "lift both feet — fully unweighted",
}

_FACING_CUE = {
    "north": "facing forward",
    "south": "facing back",
    "east":  "facing right",
    "west":  "facing left",
    "any":   "",
}


def _energy_label(level: float) -> str:
    for lo, hi, label in _ENERGY_LABELS:
        if lo <= level < hi:
            return label
    return "peak"


class CueFormatter:
    """
    Formats a CompiledRoutine for a specific output consumer.

    Parameters
    ----------
    compiled_routine : CompiledRoutine | dict
        The output of MovementSequencer.compile().  Accepts the dataclass
        or its .to_dict() form so callers need not import CompiledRoutine.
    domain : dict
        The raw domain JSON (used for clock spec and objective metadata).
    """

    def __init__(self, compiled_routine, domain: dict) -> None:
        if hasattr(compiled_routine, "to_dict"):
            self._routine = compiled_routine.to_dict()
        else:
            self._routine = compiled_routine
        self._domain = domain
        self._clock_type = self._routine.get("clock_type", "BreathClock")
        self._clock_spec = domain.get("clock", {})
        self._bpm_target = self._resolve_bpm()
        self._objective = self._routine.get("objective", "")
        self._is_pt = domain.get("requires_clinical_review", False)

    def _resolve_bpm(self) -> float:
        spec = self._clock_spec
        if spec.get("type") == "beat":
            rng = spec.get("bpm_range", [100, 100])
            return (rng[0] + rng[1]) / 2.0
        return spec.get("bpm", 12.0)

    def format(self, fmt: str = "verbal") -> List[Dict[str, Any]]:
        """
        Format all blocks.

        Parameters
        ----------
        fmt : "verbal" | "audio_energy" | "pt_biomechanical"

        Returns
        -------
        list of dicts, one per block.
        """
        if fmt not in _FORMAT_TYPES:
            raise ValueError(f"Unknown format '{fmt}'. Valid: {sorted(_FORMAT_TYPES)}")
        blocks = self._routine.get("blocks", [])
        method = getattr(self, f"_fmt_{fmt}")
        return [method(i, b) for i, b in enumerate(blocks)]

    # ------------------------------------------------------------------
    # verbal: instructor script
    # ------------------------------------------------------------------

    def _fmt_verbal(self, idx: int, block: dict) -> dict:
        name = block.get("primitive_name", block.get("primitive_id", "movement"))
        weight_shift = block.get("weight_shift", "bilateral")
        facing = block.get("facing", "any")
        energy = block.get("energy", 0.5)
        cue_density = block.get("cue_density", "moderate")
        duration_s = block.get("duration_s", 0)

        # build the instructor count cue
        if "Beat" in self._clock_type:
            count_cue = "on count 1"
        else:
            count_cue = "on your inhale"

        weight_text = _WEIGHT_CUE.get(weight_shift, "")
        facing_text = _FACING_CUE.get(facing, "")
        facing_fragment = f", {facing_text}" if facing_text else ""

        cue = f"{count_cue}, {name.lower()}{facing_fragment} — {weight_text}."
        if idx == 0:
            cue = f"We begin: {cue}"

        return {
            "block_index": idx,
            "primitive_id": block.get("primitive_id", ""),
            "primitive_name": name,
            "duration_s": duration_s,
            "energy_level": _energy_label(energy),
            "cue_density": cue_density,
            "instructor_cue": cue,
        }

    # ------------------------------------------------------------------
    # audio_energy: playlist-builder handoff
    # ------------------------------------------------------------------

    def _fmt_audio_energy(self, idx: int, block: dict) -> dict:
        energy = block.get("energy", 0.5)
        return {
            "block_index": idx,
            "block_id": block.get("primitive_id", f"block_{idx}"),
            "energy_level": _energy_label(energy),
            "energy_raw": round(energy, 4),
            "bpm_target": round(self._bpm_target, 1),
            "cue_density": block.get("cue_density", "moderate"),
            "duration_s": block.get("duration_s", 0),
        }

    # ------------------------------------------------------------------
    # pt_biomechanical: compensation cues for PT domain
    # ------------------------------------------------------------------

    def _fmt_pt_biomechanical(self, idx: int, block: dict) -> dict:
        prim_id = block.get("primitive_id", "")
        weight_shift = block.get("weight_shift", "bilateral")
        energy = block.get("energy", 0.5)

        # look up PT-specific fields from domain primitives if available
        prim_data = self._get_prim_data(prim_id)
        velocity_cap = prim_data.get("velocity_cap_m_per_s", None)
        unilateral = prim_data.get("unilateral_load", False)
        rom = prim_data.get("ROM_target_deg", None)

        cues = []
        if velocity_cap is not None and velocity_cap <= 0.1:
            cues.append("slow, controlled movement only")
        if unilateral:
            cues.append("monitor asymmetry — stop if compensating")
        if rom is not None and rom > 60:
            cues.append(f"target ROM: {rom}° — do not force end-range")
        if weight_shift in ("left", "right"):
            cues.append(f"single-limb load on {weight_shift} — brace core")

        return {
            "block_index": idx,
            "primitive_id": prim_id,
            "primitive_name": block.get("primitive_name", prim_id),
            "duration_s": block.get("duration_s", 0),
            "energy_level": _energy_label(energy),
            "velocity_cap_m_per_s": velocity_cap,
            "unilateral_load": unilateral,
            "ROM_target_deg": rom,
            "compensation_cues": cues,
        }

    def _get_prim_data(self, prim_id: str) -> dict:
        for p in self._domain.get("primitives", []):
            if p.get("id") == prim_id:
                return p
        return {}
