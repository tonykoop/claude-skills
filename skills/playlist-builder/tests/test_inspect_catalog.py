#!/usr/bin/env python3
"""Tests for the catalog/auth-state preflight.

Run from anywhere:

    python3 skills/playlist-builder/tests/test_inspect_catalog.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "inspect_catalog.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("inspect_catalog", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["inspect_catalog"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class InspectCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_module()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.skill_dir = Path(self.tmp.name)
        (self.skill_dir / "seed-banks").mkdir()
        (self.skill_dir / "references").mkdir()
        # baseline: all banks empty arrays
        for b in "ABCDE":
            (self.skill_dir / "seed-banks" / f"{b}.json").write_text("[]")
        # baseline: scrub auth env
        for env in ("SPOTIFY_ACCESS_TOKEN", "SPOTIPY_CLIENT_ID",
                    "SPOTIPY_CLIENT_SECRET", "SOUNDCLOUD_OAUTH_TOKEN",
                    "SOUNDCLOUD_CLIENT_ID"):
            os.environ.pop(env, None)

    # ---------- mode selection ----------

    def test_manual_curation_when_everything_empty(self) -> None:
        report = self.mod.build_report(self.skill_dir, None)
        self.assertEqual(report["recommended_output_mode"], "manual-curation")
        self.assertFalse(report["platform_auth_available"])
        self.assertEqual(report["seed_banks"]["total_count"], 0)

    def test_sparse_when_one_track_in_bundled_no_mode_b(self) -> None:
        track = {
            "title": "Weightless",
            "artist": "Marconi Union",
            "spotify_uri": "spotify:track:5oLh8s49fbTuxKBL5n8sHE",
            "duration_ms": 488000,
        }
        (self.skill_dir / "seed-banks" / "A.json").write_text(
            json.dumps([track])
        )
        report = self.mod.build_report(self.skill_dir, None)
        self.assertEqual(report["recommended_output_mode"], "sparse")
        self.assertEqual(report["seed_banks"]["counts"]["A"], 1)

    def test_search_assisted_when_mode_b_loaded(self) -> None:
        (self.skill_dir / "references" / "CATALOG_TONY_KOOP.md").write_text(
            "# Tony catalog placeholder\n"
        )
        report = self.mod.build_report(self.skill_dir, None)
        self.assertEqual(report["recommended_output_mode"], "search-assisted")
        self.assertTrue(report["mode_b_tony_catalog"]["loaded"])

    def test_verified_when_bank_is_rich(self) -> None:
        rich = [
            {"title": f"T{i}", "artist": "A",
             "spotify_uri": f"spotify:track:{i:022d}"}
            for i in range(8)
        ]
        (self.skill_dir / "seed-banks" / "A.json").write_text(
            json.dumps(rich)
        )
        report = self.mod.build_report(self.skill_dir, None)
        self.assertEqual(report["recommended_output_mode"], "verified")
        self.assertTrue(report["seed_banks"]["any_bank_rich"])

    def test_verified_when_auth_env_present(self) -> None:
        os.environ["SPOTIFY_ACCESS_TOKEN"] = "fake"
        try:
            report = self.mod.build_report(self.skill_dir, None)
            self.assertEqual(report["recommended_output_mode"], "verified")
            self.assertTrue(report["platform_auth_available"])
            self.assertIn("env:SPOTIFY_ACCESS_TOKEN",
                          report["auth"]["spotify_signals"])
        finally:
            os.environ.pop("SPOTIFY_ACCESS_TOKEN")

    def test_verified_when_user_catalog_has_30_plus_tracks(self) -> None:
        catalog_path = self.skill_dir / "user_catalog.json"
        catalog = {"A": [{"title": f"T{i}"} for i in range(30)]}
        catalog_path.write_text(json.dumps(catalog))
        report = self.mod.build_report(self.skill_dir, catalog_path)
        self.assertEqual(report["recommended_output_mode"], "verified")
        self.assertTrue(report["user_catalog"]["loaded"])

    # ---------- robustness ----------

    def test_malformed_seed_bank_does_not_crash(self) -> None:
        (self.skill_dir / "seed-banks" / "B.json").write_text("not json")
        report = self.mod.build_report(self.skill_dir, None)
        self.assertIn("B", report["seed_banks"]["malformed_files"])
        # malformed counts as 0; total is still 0; mode is manual-curation
        self.assertEqual(report["recommended_output_mode"], "manual-curation")

    def test_missing_seed_bank_file_counts_as_zero(self) -> None:
        (self.skill_dir / "seed-banks" / "A.json").unlink()
        report = self.mod.build_report(self.skill_dir, None)
        self.assertEqual(report["seed_banks"]["counts"]["A"], 0)
        self.assertNotIn("A", report["seed_banks"]["malformed_files"])

    # ---------- schema contract ----------

    def test_report_has_required_top_level_fields(self) -> None:
        report = self.mod.build_report(self.skill_dir, None)
        for key in ("schema_version", "skill_dir", "seed_banks",
                    "mode_b_tony_catalog", "auth", "user_catalog",
                    "recommended_output_mode", "mode_explanation",
                    "platform_auth_available"):
            self.assertIn(key, report, f"missing top-level key: {key}")

    def test_mode_explanation_is_non_empty_for_every_mode(self) -> None:
        for mode in ("verified", "search-assisted", "sparse",
                     "manual-curation"):
            text = self.mod.explain_mode(mode)
            self.assertTrue(text and len(text) > 20,
                            f"explanation for {mode} too short")


if __name__ == "__main__":
    unittest.main()
