#!/usr/bin/env python3
"""image-gen-2 chapter asset-contract validator.

Validates a proposed chapter's asset sidecar metadata against the image-gen-2
chapter template contract defined in
`references/image-gen-2-chapter-template.md` (Refs #92, #100, #210).

Hard gates from the contract:
  * Every generated asset must carry all required sidecar fields.
  * `derivative: true` always — a generated asset is never source or evidence.
  * `non_dimensional: true` always — renders must not imply measurements.
  * `kind` must be one of the allowed concept kinds.
  * `review_state` must be `proof-reviewed` before a chapter may publish; any
    asset below that threshold blocks the chapter.
  * `packet_ref` must be present and non-empty (packet-first rule: chapter sits
    on top of a validated packet).
  * The two-source rule: authority artifacts in `authority_artifacts` may NOT
    carry `derivative: true` (they are load-bearing, not generated).

Pure stdlib; no network.

Input (JSON via --input FILE or stdin):
    {
      "chapter_id": "flute-v2",
      "chapter_framing": "design-book",
      "packet_ref": "abc1234",
      "assets": [
        {
          "asset_id": "flute-v2-cover",
          "kind": "cover",
          "prompt": "isometric technical illustration of a bamboo flute...",
          "derivative": true,
          "non_dimensional": true,
          "source_provenance": "synthetic",
          "packet_ref": "abc1234",
          "caption": "Bamboo Flute v2 design study",
          "alt_text": "Isometric render of a bamboo flute",
          "review_state": "proof-reviewed"
        }
      ],
      "authority_artifacts": [
        {
          "artifact_id": "flute-v2-params",
          "kind": "parameter-csv",
          "packet_ref": "abc1234"
        }
      ]
    }

Output (JSON to stdout):
    {
      "chapter_id": "flute-v2",
      "decision": "pass",
      "publishable": true,
      "asset_count": 1,
      "authority_artifact_count": 1,
      "violations": []
    }

CLI:
    image_chapter_validator.py --input chapter.json
    cat chapter.json | image_chapter_validator.py
    image_chapter_validator.py --input chapter.json --require-publishable
Exit 0 = pass (may still have non-blocking warnings).
Exit 1 = one or more contract violations.
Exit 2 = bad input.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

# --- contract constants -------------------------------------------------------

ALLOWED_KINDS = frozenset({
    "cover", "hero", "spread", "isometric-concept",
    "collage", "restoration", "mood",
})

REVIEW_ORDER = ["draft", "privacy-reviewed", "proof-reviewed"]

REQUIRED_ASSET_FIELDS = [
    "asset_id",
    "kind",
    "prompt",
    "derivative",
    "non_dimensional",
    "source_provenance",
    "packet_ref",
    "caption",
    "alt_text",
    "review_state",
]


# --- validation logic ---------------------------------------------------------

def _review_rank(state: str) -> int:
    try:
        return REVIEW_ORDER.index(state)
    except ValueError:
        return -1


def validate_asset(asset: dict, chapter_packet_ref: str | None) -> list[dict]:
    """Return a list of violation dicts for this asset (empty = valid)."""
    violations: list[dict] = []
    asset_id = asset.get("asset_id", "<unknown>")

    def v(field: str, message: str) -> None:
        violations.append({"asset_id": asset_id, "field": field, "message": message})

    # Required fields must be present and non-empty (except booleans which can be False).
    for field in REQUIRED_ASSET_FIELDS:
        val = asset.get(field)
        if val is None:
            v(field, f"required field '{field}' is missing")
        elif isinstance(val, str) and not val.strip():
            v(field, f"required field '{field}' is empty")

    # asset_id must be a non-empty string.
    if not isinstance(asset.get("asset_id"), str) or not asset.get("asset_id", "").strip():
        v("asset_id", "asset_id must be a non-empty string")

    # kind must be one of the allowed values.
    kind = asset.get("kind")
    if kind is not None and kind not in ALLOWED_KINDS:
        v("kind", f"kind '{kind}' is not allowed; must be one of: {sorted(ALLOWED_KINDS)}")

    # derivative must be exactly True.
    derivative = asset.get("derivative")
    if derivative is not True:
        v("derivative", f"derivative must be true (got {derivative!r}); generated assets are always derivatives")

    # non_dimensional must be exactly True.
    non_dimensional = asset.get("non_dimensional")
    if non_dimensional is not True:
        v("non_dimensional", f"non_dimensional must be true (got {non_dimensional!r}); renders must not imply measurements")

    # review_state must be a recognised value.
    review_state = asset.get("review_state")
    if isinstance(review_state, str):
        if _review_rank(review_state) < 0:
            v("review_state", f"review_state '{review_state}' is not valid; must be one of: {REVIEW_ORDER}")
    elif review_state is not None:
        v("review_state", f"review_state must be a string, got {type(review_state).__name__!r}")

    # packet_ref must match chapter-level packet_ref when both are provided.
    asset_packet = asset.get("packet_ref")
    if chapter_packet_ref and isinstance(asset_packet, str) and asset_packet.strip():
        if asset_packet.strip() != chapter_packet_ref.strip():
            v("packet_ref",
              f"asset packet_ref '{asset_packet}' does not match chapter packet_ref '{chapter_packet_ref}'")

    return violations


def validate_authority_artifact(artifact: dict) -> list[dict]:
    """Authority artifacts must NOT carry derivative: true (two-source rule)."""
    violations: list[dict] = []
    artifact_id = artifact.get("artifact_id", "<unknown>")

    def v(field: str, message: str) -> None:
        violations.append({"artifact_id": artifact_id, "field": field, "message": message})

    if artifact.get("derivative") is True:
        v("derivative",
          "authority artifacts must NOT carry derivative:true — they are load-bearing evidence, "
          "not generated concept imagery (two-source rule)")

    if not artifact.get("artifact_id"):
        v("artifact_id", "authority artifact missing required 'artifact_id' field")

    if not artifact.get("packet_ref"):
        v("packet_ref", "authority artifact missing required 'packet_ref' field")

    return violations


def validate_chapter(data: dict) -> dict:
    """Validate a full chapter manifest and return the result dict."""
    chapter_id = data.get("chapter_id", "<unknown>")
    packet_ref = data.get("packet_ref") or None
    assets = data.get("assets", [])
    authority_artifacts = data.get("authority_artifacts", [])

    all_violations: list[dict] = []

    # Chapter-level: packet_ref required (packet-first rule).
    if not packet_ref:
        all_violations.append({
            "asset_id": None,
            "field": "packet_ref",
            "message": "chapter-level packet_ref is required (packet-first rule: chapter must sit on a validated packet)",
        })

    # Validate each generated asset.
    publishable_blockers: list[dict] = []
    for asset in assets:
        if not isinstance(asset, dict):
            all_violations.append({"asset_id": None, "field": None, "message": f"asset entry is not a dict: {asset!r}"})
            continue
        asset_violations = validate_asset(asset, packet_ref)
        all_violations.extend(asset_violations)

        # Publishability check: any asset not at proof-reviewed blocks publication.
        review_state = asset.get("review_state")
        if _review_rank(str(review_state)) < _review_rank("proof-reviewed"):
            publishable_blockers.append({
                "asset_id": asset.get("asset_id", "<unknown>"),
                "field": "review_state",
                "message": (
                    f"review_state '{review_state}' is below 'proof-reviewed'; "
                    "no chapter may publish with assets below this threshold"
                ),
            })

    # Also include review blockers in violations so they appear in the report.
    all_violations.extend(publishable_blockers)

    # Validate authority artifacts (two-source rule).
    for artifact in authority_artifacts:
        if not isinstance(artifact, dict):
            continue
        all_violations.extend(validate_authority_artifact(artifact))

    publishable = len(publishable_blockers) == 0 and len(all_violations) == 0
    decision = "pass" if not all_violations else "fail"

    return {
        "chapter_id": chapter_id,
        "chapter_framing": data.get("chapter_framing", ""),
        "packet_ref": packet_ref,
        "decision": decision,
        "publishable": publishable,
        "asset_count": len(assets),
        "authority_artifact_count": len(authority_artifacts),
        "violations": all_violations,
    }


# --- CLI ---------------------------------------------------------------------

def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an image-gen-2 chapter manifest against the asset-contract."
    )
    parser.add_argument("--input", help="JSON file (else stdin).")
    parser.add_argument(
        "--require-publishable", action="store_true",
        help="Exit 1 if the chapter is valid but not yet publishable.",
    )
    args = parser.parse_args(argv)

    try:
        raw = sys.stdin.read() if not args.input else open(args.input, encoding="utf-8").read()
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not isinstance(data, dict):
        print("error: input must be a JSON object", file=sys.stderr)
        return 2

    result = validate_chapter(data)
    print(json.dumps(result, indent=2))

    if result["decision"] == "fail":
        return 1
    if args.require_publishable and not result["publishable"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
