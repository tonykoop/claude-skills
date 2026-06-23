"""Tests for movement-arts hybrid cross-training generator (#470)."""

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).parent.parent
_DOMAINS = _ROOT / "plugins" / "maker" / "skills" / "movement-arts" / "domains"
_SCRIPTS = _ROOT / "plugins" / "maker" / "skills" / "movement-arts" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from cross_training import (
    CrossTrainingGenerator,
    CrossTrainingRoutine,
    CrossBlock,
    list_presets,
    load_preset,
    make_generator_from_preset,
)


def load_domain(name: str) -> dict:
    with open(_DOMAINS / f"{name}.json") as f:
        return json.load(f)


def two_domain_gen(domain_a="vinyasa", domain_b="capoeira", duration=15.0):
    da, db = load_domain(domain_a), load_domain(domain_b)
    return CrossTrainingGenerator(
        domains=[da, db],
        weights={domain_a: 0.5, domain_b: 0.5},
        duration_min=duration,
    ), da, db


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestCrossTrainingGeneratorConstruction:
    def test_requires_at_least_two_domains(self):
        da = load_domain("vinyasa")
        with pytest.raises(ValueError, match="at least 2"):
            CrossTrainingGenerator(domains=[da])

    def test_constructs_with_two_domains(self):
        gen, _, _ = two_domain_gen()
        assert gen is not None

    def test_weights_are_normalised(self):
        da, db = load_domain("vinyasa"), load_domain("hip_hop")
        gen = CrossTrainingGenerator(
            domains=[da, db],
            weights={"vinyasa": 3.0, "hip_hop": 1.0},
        )
        total = sum(gen._weights.values())
        assert abs(total - 1.0) < 1e-6


# ---------------------------------------------------------------------------
# Preset loading
# ---------------------------------------------------------------------------

class TestPresets:
    def test_list_presets_returns_at_least_two(self):
        assert len(list_presets()) >= 2

    def test_vinyasa_capoeira_preset_exists(self):
        assert "vinyasa-capoeira" in list_presets()

    def test_martial_beats_preset_exists(self):
        assert "martial-beats" in list_presets()

    def test_load_preset_returns_dict(self):
        p = load_preset("vinyasa-capoeira")
        assert "domains" in p
        assert "weights" in p

    def test_unknown_preset_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown preset"):
            load_preset("nonexistent_preset")

    def test_vinyasa_capoeira_preset_has_two_domains(self):
        p = load_preset("vinyasa-capoeira")
        assert len(p["domains"]) == 2
        assert "vinyasa" in p["domains"]
        assert "capoeira" in p["domains"]


# ---------------------------------------------------------------------------
# make_generator_from_preset
# ---------------------------------------------------------------------------

class TestMakeGeneratorFromPreset:
    def test_vinyasa_capoeira_preset_builds(self):
        dl = {"vinyasa": load_domain("vinyasa"), "capoeira": load_domain("capoeira")}
        gen = make_generator_from_preset("vinyasa-capoeira", dl, duration_min=20.0)
        assert gen is not None
        assert gen._preset_name == "vinyasa-capoeira"

    def test_martial_beats_preset_builds(self):
        dl = {"hip_hop": load_domain("hip_hop"), "kata": load_domain("kata")}
        gen = make_generator_from_preset("martial-beats", dl, duration_min=20.0)
        assert gen is not None


# ---------------------------------------------------------------------------
# compile() basics
# ---------------------------------------------------------------------------

class TestCrossTrainingCompile:
    def test_produces_non_empty_blocks(self):
        gen, _, _ = two_domain_gen()
        routine = gen.compile()
        assert len(routine.blocks) > 0

    def test_routine_is_cross_training_routine(self):
        gen, _, _ = two_domain_gen()
        assert isinstance(gen.compile(), CrossTrainingRoutine)

    def test_to_dict_is_serialisable(self):
        gen, _, _ = two_domain_gen()
        d = gen.compile().to_dict()
        json.dumps(d)  # must not raise

    def test_duration_min_preserved(self):
        gen, _, _ = two_domain_gen(duration=20.0)
        assert gen.compile().duration_min == 20.0

    def test_domains_listed_in_output(self):
        gen, _, _ = two_domain_gen("vinyasa", "capoeira")
        routine = gen.compile()
        assert "vinyasa" in routine.domains
        assert "capoeira" in routine.domains


