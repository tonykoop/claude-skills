#!/usr/bin/env python3
"""Transitions-only yoga class mode.

The unit of teaching is the TRANSITION — the connective tissue between shapes.
Poses are waypoints; their names are never spoken. The instruction lives in
the movement: the breath, the weight shift, the unfolding. This inverts the
default pose-centric model where transitions are filler.

Usage:
    python3 transitions_class.py --template references/transitions-class-template.json
    python3 transitions_class.py --template references/transitions-class-template.json --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[1]

# Short pose shorthand tokens (all-caps abbreviations) that must never appear
# as standalone words in transitions-only cue text. Matched with word boundaries
# so common words like "different" (containing "ff") are not false-positives.
_FORBIDDEN_SHORTHAND: frozenset[str] = frozenset(
    {"DD", "HL", "FF", "RLH", "CL", "PT", "PL", "CH", "UD"}
)

# Multi-word and Sanskrit pose names. Checked as substrings (case-insensitive);
# they are long enough to avoid false-positive collisions.
_FORBIDDEN_PHRASES: frozenset[str] = frozenset(
    {
        "downward dog", "down dog", "downward-facing dog",
        "crescent lunge", "warrior", "chaturanga",
        "upward dog", "upward-facing dog", "mountain pose",
        "tadasana", "vrksasana", "virabhadrasana", "trikonasana",
        "adho mukha", "urdhva mukha",
        "prayer twist", "forward fold", "half lift", "runner's lunge",
        "runner lunge", "plank pose", "cobra pose", "tree pose",
        "triangle pose", "chair pose", "bridge pose", "camel pose",
        "child's pose", "child pose", "happy baby", "pigeon pose",
        "lizard pose", "malasana", "savasana",
    }
)

# Pre-compiled regex for standalone shorthand tokens (word-boundary aware).
_SHORTHAND_RE = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in sorted(_FORBIDDEN_SHORTHAND, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)


class TransitionsClassError(ValueError):
    """Raised when a transitions-only class violates its own constraints."""


@dataclass(frozen=True)
class TransitionCue:
    """A single teachable unit: one transition described by its felt experience."""

    id: str
    phase: str
    cue: str
    somatic_focus: list[str]
    breath_instruction: str
    duration_secs: int
    pacing: str
    side: str | None = None

    def __post_init__(self) -> None:
        cue_lower = self.cue.lower()
        match = _SHORTHAND_RE.search(self.cue)
        if match:
            raise TransitionsClassError(
                f"Cue {self.id!r} contains shorthand token {match.group()!r}. "
                "Transitions-only mode must never name poses."
            )
        for phrase in _FORBIDDEN_PHRASES:
            if phrase.lower() in cue_lower:
                raise TransitionsClassError(
                    f"Cue {self.id!r} names a pose ({phrase!r}). "
                    "Transitions-only mode must never name poses."
                )


@dataclass
class TransitionsOnlyClass:
    """A yoga class structured entirely as transitions, never as a pose list."""

    class_length_mins: int
    theme: str
    level: str
    cues: list[TransitionCue] = field(default_factory=list)

    @classmethod
    def from_template(
        cls,
        template_path: Path | None = None,
    ) -> "TransitionsOnlyClass":
        path = template_path or SKILL_ROOT / "references" / "transitions-class-template.json"
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        instance = cls(
            class_length_mins=data["class_length_mins"],
            theme=data["theme"],
            level=data["level"],
        )
        for item in data.get("cues", []):
            instance.add_cue(
                TransitionCue(
                    id=item["id"],
                    phase=item["phase"],
                    cue=item["cue"],
                    somatic_focus=item.get("somatic_focus", []),
                    breath_instruction=item.get("breath_instruction", ""),
                    duration_secs=item["duration_secs"],
                    pacing=item["pacing"],
                    side=item.get("side"),
                )
            )
        return instance

    def add_cue(self, cue: TransitionCue) -> None:
        self.cues.append(cue)

    def validate(self) -> None:
        """Raise TransitionsClassError if the arc is malformed."""
        if not self.cues:
            raise TransitionsClassError("No transition cues defined.")

        total_secs = sum(c.duration_secs for c in self.cues)
        expected_secs = self.class_length_mins * 60
        # Allow ±90 seconds of rounding across a 60-minute class.
        if abs(total_secs - expected_secs) > 90:
            raise TransitionsClassError(
                f"Total duration {total_secs}s deviates from "
                f"expected {expected_secs}s by more than 90 seconds."
            )

        sides = {c.side for c in self.cues if c.side is not None}
        unilateral_phases = [c for c in self.cues if c.side is not None]
        if unilateral_phases:
            if "right" not in sides or "left" not in sides:
                raise TransitionsClassError(
                    "Unilateral transitions must cover both sides."
                )

    def as_dict(self) -> dict[str, Any]:
        return {
            "class_length_mins": self.class_length_mins,
            "theme": self.theme,
            "level": self.level,
            "total_duration_secs": sum(c.duration_secs for c in self.cues),
            "cue_count": len(self.cues),
            "cues": [asdict(c) for c in self.cues],
        }

    def as_teacher_script(self) -> str:
        """Return a plain-text teacher script with no pose names, only movement."""
        lines: list[str] = [
            f"TRANSITIONS-ONLY CLASS — {self.class_length_mins} min",
            f"Theme: {self.theme}  |  Level: {self.level}",
            "",
        ]
        current_phase = ""
        for cue in self.cues:
            if cue.phase != current_phase:
                current_phase = cue.phase
                lines.append(f"── {current_phase.upper().replace('_', ' ')} ──")
            side_tag = f" ({cue.side})" if cue.side else ""
            mins = cue.duration_secs // 60
            secs = cue.duration_secs % 60
            dur = f"{mins}:{secs:02d}"
            lines.append(f"  [{dur}] {cue.cue}{side_tag}")
            lines.append(f"          breath: {cue.breath_instruction}")
            if cue.somatic_focus:
                lines.append(f"          somatic: {', '.join(cue.somatic_focus)}")
        return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a transitions-only yoga class plan."
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=None,
        help="Path to a transitions class template JSON.",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit machine-readable JSON instead of a teacher script.",
    )
    args = parser.parse_args(argv)

    try:
        yoga_class = TransitionsOnlyClass.from_template(args.template)
        yoga_class.validate()
    except TransitionsClassError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(yoga_class.as_dict(), indent=2, sort_keys=True))
    else:
        print(yoga_class.as_teacher_script())
    return 0


if __name__ == "__main__":
    sys.exit(main())
