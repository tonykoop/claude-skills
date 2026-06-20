#!/usr/bin/env python3
"""Structured feature-extractor boundary for CADFit-style mesh workflows."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


MESH_EXTENSIONS = {".stl", ".obj", ".ply", ".off", ".step", ".stp"}
AXIS_VECTORS = {
    "x": [1.0, 0.0, 0.0],
    "y": [0.0, 1.0, 0.0],
    "z": [0.0, 0.0, 1.0],
}


def load_metadata(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def usable_mesh(path: Path | None) -> tuple[bool, list[str]]:
    findings: list[str] = []
    if path is None:
        return False, ["no mesh_path supplied; CADFit branch requires a watertight mesh or point cloud"]
    if path.suffix.lower() not in MESH_EXTENSIONS:
        findings.append(f"unsupported mesh extension {path.suffix!r}")
    if not path.exists():
        findings.append(f"mesh_path does not exist: {path}")
    return not findings, findings


def bbox_profiles(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    bbox = metadata.get("bbox") or {}
    if not bbox:
        return []
    x = float(bbox.get("x", 0))
    y = float(bbox.get("y", 0))
    z = float(bbox.get("z", 0))
    dims = sorted([("x", x), ("y", y), ("z", z)], key=lambda item: item[1], reverse=True)
    profile = "rectangular_prism"
    if len({round(x, 3), round(y, 3), round(z, 3)}) == 1:
        profile = "cube_like"
    elif min(x, y, z) > 0 and dims[0][1] / max(dims[-1][1], 1e-9) > 3:
        profile = "long_extrusion"
    return [
        {
            "id": "bbox-primary-profile",
            "profile": profile,
            "evidence": "metadata.bbox proportions",
            "confidence": "medium",
        }
    ]


def slicing_planes(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    supplied = metadata.get("planar_sections") or []
    planes = [
        {
            "id": f"supplied-plane-{index}",
            "axis": item.get("axis", "z"),
            "offset": float(item.get("offset", 0)),
            "profile": item.get("profile", "unknown"),
            "evidence": "metadata.planar_sections",
        }
        for index, item in enumerate(supplied)
    ]
    if planes:
        return planes
    bbox = metadata.get("bbox") or {}
    if not bbox:
        return []
    return [
        {"id": "midplane-x", "axis": "x", "offset": float(bbox.get("x", 0)) / 2, "profile": "unknown", "evidence": "bbox midpoint"},
        {"id": "midplane-y", "axis": "y", "offset": float(bbox.get("y", 0)) / 2, "profile": "unknown", "evidence": "bbox midpoint"},
        {"id": "midplane-z", "axis": "z", "offset": float(bbox.get("z", 0)) / 2, "profile": "unknown", "evidence": "bbox midpoint"},
    ]


def revolution_axes(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    axes = metadata.get("symmetry_axes") or []
    return [
        {
            "id": f"symmetry-axis-{axis}",
            "axis": axis,
            "vector": AXIS_VECTORS.get(axis, [0.0, 0.0, 0.0]),
            "evidence": "metadata.symmetry_axes",
            "confidence": "medium" if axis in AXIS_VECTORS else "low",
        }
        for axis in axes
    ]


def extract_features(mesh_path: Path | None, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata = metadata or {}
    ok, findings = usable_mesh(mesh_path)
    watertight = metadata.get("watertight")
    if ok and watertight is False:
        findings.append("mesh metadata says watertight=false; CADFit needs watertight or repaired mesh input")

    status = "ok" if ok and not findings else "degraded"
    return {
        "status": status,
        "mesh": {
            "path": str(mesh_path) if mesh_path else "",
            "extension": mesh_path.suffix.lower() if mesh_path else "",
            "exists": bool(mesh_path and mesh_path.exists()),
            "watertight": watertight,
            "units": metadata.get("units", ""),
            "bbox": metadata.get("bbox", {}),
        },
        "candidate_sketch_profiles": bbox_profiles(metadata),
        "slicing_planes": slicing_planes(metadata),
        "revolution_axes": revolution_axes(metadata),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract structured CADFit-style feature candidates.")
    parser.add_argument("--mesh", type=Path, default=None)
    parser.add_argument("--metadata", type=Path, default=None)
    args = parser.parse_args(argv)

    result = extract_features(args.mesh, load_metadata(args.metadata))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
