"""Append-only verification evidence ledger."""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class LedgerEntry:
    entry_id: str        # "entry_0", "entry_1", etc.
    bundle_id: str
    timestamp: str       # ISO string passed in
    event_type: str      # gate_check/panel_review/human_approval/state_transition
    actor: str
    payload: Dict[str, Any]
    signature: str       # sha256 of "bundle_id:event_type:timestamp:actor"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VerificationLedger:
    def __init__(self):
        self._entries: List[LedgerEntry] = []

    def _compute_signature(self, bundle_id: str, event_type: str, timestamp: str, actor: str) -> str:
        raw = f"{bundle_id}:{event_type}:{timestamp}:{actor}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def append(self, bundle_id: str, event_type: str, actor: str, payload: Dict[str, Any], timestamp: str) -> LedgerEntry:
        entry_id = f"entry_{len(self._entries)}"
        sig = self._compute_signature(bundle_id, event_type, timestamp, actor)
        entry = LedgerEntry(
            entry_id=entry_id,
            bundle_id=bundle_id,
            timestamp=timestamp,
            event_type=event_type,
            actor=actor,
            payload=payload,
            signature=sig,
        )
        self._entries.append(entry)
        return entry

    def entries_for(self, bundle_id: str) -> List[LedgerEntry]:
        return [e for e in self._entries if e.bundle_id == bundle_id]

    def verify_chain(self, bundle_id: str) -> bool:
        for e in self.entries_for(bundle_id):
            expected = self._compute_signature(e.bundle_id, e.event_type, e.timestamp, e.actor)
            if e.signature != expected:
                return False
        return True

    def export_json(self, bundle_id: str) -> str:
        return json.dumps([e.to_dict() for e in self.entries_for(bundle_id)], indent=2)

    def summary(self, bundle_id: str) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for e in self.entries_for(bundle_id):
            counts[e.event_type] = counts.get(e.event_type, 0) + 1
        return counts
