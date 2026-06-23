#!/usr/bin/env python3
"""
Structural polish pass — story #428.

Heuristic analysis of a script for hook strength, on-the-nose dialogue,
retention dips, transition gaps, and closing strength. Returns the
canonical pass schema expected by run_review.py.
"""
from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_STAGE_DIR_RE = re.compile(r"\*\*\[([^\]]+)\]\*\*")
_WEAK_OPENERS = re.compile(
    r"^\s*(hello\s+everyone|hi\s+everyone|hey\s+everyone|welcome\s+(back|to)|"
    r"in\s+this\s+video|today\s+we|today\s+i'?m|today\s+i\s+want|"
    r"so\s+today|welcome\s+back)",
    re.IGNORECASE,
)
_STRONG_HOOK_RE = re.compile(
    r"(\?|never|impossible|secret|i\s+let\s+an?\s+|last\s+week\s+i|"
    r"have\s+you\s+ever|what\s+if\s+|imagine\s+)",
    re.IGNORECASE,
)
_ON_THE_NOSE_PATTERNS = [
    (re.compile(r"this\s+is\s+incredible", re.IGNORECASE),
     "→ let the image speak; cut 'this is incredible'"),
    (re.compile(r"as\s+you\s+can\s+see", re.IGNORECASE),
     "→ cut entirely; the viewer can see"),
    (re.compile(r"the\s+point\s+is", re.IGNORECASE),
     "→ restructure so the point is shown, not announced"),
    (re.compile(r"what\s+this\s+means\s+is", re.IGNORECASE),
     "→ let the demo explain; trust the viewer"),
    (re.compile(r"\b(beautiful|amazing|incredible|stunning)\s+\w+(ly\s+)?(way|how|that|this)", re.IGNORECASE),
     "→ show the object/action; drop the emotional adjective"),
    (re.compile(r"it'?s\s+(really|very|super|so)\s+(important|interesting|cool|amazing)", re.IGNORECASE),
     "→ state why it matters; avoid intensity adverbs"),
]
_CTA_VERBS = re.compile(
    r"\b(subscribe|like|follow|comment|share|hit\s+the\s+bell|link\s+in\s+(the\s+)?(bio|description|below))\b",
    re.IGNORECASE,
)
_TRANSITION_RE = re.compile(r"\*\*\[(CUT|OPEN|DISSOLVE|FADE|B-ROLL|GEN|TEXT|MUSIC|SFX|ANIM)[^\]]*\]\*\*", re.IGNORECASE)


def _paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]


def _words(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text)


def _flag(location: str, severity: str, message: str) -> dict:
    return {"line": location, "severity": severity, "message": message}


def _strip_stage_dirs(text: str) -> str:
    return _STAGE_DIR_RE.sub("", text).strip()


# ---------------------------------------------------------------------------
# Hook scorer
# ---------------------------------------------------------------------------

def _score_hook(paragraphs: list[str]) -> tuple[float, str]:
    first_content = ""
    for para in paragraphs[:3]:
        clean = _strip_stage_dirs(para)
        if clean:
            first_content = clean
            break

    if not first_content:
        return 3.0, "No opening content found — hook is absent."

    score = 6.0
    note_parts: list[str] = []

    if _WEAK_OPENERS.search(first_content):
        score -= 2.0
        note_parts.append("weak opener detected (greeting/scene-setter)")

    if _STRONG_HOOK_RE.search(first_content):
        score += 2.0
        note_parts.append("strong hook signal (question/unusual claim)")

    if first_content.endswith("?") or "?" in first_content[:120]:
        score += 1.0
        note_parts.append("opens with question — creates gap")

    score = max(1.0, min(10.0, round(score, 1)))
    verdict = f"{score}/10 — " + ("; ".join(note_parts) if note_parts else "acceptable hook")
    return score, verdict


# ---------------------------------------------------------------------------
# On-the-nose detector
# ---------------------------------------------------------------------------

def _find_on_the_nose(paragraphs: list[str]) -> list[dict]:
    flags: list[dict] = []
    for i, para in enumerate(paragraphs, 1):
        clean = _strip_stage_dirs(para)
        for pattern, suggestion in _ON_THE_NOSE_PATTERNS:
            m = pattern.search(clean)
            if m:
                snippet = clean[max(0, m.start() - 20): m.end() + 40].strip()
                flags.append(_flag(
                    f"paragraph {i}", "polish",
                    f"ON-THE-NOSE: '{snippet}' {suggestion}"
                ))
    return flags


# ---------------------------------------------------------------------------
# Retention dip detector
# ---------------------------------------------------------------------------

