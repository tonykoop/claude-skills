"""seed_corpus.py — Canonical seed captures drawn from Epic #213 stories.

These captures are structural examples that boot-strap the knowledge graph.
They reference the real issue sources (#204, #205, #206) and use domain
vocabulary from the issue bodies — no invented theory content.

Intended use::

    from bigthink.seed_corpus import build_seed_registry
    reg = build_seed_registry()

The returned registry is a fresh, pre-populated CaptureRegistry ready for
further use (query, connect, export, validate).
"""
from __future__ import annotations

from bigthink.registry import CaptureRegistry
from bigthink.schema import (
    CaptureConnection,
    ConnectionKind,
    Domain,
    ManufacturingTheoryCapture,
    MaturityLevel,
)


# ---------------------------------------------------------------------------
# Seed capture definitions
# (source fields reference the GitHub issue URLs so they are citable)
# ---------------------------------------------------------------------------

_SEED_CAPTURES: list[dict] = [
    {
        "id": "koops-law-v1",
        "thesis": (
            "Physical manufacturing capability scales not with calendar time "
            "but with Evaluated Spatial Complexity (S_e) following a power-law "
            "C = k * S_e^alpha, where alpha is a physical learning-rate "
            "coefficient. Every doubling of programmatically-graded, physically "
            "verified geometric variations accelerates multi-material "
            "manufacturing automation by a fixed efficiency percentage. "
            "MakerBench-HWE is positioned as the fitness function that "
            "empirically measures the curve, mapping onto the Kardashev "
            "scale (Type 0 to I/II) as the civilizational framing."
        ),
        "domain": Domain.SCALING_LAW,
        "maturity": MaturityLevel.SEED,
        "evidence_refs": [],
        "source": "github.com/tonykoop/claude-skills/issues/204",
        "tags": [
            "koop", "scaling-law", "spatial-complexity", "makerbench",
            "kardashev", "automation", "learning-rate",
        ],
        "promotion_target": "makerbench-hwe/docs/RFC",
    },
    {
        "id": "planetary-index-v1",
        "thesis": (
            "A baseline index of human manufacturing capability and planetary "
            "material reality enables AI design agents to make resource-aware "
            "strategic decisions before committing geometry. The index captures "
            "spatial extremes (min feature / max envelope per process), "
            "kinematic cadence (speed before deflection/warp), energetic "
            "threshold (J to alter state), and tolerance floor (sigma-capability). "
            "A Planetary Element Inventory layer tracks crustal abundance (A_c) "
            "and global run-rate per element to impose scarcity-penalty triage "
            "and force abundant-atom alternatives in the design pipeline."
        ),
        "domain": Domain.MATERIALS,
        "maturity": MaturityLevel.SEED,
        "evidence_refs": [],
        "source": "github.com/tonykoop/claude-skills/issues/205",
        "tags": [
            "planetary-inventory", "element-abundance", "scarcity",
            "cnc", "tolerance", "materials-index", "resource-aware",
        ],
        "promotion_target": "maker-engineering/makerbench-hwe (index schema)",
    },
    {
        "id": "evolution-pipeline-v1",
        "thesis": (
            "A second StudioPipeline plugin — the Evolution Pipeline — automates "
            "the hardware prototype lifecycle (PLM/DFM) across three engines: "
            "Alpha Workspace Compiler (downgrade master CAD to local tool matrix), "
            "Beta Vendor Broker (Xometry/Protolabs/Hubs instant-quote and DFM API "
            "auto trade-off report), and Production Master plus BOM/PLM (multi-level "
            "BOM, ECOs, flat patterns, GD&T PDFs synced to open PLM). It closes "
            "the digital-to-atoms loop and runs parallel to the studio-pipeline "
            "video plugin, converting fabrication logs into episode segments."
        ),
        "domain": Domain.PLM_DFM,
        "maturity": MaturityLevel.SEED,
        "evidence_refs": [],
        "source": "github.com/tonykoop/claude-skills/issues/206",
        "tags": [
            "plm", "dfm", "evolution-pipeline", "studiopipeline",
            "vendor-broker", "xometry", "bom", "prototype",
        ],
        "promotion_target": "makerspace skill extension or StudioPipeline/evolution repo",
    },
]

# Inter-capture connections reflecting stated relationships in the issue bodies
_SEED_CONNECTIONS: list[dict] = [
    {
        "from_id": "koops-law-v1",
        "to_id":   "planetary-index-v1",
        "kind":    ConnectionKind.SUPPORTS,
        "note":    "Koop's Law needs the planetary index as its dynamic constraint boundary",
    },
    {
        "from_id": "planetary-index-v1",
        "to_id":   "koops-law-v1",
        "kind":    ConnectionKind.SUPPORTS,
        "note":    "Index provides resource-aware limits that feed the S_e measurement",
    },
    {
        "from_id": "evolution-pipeline-v1",
        "to_id":   "planetary-index-v1",
        "kind":    ConnectionKind.EXTENDS,
        "note":    "Vendor Broker consumes capability limits from the materials index",
    },
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_seed_registry() -> CaptureRegistry:
    """Return a fresh CaptureRegistry pre-populated with the three seed captures.

    Connections reflecting the relationships stated in the issue bodies are
    added automatically.  The registry is fully functional — callers can
    add more captures, query, export, etc.
    """
    reg = CaptureRegistry()

    for cap_data in _SEED_CAPTURES:
        cap = ManufacturingTheoryCapture(
            id=cap_data["id"],
            thesis=cap_data["thesis"],
            domain=cap_data["domain"],
            maturity=cap_data["maturity"],
            evidence_refs=cap_data.get("evidence_refs", []),
            source=cap_data.get("source", ""),
            tags=cap_data.get("tags", []),
            promotion_target=cap_data.get("promotion_target", ""),
        )
        reg.add(cap)

    for conn_data in _SEED_CONNECTIONS:
        reg.connect(
            conn_data["from_id"],
            conn_data["to_id"],
            conn_data["kind"],
            note=conn_data.get("note", ""),
        )

    return reg


def seed_capture_ids() -> list[str]:
    """Return the ids of all seed captures (for tests and discovery)."""
    return [c["id"] for c in _SEED_CAPTURES]
