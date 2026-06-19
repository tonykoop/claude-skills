"""Tests for collection_dashboard.py."""
import sys
import io
import json
import datetime
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from collection_dashboard import (
    build_dashboard,
    _bucket,
    _watering_tasks,
    _fertilizing_tasks,
    _wire_tasks,
    _bloom_tasks,
    _propagation_tasks,
    _health_tasks,
    Task,
)

TODAY = datetime.date(2026, 6, 19)
TODAY_STR = TODAY.isoformat()

MINIMAL_PLANT = {
    "plant_id": "p1",
    "display_name": "Test Plant",
    "species": "ficus",
    "growth_class": "fast",
    "phase": "active_growth",
    "heat": False,
    "stressors": [],
    "care_events": [],
    "buds": [],
    "propagules": [],
    "health_observations": [],
}


def _plant(**overrides):
    p = dict(MINIMAL_PLANT)
    p.update(overrides)
    return p


class TestBucket(unittest.TestCase):
    def _task(self, due_offset):
        due = None if due_offset is None else TODAY + datetime.timedelta(days=due_offset)
        return Task(due=due, plant_id="p", label="L", detail="D")

    def test_overdue(self):
        self.assertEqual(_bucket(self._task(-1), TODAY), "overdue")

    def test_today(self):
        self.assertEqual(_bucket(self._task(0), TODAY), "today")

    def test_this_week_edge(self):
        self.assertEqual(_bucket(self._task(1), TODAY), "this_week")
        self.assertEqual(_bucket(self._task(7), TODAY), "this_week")

    def test_this_month(self):
        self.assertEqual(_bucket(self._task(8), TODAY), "this_month")
        self.assertEqual(_bucket(self._task(30), TODAY), "this_month")

    def test_later(self):
        self.assertEqual(_bucket(self._task(31), TODAY), "later")
        self.assertEqual(_bucket(self._task(None), TODAY), "later")


class TestWateringTasks(unittest.TestCase):
    def test_no_last_watered_due_today(self):
        plant = _plant()
        tasks = _watering_tasks(plant, TODAY)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].due, TODAY)

    def test_last_watered_shifts_due(self):
        plant = _plant(care_events=[{"type": "watered", "date": "2026-06-17"}])
        tasks = _watering_tasks(plant, TODAY)
        self.assertEqual(len(tasks), 1)
        # fast growth, mild: 3-day cadence from Jun 17 → Jun 20
        self.assertEqual(tasks[0].due, datetime.date(2026, 6, 20))

    def test_heat_tightens_cadence(self):
        # heat=True, fast → 1-day cadence; last watered yesterday → due today
        plant = _plant(heat=True, care_events=[{"type": "watered", "date": "2026-06-18"}])
        tasks = _watering_tasks(plant, TODAY)
        self.assertEqual(tasks[0].due, datetime.date(2026, 6, 19))

    def test_invalid_growth_class_returns_empty(self):
        plant = _plant(growth_class="turbo")
        tasks = _watering_tasks(plant, TODAY)
        self.assertEqual(tasks, [])


class TestFertilizingTasks(unittest.TestCase):
    def test_active_growth_produces_task(self):
        plant = _plant()
        tasks = _fertilizing_tasks(plant, TODAY)
        self.assertEqual(len(tasks), 1)
        self.assertFalse(tasks[0].due is None)

    def test_dormancy_no_active_task(self):
        plant = _plant(phase="dormancy")
        tasks = _fertilizing_tasks(plant, TODAY)
        # dormancy -> suspended, no resume_after_days -> no task
        self.assertEqual(tasks, [])

    def test_repot_stressor_creates_resume_task(self):
        plant = _plant(stressors=["repot"],
                       care_events=[{"type": "repotted", "date": "2026-06-01"}])
        tasks = _fertilizing_tasks(plant, TODAY)
        self.assertEqual(len(tasks), 1)
        self.assertIn("resume", tasks[0].label.lower())
        # resume date should be 42 days after Jun 1 = Jul 13
        self.assertEqual(tasks[0].due, datetime.date(2026, 7, 13))


class TestWireTasks(unittest.TestCase):
    def test_wired_event_produces_task(self):
        plant = _plant(care_events=[{"type": "wired", "date": "2026-06-10", "branch": "R02"}])
        tasks = _wire_tasks(plant, TODAY)
        self.assertEqual(len(tasks), 1)
        self.assertIn("R02", tasks[0].label)

    def test_no_wired_events_empty(self):
        plant = _plant()
        self.assertEqual(_wire_tasks(plant, TODAY), [])

    def test_first_inspection_fast_growth_active(self):
        plant = _plant(care_events=[{"type": "wired", "date": "2026-06-12"}])
        tasks = _wire_tasks(plant, TODAY)
        # fast + active: first inspection 7 days after Jun 12 = Jun 19
        # due is always a datetime.date from the dashboard layer
        self.assertIsInstance(tasks[0].due, datetime.date)
        self.assertEqual(tasks[0].due, datetime.date(2026, 6, 19))

    def test_multiple_wired_branches(self):
        plant = _plant(care_events=[
            {"type": "wired", "date": "2026-06-10", "branch": "L01"},
            {"type": "wired", "date": "2026-06-14", "branch": "R03"},
        ])
        tasks = _wire_tasks(plant, TODAY)
        self.assertEqual(len(tasks), 2)


class TestBloomTasks(unittest.TestCase):
    def test_bud_with_history(self):
        plant = _plant(buds=[{
            "species": "phalaenopsis",
            "stage": "swelling",
            "anchor_date": "2026-06-10",
            "condition": "warm",
            "history_intervals_days": [14, 17],
        }])
        tasks = _bloom_tasks(plant, TODAY)
        self.assertEqual(len(tasks), 1)
        self.assertIn("Bloom", tasks[0].label)
        self.assertIsNotNone(tasks[0].due)

    def test_no_buds_empty(self):
        self.assertEqual(_bloom_tasks(_plant(), TODAY), [])

    def test_missing_anchor_skipped(self):
        plant = _plant(buds=[{"species": "ficus"}])
        self.assertEqual(_bloom_tasks(plant, TODAY), [])


