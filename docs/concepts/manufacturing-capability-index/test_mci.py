"""Tests for the Manufacturing Capability Index validator + triage (#205)."""
from __future__ import annotations

import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def load_module():
    spec = importlib.util.spec_from_file_location("mci_validate", HERE / "validate.py")
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mci = load_module()


# --- bundled sample data validates ------------------------------------------

def test_sample_data_is_valid():
    assert mci.main([]) == 0


def test_process_schema_loads():
    s = mci.load_schema("process_capability_row.schema.json")
    assert s["title"] == "Process Capability Row"


# --- schema validator -------------------------------------------------------

def _good_element():
    return {
        "symbol": "Al", "name": "Aluminium", "crustal_abundance_ppm": 82300,
        "annual_run_rate_tonnes": 69000000, "gateable_today": True, "source": "x",
    }


def test_valid_element_row_has_no_errors():
    schema = mci.load_schema("element_inventory_row.schema.json")
    assert mci.validate_against_schema(_good_element(), schema) == []


def test_missing_required_field_flagged():
    schema = mci.load_schema("element_inventory_row.schema.json")
    row = _good_element()
    del row["crustal_abundance_ppm"]
    errs = mci.validate_against_schema(row, schema)
    assert any("crustal_abundance_ppm" in e for e in errs)


def test_additional_property_flagged():
    schema = mci.load_schema("element_inventory_row.schema.json")
    row = _good_element()
    row["bogus"] = 1
    errs = mci.validate_against_schema(row, schema)
    assert any("bogus" in e for e in errs)


def test_bad_symbol_pattern_flagged():
    schema = mci.load_schema("element_inventory_row.schema.json")
    row = _good_element()
    row["symbol"] = "aluminium"  # must be Xx
    errs = mci.validate_against_schema(row, schema)
    assert any("symbol" in e for e in errs)


def test_negative_abundance_flagged():
    schema = mci.load_schema("element_inventory_row.schema.json")
    row = _good_element()
    row["crustal_abundance_ppm"] = -1
    errs = mci.validate_against_schema(row, schema)
    assert any("exclusiveMinimum" in e for e in errs)


def test_enum_state_of_matter_flagged():
    schema = mci.load_schema("process_capability_row.schema.json")
    row = {
        "process": "x-proc", "display_name": "X", "min_feature_mm": 1.0,
        "max_envelope_mm": {"x": 10, "y": 10, "z": 10}, "tolerance_floor_mm": 0.1,
        "states_of_matter": ["jelly"], "as_of": "2026-Q3", "gateable_today": True,
        "source": "x",
    }
    errs = mci.validate_against_schema(row, schema)
    assert any("jelly" in e for e in errs)


# --- scarcity penalty -------------------------------------------------------

def test_gold_is_scarce():
    assert mci.derive_scarcity_penalty(0.004) > 0.8


def test_aluminium_is_abundant():
    assert mci.derive_scarcity_penalty(82300) < 0.1


def test_penalty_monotonic():
    # rarer element -> higher penalty
    assert mci.derive_scarcity_penalty(0.004) > mci.derive_scarcity_penalty(41.5)
    assert mci.derive_scarcity_penalty(41.5) > mci.derive_scarcity_penalty(82300)


def test_penalty_clamped_0_1():
    assert mci.derive_scarcity_penalty(1e9) == 0.0
    assert mci.derive_scarcity_penalty(1e-9) == 1.0


def test_stored_penalty_overrides_derivation():
    row = {"symbol": "Au", "crustal_abundance_ppm": 0.004, "scarcity_penalty": 0.1}
    assert mci.scarcity_penalty_of(row) == 0.1


# --- the gate: reject scarce, force substitute ------------------------------

def test_gold_rejected_with_substitute():
    row = {"symbol": "Au", "crustal_abundance_ppm": 0.004, "abundant_substitutes": ["Cu", "Al"]}
    verdict = mci.gate_material(row)
    assert verdict["allowed"] is False
    assert "Cu" in verdict["substitutes"]
    assert "prefer" in verdict["reason"]


def test_aluminium_allowed():
    row = {"symbol": "Al", "crustal_abundance_ppm": 82300}
    assert mci.gate_material(row)["allowed"] is True


def test_scarce_without_substitute_still_rejected():
    row = {"symbol": "Au", "crustal_abundance_ppm": 0.004}
    verdict = mci.gate_material(row)
    assert verdict["allowed"] is False
    assert "no substitute" in verdict["reason"]


# --- gateable-today partition (acceptance: identify gateable fields) --------

def test_gateable_today_partition():
    assert "min_feature_mm" in mci.gateable_today("process")
    assert "crustal_abundance_ppm" in mci.gateable_today("element")
    # run-rate / kinematics under load are aspirational, not gateable today
    assert "annual_run_rate_tonnes" not in mci.gateable_today("element")
    assert "kinematic_cadence" not in mci.gateable_today("process")


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
