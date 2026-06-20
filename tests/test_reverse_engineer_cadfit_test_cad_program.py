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
    / "cadfit_test_cad_program.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("cadfit_test_cad_program", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["cadfit_test_cad_program"] = module
    spec.loader.exec_module(module)
    return module


tester = load_module()


def write_program(text: str) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
    handle.write(text)
    handle.close()
    return Path(handle.name)


class CadfitTestCadProgramTests(unittest.TestCase):
    def test_mock_score_returns_invalid_ratio_and_iou(self) -> None:
        program = write_program(
            "CADFIT_MOCK_RESULT = {'candidate_volume': 80, 'target_volume': 100, 'intersection_volume': 70}\n"
        )
        result = tester.test_cad_program(program)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["invalid_ratio"], 0.0)
        self.assertAlmostEqual(result["volumetric_iou"], 70 / 110)

    def test_syntax_error_is_returned_as_invalid_program_signal(self) -> None:
        program = write_program("def broken(:\n")
        result = tester.test_cad_program(program)
        self.assertEqual(result["status"], "invalid_program")
        self.assertEqual(result["invalid_ratio"], 1.0)
        self.assertEqual(result["volumetric_iou"], 0.0)
        self.assertTrue(any("syntax error" in finding for finding in result["findings"]))

    def test_kernel_failure_marker_is_caught_as_normal_score(self) -> None:
        program = write_program("# CADFIT_KERNEL_FAILURE\nresult = None\n")
        result = tester.test_cad_program(program)
        self.assertEqual(result["status"], "kernel_failure")
        self.assertEqual(result["invalid_ratio"], 1.0)
        self.assertTrue(any("kernel failure" in finding for finding in result["findings"]))

    def test_require_kernel_reports_unavailable_without_throwing(self) -> None:
        program = write_program("result = 'compiles only'\n")
        result = tester.test_cad_program(program, require_kernel=True)
        if tester.cadquery_available():
            self.assertEqual(result["status"], "ok")
        else:
            self.assertEqual(result["status"], "kernel_unavailable")
            self.assertEqual(result["invalid_ratio"], 1.0)


if __name__ == "__main__":
    unittest.main()
