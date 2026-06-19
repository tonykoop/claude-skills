#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins"
    / "maker"
    / "skills"
    / "idea-incubator"
    / "scripts"
    / "domain_router.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("domain_router", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["domain_router"] = module
    spec.loader.exec_module(module)
    return module


router = load_module()


# The pre-tune-up baseline: any single keyword substring hit applies the domain
# confidently (the old route_labels in gemini_to_github.py). Reconstructed here
# so we can measure the tuned router against it on the same captures.
BASELINE_KEYWORDS = {
    "instrument": ("flute", "harp", "didgeridoo", "drum", "acoustic", "reed", "fipple", "bore", "string"),
    "woodworking": ("wood", "plywood", "joinery", "dovetail", "router", "lathe", "cabinet", "grain"),
    "sheet-metal": ("sheet metal", "brake", "plasma", "bend", "flat pattern", "shear", "weld", "gauge"),
    "electronics": ("pcb", "pcba", "schematic", "gerber", "microcontroller", "mcu", "sensor", "i2c", "spi", "circuit"),
    "firmware": ("firmware", "flash", "bootloader", "rtos", "embedded", "register", "interrupt", "hal"),
    "software": ("script", "app", "api", "webhook", "automation", "cli", "database", "frontend", "backend"),
    "yoga": ("yoga", "vinyasa", "asana", "sequence", "pose", "savasana", "class"),
    "maker": ("jig", "fixture", "workholding", "mold", "cnc", "laser cutter", "3d print", "mill", "fabricate"),
}


def baseline_labels(text: str) -> list[str]:
    low = text.lower()
    labels = ["capture"]
    matched = [d for d, kws in BASELINE_KEYWORDS.items() if any(k in low for k in kws)]
    labels.extend(matched) if matched else labels.append("needs-clarification")
    return labels


# Real captures drawn from this repo's open issue inbox (title + body snippet),
# hand-labeled with the domain a human triager would assign. Routing is tuned
# against these, not synthetic strings (acceptance: "tuned against real
# captures").
REAL_CAPTURES = [
    {
        "id": 177,
        "text": "[houseplant] Propagation tracker (cuttings, air-layering, rooting timelines). "
        "A propagation sub-module that helps expand the collection over time.",
        "expect_label": None,  # no domain vocabulary -> safe fallback
    },
    {
        "id": 59,
        "text": "Mirror Storage cabinet system recovery. gun-safe / showcase / cabinet display "
        "system. Sequential EP-prefix part numbers in CAD.",
        "expect_label": "woodworking",  # 'cabinet' (single weak) -> tentative
        "tentative": True,
    },
    {
        "id": 55,
        "text": "Weather Balloon Camera Vessel — recover and scaffold repo. High-altitude "
        "photography rig to mount a camera on a weather balloon.",
        "expect_label": None,  # 'rig'/'camera' not in vocab -> safe fallback
    },
    {
        "id": 1001,
        "text": "Design a custom PCB with an STM32 microcontroller and an I2C sensor bus; "
        "write the firmware bootloader.",
        "expect_label": "electronics",  # pcb(3)+microcontroller(3) -> confident
        "tentative": False,
        "also": ["firmware", "maker"],
    },
]


class TunedRoutingTests(unittest.TestCase):
    def test_strong_signal_is_confident_no_triage(self) -> None:
        result = router.classify("Lay out the PCB and route the schematic")
        self.assertIn("electronics", result.confident)
        self.assertNotIn("needs-clarification", result.labels)
        self.assertIn("maker", result.labels)  # hardware umbrella

    def test_single_weak_hit_is_tentative_with_triage(self) -> None:
        result = router.classify("Build a cabinet for the shop")
        self.assertIn("woodworking", result.tentative)
        self.assertIn("needs-clarification", result.labels)

    def test_unroutable_falls_back_to_needs_clarification(self) -> None:
        result = router.classify("A tracker for rooting timelines on my plants")
        self.assertTrue(result.unroutable)
        self.assertEqual(result.labels, ["capture", "needs-clarification"])
        self.assertNotEqual(result.labels, ["capture"])  # never left unlabeled

    def test_firmware_electronics_cofire(self) -> None:
        labels = router.route_labels("Write firmware for the microcontroller on the PCB")
        self.assertIn("firmware", labels)
        self.assertIn("electronics", labels)

    def test_word_boundary_kills_baseline_false_positive(self) -> None:
        # Baseline matches 'pose' inside 'purpose' -> confident yoga mislabel.
        self.assertIn("yoga", baseline_labels("What is the purpose of this plan"))
        # Tuned router uses a word boundary, so 'purpose' does not fire yoga.
        self.assertNotIn("yoga", router.route_labels("What is the purpose of this plan"))


class RealCaptureTests(unittest.TestCase):
    def test_real_captures_route_as_expected(self) -> None:
        for cap in REAL_CAPTURES:
            result = router.classify(cap["text"])
            with self.subTest(issue=cap["id"]):
                if cap["expect_label"] is None:
                    self.assertTrue(result.unroutable, f"#{cap['id']} should be unroutable")
                    self.assertIn("needs-clarification", result.labels)
                else:
                    self.assertIn(cap["expect_label"], result.labels)
                    if cap.get("tentative"):
                        self.assertIn("needs-clarification", result.labels)
                    for extra in cap.get("also", []):
                        self.assertIn(extra, result.labels)

    def test_every_real_capture_is_labeled(self) -> None:
        # Acceptance: unroutable captures fall back to a safe label, never bare.
        for cap in REAL_CAPTURES:
            labels = router.route_labels(cap["text"])
            with self.subTest(issue=cap["id"]):
                self.assertGreater(len(labels), 1)  # more than just 'capture'

    def test_tuned_reduces_mislabels_vs_baseline(self) -> None:
        # A software capture that parses a 'string' — the baseline's bare
        # 'string' instrument keyword mislabels it; the tuned table uses the
        # precise 'string tension' phrase, so no instrument label fires.
        text = "Parse the string field from the API response in the backend service"
        base = set(baseline_labels(text))
        tuned = set(router.route_labels(text))
        self.assertIn("instrument", base)  # baseline mislabel
        self.assertNotIn("instrument", tuned)
        self.assertIn("software", tuned)  # the genuine signal survives


class ParityWithDocTests(unittest.TestCase):
    def test_strong_signals_have_weight_three(self) -> None:
        strong = {(d, s) for d, sigs in router.SIGNALS.items() for s, w in sigs if w == router.STRONG}
        self.assertIn(("electronics", "pcb"), strong)
        self.assertIn(("yoga", "vinyasa"), strong)
        self.assertIn(("sheet-metal", "flat pattern"), strong)

    def test_phrase_signals_match_substring(self) -> None:
        # Multi-word strong signal must match even though it is not a single word.
        self.assertIn("sheet-metal", router.route_labels("compute the flat pattern and bend allowance"))


if __name__ == "__main__":
    unittest.main()
