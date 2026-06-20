"""bigthink — Manufacturing Theory Capture KB engine.

Provides:
  schema              — ManufacturingTheoryCapture dataclass + MaturityLevel enum
  registry            — CaptureRegistry (add / query / filter / connect / graph)
  maturity            — MaturityModel (progression rules and evidence scoring)
  connections         — ConnectionFinder (cross-pollination, keyword overlap, citation)
  validator           — CaptureValidator (schema + business-rule validation)
  graph_export        — to_dot / to_json / to_mermaid graph renderers
  seed_corpus         — build_seed_registry() from Epic #213 stories
  batch_import        — BatchImporter (YAML/JSON bulk ingest, dry-run)
  search_index        — SearchIndex (inverted index, AND/OR queries)
  promotion_pipeline  — PromotionPipeline (audit + batch advance runner)
  cli / __main__      — command-line entry point (python -m bigthink)
"""

from bigthink.schema import ManufacturingTheoryCapture, MaturityLevel, CaptureConnection
from bigthink.registry import CaptureRegistry
from bigthink.maturity import MaturityModel
from bigthink.connections import ConnectionFinder
from bigthink.validator import CaptureValidator
from bigthink.graph_export import to_dot, to_json, to_mermaid
from bigthink.seed_corpus import build_seed_registry
from bigthink.batch_import import BatchImporter
from bigthink.search_index import SearchIndex
from bigthink.promotion_pipeline import PromotionPipeline

__all__ = [
    "ManufacturingTheoryCapture",
    "MaturityLevel",
    "CaptureConnection",
    "CaptureRegistry",
    "MaturityModel",
    "ConnectionFinder",
    "CaptureValidator",
    "to_dot",
    "to_json",
    "to_mermaid",
    "build_seed_registry",
    "BatchImporter",
    "SearchIndex",
    "PromotionPipeline",
]
