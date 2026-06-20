"""
transitions.py — Transition Matrix for the yoga_engine (Story #370).

Models the "space between" postures as explicit vector paths:

    TransitionVector(origin, pathway, target)

Each transition has:
- origin: source pose token (from POSE_DB)
- pathway: modifier describing the movement quality
- target: destination pose token
- pacing: "slow" | "medium" | "fast" — drives DJ/playlist crossfade speed
- breath_op: the BreathOp used when entering target (inhale/exhale/hold)
- cue_template: generic teacher-cue template for this transition
  (placeholders: {origin}, {target}, {side} — no proprietary language)

The TRANSITION_DB is a dict keyed by (origin_token, target_token) → list of
TransitionVector, so multiple entry pathways into the same target are supported.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from .schema import BreathOp


# ---------------------------------------------------------------------------
# Pathway qualifiers
# ---------------------------------------------------------------------------


class Pathway(str, Enum):
    """Movement quality / spatial path of the transition."""
    STEP_FORWARD     = "step_forward"       # foot steps toward top of mat
    STEP_BACK        = "step_back"          # foot steps toward back of mat
    SWEEP_UP         = "sweep_up"           # arms/body rise upward
    FOLD_DOWN        = "fold_down"          # body folds / descends
    PIVOT            = "pivot"              # feet pivot in place
    SLIDE            = "slide"              # sliding or gliding weight shift
    JUMP             = "jump"              # a hop or jump transition
    ROLL             = "roll"              # spinal roll (up or down)
    LOWER            = "lower"             # lowering with control (e.g. chaturanga)
    PRESS            = "press"             # pressing into the mat (upward)
    REACH            = "reach"             # extending toward / away
    OPEN             = "open"              # widening stance or chest
    CLOSE            = "close"             # narrowing/drawing in
    FLOW             = "flow"              # smooth vinyasa-style flow
    HOLD             = "hold"              # staying, no pathway movement


class Pacing(str, Enum):
    """Transition speed — feeds DJ/playlist crossfade duration."""
    SLOW   = "slow"     # 1.5–2 beats (sustained, contemplative)
    MEDIUM = "medium"   # 1 beat (standard vinyasa tempo)
    FAST   = "fast"     # half-beat or quick-transition

    @property
    def crossfade_bars(self) -> float:
        """Approximate DJ crossfade in musical bars (4/4 @ ~70 BPM)."""
        return {"slow": 2.0, "medium": 1.0, "fast": 0.5}[self.value]


# ---------------------------------------------------------------------------
# Transition data model
# ---------------------------------------------------------------------------


@dataclass
class TransitionVector:
    """
    A single directed transition: Origin → (via Pathway) → Target.

    Multiple TransitionVectors can share the same (origin, target) pair —
    each capturing a distinct pathway or cue variation.
    """
    origin: str           # pose token
    pathway: Pathway
    target: str           # pose token
    breath_op: BreathOp
    pacing: Pacing = Pacing.MEDIUM

    # Generic cue template.
    # Placeholders: {origin}, {target}, {side}, {breath}
    # Do NOT put proprietary voice patterns here — this is structural only.
    cue_template: str = ""

    # Optional transcript slot: filled at runtime by the Rosetta trainer (#371)
    # or by hand when building a class script.
    transcript_cue: Optional[str] = None

    @property
    def key(self) -> Tuple[str, str]:
        return (self.origin, self.target)

    def render_cue(self, side: str = "", breath: str = "") -> str:
        """Fill the cue_template with runtime values."""
        return self.cue_template.format(
            origin=self.origin,
            target=self.target,
            side=side,
            breath=breath or self.breath_op.value,
        )

    def __repr__(self) -> str:
        return (f"TransitionVector({self.origin!r} --[{self.pathway.value}]--> "
                f"{self.target!r}, pacing={self.pacing.value})")


# ---------------------------------------------------------------------------
# Transition lookup
# ---------------------------------------------------------------------------


TransitionKey = Tuple[str, str]
TransitionDB = Dict[TransitionKey, List[TransitionVector]]


def _t(origin: str, pathway: Pathway, target: str,
        breath: BreathOp, pacing: Pacing = Pacing.MEDIUM,
        cue: str = "") -> TransitionVector:
    return TransitionVector(
        origin=origin, pathway=pathway, target=target,
        breath_op=breath, pacing=pacing, cue_template=cue,
    )


# ---------------------------------------------------------------------------
# Core transition database
# Generic vinyasa vocabulary only — no proprietary sequence content.
# ---------------------------------------------------------------------------

TRANSITION_DB: TransitionDB = {}


def _add(*vectors: TransitionVector) -> None:
    for v in vectors:
        TRANSITION_DB.setdefault(v.key, []).append(v)


# ── Downward Dog exits ────────────────────────────────────────────────────

_add(
    _t("DD", Pathway.STEP_FORWARD, "FF",
       BreathOp.EXHALE, Pacing.MEDIUM,
       "Walk or hop your feet to your {target}, {breath} all the air out."),
    _t("DD", Pathway.STEP_FORWARD, "HL",
       BreathOp.INHALE, Pacing.MEDIUM,
       "Step your {side} foot forward between your hands, {breath} rise into {target}."),
    _t("DD", Pathway.STEP_FORWARD, "CL",
       BreathOp.INHALE, Pacing.MEDIUM,
       "Step your {side} foot forward, {breath} sweep your arms overhead into {target}."),
    _t("DD", Pathway.STEP_FORWARD, "LL",
       BreathOp.EXHALE, Pacing.SLOW,
       "Lower your {side} knee down, {breath} find {target} with your back knee soft."),
    _t("DD", Pathway.LOWER, "CH",
       BreathOp.EXHALE, Pacing.FAST,
       "{breath} bend your elbows halfway — {target} — elbows track back."),
    _t("DD", Pathway.JUMP, "FF",
       BreathOp.EXHALE, Pacing.FAST,
       "Bend your knees, {breath} hop to the top of your mat."),
    _t("DD", Pathway.HOLD, "DD",
       BreathOp.HOLD, Pacing.SLOW,
       "Hold your {origin}, breathe into the backs of your legs."),
)

# ── Forward Fold transitions ───────────────────────────────────────────────

_add(
    _t("FF", Pathway.SWEEP_UP, "HL",
       BreathOp.INHALE, Pacing.MEDIUM,
       "{breath} sweep your arms wide and up, step your {side} foot back into {target}."),
    _t("FF", Pathway.LOWER, "PL",
       BreathOp.EXHALE, Pacing.MEDIUM,
       "Plant your palms, {breath} step or float back to {target}."),
    _t("FF", Pathway.ROLL, "SC",
       BreathOp.INHALE, Pacing.SLOW,
       "Slowly roll up your spine, one vertebra at a time."),
)

# ── Plank transitions ─────────────────────────────────────────────────────

_add(
    _t("PL", Pathway.LOWER, "CH",
       BreathOp.EXHALE, Pacing.FAST,
       "{breath} lower halfway — strong {target} — body as one plank."),
    _t("PL", Pathway.PRESS, "UD",
       BreathOp.INHALE, Pacing.FAST,
       "{breath} press through your hands, open your chest into {target}."),
    _t("PL", Pathway.FOLD_DOWN, "CB",
       BreathOp.EXHALE, Pacing.SLOW,
       "Lower all the way to your belly, {breath} find rest in {target}."),
)

# ── Chaturanga transitions ────────────────────────────────────────────────

_add(
    _t("CH", Pathway.PRESS, "UD",
       BreathOp.INHALE, Pacing.FAST,
       "{breath} roll over the toes, open chest into {target}, thighs off the mat."),
)

# ── Upward Dog transitions ────────────────────────────────────────────────

_add(
    _t("UD", Pathway.FOLD_DOWN, "DD",
       BreathOp.EXHALE, Pacing.FAST,
       "{breath} tuck the toes, press the hips high — {target}."),
)

# ── High Lunge transitions ────────────────────────────────────────────────

_add(
    _t("HL", Pathway.LOWER, "LL",
       BreathOp.EXHALE, Pacing.SLOW,
       "{breath} lower your back knee down into {target}."),
    _t("HL", Pathway.OPEN, "WR2",
       BreathOp.EXHALE, Pacing.MEDIUM,
       "Open your back foot flat, {breath} lower your arms into {target}."),
    _t("HL", Pathway.STEP_BACK, "DD",
       BreathOp.EXHALE, Pacing.MEDIUM,
       "Plant your palms, {breath} step your front foot back — {target}."),
    _t("HL", Pathway.PIVOT, "WR1",
       BreathOp.INHALE, Pacing.MEDIUM,
       "{breath} anchor your back heel, spin your arms up — {target}."),
)

# ── Crescent Lunge — multiple entry pathways (Acceptance criterion #370) ──

_add(
    # Pathway 1: From Downward Dog (most common)
    _t("DD", Pathway.STEP_FORWARD, "CL",
       BreathOp.INHALE, Pacing.MEDIUM,
       "Step your {side} foot forward, {breath} sweep both arms up — {target}."),
    # Pathway 2: From Low Lunge (building intensity)
    _t("LL", Pathway.SWEEP_UP, "CL",
       BreathOp.INHALE, Pacing.MEDIUM,
       "{breath} tuck your back toes, lift your knee, sweep arms high — {target}."),
    # Pathway 3: From Warrior I (arms already up, narrow stance)
    _t("WR1", Pathway.CLOSE, "CL",
       BreathOp.INHALE, Pacing.SLOW,
       "Soften the back heel, {breath} draw the stance narrow — {target}."),
    # Pathway 4: From Warrior III (balance to lunge landing)
    _t("WR3", Pathway.STEP_BACK, "CL",
       BreathOp.EXHALE, Pacing.FAST,
       "Land your {side} foot back, {breath} soften into {target} — control the landing."),
)

# ── Warrior II transitions ─────────────────────────────────────────────────

_add(
    _t("WR2", Pathway.REACH, "EK",
       BreathOp.EXHALE, Pacing.MEDIUM,
       "Tip your torso forward, {breath} extend your front arm long — {target}."),
    _t("WR2", Pathway.PIVOT, "TR",
       BreathOp.INHALE, Pacing.MEDIUM,
       "Straighten your front leg, {breath} reach long into {target}."),
    _t("WR2", Pathway.FOLD_DOWN, "PL",
       BreathOp.EXHALE, Pacing.FAST,
       "Cartwheel your hands down to frame your foot, {breath} step back to {target}."),
)

# ── Low Lunge transitions ──────────────────────────────────────────────────

_add(
    _t("LL", Pathway.STEP_BACK, "DD",
       BreathOp.EXHALE, Pacing.MEDIUM,
       "Tuck the back toes, {breath} step or hop back to {target}."),
    _t("LL", Pathway.PIVOT, "RLH",
       BreathOp.INHALE, Pacing.SLOW,
       "{breath} open your front arm toward the sky, twisting into {target}."),
)

# ── Pigeon transitions ─────────────────────────────────────────────────────

_add(
    _t("DD", Pathway.SLIDE, "PT",
       BreathOp.EXHALE, Pacing.SLOW,
       "Draw your {side} knee toward your {side} wrist, {breath} lower into {target}."),
    _t("PT", Pathway.PRESS, "DD",
       BreathOp.INHALE, Pacing.MEDIUM,
       "Tuck the back toes, press up, step back into {target}."),
    _t("LL", Pathway.SLIDE, "PT",
       BreathOp.EXHALE, Pacing.SLOW,
       "Slide your front shin toward the top of the mat — {target}."),
)

# ── Camel transitions ─────────────────────────────────────────────────────

_add(
    _t("CB", Pathway.SWEEP_UP, "CM",
       BreathOp.INHALE, Pacing.SLOW,
       "Come to high kneeling, tuck your toes or flatten your feet, {breath} into {target}."),
    _t("CM", Pathway.FOLD_DOWN, "CB",
       BreathOp.EXHALE, Pacing.SLOW,
       "{breath} release and find {target} — let the head follow last."),
)

# ── Savasana entry ────────────────────────────────────────────────────────

_add(
    _t("SF", Pathway.ROLL, "SV",
       BreathOp.EXHALE, Pacing.SLOW,
       "Let your body settle, {breath}, and lie all the way down into {target}."),
    _t("KN", Pathway.SLIDE, "SV",
       BreathOp.EXHALE, Pacing.SLOW,
       "Let your legs extend long, arms fall open — {target}."),
    _t("ST", Pathway.ROLL, "SV",
       BreathOp.EXHALE, Pacing.SLOW,
       "Unwind from your twist, extend out — {target}."),
)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def get_transitions(origin: str, target: str) -> List[TransitionVector]:
    """
    Return all known transition vectors from *origin* to *target*.

    Returns an empty list if the pair is not in the database (callers
    should treat this as an unscripted transition, not an error).
    """
    return TRANSITION_DB.get((origin, target), [])


def get_exits(origin: str) -> List[TransitionVector]:
    """Return all transitions that depart from *origin*."""
    return [v for (o, _), vs in TRANSITION_DB.items()
            if o == origin for v in vs]


def get_entries(target: str) -> List[TransitionVector]:
    """Return all transitions that arrive at *target*."""
    return [v for (_, t), vs in TRANSITION_DB.items()
            if t == target for v in vs]


def suggest_transition(
    origin: str,
    target: str,
    preferred_pacing: Optional[Pacing] = None,
) -> Optional[TransitionVector]:
    """
    Return the best single transition for a given pose pair.

    Prefers *preferred_pacing* if specified; otherwise returns the first
    entry (insertion order = most common pathway first).
    """
    candidates = get_transitions(origin, target)
    if not candidates:
        return None
    if preferred_pacing:
        paced = [c for c in candidates if c.pacing == preferred_pacing]
        return paced[0] if paced else candidates[0]
    return candidates[0]


def annotate_sequence_transitions(
    sequence_tokens: List[Tuple[str, Optional[str]]],
) -> List[Tuple[Tuple[str, Optional[str]], Optional[TransitionVector]]]:
    """
    Annotate a flat list of (token, side) tuples with their transitions.

    Returns a list of ((token, side), TransitionVector | None) pairs.
    The first element has no incoming transition (None).

    Args:
        sequence_tokens: Ordered list of (pose_token, side_or_None) tuples.

    Returns:
        List of ((token, side), incoming_transition_or_None).
    """
    result = []
    for idx, item in enumerate(sequence_tokens):
        if idx == 0:
            result.append((item, None))
        else:
            prev_token = sequence_tokens[idx - 1][0]
            curr_token = item[0]
            tv = suggest_transition(prev_token, curr_token)
            result.append((item, tv))
    return result
