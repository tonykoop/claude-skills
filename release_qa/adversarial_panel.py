"""Adversarial Review Panel — 5-persona multi-lens review of a ReleaseBundle."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from release_qa.manifest import ReleaseBundle

PROHIBITED_KEYWORDS = ["explicit", "nsfw", "controversial", "violence", "adult"]


@dataclass
class ReviewerPersona:
    id: str
    name: str
    lens: str
    severity_bias: str  # "strict" | "lenient" | "balanced"


@dataclass
class Critique:
    reviewer_id: str
    lens: str
    finding: str
    severity: str  # info / warning / error / blocker
    score: float   # 0-1 (persona's sub-score for this finding)


@dataclass
class PanelReport:
    bundle_id: str
    critiques: List[Critique] = field(default_factory=list)
    consensus_score: float = 0.0
    recommendation: str = "revise"  # approve / revise / reject
    dissenting_reviewers: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Persona implementations
# ---------------------------------------------------------------------------

def _review_technical_auditor(bundle: ReleaseBundle, persona: ReviewerPersona) -> List[Critique]:
    critiques = []
    score = 1.0

    # Check video resolution
    videos = [a for a in bundle.artifacts if a.artifact_type == "video"]
    for v in videos:
        if not v.resolution:
            critiques.append(Critique(
                reviewer_id=persona.id,
                lens=persona.lens,
                finding=f"Video artifact '{v.id}' has no resolution metadata.",
                severity="error",
                score=0.5,
            ))
            score = min(score, 0.5)
        else:
            try:
                parts = v.resolution.lower().split("x")
                height = int(parts[1]) if len(parts) >= 2 else 0
                if height < 720:
                    critiques.append(Critique(
                        reviewer_id=persona.id,
                        lens=persona.lens,
                        finding=f"Video '{v.id}' is below 720p ({v.resolution}).",
                        severity="error",
                        score=0.4,
                    ))
                    score = min(score, 0.4)
                else:
                    critiques.append(Critique(
                        reviewer_id=persona.id,
                        lens=persona.lens,
                        finding=f"Video '{v.id}' meets resolution requirement ({v.resolution}).",
                        severity="info",
                        score=1.0,
                    ))
            except (ValueError, IndexError):
                critiques.append(Critique(
                    reviewer_id=persona.id,
                    lens=persona.lens,
                    finding=f"Video '{v.id}' has unparseable resolution '{v.resolution}'.",
                    severity="warning",
                    score=0.6,
                ))
                score = min(score, 0.6)

    # Check audio presence
    has_audio = any(a.artifact_type == "audio" for a in bundle.artifacts)
    if not has_audio:
        critiques.append(Critique(
            reviewer_id=persona.id,
            lens=persona.lens,
            finding="No audio artifact found in bundle.",
            severity="warning",
            score=0.7,
        ))
        score = min(score, 0.7)
    else:
        critiques.append(Critique(
            reviewer_id=persona.id,
            lens=persona.lens,
            finding="Audio artifact present.",
            severity="info",
            score=1.0,
        ))

    # Check checksums on required artifacts
    missing_cs = [a.id for a in bundle.artifacts if a.required and not a.checksum_sha256]
    if missing_cs:
        critiques.append(Critique(
            reviewer_id=persona.id,
            lens=persona.lens,
            finding=f"Required artifacts missing checksums: {missing_cs}.",
            severity="blocker",
            score=0.0,
        ))
        score = 0.0
    else:
        critiques.append(Critique(
            reviewer_id=persona.id,
            lens=persona.lens,
            finding="All required artifacts have checksums.",
            severity="info",
            score=1.0,
        ))

    if not critiques:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding="No technical issues found.", severity="info", score=1.0,
        ))
        score = 1.0

    # Final score = minimum of sub-scores found
    final_score = min((c.score for c in critiques), default=score)
    # Adjust final critique score into a single number
    for c in critiques:
        pass  # scores attached per-critique; overall persona score computed below

    return critiques, final_score


def _review_audience_fit_critic(bundle: ReleaseBundle, persona: ReviewerPersona) -> tuple:
    critiques = []
    score = 1.0

    # Title length
    if len(bundle.title.strip()) < 5:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding="Title is too short (< 5 chars); poor audience discoverability.",
            severity="warning", score=0.6,
        ))
        score = min(score, 0.6)
    elif len(bundle.title.strip()) > 100:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding="Title is too long (> 100 chars); may be truncated in feeds.",
            severity="warning", score=0.7,
        ))
        score = min(score, 0.7)
    else:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding=f"Title length ({len(bundle.title.strip())} chars) is appropriate.",
            severity="info", score=1.0,
        ))

    # Tags count
    if len(bundle.tags) < 3:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding=f"Only {len(bundle.tags)} tag(s); recommend at least 3 for discoverability.",
            severity="warning", score=0.6,
        ))
        score = min(score, 0.6)
    else:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding=f"{len(bundle.tags)} tags present — good discoverability.",
            severity="info", score=1.0,
        ))

    # Caption presence for wide audience
    has_caption = any(a.artifact_type == "caption" for a in bundle.artifacts)
    if not has_caption:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding="No caption artifact; accessibility will suffer for broad audience.",
            severity="warning", score=0.7,
        ))
        score = min(score, 0.7)
    else:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding="Caption artifact present; good for accessibility.",
            severity="info", score=1.0,
        ))

    final_score = min((c.score for c in critiques), default=score)
    return critiques, final_score


def _review_brand_safety(bundle: ReleaseBundle, persona: ReviewerPersona) -> tuple:
    critiques = []
    score = 1.0

    prohibited_found = [t for t in bundle.tags if any(kw in t.lower() for kw in PROHIBITED_KEYWORDS)]
    if prohibited_found:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding=f"Tags contain prohibited keywords: {prohibited_found}.",
            severity="blocker", score=0.0,
        ))
        score = 0.0
    else:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding="No prohibited keywords in tags.",
            severity="info", score=1.0,
        ))

    # Check title for prohibited keywords
    title_issues = [kw for kw in PROHIBITED_KEYWORDS if kw in bundle.title.lower()]
    if title_issues:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding=f"Title contains prohibited keywords: {title_issues}.",
            severity="blocker", score=0.0,
        ))
        score = 0.0
    else:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding="Title passes brand safety check.",
            severity="info", score=1.0,
        ))

    final_score = min((c.score for c in critiques), default=score)
    return critiques, final_score


def _review_pacing_analyst(bundle: ReleaseBundle, persona: ReviewerPersona) -> tuple:
    critiques = []
    score = 1.0

    videos = [a for a in bundle.artifacts if a.artifact_type == "video"]
    if not videos:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding="No video artifacts to analyze for pacing.",
            severity="info", score=1.0,
        ))
        return critiques, 1.0

    for v in videos:
        if v.duration_seconds is None:
            critiques.append(Critique(
                reviewer_id=persona.id, lens=persona.lens,
                finding=f"Video '{v.id}' has no duration metadata; pacing cannot be assessed.",
                severity="warning", score=0.7,
            ))
            score = min(score, 0.7)
        elif v.duration_seconds > 3600:
            critiques.append(Critique(
                reviewer_id=persona.id, lens=persona.lens,
                finding=f"Video '{v.id}' is very long ({v.duration_seconds:.0f}s > 3600s); pacing risk.",
                severity="warning", score=0.7,
            ))
            score = min(score, 0.7)
        elif v.duration_seconds < 60:
            critiques.append(Critique(
                reviewer_id=persona.id, lens=persona.lens,
                finding=f"Video '{v.id}' is very short ({v.duration_seconds:.0f}s < 60s); may feel rushed.",
                severity="warning", score=0.6,
            ))
            score = min(score, 0.6)
        else:
            critiques.append(Critique(
                reviewer_id=persona.id, lens=persona.lens,
                finding=f"Video '{v.id}' duration ({v.duration_seconds:.0f}s) is within normal pacing range.",
                severity="info", score=1.0,
            ))

    final_score = min((c.score for c in critiques), default=score)
    return critiques, final_score


def _review_metadata_completeness(bundle: ReleaseBundle, persona: ReviewerPersona) -> tuple:
    critiques = []
    score = 1.0

    # Tags not empty
    if not bundle.tags:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding="Tags list is empty.",
            severity="error", score=0.5,
        ))
        score = min(score, 0.5)
    else:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding=f"{len(bundle.tags)} tag(s) present.",
            severity="info", score=1.0,
        ))

    # Metadata not empty
    if not bundle.metadata:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding="Metadata dict is empty; no project/episode information.",
            severity="error", score=0.5,
        ))
        score = min(score, 0.5)
    else:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding=f"Metadata has {len(bundle.metadata)} key(s).",
            severity="info", score=1.0,
        ))

    # created_at populated
    if not bundle.created_at:
        critiques.append(Critique(
            reviewer_id=persona.id, lens=persona.lens,
            finding="created_at timestamp is missing.",
            severity="warning", score=0.8,
        ))
        score = min(score, 0.8)

    final_score = min((c.score for c in critiques), default=score)
    return critiques, final_score


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

DEFAULT_PERSONAS = [
    ReviewerPersona(id="tech_auditor", name="Technical Auditor", lens="technical", severity_bias="strict"),
    ReviewerPersona(id="audience_fit", name="Audience Fit Critic", lens="audience", severity_bias="balanced"),
    ReviewerPersona(id="brand_safety", name="Brand Safety Reviewer", lens="brand_safety", severity_bias="strict"),
    ReviewerPersona(id="pacing", name="Pacing Analyst", lens="pacing", severity_bias="lenient"),
    ReviewerPersona(id="metadata", name="Metadata Completeness", lens="metadata", severity_bias="balanced"),
]

_PERSONA_REVIEWERS = {
    "tech_auditor": _review_technical_auditor,
    "audience_fit": _review_audience_fit_critic,
    "brand_safety": _review_brand_safety,
    "pacing": _review_pacing_analyst,
    "metadata": _review_metadata_completeness,
}

# Weights per persona
_PERSONA_WEIGHTS = {
    "tech_auditor": 1.5,
    "audience_fit": 1.0,
    "brand_safety": 2.0,
    "pacing": 0.8,
    "metadata": 0.7,
}


class AdversarialPanel:
    def __init__(self, personas: Optional[List[ReviewerPersona]] = None):
        self.personas = personas if personas is not None else DEFAULT_PERSONAS

    def review(self, bundle: ReleaseBundle) -> PanelReport:
        all_critiques: List[Critique] = []
        persona_scores: Dict[str, float] = {}

        for persona in self.personas:
            fn = _PERSONA_REVIEWERS.get(persona.id)
            if fn is None:
                continue
            critiques, p_score = fn(bundle, persona)
            all_critiques.extend(critiques)
            persona_scores[persona.id] = p_score

        # Weighted consensus score
        total_weight = sum(_PERSONA_WEIGHTS.get(pid, 1.0) for pid in persona_scores)
        if total_weight > 0:
            consensus = sum(
                _PERSONA_WEIGHTS.get(pid, 1.0) * score
                for pid, score in persona_scores.items()
            ) / total_weight
        else:
            consensus = 0.0

        consensus = max(0.0, min(1.0, consensus))

        # Recommendation logic
        # >=3/5 personas at >=0.6 → "approve"; <0.4 avg → "reject"; else "revise"
        high_scorers = sum(1 for s in persona_scores.values() if s >= 0.6)
        if consensus >= 0.4 and high_scorers >= 3:
            recommendation = "approve"
        elif consensus < 0.4:
            recommendation = "reject"
        else:
            recommendation = "revise"

        # Dissenters = personas below average
        avg = sum(persona_scores.values()) / max(len(persona_scores), 1)
        dissenting = [pid for pid, s in persona_scores.items() if s < avg - 0.15]

        return PanelReport(
            bundle_id=bundle.id,
            critiques=all_critiques,
            consensus_score=round(consensus, 4),
            recommendation=recommendation,
            dissenting_reviewers=dissenting,
        )
