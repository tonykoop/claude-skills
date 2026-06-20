"""Thin public client for the private Aesthetic Synthesis Crawler (ASC) backend.

This module is the ONLY ASC-related code in the public repo.  It contains:
  - A typed ClipNote schema (dataclasses, stdlib-only — no Pydantic dependency)
  - A ClipHandoff wrapper used as the POST body
  - A single ``call_asc_backend()`` function that POSTs the payload and returns
    a structured result
  - Graceful degradation when the backend is unconfigured or unavailable

All ASC matrix routing, selector scoring, and curation pipeline logic lives
EXCLUSIVELY in the private ``tonykoop/StudioPipeline-Selecta`` backend.  This
file MUST NOT import or reimplement any of that logic.

See ``references/ASC_BACKEND_CONTRACT.md`` for the full handoff schema.
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

_ENV_URL = "CLIP_HARVESTER_BACKEND_URL"
_ENV_TOKEN = "CLIP_HARVESTER_BACKEND_TOKEN"

HANDOFF_SCHEMA = "asc-handoff-v1"

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclass
class ClipNote:
    """Normalised representation of a clipped social-feed post or screenshot.

    Required fields must be supplied; optional fields default to None / empty.
    The agent (Claude) fills this from vision extraction and/or the user's text.
    """

    note_id: str
    source_type: str  # "screenshot" | "text_clip" | "url_clip"
    captured_at: str  # ISO-8601 UTC
    raw_text: str
    tags: list[str] = field(default_factory=list)

    # optional
    platform: Optional[str] = None  # instagram|tiktok|pinterest|youtube|twitter|reddit|other
    source_url: Optional[str] = None
    author: Optional[str] = None
    media_paths: list[str] = field(default_factory=list)
    media_description: Optional[str] = None
    engagement: dict[str, str] = field(default_factory=dict)


@dataclass
class ClipHandoff:
    """Payload posted to the private ASC backend."""

    note: ClipNote
    routing_hint: Optional[str] = None
    schema: str = HANDOFF_SCHEMA


@dataclass
class ClipBackendResult:
    """What the public skill receives back from the backend call."""

    available: bool
    status: str
    job_id: Optional[str] = None
    output_url: Optional[str] = None
    message: str = ""

    @property
    def succeeded(self) -> bool:
        return self.available and self.status in ("ok", "queued")


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


def call_asc_backend(handoff: ClipHandoff) -> ClipBackendResult:
    """POST the ClipHandoff payload to the private ASC backend.

    Returns ``ClipBackendResult(available=False)`` (without raising) when:
    - ``CLIP_HARVESTER_BACKEND_URL`` is not set
    - The backend returns a non-2xx status
    - A network or timeout error occurs
    """
    url = _backend_url()
    if not url:
        logger.info(
            "ASC backend not configured — set %s to enable", _ENV_URL
        )
        return ClipBackendResult(
            available=False,
            status="unavailable",
            message="CLIP_HARVESTER_BACKEND_URL not set",
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
            return ClipBackendResult(
                available=True,
                status=body.get("status", "ok"),
                job_id=body.get("job_id"),
                output_url=body.get("output_url"),
                message=body.get("message", ""),
            )
    except urllib.error.HTTPError as exc:
        logger.warning("ASC backend HTTP %s: %s", exc.code, exc.reason)
        return ClipBackendResult(
            available=False,
            status="error",
            message=f"HTTP {exc.code}: {exc.reason}",
        )
    except (urllib.error.URLError, OSError, ValueError) as exc:
        logger.warning("ASC backend unreachable: %s", exc)
        return ClipBackendResult(
            available=False,
            status="error",
            message=str(exc),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _serialise(handoff: ClipHandoff) -> dict[str, Any]:
    d = asdict(handoff)
    return {"schema": d.pop("schema"), **d}
