"""
schema.py — core data models for the yoga_engine.

Principles:
- Pure Python dataclasses; no third-party runtime deps.
- Intensity is 1–10 (1=rest/savasana, 10=maximum-effort peak pose).
- BreathOp describes how you *enter* a pose from the previous one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PoseFamily(str, Enum):
    CENTERING = "centering"
    WARMUP = "warmup"
    SPINAL_MOBILITY = "spinal_mobility"
    STANDING = "standing"
    BALANCE = "balance"
    TWIST = "twist"
    BACKBEND = "backbend"
    HIP_OPENER = "hip_opener"
    INVERSION = "inversion"
    ARM_BALANCE = "arm_balance"
    FORWARD_FOLD = "forward_fold"
    CORE = "core"
    COOLDOWN = "cooldown"
    RESET = "reset"
    SAVASANA = "savasana"
    TRANSITION = "transition"


class Phase(str, Enum):
    ARRIVAL = "arrival"
    WARMUP = "warmup"
    BUILD = "build"
    PEAK = "peak"
    COOLDOWN = "cooldown"
    SAVASANA = "savasana"


class BreathOp(str, Enum):
    INHALE = "inhale"  # shorthand: +
    EXHALE = "exhale"  # shorthand: >
    HOLD = "hold"      # shorthand: //


# ---------------------------------------------------------------------------
# Pose definition  (static knowledge about a pose)
# ---------------------------------------------------------------------------


@dataclass
class Pose:
    """Static descriptor for a single yoga pose."""
    token: str                          # shorthand token, e.g. "DD"
    name: str                           # human name, e.g. "Downward Dog"
    family: PoseFamily
    intensity: int                      # 1–10

    # Phase suitability
    phase_roles: List[Phase] = field(default_factory=list)

    # Structural flags (used by validator)
    requires_warmup: bool = False       # should not appear before warmup is done
    needs_counter: bool = False         # should be followed by a counter pose
    is_backbend: bool = False
    is_twist: bool = False
    is_inversion: bool = False
    is_arm_balance: bool = False
    is_peak: bool = False               # archetypal peak / climax pose
    is_counter: bool = False            # can serve as a counter pose
    is_prep: bool = False               # primarily a prep / lead-up pose

    # Safety
    contraindications: List[str] = field(default_factory=list)
    heated_caution: bool = False        # extra care in hot-room context

    def __post_init__(self) -> None:
        if not 1 <= self.intensity <= 10:
            raise ValueError(f"Pose {self.token!r}: intensity must be 1–10, got {self.intensity}")

    def __repr__(self) -> str:
        return f"Pose({self.token!r}, {self.name!r}, intensity={self.intensity})"


# ---------------------------------------------------------------------------
# PoseInstance  (a pose as it appears inside a sequence, with side + breath)
# ---------------------------------------------------------------------------


@dataclass
class PoseInstance:
    """A single pose occurrence inside a sequence block."""
    pose: Pose
    side: Optional[str] = None          # 'r', 'l', 'f', 'b', 'open', 'cl'
    breath_count: Optional[int] = None  # explicit breath hold count
    entry_op: Optional[BreathOp] = None # how we arrive here from prev pose
    raw_token: str = ""                 # original shorthand fragment

    @property
    def display_name(self) -> str:
        base = self.pose.name
        side_map = {"r": "(R)", "l": "(L)", "f": "(Front)", "b": "(Back)",
                    "open": "(Open)", "cl": "(Closed)"}
        if self.side and self.side in side_map:
            base += f" {side_map[self.side]}"
        return base


# ---------------------------------------------------------------------------
# PhaseBlock  (a named phase within a sequence: WU, BD, PK …)
# ---------------------------------------------------------------------------


@dataclass
class PhaseBlock:
    """One phase segment of a class (warmup, build, peak, etc.)."""
    label: str              # raw label from shorthand, e.g. "WU"
    phase: Phase            # normalised phase enum
    poses: List[PoseInstance] = field(default_factory=list)

    @property
    def max_intensity(self) -> int:
        if not self.poses:
            return 0
        return max(p.pose.intensity for p in self.poses)

    @property
    def avg_intensity(self) -> float:
        if not self.poses:
            return 0.0
        return sum(p.pose.intensity for p in self.poses) / len(self.poses)


# ---------------------------------------------------------------------------
# Sequence  (a complete class plan)
# ---------------------------------------------------------------------------


@dataclass
class Sequence:
    """A complete yoga class sequence parsed from shorthand."""
    title: str
    duration_minutes: int
    phases: List[PhaseBlock] = field(default_factory=list)
    heated_room: bool = False
    level: str = "mixed"          # "beginner" | "intermediate" | "advanced" | "mixed"
    theme: str = ""
    raw_shorthand: str = ""

    @property
    def all_poses(self) -> List[PoseInstance]:
        """Flat list of every PoseInstance across all phases."""
        result: List[PoseInstance] = []
        for ph in self.phases:
            result.extend(ph.poses)
        return result

    @property
    def intensity_curve(self) -> List[int]:
        """Intensity value per pose, in order."""
        return [p.pose.intensity for p in self.all_poses]

    def get_phase(self, phase: Phase) -> Optional[PhaseBlock]:
        for ph in self.phases:
            if ph.phase == phase:
                return ph
        return None


# ---------------------------------------------------------------------------
# Validation & Arc report types
# ---------------------------------------------------------------------------


class IssueSeverity(str, Enum):
    ERROR = "error"       # safety / structural violation
    WARNING = "warning"   # best-practice deviation
    INFO = "info"         # informational note


@dataclass
class ValidationIssue:
    severity: IssueSeverity
    code: str             # machine-readable slug, e.g. "NO_WARMUP_BEFORE_PEAK"
    message: str
    phase: Optional[str] = None
    pose_token: Optional[str] = None


@dataclass
class ValidationReport:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == IssueSeverity.ERROR]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == IssueSeverity.WARNING]

    @property
    def is_safe(self) -> bool:
        return len(self.errors) == 0

    def __repr__(self) -> str:
        return (f"ValidationReport(errors={len(self.errors)}, "
                f"warnings={len(self.warnings)}, safe={self.is_safe})")


@dataclass
class ArcReport:
    """Energy-curve analysis of a sequence."""
    intensity_curve: List[int]
    phase_labels: List[str]           # parallel to intensity_curve
    peak_index: int                   # index of highest intensity pose
    peak_intensity: int
    warmup_plateau: float             # avg intensity in warmup phase
    cooldown_plateau: float           # avg intensity in cooldown phase
    arc_shape: str                    # "mountain" | "plateau" | "spike" | "flat" | "inverted"
    notes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Arc: {self.arc_shape}  |  "
            f"Peak intensity {self.peak_intensity} at position {self.peak_index + 1}  |  "
            f"Warmup avg {self.warmup_plateau:.1f}  |  "
            f"Cooldown avg {self.cooldown_plateau:.1f}"
        )
