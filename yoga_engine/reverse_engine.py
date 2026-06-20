"""
reverse_engine.py — Reverse Sequence Engine structural scaffolding (Story #373).

Accepts ~5 lines of shorthand and expands them into a class-script skeleton:

    shorthand  →  [parse]  →  Sequence
               →  [annotate transitions]  →  Annotated sequence
               →  [expand script]  →  ScriptOutput

Design decisions
----------------
- This module provides the STRUCTURAL pipeline and placeholder cue system.
  Voice/style generation (Tony's voice) requires the Rosetta-Stone parallel-dataset
  trainer (#371) which feeds into the ``voice_style`` slot — that slot is None here
  until the trainer populates it.
- The quality gate is explicit: ScriptOutput has an ``is_reviewed`` flag and
  a ``human_review_notes`` field.  The engine marks every output as NOT reviewed;
  a human (Tony) must call ``approve()`` before the output is considered final.
- Thematic-infusion points are modeled as ThemeInfusion dataclasses placed at
  arc positions; content is template-driven (generic; not proprietary).
- Pacing uses the Transition Matrix crossfade data and EngineConfig LUFS target
  to build a PlaylistHandoff struct compatible with the playlist-builder skill.

Public API
----------
    engine = ReverseSequenceEngine()
    result = engine.expand(shorthand_text)
    print(result.render_markdown())   # human-reviewable draft
    result.approve("Looks good!")     # gates the output
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .config import get_config, get_thesaurus
from .parser import parse_shorthand
from .schema import BreathOp, Phase, PhaseBlock, PoseInstance, Sequence
from .transitions import (
    Pacing, TransitionVector, annotate_sequence_transitions, suggest_transition,
)
from .validator import validate_sequence


# ---------------------------------------------------------------------------
# Thematic infusion point
# ---------------------------------------------------------------------------


@dataclass
class ThemeInfusion:
    """
    A thematic cue injected at a specific point in the class arc.

    Content is a generic template placeholder — the Rosetta trainer (#371)
    or Tony's own text fills in the voice-accurate language.
    """
    phase: Phase
    position_in_phase: float       # 0.0–1.0 (relative position within the phase)
    template_key: str              # e.g. "arrival_intention", "peak_encouragement"
    placeholder_text: str          # generic structural placeholder


_THEME_INFUSION_TEMPLATES = {
    Phase.ARRIVAL: [
        ThemeInfusion(
            phase=Phase.ARRIVAL,
            position_in_phase=0.5,
            template_key="arrival_intention",
            placeholder_text="[Set the class intention here — generic or thematic.]",
        ),
    ],
    Phase.WARMUP: [
        ThemeInfusion(
            phase=Phase.WARMUP,
            position_in_phase=0.3,
            template_key="warmup_body_scan",
            placeholder_text="[Invite students to notice what they're bringing to the mat today.]",
        ),
    ],
    Phase.BUILD: [
        ThemeInfusion(
            phase=Phase.BUILD,
            position_in_phase=0.5,
            template_key="build_midpoint_anchor",
            placeholder_text="[Mid-build anchor: connect the movement to the class theme.]",
        ),
    ],
    Phase.PEAK: [
        ThemeInfusion(
            phase=Phase.PEAK,
            position_in_phase=0.0,
            template_key="peak_preparation",
            placeholder_text="[Frame the peak pose — physical setup, breath, invitation.]",
        ),
        ThemeInfusion(
            phase=Phase.PEAK,
            position_in_phase=1.0,
            template_key="peak_integration",
            placeholder_text="[After the peak: acknowledge effort, invite observation.]",
        ),
    ],
    Phase.COOLDOWN: [
        ThemeInfusion(
            phase=Phase.COOLDOWN,
            position_in_phase=0.3,
            template_key="cooldown_release",
            placeholder_text="[Invite the body to release effort and absorb the practice.]",
        ),
    ],
    Phase.SAVASANA: [
        ThemeInfusion(
            phase=Phase.SAVASANA,
            position_in_phase=0.0,
            template_key="savasana_entry",
            placeholder_text="[Guide savasana entry — let the practice land.]",
        ),
    ],
}


# ---------------------------------------------------------------------------
# Script line
# ---------------------------------------------------------------------------


@dataclass
class ScriptLine:
    """
    A single rendered line of the class script.

    Fields:
        kind:     "pose" | "transition" | "theme" | "cue" | "breath"
        text:     The human-facing teacher text (template or Rosetta-trained).
        pose_token:  The current pose token (if kind="pose" or "transition").
        transition:  The incoming TransitionVector (if kind="transition").
        is_placeholder:  True if the text is a structural placeholder, not final voice.
    """
    kind: str
    text: str
    pose_token: Optional[str] = None
    transition: Optional[TransitionVector] = None
    is_placeholder: bool = True


# ---------------------------------------------------------------------------
# Playlist handoff
# ---------------------------------------------------------------------------


@dataclass
class PlaylistPhase:
    """One phase's worth of playlist-builder handoff data."""
    phase: Phase
    label: str
    duration_minutes: float
    energy: str               # "low" | "medium" | "high" | "peak"
    cue_density: str          # "sparse" | "moderate" | "rhythmic" | "focused" | "minimal"
    lufs_target: float
    avg_crossfade_bars: float


@dataclass
class PlaylistHandoff:
    """
    Playlist-builder handoff payload.
    Compatible with the existing playlist-builder-handoff.md schema
    in yoga-sequencer/references/.
    """
    title: str
    duration_minutes: int
    phases: List[PlaylistPhase]


# ---------------------------------------------------------------------------
# ScriptOutput
# ---------------------------------------------------------------------------


@dataclass
class ScriptOutput:
    """
    A fully expanded class script, pending human review.

    IMPORTANT: The quality gate is explicit.
    ``is_reviewed`` starts as False.  Call :meth:`approve` before treating
    the output as final — generation is reviewed, not autopilot.
    """
    sequence: Sequence
    lines: List[ScriptLine]
    theme_infusions: List[ThemeInfusion]
    playlist_handoff: PlaylistHandoff
    validation_summary: str

    is_reviewed: bool = False
    human_review_notes: str = ""

    def approve(self, notes: str = "") -> None:
        """Mark this output as human-reviewed."""
        self.is_reviewed = True
        self.human_review_notes = notes

    def render_markdown(self) -> str:
        """Render the script as a human-reviewable Markdown document."""
        lines: List[str] = [
            f"# {self.sequence.title}",
            f"**Duration:** {self.sequence.duration_minutes} min  "
            f"| **Level:** {self.sequence.level}  "
            f"| **Reviewed:** {'✅' if self.is_reviewed else '⚠️ NOT YET REVIEWED'}",
            "",
        ]
        if self.human_review_notes:
            lines.append(f"> **Review notes:** {self.human_review_notes}\n")

        lines.append("---\n")
        lines.append(f"**Validation:** {self.validation_summary}\n")
        lines.append("---\n")

        current_phase = None
        for sl in self.lines:
            if sl.kind == "theme":
                lines.append(f"\n> *{sl.text}*\n")
                continue
            if sl.pose_token:
                from .pose_db import POSE_DB
                pose = POSE_DB.get(sl.pose_token)
                phase_label = pose.phase_roles[0].value if pose and pose.phase_roles else "?"
                if phase_label != current_phase:
                    lines.append(f"\n## {phase_label.upper()}\n")
                    current_phase = phase_label
            if sl.is_placeholder:
                lines.append(f"_{sl.text}_")
            else:
                lines.append(sl.text)

        lines.append("\n---")
        lines.append("\n### Playlist Handoff\n")
        for ph in self.playlist_handoff.phases:
            lines.append(
                f"- **{ph.label}** — {ph.duration_minutes:.1f} min, "
                f"energy: {ph.energy}, cue_density: {ph.cue_density}, "
                f"LUFS: {ph.lufs_target}, crossfade: {ph.avg_crossfade_bars:.1f} bars"
            )

        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"ScriptOutput(title={self.sequence.title!r}, "
            f"lines={len(self.lines)}, reviewed={self.is_reviewed})"
        )


