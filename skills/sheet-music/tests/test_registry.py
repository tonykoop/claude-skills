"""Verify that instruments/registry.yaml stays well-formed.

The skill's pipeline reads the registry as both YAML and via a
text-search fallback. Both paths need to keep working as new
instruments are added, so we test both here.
"""
from __future__ import annotations

from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "instruments" / "registry.yaml"

REQUIRED_FIELDS = {
    "id", "display_name", "family", "subfamily", "build_repo",
    "transposition", "fingering",
}
KNOWN_FAMILIES = {"flute", "strings", "reeds-and-pipes",
                  "percussion", "hybrid"}


def test_registry_parses_as_yaml():
    data = yaml.safe_load(REGISTRY.read_text())
    assert isinstance(data, dict)
    assert KNOWN_FAMILIES.issuperset(data.keys()), \
        f"unexpected family keys: {set(data) - KNOWN_FAMILIES}"


def test_every_row_has_required_fields():
    data = yaml.safe_load(REGISTRY.read_text())
    for family, rows in data.items():
        for row in rows:
            missing = REQUIRED_FIELDS - row.keys()
            assert not missing, (
                f"{family}/{row.get('id')}: missing required "
                f"fields {missing}"
            )


def test_ids_are_unique_across_families():
    data = yaml.safe_load(REGISTRY.read_text())
    ids = []
    for rows in data.values():
        ids.extend(row["id"] for row in rows)
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"duplicate instrument ids: {duplicates}"


def test_pitched_instruments_have_range():
    """Pitched instruments need range_low and range_high. Unpitched
    percussion (range_low: ~) is exempt."""
    data = yaml.safe_load(REGISTRY.read_text())
    for family, rows in data.items():
        for row in rows:
            if row.get("range_low") is None:
                # Only acceptable for unpitched percussion
                assert family == "percussion", (
                    f"{row['id']}: missing range_low (only OK for "
                    "unpitched percussion)"
                )


def test_soundfont_presets_in_gm_range():
    data = yaml.safe_load(REGISTRY.read_text())
    for rows in data.values():
        for row in rows:
            preset = row.get("soundfont_preset")
            if preset is None:
                continue  # unpitched perc uses GM channel 10, no preset
            assert 1 <= preset <= 128, (
                f"{row['id']}: soundfont_preset {preset} outside GM "
                "range 1-128"
            )


def test_text_search_fallback_finds_naf():
    """The scripts include a text-search fallback for environments
    without PyYAML. Verify that fallback can still find expected fields."""
    text = REGISTRY.read_text()
    assert "id: naf-6hole" in text
    block = text.split("id: naf-6hole", 1)[1].split("- id:", 1)[0]
    assert "range_low: A4" in block
    assert "fingering: naf-6hole" in block
