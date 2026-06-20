#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "plugins" / "maker" / "skills" / "yoga-sequencer"
SCRIPT = SKILL_ROOT / "scripts" / "transitions_class.py"
TEMPLATE = SKILL_ROOT / "references" / "transitions-class-template.json"


def load_module():
    spec = importlib.util.spec_from_file_location("yoga_transitions_class", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["yoga_transitions_class"] = module
    spec.loader.exec_module(module)
    return module


transitions_class = load_module()


class TransitionsCueContractTests(unittest.TestCase):
    def test_cue_rejects_pose_tokens_case_insensitive(self) -> None:
        with self.assertRaises(transitions_class.TransitionsClassError):
            transitions_class.TransitionCue(
                id="bad-cue",
                phase="warm_up",
                cue="Step into crescent lunge and feel the front knee track.",
                somatic_focus=["knee-tracking"],
                breath_instruction="Inhale to rise.",
                duration_secs=60,
                pacing="medium",
            )

    def test_cue_rejects_shorthand_tokens(self) -> None:
        with self.assertRaises(transitions_class.TransitionsClassError):
            transitions_class.TransitionCue(
                id="bad-shorthand",
                phase="flow",
                cue="Move from DD into RLH with an exhale.",
                somatic_focus=[],
                breath_instruction="Exhale.",
                duration_secs=30,
                pacing="fast",
            )

    def test_cue_rejects_common_english_names(self) -> None:
        with self.assertRaises(transitions_class.TransitionsClassError):
            transitions_class.TransitionCue(
                id="bad-english",
                phase="cooldown",
                cue="Settle into child's pose and let the forehead rest.",
                somatic_focus=["forehead-contact"],
                breath_instruction="Natural breath.",
                duration_secs=120,
                pacing="slow",
            )

    def test_cue_accepts_movement_only_language(self) -> None:
        cue = transitions_class.TransitionCue(
            id="good-cue",
            phase="warm_up",
            cue="Shift your weight forward until your hands find the floor. Let the transfer happen gradually.",
            somatic_focus=["weight-transfer", "wrist-loading"],
            breath_instruction="Exhale as weight moves into the hands.",
            duration_secs=90,
            pacing="medium",
        )
        self.assertEqual(cue.id, "good-cue")
        self.assertEqual(cue.duration_secs, 90)


class TransitionsOnlyClassTests(unittest.TestCase):
    def setUp(self) -> None:
        self.yoga_class = transitions_class.TransitionsOnlyClass.from_template(TEMPLATE)

    def test_template_loads_with_expected_fields(self) -> None:
        self.assertEqual(self.yoga_class.class_length_mins, 60)
        self.assertIn("space between", self.yoga_class.theme)
        self.assertGreater(len(self.yoga_class.cues), 0)

    def test_no_pose_names_in_any_cue_text(self) -> None:
        # All cues in the template must pass the forbidden-token guard.
        # TransitionCue.__post_init__ enforces this at construction time,
        # so successful loading already proves the constraint holds.
        # This test makes the contract explicit and documents the expectation.
        for cue in self.yoga_class.cues:
            self.assertIsInstance(cue, transitions_class.TransitionCue)

    def test_class_arc_covers_full_duration(self) -> None:
        total_secs = sum(c.duration_secs for c in self.yoga_class.cues)
        expected_secs = self.yoga_class.class_length_mins * 60
        self.assertAlmostEqual(total_secs, expected_secs, delta=90)

    def test_bilateral_symmetry_both_sides_present(self) -> None:
        sides = {c.side for c in self.yoga_class.cues if c.side is not None}
        self.assertIn("right", sides)
        self.assertIn("left", sides)

    def test_bilateral_cues_are_paired(self) -> None:
        right_ids = {c.id for c in self.yoga_class.cues if c.side == "right"}
        left_ids = {c.id for c in self.yoga_class.cues if c.side == "left"}
        self.assertEqual(len(right_ids), len(left_ids))

    def test_validate_passes_on_good_template(self) -> None:
        self.yoga_class.validate()  # must not raise

    def test_all_phases_present(self) -> None:
        phases = {c.phase for c in self.yoga_class.cues}
        for expected in ("arrival", "warm_up", "standing_flow", "peak_work", "cooldown", "stillness"):
            self.assertIn(expected, phases, f"Missing phase: {expected!r}")

    def test_as_dict_round_trips_cue_count(self) -> None:
        d = self.yoga_class.as_dict()
        self.assertEqual(d["cue_count"], len(self.yoga_class.cues))
        self.assertIn("cues", d)
        self.assertEqual(len(d["cues"]), d["cue_count"])

    def test_teacher_script_contains_no_forbidden_tokens(self) -> None:
        script = self.yoga_class.as_teacher_script()
        forbidden = [
            "crescent lunge", "downward dog", "warrior",
            "chaturanga", "child's pose", "savasana",
        ]
        for token in forbidden:
            self.assertNotIn(token.lower(), script.lower(), f"Pose name leaked into script: {token!r}")

    def test_teacher_script_has_phase_headers(self) -> None:
        script = self.yoga_class.as_teacher_script()
        self.assertIn("ARRIVAL", script)
        self.assertIn("WARM UP", script)
        self.assertIn("STILLNESS", script)

    def test_validate_rejects_empty_class(self) -> None:
        empty = transitions_class.TransitionsOnlyClass(
            class_length_mins=60,
            theme="test",
            level="all-levels",
        )
        with self.assertRaises(transitions_class.TransitionsClassError):
            empty.validate()

    def test_validate_rejects_duration_mismatch(self) -> None:
        short = transitions_class.TransitionsOnlyClass(
            class_length_mins=60,
            theme="test",
            level="all-levels",
        )
        short.add_cue(
            transitions_class.TransitionCue(
                id="only-cue",
                phase="arrival",
                cue="Breathe and settle into the floor beneath you.",
                somatic_focus=["floor-contact"],
                breath_instruction="Natural breath.",
                duration_secs=60,  # only 1 minute for a 60-min class
                pacing="slow",
            )
        )
        with self.assertRaises(transitions_class.TransitionsClassError):
            short.validate()

    def test_validate_rejects_unilateral_missing_side(self) -> None:
        one_sided = transitions_class.TransitionsOnlyClass(
            class_length_mins=1,
            theme="test",
            level="all-levels",
        )
        one_sided.add_cue(
            transitions_class.TransitionCue(
                id="right-only",
                phase="flow",
                cue="Step forward and feel the front hip open to the right.",
                somatic_focus=["hip-flexor"],
                breath_instruction="Exhale.",
                duration_secs=60,
                pacing="medium",
                side="right",
            )
        )
        with self.assertRaises(transitions_class.TransitionsClassError):
            one_sided.validate()


class TransitionsClassCLITests(unittest.TestCase):
    def test_cli_teacher_script_mode(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--template", str(TEMPLATE)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("TRANSITIONS-ONLY CLASS", result.stdout)
        self.assertIn("ARRIVAL", result.stdout)

    def test_cli_json_mode(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--template", str(TEMPLATE), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("cues", data)
        self.assertIn("class_length_mins", data)
        self.assertEqual(data["class_length_mins"], 60)

    def test_template_json_is_valid_json(self) -> None:
        with TEMPLATE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertIn("schema_version", data)
        self.assertIn("cues", data)
        self.assertEqual(data["mode"], "transitions-only")

    def test_template_schema_version_is_string(self) -> None:
        with TEMPLATE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertIsInstance(data["schema_version"], str)


if __name__ == "__main__":
    unittest.main()
