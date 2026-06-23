"""End-to-end multimedia release hook for the audio-dynamic engine.

SCHEMA_ID: playlist-builder/release-hook@1.0.0
VERSION    = "1.0.0"

Story #476 — Epic #471 (playlist-builder audio-dynamic).

See references/RELEASE_HOOK_CONTRACT.md for the full spec.

Usage
-----
    from scripts.release_hook import compile_release

    bundle = compile_release(
        mix_plan=mix_plan_dict_or_obj,
        choreo_script_path="path/to/choreo.md",
        output_dir="path/to/output/",
    )
    # bundle.bundle_dir    — where the files landed
    # bundle.provenance    — the provenance block dict
    # bundle.hook_sent     — True if StudioPipeline notified
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "1.0.0"
_SKILL_VERSION = f"playlist-builder/release-hook@{VERSION}"
_EPIC_REF = "tonykoop/claude-skills#471"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ReleaseBundle:
    routine_id: str
    bundle_dir: Path
    provenance: dict[str, Any]
    hook_sent: bool = False
    hook_warning: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "routine_id": self.routine_id,
            "bundle_dir": str(self.bundle_dir),
            "provenance": self.provenance,
            "hook_sent": self.hook_sent,
            "hook_warning": self.hook_warning,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256_of_str(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _now_utc_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_dict(mix_plan: Any) -> dict[str, Any]:
    """Accept a MixPlan object or a plain dict."""
    if hasattr(mix_plan, "to_dict"):
        return mix_plan.to_dict()
    if isinstance(mix_plan, dict):
        return mix_plan
    raise TypeError(f"mix_plan must be a MixPlan object or dict, got {type(mix_plan)}")


def _try_studio_handoff(
    routine_id: str,
    bundle_dir: Path,
    provenance: dict[str, Any],
) -> tuple[bool, str | None]:
    """POST bundle metadata to StudioPipeline if the hook URL is set.

    Returns (sent: bool, warning: str|None).
    Always non-blocking — errors become warnings.
    """
    hook_url = os.environ.get("STUDIOPIPELINE_HOOK_URL", "")
    if not hook_url:
        return False, None

    payload = json.dumps({
        "routine_id": routine_id,
        "bundle_dir": str(bundle_dir),
        "provenance": provenance,
        "source": _SKILL_VERSION,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            hook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10):
            return True, None
    except (urllib.error.URLError, OSError) as exc:
        warning = f"StudioPipeline hook failed: {exc}"
        print(f"[release_hook] WARNING: {warning}")
        return False, warning


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compile_release(
    mix_plan: Any,
    choreo_script_path: str | Path,
    output_dir: str | Path,
    *,
    timestamp: str | None = None,
) -> ReleaseBundle:
    """Compile a release bundle from *mix_plan* and *choreo_script_path*.

    Writes to *output_dir*:
    - ``choreo_script.md``      — verbatim copy of the choreography script
    - ``audio_mix_plan.json``   — MixPlan as JSON
    - ``provenance_block.json`` — IP-timestamp + SHA-256 fingerprints

    Then optionally POSTs to StudioPipeline if ``STUDIOPIPELINE_HOOK_URL`` is set.

    Args:
        mix_plan:           MixPlan object or dict (from movement_bridge).
        choreo_script_path: Path to the choreography Markdown script.
        output_dir:         Directory to write the bundle into (created if absent).
        timestamp:          Override the ``generated_at`` ISO-8601 timestamp (for tests).

    Returns:
        A ``ReleaseBundle`` with paths and provenance info.

    Raises:
        FileNotFoundError: if *choreo_script_path* does not exist.
    """
    choreo_path = Path(choreo_script_path).resolve()
    if not choreo_path.exists():
        raise FileNotFoundError(f"Choreography script not found: {choreo_path}")

    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy choreography script
    choreo_dest = out_dir / "choreo_script.md"
    shutil.copy2(choreo_path, choreo_dest)
    choreo_content = choreo_dest.read_text(encoding="utf-8")

    # 2. Write audio mix plan
    mix_dict = _to_dict(mix_plan)
    routine_id = mix_dict.get("routine_id", "unknown")
    mix_json = json.dumps(mix_dict, indent=2, ensure_ascii=False)
    mix_dest = out_dir / "audio_mix_plan.json"
    mix_dest.write_text(mix_json, encoding="utf-8")

    # 3. Build provenance block
    generated_at = timestamp or _now_utc_iso()
    provenance = {
        "routine_id": routine_id,
        "generated_at": generated_at,
        "choreo_script_sha256": _sha256_of_str(choreo_content),
        "audio_mix_plan_sha256": _sha256_of_str(mix_json),
        "epic": _EPIC_REF,
        "skill_version": _SKILL_VERSION,
    }
    prov_dest = out_dir / "provenance_block.json"
    prov_dest.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # 4. StudioPipeline handoff (non-blocking)
    hook_sent, hook_warning = _try_studio_handoff(routine_id, out_dir, provenance)

    return ReleaseBundle(
        routine_id=routine_id,
        bundle_dir=out_dir,
        provenance=provenance,
        hook_sent=hook_sent,
        hook_warning=hook_warning,
    )