# ---------------------------------------------------------------------------
# Both domains appear in the output
# ---------------------------------------------------------------------------

class TestCrossTrainingDomainCoverage:
    def test_blocks_from_both_domains(self):
        gen, _, _ = two_domain_gen("hip_hop", "kata", duration=30.0)
        routine = gen.compile()
        domains_in_output = {b.domain for b in routine.blocks}
        assert len(domains_in_output) == 2, (
            f"Expected blocks from 2 domains, got: {domains_in_output}"
        )

    def test_block_domain_field_is_set(self):
        gen, _, _ = two_domain_gen()
        routine = gen.compile()
        for b in routine.blocks:
            assert b.domain in {"vinyasa", "capoeira"}, f"Unexpected domain: {b.domain}"

    def test_neither_domain_has_zero_blocks(self):
        gen, _, _ = two_domain_gen("vinyasa", "capoeira", duration=45.0)
        routine = gen.compile()
        vinyasa_count = sum(1 for b in routine.blocks if b.domain == "vinyasa")
        capoeira_count = sum(1 for b in routine.blocks if b.domain == "capoeira")
        assert vinyasa_count > 0
        assert capoeira_count > 0


# ---------------------------------------------------------------------------
# Transitions across domain boundary respect state machine
# ---------------------------------------------------------------------------

class TestCrossTrainingTransitions:
    def test_tracker_state_has_required_fields(self):
        gen, _, _ = two_domain_gen()
        routine = gen.compile()
        state = routine.tracker_final_state
        assert "weight_distribution" in state
        assert "intensity" in state
        assert "facing_direction" in state

    def test_all_blocks_have_valid_weight_shift(self):
        gen, _, _ = two_domain_gen()
        routine = gen.compile()
        valid_ws = {"left", "right", "bilateral", "unweighted"}
        for b in routine.blocks:
            assert b.weight_shift in valid_ws, f"Invalid weight_shift: {b.weight_shift}"

    def test_all_blocks_have_valid_facing(self):
        gen, _, _ = two_domain_gen()
        routine = gen.compile()
        valid_facing = {"north", "south", "east", "west", "any"}
        for b in routine.blocks:
            assert b.facing in valid_facing, f"Invalid facing: {b.facing}"


# ---------------------------------------------------------------------------
# PT safety gate
# ---------------------------------------------------------------------------

class TestCrossTrainingPTGate:
    def test_compile_raises_if_pt_domain_without_acknowledgement(self):
        da = load_domain("vinyasa")
        pt = load_domain("physical_therapy")
        gen = CrossTrainingGenerator(
            domains=[da, pt],
            weights={"vinyasa": 0.5, "physical_therapy": 0.5},
        )
        with pytest.raises(PermissionError):
            gen.compile(safety_acknowledged=False)

    def test_compile_succeeds_with_acknowledgement(self):
        da = load_domain("vinyasa")
        pt = load_domain("physical_therapy")
        gen = CrossTrainingGenerator(
            domains=[da, pt],
            weights={"vinyasa": 0.5, "physical_therapy": 0.5},
        )
        routine = gen.compile(safety_acknowledged=True)
        assert len(routine.blocks) > 0


# ---------------------------------------------------------------------------
# Preset compile integration
# ---------------------------------------------------------------------------

class TestPresetCompileIntegration:
    def test_vinyasa_capoeira_preset_compiles(self):
        dl = {"vinyasa": load_domain("vinyasa"), "capoeira": load_domain("capoeira")}
        gen = make_generator_from_preset("vinyasa-capoeira", dl, duration_min=20.0)
        routine = gen.compile()
        assert len(routine.blocks) > 0
        assert routine.preset == "vinyasa-capoeira"

    def test_martial_beats_preset_compiles(self):
        dl = {"hip_hop": load_domain("hip_hop"), "kata": load_domain("kata")}
        gen = make_generator_from_preset("martial-beats", dl, duration_min=20.0)
        routine = gen.compile()
        assert len(routine.blocks) > 0

    def test_preset_output_is_serialisable(self):
        dl = {"vinyasa": load_domain("vinyasa"), "capoeira": load_domain("capoeira")}
        gen = make_generator_from_preset("vinyasa-capoeira", dl, duration_min=15.0)
        json.dumps(gen.compile().to_dict())
