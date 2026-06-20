#!/usr/bin/env python3
"""Expand shorthand into a review-gated 60-minute yoga class scaffold."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PHASES = [
    ("arrival", 0, 5, "sparse", "low"),
    ("warm_up", 5, 15, "moderate", "low_to_medium"),
    ("standing_build", 15, 35, "rhythmic", "medium_to_high"),
    ("peak_or_focal", 35, 45, "focused", "high"),
    ("cooldown", 45, 56, "sparse", "low"),
    ("savasana", 56, 60, "minimal", "rest"),
]


class ReverseSequenceError(ValueError):
    """Raised when shorthand cannot expand into a class scaffold."""


def load_local_module(module_name: str, filename: str):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


engine_config = load_local_module("yoga_engine_config_for_reverse", "engine_config.py")
transition_matrix = load_local_module("yoga_transition_matrix_for_reverse", "transition_matrix.py")


@dataclass(frozen=True)
class ReverseSequenceInput:
    lines: list[str]
    theme: str = "space between effort and ease"
    level: str = "mixed-level"
    energy: str = "steady vinyasa"
    reviewer: str = ""


class ReverseSequenceEngine:
    def __init__(self, engine: Any, transitions: Any):
        self.engine = engine
        self.transitions = transitions

    @classmethod
    def load(cls, skill_root: Path | None = None) -> "ReverseSequenceEngine":
        return cls(
            engine=engine_config.YogaEngineConfig.load(skill_root),
            transitions=transition_matrix.TransitionMatrix.load(skill_root),
        )

    def generate(self, request: ReverseSequenceInput) -> dict[str, Any]:
        parsed = self.engine.parse_program(request.lines)
        expanded_tokens = [
            token
            for line in parsed
            if line.kind == "sequence"
            for token in line.tokens
            if token.kind in {"pose", "operator"}
        ]
        pose_tokens = [token.base for token in expanded_tokens if token.kind == "pose"]
        if not pose_tokens:
            raise ReverseSequenceError("shorthand must expand to at least one pose token")

        transition_handoffs = self._transition_handoffs(pose_tokens)
        phases = self._phases(pose_tokens, request)
        script_lines = self._script_lines(phases, transition_handoffs, request)
        findings = self._quality_findings(expanded_tokens, phases, transition_handoffs, request)

        return {
            "class_summary": {
                "length_min": 60,
                "level": request.level,
                "theme": request.theme,
                "energy": request.energy,
                "voice_mode": "public_teacher_style_scaffold",
            },
            "expanded_tokens": [token.__dict__ for token in expanded_tokens],
            "transition_handoffs": transition_handoffs,
            "phases": phases,
            "script_lines": script_lines,
            "playlist_phase_map": [
                {
                    "phase": phase["name"],
                    "start_min": phase["start_min"],
                    "end_min": phase["end_min"],
                    "energy": phase["energy"],
                    "cue_density": phase["cue_density"],
                }
                for phase in phases
            ],
            "quality_gate": {
                "trusted_for_teaching": not findings,
                "status": "approved" if not findings else "needs_human_review",
                "findings": findings,
            },
        }

    def _transition_handoffs(self, pose_tokens: list[str]) -> list[dict[str, Any]]:
        handoffs: list[dict[str, Any]] = []
        for origin, target in zip(pose_tokens, pose_tokens[1:]):
            matches = self.transitions.between(origin, target)
            if matches:
                handoffs.append(self.transitions.as_handoff(matches[0]))
            else:
                handoffs.append(
                    {
                        "transition_id": f"generic-{origin.lower()}-{target.lower()}",
                        "origin": origin,
                        "pathway": "generic_public_scaffold",
                        "target": target,
                        "pacing": "medium",
                        "crossfade_seconds": self.transitions.crossfade_seconds("medium"),
                        "transcript_cue": f"Move from {origin} toward {target} with steady breath.",
                        "shorthand": f"{origin} > {target}",
                    }
                )
        return handoffs

    def _phases(self, pose_tokens: list[str], request: ReverseSequenceInput) -> list[dict[str, Any]]:
        chunks = self._chunk_pose_tokens(pose_tokens, len(PHASES))
        phases = []
        for (name, start, end, cue_density, energy), poses in zip(PHASES, chunks):
            phases.append(
                {
                    "name": name,
                    "start_min": start,
                    "end_min": end,
                    "intent": self._phase_intent(name, request.theme),
                    "pose_tokens": poses,
                    "cue_density": cue_density,
                    "energy": energy,
                    "thematic_infusion": name in {"arrival", "peak_or_focal", "cooldown"},
                }
            )
        return phases

    def _chunk_pose_tokens(self, pose_tokens: list[str], count: int) -> list[list[str]]:
        chunks = [[] for _ in range(count)]
        for index, token in enumerate(pose_tokens):
            bucket = min(count - 1, int(index * count / max(len(pose_tokens), 1)))
            chunks[bucket].append(token)
        return chunks

    def _phase_intent(self, name: str, theme: str) -> str:
        intents = {
            "arrival": f"Introduce {theme} through breath and attention.",
            "warm_up": "Build joint mobility and simple pattern recognition.",
            "standing_build": "Layer heat, side balance, and transition familiarity.",
            "peak_or_focal": "Use the strongest shorthand material with focused cueing and quiet attempt space.",
            "cooldown": f"Downshift and integrate the theme of {theme}.",
            "savasana": "Let the class land with minimal language.",
        }
        return intents[name]

    def _script_lines(
        self, phases: list[dict[str, Any]], handoffs: list[dict[str, Any]], request: ReverseSequenceInput
    ) -> list[str]:
        lines = []
        for phase in phases:
            poses = " -> ".join(phase["pose_tokens"]) if phase["pose_tokens"] else "rest"
            lines.append(
                f"{phase['start_min']:02d}-{phase['end_min']:02d} {phase['name']}: {phase['intent']} Sequence: {poses}."
            )
        if handoffs:
            lines.append(f"Transition cue sample: {handoffs[0]['transcript_cue']}")
        lines.append(
            f"Review note: this is a public scaffold for {request.level}; final Tony-voice phrasing requires human review."
        )
        return lines

    def _quality_findings(
        self,
        expanded_tokens: list[Any],
        phases: list[dict[str, Any]],
        handoffs: list[dict[str, Any]],
        request: ReverseSequenceInput,
    ) -> list[str]:
        findings: list[str] = []
        if any(token.draft for token in expanded_tokens):
            findings.append("draft tokens require thesaurus review")
        if phases[-1]["end_min"] != 60 or phases[0]["start_min"] != 0:
            findings.append("phase map must cover exactly 60 minutes")
        if not handoffs:
            findings.append("transition handoffs are required")
        if not any(phase["thematic_infusion"] for phase in phases):
            findings.append("thematic-infusion slots are required")
        if not request.reviewer:
            findings.append("named human reviewer approval is required before teaching")
        return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Expand yoga shorthand into a 60-minute class scaffold.")
    parser.add_argument("program_file", type=Path)
    parser.add_argument("--theme", default="space between effort and ease")
    parser.add_argument("--level", default="mixed-level")
    parser.add_argument("--energy", default="steady vinyasa")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--skill-root", type=Path, default=None)
    args = parser.parse_args(argv)

    request = ReverseSequenceInput(
        lines=args.program_file.read_text(encoding="utf-8").splitlines(),
        theme=args.theme,
        level=args.level,
        energy=args.energy,
        reviewer=args.reviewer,
    )
    result = ReverseSequenceEngine.load(args.skill_root).generate(request)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
