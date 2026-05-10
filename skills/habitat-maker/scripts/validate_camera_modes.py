#!/usr/bin/env python3
"""Validate habitat-maker observation-camera contracts.

The validator is intentionally schema-light and dependency-free. It checks the
parts of `geometry_params.json` that affect animal welfare and generator-backed
camera geometry:

* observation-camera mode enum
* primary interior-view camera fields
* optional secondary exterior-approach camera fields
* required camera welfare gates
* camera geometry manifest expectations

Exit codes:
    0 = valid
    1 = validation findings
    2 = invalid invocation or unreadable input
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_MODES = {
    "none",
    "interior_view",
    "exterior_approach",
    "interior_plus_exterior_approach",
}

CAMERA_WELFARE_GATES = {
    "electronics_isolation",
    "interior_heat",
    "interior_light",
    "moisture_control",
    "cable_routing",
    "service_independence",
    "non_disturbance",
}

INTERIOR_TESTS = {
    "dark_room_light_leak",
    "30_min_heat",
    "spray_test",
    "service_independence",
}

EXTERIOR_TESTS = {
    "dark_room_light_leak",
    "30_min_heat",
    "cable_drip_loop",
}

BASE_GEOMETRY_FEATURES = {
    "entrance_hole",
    "side_ventilation",
    "floor_drainage",
    "cleanout_access",
}

INTERIOR_GEOMETRY_FEATURES = {
    "interior_camera_pod",
    "sealed_viewport",
    "external_cable_gland",
}

EXTERIOR_GEOMETRY_FEATURES = {
    "exterior_approach_mount",
}


@dataclass
class Finding:
    path: str
    message: str


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"expected object at top level of {path}")
    return data


def require_bool_false(findings: list[Finding], obj: dict[str, Any], key: str, path: str) -> None:
    if obj.get(key) is not False:
        findings.append(Finding(f"{path}.{key}", "must be false"))


def require_non_empty_list(findings: list[Finding], obj: dict[str, Any], key: str, path: str) -> None:
    value = obj.get(key)
    if not isinstance(value, list) or not value:
        findings.append(Finding(f"{path}.{key}", "must be a non-empty list"))


def check_common_camera(findings: list[Finding], obj: dict[str, Any], path: str) -> None:
    require_bool_false(findings, obj, "electronics_inside_cavity", path)
    require_bool_false(findings, obj, "cable_route_enters_cavity", path)
    require_bool_false(findings, obj, "service_requires_opening_nest_cavity", path)
    require_non_empty_list(findings, obj, "disturbance_controls", path)
    require_non_empty_list(findings, obj, "validation_tests", path)


def check_primary_interior(findings: list[Finding], primary: Any) -> None:
    path = "camera_observation.primary"
    if not isinstance(primary, dict):
        findings.append(Finding(path, "is required for interior-view modes"))
        return
    if primary.get("mode") != "interior_view":
        findings.append(Finding(f"{path}.mode", "must be interior_view"))
    check_common_camera(findings, primary, path)
    require_bool_false(findings, primary, "visible_light_into_cavity", path)
    require_bool_false(findings, primary, "status_led_visible_to_cavity", path)
    require_non_empty_list(findings, primary, "moisture_barriers", path)
    max_w = primary.get("max_continuous_dissipation_w")
    if not isinstance(max_w, (int, float)) or max_w <= 0 or max_w > 3.0:
        findings.append(
            Finding(
                f"{path}.max_continuous_dissipation_w",
                "must be numeric and no greater than 3.0 W",
            )
        )
    tests = set(primary.get("validation_tests", []))
    missing_tests = INTERIOR_TESTS - tests
    if missing_tests:
        findings.append(
            Finding(f"{path}.validation_tests", f"missing tests: {sorted(missing_tests)}")
        )


def check_secondary_exterior(findings: list[Finding], secondary: Any, required: bool) -> None:
    path = "camera_observation.secondary"
    if not isinstance(secondary, dict):
        if required:
            findings.append(Finding(path, "is required for interior_plus_exterior_approach"))
        return
    enabled = secondary.get("enabled", required)
    if required and enabled is not True:
        findings.append(Finding(f"{path}.enabled", "must be true for combined mode"))
    if not enabled:
        return
    if secondary.get("mode") != "exterior_approach":
        findings.append(Finding(f"{path}.mode", "must be exterior_approach"))
    check_common_camera(findings, secondary, path)
    tests = set(secondary.get("validation_tests", []))
    missing_tests = EXTERIOR_TESTS - tests
    if missing_tests:
        findings.append(
            Finding(f"{path}.validation_tests", f"missing tests: {sorted(missing_tests)}")
        )


def check_welfare_gates(findings: list[Finding], params: dict[str, Any], mode: str) -> None:
    if mode == "none":
        return
    gates = params.get("welfare_gates")
    if not isinstance(gates, dict):
        findings.append(Finding("welfare_gates", "must be an object"))
        return
    missing = CAMERA_WELFARE_GATES - set(gates.keys())
    if missing:
        findings.append(Finding("welfare_gates", f"missing camera gates: {sorted(missing)}"))


def check_manifest(findings: list[Finding], packet: Path, mode: str) -> None:
    if mode == "none":
        return
    manifest_path = packet / "camera-geometry-manifest.json"
    manifest = load_json(manifest_path)
    if manifest.get("source_params") != "geometry_params.json":
        findings.append(
            Finding("camera-geometry-manifest.json.source_params", "must be geometry_params.json")
        )
    generated = manifest.get("generated_artifacts")
    if not isinstance(generated, list) or not generated:
        findings.append(
            Finding("camera-geometry-manifest.json.generated_artifacts", "must be non-empty")
        )
    generator = manifest.get("generator")
    if not isinstance(generator, str) or not generator:
        findings.append(Finding("camera-geometry-manifest.json.generator", "must be set"))

    features = set(manifest.get("required_features", []))
    expected = set(BASE_GEOMETRY_FEATURES)
    if mode in {"interior_view", "interior_plus_exterior_approach"}:
        expected |= INTERIOR_GEOMETRY_FEATURES
    if mode in {"exterior_approach", "interior_plus_exterior_approach"}:
        expected |= EXTERIOR_GEOMETRY_FEATURES
    missing = expected - features
    if missing:
        findings.append(
            Finding("camera-geometry-manifest.json.required_features", f"missing: {sorted(missing)}")
        )


def validate_packet(packet: Path) -> list[Finding]:
    params = load_json(packet / "geometry_params.json")
    findings: list[Finding] = []

    obs = params.get("camera_observation")
    if obs is None:
        return findings
    if not isinstance(obs, dict):
        return [Finding("camera_observation", "must be an object")]

    mode = obs.get("mode")
    if mode not in ALLOWED_MODES:
        findings.append(
            Finding("camera_observation.mode", f"must be one of {sorted(ALLOWED_MODES)}")
        )
        return findings

    if mode in {"interior_view", "interior_plus_exterior_approach"}:
        check_primary_interior(findings, obs.get("primary"))
    if mode == "exterior_approach":
        check_secondary_exterior(findings, obs.get("secondary", obs.get("primary")), required=True)
    if mode == "interior_plus_exterior_approach":
        check_secondary_exterior(findings, obs.get("secondary"), required=True)

    check_welfare_gates(findings, params, mode)
    check_manifest(findings, packet, mode)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", required=True, type=Path, help="packet folder to validate")
    args = parser.parse_args(argv)

    packet = args.packet.resolve()
    if not packet.is_dir():
        print(f"not a directory: {packet}")
        return 2

    try:
        findings = validate_packet(packet)
    except SystemExit as exc:
        print(exc)
        return 2

    if findings:
        print(f"camera-mode validation failed: {packet}")
        for finding in findings:
            print(f"- {finding.path}: {finding.message}")
        return 1

    print(f"camera-mode validation passed: {packet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
