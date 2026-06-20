"""
pose_db.py — built-in pose vocabulary and macro definitions.

All knowledge here is generic public vinyasa anatomy — not proprietary.

Token design goals:
  - 2–4 chars, uppercase
  - Mnemonic: DD = Downward Dog, HL = High Lunge, etc.
  - Tokens used in the shorthand grammar defined in NOTATION.md

MACROS expand into raw shorthand fragments (pre-parse).
"""

from __future__ import annotations
from typing import Dict

from .schema import Pose, PoseFamily, Phase


# ---------------------------------------------------------------------------
# Pose database
# ---------------------------------------------------------------------------

def _p(**kw) -> Pose:
    return Pose(**kw)


POSE_DB: Dict[str, Pose] = {p.token: p for p in [

    # ── Arrival / centering ──────────────────────────────────────────────
    _p(token="SC",  name="Seated Centering",  family=PoseFamily.CENTERING, intensity=1,
       phase_roles=[Phase.ARRIVAL, Phase.WARMUP],
       is_counter=True,
       contraindications=[]),

    _p(token="SB",  name="Seated Forward Bend", family=PoseFamily.FORWARD_FOLD, intensity=2,
       phase_roles=[Phase.ARRIVAL, Phase.COOLDOWN],
       is_counter=True, is_prep=True,
       contraindications=["herniated_disc"]),

    _p(token="BW",  name="Breath Work / Pranayama", family=PoseFamily.CENTERING, intensity=1,
       phase_roles=[Phase.ARRIVAL],
       contraindications=[]),

    # ── Warm-up ──────────────────────────────────────────────────────────
    _p(token="CB",  name="Child's Pose",  family=PoseFamily.RESET, intensity=1,
       phase_roles=[Phase.WARMUP, Phase.COOLDOWN],
       is_counter=True,
       contraindications=["sensitive_knees", "pregnancy_compressed"]),

    _p(token="CC",  name="Cat-Cow",  family=PoseFamily.SPINAL_MOBILITY, intensity=2,
       phase_roles=[Phase.WARMUP],
       is_prep=True,
       contraindications=["wrist_sensitivity"]),

    _p(token="TB",  name="Tabletop",  family=PoseFamily.WARMUP, intensity=1,
       phase_roles=[Phase.WARMUP],
       is_prep=True,
       contraindications=["wrist_sensitivity"]),

    _p(token="TNT", name="Thread the Needle", family=PoseFamily.TWIST, intensity=2,
       phase_roles=[Phase.WARMUP],
       is_twist=True, is_prep=True, is_counter=True,
       contraindications=["shoulder_pressure"]),

    # ── Transitions ──────────────────────────────────────────────────────
    _p(token="PL",  name="Plank",  family=PoseFamily.TRANSITION, intensity=5,
       phase_roles=[Phase.BUILD, Phase.BUILD],
       requires_warmup=True,
       contraindications=["wrist_sensitivity", "shoulder_injury"]),

    _p(token="CH",  name="Chaturanga",  family=PoseFamily.TRANSITION, intensity=6,
       phase_roles=[Phase.BUILD, Phase.BUILD],
       requires_warmup=True,
       heated_caution=True,
       contraindications=["wrist_sensitivity", "shoulder_injury", "pregnancy"]),

    _p(token="UD",  name="Upward Dog",  family=PoseFamily.BACKBEND, intensity=5,
       phase_roles=[Phase.BUILD, Phase.BUILD],
       is_backbend=True, requires_warmup=True,
       needs_counter=True,
       contraindications=["lower_back_injury"]),

    _p(token="DD",  name="Downward Dog",  family=PoseFamily.TRANSITION, intensity=3,
       phase_roles=[Phase.WARMUP, Phase.BUILD, Phase.COOLDOWN],
       is_counter=True, is_prep=True,
       heated_caution=True,
       contraindications=["wrist_sensitivity", "shoulder_injury",
                          "high_blood_pressure_uninverted"]),

    # ── Standing poses ────────────────────────────────────────────────────
    _p(token="FF",  name="Forward Fold",  family=PoseFamily.FORWARD_FOLD, intensity=3,
       phase_roles=[Phase.WARMUP, Phase.BUILD, Phase.COOLDOWN],
       is_counter=True, is_prep=True,
       heated_caution=True,
       contraindications=["herniated_disc"]),

    _p(token="HL",  name="High Lunge",  family=PoseFamily.STANDING, intensity=5,
       phase_roles=[Phase.BUILD],
       requires_warmup=True, is_prep=True,
       contraindications=[]),

    _p(token="CL",  name="Crescent Lunge",  family=PoseFamily.STANDING, intensity=5,
       phase_roles=[Phase.BUILD],
       requires_warmup=True, is_prep=True,
       contraindications=[]),

    _p(token="LL",  name="Low Lunge",  family=PoseFamily.HIP_OPENER, intensity=4,
       phase_roles=[Phase.WARMUP, Phase.BUILD],
       is_prep=True,
       contraindications=["sensitive_knees"]),

    _p(token="WR1", name="Warrior I",  family=PoseFamily.STANDING, intensity=6,
       phase_roles=[Phase.BUILD],
       requires_warmup=True, is_prep=True,
       contraindications=["knee_injury"]),

    _p(token="WR2", name="Warrior II",  family=PoseFamily.STANDING, intensity=6,
       phase_roles=[Phase.BUILD],
       requires_warmup=True, is_prep=True,
       contraindications=["knee_injury"]),

    _p(token="WR3", name="Warrior III",  family=PoseFamily.BALANCE, intensity=7,
       phase_roles=[Phase.BUILD, Phase.PEAK],
       requires_warmup=True, is_peak=True, is_prep=True,
       contraindications=["balance_issues_severe"]),

    _p(token="TR",  name="Triangle",  family=PoseFamily.STANDING, intensity=5,
       phase_roles=[Phase.BUILD],
       requires_warmup=True, is_prep=True,
       contraindications=["herniated_disc_lateral"]),

    _p(token="EK",  name="Extended Side Angle",  family=PoseFamily.STANDING, intensity=5,
       phase_roles=[Phase.BUILD],
       requires_warmup=True,
       contraindications=[]),

    _p(token="RH",  name="Revolved High Lunge",  family=PoseFamily.TWIST, intensity=6,
       phase_roles=[Phase.BUILD],
       requires_warmup=True, is_twist=True, is_prep=True, needs_counter=True,
       contraindications=["lower_back_injury"]),

    _p(token="RLH", name="Revolved Low Lunge",  family=PoseFamily.TWIST, intensity=5,
       phase_roles=[Phase.BUILD],
       requires_warmup=True, is_twist=True, needs_counter=True,
       contraindications=["lower_back_injury"]),

    _p(token="HP",  name="Half Moon",  family=PoseFamily.BALANCE, intensity=7,
       phase_roles=[Phase.BUILD, Phase.PEAK],
       requires_warmup=True, is_peak=True,
       contraindications=["balance_issues_severe"]),

    _p(token="BD",  name="Bridge",  family=PoseFamily.BACKBEND, intensity=5,
       phase_roles=[Phase.BUILD, Phase.COOLDOWN],
       requires_warmup=True, is_backbend=True, needs_counter=True,
       is_prep=True,
       contraindications=["neck_injury"]),

    # ── Hip openers ───────────────────────────────────────────────────────
    _p(token="PT",  name="Pigeon",  family=PoseFamily.HIP_OPENER, intensity=6,
       phase_roles=[Phase.COOLDOWN],
       requires_warmup=True,
       needs_counter=True,
       heated_caution=False,
       contraindications=["knee_injury", "hip_replacement"]),

    _p(token="LZ",  name="Lizard",  family=PoseFamily.HIP_OPENER, intensity=6,
       phase_roles=[Phase.BUILD, Phase.COOLDOWN],
       requires_warmup=True,
       contraindications=["knee_injury", "hip_replacement"]),

    _p(token="BT",  name="Bound Angle / Butterfly",  family=PoseFamily.HIP_OPENER, intensity=2,
       phase_roles=[Phase.COOLDOWN],
       is_counter=True,
       contraindications=["knee_sensitivity"]),

    # ── Backbends ─────────────────────────────────────────────────────────
    _p(token="CB2", name="Cobra",  family=PoseFamily.BACKBEND, intensity=4,
       phase_roles=[Phase.WARMUP, Phase.BUILD],
       is_backbend=True, is_prep=True, needs_counter=True,
       contraindications=["lower_back_injury"]),

    _p(token="CM",  name="Camel",  family=PoseFamily.BACKBEND, intensity=8,
       phase_roles=[Phase.PEAK],
       requires_warmup=True, is_backbend=True, is_peak=True, needs_counter=True,
       heated_caution=True,
       contraindications=["lower_back_injury", "neck_injury", "high_blood_pressure"]),

    _p(token="UB",  name="Upward Bow / Wheel",  family=PoseFamily.BACKBEND, intensity=9,
       phase_roles=[Phase.PEAK],
       requires_warmup=True, is_backbend=True, is_peak=True, needs_counter=True,
       heated_caution=True,
       contraindications=["wrist_sensitivity", "lower_back_injury", "shoulder_injury"]),

    _p(token="LB",  name="Locust",  family=PoseFamily.BACKBEND, intensity=5,
       phase_roles=[Phase.BUILD],
       is_backbend=True, needs_counter=True, is_prep=True,
       contraindications=["pregnancy"]),

    # ── Arm balances ──────────────────────────────────────────────────────
    _p(token="CW",  name="Crow",  family=PoseFamily.ARM_BALANCE, intensity=8,
       phase_roles=[Phase.PEAK],
       requires_warmup=True, is_arm_balance=True, is_peak=True,
       heated_caution=True,
       contraindications=["wrist_sensitivity", "pregnancy"]),

    _p(token="SK",  name="Side Crow",  family=PoseFamily.ARM_BALANCE, intensity=9,
       phase_roles=[Phase.PEAK],
       requires_warmup=True, is_arm_balance=True, is_peak=True,
       needs_counter=True,
       contraindications=["wrist_sensitivity"]),

    # ── Inversions ────────────────────────────────────────────────────────
    _p(token="SH",  name="Shoulder Stand",  family=PoseFamily.INVERSION, intensity=7,
       phase_roles=[Phase.PEAK, Phase.COOLDOWN],
       requires_warmup=True, is_inversion=True, needs_counter=True,
       heated_caution=True,
       contraindications=["neck_injury", "high_blood_pressure", "pregnancy",
                          "glaucoma", "detached_retina"]),

    _p(token="HH",  name="Headstand",  family=PoseFamily.INVERSION, intensity=8,
       phase_roles=[Phase.PEAK],
       requires_warmup=True, is_inversion=True, is_peak=True, needs_counter=True,
       heated_caution=True,
       contraindications=["neck_injury", "high_blood_pressure", "pregnancy",
                          "glaucoma", "detached_retina"]),

    # ── Seated / floor ────────────────────────────────────────────────────
    _p(token="ST",  name="Seated Twist",  family=PoseFamily.TWIST, intensity=3,
       phase_roles=[Phase.COOLDOWN],
       is_twist=True, is_counter=True, needs_counter=True,
       contraindications=["herniated_disc_rotation"]),

    _p(token="SF",  name="Seated Forward Fold", family=PoseFamily.FORWARD_FOLD, intensity=3,
       phase_roles=[Phase.COOLDOWN],
       is_counter=True,
       contraindications=["herniated_disc"]),

    _p(token="SL",  name="Supine Leg Stretch",  family=PoseFamily.COOLDOWN, intensity=2,
       phase_roles=[Phase.COOLDOWN],
       is_counter=True,
       contraindications=[]),

    _p(token="BS",  name="Boat",  family=PoseFamily.CORE, intensity=6,
       phase_roles=[Phase.BUILD],
       requires_warmup=True,
       contraindications=["lower_back_injury", "pregnancy"]),

    _p(token="KN",  name="Knees to Chest",  family=PoseFamily.RESET, intensity=1,
       phase_roles=[Phase.COOLDOWN],
       is_counter=True,
       contraindications=[]),

    _p(token="HS",  name="Happy Baby",  family=PoseFamily.HIP_OPENER, intensity=2,
       phase_roles=[Phase.COOLDOWN],
       is_counter=True,
       contraindications=["pregnancy"]),

    _p(token="SV",  name="Savasana",  family=PoseFamily.SAVASANA, intensity=1,
       phase_roles=[Phase.SAVASANA],
       is_counter=True,
       contraindications=[]),
]}


# ---------------------------------------------------------------------------
# Macro definitions  (expand at parse-time into raw token chains)
# ---------------------------------------------------------------------------

# Format: macro name -> raw shorthand fragment (same syntax as a pose chain)
# Macros may chain poses with operators but must NOT contain other macros
# (single expansion pass).

MACROS: Dict[str, str] = {
    # Sun Salutation A spine (vinyasa)
    "Viny":  "PL>CH+UD>DD",

    # Half sun salutation
    "HalfA": "FF+HL>DD",

    # Full Sun-A
    "SunA":  "FF+HL>DD+HL>FF",

    # Short upward transition (skip chaturanga, gentler)
    "VinyLt": "PL+UD>DD",

    # Knee-chest-chin vinyasa (gentler alternative)
    "VinyK":  "PL>CB2+DD",

    # Cobra vinyasa (beginners)
    "VinyC":  "PL>CB2>DD",
}
