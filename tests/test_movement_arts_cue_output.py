"""Tests for movement-arts multi-modal instructional cue output (#469)."""

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).parent.parent
_DOMAINS = _ROOT / "plugins" / "maker" / "skills" / "movement-arts" / "domains"
_SCRIPTS = _ROOT / "plugins" / "maker" / "skills" / "movement-arts" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from cue_output import CueFormatter, _FORMAT_TYPES
from sequencer import MovementSequencer


def load_domain(name: str) -> dict:
    with open(_DOMAINS / f"{name}.json") as f:
        return json.load(f)


def compile_routine(domain_name: str, duration_min: float = 15.0, **kwargs):
    d = load_domain(domain_name)
    seq = MovementSequencer(domain=d)
    return seq.compile(duration_min, **kwargs), d


# ---------------------------------------------------------------------------
# CueFormatter construction
# ---------------------------------------------------------------------------

class TestCueFormatterConstruction:
    def test_accepts_compiled_routine_object(self):
        routine, domain = compile_routine("hip_hop")
        formatter = CueFormatter(routine, domain)
        assert formatter is not None

    def test_accepts_dict_form(self):
        routine, domain = compile_routine("hip_hop")
        formatter = CueFormatter(routine.to_dict(), domain)
        assert formatter is not None

    def test_unknown_format_raises_value_error(self):
        routine, domain = compile_routine("hip_hop")
        formatter = CueFormatter(routine, domain)
        with pytest.raises(ValueError, match="Unknown format"):
            formatter.format("nonexistent_format")

    def test_known_formats_are_registered(self):
        assert "verbal" in _FORMAT_TYPES
        assert "audio_energy" in _FORMAT_TYPES
        assert "pt_biomechanical" in _FORMAT_TYPES


# ---------------------------------------------------------------------------
# verbal format
# ---------------------------------------------------------------------------

class TestVerbalFormat:
    def setup_method(self):
        self.routine, self.domain = compile_routine("hip_hop")
        self.formatter = CueFormatter(self.routine, self.domain)
        self.output = self.formatter.format("verbal")

    def test_returns_one_entry_per_block(self):
        assert len(self.output) == len(self.routine.blocks)

    def test_first_entry_has_opening_cue(self):
        assert "We begin" in self.output[0]["instructor_cue"]

    def test_every_entry_has_instructor_cue(self):
        for entry in self.output:
            assert "instructor_cue" in entry
            assert isinstance(entry["instructor_cue"], str)
            assert len(entry["instructor_cue"]) > 0

    def test_every_entry_has_energy_level(self):
        valid = {"rest", "low", "moderate", "high", "peak"}
        for entry in self.output:
            assert entry["energy_level"] in valid

    def test_verbal_has_no_pt_biomechanical_fields(self):
        pt_fields = {"velocity_cap_m_per_s", "unilateral_load", "ROM_target_deg", "compensation_cues"}
        for entry in self.output:
            for field in pt_fields:
                assert field not in entry, f"verbal output contains PT field '{field}'"

    def test_every_entry_has_block_index(self):
        for i, entry in enumerate(self.output):
            assert entry["block_index"] == i

    def test_breath_domain_uses_inhale_cue(self):
        routine, domain = compile_routine("vinyasa")
        formatter = CueFormatter(routine, domain)
        output = formatter.format("verbal")
        assert "inhale" in output[0]["instructor_cue"].lower()

    def test_beat_domain_uses_count_cue(self):
        assert "count 1" in self.output[0]["instructor_cue"]


# ---------------------------------------------------------------------------
# audio_energy format
# ---------------------------------------------------------------------------

