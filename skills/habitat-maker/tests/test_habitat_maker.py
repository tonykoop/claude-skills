"""
Smoke tests for habitat-maker v0.4.

Asserts:
  1. Canonical examples parse, have required schema sections, and declare
     their welfare gates.
  2. Generator scripts emit deterministic SVG/CSV artifacts.
  3. Example packets have the files their build-packet contracts require.

Run from repo root:
    python3 -m unittest discover -s skills/habitat-maker/tests

Pure-stdlib (json, pathlib, subprocess, unittest, xml.etree). No
third-party deps required.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parent.parent
PACKET_DIR = SKILL_DIR / "examples" / "chickadee-laser-baltic-birch"
CAMERA_PACKET_DIR = SKILL_DIR / "examples" / "chickadee-camera-observation-contract"
GENERATOR = SKILL_DIR / "scripts" / "generate_chickadee_packet.py"
SKILL_MD = SKILL_DIR / "SKILL.md"
BIRD_BATH_REFERENCE = SKILL_DIR / "references" / "bird-bath-balcony.md"
BAT_BEE_REFERENCE = (
    SKILL_DIR / "references" / "bat-bee-observation-hive-welfare.md"
)
WELFARE_GATE_SCHEMA = SKILL_DIR / "references" / "welfare-gate-schema.md"
CAMERA_VALIDATOR = SKILL_DIR / "scripts" / "validate_camera_modes.py"
OBSERVATION_HIVE_PREFLIGHT_GATES = (
    SKILL_DIR / "references" / "observation-hive-preflight-gates.json"
)
BAT_PACKET_DIR = SKILL_DIR / "examples" / "temperate-na-four-chamber-bat-house"
BAT_GENERATOR = SKILL_DIR / "scripts" / "generate_bat_house_packet.py"


REQUIRED_WELFARE_GATES = {
    "no_perch",
    "no_interior_finish",
    "drainage",
    "ventilation",
    "fledgling_grip",
    "predator_baffle",
    "cleanout_access",
}

REQUIRED_PACKET_FILES = {
    "README.md",
    "geometry_params.json",
    "cut-list.md",
    "BOM.md",
    "validation-checklist.md",
    "safety-notes.md",
    "agent-record.md",
    "chickadee-panels.svg",
}

REQUIRED_BAT_WELFARE_GATES = {
    "four_chambers",
    "roost_gap",
    "roughened_landing",
    "venting",
    "clear_drop_space",
    "no_mesh",
    "no_interior_finish",
    "no_treated_interior_lumber",
    "tree_mount_discouraged",
    "maintenance_timing",
}

REQUIRED_BAT_PACKET_FILES = {
    "README.md",
    "geometry_params.json",
    "cut-list.md",
    "BOM.md",
    "mounting-worksheet.md",
    "validation-checklist.md",
    "validation-report.schema.json",
    "validation-report.json",
    "safety-notes.md",
    "agent-record.md",
    "generated-cut-list.csv",
    "four-chamber-bat-house-layout.svg",
}


class TestGeometryParams(unittest.TestCase):
    """The JSON parameter file is the single source of truth."""

    def setUp(self) -> None:
        self.params = json.loads((PACKET_DIR / "geometry_params.json").read_text())

    def test_schema_version(self) -> None:
        self.assertEqual(self.params.get("schema_version"), "1.0")
        self.assertEqual(self.params.get("skill"), "habitat-maker")

    def test_target_species_listed(self) -> None:
        species = self.params.get("target_species", [])
        self.assertGreaterEqual(len(species), 1)
        self.assertTrue(any("Chickadee" in s for s in species))

    def test_references_have_urls(self) -> None:
        refs = self.params.get("references", [])
        self.assertGreaterEqual(len(refs), 1)
        for r in refs:
            self.assertIn("url", r)
            self.assertTrue(r["url"].startswith("http"))

    def test_at_least_two_material_profiles(self) -> None:
        material = self.params.get("material", {})
        self.assertIn("primary", material)
        self.assertIn("alternate", material)

    def test_all_welfare_gates_present(self) -> None:
        gates = set(self.params.get("welfare_gates", {}).keys())
        missing = REQUIRED_WELFARE_GATES - gates
        self.assertFalse(missing, f"missing welfare gates: {missing}")

    def test_derived_panel_geometry_consistency(self) -> None:
        """Spot-check derived dimensions against their stated formulas."""
        d = self.params["derived_panel_geometry_mm"]
        t = d["panel_thickness"]
        floor_int = d["floor_interior"]
        # box_exterior should be floor_interior + 2 * panel_thickness
        self.assertAlmostEqual(d["box_exterior"], floor_int + 2 * t, places=3)
        # back_panel_box_h = interior_height + 2 * panel_thickness
        # interior_height comes from cavity_dimensions_mm
        cav = self.params["cavity_dimensions_mm"]
        self.assertAlmostEqual(
            d["back_panel_box_h"],
            cav["interior_height_floor_to_roof_underside"] + 2 * t,
            places=3,
        )
        # entrance_above_floor mirrors cavity input
        self.assertAlmostEqual(
            d["entrance_above_floor"],
            cav["entrance_center_above_interior_floor_top"],
            places=3,
        )


class TestGenerator(unittest.TestCase):
    """The generator must regenerate the SVG from the JSON deterministically."""

    def test_generator_runs_and_writes_svg(self) -> None:
        # Generate into a tmpdir copy so we don't rely on / overwrite the
        # committed chickadee-panels.svg during tests.
        with tempfile.TemporaryDirectory() as tmp:
            tmp_packet = Path(tmp) / "chickadee"
            shutil.copytree(PACKET_DIR, tmp_packet)
            (tmp_packet / "chickadee-panels.svg").unlink(missing_ok=True)

            result = subprocess.run(
                [sys.executable, str(GENERATOR), "--packet", str(tmp_packet)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0,
                             f"generator exit={result.returncode}; "
                             f"stderr={result.stderr}")
            out = tmp_packet / "chickadee-panels.svg"
            self.assertTrue(out.is_file())
            self.assertGreater(out.stat().st_size, 1000)

            # Parse the SVG and confirm all 8 panel groups present
            tree = ET.parse(out)
            root = tree.getroot()
            ns = {"svg": "http://www.w3.org/2000/svg"}
            group_ids = {g.get("id") for g in root.findall(".//svg:g", ns) if g.get("id")}
            expected = {"front", "back", "sideL", "sideR", "floor",
                        "roof", "kerf", "guard"}
            self.assertEqual(group_ids, expected,
                             f"unexpected group ids: {group_ids}")


class TestPacketShape(unittest.TestCase):
    """Every required artifact is present in the canonical example."""

    def test_required_files_present(self) -> None:
        present = {p.name for p in PACKET_DIR.iterdir() if p.is_file()}
        missing = REQUIRED_PACKET_FILES - present
        self.assertFalse(missing, f"missing required files: {missing}")


class TestBirdBathReference(unittest.TestCase):
    """Bird-bath prompts must route to welfare-first balcony guidance."""

    def setUp(self) -> None:
        self.skill = SKILL_MD.read_text()
        self.skill_one_line = " ".join(self.skill.split())
        self.reference = BIRD_BATH_REFERENCE.read_text()

    def test_skill_routes_bird_bath_prompts(self) -> None:
        self.assertIn("design a balcony bird bath", self.skill)
        self.assertIn("Bird-bath and balcony packet contract", self.skill)
        self.assertIn("references/bird-bath-balcony.md", self.skill)
        self.assertIn(
            "do not need `geometry_params.json` unless the output includes machine-driven",
            self.skill_one_line,
        )

    def test_required_welfare_gates_present(self) -> None:
        required = [
            "Shallow depth",
            "Textured footing",
            "Escape path",
            "Dump/scrub cadence",
            "Mosquito prevention",
            "Water-contact material safety",
            "Heat/evaporation",
            "Stability",
        ]
        for term in required:
            self.assertIn(term, self.reference)

    def test_balcony_renter_checks_present(self) -> None:
        required = [
            "No-drill anchoring",
            "Wind/tip resistance",
            "Drip control",
            "Window-strike posture",
            "Railing/neighbor constraints",
            "Travel-dry behavior",
        ]
        for term in required:
            self.assertIn(term, self.reference)

    def test_material_safety_matrix_covers_issue_scope(self) -> None:
        required = [
            "Lead-free ceramic/glaze",
            "Concrete",
            "Natural stone",
            "BPA-free hard plastic",
            "Stainless steel",
            "Copper alloys",
            "Galvanized metal",
            "Treated wood",
            "Paint/sealer",
            "Unknown glaze",
        ]
        for term in required:
            self.assertIn(term, self.reference)

    def test_fill_depth_gauge_template_present(self) -> None:
        self.assertIn("Optional Fill-Depth Gauge Template", self.reference)
        self.assertIn("3/4 in    maximum fill line", self.reference)
        self.assertIn("1 in      reject", self.reference)


class TestBatBeeObservationHiveReference(unittest.TestCase):
    """Bat, bee, observation-hive, and electronics prompts get welfare gates."""

    def setUp(self) -> None:
        self.skill = SKILL_MD.read_text()
        self.reference = BAT_BEE_REFERENCE.read_text()

    def test_skill_routes_new_prompt_types(self) -> None:
        required = [
            "review bat house welfare gates",
            "native bee house",
            "observation hive design review",
            "camera in an observation hive",
            "Bat, bee, observation-hive, and electronics welfare contract",
            "references/bat-bee-observation-hive-welfare.md",
        ]
        for term in required:
            self.assertIn(term, self.skill)

    def test_bat_house_gates_present(self) -> None:
        required = [
            "Rough landing and roost surfaces",
            "Chamber spacing",
            "Heat and sun posture",
            "Predator exclusion",
            "Untreated interior",
            "Exterior-only weatherproofing",
            "Mounting stability",
            "Clear drop space",
            "Venting and moisture",
            "Seasonal disturbance",
        ]
        for term in required:
            self.assertIn(term, self.reference)

    def test_four_chamber_is_example_scope_not_universal_requirement(self) -> None:
        required_skill_terms = [
            "A four-chamber layout is a",
            "not a universal requirement",
            "choose chamber count from",
        ]
        for term in required_skill_terms:
            self.assertIn(term, self.skill)

        required_reference_terms = [
            "Bat-house example scope",
            "chamber count is not a default",
            "Do not let the canonical example layout substitute",
        ]
        for term in required_reference_terms:
            self.assertIn(term, self.reference)

    def test_bat_house_round11_tightening_present(self) -> None:
        required = [
            "without mesh or snag-prone liners",
            "climate/site preset",
            "tree mounts are discouraged",
            "mount type",
            "service calendar",
            "seasonal disturbance windows",
        ]
        for term in required:
            self.assertIn(term, self.reference)

    def test_native_bee_gates_present(self) -> None:
        required = [
            "Native solitary bee scope",
            "Tunnel diameter and depth",
            "Smooth tunnel interiors",
            "Dry overhang",
            "Replaceable media",
            "Parasite and mold management",
            "Chemical avoidance",
            "Predator and pest posture",
        ]
        for term in required:
            self.assertIn(term, self.reference)

    def test_observation_hive_preflight_gates_present(self) -> None:
        required = [
            "Qualified keeper review",
            "Secure containment",
            "Ventilation and thermal management",
            "Escape-proof service access",
            "Public and privacy safety",
            "Route-out decisions",
        ]
        for term in required:
            self.assertIn(term, self.reference)

    def test_camera_electronics_caveats_present(self) -> None:
        required = [
            "No contact protrusions",
            "No exposed wires",
            "Low heat load",
            "Weatherproof external routing",
            "Service without disturbance",
            "Species-safe sensing",
            "Fabrication authority",
        ]
        for term in required:
            self.assertIn(term, self.reference)

    def test_reusable_gate_record_shape_present(self) -> None:
        required = [
            "Reusable Gate Record Shape",
            "`gate_id`",
            "`label`",
            "`applies_to`",
            "`severity`",
            "`pass_condition`",
            "`fail_remedy`",
            "`evidence`",
            "`source_ref`",
            "habitat-reference",
            "Do not drop a welfare gate",
        ]
        for term in required:
            self.assertIn(term, self.reference)


class TestWelfareGateSchemaReference(unittest.TestCase):
    """Shared welfare gates must stay machine-readable enough to reuse."""

    def setUp(self) -> None:
        self.skill = SKILL_MD.read_text()
        self.reference = WELFARE_GATE_SCHEMA.read_text()

    def test_skill_routes_to_shared_welfare_schema(self) -> None:
        self.assertIn("references/welfare-gate-schema.md", self.skill)
        self.assertIn("habitat-reference", self.skill)
        self.assertIn("geometry_params.json", self.skill)

    def test_reference_defines_required_fields(self) -> None:
        required = [
            "`gate_id`",
            "`label`",
            "`applies_to`",
            "`severity`",
            "`pass_condition`",
            "`fail_remedy`",
            "`evidence`",
            "`source_ref`",
        ]
        for term in required:
            self.assertIn(term, self.reference)

    def test_reference_preserves_cavity_baseline_gates(self) -> None:
        for gate_id in REQUIRED_WELFARE_GATES:
            self.assertIn(f"`{gate_id}`", self.reference)

    def test_reference_documents_habitat_reference_workflow(self) -> None:
        self.assertIn("Habitat-reference workflow", self.reference)
        self.assertIn("habitat-reference", self.reference)
        self.assertIn("drop a gate", self.reference)

    def test_reference_connects_concrete_gate_families(self) -> None:
        required = [
            "`bat_house`",
            "`clear_drop_space`",
            "`venting_moisture`",
            "`no_mesh`",
            "`tree_mount_discouraged`",
            "`native_bee_house`",
            "`observation_hive_preflight`",
            "`camera_electronics`",
            "`fabrication_authority`",
            "private family/media details",
        ]
        for term in required:
            self.assertIn(term, self.reference)

    def test_bat_house_schema_keeps_makerspace_downstream(self) -> None:
        required = [
            "Keep `habitat-maker` as the first owner",
            "route downstream DXF/CNC, fastener, and workholding details to `makerspace`",
            "preserve unknowns instead of inventing dimensions",
            "climate/site",
            "mount type",
            "service calendar",
        ]
        for term in required:
            self.assertIn(term, self.reference)

    def test_skill_routes_preflight_without_colony_operations(self) -> None:
        required = [
            "native bee house",
            "observation hive design preflight",
            "camera/electronics prompts use the same welfare-gate schema",
            "colony management, legal compliance, or live",
            "fabrication authority",
        ]
        for term in required:
            self.assertIn(term, self.skill)

class TestCameraObservationContract(unittest.TestCase):
    """Camera-mode packets declare welfare-critical mode and manifest data."""

    def setUp(self) -> None:
        self.params = json.loads((CAMERA_PACKET_DIR / "geometry_params.json").read_text())

    def test_camera_mode_enum_and_secondary_mode(self) -> None:
        obs = self.params["camera_observation"]
        self.assertEqual(obs["mode"], "interior_plus_exterior_approach")
        self.assertEqual(obs["primary"]["mode"], "interior_view")
        self.assertTrue(obs["secondary"]["enabled"])
        self.assertEqual(obs["secondary"]["mode"], "exterior_approach")

    def test_camera_welfare_gates_present(self) -> None:
        gates = set(self.params.get("welfare_gates", {}).keys())
        expected = {
            "electronics_isolation",
            "interior_heat",
            "interior_light",
            "moisture_control",
            "cable_routing",
            "service_independence",
            "non_disturbance",
        }
        self.assertFalse(expected - gates)

    def test_camera_validator_accepts_example(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CAMERA_VALIDATOR), "--packet", str(CAMERA_PACKET_DIR)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("camera-mode validation passed", result.stdout)

    def test_camera_validator_rejects_unknown_mode(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "validate_camera_modes", CAMERA_VALIDATOR
        )
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        bad = dict(self.params)
        bad["camera_observation"] = dict(self.params["camera_observation"])
        bad["camera_observation"]["mode"] = "nestcam_surprise"

        with mock.patch.object(module, "load_json", return_value=bad):
            findings = module.validate_packet(CAMERA_PACKET_DIR)
        self.assertTrue(any("camera_observation.mode" == f.path for f in findings))



class TestObservationHivePreflightGateContract(unittest.TestCase):
    """Observation-hive packets need a concrete preflight gate contract."""

    REQUIRED_GATE_IDS = {
        "qualified_keeper_review",
        "secure_containment",
        "ventilation_thermal_management",
        "escape_proof_service_access",
        "public_privacy_safety",
        "route_out_colony_decisions",
    }

    REQUIRED_GATE_FIELDS = {
        "gate_id",
        "label",
        "applies_to",
        "severity",
        "pass_condition",
        "fail_remedy",
        "evidence",
        "source_ref",
    }

    def setUp(self) -> None:
        self.skill = SKILL_MD.read_text()
        self.reference = BAT_BEE_REFERENCE.read_text()
        self.contract = json.loads(OBSERVATION_HIVE_PREFLIGHT_GATES.read_text())

    def test_skill_and_reference_point_to_contract(self) -> None:
        self.assertIn("observation-hive-preflight-gates.json", self.skill)
        self.assertIn("observation-hive-preflight-gates.json", self.reference)

    def test_contract_declares_required_gate_ids(self) -> None:
        self.assertEqual(
            set(self.contract["required_gate_ids"]),
            self.REQUIRED_GATE_IDS,
        )
        gate_ids = {gate["gate_id"] for gate in self.contract["gates"]}
        self.assertEqual(gate_ids, self.REQUIRED_GATE_IDS)

    def test_contract_preserves_welfare_gate_record_shape(self) -> None:
        for gate in self.contract["gates"]:
            missing = self.REQUIRED_GATE_FIELDS - set(gate)
            self.assertFalse(missing, f"{gate['gate_id']} missing {missing}")
            self.assertEqual(gate["severity"], "required")
            self.assertEqual(gate["applies_to"], ["observation_hive_preflight"])
            self.assertIsInstance(gate["source_ref"], list)
            self.assertTrue(gate["pass_condition"].strip())
            self.assertTrue(gate["fail_remedy"].strip())

    def test_contract_blocks_live_colony_claims(self) -> None:
        label = self.contract["readiness_label"]
        self.assertIn("concept/preflight only", label)
        self.assertIn("not approved for live colony use", label)
        route_out = " ".join(self.contract["route_out_topics"])
        for term in [
            "live colony handling",
            "legal compliance",
            "feeding",
            "disease response",
            "queen status",
            "private family or media details",
        ]:
            self.assertIn(term, route_out)

    def test_contract_keeps_camera_electronics_external_by_default(self) -> None:
        electronics = self.contract["camera_electronics_default"]
        self.assertEqual(
            electronics["default_posture"],
            "external observation only for v1",
        )
        for gate_id in [
            "no_contact_protrusions",
            "no_exposed_wires",
            "low_heat_load",
            "weatherproof_external_routing",
            "service_without_disturbance",
            "species_safe_sensing",
            "fabrication_authority",
        ]:
            self.assertIn(gate_id, electronics["required_if_electronics_present"])


class TestBatHouseGeometryParams(unittest.TestCase):
    """The bat-house JSON must carry bat-specific welfare and site rules."""

    def setUp(self) -> None:
        self.params = json.loads((BAT_PACKET_DIR / "geometry_params.json").read_text())

    def test_schema_version(self) -> None:
        self.assertEqual(self.params.get("schema_version"), "1.0")
        self.assertEqual(self.params.get("skill"), "habitat-maker")
        self.assertEqual(self.params.get("packet"), "temperate-na-four-chamber-bat-house")

    def test_references_have_urls(self) -> None:
        refs = self.params.get("references", [])
        self.assertGreaterEqual(len(refs), 2)
        for r in refs:
            self.assertIn("url", r)
            self.assertTrue(r["url"].startswith("http"))

    def test_all_bat_welfare_gates_present(self) -> None:
        gates = set(self.params.get("welfare_gates", {}).keys())
        missing = REQUIRED_BAT_WELFARE_GATES - gates
        self.assertFalse(missing, f"missing bat welfare gates: {missing}")

    def test_four_chamber_geometry_consistency(self) -> None:
        chamber = self.params["chamber_geometry_mm"]
        self.assertEqual(chamber["chamber_count"], 4)
        self.assertGreaterEqual(chamber["clear_chamber_depth_each"], 19)
        self.assertLessEqual(chamber["clear_chamber_depth_each"], 25)
        self.assertGreaterEqual(
            chamber["landing_extension_below_lower_front"],
            self.params["validation_targets"]["minimum_landing_extension_mm"],
        )
        self.assertFalse(self.params["validation_targets"]["mesh_allowed"])
        self.assertFalse(self.params["validation_targets"]["interior_finish_allowed"])

    def test_climate_and_mounting_presets(self) -> None:
        profiles = self.params["climate_profiles"]
        self.assertIn("cool_to_mild", profiles)
        self.assertIn("warm", profiles)
        self.assertIn("very_hot", profiles)
        mounting = self.params["mounting"]
        self.assertFalse(mounting["tree_mount_recommended"])
        self.assertGreaterEqual(mounting["minimum_clear_drop_below_ft"], 12)


class TestBatHouseGenerator(unittest.TestCase):
    """The bat-house generator must refresh generated artifacts from JSON."""

    def test_generator_runs_and_writes_svg_and_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_packet = Path(tmp) / "bat-house"
            shutil.copytree(BAT_PACKET_DIR, tmp_packet)
            (tmp_packet / "four-chamber-bat-house-layout.svg").unlink(missing_ok=True)
            (tmp_packet / "generated-cut-list.csv").unlink(missing_ok=True)

            result = subprocess.run(
                [sys.executable, str(BAT_GENERATOR), "--packet", str(tmp_packet)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0,
                             f"generator exit={result.returncode}; "
                             f"stderr={result.stderr}")

            svg_out = tmp_packet / "four-chamber-bat-house-layout.svg"
            csv_out = tmp_packet / "generated-cut-list.csv"
            self.assertTrue(svg_out.is_file())
            self.assertTrue(csv_out.is_file())
            self.assertGreater(svg_out.stat().st_size, 1000)
            self.assertIn("back_panel", csv_out.read_text())

            tree = ET.parse(svg_out)
            root = tree.getroot()
            ns = {"svg": "http://www.w3.org/2000/svg"}
            group_ids = {g.get("id") for g in root.findall(".//svg:g", ns) if g.get("id")}
            expected = {
                "back_panel",
                "upper_front_panel",
                "lower_front_panel",
                "roof_panel",
                "side_wall",
                "partition",
                "side_spacer_strip",
                "top_spacer_strip",
                "building_mount_batten_optional",
            }
            self.assertEqual(group_ids, expected,
                             f"unexpected group ids: {group_ids}")
            side_wall = root.find(".//svg:g[@id='side_wall']", ns)
            self.assertIsNotNone(side_wall)
            side_vents = [
                elem for elem in side_wall.findall(".//svg:rect", ns)
                if "side-vent-slot" in (elem.get("class") or "")
            ]
            self.assertEqual(len(side_vents), 1)
            self.assertGreater(float(side_vents[0].get("width", "0")), 0)
            self.assertGreater(float(side_vents[0].get("height", "0")), 0)


class TestBatHousePacketShape(unittest.TestCase):
    """Every required artifact is present in the bat-house example."""

    def test_required_files_present(self) -> None:
        present = {p.name for p in BAT_PACKET_DIR.iterdir() if p.is_file()}
        missing = REQUIRED_BAT_PACKET_FILES - present
        self.assertFalse(missing, f"missing required files: {missing}")

    def test_validation_report_shape(self) -> None:
        schema = json.loads((BAT_PACKET_DIR / "validation-report.schema.json").read_text())
        report = json.loads((BAT_PACKET_DIR / "validation-report.json").read_text())
        for key in schema["required"]:
            self.assertIn(key, report)
        self.assertIn(report["result"], {"pass", "fail", "pending_site"})
        self.assertGreaterEqual(len(report["gates"]), 6)
        for gate in report["gates"]:
            self.assertIn("id", gate)
            self.assertIn("status", gate)
            self.assertIn(gate["status"], {"pass", "fail", "pending_site"})
            self.assertIn("evidence", gate)


if __name__ == "__main__":
    unittest.main()
