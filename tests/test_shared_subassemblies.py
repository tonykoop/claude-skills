#!/usr/bin/env python3
"""Tests for the offline Shared Subassemblies reporter (#244)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins" / "maker" / "skills" / "idea-incubator" / "scripts" / "shared_subassemblies.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("shared_subassemblies", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["shared_subassemblies"] = module
    spec.loader.exec_module(module)
    return module


ss = load_module()

OBSIDIAN_NOTE = textwrap.dedent(
    """
    ---
    idea: "detent-locking telescoping leg"
    id: idea-0142
    functions:
      - index-detent
      - tension
    interfaces:
      - mount:t-slot-2020
      - fastener:m5
    materials:
      - aluminum-6061
    ---
    Body text here.
    """
).strip()

FENCED_NOTE = textwrap.dedent(
    """
    # Some GitHub issue body
    ```yaml
    idea: adjustable monitor arm
    functions: [index-detent, slide]
    interfaces:
      - mount:t-slot-2020
    ```
    """
).strip()

UNTAGGED_NOTE = "---\nidea: just a thought\n---\nno functions here\n"


class ParseTests(unittest.TestCase):
    def test_parses_obsidian_block_lists(self):
        fm = ss.parse_frontmatter(OBSIDIAN_NOTE)
        self.assertEqual(fm["functions"], ["index-detent", "tension"])
        self.assertEqual(fm["interfaces"], ["mount:t-slot-2020", "fastener:m5"])
        self.assertEqual(fm["idea"], "detent-locking telescoping leg")

    def test_parses_fenced_flow_list(self):
        fm = ss.parse_frontmatter(FENCED_NOTE)
        self.assertEqual(fm["functions"], ["index-detent", "slide"])
        self.assertEqual(fm["interfaces"], ["mount:t-slot-2020"])

    def test_untagged_note_has_no_functions(self):
        fm = ss.parse_frontmatter(UNTAGGED_NOTE)
        self.assertEqual(fm["functions"], [])


class GroupingTests(unittest.TestCase):
    def setUp(self):
        self.notes = [
            {"label": "leg", "functions": ["index-detent", "tension"], "interfaces": ["mount:t-slot-2020"]},
            {"label": "arm", "functions": ["index-detent", "slide"], "interfaces": ["mount:t-slot-2020"]},
            {"label": "clamp", "functions": ["tension"], "interfaces": ["fastener:m5"]},
        ]

    def test_group_by_function(self):
        g = ss.group_by(self.notes, "functions")
        self.assertEqual(g["index-detent"], ["leg", "arm"])
        self.assertCountEqual(g["tension"], ["leg", "clamp"])

    def test_shared_filters_to_2plus(self):
        sh = ss.shared(ss.group_by(self.notes, "functions"))
        self.assertIn("index-detent", sh)
        self.assertIn("tension", sh)
        self.assertNotIn("slide", sh)  # only one idea

    def test_shared_interfaces(self):
        sh = ss.shared(ss.group_by(self.notes, "interfaces"))
        self.assertIn("mount:t-slot-2020", sh)
        self.assertNotIn("fastener:m5", sh)

    def test_candidate_pairs_rank_by_score(self):
        pairs = ss.candidate_pairs(self.notes)
        top = pairs[0]
        self.assertEqual({top["a"], top["b"]}, {"leg", "arm"})
        self.assertIn("index-detent", top["shared_functions"])
        self.assertIn("mount:t-slot-2020", top["shared_interfaces"])
        self.assertEqual(top["score"], 2)  # 1 shared function + 1 shared interface

    def test_no_pair_without_shared_function(self):
        notes = [
            {"label": "a", "functions": ["x"], "interfaces": ["i"]},
            {"label": "b", "functions": ["y"], "interfaces": ["i"]},  # shared iface only
        ]
        self.assertEqual(ss.candidate_pairs(notes), [])

    def test_untagged_surfaced_in_report(self):
        notes = self.notes + [{"label": "mystery", "functions": [], "interfaces": []}]
        report = ss.build_report(notes)
        self.assertIn("mystery", report["untagged"])


class IntegrationTests(unittest.TestCase):
    def test_load_notes_and_render_from_dir(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "leg.md").write_text(OBSIDIAN_NOTE, encoding="utf-8")
            (Path(d) / "arm.md").write_text(FENCED_NOTE, encoding="utf-8")
            (Path(d) / "blank.md").write_text(UNTAGGED_NOTE, encoding="utf-8")
            notes = ss.load_notes(Path(d))
            self.assertEqual(len(notes), 3)
            report = ss.build_report(notes)
            self.assertIn("index-detent", report["shared_subassemblies"])  # leg + arm
            md = ss.render_markdown(report)
            self.assertIn("# Shared Subassemblies (offline)", md)
            self.assertIn("Shared subassemblies (functions in 2+ ideas)", md)
            self.assertIn("Cross-pollination candidate pairs", md)

    def test_main_json_and_dir_validation(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "n.md").write_text(OBSIDIAN_NOTE, encoding="utf-8")
            self.assertEqual(ss.main(["--dir", d, "--json"]), 0)
        self.assertEqual(ss.main(["--dir", "/no/such/dir/xyz"]), 2)


if __name__ == "__main__":
    unittest.main()
