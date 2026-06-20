"""
archive_recovery.project_router
================================
Project routing: given a classified ArchiveItem list and a set of
known destination repos, decide WHERE each project should land.

Story #54 — Betabrand shacket → sewing repo organization.

The project router maps inferred project names onto "destination repos"
using:
  1. Keyword rules (project name contains "shacket" → "sewing" repo)
  2. Dominant FileKind (a project with mostly CAD → "cad-projects" repo)
  3. Configurable explicit overrides (project "synth_v2" → "electronics" repo)

The router is purely data-driven — no I/O, no filesystem access.  All
mapping rules are supplied by the caller.

RoutingDecision
---------------
One routing decision per project:
  destination_repo   : target repo slug (e.g. "sewing", "cad-projects")
  confidence         : "high" (explicit override or keyword match) |
                       "medium" (dominant kind match) |
                       "low" (fallback)
  rule_used          : human-readable description of the rule that fired
  sub_path           : suggested sub-path within the repo
                       (e.g. "projects/2015-betabrand-shacket/")
"""

from __future__ import annotations

from collections import Counter

from pydantic import BaseModel

from archive_recovery.models import ArchiveItem, FileKind


# ---------------------------------------------------------------------------
# Rule models
# ---------------------------------------------------------------------------

class KeywordRule(BaseModel):
    """Match a project name by case-insensitive substring."""
    pattern: str
    destination_repo: str
    sub_path_template: str = "projects/{project}/"


class KindRule(BaseModel):
    """Match a project by its dominant FileKind."""
    kind: FileKind
    destination_repo: str
    sub_path_template: str = "projects/{project}/"


class RouterConfig(BaseModel):
    """Full router configuration."""
    keyword_rules: list[KeywordRule] = []
    kind_rules: list[KindRule] = []
    explicit_overrides: dict[str, str] = {}
    fallback_repo: str = "archive-misc"


# ---------------------------------------------------------------------------
# Decision model
# ---------------------------------------------------------------------------

class RoutingDecision(BaseModel):
    """One routing decision per project."""
    project: str
    destination_repo: str
    sub_path: str
    confidence: str  # "high" | "medium" | "low"
    rule_used: str
    item_count: int = 0
    dominant_kind: FileKind = FileKind.UNKNOWN


# ---------------------------------------------------------------------------
# Tie-break priority (index = lower is higher priority)
# ---------------------------------------------------------------------------

_KIND_PRIORITY: list[FileKind] = [
    FileKind.CAD,
    FileKind.CODE,
    FileKind.DOC,
    FileKind.PHOTO,
    FileKind.MEDIA,
    FileKind.UNKNOWN,
]


def _dominant_kind(items: list[ArchiveItem]) -> FileKind:
    """
    Return the most common FileKind among items, excluding UNKNOWN.
    Tie-break: CAD > CODE > DOC > PHOTO > MEDIA (UNKNOWN last).
    If all items are UNKNOWN (or list is empty), return UNKNOWN.
    """
    counts: Counter[FileKind] = Counter()
    for item in items:
        if item.kind != FileKind.UNKNOWN:
            counts[item.kind] += 1

    if not counts:
        return FileKind.UNKNOWN

    max_count = max(counts.values())
    candidates = [k for k, v in counts.items() if v == max_count]

    # pick highest-priority candidate
    for kind in _KIND_PRIORITY:
        if kind in candidates:
            return kind
    return FileKind.UNKNOWN  # should not reach here


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

class ProjectRouter:
    def __init__(self, config: RouterConfig | None = None) -> None:
        self.config = config or RouterConfig()

    def route(self, project: str, items: list[ArchiveItem]) -> RoutingDecision:
        """
        Determine the destination repo for a project.

        Priority:
          1. Explicit override → "high"
          2. Keyword rules (first match) → "high"
          3. Dominant kind via kind_rules → "medium"
          4. Fallback repo → "low"
        """
        cfg = self.config
        dom_kind = _dominant_kind(items)

        # 1. Explicit override
        if project in cfg.explicit_overrides:
            repo = cfg.explicit_overrides[project]
            sub_path = f"projects/{project}/"
            return RoutingDecision(
                project=project,
                destination_repo=repo,
                sub_path=sub_path,
                confidence="high",
                rule_used="explicit override",
                item_count=len(items),
                dominant_kind=dom_kind,
            )

        # 2. Keyword rules
        project_lower = project.lower()
        for rule in cfg.keyword_rules:
            if rule.pattern.lower() in project_lower:
                sub_path = rule.sub_path_template.format(project=project)
                return RoutingDecision(
                    project=project,
                    destination_repo=rule.destination_repo,
                    sub_path=sub_path,
                    confidence="high",
                    rule_used=f"keyword rule: '{rule.pattern}'",
                    item_count=len(items),
                    dominant_kind=dom_kind,
                )

        # 3. Kind rules
        if dom_kind != FileKind.UNKNOWN:
            for rule in cfg.kind_rules:
                if rule.kind == dom_kind:
                    sub_path = rule.sub_path_template.format(project=project)
                    return RoutingDecision(
                        project=project,
                        destination_repo=rule.destination_repo,
                        sub_path=sub_path,
                        confidence="medium",
                        rule_used=f"kind rule: {dom_kind.value}",
                        item_count=len(items),
                        dominant_kind=dom_kind,
                    )

        # 4. Fallback
        return RoutingDecision(
            project=project,
            destination_repo=cfg.fallback_repo,
            sub_path=f"archive/{project}/",
            confidence="low",
            rule_used="fallback",
            item_count=len(items),
            dominant_kind=dom_kind,
        )

    def route_all(
        self,
        groups: dict[str, list[ArchiveItem]],
    ) -> list[RoutingDecision]:
        """Route each project group; return decisions sorted by project name."""
        decisions = [self.route(proj, items) for proj, items in groups.items()]
        return sorted(decisions, key=lambda d: d.project)

    def decisions_to_repo(
        self,
        decisions: list[RoutingDecision],
    ) -> dict[str, list[RoutingDecision]]:
        """Group decisions by destination_repo."""
        result: dict[str, list[RoutingDecision]] = {}
        for dec in decisions:
            result.setdefault(dec.destination_repo, []).append(dec)
        return result
