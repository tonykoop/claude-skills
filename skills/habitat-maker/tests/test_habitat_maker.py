"""
Smoke tests for habitat-maker v0.3.

Asserts:
  1. The canonical example's geometry_params.json parses, has the
     required schema sections, and declares all seven welfare gates.
  2. The generator script emits a chickadee-panels.svg that contains the
     expected panel groups and class layers.
  3. The example packet has all the files the v0.2 build-packet contract
     requires.

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


SKILL_DIR = Path(__file__).resolve().parent.parent
PACKET_DIR = SKILL_DIR / "examples" / "chickadee-laser-baltic-birch"
GENERATOR = SKILL_DIR / "scripts" / "generate_chickadee_packet.py"
SKILL_MD = SKILL_DIR / "SKILL.md"
BIRD_BATH_REFERENCE = SKILL_DIR / "references" / "bird-bath-balcony.md"


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
            group_ids = {g.get("id") for g in root.findall(".//svg:g", ns)}
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


if __name__ == "__main__":
    unittest.main()
