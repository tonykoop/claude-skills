#!/usr/bin/env python3
"""End-to-end integration tests for bigthink.cli.

These tests invoke the CLI's main() with a real temporary JSON registry file
and assert on registry state after each command — a genuine round-trip.
No mock patches; the file system is used.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigthink.cli import main
from bigthink.registry import CaptureRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_THESIS = (
    "Physical manufacturing capability follows a power-law scaling with "
    "evaluated spatial complexity, analogous to digital Moore's Law."
)

_THESIS2 = (
    "Planetary element inventory maps crustal abundance to enable "
    "resource-aware AI hardware design and scarcity-penalty triage."
)


def _run(*args: str, registry: str) -> tuple[str, str, int]:
    """Invoke main() with args, capturing stdout/stderr and exit code."""
    out_buf, err_buf = StringIO(), StringIO()
    exit_code = 0
    try:
        with patch("sys.stdout", out_buf), patch("sys.stderr", err_buf):
            main(["--registry", registry, *args])
    except SystemExit as exc:
        exit_code = int(exc.code) if exc.code is not None else 0
    return out_buf.getvalue(), err_buf.getvalue(), exit_code


class TestCliAdd(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.reg_path = str(Path(self.tmpdir) / "reg.json")

    def test_add_creates_registry_file(self) -> None:
        out, err, code = _run(
            "add", "--id", "koops-law", "--thesis", _THESIS,
            "--domain", "scaling_law",
            registry=self.reg_path,
        )
        self.assertEqual(code, 0, f"stderr: {err}")
        self.assertTrue(Path(self.reg_path).exists())

    def test_add_capture_appears_in_list(self) -> None:
        _run("add", "--id", "koops-law", "--thesis", _THESIS,
             "--domain", "scaling_law", registry=self.reg_path)
        out, _, code = _run("list", registry=self.reg_path)
        self.assertIn("koops-law", out)

    def test_add_with_evidence_and_tags(self) -> None:
        out, err, code = _run(
            "add", "--id", "planet-idx", "--thesis", _THESIS2,
            "--domain", "materials",
            "--evidence-refs", "https://example.com/paper1",
            "--tags", "elements", "earth",
            "--source", "Gemini 2026-06-13",
            registry=self.reg_path,
        )
        self.assertEqual(code, 0, err)
        reg = CaptureRegistry.load(self.reg_path)
        cap = reg.get("planet-idx")
        self.assertEqual(cap.evidence_refs, ["https://example.com/paper1"])
        self.assertIn("elements", cap.tags)

    def test_add_duplicate_fails(self) -> None:
        _run("add", "--id", "dup", "--thesis", _THESIS,
             "--domain", "scaling_law", registry=self.reg_path)
        _, _, code = _run("add", "--id", "dup", "--thesis", _THESIS,
                           "--domain", "scaling_law", registry=self.reg_path)
        self.assertNotEqual(code, 0)


class TestCliQuery(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.reg_path = str(Path(self.tmpdir) / "reg.json")
        _run("add", "--id", "koops-law", "--thesis", _THESIS,
             "--domain", "scaling_law", "--tags", "koop",
             registry=self.reg_path)
        _run("add", "--id", "planet-idx", "--thesis", _THESIS2,
             "--domain", "materials", "--tags", "elements",
             registry=self.reg_path)

    def test_query_by_thesis_content(self) -> None:
        out, _, code = _run("query", "power-law", registry=self.reg_path)
        self.assertEqual(code, 0)
        self.assertIn("koops-law", out)

    def test_query_no_match(self) -> None:
        out, _, code = _run("query", "zzznomatch", registry=self.reg_path)
        self.assertEqual(code, 0)
        self.assertIn("No captures", out)

    def test_list_filter_by_domain(self) -> None:
        out, _, _ = _run("list", "--domain", "materials", registry=self.reg_path)
        self.assertIn("planet-idx", out)
        self.assertNotIn("koops-law", out)

    def test_list_filter_by_tag(self) -> None:
        out, _, _ = _run("list", "--tag", "koop", registry=self.reg_path)
        self.assertIn("koops-law", out)
        self.assertNotIn("planet-idx", out)


class TestCliShow(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.reg_path = str(Path(self.tmpdir) / "reg.json")
        _run("add", "--id", "koops-law", "--thesis", _THESIS,
             "--domain", "scaling_law", registry=self.reg_path)

    def test_show_outputs_json(self) -> None:
        out, _, code = _run("show", "koops-law", registry=self.reg_path)
        self.assertEqual(code, 0)
        data = json.loads(out.split("\n\n")[0])  # split off maturity line
        self.assertEqual(data["id"], "koops-law")

    def test_show_unknown_exits_nonzero(self) -> None:
        _, _, code = _run("show", "nobody", registry=self.reg_path)
        self.assertNotEqual(code, 0)


class TestCliConnect(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.reg_path = str(Path(self.tmpdir) / "reg.json")
        _run("add", "--id", "koops-law", "--thesis", _THESIS,
             "--domain", "scaling_law", registry=self.reg_path)
        _run("add", "--id", "planet-idx", "--thesis", _THESIS2,
             "--domain", "materials", registry=self.reg_path)

    def test_connect_adds_edge(self) -> None:
        out, err, code = _run(
            "connect", "koops-law", "planet-idx",
            "--kind", "supports",
            registry=self.reg_path,
        )
        self.assertEqual(code, 0, err)
        reg = CaptureRegistry.load(self.reg_path)
        edges = reg.edges_for("koops-law")
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].to_id, "planet-idx")

    def test_connect_unknown_target_fails(self) -> None:
        _, _, code = _run(
            "connect", "koops-law", "ghost", "--kind", "supports",
            registry=self.reg_path,
        )
        self.assertNotEqual(code, 0)


class TestCliSuggest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.reg_path = str(Path(self.tmpdir) / "reg.json")
        # Add two captures with overlapping keyword content
        _run("add", "--id", "koops-law", "--thesis", _THESIS,
             "--domain", "scaling_law", "--tags", "scaling", "complexity",
             registry=self.reg_path)
        _run("add", "--id", "spatial-comp", "--thesis",
             "Evaluated spatial complexity drives manufacturing automation "
             "efficiency in a power-law scaling relationship for physical systems.",
             "--domain", "scaling_law", "--tags", "complexity",
             registry=self.reg_path)

    def test_suggest_returns_output(self) -> None:
        out, _, code = _run("suggest", "koops-law", registry=self.reg_path)
        self.assertEqual(code, 0)

    def test_suggest_all_returns_output(self) -> None:
        out, _, code = _run("suggest-all", registry=self.reg_path)
        self.assertEqual(code, 0)


class TestCliValidate(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.reg_path = str(Path(self.tmpdir) / "reg.json")
        _run("add", "--id", "koops-law", "--thesis", _THESIS,
             "--domain", "scaling_law", registry=self.reg_path)

    def test_validate_valid_capture(self) -> None:
        _, _, code = _run("validate", "koops-law", registry=self.reg_path)
        self.assertEqual(code, 0)

    def test_validate_all(self) -> None:
        _, _, code = _run("validate", registry=self.reg_path)
        self.assertEqual(code, 0)

    def test_validate_unknown_exits_nonzero(self) -> None:
        _, _, code = _run("validate", "ghost", registry=self.reg_path)
        self.assertNotEqual(code, 0)


class TestCliPromote(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.reg_path = str(Path(self.tmpdir) / "reg.json")

    def test_promote_seed_to_developing(self) -> None:
        # Add a capture that meets the developing gate
        _run(
            "add", "--id", "ready-cap",
            "--thesis", (
                "Manufacturing capability scales with evaluated spatial complexity "
                "in a power-law relationship where each doubling of programmatically "
                "graded geometric variations accelerates multi-material automation "
                "by a fixed efficiency percentage, empirically measured by MakerBench HWE."
            ),
            "--domain", "scaling_law",
            "--evidence-refs", "https://example.com/paper1",
            "--source", "Gemini 2026-06-13",
            registry=self.reg_path,
        )
        out, err, code = _run("promote", "ready-cap", registry=self.reg_path)
        self.assertEqual(code, 0, err)
        self.assertIn("developing", out)
        reg = CaptureRegistry.load(self.reg_path)
        self.assertEqual(reg.get("ready-cap").maturity.value, "developing")

    def test_promote_fails_if_gates_not_met(self) -> None:
        _run("add", "--id", "bare-cap", "--thesis", _THESIS,
             "--domain", "scaling_law", registry=self.reg_path)
        _, _, code = _run("promote", "bare-cap", registry=self.reg_path)
        self.assertNotEqual(code, 0)


class TestCliSummary(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.reg_path = str(Path(self.tmpdir) / "reg.json")
        _run("add", "--id", "koops-law", "--thesis", _THESIS,
             "--domain", "scaling_law", registry=self.reg_path)

    def test_summary_shows_count(self) -> None:
        out, _, code = _run("summary", registry=self.reg_path)
        self.assertEqual(code, 0)
        self.assertIn("1", out)

    def test_summary_shows_seed(self) -> None:
        out, _, _ = _run("summary", registry=self.reg_path)
        self.assertIn("seed", out)


class TestCliDumpLoad(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.reg_path = str(Path(self.tmpdir) / "reg.json")
        self.dump_path = str(Path(self.tmpdir) / "dump.json")
        _run("add", "--id", "koops-law", "--thesis", _THESIS,
             "--domain", "scaling_law", registry=self.reg_path)

    def test_dump_and_load_round_trip(self) -> None:
        _run("dump", self.dump_path, registry=self.reg_path)
        self.assertTrue(Path(self.dump_path).exists())

        new_reg = str(Path(self.tmpdir) / "new_reg.json")
        _run("load", self.dump_path, registry=new_reg)
        out, _, code = _run("list", registry=new_reg)
        self.assertEqual(code, 0)
        self.assertIn("koops-law", out)


if __name__ == "__main__":
    unittest.main()
