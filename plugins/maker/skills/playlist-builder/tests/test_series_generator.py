#!/usr/bin/env python3
"""Tests for generate_series.py — story #420.

Run from anywhere:
    python3 plugins/maker/skills/playlist-builder/tests/test_series_generator.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "generate_series.py"
)
CONTEXTS_DIR = Path(__file__).resolve().parent.parent / "contexts"
SERIES_CTX = CONTEXTS_DIR / "series" / "4week-yoga-progression.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("generate_series", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["generate_series"] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_catalog(n_per_bank: int = 5) -> dict:
    """Minimal catalog with tracks in all five banks."""
    banks: dict[str, list] = {}
    for bank in "ABCDE":
        banks[bank] = [
            {
                "artist": f"Artist-{bank}{i}",
                "title": f"Track {bank}{i}",
                "duration_ms": 300_000,
                "spotify_uri": f"spotify:track:{bank}{i}",
            }
            for i in range(n_per_bank)
        ]
    return {"banks": banks, "exclusions": []}


class TestSeriesGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.series = json.loads(SERIES_CTX.read_text(encoding="utf-8"))
        cls.catalog = _make_catalog(n_per_bank=8)

    # --- series context shape ---

    def test_series_has_four_episodes(self):
        self.assertEqual(len(self.series["episodes"]), 4)

    def test_episode_weeks_sequential(self):
        weeks = [ep["week"] for ep in self.series["episodes"]]
        self.assertEqual(weeks, [1, 2, 3, 4])

    def test_each_episode_has_phases(self):
        for ep in self.series["episodes"]:
            self.assertIn("phases", ep)
            self.assertGreater(len(ep["phases"]), 0)

    def test_bpm_scales_present(self):
        for ep in self.series["episodes"]:
            self.assertIn("bpm_scale", ep)
            self.assertIsInstance(ep["bpm_scale"], float)

    # --- episode generation ---

    def test_generate_episode_returns_tracks(self):
        ep = self.series["episodes"][0]
        excludes: set = set()
        playlist = self.mod.generate_episode(ep, self.catalog, excludes)
        self.assertGreater(len(playlist), 0)

    def test_generate_episode_updates_excludes(self):
        ep = self.series["episodes"][0]
        excludes: set = set()
        playlist = self.mod.generate_episode(ep, self.catalog, excludes)
        self.assertEqual(len(excludes), len(playlist))

    def test_no_cross_episode_repeats(self):
        excludes: set = set()
        all_ids = []
        for ep in self.series["episodes"]:
            playlist = self.mod.generate_episode(ep, self.catalog, excludes)
            ids = [self.mod._track_id(t) for t in playlist]
            all_ids.extend(ids)
        self.assertEqual(len(all_ids), len(set(all_ids)),
                         "Duplicate tracks found across episodes")

    def test_each_track_has_phase(self):
        ep = self.series["episodes"][1]
        excludes: set = set()
        playlist = self.mod.generate_episode(ep, self.catalog, excludes)
        for t in playlist:
            self.assertIn("phase", t)

    # --- full series generation ---

    def test_generate_series_writes_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "catalog.json"
            catalog_path.write_text(json.dumps(self.catalog))
            out = Path(tmpdir) / "out"
            self.mod.generate_series(SERIES_CTX, catalog_path, out, seed=42)
            files = list(out.iterdir())
            # 4 episode files + 1 summary
            self.assertGreaterEqual(len(files), 5)

    def test_summary_file_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "catalog.json"
            catalog_path.write_text(json.dumps(self.catalog))
            out = Path(tmpdir) / "out"
            self.mod.generate_series(SERIES_CTX, catalog_path, out, seed=1)
            summary = out / "series-summary.md"
            self.assertTrue(summary.exists())
            content = summary.read_text()
            self.assertIn("4-Week", content)

    def test_reproducible_with_seed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "catalog.json"
            catalog_path.write_text(json.dumps(self.catalog))
            out1 = Path(tmpdir) / "out1"
            out2 = Path(tmpdir) / "out2"
            self.mod.generate_series(SERIES_CTX, catalog_path, out1, seed=99)
            self.mod.generate_series(SERIES_CTX, catalog_path, out2, seed=99)
            for f in out1.iterdir():
                self.assertEqual(
                    f.read_text(),
                    (out2 / f.name).read_text(),
                    f"Non-deterministic output for {f.name}",
                )


if __name__ == "__main__":
    unittest.main()
