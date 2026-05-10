"""Tests for generate_folded_drone_dxf.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent / "scripts"
EXAMPLES_DIR = THIS_DIR.parent / "examples" / "folded-drone"

sys.path.insert(0, str(SCRIPTS_DIR))

import generate_folded_drone_dxf as g  # noqa: E402


class FoldedDroneDxfTests(unittest.TestCase):
    def test_example_fixture_generates_required_layers_and_notes(self):
        csv_path = EXAMPLES_DIR / "centerline-stations.csv"
        stations = g.load_stations(csv_path, default_height_mm=42.0)
        summary = g.build_summary(
            stations,
            target_hz=82.41,
            playing_temperature_c=33.0,
            room_temperature_c=20.0,
            tuning_tail_mm=180.0,
        )
        dxf = g.generate_dxf(stations, csv_path.name, summary)

        self.assertIn("$INSUNITS", dxf)
        self.assertIn("\n70\n4\n", dxf)
        for layer in g.DXF_LAYERS:
            self.assertIn(layer, dxf)
        self.assertIn("Warm straight reference", dxf)
        self.assertIn("Leak-test before and after finish", dxf)
        self.assertIn("Breath path requires cured non-toxic finish", dxf)
        self.assertIn("Reserve 180 mm removable/trim tail", dxf)

    def test_fixture_length_matches_e2_target_plus_tuning_tail(self):
        csv_path = EXAMPLES_DIR / "centerline-stations.csv"
        stations = g.load_stations(csv_path, default_height_mm=42.0)
        summary = g.build_summary(
            stations,
            target_hz=82.41,
            playing_temperature_c=33.0,
            room_temperature_c=20.0,
            tuning_tail_mm=180.0,
        )
        expected_untrimmed = (
            summary.warm_straight_reference_length_mm + summary.tuning_tail_mm
        )
        self.assertAlmostEqual(
            summary.centerline_length_mm, expected_untrimmed, delta=20.0)

    def test_equivalent_diameter_uses_rectangular_area(self):
        d_eq = g.equivalent_diameter_mm(52.0, 42.0)
        self.assertAlmostEqual(d_eq, 52.73, places=2)

    def test_wall_points_are_continuous_at_fold_joins(self):
        csv_path = EXAMPLES_DIR / "centerline-stations.csv"
        stations = g.load_stations(csv_path, default_height_mm=42.0)
        for side in (1.0, -1.0):
            wall = g.continuous_wall_points(stations, side)
            self.assertEqual(len(wall), len(stations))
            for point in wall:
                self.assertTrue(all(isinstance(coord, float) for coord in point))

            # A 90-degree bend should miter to one shared point, not leave
            # separate previous-end and next-start offsets.
            prev_start, prev_end = g.offset_segment_points(
                stations[0], stations[1], side)
            next_start, next_end = g.offset_segment_points(
                stations[1], stations[2], side)
            independent_gap = (
                (prev_end[0] - next_start[0]) ** 2 +
                (prev_end[1] - next_start[1]) ** 2
            ) ** 0.5
            self.assertGreater(independent_gap, 1.0)
            self.assertEqual(wall[1], g.line_intersection(
                prev_start, prev_end, next_start, next_end))

    def test_cli_writes_dxf(self):
        csv_path = EXAMPLES_DIR / "centerline-stations.csv"
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "folded.dxf"
            rc = g.main([str(csv_path), "--output", str(output)])
            self.assertEqual(rc, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("DUCT_CENTERLINE", text)
            self.assertIn("NOTES_NO_CUT", text)

    def test_missing_required_column_returns_2(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.csv"
            bad.write_text("station_id,x_mm,y_mm\nS0,0,0\nS1,1,1\n", encoding="utf-8")
            self.assertEqual(g.main([str(bad), "--dry-run"]), 2)


if __name__ == "__main__":
    unittest.main()
