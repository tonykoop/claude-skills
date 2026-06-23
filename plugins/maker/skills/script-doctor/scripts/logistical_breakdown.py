#!/usr/bin/env python3
"""
Logistical breakdown pass — story #429.

Parses a script into a production asset table. One row per segment.
Returns the canonical pass schema expected by run_review.py.
"""
from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Segment detection
# ---------------------------------------------------------------------------

_SEG_RE = re.compile(
    r"\*\*\[(?P<directive>[^\]]+)\]\*\*",
    re.IGNORECASE,
)

_TYPE_MAP: dict[str, str] = {
    "open": "A-roll",
    "a-roll": "A-roll",
    "aroll": "A-roll",
    "cut": "A-roll",  # refined below by inspecting directive text
    "b-roll": "B-roll",
    "broll": "B-roll",
    "gen": "GEN",
    "text": "TEXT",
    "music": "MUSIC",
    "sfx": "SFX",
    "anim": "ANIM",
    "dissolve": "A-roll",
    "fade": "A-roll",
}

_BROLL_HINT_RE = re.compile(
    r"\b(b-roll|broll|footage|cutaway|close-?up|screen\s+recording|screengrab|screenshot|"
    r"terminal|tmux|ide|dashboard|chart|map|animation|archival|stock)\b",
    re.IGNORECASE,
)
_GEN_HINT_RE = re.compile(
    r"\b(gen|ai.gen|firefly|sora|kling|agy|midjourney|dall.?e|generated)\b",
    re.IGNORECASE,
)
_TEXT_HINT_RE = re.compile(
    r"\b(text\s+overlay|caption|lower\s+third|on.screen\s+(text|graphic)|overlay)\b",
    re.IGNORECASE,
)
_MUSIC_HINT_RE = re.compile(r"\b(music|sting|ambient|soundtrack|audio\s+bridge)\b", re.IGNORECASE)
_SFX_HINT_RE = re.compile(r"\b(sfx|sound\s+effect|foley)\b", re.IGNORECASE)


def _detect_type(directive: str) -> str:
    d = directive.lower()
    if _SFX_HINT_RE.search(d):
        return "SFX"
    if _MUSIC_HINT_RE.search(d):
        return "MUSIC"
    if _TEXT_HINT_RE.search(d):
        return "TEXT"
    if _GEN_HINT_RE.search(d):
        return "GEN"
    if _BROLL_HINT_RE.search(d):
        return "B-roll"
    first_word = d.split()[0].strip(",;:") if d.split() else ""
    return _TYPE_MAP.get(first_word, "A-roll")


# ---------------------------------------------------------------------------
# Location inference
# ---------------------------------------------------------------------------

_STUDIO_RE = re.compile(r"\b(studio|desk|workshop|home\s+(shop|lab)|on.mat|indoor)\b", re.IGNORECASE)
_OUTDOOR_RE = re.compile(r"\b(outdoor|outside|field|location)\b", re.IGNORECASE)
_SCREEN_RE = re.compile(r"\b(screen\s+recording|terminal|tmux|ide|vs\s+code|browser|dashboard)\b", re.IGNORECASE)
_ARCHIVAL_RE = re.compile(r"\b(archival|archive|stock|footage\s+from|from\s+\d{4})\b", re.IGNORECASE)


def _detect_location(directive: str, seg_type: str) -> str:
    if seg_type == "TEXT":
        return "graphic"
    if seg_type in ("MUSIC", "SFX"):
        return "audio"
    if seg_type == "GEN":
        return "AI-generated"
    if _SCREEN_RE.search(directive):
        return "screen recording"
    if _ARCHIVAL_RE.search(directive):
        return "archival / stock"
    if _OUTDOOR_RE.search(directive):
        return "outdoor"
    if _STUDIO_RE.search(directive):
        return "studio"
    if seg_type == "B-roll":
        return "location TBD"
    return "studio"


# ---------------------------------------------------------------------------
# Asset extraction
# ---------------------------------------------------------------------------

_QUOTED_RE = re.compile(r'"([^"]{3,80})"')
_FILENAME_RE = re.compile(r"\b[\w.-]+\.(csv|md|json|yaml|yml|py|js|ts|png|jpg|mp4|mov|wav|mp3)\b", re.IGNORECASE)
_TRACK_RE = re.compile(r"\b(artlist|storyblocks|pixabay|epidemic\s+sound)\b", re.IGNORECASE)


def _extract_assets(directive: str, seg_type: str) -> list[str]:
    assets: list[str] = []
    quoted = _QUOTED_RE.findall(directive)
    assets.extend(quoted)
    filenames = _FILENAME_RE.findall(directive)
    assets.extend(filenames)
    if seg_type == "MUSIC" and not assets:
        assets.append("background music track (source TBD)")
    if seg_type == "GEN" and not assets:
        assets.append("AI-generated visual (tool + prompt TBD)")
    return assets


# ---------------------------------------------------------------------------
# Props extraction
# ---------------------------------------------------------------------------

