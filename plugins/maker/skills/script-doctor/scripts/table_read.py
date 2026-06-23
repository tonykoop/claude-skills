#!/usr/bin/env python3
"""
Table-read pass — story #427.

Heuristic analysis of a script for readability, breath breaks, pacing,
and archetype alignment. Returns the canonical pass schema expected by
run_review.py and test_scaffold.py.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_REFERENCES_DIR = Path(__file__).resolve().parent.parent / "references"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ACRONYM_RE = re.compile(r"\b[A-Z]{2,5}\b")
_PASSIVE_RE = re.compile(
    r"\b(?:is|are|was|were|be|been|being)\s+\w+ed\b", re.IGNORECASE
)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _sentences(text: str) -> list[str]:
    clean = re.sub(r"\*\*\[.*?\]\*\*", "", text)
    clean = re.sub(r"[*_#>`|-]", "", clean)
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(clean) if s.strip()]


def _paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]


def _words(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text)


def _flag(location: str, severity: str, message: str) -> dict:
    return {"line": location, "severity": severity, "message": message}


# ---------------------------------------------------------------------------
# Hard-to-speak detector
# ---------------------------------------------------------------------------

def _find_hard_to_speak(sentences: list[str]) -> list[dict]:
    flags: list[dict] = []
    for i, sent in enumerate(sentences, 1):
        words = _words(sent)
        comma_count = sent.count(",")
        label = f"sentence {i}"

        if len(words) > 30:
            flags.append(_flag(label, "polish",
                               f"HARD-TO-SPEAK: {sent[:80]}{'…' if len(sent) > 80 else ''} "
                               f"→ EASIER: break into two shorter sentences ({len(words)} words)"))

        elif comma_count > 3:
            flags.append(_flag(label, "polish",
                               f"HARD-TO-SPEAK: {sent[:80]}{'…' if len(sent) > 80 else ''} "
                               f"→ EASIER: reduce nested clauses ({comma_count} commas)"))

        acronyms = _ACRONYM_RE.findall(sent)
        if acronyms:
            for acr in set(acronyms):
                flags.append(_flag(label, "note",
                                   f"ACRONYM: '{acr}' — confirm pronunciation is clear when spoken aloud"))

        if _PASSIVE_RE.search(sent):
            flags.append(_flag(label, "note",
                               f"PASSIVE: '{sent[:60]}…' — consider active voice for clearer delivery"))

    return flags


# ---------------------------------------------------------------------------
# Breath-break inserter
# ---------------------------------------------------------------------------

def _breath_breaks(paragraphs: list[str]) -> list[dict]:
    breaks: list[dict] = []
    word_accumulator = 0
    last_break_at = 0

    for i, para in enumerate(paragraphs):
        word_count = len(_words(para))
        word_accumulator += word_count

        is_stage_direction = para.startswith("**[") or para.startswith("[")
        if is_stage_direction:
            breaks.append({
                "location": f"paragraph {i + 1}",
                "type": "natural",
                "note": "[BREATH] — stage direction / scene transition"
            })
            last_break_at = word_accumulator
            continue

        if word_accumulator - last_break_at >= 50:
            breaks.append({
                "location": f"end of paragraph {i + 1}",
                "type": "recommended",
                "note": "[BREATH] — insert pause here"
            })
            last_break_at = word_accumulator

    return breaks


# ---------------------------------------------------------------------------
# Pacing scorer
# ---------------------------------------------------------------------------

def _pacing_by_section(paragraphs: list[str]) -> list[dict]:
    sections: list[dict] = []
    bucket_words = 0
    bucket_paras: list[str] = []
    bucket_start = 1

    def _flush(start: int, paras: list[str], words: int) -> dict | None:
        if not paras:
            return None
        duration_sec = words / 2.5
        label = f"paragraphs {start}–{start + len(paras) - 1}"
        if duration_sec < 15:
            pace = "FAST"
        elif duration_sec < 35:
            pace = "MEDIUM"
        else:
            pace = "SLOW"
        return {"label": label, "pace": pace,
                "words": words, "estimated_sec": round(duration_sec)}

    for i, para in enumerate(paragraphs, 1):
        wc = len(_words(para))
        bucket_words += wc
        bucket_paras.append(para)
        if bucket_words >= 60 or i == len(paragraphs):
            result = _flush(bucket_start, bucket_paras, bucket_words)
            if result:
                sections.append(result)
            bucket_words = 0
            bucket_paras = []
            bucket_start = i + 1

    return sections


# ---------------------------------------------------------------------------
# Archetype alignment
# ---------------------------------------------------------------------------

def _check_archetype(text: str, channel: str, avg_sentence_len: float) -> str:
    profile_path = _REFERENCES_DIR / "channel-profiles.yaml"
    try:
        import yaml  # noqa: PLC0415
        profiles = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
        profile = profiles.get("profiles", {}).get(channel)
    except Exception:
        profile = None

    if not profile:
        return "MATCH"  # unknown channel — no constraints to check

    archetype = profile.get("archetype", channel)
    pacing = profile.get("pacing_profile", {})

    intro_sec = pacing.get("intro_sec", 15)
    word_budget_intro = intro_sec * 2.5

    # Yoga: avg sentence should be short; AI/agentic: punchy
    if archetype == "yoga":
        if avg_sentence_len > 20:
            return "MISMATCH"
    elif archetype in ("ai_agentic", "coding"):
        if avg_sentence_len > 25:
            return "MISMATCH"
    elif archetype == "wrfcoin":
        numbers = re.findall(r"\b\d[\d,.%$]*\b", text)
        labels = re.findall(r"\b\d[\d,.%$]*\s+\w+\b", text)
        if numbers and len(labels) < len(numbers) * 0.5:
            return "MISMATCH"

    return "MATCH"


# ---------------------------------------------------------------------------
# Readability scorer
# ---------------------------------------------------------------------------

def _readability_score(hard_to_speak: list[dict],
                       breath_breaks: list[dict],
                       archetype_alignment: str) -> float:
    score = 9.0
    blocker_flags = [f for f in hard_to_speak if f["severity"] == "polish"]
    score -= min(len(blocker_flags), 3)
    recommended_breaks = [b for b in breath_breaks if b["type"] == "recommended"]
    if not recommended_breaks:
        score -= 1.0
    if archetype_alignment == "MISMATCH":
        score -= 1.0
    return max(1.0, round(score, 1))


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_table_read(script: str, channel: str = "generic") -> dict[str, Any]:
    sentences = _sentences(script)
    paragraphs = _paragraphs(script)
    all_words = _words(script)

    word_count = len(all_words)
    estimated_runtime_sec = round(word_count / 2.5)
    avg_sentence_len = (word_count / len(sentences)) if sentences else 0

    hard_to_speak = _find_hard_to_speak(sentences)
    breath_breaks = _breath_breaks(paragraphs)
    pacing = _pacing_by_section(paragraphs)
    archetype_alignment = _check_archetype(script, channel, avg_sentence_len)
    readability = _readability_score(hard_to_speak, breath_breaks, archetype_alignment)

    all_flags = hard_to_speak[:]
    if archetype_alignment == "MISMATCH":
        all_flags.append(_flag("overall", "polish",
                               f"ARCHETYPE MISMATCH: spoken rhythm does not match '{channel}' profile — "
                               "review sentence length and pacing targets"))

    return {
        "pass": "table_read",
        "score": readability,
        "flags": all_flags,
        "archetype": channel,
        "readability_score": readability,
        "estimated_runtime_sec": estimated_runtime_sec,
        "word_count": word_count,
        "breath_breaks": breath_breaks,
        "hard_to_speak": hard_to_speak,
        "pacing_by_section": pacing,
        "archetype_alignment": archetype_alignment,
    }
