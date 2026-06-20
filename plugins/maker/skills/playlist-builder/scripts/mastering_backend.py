"""Thin client for the private mastering / MIR-critique / album-builder backend.

This module is the ONLY mastering-related code in the public repo.  It
contains:
  - A typed handoff schema (dataclasses, no Pydantic dependency)
  - A single ``call_mastering_backend()`` function that POSTs the payload and
    returns a structured result
  - Graceful degradation when the backend is unconfigured or unavailable

All mastering chains, MIR-critique scoring, and album-segmentation logic live
EXCLUSIVELY in the private ``tonykoop/StudioPipeline-Selecta`` backend.  This
file MUST NOT import or reimplement any of that logic.

See ``references/MASTERING_BACKEND_CONTRACT.md`` for the full handoff schema.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)

_ENV_URL = "PLAYLIST_MASTERING_BACKEND_URL"
_ENV_TOKEN = "PLAYLIST_MASTERING_BACKEND_TOKEN"

HANDOFF_SCHEMA = "mastering-handoff-v1"

_DEFAULT_TARGET_LUFS = -14.0
_DEFAULT_TRUE_PEAK_DBFS = -1.0
_DEFAULT_FORMAT = "album"


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclass
class MasteringTrack:
    """One track entry in the handoff payload."""

    phase: str
    bank: str
    search_string: str
    approx_duration_s: int
    exact_id_status: str
    spotify_uri: Optional[str] = None


@dataclass
class MasteringIntent:
    """Advisory mastering parameters — the private backend may override these."""

    target_lufs: float = _DEFAULT_TARGET_LUFS
    true_peak_dbfs: float = _DEFAULT_TRUE_PEAK_DBFS
    format: str = _DEFAULT_FORMAT


@dataclass
class MasteringHandoff:
    """Full handoff payload sent to the private backend."""

    playlist_id: str
    context: str
    tracks: list[MasteringTrack] = field(default_factory=list)
    mastering_intent: MasteringIntent = field(default_factory=MasteringIntent)
    schema: str = HANDOFF_SCHEMA


@dataclass
class MasteringBackendResult:
    """What the public skill receives back from the backend call.

    The public skill ONLY surfaces ``status``, ``job_id``, and ``output_url``
    to the user.  It never parses or re-emits chain parameters or scores.
    """

    available: bool
    status: str
    job_id: Optional[str] = None
    output_url: Optional[str] = None
    message: str = ""

    @property
    def succeeded(self) -> bool:
        return self.available and self.status == "ok"


# ---------------------------------------------------------------------------
# Backend discovery
# ---------------------------------------------------------------------------


def _backend_url() -> Optional[str]:
    return os.environ.get(_ENV_URL) or None


def _auth_headers() -> dict[str, str]:
    token = os.environ.get(_ENV_TOKEN)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def call_mastering_backend(handoff: MasteringHandoff) -> MasteringBackendResult:
    """POST the handoff payload to the private backend and return a result.

    Returns a result with ``available=False`` (without raising) when:
    - ``PLAYLIST_MASTERING_BACKEND_URL`` is not set
    - The backend returns a non-2xx status
    - A network or timeout error occurs
    """
    url = _backend_url()
    if not url:
        logger.info(
            "mastering backend not configured — set %s to enable", _ENV_URL
        )
        return MasteringBackendResult(
            available=False,
            status="unavailable",
            message="PLAYLIST_MASTERING_BACKEND_URL not set",
        )

    payload = json.dumps(_serialise(handoff)).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        **_auth_headers(),
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
            return MasteringBackendResult(
                available=True,
                status=body.get("status", "ok"),
                job_id=body.get("job_id"),
                output_url=body.get("output_url"),
                message=body.get("message", ""),
            )
    except urllib.error.HTTPError as exc:
        logger.warning("mastering backend HTTP %s: %s", exc.code, exc.reason)
        return MasteringBackendResult(
            available=False,
            status="error",
            message=f"HTTP {exc.code}: {exc.reason}",
        )
    except (urllib.error.URLError, OSError, ValueError) as exc:
        logger.warning("mastering backend unreachable: %s", exc)
        return MasteringBackendResult(
            available=False,
            status="error",
            message=str(exc),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _serialise(handoff: MasteringHandoff) -> dict[str, Any]:
    d = asdict(handoff)
    # Re-order so schema comes first (cosmetic, for readability).
    return {"schema": d.pop("schema"), **d}
