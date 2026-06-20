"""
yoga_engine — structural scaffolding for the yoga-sequencer skill upgrade (epic #368).

Public API:
    parse_shorthand(text)       -> Sequence
    validate_sequence(seq)      -> ValidationReport
    analyze_arc(seq)            -> ArcReport
    expand_macros(text)         -> str
"""

from .schema import (
    Pose, PoseFamily, PoseInstance, Phase, PhaseBlock,
    Sequence, BreathOp, ValidationIssue, ValidationReport, ArcReport,
)
from .pose_db import POSE_DB, MACROS
from .parser import parse_shorthand, expand_macros
from .validator import validate_sequence
from .arc import analyze_arc
from .transitions import (
    TransitionVector, Pathway, Pacing,
    TRANSITION_DB,
    get_transitions, get_exits, get_entries,
    suggest_transition, annotate_sequence_transitions,
)
from .config import (
    EngineConfig, AudioSyncConfig, ValidationConfig, ArcConfig,
    PoseThesaurus, ThesaurusEntry,
    load_config, load_thesaurus,
    get_config, get_thesaurus, reset_singletons,
)

__version__ = "0.1.0"
__all__ = [
    "Pose", "PoseFamily", "PoseInstance", "Phase", "PhaseBlock",
    "Sequence", "BreathOp", "ValidationIssue", "ValidationReport", "ArcReport",
    "POSE_DB", "MACROS",
    "parse_shorthand", "expand_macros",
    "validate_sequence",
    "analyze_arc",
]
