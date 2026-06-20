#!/usr/bin/env python3
"""Tests for bigthink.registry — CaptureRegistry add/get/filter/connect/graph."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigthink.registry import CaptureRegistry, RegistryError
from bigthink.schema import (
    CaptureConnection,
    ConnectionKind,
    Domain,
    ManufacturingTheoryCapture,
    MaturityLevel,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_THESIS = (
    "Manufacturing capability scales with evaluated spatial complexity "
    "in a power-law relationship that underpins modern fabrication limits."
)


def make_cap(id_: str, domain: Domain = Domain.SCALING_LAW, **kw) -> ManufacturingTheoryCapture:
    # Ensure IDs are at least 2 chars (schema requires slug of 2–64 chars)
    _id = id_ if len(id_) >= 2 else id_ + "x"
    return ManufacturingTheoryCapture(id=_id, thesis=_THESIS, domain=domain, **kw)


class TestCaptureRegistryCRUD(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = CaptureRegistry()

    def test_add_and_get(self) -> None:
        cap = make_cap("koops-law")
        self.reg.add(cap)
        self.assertIs(self.reg.get("koops-law"), cap)

    def test_len(self) -> None:
        self.assertEqual(len(self.reg), 0)
        self.reg.add(make_cap("nn"))
        self.assertEqual(len(self.reg), 1)

    def test_contains(self) -> None:
        self.reg.add(make_cap("nn"))
        self.assertIn("nn", self.reg)
        self.assertNotIn("xx", self.reg)

    def test_duplicate_id_raises(self) -> None:
        self.reg.add(make_cap("cap1"))
        with self.assertRaises(RegistryError):
            self.reg.add(make_cap("cap1"))

    def test_get_unknown_raises_key_error(self) -> None:
        with self.assertRaises(KeyError):
            self.reg.get("nonexistent")

    def test_remove_returns_capture(self) -> None:
        cap = make_cap("to-remove")
        self.reg.add(cap)
        removed = self.reg.remove("to-remove")
        self.assertIs(removed, cap)
        self.assertNotIn("to-remove", self.reg)

    def test_remove_cleans_incoming_edges(self) -> None:
        self.reg.add(make_cap("na"))
        self.reg.add(make_cap("nb"))
        self.reg.connect("na", "nb", ConnectionKind.SUPPORTS)
        self.reg.remove("nb")
        # No edge should point to deleted capture
        for e in self.reg.all_edges():
            self.assertNotEqual(e.to_id, "nb")

    def test_iter(self) -> None:
        caps = [make_cap(f"cp{i}") for i in range(3)]
        for c in caps:
            self.reg.add(c)
        ids = {c.id for c in self.reg}
        self.assertEqual(ids, {"cp0", "cp1", "cp2"})


class TestCaptureRegistryQuery(unittest.TestCase):
    def setUp(self) -> None:
        self.reg = CaptureRegistry()
        self.reg.add(make_cap("scaling-law", tags=["koop", "alpha"]))
        self.reg.add(make_cap(
            "planetary-index",
            domain=Domain.MATERIALS,
            tags=["elements", "earth"],
        ))

    def test_query_hits_thesis(self) -> None:
        results = self.reg.query("evaluated spatial complexity")
        self.assertEqual(len(results), 2)  # both share same thesis in test helper

    def test_query_hits_tags(self) -> None:
        results = self.reg.query("elements")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "planetary-index")

    def test_query_case_insensitive(self) -> None:
        results = self.reg.query("KOOP")
        self.assertEqual(len(results), 1)

    def test_query_no_match_empty(self) -> None:
        results = self.reg.query("zzznomatch")
        self.assertEqual(results, [])

    def test_filter_by_domain(self) -> None:
        results = self.reg.filter(domain=Domain.MATERIALS)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "planetary-index")

    def test_filter_by_maturity(self) -> None:
        results = self.reg.filter(maturity=MaturityLevel.SEED)
        self.assertEqual(len(results), 2)

    def test_filter_by_tag(self) -> None:
        results = self.reg.filter(tag="koop")
        self.assertEqual(len(results), 1)

    def test_filter_combined(self) -> None:
        results = self.reg.filter(domain=Domain.MATERIALS, tag="elements")
        self.assertEqual(len(results), 1)

    def test_filter_no_match(self) -> None:
        results = self.reg.filter(domain=Domain.METROLOGY)
        self.assertEqual(results, [])


class TestCaptureRegistryGraph(unittest.TestCase):
    # Use proper 2+ char slugs — schema rejects single-char IDs
    _IDS = ("na", "nb", "nc", "nd")

    def setUp(self) -> None:
        self.reg = CaptureRegistry()
        for id_ in self._IDS:
            self.reg.add(make_cap(id_))

    def test_connect_creates_edge(self) -> None:
        conn = self.reg.connect("na", "nb", ConnectionKind.SUPPORTS)
        self.assertEqual(conn.from_id, "na")
        self.assertEqual(conn.to_id, "nb")
        self.assertIn(conn, self.reg.edges_for("na"))

    def test_connect_unknown_id_raises(self) -> None:
        with self.assertRaises(RegistryError):
            self.reg.connect("na", "NOPE", ConnectionKind.SUPPORTS)

    def test_connect_idempotent(self) -> None:
        self.reg.connect("na", "nb", ConnectionKind.SUPPORTS)
        self.reg.connect("na", "nb", ConnectionKind.SUPPORTS)
        self.assertEqual(len(self.reg.edges_for("na")), 1)

    def test_bidirectional_connect(self) -> None:
        self.reg.connect("na", "nb", ConnectionKind.SHARES_DOMAIN, bidirectional=True)
        self.assertEqual(len(self.reg.edges_for("na")), 1)
        self.assertEqual(len(self.reg.edges_for("nb")), 1)
        self.assertEqual(self.reg.edges_for("nb")[0].to_id, "na")

    def test_neighbors_outgoing(self) -> None:
        self.reg.connect("na", "nb", ConnectionKind.EXTENDS)
        self.reg.connect("na", "nc", ConnectionKind.EXTENDS)
        neighbors = self.reg.neighbors("na", direction="outgoing")
        self.assertEqual({n.id for n in neighbors}, {"nb", "nc"})

    def test_neighbors_incoming(self) -> None:
        self.reg.connect("na", "nb", ConnectionKind.EXTENDS)
        incoming = self.reg.neighbors("nb", direction="incoming")
        self.assertEqual({n.id for n in incoming}, {"na"})

    def test_neighbors_both(self) -> None:
        self.reg.connect("na", "nb", ConnectionKind.EXTENDS)
        self.reg.connect("nc", "na", ConnectionKind.SUPPORTS)
        both = self.reg.neighbors("na", direction="both")
        self.assertEqual({n.id for n in both}, {"nb", "nc"})

    def test_neighbors_kind_filter(self) -> None:
        self.reg.connect("na", "nb", ConnectionKind.EXTENDS)
        self.reg.connect("na", "nc", ConnectionKind.CITES)
        extends_only = self.reg.neighbors("na", kind=ConnectionKind.EXTENDS)
        self.assertEqual(len(extends_only), 1)
        self.assertEqual(extends_only[0].id, "nb")

    def test_subgraph_bfs(self) -> None:
        # na → nb → nc
        self.reg.connect("na", "nb", ConnectionKind.SUPPORTS)
        self.reg.connect("nb", "nc", ConnectionKind.SUPPORTS)
        sg = self.reg.subgraph("na", max_depth=2)
        ids = {c.id for c in sg}
        self.assertIn("na", ids)
        self.assertIn("nb", ids)
        self.assertIn("nc", ids)
        self.assertNotIn("nd", ids)  # unreachable

    def test_subgraph_max_depth_respected(self) -> None:
        self.reg.connect("na", "nb", ConnectionKind.SUPPORTS)
        self.reg.connect("nb", "nc", ConnectionKind.SUPPORTS)
        sg = self.reg.subgraph("na", max_depth=1)
        ids = {c.id for c in sg}
        self.assertIn("nb", ids)
        self.assertNotIn("nc", ids)  # 2 hops away, excluded at depth=1

    def test_all_edges(self) -> None:
        self.reg.connect("na", "nb", ConnectionKind.CITES)
        self.reg.connect("nb", "nc", ConnectionKind.CITES)
        self.assertEqual(len(self.reg.all_edges()), 2)


class TestCaptureRegistryPersistence(unittest.TestCase):
    def test_dump_and_load_round_trip(self) -> None:
        reg = CaptureRegistry()
        reg.add(make_cap("koops-law", evidence_refs=["https://example.com"], tags=["scale"]))
        reg.add(make_cap("planetary-index", domain=Domain.MATERIALS))
        reg.connect("koops-law", "planetary-index", ConnectionKind.SUPPORTS)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)

        reg.dump(path)
        reg2 = CaptureRegistry.load(path)

        self.assertEqual(len(reg2), 2)
        self.assertIn("koops-law", reg2)
        cap = reg2.get("koops-law")
        self.assertEqual(cap.evidence_refs, ["https://example.com"])

    def test_dump_produces_valid_json(self) -> None:
        reg = CaptureRegistry()
        reg.add(make_cap("solo"))
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)
        reg.dump(path)
        data = json.loads(path.read_text())
        self.assertIn("captures", data)
        self.assertEqual(len(data["captures"]), 1)


if __name__ == "__main__":
    unittest.main()
