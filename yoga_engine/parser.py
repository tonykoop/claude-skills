"""
parser.py — shorthand → Sequence parser.

Full notation documented in yoga_engine/NOTATION.md.

Grammar (EBNF sketch):
    shorthand    := { comment | meta_line | phase_line }
    meta_line    := "#" META_KEY ":" VALUE
    phase_line   := LABEL ":" chain
    chain        := token_spec { OP token_spec }
    token_spec   := TOKEN [ "_" SIDE ] [ "/" BREATH_COUNT ]
    OP           := "+" | ">" | "//"
    META_KEY     := "TITLE" | "DURATION" | "HEATED" | "LEVEL" | "THEME"

Examples:
    # TITLE: Sunday Flow
    # DURATION: 60
    # HEATED: true
    AR: SC/3 > BW/3
    WU: CC/5 > TB > DD > LL_r > DD > LL_l
    BD: WR2_r > EK_r > Viny > WR2_l > EK_l > Viny > HL_r/3 > Viny > HL_l/3
    PK: WR3_r > Viny > WR3_l > CM/5 > CB
    CD: PT_r/10 > ST > PT_l/10 > SF/5
    SV: SV/5
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from .schema import (
    BreathOp, Phase, PhaseBlock, PoseInstance, Sequence,
)
from .pose_db import MACROS, POSE_DB


# ---------------------------------------------------------------------------
# Phase label → Phase enum map
# ---------------------------------------------------------------------------

_LABEL_TO_PHASE: Dict[str, Phase] = {
    "AR":  Phase.ARRIVAL,
    "ARR": Phase.ARRIVAL,
    "WU":  Phase.WARMUP,
    "BD":  Phase.BUILD,
    "BLD": Phase.BUILD,
    "PK":  Phase.PEAK,
    "PKS": Phase.PEAK,
    "CD":  Phase.COOLDOWN,
    "CDN": Phase.COOLDOWN,
    "SV":  Phase.SAVASANA,
    "SAV": Phase.SAVASANA,
    # Alternates
    "ARRIVAL":  Phase.ARRIVAL,
    "WARMUP":   Phase.WARMUP,
    "BUILD":    Phase.BUILD,
    "PEAK":     Phase.PEAK,
    "COOLDOWN": Phase.COOLDOWN,
    "SAVASANA": Phase.SAVASANA,
}

# ---------------------------------------------------------------------------
# Breath operator tokens
# ---------------------------------------------------------------------------

_OP_TOKENS: Dict[str, BreathOp] = {
    "+":  BreathOp.INHALE,
    ">":  BreathOp.EXHALE,
    "//": BreathOp.HOLD,
}

# Regex for a single token + optional _SIDE + optional /N
# TOKEN: 1–5 uppercase alphanumeric chars (e.g. DD, WR2, Viny)
# SIDE:  one of r|l|f|b|open|cl
# N:     1–3 digit breath count
_TOKEN_RE = re.compile(
    r"(?P<token>[A-Za-z][A-Za-z0-9]{0,4})"
    r"(?:_(?P<side>r|l|f|b|open|cl))?"
    r"(?:/(?P<bc>\d{1,3}))?"
)

# Meta line  "#  KEY : value"
_META_RE = re.compile(r"#\s*(?P<key>\w+)\s*:\s*(?P<value>.+)")


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def expand_macros(text: str, macros: Optional[Dict[str, str]] = None) -> str:
    """
    Replace macro names in *text* with their expanded form.

    Only top-level tokens (whole words bounded by operators / whitespace)
    are substituted — avoids replacing substrings inside longer tokens.

    Args:
        text:   Raw shorthand text (may span multiple lines).
        macros: Custom macro dict; defaults to yoga_engine.pose_db.MACROS.

    Returns:
        Shorthand with macros expanded (single pass; no recursive expansion).
    """
    if macros is None:
        macros = MACROS

    # Sort longest macro name first to avoid partial matches
    sorted_names = sorted(macros.keys(), key=len, reverse=True)

    # Build a regex that matches macro names as whole tokens
    if not sorted_names:
        return text

    pattern = re.compile(
        r"(?<![A-Za-z0-9_])(" + "|".join(re.escape(n) for n in sorted_names) + r")(?![A-Za-z0-9_/])"
    )

    def _replace(m: re.Match) -> str:
        return macros[m.group(1)]

    return pattern.sub(_replace, text)


# ---------------------------------------------------------------------------
# Internal parse helpers
# ---------------------------------------------------------------------------


def _parse_op(fragment: str) -> Optional[BreathOp]:
    """Return BreathOp if fragment is a breath operator, else None."""
    return _OP_TOKENS.get(fragment.strip())


def _parse_token_spec(fragment: str) -> PoseInstance:
    """
    Parse a single token spec like ``WR2_r/5``.

    Returns a PoseInstance (entry_op is None — callers set it).

    Raises ValueError if token is unknown.
    """
    fragment = fragment.strip()
    m = _TOKEN_RE.fullmatch(fragment)
    if not m:
        raise ValueError(f"Cannot parse token spec {fragment!r}")

    token = m.group("token")
    side = m.group("side")          # may be None
    bc_str = m.group("bc")          # may be None
    breath_count = int(bc_str) if bc_str else None

    pose = POSE_DB.get(token)
    if pose is None:
        raise ValueError(
            f"Unknown pose token {token!r}. "
            f"Available tokens: {', '.join(sorted(POSE_DB))}"
        )

    return PoseInstance(
        pose=pose,
        side=side,
        breath_count=breath_count,
        entry_op=None,
        raw_token=fragment,
    )


def _tokenize_chain(chain: str) -> List[Tuple[Optional[BreathOp], str]]:
    """
    Split a chain like ``WR2_r > EK_r > Viny`` into a list of
    ``(entry_op, raw_token_spec)`` tuples.

    The first entry always has entry_op=None.
    """
    # Normalise the chain: add spaces around operators so splitting is uniform
    # Operators: "//" must come before "/" so it is matched first
    chain = chain.strip()

    # Insert sentinel spaces around operators for easy splitting
    chain = re.sub(r"\s*//()\s*", " // ", chain)
    chain = re.sub(r"\s*\+\s*", " + ", chain)
    chain = re.sub(r"\s*>\s*", " > ", chain)

    parts = chain.split()

    result: List[Tuple[Optional[BreathOp], str]] = []
    pending_op: Optional[BreathOp] = None

    for part in parts:
        if part in _OP_TOKENS:
            pending_op = _OP_TOKENS[part]
        else:
            result.append((pending_op, part))
            pending_op = None

    return result


def _parse_phase_line(label: str, chain: str) -> PhaseBlock:
    """
    Parse a phase label + chain into a PhaseBlock.

    Unknown phase labels default to WARMUP with a warning (parseable, not fatal).
    """
    phase = _LABEL_TO_PHASE.get(label.upper(), Phase.WARMUP)
    block = PhaseBlock(label=label, phase=phase)

    pairs = _tokenize_chain(chain)
    for op, raw_spec in pairs:
        instance = _parse_token_spec(raw_spec)
        instance.entry_op = op
        block.poses.append(instance)

    return block


# ---------------------------------------------------------------------------
# Public parse entry point
# ---------------------------------------------------------------------------


class ParseError(ValueError):
    """Raised when the shorthand cannot be parsed."""


def parse_shorthand(
    text: str,
    macros: Optional[Dict[str, str]] = None,
    default_title: str = "Untitled Class",
    default_duration: int = 60,
) -> Sequence:
    """
    Parse a shorthand string into a :class:`~yoga_engine.schema.Sequence`.

    Meta directives (``# KEY: value``) recognised:
    - ``# TITLE: My Sunday Flow``
    - ``# DURATION: 75``
    - ``# HEATED: true``
    - ``# LEVEL: intermediate``
    - ``# THEME: hip openers``

    Args:
        text:             Raw shorthand text.
        macros:           Custom macro dict; pass ``{}`` to disable macros.
        default_title:    Fallback title if none specified in text.
        default_duration: Fallback duration in minutes.

    Returns:
        Parsed :class:`~yoga_engine.schema.Sequence`.

    Raises:
        ParseError: On any unrecoverable parse failure.
    """
    if macros is None:
        macros = MACROS

    # Step 1 — expand macros
    expanded = expand_macros(text, macros)

    # Step 2 — extract meta + phase lines
    title = default_title
    duration = default_duration
    heated = False
    level = "mixed"
    theme = ""

    phases: List[PhaseBlock] = []

    for lineno, raw_line in enumerate(expanded.splitlines(), start=1):
        line = raw_line.strip()

        # Skip blank lines
        if not line:
            continue

        # Meta comment: # KEY: value
        meta_m = _META_RE.match(line)
        if meta_m:
            key = meta_m.group("key").upper()
            value = meta_m.group("value").strip()
            if key == "TITLE":
                title = value
            elif key == "DURATION":
                try:
                    duration = int(value)
                except ValueError:
                    raise ParseError(f"Line {lineno}: DURATION must be an integer, got {value!r}")
            elif key == "HEATED":
                heated = value.lower() in ("true", "yes", "1", "on")
            elif key == "LEVEL":
                level = value.lower()
            elif key == "THEME":
                theme = value
            # Unknown meta keys are silently ignored (forward-compat)
            continue

        # Regular comment (no colon after #keyword) — skip
        if line.startswith("#"):
            continue

        # Phase line: LABEL: chain
        if ":" not in line:
            raise ParseError(
                f"Line {lineno}: expected 'LABEL: chain' or '# META: value', "
                f"got {raw_line!r}"
            )

        colon_idx = line.index(":")
        label = line[:colon_idx].strip()
        chain = line[colon_idx + 1:].strip()

        if not chain:
            # Empty phase is legal (teacher leaves it blank)
            phases.append(PhaseBlock(
                label=label,
                phase=_LABEL_TO_PHASE.get(label.upper(), Phase.WARMUP),
            ))
            continue

        try:
            block = _parse_phase_line(label, chain)
        except ValueError as exc:
            raise ParseError(f"Line {lineno}: {exc}") from exc

        phases.append(block)

    return Sequence(
        title=title,
        duration_minutes=duration,
        phases=phases,
        heated_room=heated,
        level=level,
        theme=theme,
        raw_shorthand=text,
    )
