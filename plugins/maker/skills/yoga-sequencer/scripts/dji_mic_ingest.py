#!/usr/bin/env python3
"""Validate and split DJI Mic capture manifests into language and audio paths."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


THEME_TERMS = {"attention", "breath", "ease", "effort", "intention", "notice", "space", "theme"}
ALLOWED_NOISE = {"low", "moderate", "high"}


class DjiMicIngestError(ValueError):
    """Raised when a capture manifest is structurally invalid."""


@dataclass(frozen=True)
class CaptureSplit:
    capture_id: str
    path_a_language: dict[str, Any]
    path_b_audio: dict[str, Any]
    quality_gate: dict[str, Any]


class DjiMicIngest:
    def split(self, manifest: dict[str, Any]) -> CaptureSplit:
        capture_id = str(manifest.get("capture_id", "")).strip()
        if not capture_id:
            raise DjiMicIngestError("capture_id is required")
        duration_sec = float(manifest.get("duration_sec", 0))
        if duration_sec <= 0:
            raise DjiMicIngestError(f"{capture_id}: duration_sec must be positive")

        transcript_spans = self._transcript_spans(manifest)
        thematic_script = self._thematic_script(transcript_spans)
        audio_timeline = self._audio_timeline(manifest)
        findings = self._quality_findings(manifest, transcript_spans)

        return CaptureSplit(
            capture_id=capture_id,
            path_a_language={
                "transcript_spans": transcript_spans,
                "thematic_script": thematic_script,
                "rosetta_ready": not findings,
            },
            path_b_audio={
                "audio_file": manifest.get("audio_file", ""),
                "duration_sec": duration_sec,
                "timeline": audio_timeline,
                "playlist_handoff_ready": bool(audio_timeline),
            },
            quality_gate={
                "capture_quality_ok": not findings,
                "findings": findings,
            },
        )

    def _transcript_spans(self, manifest: dict[str, Any]) -> list[dict[str, Any]]:
        spans = manifest.get("transcript", [])
        if not isinstance(spans, list) or not spans:
            raise DjiMicIngestError("transcript must be a non-empty list")
        normalized = []
        for index, span in enumerate(spans):
            start = float(span.get("start_sec", 0))
            end = float(span.get("end_sec", 0))
            text = str(span.get("text", "")).strip()
            if end <= start:
                raise DjiMicIngestError(f"transcript span {index} must have positive duration")
            if not text:
                raise DjiMicIngestError(f"transcript span {index} must include text")
            normalized.append({"start_sec": start, "end_sec": end, "text": text})
        return normalized

    def _thematic_script(self, spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
        thematic = []
        for span in spans:
            lower = span["text"].lower()
            terms = sorted(term for term in THEME_TERMS if term in lower)
            if terms:
                thematic.append({**span, "terms": terms})
        return thematic

    def _audio_timeline(self, manifest: dict[str, Any]) -> list[dict[str, Any]]:
        timeline = manifest.get("timeline", [])
        if not isinstance(timeline, list):
            raise DjiMicIngestError("timeline must be a list")
        normalized = []
        for index, item in enumerate(timeline):
            start = float(item.get("start_sec", 0))
            end = float(item.get("end_sec", 0))
            if end <= start:
                raise DjiMicIngestError(f"timeline item {index} must have positive duration")
            normalized.append(
                {
                    "start_sec": start,
                    "end_sec": end,
                    "phase": item.get("phase", ""),
                    "energy": item.get("energy", ""),
                    "cue_density": item.get("cue_density", ""),
                }
            )
        return normalized

    def _quality_findings(self, manifest: dict[str, Any], spans: list[dict[str, Any]]) -> list[str]:
        findings: list[str] = []
        quality = manifest.get("quality", {})
        music_bed_db = float(quality.get("music_bed_db", -99))
        movement_noise = str(quality.get("movement_noise", "low"))
        dropouts = int(quality.get("dropouts", 0))
        clipping = bool(quality.get("clipping", False))

        if music_bed_db > -18:
            findings.append("music bed is too loud for reliable transcript alignment")
        if movement_noise not in ALLOWED_NOISE:
            findings.append(f"movement_noise must be one of {sorted(ALLOWED_NOISE)}")
        elif movement_noise == "high":
            findings.append("movement noise is high; transcript needs QA before Rosetta ingest")
        if dropouts:
            findings.append("audio dropouts must be repaired before Rosetta ingest")
        if clipping:
            findings.append("clipping detected; capture is not Rosetta-ready")
        if not spans:
            findings.append("no transcript spans found")
        return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Split a DJI Mic capture manifest into language/audio paths.")
    parser.add_argument("manifest_json", type=Path)
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest_json.read_text(encoding="utf-8"))
    split = DjiMicIngest().split(manifest)
    print(json.dumps(split.__dict__, indent=2, sort_keys=True))
    return 0 if split.quality_gate["capture_quality_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
