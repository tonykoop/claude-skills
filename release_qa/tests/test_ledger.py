"""Tests for release_qa.ledger — append-only VerificationLedger."""
from __future__ import annotations

import hashlib
import json

import pytest

from release_qa.ledger import LedgerEntry, VerificationLedger


# ---------------------------------------------------------------------------
# LedgerEntry dataclass
# ---------------------------------------------------------------------------

def test_ledger_entry_fields():
    e = LedgerEntry(
        entry_id="entry_0",
        bundle_id="b1",
        timestamp="2026-06-19T00:00:00Z",
        event_type="gate_check",
        actor="system",
        payload={"gate": "version_valid"},
        signature="abc123",
    )
    assert e.entry_id == "entry_0"
    assert e.bundle_id == "b1"
    assert e.event_type == "gate_check"
    assert e.actor == "system"
    assert e.signature == "abc123"


def test_ledger_entry_to_dict():
    e = LedgerEntry(
        entry_id="entry_0",
        bundle_id="b1",
        timestamp="2026-06-19T00:00:00Z",
        event_type="gate_check",
        actor="system",
        payload={"gate": "ok"},
        signature="sig",
    )
    d = e.to_dict()
    assert d["entry_id"] == "entry_0"
    assert d["bundle_id"] == "b1"
    assert isinstance(d["payload"], dict)


# ---------------------------------------------------------------------------
# VerificationLedger — basic append
# ---------------------------------------------------------------------------

def test_ledger_append_returns_entry():
    ledger = VerificationLedger()
    entry = ledger.append(
        bundle_id="b1",
        event_type="gate_check",
        actor="system",
        payload={"gate": "manifest_complete", "passed": True},
        timestamp="2026-06-19T00:00:00Z",
    )
    assert isinstance(entry, LedgerEntry)
    assert entry.entry_id == "entry_0"
    assert entry.bundle_id == "b1"
    assert entry.event_type == "gate_check"


