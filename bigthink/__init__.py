"""bigthink — Manufacturing Theory Capture KB engine.

Provides:
  schema     — ManufacturingTheoryCapture dataclass + MaturityLevel enum
  registry   — CaptureRegistry (add / query / filter / connect / graph)
  maturity   — MaturityModel (progression rules and evidence scoring)
  connections — ConnectionFinder (cross-pollination, keyword overlap, citation)
  validator  — CaptureValidator (schema + business-rule validation)
  cli        — command-line entry point
"""

from bigthink.schema import ManufacturingTheoryCapture, MaturityLevel, CaptureConnection
from bigthink.registry import CaptureRegistry
from bigthink.maturity import MaturityModel
from bigthink.connections import ConnectionFinder
from bigthink.validator import CaptureValidator

__all__ = [
    "ManufacturingTheoryCapture",
    "MaturityLevel",
    "CaptureConnection",
    "CaptureRegistry",
    "MaturityModel",
    "ConnectionFinder",
    "CaptureValidator",
]
