"""Movement-engine → playlist data bridge for the audio-dynamic engine.

SCHEMA_ID: playlist-builder/movement-bridge@1.0.0
VERSION    = "1.0.0"

Story #475 — Epic #471 (playlist-builder audio-dynamic).

See references/MOVEMENT_BRIDGE_CONTRACT.md for the full protocol.
See schemas/agent_packets/MovementRoutinePayload.schema.json for the
constraint payload schema.

Usage
-----
    from scripts.movement_bridge import build_mix_plan, validate_payload

    payload = {
        "routine_id": "hip-hop-demo",
        "style": "hip-hop",
        "total_duration_s": 480,
        "blocks": [
            {"name": "Warm-up", "bpm_target": 80, "duration_s": 120, "energy": 0.3},
            {"name": "Peak",    "bpm_target": 97, "duration_s": 120,
             "energy": 0.65, "kinetic_texture": "tutting", "peak_count_s": 75.0},
        ],
    }

    validate_payload(payload)          # raises ValueError if invalid
    mix_plan = build_mix_plan(payload, catalog)
    # mix_plan.blocks[i].candidates   → ranked track list
    # mix_plan.blocks[i].anchor_offset_s → seconds to shift track start
"""
from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Lazy-load sibling scripts (importlib avoids PYTHONPATH assumptions)
# ---------------------------------------------------------------------------

_SCRIPTS = Path(__file__).resolve().parent


def _load(name: str):
    path = _SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, mod)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class MixBlock:
    name: str
    bpm_target: float
    duration_s: float
    kinetic_texture: str | None
    peak_count_s: float | None
    candidates: list[dict[str, Any]] = field(default_factory=list)
    anchor_offset_s: float = 0.0
    anchor_fallback: bool = True
    anchor_type_used: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "bpm_target": self.bpm_target,
            "duration_s": self.duration_s,
            "kinetic_texture": self.kinetic_texture,
            "peak_count_s": self.peak_count_s,
            "candidates": self.candidates,
            "anchor_offset_s": self.anchor_offset_s,
            "anchor_fallback": self.anchor_fallback,
        }
        if self.anchor_type_used is not None:
            d["anchor_type_used"] = self.anchor_type_used
        if self.notes is not None:
            d["notes"] = self.notes
        return d


@dataclass
class MixPlan:
    routine_id: str
    style: str
    total_duration_s: float
    blocks: list[MixBlock] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "routine_id": self.routine_id,
            "style": self.style,
            "total_duration_s": self.total_duration_s,
            "blocks": [b.to_dict() for b in self.blocks],
        }


# ---------------------------------------------------------------------------
# Payload from dict
# ---------------------------------------------------------------------------

