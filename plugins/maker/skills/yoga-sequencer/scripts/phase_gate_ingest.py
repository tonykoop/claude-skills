#!/usr/bin/env python3
"""Phase-gated ingest for yoga class JSON captures."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PHASE_RULES = {
    "anchor": (1, 1),
    "triangulation": (3, None),
    "micro_batch": (3, 5),
    "bulk": (35, None),
}
THEME_TERMS = {"attention", "breath", "ease", "effort", "intention", "notice", "space", "theme"}


class PhaseGateError(ValueError):
    """Raised when source class data cannot be parsed."""


def load_engine_module():
    path = Path(__file__).with_name("engine_config.py")
    spec = importlib.util.spec_from_file_location("yoga_engine_config_for_ingest", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["yoga_engine_config_for_ingest"] = module
    spec.loader.exec_module(module)
    return module


engine_config = load_engine_module()


@dataclass(frozen=True)
class PhaseResult:
    phase: str
    class_count: int
    go: bool
    findings: list[str]
    parsed_classes: list[dict[str, Any]]


class PhaseGateIngest:
    def __init__(self, engine: Any):
        self.engine = engine

    @classmethod
    def load(cls, skill_root: Path | None = None) -> "PhaseGateIngest":
        return cls(engine_config.YogaEngineConfig.load(skill_root))

    def parse_class(self, data: dict[str, Any]) -> dict[str, Any]:
        class_id = str(data.get("class_id", "")).strip()
        if not class_id:
            raise PhaseGateError("class is missing class_id")
        segments = data.get("segments", [])
        if not isinstance(segments, list) or not segments:
            raise PhaseGateError(f"{class_id}: segments must be a non-empty list")

        metadata = {
            "class_id": class_id,
            "teacher": data.get("teacher", ""),
            "duration_min": data.get("duration_min"),
            "source": data.get("source", ""),
            "segment_count": len(segments),
        }
        audio_timeline: list[dict[str, Any]] = []
        choreography_raw: list[dict[str, Any]] = []
        thematic_drops: list[dict[str, Any]] = []

        for index, segment in enumerate(segments):
            start = float(segment.get("start_sec", 0))
            end = float(segment.get("end_sec", 0))
            if end <= start:
                raise PhaseGateError(f"{class_id}: segment {index} must have positive duration")
            kind = str(segment.get("kind", "")).strip()
            text = str(segment.get("text", "")).strip()

            if kind == "audio":
                audio_timeline.append(
                    {
                        "start_sec": start,
                        "end_sec": end,
                        "pacing": segment.get("pacing", "medium"),
                        "text": text,
                    }
                )
            elif kind == "choreography":
                shorthand = str(segment.get("shorthand", "")).strip()
                if not shorthand:
                    raise PhaseGateError(f"{class_id}: choreography segment {index} missing shorthand")
                tokens = self.engine.parse_line(shorthand)
                choreography_raw.append(
                    {
                        "start_sec": start,
                        "end_sec": end,
                        "shorthand": shorthand,
                        "pose_tokens": [token.base for token in tokens if token.kind == "pose"],
                        "operator_tokens": [token.raw for token in tokens if token.kind == "operator"],
                        "text": text,
                    }
                )
            elif kind == "theme":
                lower = text.lower()
                thematic_drops.append(
                    {
                        "start_sec": start,
                        "end_sec": end,
                        "text": text,
                        "terms": sorted(term for term in THEME_TERMS if term in lower),
                    }
                )
            else:
                raise PhaseGateError(f"{class_id}: segment {index} has unknown kind {kind!r}")

        return {
            "metadata": metadata,
            "audio_timeline": audio_timeline,
            "choreography_raw": choreography_raw,
            "thematic_drops": thematic_drops,
        }

    def run_phase(self, phase: str, classes: list[dict[str, Any]]) -> PhaseResult:
        if phase not in PHASE_RULES:
            raise PhaseGateError(f"unknown phase {phase!r}")

        parsed: list[dict[str, Any]] = []
        findings: list[str] = []
        for data in classes:
            try:
                parsed_class = self.parse_class(data)
                parsed.append(parsed_class)
                for required in ("metadata", "audio_timeline", "choreography_raw", "thematic_drops"):
                    if not parsed_class.get(required):
                        findings.append(f"{parsed_class['metadata']['class_id']}: missing {required}")
            except PhaseGateError as exc:
                findings.append(str(exc))

        min_count, max_count = PHASE_RULES[phase]
        count = len(classes)
        if count < min_count:
            findings.append(f"{phase}: requires at least {min_count} class(es), got {count}")
        if max_count is not None and count > max_count:
            findings.append(f"{phase}: allows at most {max_count} class(es), got {count}")

        return PhaseResult(
            phase=phase,
            class_count=count,
            go=not findings,
            findings=findings,
            parsed_classes=parsed,
        )


def load_classes(paths: list[Path]) -> list[dict[str, Any]]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a yoga class ingest phase gate.")
    parser.add_argument("phase", choices=sorted(PHASE_RULES))
    parser.add_argument("class_json", nargs="+", type=Path)
    parser.add_argument("--skill-root", type=Path, default=None)
    args = parser.parse_args(argv)

    ingest = PhaseGateIngest.load(args.skill_root)
    result = ingest.run_phase(args.phase, load_classes(args.class_json))
    print(json.dumps(result.__dict__, indent=2, sort_keys=True))
    return 0 if result.go else 1


if __name__ == "__main__":
    sys.exit(main())
