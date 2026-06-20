"""graph_export.py — Knowledge graph export in multiple formats.

Exports the CaptureRegistry knowledge graph to:
  - DOT (Graphviz) — for visualization with dot/neato/fdp
  - JSON adjacency list — for web-based graph renderers (D3, Cytoscape)
  - Mermaid flowchart — for embedding in Markdown documentation

None of these functions mutate the registry.
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from bigthink.schema import ConnectionKind, MaturityLevel

if TYPE_CHECKING:
    from bigthink.registry import CaptureRegistry


# ---------------------------------------------------------------------------
# Colour / style maps
# ---------------------------------------------------------------------------

_MATURITY_COLOUR: dict[MaturityLevel, str] = {
    MaturityLevel.SEED:       "#fffde7",   # light yellow
    MaturityLevel.DEVELOPING: "#e3f2fd",   # light blue
    MaturityLevel.VALIDATED:  "#e8f5e9",   # light green
}

_EDGE_STYLE: dict[ConnectionKind, tuple[str, str]] = {
    # (DOT style, DOT colour)
    ConnectionKind.SUPPORTS:      ("solid",  "#2196F3"),
    ConnectionKind.CONTRADICTS:   ("dashed", "#f44336"),
    ConnectionKind.EXTENDS:       ("solid",  "#4CAF50"),
    ConnectionKind.SHARES_DOMAIN: ("dotted", "#9E9E9E"),
    ConnectionKind.CITES:         ("bold",   "#FF9800"),
}

_MERMAID_ARROW: dict[ConnectionKind, str] = {
    ConnectionKind.SUPPORTS:      "-->",
    ConnectionKind.CONTRADICTS:   "-.-x",
    ConnectionKind.EXTENDS:       "==>",
    ConnectionKind.SHARES_DOMAIN: "-.->",
    ConnectionKind.CITES:         "--o",
}


# ---------------------------------------------------------------------------
# DOT export
# ---------------------------------------------------------------------------

def to_dot(registry: "CaptureRegistry", *, graph_name: str = "bigthink") -> str:
    """Return a Graphviz DOT string representing the knowledge graph.

    Args:
        registry:   The ``CaptureRegistry`` to export.
        graph_name: Name attribute for the DOT digraph node.

    Returns:
        A DOT-language string suitable for piping to ``dot -Tsvg``.
    """
    lines: list[str] = [
        f'digraph "{graph_name}" {{',
        "  rankdir=LR;",
        "  node [shape=box, style=filled, fontname=Helvetica, fontsize=10];",
        "  edge [fontname=Helvetica, fontsize=9];",
        "",
    ]

    # Nodes
    for cap in registry:
        colour = _MATURITY_COLOUR.get(cap.maturity, "#ffffff")
        # Escape quotes in label
        label = cap.id.replace('"', '\\"')
        domain = cap.domain.value.replace("_", "-")
        lines.append(
            f'  "{cap.id}" [label="{label}\\n[{domain}]", '
            f'fillcolor="{colour}", tooltip="{cap.maturity.value}"];'
        )

    lines.append("")

    # Edges
    for edge in registry.all_edges():
        style, colour = _EDGE_STYLE.get(edge.kind, ("solid", "#000000"))
        note = edge.note[:30] + "…" if len(edge.note) > 30 else edge.note
        label_part = f', label="{edge.kind.value}"' if not note else (
            f', label="{edge.kind.value}: {note}"'
        )
        lines.append(
            f'  "{edge.from_id}" -> "{edge.to_id}" '
            f'[style={style}, color="{colour}"{label_part}];'
        )

    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# JSON adjacency list
# ---------------------------------------------------------------------------

def to_json(registry: "CaptureRegistry") -> str:
    """Return a JSON string with nodes and edges for web graph renderers.

    Schema::

        {
          "nodes": [
            { "id": "koops-law", "domain": "scaling_law",
              "maturity": "seed", "thesis_excerpt": "..." }
          ],
          "edges": [
            { "from": "koops-law", "to": "planet-idx",
              "kind": "supports", "note": "" }
          ]
        }
    """
    nodes = [
        {
            "id":            cap.id,
            "domain":        cap.domain.value,
            "maturity":      cap.maturity.value,
            "tags":          cap.tags,
            "thesis_excerpt": cap.thesis[:120] + ("…" if len(cap.thesis) > 120 else ""),
        }
        for cap in registry
    ]
    edges = [
        {
            "from": e.from_id,
            "to":   e.to_id,
            "kind": e.kind.value,
            "note": e.note,
        }
        for e in registry.all_edges()
    ]
    return json.dumps({"nodes": nodes, "edges": edges}, indent=2)


# ---------------------------------------------------------------------------
# Mermaid flowchart
# ---------------------------------------------------------------------------

def to_mermaid(registry: "CaptureRegistry") -> str:
    """Return a Mermaid flowchart string.

    Each node is labeled ``id\\n[domain]``.  Maturity is encoded in a class.
    Suitable for embedding in GitHub-flavoured Markdown fenced code blocks.

    Example output::

        flowchart LR
          koops-law["koops-law\\n[scaling-law]"]:::seed
          koops-law --> planet-idx
          classDef seed fill:#fffde7
          classDef developing fill:#e3f2fd
          classDef validated fill:#e8f5e9
    """
    lines = ["flowchart LR"]

    # Node declarations with class
    for cap in registry:
        safe_id    = cap.id.replace("-", "_")
        domain     = cap.domain.value.replace("_", "-")
        label      = f'{cap.id}\\n[{domain}]'
        maturity_class = cap.maturity.value
        lines.append(f'  {safe_id}["{label}"]:::{maturity_class}')

    lines.append("")

    # Edge declarations
    seen_pairs: set[tuple[str, str]] = set()
    for edge in registry.all_edges():
        from_safe = edge.from_id.replace("-", "_")
        to_safe   = edge.to_id.replace("-", "_")
        arrow = _MERMAID_ARROW.get(edge.kind, "-->")
        pair = (from_safe, to_safe)
        if pair not in seen_pairs:
            note = f"|{edge.kind.value}|" if arrow in ("-->", "==>") else ""
            lines.append(f"  {from_safe} {arrow}{note} {to_safe}")
            seen_pairs.add(pair)

    lines.append("")

    # Class definitions
    for maturity, colour in _MATURITY_COLOUR.items():
        lines.append(f"  classDef {maturity.value} fill:{colour}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI helper — register with bigthink.cli
# ---------------------------------------------------------------------------

EXPORT_FORMATS = {
    "dot":     to_dot,
    "json":    to_json,
    "mermaid": to_mermaid,
}
