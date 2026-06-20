#!/usr/bin/env python3
"""Tests for bigthink.graph_export — DOT, JSON, and Mermaid renderers."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigthink.graph_export import to_dot, to_json, to_mermaid
from bigthink.seed_corpus import build_seed_registry


class TestDotExport(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = build_seed_registry()

    def test_dot_is_string(self) -> None:
        dot = to_dot(self.reg)
        self.assertIsInstance(dot, str)

    def test_dot_contains_digraph(self) -> None:
        dot = to_dot(self.reg)
        self.assertIn("digraph", dot)

    def test_dot_contains_all_node_ids(self) -> None:
        dot = to_dot(self.reg)
        for cap in self.reg:
            self.assertIn(cap.id, dot)

    def test_dot_contains_edges(self) -> None:
        dot = to_dot(self.reg)
        self.assertIn("->", dot)

    def test_dot_custom_graph_name(self) -> None:
        dot = to_dot(self.reg, graph_name="mytest")
        self.assertIn("mytest", dot)

    def test_dot_empty_registry(self) -> None:
        from bigthink.registry import CaptureRegistry
        reg = CaptureRegistry()
        dot = to_dot(reg)
        self.assertIn("digraph", dot)
        self.assertNotIn("->", dot)


class TestJsonExport(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = build_seed_registry()

    def test_json_is_valid(self) -> None:
        raw = to_json(self.reg)
        data = json.loads(raw)
        self.assertIn("nodes", data)
        self.assertIn("edges", data)

    def test_json_node_count(self) -> None:
        data = json.loads(to_json(self.reg))
        self.assertEqual(len(data["nodes"]), len(self.reg))

    def test_json_edge_count(self) -> None:
        data = json.loads(to_json(self.reg))
        self.assertEqual(len(data["edges"]), len(self.reg.all_edges()))

    def test_json_node_has_required_fields(self) -> None:
        data = json.loads(to_json(self.reg))
        for node in data["nodes"]:
            self.assertIn("id", node)
            self.assertIn("domain", node)
            self.assertIn("maturity", node)
            self.assertIn("thesis_excerpt", node)

    def test_json_edge_has_required_fields(self) -> None:
        data = json.loads(to_json(self.reg))
        for edge in data["edges"]:
            self.assertIn("from", edge)
            self.assertIn("to", edge)
            self.assertIn("kind", edge)

    def test_json_thesis_excerpt_truncated(self) -> None:
        data = json.loads(to_json(self.reg))
        for node in data["nodes"]:
            self.assertLessEqual(len(node["thesis_excerpt"]), 121)  # 120 + "…"

    def test_json_empty_registry(self) -> None:
        from bigthink.registry import CaptureRegistry
        data = json.loads(to_json(CaptureRegistry()))
        self.assertEqual(data["nodes"], [])
        self.assertEqual(data["edges"], [])


class TestMermaidExport(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = build_seed_registry()

    def test_mermaid_starts_with_flowchart(self) -> None:
        m = to_mermaid(self.reg)
        self.assertTrue(m.startswith("flowchart LR"))

    def test_mermaid_contains_all_captures(self) -> None:
        m = to_mermaid(self.reg)
        for cap in self.reg:
            # IDs have hyphens replaced with underscores in Mermaid
            safe_id = cap.id.replace("-", "_")
            self.assertIn(safe_id, m)

    def test_mermaid_has_classdefs(self) -> None:
        m = to_mermaid(self.reg)
        self.assertIn("classDef seed", m)
        self.assertIn("classDef developing", m)
        self.assertIn("classDef validated", m)

    def test_mermaid_has_edges(self) -> None:
        m = to_mermaid(self.reg)
        # At least one arrow notation should appear
        has_arrow = any(arrow in m for arrow in ["-->", "==>", "-.->", "-.-x", "--o"])
        self.assertTrue(has_arrow)

    def test_mermaid_empty_registry(self) -> None:
        from bigthink.registry import CaptureRegistry
        m = to_mermaid(CaptureRegistry())
        self.assertIn("flowchart LR", m)
        self.assertIn("classDef", m)


class TestSeedCorpus(unittest.TestCase):
    def test_build_returns_registry(self) -> None:
        from bigthink.registry import CaptureRegistry
        reg = build_seed_registry()
        self.assertIsInstance(reg, CaptureRegistry)

    def test_seed_contains_three_captures(self) -> None:
        reg = build_seed_registry()
        self.assertEqual(len(reg), 3)

    def test_seed_contains_expected_ids(self) -> None:
        reg = build_seed_registry()
        self.assertIn("koops-law-v1", reg)
        self.assertIn("planetary-index-v1", reg)
        self.assertIn("evolution-pipeline-v1", reg)

    def test_seed_captures_have_tags(self) -> None:
        reg = build_seed_registry()
        for cap in reg:
            self.assertGreater(len(cap.tags), 0, f"{cap.id} has no tags")

    def test_seed_connections_exist(self) -> None:
        reg = build_seed_registry()
        all_edges = reg.all_edges()
        self.assertGreater(len(all_edges), 0)

    def test_koops_law_neighbors_planetary(self) -> None:
        reg = build_seed_registry()
        neighbors = reg.neighbors("koops-law-v1", direction="outgoing")
        neighbor_ids = {n.id for n in neighbors}
        self.assertIn("planetary-index-v1", neighbor_ids)

    def test_seed_all_valid(self) -> None:
        from bigthink.validator import CaptureValidator
        reg = build_seed_registry()
        validator = CaptureValidator()
        results = validator.validate_registry(reg)
        for r in results:
            self.assertTrue(r.valid, str(r))

    def test_seed_corpus_ids_function(self) -> None:
        from bigthink.seed_corpus import seed_capture_ids
        ids = seed_capture_ids()
        self.assertEqual(len(ids), 3)
        self.assertIn("koops-law-v1", ids)

    def test_seed_corpus_is_independent(self) -> None:
        """Each call returns a fresh, independent registry."""
        reg1 = build_seed_registry()
        reg2 = build_seed_registry()
        reg1.remove("koops-law-v1")
        self.assertIn("koops-law-v1", reg2)


if __name__ == "__main__":
    unittest.main()
