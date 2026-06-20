"""Governance Policy System — load YAML policies and evaluate against ReleaseBundle."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional

import yaml

from release_qa.manifest import ReleaseBundle

# Default policies directory relative to this file
_DEFAULT_POLICIES_DIR = Path(__file__).parent / "data" / "policies"


@dataclass
class Policy:
    id: str
    name: str
    applies_to: List[str]   # release types
    severity: str            # info / warning / error / blocker
    rule: Dict[str, Any]


@dataclass
class PolicyViolation:
    policy_id: str
    policy_name: str
    severity: str
    detail: str


class PolicyEngine:
    def __init__(self, policy_dir: Optional[str] = None):
        if policy_dir is None:
            self._policy_dir = _DEFAULT_POLICIES_DIR
        else:
            self._policy_dir = Path(policy_dir)
        self._policies: List[Policy] = []

    def load_policies(self) -> None:
        self._policies = []
        if not self._policy_dir.exists():
            return
        for yaml_file in sorted(self._policy_dir.glob("*.yaml")):
            with open(yaml_file, "r") as f:
                data = yaml.safe_load(f)
            if data:
                self._policies.append(Policy(
                    id=data["id"],
                    name=data["name"],
                    applies_to=data.get("applies_to", []),
                    severity=data.get("severity", "warning"),
                    rule=data.get("rule", {}),
                ))

    @property
    def policies(self) -> List[Policy]:
        return list(self._policies)

    def applicable_policies(self, release_type: str) -> List[Policy]:
        return [p for p in self._policies if release_type in p.applies_to]

    def evaluate(self, bundle: ReleaseBundle) -> List[PolicyViolation]:
        violations: List[PolicyViolation] = []
        applicable = self.applicable_policies(bundle.release_type)

        for policy in applicable:
            rule = policy.rule
            rule_type = rule.get("type", "")

            violation = self._evaluate_rule(policy, rule_type, rule, bundle)
            if violation:
                violations.append(violation)

        return violations

    def _evaluate_rule(
        self, policy: Policy, rule_type: str, rule: Dict[str, Any], bundle: ReleaseBundle
    ) -> Optional[PolicyViolation]:
        if rule_type == "artifact_required":
            required_type = rule.get("artifact_type", "")
            present = {a.artifact_type for a in bundle.artifacts}
            if required_type not in present:
                return PolicyViolation(
                    policy_id=policy.id,
                    policy_name=policy.name,
                    severity=policy.severity,
                    detail=f"Required artifact type '{required_type}' is not present in bundle.",
                )

        elif rule_type == "min_resolution":
            min_height = int(rule.get("min_height", 720))
            for a in bundle.artifacts:
                if a.artifact_type != "video":
                    continue
                if not a.resolution:
                    return PolicyViolation(
                        policy_id=policy.id,
                        policy_name=policy.name,
                        severity=policy.severity,
                        detail=f"Video artifact '{a.id}' has no resolution metadata.",
                    )
                try:
                    parts = a.resolution.lower().split("x")
                    height = int(parts[1]) if len(parts) >= 2 else 0
                    if height < min_height:
                        return PolicyViolation(
                            policy_id=policy.id,
                            policy_name=policy.name,
                            severity=policy.severity,
                            detail=f"Video artifact '{a.id}' resolution {a.resolution} is below minimum {min_height}p.",
                        )
                except (ValueError, IndexError):
                    return PolicyViolation(
                        policy_id=policy.id,
                        policy_name=policy.name,
                        severity=policy.severity,
                        detail=f"Video artifact '{a.id}' has unparseable resolution '{a.resolution}'.",
                    )

        elif rule_type == "prohibited_tags":
            keywords = [kw.lower() for kw in rule.get("keywords", [])]
            for tag in bundle.tags:
                if any(kw in tag.lower() for kw in keywords):
                    return PolicyViolation(
                        policy_id=policy.id,
                        policy_name=policy.name,
                        severity=policy.severity,
                        detail=f"Tag '{tag}' contains a prohibited keyword.",
                    )

        elif rule_type == "version_format":
            pattern = rule.get("pattern", r"^\d+\.\d+\.\d+(?:[-.].+)?$")
            if not re.match(pattern, bundle.version):
                return PolicyViolation(
                    policy_id=policy.id,
                    policy_name=policy.name,
                    severity=policy.severity,
                    detail=f"Version '{bundle.version}' does not match required format '{pattern}'.",
                )

        elif rule_type == "required_metadata_fields":
            required_fields = rule.get("fields", [])
            missing = [f for f in required_fields if f not in bundle.metadata]
            if missing:
                return PolicyViolation(
                    policy_id=policy.id,
                    policy_name=policy.name,
                    severity=policy.severity,
                    detail=f"Metadata is missing required fields: {missing}.",
                )

        elif rule_type == "artifact_size_limit":
            artifact_type = rule.get("artifact_type")
            max_bytes = int(rule.get("max_bytes", 0))
            for a in bundle.artifacts:
                if artifact_type and a.artifact_type != artifact_type:
                    continue
                if a.size_bytes > max_bytes:
                    return PolicyViolation(
                        policy_id=policy.id,
                        policy_name=policy.name,
                        severity=policy.severity,
                        detail=f"Artifact '{a.id}' ({a.artifact_type}) size {a.size_bytes} bytes exceeds limit {max_bytes} bytes.",
                    )

        elif rule_type == "min_artifact_count":
            min_count = int(rule.get("min_count", 1))
            if len(bundle.artifacts) < min_count:
                return PolicyViolation(
                    policy_id=policy.id,
                    policy_name=policy.name,
                    severity=policy.severity,
                    detail=f"Bundle has {len(bundle.artifacts)} artifact(s) but requires at least {min_count}.",
                )

        elif rule_type == "required_tags":
            if not bundle.tags:
                return PolicyViolation(
                    policy_id=policy.id,
                    policy_name=policy.name,
                    severity=policy.severity,
                    detail="Bundle has no tags.",
                )

        return None

    def is_release_blocked(self, bundle: ReleaseBundle) -> bool:
        violations = self.evaluate(bundle)
        blocking_severities = {"error", "blocker"}
        return any(v.severity in blocking_severities for v in violations)