def test_ledger_sequential_ids():
    ledger = VerificationLedger()
    e0 = ledger.append("b1", "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    e1 = ledger.append("b1", "panel_review", "panel", {}, "2026-06-19T01:00:00Z")
    e2 = ledger.append("b1", "human_approval", "tony", {}, "2026-06-19T02:00:00Z")
    assert e0.entry_id == "entry_0"
    assert e1.entry_id == "entry_1"
    assert e2.entry_id == "entry_2"


def test_ledger_stores_payload():
    ledger = VerificationLedger()
    payload = {"gate": "version_valid", "passed": True, "score": 1.0}
    entry = ledger.append("b1", "gate_check", "sys", payload, "2026-06-19T00:00:00Z")
    assert entry.payload == payload


# ---------------------------------------------------------------------------
# VerificationLedger — entries_for
# ---------------------------------------------------------------------------

def test_entries_for_filters_by_bundle_id():
    ledger = VerificationLedger()
    ledger.append("b1", "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    ledger.append("b2", "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    ledger.append("b1", "panel_review", "panel", {}, "2026-06-19T01:00:00Z")

    b1_entries = ledger.entries_for("b1")
    assert len(b1_entries) == 2
    assert all(e.bundle_id == "b1" for e in b1_entries)


def test_entries_for_empty_bundle():
    ledger = VerificationLedger()
    ledger.append("b1", "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    assert ledger.entries_for("nonexistent") == []


def test_entries_for_preserves_order():
    ledger = VerificationLedger()
    ts = ["2026-06-19T00:00:00Z", "2026-06-19T01:00:00Z", "2026-06-19T02:00:00Z"]
    for i, t in enumerate(ts):
        ledger.append("b1", f"event_{i}", "sys", {}, t)
    entries = ledger.entries_for("b1")
    assert [e.event_type for e in entries] == ["event_0", "event_1", "event_2"]


# ---------------------------------------------------------------------------
# VerificationLedger — signature verification
# ---------------------------------------------------------------------------

def test_signature_computed_correctly():
    ledger = VerificationLedger()
    bid, etype, ts, actor = "b1", "gate_check", "2026-06-19T00:00:00Z", "system"
    entry = ledger.append(bid, etype, actor, {}, ts)
    expected = hashlib.sha256(f"{bid}:{etype}:{ts}:{actor}".encode()).hexdigest()
    assert entry.signature == expected


def test_verify_chain_valid():
    ledger = VerificationLedger()
    ledger.append("b1", "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    ledger.append("b1", "panel_review", "panel", {}, "2026-06-19T01:00:00Z")
    assert ledger.verify_chain("b1") is True


def test_verify_chain_tampered():
    ledger = VerificationLedger()
    entry = ledger.append("b1", "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    # Tamper directly
    entry.signature = "tampered_signature"
    assert ledger.verify_chain("b1") is False


def test_verify_chain_empty_bundle():
    ledger = VerificationLedger()
    # Empty = vacuously true
    assert ledger.verify_chain("nonexistent") is True


def test_verify_chain_multiple_bundles():
    ledger = VerificationLedger()
    ledger.append("b1", "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    ledger.append("b2", "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    assert ledger.verify_chain("b1") is True
    assert ledger.verify_chain("b2") is True


# ---------------------------------------------------------------------------
# VerificationLedger — export_json
# ---------------------------------------------------------------------------

def test_export_json_valid_json():
    ledger = VerificationLedger()
    ledger.append("b1", "gate_check", "sys", {"x": 1}, "2026-06-19T00:00:00Z")
    j = ledger.export_json("b1")
    data = json.loads(j)
    assert isinstance(data, list)
    assert len(data) == 1


def test_export_json_fields():
    ledger = VerificationLedger()
    ledger.append("b1", "human_approval", "tony", {"approved": True}, "2026-06-19T00:00:00Z")
    data = json.loads(ledger.export_json("b1"))
    entry = data[0]
    assert entry["bundle_id"] == "b1"
    assert entry["event_type"] == "human_approval"
    assert entry["actor"] == "tony"
    assert entry["payload"]["approved"] is True


def test_export_json_empty_bundle():
    ledger = VerificationLedger()
    j = ledger.export_json("nonexistent")
    assert json.loads(j) == []


def test_export_json_multiple_entries():
    ledger = VerificationLedger()
    for i in range(5):
        ledger.append("b1", f"event_{i}", "sys", {"i": i}, f"2026-06-19T0{i}:00:00Z")
    data = json.loads(ledger.export_json("b1"))
    assert len(data) == 5


# ---------------------------------------------------------------------------
# VerificationLedger — summary
# ---------------------------------------------------------------------------

def test_summary_counts_event_types():
    ledger = VerificationLedger()
    ledger.append("b1", "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    ledger.append("b1", "gate_check", "sys", {}, "2026-06-19T01:00:00Z")
    ledger.append("b1", "panel_review", "panel", {}, "2026-06-19T02:00:00Z")
    summary = ledger.summary("b1")
    assert summary["gate_check"] == 2
    assert summary["panel_review"] == 1


def test_summary_empty_bundle():
    ledger = VerificationLedger()
    assert ledger.summary("nonexistent") == {}


def test_summary_only_for_bundle():
    ledger = VerificationLedger()
    ledger.append("b1", "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    ledger.append("b2", "human_approval", "tony", {}, "2026-06-19T00:00:00Z")
    s1 = ledger.summary("b1")
    s2 = ledger.summary("b2")
    assert "gate_check" in s1
    assert "human_approval" not in s1
    assert "human_approval" in s2


def test_summary_all_event_types():
    ledger = VerificationLedger()
    for etype in ["gate_check", "panel_review", "human_approval", "state_transition"]:
        ledger.append("b1", etype, "sys", {}, "2026-06-19T00:00:00Z")
    summary = ledger.summary("b1")
    assert len(summary) == 4
    assert all(v == 1 for v in summary.values())


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_ledger_global_entries_count():
    ledger = VerificationLedger()
    for i in range(10):
        bid = f"bundle_{i % 3}"
        ledger.append(bid, "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    # Total 10 entries split across 3 bundles
    total = sum(len(ledger.entries_for(f"bundle_{i}")) for i in range(3))
    assert total == 10


def test_ledger_entry_ids_global_not_per_bundle():
    ledger = VerificationLedger()
    ledger.append("b1", "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    ledger.append("b2", "gate_check", "sys", {}, "2026-06-19T00:00:00Z")
    ledger.append("b1", "panel_review", "sys", {}, "2026-06-19T01:00:00Z")
    # Entry IDs are global, not per-bundle
    b1 = ledger.entries_for("b1")
    assert b1[0].entry_id == "entry_0"
    assert b1[1].entry_id == "entry_2"
