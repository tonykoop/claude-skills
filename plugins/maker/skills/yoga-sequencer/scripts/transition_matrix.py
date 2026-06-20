#!/usr/bin/env python3
"""Load and query the public yoga-sequencer Transition Matrix."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class TransitionMatrixError(ValueError):
    """Raised when transition matrix data is invalid or incomplete."""


@dataclass(frozen=True)
class TransitionVector:
    id: str
    origin: str
    pathway: str
    target: str
    pacing: str
    transcript_cue: str
    side: str | None = None
    shorthand: str | None = None


class TransitionMatrix:
    def __init__(self, data: dict[str, Any]):
        self.data = data
        self._validate()

    @classmethod
    def load(cls, skill_root: Path | None = None, *, matrix_path: Path | None = None) -> "TransitionMatrix":
        root = skill_root or Path(__file__).resolve().parents[1]
        path = matrix_path or root / "references" / "transition-matrix.json"
        with path.open("r", encoding="utf-8") as handle:
            return cls(json.load(handle))

    @property
    def pacing_to_crossfade(self) -> dict[str, dict[str, Any]]:
        return self.data.get("pacing_to_crossfade", {})

    @property
    def transitions(self) -> list[TransitionVector]:
        return [
            TransitionVector(
                id=str(item["id"]),
                origin=str(item["origin"]),
                pathway=str(item["pathway"]),
                target=str(item["target"]),
                pacing=str(item["pacing"]),
                transcript_cue=str(item["transcript_cue"]),
                side=item.get("side"),
                shorthand=item.get("shorthand"),
            )
            for item in self.data.get("transitions", [])
        ]

    def _validate(self) -> None:
        crossfades = self.pacing_to_crossfade
        if not crossfades:
            raise TransitionMatrixError("pacing_to_crossfade is required")
        for pacing, handoff in crossfades.items():
            if "crossfade_seconds" not in handoff:
                raise TransitionMatrixError(f"missing crossfade_seconds for pacing {pacing!r}")

        for item in self.data.get("transitions", []):
            for key in ("id", "origin", "pathway", "target", "pacing", "transcript_cue"):
                if not item.get(key):
                    raise TransitionMatrixError(f"transition {item.get('id', '<unknown>')!r} missing {key}")
            if item["pacing"] not in crossfades:
                raise TransitionMatrixError(
                    f"transition {item['id']!r} uses unknown pacing {item['pacing']!r}"
                )

    def for_target(self, target: str) -> list[TransitionVector]:
        return [transition for transition in self.transitions if transition.target == target]

    def between(self, origin: str, target: str) -> list[TransitionVector]:
        return [
            transition
            for transition in self.transitions
            if transition.origin == origin and transition.target == target
        ]

    def crossfade_seconds(self, pacing: str) -> float:
        try:
            return float(self.pacing_to_crossfade[pacing]["crossfade_seconds"])
        except KeyError as exc:
            raise TransitionMatrixError(f"unknown pacing {pacing!r}") from exc

    def as_handoff(self, transition: TransitionVector) -> dict[str, Any]:
        return {
            "transition_id": transition.id,
            "origin": transition.origin,
            "pathway": transition.pathway,
            "target": transition.target,
            "pacing": transition.pacing,
            "crossfade_seconds": self.crossfade_seconds(transition.pacing),
            "transcript_cue": transition.transcript_cue,
            "shorthand": transition.shorthand,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Query yoga-sequencer transition vectors.")
    parser.add_argument("--target", default="CL", help="Target pose token to inspect.")
    parser.add_argument("--skill-root", type=Path, default=None)
    args = parser.parse_args(argv)

    matrix = TransitionMatrix.load(args.skill_root)
    print(
        json.dumps(
            [matrix.as_handoff(transition) for transition in matrix.for_target(args.target)],
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
