"""
config.py — runtime configuration loader for yoga_engine (Story #374).

Reads ``yoga_engine/data/config.toml`` (or a user-supplied path) and exposes a
typed :class:`EngineConfig` object.  Falls back to sensible defaults when the
TOML file is absent or when individual keys are missing — the engine always starts.

The thesaurus (pose_thesaurus.json) is also loaded here and exposed via
:func:`lookup_token` and :func:`resolve_alias`.

No third-party dependencies: uses ``tomllib`` (stdlib ≥ 3.11) with a
``tomli`` shim for Python 3.10 and below.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# TOML loading — stdlib 3.11+ or fallback
# ---------------------------------------------------------------------------

try:
    import tomllib  # Python ≥ 3.11
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]


_DATA_DIR = Path(__file__).parent / "data"
_DEFAULT_CONFIG_PATH = _DATA_DIR / "config.toml"
_DEFAULT_THESAURUS_PATH = _DATA_DIR / "pose_thesaurus.json"


# ---------------------------------------------------------------------------
# Typed config dataclass
# ---------------------------------------------------------------------------


@dataclass
class AudioSyncConfig:
    lufs_target: float = -16.0
    crossfade_slow_multiplier: float = 1.5
    crossfade_medium_multiplier: float = 1.0
    crossfade_fast_multiplier: float = 0.5


@dataclass
class ValidationConfig:
    suppress_codes: List[str] = field(default_factory=list)
    min_warmup_poses_before_peak: int = 3


@dataclass
class ArcConfig:
    flat_stdev_threshold: float = 1.2
    spike_ratio: float = 0.60


@dataclass
class EngineConfig:
    current_phase: str = "warmup"
    syntax_strictness: str = "strict"   # "strict" | "lenient" | "debug"
    audio_sync: AudioSyncConfig = field(default_factory=AudioSyncConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    arc: ArcConfig = field(default_factory=ArcConfig)

    # Path the config was loaded from (None = defaults used)
    _source_path: Optional[Path] = field(default=None, repr=False, compare=False)

    @property
    def source_path(self) -> Optional[Path]:
        return self._source_path

    def is_strict(self) -> bool:
        return self.syntax_strictness in ("strict", "debug")

    def is_debug(self) -> bool:
        return self.syntax_strictness == "debug"


# ---------------------------------------------------------------------------
# TOML loader
# ---------------------------------------------------------------------------


def _load_toml(path: Path) -> dict:
    if tomllib is None:
        return {}
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except FileNotFoundError:
        return {}
    except Exception:
        return {}


def load_config(path: Optional[Path] = None) -> EngineConfig:
    """
    Load engine configuration from a TOML file.

    Args:
        path: Path to a ``.toml`` file.  Defaults to
              ``yoga_engine/data/config.toml``.

    Returns:
        :class:`EngineConfig` populated from the file.  Missing keys use
        dataclass defaults.
    """
    resolved_path = path or _DEFAULT_CONFIG_PATH
    raw = _load_toml(resolved_path)

    eng = raw.get("engine", {})
    aud = raw.get("audio_sync", {})
    val = raw.get("validation", {})
    arc = raw.get("arc", {})

    cfg = EngineConfig(
        current_phase=eng.get("current_phase", "warmup"),
        syntax_strictness=eng.get("syntax_strictness", "strict"),
        audio_sync=AudioSyncConfig(
            lufs_target=aud.get("lufs_target", -16.0),
            crossfade_slow_multiplier=aud.get("crossfade_slow_multiplier", 1.5),
            crossfade_medium_multiplier=aud.get("crossfade_medium_multiplier", 1.0),
            crossfade_fast_multiplier=aud.get("crossfade_fast_multiplier", 0.5),
        ),
        validation=ValidationConfig(
            suppress_codes=val.get("suppress_codes", []),
            min_warmup_poses_before_peak=val.get("min_warmup_poses_before_peak", 3),
        ),
        arc=ArcConfig(
            flat_stdev_threshold=arc.get("flat_stdev_threshold", 1.2),
            spike_ratio=arc.get("spike_ratio", 0.60),
        ),
        _source_path=resolved_path if resolved_path.exists() else None,
    )
    return cfg


# ---------------------------------------------------------------------------
# Thesaurus loader
# ---------------------------------------------------------------------------


@dataclass
class ThesaurusEntry:
    token: str
    name: str
    sanskrit: str
    aliases: List[str]
    family: str
    intensity: int


class PoseThesaurus:
    """
    Pose token ↔ name/alias lookup.

    Built from ``pose_thesaurus.json``; exposes:
    - :meth:`lookup` — token → ThesaurusEntry
    - :meth:`resolve` — alias / name → canonical token
    """

    def __init__(self, entries: List[ThesaurusEntry]) -> None:
        self._by_token: Dict[str, ThesaurusEntry] = {e.token: e for e in entries}
        self._alias_map: Dict[str, str] = {}
        for e in entries:
            self._alias_map[e.token.lower()] = e.token
            self._alias_map[e.name.lower()] = e.token
            if e.sanskrit:
                self._alias_map[e.sanskrit.lower()] = e.token
            for alias in e.aliases:
                self._alias_map[alias.lower()] = e.token

    def lookup(self, token: str) -> Optional[ThesaurusEntry]:
        """Return the ThesaurusEntry for *token*, or None if not found."""
        return self._by_token.get(token)

    def resolve(self, alias_or_name: str) -> Optional[str]:
        """
        Resolve an alias, common name, Sanskrit name, or token string
        to the canonical token.  Returns None if unrecognised.
        """
        return self._alias_map.get(alias_or_name.lower())

    def all_tokens(self) -> List[str]:
        return list(self._by_token.keys())

    def __len__(self) -> int:
        return len(self._by_token)

    def __repr__(self) -> str:
        return f"PoseThesaurus({len(self)} poses)"


def load_thesaurus(path: Optional[Path] = None) -> PoseThesaurus:
    """
    Load the pose thesaurus from JSON.

    Args:
        path: Path to ``pose_thesaurus.json``.  Defaults to
              ``yoga_engine/data/pose_thesaurus.json``.

    Returns:
        :class:`PoseThesaurus` ready for lookup.
    """
    resolved_path = path or _DEFAULT_THESAURUS_PATH
    try:
        with resolved_path.open() as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        return PoseThesaurus([])

    entries = [
        ThesaurusEntry(
            token=p["token"],
            name=p["name"],
            sanskrit=p.get("sanskrit", ""),
            aliases=p.get("aliases", []),
            family=p.get("family", ""),
            intensity=p.get("intensity", 5),
        )
        for p in raw.get("poses", [])
    ]
    return PoseThesaurus(entries)


# ---------------------------------------------------------------------------
# Module-level singletons (lazy-loaded)
# ---------------------------------------------------------------------------

_config: Optional[EngineConfig] = None
_thesaurus: Optional[PoseThesaurus] = None


def get_config() -> EngineConfig:
    """Return the module-level EngineConfig (loaded once, cached)."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def get_thesaurus() -> PoseThesaurus:
    """Return the module-level PoseThesaurus (loaded once, cached)."""
    global _thesaurus
    if _thesaurus is None:
        _thesaurus = load_thesaurus()
    return _thesaurus


def reset_singletons() -> None:
    """Reset cached singletons — used in tests to force reload."""
    global _config, _thesaurus
    _config = None
    _thesaurus = None
