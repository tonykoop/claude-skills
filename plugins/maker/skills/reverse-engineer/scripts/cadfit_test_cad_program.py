#!/usr/bin/env python3
"""Safe CADFit-shaped test_cad_program scoring adapter."""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def cadquery_available() -> bool:
    return importlib.util.find_spec("cadquery") is not None


def _literal_mock_result(tree: ast.AST) -> dict[str, float] | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            names = [target.id for target in node.targets if isinstance(target, ast.Name)]
            if "CADFIT_MOCK_RESULT" not in names:
                continue
            value = ast.literal_eval(node.value)
            return {key: float(value[key]) for key in ("candidate_volume", "target_volume", "intersection_volume")}
    return None


def _iou(candidate_volume: float, target_volume: float, intersection_volume: float) -> float:
    union = candidate_volume + target_volume - intersection_volume
    if union <= 0:
        return 0.0
    return max(0.0, min(1.0, intersection_volume / union))


def test_cad_program(program_path: Path, *, require_kernel: bool = False) -> dict[str, Any]:
    source = program_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(program_path))
        compile(tree, str(program_path), "exec")
    except SyntaxError as exc:
        return {
            "status": "invalid_program",
            "invalid_ratio": 1.0,
            "volumetric_iou": 0.0,
            "kernel_available": cadquery_available(),
            "findings": [f"syntax error: {exc.msg}"],
        }

    if "CADFIT_KERNEL_FAILURE" in source:
        return {
            "status": "kernel_failure",
            "invalid_ratio": 1.0,
            "volumetric_iou": 0.0,
            "kernel_available": cadquery_available(),
            "findings": ["kernel failure signal returned as scoring data"],
        }

    mock = _literal_mock_result(tree)
    if mock is not None:
        return {
            "status": "ok",
            "invalid_ratio": 0.0,
            "volumetric_iou": _iou(**mock),
            "kernel_available": cadquery_available(),
            "findings": ["scored from CADFIT_MOCK_RESULT fixture; not real kernel IoU"],
        }

    if require_kernel and not cadquery_available():
        return {
            "status": "kernel_unavailable",
            "invalid_ratio": 1.0,
            "volumetric_iou": 0.0,
            "kernel_available": False,
            "findings": ["cadquery/OpenCascade is not available in this runtime"],
        }

    return {
        "status": "kernel_unavailable" if not cadquery_available() else "ok",
        "invalid_ratio": 1.0 if not cadquery_available() else 0.0,
        "volumetric_iou": 0.0,
        "kernel_available": cadquery_available(),
        "findings": [
            "candidate compiles, but no real target/kernel score was produced by the public adapter"
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Return CADFit-shaped score feedback for a CadQuery program.")
    parser.add_argument("program", type=Path)
    parser.add_argument("--require-kernel", action="store_true")
    args = parser.parse_args(argv)

    result = test_cad_program(args.program, require_kernel=args.require_kernel)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