# ---------------------------------------------------------------------------
# Reverse Sequence Engine
# ---------------------------------------------------------------------------


class ReverseSequenceEngine:
    """
    Expands a shorthand string into a :class:`ScriptOutput`.

    Usage::

        engine = ReverseSequenceEngine()
        result = engine.expand(shorthand_text)
        print(result.render_markdown())
        result.approve("Reviewed and approved.")

    The engine chains:
    1. ``parse_shorthand``       — text → Sequence
    2. ``validate_sequence``     — safety check; warnings included in output
    3. ``annotate_sequence_transitions`` — attach TransitionVectors
    4. ``_build_script_lines``   — pose + transition + theme cues → ScriptLine list
    5. ``_build_playlist_handoff`` — per-phase playlist metadata
    6. Wrap in :class:`ScriptOutput` with ``is_reviewed=False``
    """

    def __init__(self, voice_style: Optional[object] = None) -> None:
        """
        Args:
            voice_style: Reserved for the Rosetta-Stone trained voice model (#371).
                         When None (default), all cue text is generic placeholder.
        """
        self._voice_style = voice_style
        self._cfg = get_config()
        self._thesaurus = get_thesaurus()

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def expand(self, shorthand: str) -> ScriptOutput:
        """
        Expand *shorthand* into a :class:`ScriptOutput`.

        Args:
            shorthand: Multi-line shorthand string (see NOTATION.md).

        Returns:
            :class:`ScriptOutput` with ``is_reviewed=False``.
        """
        # 1. Parse
        seq = parse_shorthand(shorthand)

        # 2. Validate
        report = validate_sequence(seq)
        val_summary = (
            f"{'✅ Safe' if report.is_safe else '❌ Errors'} — "
            f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)"
        )

        # 3. Annotate transitions
        token_side_pairs = [(i.pose.token, i.side) for i in seq.all_poses]
        annotated = annotate_sequence_transitions(token_side_pairs)

        # 4. Build script lines
        script_lines = self._build_script_lines(seq, annotated)

        # 5. Playlist handoff
        handoff = self._build_playlist_handoff(seq)

        # 6. Collect theme infusions
        infusions = self._collect_theme_infusions(seq)

        return ScriptOutput(
            sequence=seq,
            lines=script_lines,
            theme_infusions=infusions,
            playlist_handoff=handoff,
            validation_summary=val_summary,
            is_reviewed=False,
        )

    # ------------------------------------------------------------------ #
    # Script line builder                                                  #
    # ------------------------------------------------------------------ #

    def _build_script_lines(
        self,
        seq: Sequence,
        annotated: List[Tuple],
    ) -> List[ScriptLine]:
        """Build the ordered list of ScriptLines for the class."""
        lines: List[ScriptLine] = []
        phase_infusions = {
            ph: list(infusions)
            for ph, infusions in _THEME_INFUSION_TEMPLATES.items()
        }
        phase_infusion_inserted: set = set()

        flat = seq.all_poses
        ann_idx = 0

        for block in seq.phases:
            # Opening theme infusion for this phase
            phase_inf_list = phase_infusions.get(block.phase, [])
            for inf in phase_inf_list:
                if inf.position_in_phase == 0.0 and block.phase not in phase_infusion_inserted:
                    lines.append(ScriptLine(
                        kind="theme",
                        text=inf.placeholder_text,
                        is_placeholder=True,
                    ))
                    phase_infusion_inserted.add(block.phase)

            n_block = len(block.poses)
            for pose_idx, inst in enumerate(block.poses):
                (token, side), transition = annotated[ann_idx]
                ann_idx += 1

                # Transition cue (skip for first pose overall)
                if transition is not None:
                    trans_cue = self._render_transition_cue(transition, side)
                    lines.append(ScriptLine(
                        kind="transition",
                        text=trans_cue,
                        pose_token=token,
                        transition=transition,
                        is_placeholder=self._voice_style is None,
                    ))

                # Pose cue
                pose_cue = self._render_pose_cue(inst, block)
                lines.append(ScriptLine(
                    kind="pose",
                    text=pose_cue,
                    pose_token=token,
                    is_placeholder=self._voice_style is None,
                ))

                # Mid-phase theme infusion
                if n_block > 1:
                    rel_pos = (pose_idx + 1) / n_block
                    for inf in phase_inf_list:
                        if (0.0 < inf.position_in_phase <= rel_pos
                                and f"{block.phase}_{inf.template_key}" not in phase_infusion_inserted):
                            lines.append(ScriptLine(
                                kind="theme",
                                text=inf.placeholder_text,
                                is_placeholder=True,
                            ))
                            phase_infusion_inserted.add(f"{block.phase}_{inf.template_key}")

        return lines

    def _render_transition_cue(
        self,
        tv: TransitionVector,
        side: Optional[str],
    ) -> str:
        """Render a transition cue line from a TransitionVector."""
        if self._voice_style is not None:
            # Rosetta-trained path (placeholder for #371)
            return self._voice_style.render_transition(tv, side)  # type: ignore[attr-defined]
        # Generic structural template
        rendered = tv.render_cue(side=side or "", breath=tv.breath_op.value)
        if not rendered.strip():
            return (
                f"[Transition: {tv.origin} → {tv.target} "
                f"via {tv.pathway.value}, {tv.breath_op.value}]"
            )
        return rendered

    def _render_pose_cue(self, inst: PoseInstance, block: PhaseBlock) -> str:
        """Render a pose hold/instruction cue."""
        if self._voice_style is not None:
            return self._voice_style.render_pose(inst, block)  # type: ignore[attr-defined]
        bc = inst.breath_count
        bc_str = f" for {bc} breaths" if bc else ""
        side_str = f" ({inst.side} side)" if inst.side else ""
        return (
            f"[{inst.pose.name}{side_str}{bc_str} — "
            f"intensity {inst.pose.intensity}/10]"
        )

    # ------------------------------------------------------------------ #
    # Theme infusions                                                      #
    # ------------------------------------------------------------------ #

    def _collect_theme_infusions(self, seq: Sequence) -> List[ThemeInfusion]:
        """Return all theme infusions relevant to this sequence's phases."""
        result: List[ThemeInfusion] = []
        seen_phases = {b.phase for b in seq.phases}
        for phase, infusions in _THEME_INFUSION_TEMPLATES.items():
            if phase in seen_phases:
                result.extend(infusions)
        return result

    # ------------------------------------------------------------------ #
    # Playlist handoff builder                                             #
    # ------------------------------------------------------------------ #

    def _build_playlist_handoff(self, seq: Sequence) -> PlaylistHandoff:
        """Build a playlist-builder-compatible handoff from the sequence."""
        cfg = self._cfg
        lufs = cfg.audio_sync.lufs_target

        # Approximate duration split by phase (generic vinyasa defaults)
        _PHASE_DURATION_PCTS = {
            Phase.ARRIVAL:  0.07,
            Phase.WARMUP:   0.17,
            Phase.BUILD:    0.37,
            Phase.PEAK:     0.15,
            Phase.COOLDOWN: 0.17,
            Phase.SAVASANA: 0.07,
        }
        _PHASE_ENERGY = {
            Phase.ARRIVAL:  "low",
            Phase.WARMUP:   "low",
            Phase.BUILD:    "medium",
            Phase.PEAK:     "high",
            Phase.COOLDOWN: "medium",
            Phase.SAVASANA: "low",
        }
        _PHASE_CUE_DENSITY = {
            Phase.ARRIVAL:  "sparse",
            Phase.WARMUP:   "moderate",
            Phase.BUILD:    "rhythmic",
            Phase.PEAK:     "focused",
            Phase.COOLDOWN: "moderate",
            Phase.SAVASANA: "minimal",
        }
        _LUFS_OFFSET = {
            Phase.ARRIVAL: -4.0, Phase.WARMUP: -2.0, Phase.BUILD: 0.0,
            Phase.PEAK: +2.0, Phase.COOLDOWN: -1.0, Phase.SAVASANA: -5.0,
        }

        pl_phases: List[PlaylistPhase] = []
        total = seq.duration_minutes

        for block in seq.phases:
            pct = _PHASE_DURATION_PCTS.get(block.phase, 0.1)
            dur = round(total * pct, 1)

            # Compute avg crossfade bars for the block's transitions
            cf_bars: List[float] = []
            for i in range(1, len(block.poses)):
                prev_tok = block.poses[i - 1].pose.token
                curr_tok = block.poses[i].pose.token
                tv = suggest_transition(prev_tok, curr_tok)
                if tv:
                    base = tv.pacing.crossfade_bars
                    mult = {
                        Pacing.SLOW:   cfg.audio_sync.crossfade_slow_multiplier,
                        Pacing.MEDIUM: cfg.audio_sync.crossfade_medium_multiplier,
                        Pacing.FAST:   cfg.audio_sync.crossfade_fast_multiplier,
                    }.get(tv.pacing, 1.0)
                    cf_bars.append(base * mult)
            avg_cf = sum(cf_bars) / len(cf_bars) if cf_bars else 1.0

            pl_phases.append(PlaylistPhase(
                phase=block.phase,
                label=block.label,
                duration_minutes=dur,
                energy=_PHASE_ENERGY.get(block.phase, "medium"),
                cue_density=_PHASE_CUE_DENSITY.get(block.phase, "moderate"),
                lufs_target=round(lufs + _LUFS_OFFSET.get(block.phase, 0.0), 1),
                avg_crossfade_bars=round(avg_cf, 2),
            ))

        return PlaylistHandoff(
            title=seq.title,
            duration_minutes=seq.duration_minutes,
            phases=pl_phases,
        )
