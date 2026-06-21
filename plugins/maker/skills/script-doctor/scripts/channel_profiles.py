"""
channel_profiles.py — load and validate channel profiles for the script-doctor skill.

Usage:
    from channel_profiles import load_profiles, get_profile, list_archetypes
    profiles = load_profiles()
    profile = get_profile("yoga", profiles)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# Fallback minimal profiles when PyYAML is not installed
_FALLBACK_ARCHETYPES = [
    "yoga", "instrument_maker", "ai_agentic", "consciousness", "wrfcoin", "unknown"
]

_REFERENCES_DIR = Path(__file__).parent.parent / "references"
_PROFILES_FILE = _REFERENCES_DIR / "channel-profiles.yaml"

ARCHETYPE_ALIASES: dict[str, str] = {
    "yoga": "yoga",
    "inner_compass_yoga": "yoga",
    "maker": "instrument_maker",
    "instrument_maker": "instrument_maker",
    "fabrication": "instrument_maker",
    "ai": "ai_agentic",
    "agentic": "ai_agentic",
    "ai_agentic": "ai_agentic",
    "consciousness": "consciousness",
    "reflective": "consciousness",
    "wrfcoin": "wrfcoin",
    "crypto": "wrfcoin",
    "unknown": "unknown",
}


def load_profiles(path: Path | None = None) -> dict[str, Any]:
    """Load channel-profiles.yaml. Returns a dict keyed by archetype name."""
    file = path or _PROFILES_FILE
    if not _HAS_YAML:
        raise RuntimeError(
            "PyYAML is required: pip install pyyaml. "
            "Use list_archetypes() for archetype names without loading profiles."
        )
    if not file.exists():
        raise FileNotFoundError(f"Channel profiles file not found: {file}")
    with file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    profiles = data.get("profiles", {})
    if not profiles:
        raise ValueError(f"No profiles found in {file}")
    return profiles


def resolve_archetype(name: str) -> str:
    """Normalize an archetype name or alias to its canonical key."""
    key = name.lower().replace("-", "_").strip()
    return ARCHETYPE_ALIASES.get(key, "unknown")


def get_profile(archetype: str, profiles: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the profile dict for the given archetype (loads if not supplied)."""
    canonical = resolve_archetype(archetype)
    if profiles is None:
        profiles = load_profiles()
    profile = profiles.get(canonical)
    if profile is None:
        profile = profiles.get("unknown", {})
    return profile


def list_archetypes(profiles: dict[str, Any] | None = None) -> list[str]:
    """Return a sorted list of available archetype keys."""
    if profiles is None:
        if not _HAS_YAML:
            return sorted(_FALLBACK_ARCHETYPES)
        profiles = load_profiles()
    return sorted(profiles.keys())


def check_hard_constraints(archetype: str, notes: str, profiles: dict[str, Any] | None = None) -> list[str]:
    """Return any hard constraints from the profile whose keywords appear in notes."""
    profile = get_profile(archetype, profiles)
    violations: list[str] = []
    for constraint in profile.get("hard_constraints", []):
        # Simple keyword presence check — the AI does the deep semantic check
        first_word = constraint.split()[0].lower().rstrip("—-:").lower()
        if first_word in ("no", "never") and len(constraint.split()) > 2:
            forbidden_phrase = " ".join(constraint.split()[1:4]).lower().strip("'\"")
            if forbidden_phrase in notes.lower():
                violations.append(constraint)
    return violations
