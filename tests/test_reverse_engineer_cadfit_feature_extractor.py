#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "maker"
    / "skills"
    / "reverse-engineer"
    / "scripts"
    / "cadfit_feature_extractor.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("cadfit_feature_extractor", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["cadfit_feature_extractor"] = module
    spec.loader.exec_module(module)
    return module


extractor = load_module()


class CadfitFeatureExtractorTests(unittest.TestCase):
    def test_extracts_structured_candidate_menu_from_mesh_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mesh = Path(tmp) / "part.stl"
            mesh.write_text("solid test\nendsolid test\n", encoding="utf-8")
            result = extractor.extract_features(
                mesh,
                {
                    "watertight": True,
                    "bbox": {"x": 120, "y": 80, "z": 30},
                    "units": "mm",
                    "symmetry_axes": ["z"],
                    "planar_sections": [{"axis": "z", "offset": 0, "profile": "rounded_rectangle"}],
                },
            )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["mesh"]["extension"], ".stl")
        self.assertEqual(result["candidate_sketch_profiles"][0]["profile"], "long_extrusion")
        self.assertEqual(result["slicing_planes"][0]["profile"], "rounded_rectangle")
        self.assertEqual(result["revolution_axes"][0]["vector"], [0.0, 0.0, 1.0])

    def test_missing_mesh_degrades_with_actionable_finding(self) -> None:
        result = extractor.extract_features(None, {})
        self.assertEqual(result["status"], "degraded")
        self.assertTrue(any("no mesh_path supplied" in finding for finding in result["findings"]))
        self.assertEqual(result["candidate_sketch_profiles"], [])

    def test_non_watertight_mesh_degrades_without_dropping_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mesh = Path(tmp) / "part.obj"
            mesh.write_text("# obj\n", encoding="utf-8")
            result = extractor.extract_features(
                mesh,
                {"watertight": False, "bbox": {"x": 10, "y": 10, "z": 10}, "symmetry_axes": ["x"]},
            )

        self.assertEqual(result["status"], "degraded")
        self.assertTrue(any("watertight=false" in finding for finding in result["findings"]))
        self.assertEqual(result["candidate_sketch_profiles"][0]["profile"], "cube_like")

    def test_unsupported_extension_is_rejected_as_degraded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mesh = Path(tmp) / "part.txt"
            mesh.write_text("not a mesh", encoding="utf-8")
            result = extractor.extract_features(mesh, {})
        self.assertEqual(result["status"], "degraded")
        self.assertTrue(any("unsupported mesh extension" in finding for finding in result["findings"]))


if __name__ == "__main__":
    unittest.main()
