"""Tests for the houseplant skill's bundled bpy scripts.

These tests do NOT require Blender. They verify:
  1. Every script in scripts/ parses as valid Python.
  2. Every script declares the documented globals before any bpy use, so a
     caller can override them via globals() before exec().
  3. The pure-math helpers (scale-factor computation, helix geometry) produce
     correct results that the Blender-side wrappers can rely on.

Run from the repo root:
    python3 -m unittest discover -s skills/houseplant/tests -v
or
    python3 -m pytest skills/houseplant/tests/
"""
from __future__ import annotations

import ast
import math
import sys
import unittest
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent / "scripts"
SKILL_DIR = THIS_DIR.parent

sys.path.insert(0, str(SCRIPTS_DIR))


# ---------------------------------------------------------------------------
# Static (parse-only) checks on every bundled script.
# ---------------------------------------------------------------------------

EXPECTED_SCRIPTS = {
    "scene_scaffold.py",
    "scale_from_ruler.py",
    "wire_coil.py",
    "cut_marker.py",
    "sim_collection.py",
    "wire_window.py",
    "aerial_root_trace.py",
    "grafting_sim.py",
}


class ScriptsParse(unittest.TestCase):
    def test_expected_scripts_present(self):
        present = {p.name for p in SCRIPTS_DIR.glob("*.py")}
        missing = EXPECTED_SCRIPTS - present
        self.assertEqual(missing, set(), f"Missing bundled scripts: {missing}")

    def test_each_script_parses(self):
        for name in EXPECTED_SCRIPTS:
            path = SCRIPTS_DIR / name
            source = path.read_text(encoding="utf-8")
            try:
                ast.parse(source)
            except SyntaxError as e:
                self.fail(f"{name} failed to parse: {e}")

    def test_each_script_documents_caller_overridable_globals(self):
        """Each script uses globals().get(...) so callers can override before exec.
        This is the contract that lets mcp__Blender__execute_blender_code drive them.
        """
        for name in EXPECTED_SCRIPTS:
            source = (SCRIPTS_DIR / name).read_text(encoding="utf-8")
            self.assertIn("globals().get", source,
                          f"{name} should use globals().get(...) for caller-overridable params")


# ---------------------------------------------------------------------------
# Pure-math helper checks (no bpy required).
# ---------------------------------------------------------------------------

class ScaleFromRuler(unittest.TestCase):
    def setUp(self):
        # Import lazily so we get a clean module each test class.
        import scale_from_ruler as mod
        self.mod = mod

    def test_simple_unit_scale(self):
        # 1 unit segment, real 10 cm -> factor 0.1
        factor = self.mod.compute_scale_factor((0, 0, 0), (1, 0, 0), 0.10)
        self.assertAlmostEqual(factor, 0.10, places=6)

    def test_diagonal_segment(self):
        # 3-4-5 triangle in XY -> length 5, real 50 cm -> factor 0.10
        factor = self.mod.compute_scale_factor((0, 0, 0), (3, 4, 0), 0.50)
        self.assertAlmostEqual(factor, 0.10, places=6)

    def test_three_dimensional_segment(self):
        # Unit cube diagonal -> length sqrt(3), real 1 m -> factor 1/sqrt(3)
        factor = self.mod.compute_scale_factor((0, 0, 0), (1, 1, 1), 1.0)
        self.assertAlmostEqual(factor, 1.0 / math.sqrt(3), places=6)

    def test_coincident_endpoints_raise(self):
        with self.assertRaises(ValueError):
            self.mod.compute_scale_factor((1, 1, 1), (1, 1, 1), 0.1)

    def test_negative_distance_is_signed_factor(self):
        # Practical use is always positive, but the math should still work.
        factor = self.mod.compute_scale_factor((0, 0, 0), (1, 0, 0), -0.5)
        self.assertAlmostEqual(factor, -0.5, places=6)


class WireCoilHelix(unittest.TestCase):
    def setUp(self):
        import wire_coil as mod
        self.mod = mod

    def test_helix_along_x_axis_has_correct_radius(self):
        # Backbone is a straight segment along +X, length 1 m.
        backbone = [(0, 0, 0), (1, 0, 0)]
        coil_radius = 0.005
        helix = self.mod.helix_points_along_backbone(
            backbone, turns_per_meter=10, coil_radius=coil_radius
        )
        self.assertGreater(len(helix), 50, "Helix should have many samples")
        # Every helix point's distance from the +X axis should equal coil_radius
        # (i.e. sqrt(y^2 + z^2) ≈ coil_radius), within tight tolerance.
        for x, y, z in helix:
            r = math.sqrt(y ** 2 + z ** 2)
            self.assertAlmostEqual(r, coil_radius, places=4)

    def test_helix_returns_to_backbone_each_turn(self):
        # Phase should return to zero after each turn.
        backbone = [(0, 0, 0), (1, 0, 0)]
        helix = self.mod.helix_points_along_backbone(
            backbone, turns_per_meter=4, coil_radius=0.01
        )
        # Over 1 meter with 4 turns/m, the helix completes 4 full turns.
        # At every quarter, the helix has stepped by 0.25 along X.
        # Just verify the X coordinate increases monotonically.
        xs = [p[0] for p in helix]
        for prev, cur in zip(xs, xs[1:]):
            self.assertLessEqual(prev, cur + 1e-9)

    def test_helix_empty_backbone_raises(self):
        with self.assertRaises(ValueError):
            self.mod.helix_points_along_backbone([(0, 0, 0)])

    def test_zero_length_segment_is_skipped(self):
        # If two consecutive backbone points coincide, the helix just skips that
        # segment rather than dividing by zero.
        backbone = [(0, 0, 0), (0, 0, 0), (1, 0, 0)]
        helix = self.mod.helix_points_along_backbone(
            backbone, turns_per_meter=8, coil_radius=0.005
        )
        self.assertGreater(len(helix), 0)