@dataclass
class MovementRoutinePayload:
    routine_id: str
    style: str
    total_duration_s: float
    blocks: list[dict[str, Any]]
    bpm_global: float | None = None
    source_engine: str | None = None
    created_at: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MovementRoutinePayload":
        return cls(
            routine_id=str(d["routine_id"]),
            style=str(d["style"]),
            total_duration_s=float(d["total_duration_s"]),
            blocks=list(d["blocks"]),
            bpm_global=d.get("bpm_global"),
            source_engine=d.get("source_engine"),
            created_at=d.get("created_at"),
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_payload(d: dict[str, Any]) -> None:
    """Validate *d* against the MovementRoutinePayload schema.

    Uses ``jsonschema`` if available, otherwise falls back to a structural check.
    Raises ``ValueError`` on failure.
    """
    # Structural fast-path (always runs first for speed)
    for required in ("routine_id", "style", "total_duration_s", "blocks"):
        if required not in d:
            raise ValueError(f"MovementRoutinePayload missing required field: {required!r}")

    if not isinstance(d["blocks"], list) or len(d["blocks"]) == 0:
        raise ValueError("MovementRoutinePayload 'blocks' must be a non-empty list")

    for i, block in enumerate(d["blocks"]):
        for req in ("name", "bpm_target", "duration_s"):
            if req not in block:
                raise ValueError(
                    f"RoutineBlock[{i}] missing required field: {req!r}"
                )
        if not isinstance(block["bpm_target"], (int, float)) or block["bpm_target"] <= 0:
            raise ValueError(
                f"RoutineBlock[{i}].bpm_target must be a positive number"
            )

    # jsonschema pass (optional — enhances coverage)
    try:
        import jsonschema  # type: ignore

        schema_path = (
            Path(__file__).resolve().parents[5]
            / "schemas" / "agent_packets" / "MovementRoutinePayload.schema.json"
        )
        if schema_path.exists():
            import json
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            jsonschema.validate(d, schema)
    except ImportError:
        pass  # jsonschema not installed; structural check is sufficient


# ---------------------------------------------------------------------------
# Core bridge
# ---------------------------------------------------------------------------

def build_mix_plan(
    payload: dict[str, Any] | MovementRoutinePayload,
    catalog: list[dict[str, Any]],
    top_n: int = 5,
) -> MixPlan:
    """Build a MixPlan by matching each routine block to catalog tracks.

    Args:
        payload:  A ``MovementRoutinePayload`` instance or a raw dict
                  (will be parsed via ``from_dict``).
        catalog:  List of track dicts from the playlist-builder catalog.
        top_n:    Maximum candidates per block.

    Returns:
        A ``MixPlan`` with one ``MixBlock`` per input block.
    """
    if isinstance(payload, dict):
        payload = MovementRoutinePayload.from_dict(payload)

    bpm_mod = _load("bpm_match")
    tex_mod = _load("texture_map")
    anc_mod = _load("sonic_anchor")

    mix_blocks: list[MixBlock] = []

    for raw_block in payload.blocks:
        name = str(raw_block["name"])
        bpm_target = float(raw_block["bpm_target"])
        duration_s = float(raw_block["duration_s"])
        energy = raw_block.get("energy")
        texture = raw_block.get("kinetic_texture")
        peak_s = raw_block.get("peak_count_s")
        notes = raw_block.get("notes")

        bpm_range_raw = raw_block.get("bpm_range")
        bpm_range = (
            (float(bpm_range_raw[0]), float(bpm_range_raw[1]))
            if bpm_range_raw else None
        )

        # 1. BPM filter (with optional texture pre-filter)
        working_catalog = (
            tex_mod.filter_tracks_by_texture(catalog, texture)
            if texture else catalog
        )

        candidates = bpm_mod.bpm_candidates(
            working_catalog,
            bpm_target=bpm_target,
            bpm_range=bpm_range,
            energy_target=energy,
            top_n=top_n,
        )

        # 2. Sonic anchor alignment on the top candidate
        if candidates and peak_s is not None:
            top_track = candidates[0]
            aligned = anc_mod.align_timeline(
                [{"name": name, "bpm_target": bpm_target,
                  "peak_count_s": peak_s}],
                [top_track],
            )[0]
            anchor_offset = aligned.get("anchor_offset_s", 0.0)
            anchor_fallback = aligned.get("anchor_fallback", True)
            anchor_type_used = aligned.get("anchor_type_used")
        else:
            anchor_offset = 0.0
            anchor_fallback = True
            anchor_type_used = None

        mix_blocks.append(MixBlock(
            name=name,
            bpm_target=bpm_target,
            duration_s=duration_s,
            kinetic_texture=texture,
            peak_count_s=peak_s,
            candidates=candidates,
            anchor_offset_s=anchor_offset,
            anchor_fallback=anchor_fallback,
            anchor_type_used=anchor_type_used,
            notes=notes,
        ))

    return MixPlan(
        routine_id=payload.routine_id,
        style=payload.style,
        total_duration_s=payload.total_duration_s,
        blocks=mix_blocks,
    )
