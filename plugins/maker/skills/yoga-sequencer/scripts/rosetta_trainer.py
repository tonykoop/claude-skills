#!/usr/bin/env python3
"""Deterministic Rosetta shorthand/transcript alignment trainer."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


THEMATIC_TERMS = {
    "attention",
    "breath",
    "ease",
    "effort",
    "feel",
    "ground",
    "intention",
    "notice",
    "space",
    "theme",
}


class RosettaError(ValueError):
    """Raised when a Rosetta input cannot be aligned."""


def load_engine_module():
    path = Path(__file__).with_name("engine_config.py")
    spec = importlib.util.spec_from_file_location("yoga_engine_config_for_rosetta", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["yoga_engine_config_for_rosetta"] = module
    spec.loader.exec_module(module)
    return module


engine_config = load_engine_module()


@dataclass(frozen=True)
class Alignment:
    pair_id: str
    shorthand: str
    transcript_text: str
    start_sec: float
    end_sec: float
    duration_sec: float
    pose_tokens: list[str]
    operator_tokens: list[str]
    draft_tokens: list[str]
    structural_transitions: list[dict[str, str]]
    thematic_terms: list[str]
    somatic_spacing: dict[str, float]


class RosettaTrainer:
    def __init__(self, engine: Any):
        self.engine = engine

    @classmethod
    def load(cls, skill_root: Path | None = None) -> "RosettaTrainer":
        return cls(engine_config.YogaEngineConfig.load(skill_root))

    def align_pair(self, pair: dict[str, Any]) -> Alignment:
        pair_id = str(pair.get("id", ""))
        shorthand = str(pair.get("shorthand", "")).strip()
        transcript = pair.get("transcript", {})
        text = str(transcript.get("text", "")).strip()

        if not pair_id:
            raise RosettaError("pair is missing id")
        if not shorthand:
            raise RosettaError(f"pair {pair_id} is missing shorthand")
        if not text:
            raise RosettaError(f"pair {pair_id} is missing transcript text")

        start_sec = float(transcript.get("start_sec", 0))
        end_sec = float(transcript.get("end_sec", 0))
        duration_sec = end_sec - start_sec
        if duration_sec <= 0:
            raise RosettaError(f"pair {pair_id} must have positive transcript duration")

        tokens = self.engine.parse_line(shorthand)
        pose_tokens = [token.base for token in tokens if token.kind == "pose"]
        operator_tokens = [token.raw for token in tokens if token.kind == "operator"]
        draft_tokens = [token.raw for token in tokens if token.draft]

        transitions = []
        for origin, target in zip(pose_tokens, pose_tokens[1:]):
            transitions.append({"origin": origin, "target": target})

        lower_text = text.lower()
        thematic_terms = sorted(term for term in THEMATIC_TERMS if term in lower_text)
        seconds_per_pose = duration_sec / len(pose_tokens) if pose_tokens else duration_sec
        breath_counts = [int(token[:-1]) for token in operator_tokens if token.endswith("B")]

        return Alignment(
            pair_id=pair_id,
            shorthand=shorthand,
            transcript_text=text,
            start_sec=start_sec,
            end_sec=end_sec,
            duration_sec=duration_sec,
            pose_tokens=pose_tokens,
            operator_tokens=operator_tokens,
            draft_tokens=draft_tokens,
            structural_transitions=transitions,
            thematic_terms=thematic_terms,
            somatic_spacing={
                "duration_sec": duration_sec,
                "seconds_per_pose": seconds_per_pose,
                "explicit_breath_count": float(sum(breath_counts)),
            },
        )

    def train(self, data: dict[str, Any]) -> dict[str, Any]:
        pairs = data.get("pairs", [])
        if not isinstance(pairs, list) or not pairs:
            raise RosettaError("Rosetta input must contain a non-empty pairs list")

        alignments = [self.align_pair(pair) for pair in pairs]
        review_findings = self._review_findings(pairs, alignments)

        return {
            "class_id": data.get("class_id", ""),
            "source": data.get("source", ""),
            "pair_count": len(alignments),
            "alignments": [alignment.__dict__ for alignment in alignments],
            "structural_transition_count": sum(len(a.structural_transitions) for a in alignments),
            "thematic_infusion_count": sum(1 for a in alignments if a.thematic_terms),
            "quality_gate": {
                "trusted_for_training": not review_findings,
                "status": "approved" if not review_findings else "needs_human_review",
                "findings": review_findings,
            },
        }

    def _review_findings(self, pairs: list[dict[str, Any]], alignments: list[Alignment]) -> list[str]:
        findings: list[str] = []
        for alignment in alignments:
            if alignment.draft_tokens:
                findings.append(f"{alignment.pair_id}: draft tokens need thesaurus review")

        if not any(alignment.structural_transitions for alignment in alignments):
            findings.append("class has no structural transitions")
        if not any(alignment.thematic_terms for alignment in alignments):
            findings.append("class has no thematic-infusion points")

        for pair in pairs:
            review = pair.get("human_review", {})
            if review.get("status") != "approved" or not str(review.get("reviewer", "")).strip():
                findings.append(f"{pair.get('id', '<unknown>')}: human review approval is required")
        return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Rosetta shorthand/transcript alignment labels.")
    parser.add_argument("input_json", type=Path)
    parser.add_argument("--skill-root", type=Path, default=None)
    args = parser.parse_args(argv)

    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    trainer = RosettaTrainer.load(args.skill_root)
    print(json.dumps(trainer.train(data), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