def _retention_dips(paragraphs: list[str]) -> list[dict]:
    dips: list[dict] = []
    for i, para in enumerate(paragraphs, 1):
        clean = _strip_stage_dirs(para)
        all_words = _words(clean)
        if len(all_words) < 8:
            continue
        unique_ratio = len(set(w.lower() for w in all_words)) / len(all_words)
        duration_sec = len(all_words) / 2.5
        if unique_ratio < 0.4 and duration_sec > 10:
            dips.append(_flag(
                f"paragraph {i}", "polish",
                f"RETENTION DIP: low information density ({unique_ratio:.0%} unique words, "
                f"~{duration_sec:.0f}s) — consider cutting or adding B-roll to maintain visual interest"
            ))
    return dips


# ---------------------------------------------------------------------------
# Transition auditor
# ---------------------------------------------------------------------------

def _transition_audit(text: str) -> list[dict]:
    gaps: list[dict] = []
    lines = text.split("\n")
    prev_was_transition = False
    prev_line_num = 0

    for i, line in enumerate(lines, 1):
        is_transition = bool(_TRANSITION_RE.search(line))
        if is_transition:
            if prev_was_transition:
                gaps.append(_flag(
                    f"line {i}", "note",
                    f"TRANSITION GAP: consecutive stage directions at lines {prev_line_num}–{i} "
                    "with no content between them — suggest cold cut or merge into one direction"
                ))
            prev_was_transition = True
            prev_line_num = i
        elif line.strip():
            prev_was_transition = False

    return gaps


# ---------------------------------------------------------------------------
# Closing scorer
# ---------------------------------------------------------------------------

def _score_closing(paragraphs: list[str]) -> tuple[float, str]:
    last_content = ""
    for para in reversed(paragraphs[-4:]):
        clean = _strip_stage_dirs(para)
        if clean:
            last_content = clean
            break

    if not last_content:
        return 4.0, "No closing content found."

    score = 6.0
    note_parts: list[str] = []

    if _CTA_VERBS.search(last_content):
        score += 1.5
        note_parts.append("CTA present")
    else:
        score -= 1.0
        note_parts.append("no CTA detected")

    cta_count = len(_CTA_VERBS.findall(last_content))
    if cta_count > 3:
        score -= 1.0
        note_parts.append(f"{cta_count} CTAs — reduce to 1–2 asks")

    if last_content.endswith("?"):
        score += 0.5
        note_parts.append("closing question — mild memory hook")

    score = max(1.0, min(10.0, round(score, 1)))
    verdict = f"{score}/10 — " + ("; ".join(note_parts) if note_parts else "acceptable closing")
    return score, verdict


# ---------------------------------------------------------------------------
# Overall summary
# ---------------------------------------------------------------------------

def _overall_summary(hook_score: float, closing_score: float,
                     on_the_nose: list, dips: list) -> str:
    issues = []
    if hook_score < 5:
        issues.append("rewrite the hook (under 5/10)")
    if on_the_nose:
        issues.append(f"cut {len(on_the_nose)} on-the-nose line(s)")
    if len(dips) > 2:
        issues.append("compress low-density sections to improve retention")
    if closing_score < 5:
        issues.append("add a clear CTA to the closing")

    if not issues:
        return "Script is structurally solid — polish optional."
    return "Highest-impact single rewrite: " + issues[0] + (
        f" (also: {'; '.join(issues[1:])})" if len(issues) > 1 else ""
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_structural_polish(script: str, channel: str = "generic") -> dict[str, Any]:
    paragraphs = _paragraphs(script)

    hook_score, hook_verdict = _score_hook(paragraphs)
    closing_score, closing_verdict = _score_closing(paragraphs)
    on_the_nose = _find_on_the_nose(paragraphs)
    retention_dips = _retention_dips(paragraphs)
    transition_gaps = _transition_audit(script)

    all_flags: list[dict] = []
    if hook_score < 5:
        all_flags.append(_flag("hook", "blocker",
                               f"Hook strength {hook_score}/10 — below threshold; rewrite required"))
    all_flags.extend(on_the_nose)
    all_flags.extend(retention_dips)
    all_flags.extend(transition_gaps)

    composite = round((hook_score + closing_score) / 2, 1)

    return {
        "pass": "structural_polish",
        "score": composite,
        "flags": all_flags,
        "hook_score": hook_score,
        "hook_verdict": hook_verdict,
        "closing_score": closing_score,
        "closing_verdict": closing_verdict,
        "on_the_nose": on_the_nose,
        "retention_dips": retention_dips,
        "transition_gaps": transition_gaps,
        "overall_summary": _overall_summary(hook_score, closing_score, on_the_nose, retention_dips),
    }
