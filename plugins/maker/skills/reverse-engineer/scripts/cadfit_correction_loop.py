#!/usr/bin/env python3
"""Error-guided CADFit correction and pruning helpers."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_TARGET_IOU = 0.92
DEFAULT_MAX_ITERATIONS = 8
DEFAULT_PRUNE_TOLERANCE = 0.01


def correction_actions(score: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    status = score.get("status", "ok")
    if status in {"kernel_failure", "invalid_program"}:
        return [
            {
                "action": "simplify",
                "reason": "kernel/program failure",
                "target": "last risky operation",
            }
        ]

    for residual in score.get("residuals", []):
        kind = residual.get("kind")
        region = residual.get("region", "unknown")
        if kind == "over_reconstruction":
            actions.append({"action": "cut", "target": region, "reason": "extra candidate material"})
        elif kind == "under_reconstruction":
            actions.append({"action": "union", "target": region, "reason": "missing candidate material"})

    if not actions and float(score.get("volumetric_iou", 0)) < DEFAULT_TARGET_IOU:
        actions.append({"action": "reextract_features", "target": "global", "reason": "low IoU without residual labels"})
    return actions


def should_terminate(
    score: dict[str, Any],
    *,
    iteration: int,
    target_iou: float = DEFAULT_TARGET_IOU,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if float(score.get("volumetric_iou", 0)) >= target_iou:
        reasons.append("target IoU reached")
    if iteration >= max_iterations:
        reasons.append("max iterations reached")
    if score.get("status") == "kernel_unavailable":
        reasons.append("kernel unavailable")
    if score.get("manufacturing_review") == "unresolved":
        reasons.append("manufacturing review unresolved")
    return bool(reasons), reasons


def backward_prune(
    operations: list[dict[str, Any]],
    *,
    prune_tolerance: float = DEFAULT_PRUNE_TOLERANCE,
) -> dict[str, Any]:
    kept = []
    dropped = []
    for operation in reversed(operations):
        delta = float(operation.get("iou_delta_without", 1.0))
        critical = bool(operation.get("manufacturing_critical", False))
        if not critical and delta <= prune_tolerance:
            dropped.append({**operation, "drop_reason": "IoU loss within prune tolerance"})
        else:
            kept.append(operation)
    kept.reverse()
    dropped.reverse()
    return {"kept_operations": kept, "dropped_operations": dropped}


def run_loop_plan(payload: dict[str, Any]) -> dict[str, Any]:
    score = payload.get("score", {})
    terminate, reasons = should_terminate(score, iteration=int(payload.get("iteration", 0)))
    return {
        "terminate": terminate,
        "termination_reasons": reasons,
        "correction_actions": [] if terminate else correction_actions(score),
        "pruning": backward_prune(payload.get("operations", [])),
        "manufacturing_guardrail": (
            "human manufacturing review required before builder-ready handoff; IoU alone is not correctness"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan CADFit error-guided correction and pruning.")
    parser.add_argument("score_payload", type=Path)
    args = parser.parse_args(argv)

    payload = json.loads(args.score_payload.read_text(encoding="utf-8"))
    print(json.dumps(run_loop_plan(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
