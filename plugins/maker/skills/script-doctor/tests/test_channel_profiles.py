"""Tests for channel_profiles.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from channel_profiles import (
    resolve_archetype,
    list_archetypes,
    get_profile,
    load_profiles,
    check_hard_constraints,
    ARCHETYPE_ALIASES,
)


def test_resolve_archetype_canonical():
    assert resolve_archetype("yoga") == "yoga"
    assert resolve_archetype("wrfcoin") == "wrfcoin"
    assert resolve_archetype("ai_agentic") == "ai_agentic"


def test_resolve_archetype_alias():
    assert resolve_archetype("inner-compass-yoga") == "yoga"
    assert resolve_archetype("maker") == "instrument_maker"
    assert resolve_archetype("agentic") == "ai_agentic"
    assert resolve_archetype("reflective") == "consciousness"
    assert resolve_archetype("crypto") == "wrfcoin"


def test_resolve_archetype_unknown_fallback():
    assert resolve_archetype("this-is-not-a-channel") == "unknown"


def test_list_archetypes_returns_all():
    try:
        profiles = load_profiles()
        archetypes = list_archetypes(profiles)
    except (RuntimeError, FileNotFoundError):
        archetypes = list_archetypes()  # fallback list
    assert "yoga" in archetypes
    assert "instrument_maker" in archetypes
    assert "ai_agentic" in archetypes
    assert "consciousness" in archetypes
    assert "wrfcoin" in archetypes
    assert "unknown" in archetypes


def test_get_profile_yoga_has_constraints():
    try:
        profiles = load_profiles()
    except (RuntimeError, FileNotFoundError):
        return  # skip if yaml unavailable
    profile = get_profile("yoga", profiles)
    assert "hard_constraints" in profile
    assert len(profile["hard_constraints"]) > 0


def test_get_profile_unknown_alias():
    try:
        profiles = load_profiles()
    except (RuntimeError, FileNotFoundError):
        return
    profile = get_profile("inner-compass-yoga", profiles)
    assert profile.get("archetype") == "yoga"


def test_get_profile_unknown_archetype_returns_unknown():
    try:
        profiles = load_profiles()
    except (RuntimeError, FileNotFoundError):
        return
    profile = get_profile("nonexistent-channel-xyz", profiles)
    assert profile.get("archetype") == "unknown"


def test_check_hard_constraints_no_violations():
    try:
        profiles = load_profiles()
    except (RuntimeError, FileNotFoundError):
        return
    # Yoga script with no rushed cues
    notes = "A warm, grounded narration with 8-count breath pauses throughout."
    violations = check_hard_constraints("yoga", notes, profiles)
    assert violations == []


def test_all_profiles_have_required_keys():
    try:
        profiles = load_profiles()
    except (RuntimeError, FileNotFoundError):
        return
    required_keys = ["archetype", "spoken_pace_target", "hard_constraints", "cta_language"]
    for name, profile in profiles.items():
        for key in required_keys:
            assert key in profile, f"Profile '{name}' missing key '{key}'"