_PROP_NOUNS = re.compile(
    r"\b(reed|pipe|bamboo|brass|caliper|file|saw|router|drill|jig|mould|form|clamp|"
    r"instrument|microphone|camera|tripod|green\s*screen|whiteboard|notebook|laptop|"
    r"phone|tablet|book|poster|chart|graph|tool|material|wood|stave)\b",
    re.IGNORECASE,
)


def _extract_props(directive: str, seg_type: str) -> list[str]:
    if seg_type not in ("A-roll", "B-roll"):
        return []
    return list({m.lower() for m in _PROP_NOUNS.findall(directive)})


# ---------------------------------------------------------------------------
# Missing / at-risk classification
# ---------------------------------------------------------------------------

def _assess_risk(directive: str, seg_type: str, assets: list[str]) -> list[dict]:
    issues: list[dict] = []

    if seg_type == "GEN":
        has_prompt = bool(re.search(r"prompt[:：]", directive, re.IGNORECASE))
        if not has_prompt:
            issues.append({
                "severity": "risk",
                "message": f"GEN segment has no prompt annotation — specify tool + visual prompt"
            })

    if seg_type == "B-roll":
        has_source = bool(_TRACK_RE.search(directive) or _SCREEN_RE.search(directive)
                          or _ARCHIVAL_RE.search(directive) or _FILENAME_RE.search(directive))
        if not has_source:
            issues.append({
                "severity": "note",
                "message": f"B-roll has no stated source — add stock library, screen recording plan, or archival note"
            })

    if seg_type == "TEXT" and not assets:
        issues.append({
            "severity": "note",
            "message": "TEXT overlay has no graphic spec — add filename or graphic brief"
        })

    return issues


# ---------------------------------------------------------------------------
# TC estimator
# ---------------------------------------------------------------------------

def _tc(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_logistical_breakdown(script: str, channel: str = "generic") -> dict[str, Any]:
    segments: list[dict] = []
    missing_assets: list[dict] = []
    all_props: set[str] = set()
    all_locations: set[str] = set()
    all_flags: list[dict] = []

    word_cursor = 0
    lines = script.split("\n")
    current_seg_start_words = 0
    current_directive: str | None = None
    current_type: str | None = None
    current_body_words: list[str] = []
    seg_index = 0

    def _flush_seg():
        nonlocal seg_index, current_directive, current_type, current_body_words, current_seg_start_words, word_cursor
        if current_directive is None:
            return
        body = " ".join(current_body_words)
        body_wc = len(current_body_words)
        tc_in = _tc(current_seg_start_words / 2.5)
        tc_out = _tc(word_cursor / 2.5)

        seg_type = current_type or "A-roll"
        assets = _extract_assets(current_directive, seg_type)
        props = _extract_props(current_directive + " " + body, seg_type)
        location = _detect_location(current_directive + " " + body, seg_type)
        risks = _assess_risk(current_directive, seg_type, assets)

        all_props.update(props)
        all_locations.add(location)

        missing = [r["message"] for r in risks]
        if risks:
            for r in risks:
                sev = r["severity"]
                msg = r["message"]
                all_flags.append({"line": f"segment {seg_index + 1}", "severity": sev, "message": msg})
                missing_assets.append({"segment": seg_index + 1, "severity": sev, "issue": msg})

        segments.append({
            "index": seg_index + 1,
            "tc_in": tc_in,
            "tc_out": tc_out,
            "type": seg_type,
            "description": body[:120] if body else current_directive[:120],
            "assets_needed": assets,
            "props": props,
            "location": location,
            "missing_at_risk": missing,
        })
        seg_index += 1
        current_directive = None
        current_type = None
        current_body_words = []
        current_seg_start_words = word_cursor

    for line in lines:
        seg_match = _SEG_RE.search(line)
        if seg_match:
            _flush_seg()
            directive = seg_match.group("directive")
            current_directive = directive
            current_type = _detect_type(directive)
            current_seg_start_words = word_cursor
        else:
            content_words = re.findall(r"\b\w+\b", line)
            if current_directive is not None:
                current_body_words.extend(content_words)
            word_cursor += len(content_words)

    _flush_seg()

    if not segments:
        segments.append({
            "index": 1,
            "tc_in": "0:00",
            "tc_out": _tc(len(re.findall(r"\b\w+\b", script)) / 2.5),
            "type": "A-roll",
            "description": script[:120],
            "assets_needed": [],
            "props": [],
            "location": "studio",
            "missing_at_risk": ["NOTE: no stage directions detected — breakdown is estimated"],
        })

    blocker_count = sum(1 for f in all_flags if f["severity"] == "blocker")
    risk_count = sum(1 for f in all_flags if f["severity"] == "risk")
    producibility = max(1.0, round(10.0 - blocker_count * 1.0 - risk_count * 0.5, 1))

    return {
        "pass": "logistical_breakdown",
        "score": producibility,
        "flags": all_flags,
        "segments": segments,
        "missing_assets": missing_assets,
        "props": sorted(all_props),
        "locations": sorted(all_locations),
        "producibility_score": producibility,
    }