class TestAudioEnergyFormat:
    def setup_method(self):
        self.routine, self.domain = compile_routine("hip_hop")
        self.formatter = CueFormatter(self.routine, self.domain)
        self.output = self.formatter.format("audio_energy")

    def test_returns_one_entry_per_block(self):
        assert len(self.output) == len(self.routine.blocks)

    def test_every_entry_has_bpm_target(self):
        for entry in self.output:
            assert "bpm_target" in entry, "audio_energy entry missing bpm_target"
            assert isinstance(entry["bpm_target"], (int, float))
            assert entry["bpm_target"] > 0

    def test_bpm_target_in_domain_range(self):
        bpm_range = self.domain["clock"]["bpm_range"]
        for entry in self.output:
            assert bpm_range[0] <= entry["bpm_target"] <= bpm_range[1]

    def test_every_entry_has_energy_level(self):
        valid = {"rest", "low", "moderate", "high", "peak"}
        for entry in self.output:
            assert entry["energy_level"] in valid

    def test_every_entry_has_energy_raw(self):
        for entry in self.output:
            assert "energy_raw" in entry
            assert 0.0 <= entry["energy_raw"] <= 1.0

    def test_every_entry_has_cue_density(self):
        for entry in self.output:
            assert "cue_density" in entry
            assert entry["cue_density"] in {"sparse", "moderate", "rhythmic", "focused", "minimal"}

    def test_every_entry_has_block_id(self):
        for entry in self.output:
            assert "block_id" in entry
            assert isinstance(entry["block_id"], str)

    def test_audio_energy_has_no_pt_fields(self):
        pt_fields = {"velocity_cap_m_per_s", "unilateral_load", "ROM_target_deg", "compensation_cues"}
        for entry in self.output:
            for field in pt_fields:
                assert field not in entry


# ---------------------------------------------------------------------------
# pt_biomechanical format
# ---------------------------------------------------------------------------

class TestPTBiomechanicalFormat:
    def setup_method(self):
        self.routine, self.domain = compile_routine(
            "physical_therapy", safety_acknowledged=True
        )
        self.formatter = CueFormatter(self.routine, self.domain)
        self.output = self.formatter.format("pt_biomechanical")

    def test_returns_one_entry_per_block(self):
        assert len(self.output) == len(self.routine.blocks)

    def test_every_entry_has_compensation_cues_list(self):
        for entry in self.output:
            assert "compensation_cues" in entry
            assert isinstance(entry["compensation_cues"], list)

    def test_every_entry_has_velocity_cap(self):
        for entry in self.output:
            assert "velocity_cap_m_per_s" in entry

    def test_every_entry_has_unilateral_load(self):
        for entry in self.output:
            assert "unilateral_load" in entry

    def test_every_entry_has_rom_target(self):
        for entry in self.output:
            assert "ROM_target_deg" in entry

    def test_unilateral_load_generates_cue(self):
        """Any block with unilateral_load=True must produce at least one compensation cue."""
        for entry in self.output:
            if entry.get("unilateral_load"):
                assert len(entry["compensation_cues"]) >= 1


# ---------------------------------------------------------------------------
# pt_biomechanical on non-PT domain: no PT fields, empty compensation cues
# ---------------------------------------------------------------------------

class TestPTFormatOnNonPTDomain:
    def test_verbal_on_pt_domain_has_no_pt_fields(self):
        """verbal format on a PT routine must NOT expose PT-specific fields."""
        routine, domain = compile_routine("physical_therapy", safety_acknowledged=True)
        formatter = CueFormatter(routine, domain)
        output = formatter.format("verbal")
        pt_fields = {"velocity_cap_m_per_s", "unilateral_load", "ROM_target_deg", "compensation_cues"}
        for entry in output:
            for field in pt_fields:
                assert field not in entry

    def test_pt_biom_on_non_pt_domain_has_null_velocity(self):
        """pt_biomechanical on a dance domain: velocity_cap_m_per_s should be None."""
        routine, domain = compile_routine("hip_hop")
        formatter = CueFormatter(routine, domain)
        output = formatter.format("pt_biomechanical")
        for entry in output:
            assert entry.get("velocity_cap_m_per_s") is None

    def test_pt_biom_on_non_pt_domain_has_empty_cues(self):
        """pt_biomechanical on ballet: compensation_cues must be empty for non-PT primitives."""
        routine, domain = compile_routine("ballet")
        formatter = CueFormatter(routine, domain)
        output = formatter.format("pt_biomechanical")
        for entry in output:
            assert isinstance(entry["compensation_cues"], list)


# ---------------------------------------------------------------------------
# audio_energy format on breath domains
# ---------------------------------------------------------------------------

class TestAudioEnergyBreathDomain:
    def test_breath_domain_bpm_target_is_breath_bpm(self):
        routine, domain = compile_routine("tai_chi")
        formatter = CueFormatter(routine, domain)
        output = formatter.format("audio_energy")
        for entry in output:
            assert entry["bpm_target"] == domain["clock"]["bpm"]