class TestPropagationTasks(unittest.TestCase):
    def test_tip_cutting_produces_task(self):
        plant = _plant(propagules=[{
            "method": "tip-cutting",
            "species": "ficus",
            "condition": "warm",
            "started_date": "2026-06-01",
        }])
        tasks = _propagation_tasks(plant, TODAY)
        self.assertEqual(len(tasks), 1)
        self.assertIn("root", tasks[0].label.lower())

    def test_no_propagules_empty(self):
        self.assertEqual(_propagation_tasks(_plant(), TODAY), [])

    def test_missing_started_date_skipped(self):
        plant = _plant(propagules=[{"method": "tip-cutting", "species": "ficus"}])
        self.assertEqual(_propagation_tasks(plant, TODAY), [])


class TestHealthTasks(unittest.TestCase):
    def test_chlorosis_produces_flag(self):
        plant = _plant(health_observations=[
            {"symptom": "chlorosis-lower-leaves", "region": "lower interior"}
        ])
        tasks = _health_tasks(plant, TODAY)
        self.assertGreater(len(tasks), 0)
        labels = [t.label for t in tasks]
        self.assertTrue(any("chlorosis" in l.lower() for l in labels))

    def test_no_observations_empty(self):
        self.assertEqual(_health_tasks(_plant(), TODAY), [])

    def test_pest_flag_adds_structural_blocker(self):
        plant = _plant(health_observations=[
            {"symptom": "webbing-suspected-spidermite", "region": "leaf axils"}
        ])
        tasks = _health_tasks(plant, TODAY)
        labels = [t.label for t in tasks]
        self.assertTrue(any("BLOCKED" in l or "pest" in l.lower() for l in labels))


class TestBuildDashboard(unittest.TestCase):
    def _collection(self, plants):
        return {"today": TODAY_STR, "plants": plants}

    def test_empty_collection(self):
        out = build_dashboard({"today": TODAY_STR, "plants": []})
        self.assertIn("Dashboard", out)

    def test_missing_today_raises(self):
        with self.assertRaises(ValueError):
            build_dashboard({"plants": []})

    def test_plants_not_list_raises(self):
        with self.assertRaises(ValueError):
            build_dashboard({"today": TODAY_STR, "plants": "not-a-list"})

    def test_full_plant_renders(self):
        plant = _plant(
            care_events=[
                {"type": "watered", "date": "2026-06-17"},
                {"type": "wired", "date": "2026-06-10", "branch": "R02"},
                {"type": "fertilized", "date": "2026-06-01"},
            ],
            buds=[{
                "species": "phalaenopsis", "stage": "swelling",
                "anchor_date": "2026-06-10", "condition": "warm",
                "history_intervals_days": [14, 18],
            }],
            propagules=[{
                "method": "tip-cutting", "species": "ficus",
                "condition": "warm", "started_date": "2026-06-01",
            }],
        )
        out = build_dashboard(self._collection([plant]))
        self.assertIn("Watering", out)
        self.assertIn("Wire", out)
        self.assertIn("Fertiliz", out)
        self.assertIn("Bloom", out)

    def test_display_name_used(self):
        plant = _plant(display_name="My Ficus")
        out = build_dashboard(self._collection([plant]))
        self.assertIn("My Ficus", out)

    def test_overdue_task_appears_in_overdue_bucket(self):
        # last watered 10 days ago, fast growth 3-day cadence → overdue
        plant = _plant(care_events=[{"type": "watered", "date": "2026-06-08"}])
        out = build_dashboard(self._collection([plant]))
        self.assertIn("Overdue", out)

    def test_plant_without_plant_id_skipped(self):
        plants = [{"display_name": "orphan"}]
        out = build_dashboard({"today": TODAY_STR, "plants": plants})
        self.assertIn("Dashboard", out)

    def test_date_format_in_header(self):
        out = build_dashboard({"today": TODAY_STR, "plants": []})
        self.assertIn(TODAY_STR, out)

    def test_multiple_plants(self):
        p1 = _plant(plant_id="p1", display_name="Plant A")
        p2 = _plant(plant_id="p2", display_name="Plant B",
                    care_events=[{"type": "watered", "date": "2026-06-05"}])
        out = build_dashboard(self._collection([p1, p2]))
        self.assertIn("Plant A", out)
        self.assertIn("Plant B", out)

    def test_no_tasks_message(self):
        # A plant with no events, no buds, no observations -> just watering (due today).
        # To get "no tasks" we'd need every event very recent. Let's test the message
        # only appears when collection is truly empty.
        out = build_dashboard({"today": TODAY_STR, "plants": []})
        self.assertIn("up to date", out)


class TestCLI(unittest.TestCase):
    def test_cli_stdin(self):
        """collection_dashboard main() reads JSON from stdin and exits 0."""
        import io
        from unittest.mock import patch
        from collection_dashboard import main

        payload = json.dumps({
            "today": TODAY_STR,
            "plants": [_plant()],
        })
        with patch("sys.stdin", io.StringIO(payload)):
            out = io.StringIO()
            with patch("sys.stdout", out):
                rc = main([])
        self.assertEqual(rc, 0)
        self.assertIn("Dashboard", out.getvalue())

    def test_cli_bad_json_exits_2(self):
        from unittest.mock import patch
        from collection_dashboard import main

        with patch("sys.stdin", io.StringIO("not-json")):
            rc = main([])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