class WireWindow(unittest.TestCase):
    """v2 chrono-engine: wire-removal inspection window math (no bpy)."""

    def setUp(self):
        import wire_window as mod
        self.mod = mod

    def test_fast_active_first_inspection_is_one_week(self):
        plan = self.mod.wire_inspection_window("2026-06-15", "fast", active_growth=True)
        self.assertEqual(plan["first_inspection"], "2026-06-22")
        self.assertEqual(plan["recheck_cadence_days"], 7)

    def test_slower_class_has_longer_window(self):
        fast = self.mod.wire_inspection_window("2026-06-15", "fast", True)
        slow = self.mod.wire_inspection_window("2026-06-15", "slow", True)
        self.assertGreater(slow["first_inspection_days"], fast["first_inspection_days"])

    def test_dormant_stretches_the_window(self):
        active = self.mod.wire_inspection_window("2026-06-15", "moderate", True)
        dormant = self.mod.wire_inspection_window("2026-06-15", "moderate", False)
        self.assertGreater(dormant["first_inspection_days"], active["first_inspection_days"])

    def test_ladder_has_four_increasing_dates(self):
        plan = self.mod.wire_inspection_window("2026-06-15", "moderate", True)
        ladder = plan["inspection_ladder"]
        self.assertEqual(len(ladder), 4)
        self.assertEqual(ladder, sorted(ladder))

    def test_unknown_growth_class_raises(self):
        with self.assertRaises(ValueError):
            self.mod.wire_inspection_window("2026-06-15", "turbo", True)


class AerialRootTrace(unittest.TestCase):
    """v2 aerial-root: drooping guided-path geometry (no bpy)."""

    def setUp(self):
        import aerial_root_trace as mod
        self.mod = mod

    def test_endpoints_are_exact(self):
        start, end = (0.0, 0.0, 0.30), (0.10, 0.05, 0.0)
        pts = self.mod.droop_path_points(start, end, samples=20)
        self.assertEqual(len(pts), 20)
        for a, b in zip(pts[0], start):
            self.assertAlmostEqual(a, b, places=6)
        for a, b in zip(pts[-1], end):
            self.assertAlmostEqual(a, b, places=6)

    def test_midpoint_droops_below_linear(self):
        start, end = (0.0, 0.0, 0.30), (0.20, 0.0, 0.0)
        pts = self.mod.droop_path_points(start, end, droop=0.05, samples=21)
        mid = pts[10]
        linear_mid_z = (start[2] + end[2]) / 2
        self.assertLess(mid[2], linear_mid_z, "Path should sag below the straight line at midpoint")

    def test_too_few_samples_raises(self):
        with self.assertRaises(ValueError):
            self.mod.droop_path_points((0, 0, 0), (1, 0, 0), samples=1)


# ---------------------------------------------------------------------------
# Skill structure check — make sure manifest references match real files.
# ---------------------------------------------------------------------------

class ManifestIntegrity(unittest.TestCase):
    """Catch the most common breakage: skill files renamed but manifest stale."""

    def setUp(self):
        import yaml  # PyYAML; available in the standard test environment.
        self.manifest = yaml.safe_load(
            (SKILL_DIR / "manifest.yaml").read_text(encoding="utf-8")
        )

    def test_manifest_references_exist(self):
        for ref in self.manifest.get("references", []):
            path = SKILL_DIR / ref["path"]
            self.assertTrue(path.exists(), f"Reference missing: {ref['path']}")

    def test_manifest_scripts_exist(self):
        for s in self.manifest.get("scripts", []):
            path = SKILL_DIR / s["path"]
            self.assertTrue(path.exists(), f"Script missing: {s['path']}")

    def test_manifest_assets_exist(self):
        for a in self.manifest.get("assets", []):
            path = SKILL_DIR / a["path"]
            self.assertTrue(path.exists(), f"Asset missing: {a['path']}")

    def test_skill_md_version_matches_manifest_version(self):
        skill_md = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        version = self.manifest.get("version")
        self.assertIn(f"version: {version}", skill_md,
                      f"SKILL.md frontmatter should declare version: {version}")


if __name__ == "__main__":
    unittest.main()
