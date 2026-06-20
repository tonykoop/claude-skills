"""Expanded plant health diagnostics engine (story #175).

Multi-factor diagnostic engine that goes beyond the binary observation
flags in ``health.py`` to produce richer, evidence-grounded health
assessments.  It cross-references visual observations with care-history
patterns to distinguish between similar presentations (e.g. drought-
yellowing vs. nitrogen deficiency) and to rank confidence in each flag.

Key design principles:
- Conservative: prefer "inspect" over "treat"; flag uncertainty explicitly.
- Evidence-based: every flag cites which observation(s) triggered it.
- Non-destructive: no treatment is recommended without noting that a
  second look / confirmed diagnosis should precede any chemical use.
- Integrates with existing ``assess_health()`` for a richer context.

Key objects:

- ``PestFlag`` — identifies a likely pest from symptom patterns.
- ``NutritionFlag`` — identifies a likely deficiency from yellowing pattern.
- ``RootHealthFlag`` — root-rot risk signal from overwatering / soggy-soil.
- ``DiagnosticFinding`` — a single issue with evidence list and confidence.
- ``DiagnosticReport`` — full report for one specimen at one date.

Pure functions:

- ``diagnose(specimen, observations, history, today, profile)``
  → ``DiagnosticReport``
- ``root_rot_risk(history, profile, today)`` → ``float`` [0, 1]
- ``probable_pests(observations)`` → ``List[PestFlag]``
- ``nutrition_flags(observations)`` → ``List[NutritionFlag]``

No I/O, no real-clock calls.

Usage::

    import datetime
    from plant_care.diagnostics import diagnose
    from plant_care.models import Specimen, CareProfile, CareEvent, Observations

    obs = Observations(yellowing=True, dry_soil=False)
    report = diagnose(specimen, obs, history, datetime.date(2024, 6, 15), profile)
    for f in report.findings:
        print(f.flag, f.confidence, f.evidence)
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from .models import CareEvent, CareProfile, Observations, Specimen


# ── Enums ─────────────────────────────────────────────────────────────────────


class Confidence(str, Enum):
    """Confidence level for a diagnostic finding."""

    HIGH = "high"         # Multiple corroborating signals
    MEDIUM = "medium"     # Plausible; one or two signals
    LOW = "low"           # Speculative; rule out other causes first


class PestFlag(str, Enum):
    """Pest identifications inferred from symptom patterns."""

    SCALE_INSECT = "scale_insect"        # Brown/tan bumps; sticky honeydew
    SPIDER_MITE = "spider_mite"          # Fine webbing; stippled/bleached leaves
    THRIPS = "thrips"                    # Silver streaks; distorted new growth
    FUNGUS_GNAT = "fungus_gnat"          # Tiny flies at soil; larvae in roots
    MEALYBUG = "mealybug"                # White cottony masses in leaf axils
    APHID = "aphid"                      # Sticky residue; clustered on new shoots


class NutritionFlag(str, Enum):
    """Nutritional deficiency flags from yellowing pattern descriptions."""

    NITROGEN_DEFICIENCY = "nitrogen_deficiency"    # Generalised pale-yellow
    IRON_DEFICIENCY = "iron_deficiency"            # Interveinal chlorosis, young leaves
    MAGNESIUM_DEFICIENCY = "magnesium_deficiency"  # Interveinal chlorosis, old leaves
    OVERFEEDING = "overfeeding"                    # Leaf tip/edge burn


# ── DiagnosticFinding ────────────────────────────────────────────────────────


@dataclass
class DiagnosticFinding:
    """A single issue identified during diagnosis.

    Attributes
    ----------
    flag:
        Short identifier for the issue
        (e.g. ``"scale_insect"``, ``"nitrogen_deficiency"``).
    category:
        Broad category: ``"pest"``, ``"nutrition"``, ``"root_health"``,
        ``"environment"``, or ``"cultural"``.
    confidence:
        ``Confidence`` level — HIGH, MEDIUM, or LOW.
    evidence:
        List of observation or care-history strings that triggered this flag.
    recommendation:
        Short action recommendation.
    caution:
        Any important caveats (confirm before treating, isolate first, etc.).
    """

    flag: str
    category: str
    confidence: Confidence
    evidence: List[str]
    recommendation: str
    caution: str = ""

    def to_dict(self) -> dict:
        return {
            "flag": self.flag,
            "category": self.category,
            "confidence": self.confidence.value,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "caution": self.caution,
        }


# ── DiagnosticReport ─────────────────────────────────────────────────────────


@dataclass
class DiagnosticReport:
    """Full diagnostic assessment for one specimen at one point in time.

    Attributes
    ----------
    specimen_id:
        The specimen that was assessed.
    date:
        Assessment date (injected; no real-clock calls).
    overall_status:
        Highest-severity status across all findings:
        ``"healthy"``, ``"needs-attention"``, or ``"declining"``.
    findings:
        List of ``DiagnosticFinding`` objects, sorted severity-first.
    root_rot_risk_score:
        Float in [0, 1] — risk of root rot based on watering history.
        0 = no risk signal; 1 = strong evidence.
    notes:
        Human-readable summary of the assessment.
    """

    specimen_id: str
    date: datetime.date
    overall_status: str
    findings: List[DiagnosticFinding]
    root_rot_risk_score: float = 0.0
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "specimen_id": self.specimen_id,
            "date": self.date.isoformat(),
            "overall_status": self.overall_status,
            "findings": [f.to_dict() for f in self.findings],
            "root_rot_risk_score": self.root_rot_risk_score,
            "notes": self.notes,
        }

    def findings_by_category(self, category: str) -> List[DiagnosticFinding]:
        return [f for f in self.findings if f.category == category]

    def has_flag(self, flag: str) -> bool:
        return any(f.flag == flag for f in self.findings)


# ── Internal helpers ──────────────────────────────────────────────────────────


def _last_event_date(
    history: List[CareEvent], action_type: str
) -> Optional[datetime.date]:
    dates = [e.date for e in history if e.type == action_type]
    return max(dates) if dates else None


def _days_since(last_date: Optional[datetime.date], today: datetime.date) -> Optional[int]:
    return (today - last_date).days if last_date else None


# ── Pure functions ────────────────────────────────────────────────────────────


def root_rot_risk(
    history: List[CareEvent],
    profile: CareProfile,
    today: datetime.date,
) -> float:
    """Estimate root-rot risk as a score in [0, 1].

    Risk is elevated when the plant has been watered significantly more
    frequently than its care profile specifies — overwatering is the
    primary cause of root rot in container plants.

    Args:
        history:  Full care event history for the specimen.
        profile:  The specimen's care profile (defines normal interval).
        today:    Reference date (injected).

    Returns:
        Float in [0, 1]; 0 = no risk signal; 1 = strong risk signal.
        Confidence is LOW even at 1.0 — root rot requires soil inspection
        to confirm.

    Scoring:
    - Water interval shortened to < 50% of prescribed → score 0.8
    - Water interval 50%–75% of prescribed → score 0.4
    - Water interval > 75% → score 0.0
    - No watering history → score 0.0 (no evidence either way)
    """
    water_events = sorted(
        [e for e in history if e.type == "water"], key=lambda e: e.date
    )
    if len(water_events) < 2:
        return 0.0

    # Calculate the mean interval between the last N waterings (up to 5)
    recent = water_events[-min(len(water_events), 6):]
    intervals = [(recent[i].date - recent[i - 1].date).days
                 for i in range(1, len(recent))]
    if not intervals:
        return 0.0

    mean_interval = sum(intervals) / len(intervals)
    prescribed = profile.watering_interval_days

    ratio = mean_interval / prescribed  # < 1 = watering too frequently
    if ratio < 0.5:
        return 0.8
    elif ratio < 0.75:
        return 0.4
    return 0.0


def probable_pests(observations: Observations) -> List[DiagnosticFinding]:
    """Infer likely pests from visual observations.

    Returns a list of ``DiagnosticFinding`` objects for each plausible
    pest, with evidence from the observations that triggered each flag.

    These are probability-weighted inferences, not confirmed diagnoses.
    Always confirm with a hand-lens inspection before treating.
    """
    findings: List[DiagnosticFinding] = []

    # Pest observation flags (simple boolean checks on the extended obs)
    obs = observations

    # Spider mites: webbing, stippling — dry conditions
    if getattr(obs, "webbing", False):
        findings.append(DiagnosticFinding(
            flag=PestFlag.SPIDER_MITE.value,
            category="pest",
            confidence=Confidence.HIGH,
            evidence=["webbing observed on leaves or stems"],
            recommendation=(
                "Wipe leaves with a damp cloth; isolate plant. "
                "Increase humidity — spider mites thrive in dry conditions. "
                "Repeat weekly until clear."
            ),
            caution=(
                "Confirm with hand-lens inspection before chemical treatment. "
                "Check undersides of leaves for tiny moving specks."
            ),
        ))

    if getattr(obs, "sticky_residue", False):
        findings.append(DiagnosticFinding(
            flag=PestFlag.SCALE_INSECT.value,
            category="pest",
            confidence=Confidence.MEDIUM,
            evidence=["sticky honeydew residue on leaves or pot"],
            recommendation=(
                "Inspect stems and leaf undersides for brown/tan bumps. "
                "Remove manually with a cotton swab dipped in 70% isopropyl "
                "alcohol. Repeat weekly."
            ),
            caution="Sticky residue may also indicate aphids or mealybugs — inspect closely.",
        ))
        # Aphids also produce honeydew
        findings.append(DiagnosticFinding(
            flag=PestFlag.APHID.value,
            category="pest",
            confidence=Confidence.LOW,
            evidence=["sticky honeydew residue (aphids also produce this)"],
            recommendation=(
                "Check new growth for clusters of small, pear-shaped insects. "
                "Knock off with a stream of water; or use insecticidal soap."
            ),
            caution="Low confidence — honeydew is non-specific. Inspect before treating.",
        ))

    if getattr(obs, "white_cottony_masses", False):
        findings.append(DiagnosticFinding(
            flag=PestFlag.MEALYBUG.value,
            category="pest",
            confidence=Confidence.HIGH,
            evidence=["white cottony masses observed in leaf axils or on stems"],
            recommendation=(
                "Isolate immediately. Remove with alcohol-soaked cotton swab. "
                "Spray with diluted neem oil solution every 7 days for 3 cycles."
            ),
            caution="Check roots — root mealybugs are common and harder to detect.",
        ))

    if getattr(obs, "fungus_gnats", False) or getattr(obs, "soil_flies", False):
        findings.append(DiagnosticFinding(
            flag=PestFlag.FUNGUS_GNAT.value,
            category="pest",
            confidence=Confidence.HIGH,
            evidence=["small flies observed near soil surface"],
            recommendation=(
                "Allow soil to dry thoroughly between waterings — larvae need "
                "moist soil. Yellow sticky traps catch adults. "
                "Beneficial nematodes (Steinernema feltiae) target larvae."
            ),
            caution=(
                "Larvae damage roots of seedlings more than established plants, "
                "but heavy infestations weaken any plant."
            ),
        ))

    # Thrips: distorted new growth, silver streaks
    if getattr(obs, "distorted_new_growth", False):
        findings.append(DiagnosticFinding(
            flag=PestFlag.THRIPS.value,
            category="pest",
            confidence=Confidence.MEDIUM,
            evidence=["distorted or stunted new growth observed"],
            recommendation=(
                "Inspect with hand-lens for tiny (1–2 mm) slender insects on "
                "new leaves. Blue sticky traps are effective monitors. "
                "Systemic insecticide or spinosad-based spray if confirmed."
            ),
            caution="Distorted growth may also result from water stress or herbicide drift.",
        ))

    # Pests flag already in base observations
    if obs.pests:
        # Generic pest flag from base model — add a general finding if not
        # already covered by more specific flags
        specific_pest_flags = {f.flag for f in findings if f.category == "pest"}
        if not specific_pest_flags:
            findings.append(DiagnosticFinding(
                flag="unknown_pest",
                category="pest",
                confidence=Confidence.MEDIUM,
                evidence=["pest presence observed"],
                recommendation=(
                    "Isolate the plant. Inspect with hand-lens for insects, "
                    "eggs, or webbing. Identify before treating."
                ),
                caution="Do not treat until pest is identified.",
            ))

    return findings


def nutrition_flags(observations: Observations) -> List[DiagnosticFinding]:
    """Infer likely nutritional issues from observation patterns.

    Returns a list of ``DiagnosticFinding`` objects.

    NOTE: Yellowing pattern matters enormously but the base ``Observations``
    model only has a boolean ``yellowing`` flag.  The extended observation
    attributes (``yellowing_old_leaves``, ``yellowing_new_leaves``,
    ``interveinal_yellowing``) are checked if present.  If only the
    generic ``yellowing`` flag is set, a lower-confidence general finding
    is returned.
    """
    findings: List[DiagnosticFinding] = []
    obs = observations

    if not obs.yellowing:
        # No yellowing → no nutritional flags
        return findings

    # Iron deficiency: interveinal chlorosis on new/young leaves
    if getattr(obs, "interveinal_yellowing", False) and getattr(obs, "yellowing_new_leaves", False):
        findings.append(DiagnosticFinding(
            flag=NutritionFlag.IRON_DEFICIENCY.value,
            category="nutrition",
            confidence=Confidence.MEDIUM,
            evidence=[
                "interveinal chlorosis (green veins, yellow between)",
                "yellowing concentrated on newer/younger leaves",
            ],
            recommendation=(
                "Check soil pH — high pH locks out iron. "
                "Foliar spray with chelated iron is fast-acting. "
                "Address pH (lower to 6.0–6.5 for most houseplants) for lasting fix."
            ),
            caution="Confirm with a soil pH test; iron supplements on already-correct pH are wasteful.",
        ))

    # Magnesium deficiency: interveinal chlorosis on old leaves
    elif getattr(obs, "interveinal_yellowing", False) and getattr(obs, "yellowing_old_leaves", False):
        findings.append(DiagnosticFinding(
            flag=NutritionFlag.MAGNESIUM_DEFICIENCY.value,
            category="nutrition",
            confidence=Confidence.MEDIUM,
            evidence=[
                "interveinal chlorosis on older/lower leaves",
            ],
            recommendation=(
                "Apply Epsom salt solution (1 tsp / litre) as a foliar spray "
                "or soil drench. Repeat monthly during growing season."
            ),
            caution="Magnesium deficiency can mimic iron deficiency — leaf age is the key differentiator.",
        ))

    # General nitrogen deficiency: pale yellow-green, starting at old leaves
    elif getattr(obs, "yellowing_old_leaves", False):
        findings.append(DiagnosticFinding(
            flag=NutritionFlag.NITROGEN_DEFICIENCY.value,
            category="nutrition",
            confidence=Confidence.MEDIUM,
            evidence=["generalised yellowing starting from older/lower leaves"],
            recommendation=(
                "Apply a balanced fertiliser (or higher-nitrogen formulation) "
                "at half strength. Resume regular feeding programme."
            ),
            caution=(
                "If overwatered, root damage may prevent nitrogen uptake even "
                "when fertiliser is present — assess root health first."
            ),
        ))

    # Overfeeding: tip/edge burn alongside yellowing
    if getattr(obs, "leaf_tip_burn", False) or getattr(obs, "leaf_edge_burn", False):
        findings.append(DiagnosticFinding(
            flag=NutritionFlag.OVERFEEDING.value,
            category="nutrition",
            confidence=Confidence.MEDIUM,
            evidence=["leaf tip or edge browning/burning"],
            recommendation=(
                "Flush soil with plain water (3× pot volume) to leach excess "
                "salts. Reduce fertiliser concentration or frequency."
            ),
            caution="Tip burn can also result from fluoride sensitivity (common in Dracaena/Chlorophytum).",
        ))

    # Generic yellowing with no pattern info
    if not findings:
        findings.append(DiagnosticFinding(
            flag="yellowing_unspecified",
            category="nutrition",
            confidence=Confidence.LOW,
            evidence=["yellowing observed; pattern not specified"],
            recommendation=(
                "Note which leaves are yellowing (old/new, interveinal or "
                "uniform) to narrow the diagnosis.  Check soil moisture first — "
                "both overwatering and underwatering cause yellowing."
            ),
            caution=(
                "Yellowing is non-specific.  Rule out watering issues before "
                "adjusting nutrition."
            ),
        ))

    return findings


def diagnose(
    specimen: Specimen,
    observations: Observations,
    history: List[CareEvent],
    today: datetime.date,
    profile: Optional[CareProfile] = None,
) -> DiagnosticReport:
    """Run a full diagnostic pass on one specimen.

    Combines:
    1. Basic health assessment from ``health.py`` rules.
    2. Pest identification from extended observation attributes.
    3. Nutritional flags from yellowing patterns.
    4. Root-rot risk from watering history.

    Args:
        specimen:      The specimen to assess.
        observations:  Visual observation flags (base + any extended attrs).
        history:       Full care event history.
        today:         Reference date (injected; no real-clock calls).
        profile:       Optional care profile; needed for root-rot risk.

    Returns:
        A ``DiagnosticReport`` with all findings, a risk score, and a
        human-readable status summary.
    """
    findings: List[DiagnosticFinding] = []

    # ── 1. Basic observation flags ────────────────────────────────────────────

    if observations.drooping:
        findings.append(DiagnosticFinding(
            flag="drooping",
            category="cultural",
            confidence=Confidence.MEDIUM,
            evidence=["drooping/wilting observed"],
            recommendation=(
                "Check soil moisture first — both drought and waterlogging cause "
                "drooping. If soil is dry, water thoroughly. If moist, check for "
                "root rot (earthy/musty smell, dark slimy roots)."
            ),
        ))

    if observations.mold:
        findings.append(DiagnosticFinding(
            flag="surface_mold",
            category="environment",
            confidence=Confidence.HIGH,
            evidence=["mold or fungal growth observed on soil or foliage"],
            recommendation=(
                "Increase air circulation. Reduce watering frequency. "
                "Remove affected debris. A light dusting of cinnamon on "
                "soil surface can suppress mold without harming the plant."
            ),
            caution=(
                "Mold on foliage may indicate powdery mildew (a disease) "
                "rather than saprophytic soil mold — inspect closely."
            ),
        ))

    if observations.leaf_drop:
        findings.append(DiagnosticFinding(
            flag="leaf_drop",
            category="cultural",
            confidence=Confidence.HIGH,
            evidence=["active leaf drop observed"],
            recommendation=(
                "Identify the trigger: draft, temperature change, overwatering, "
                "underwatering, or root disturbance (recent repotting). "
                "Ficus species are particularly sensitive to environmental change."
            ),
            caution=(
                "Some leaf drop after relocation is normal for Ficus — "
                "wait 3–4 weeks and assess recovery before intervention."
            ),
        ))

    # ── 2. Pest findings ─────────────────────────────────────────────────────

    findings.extend(probable_pests(observations))

    # ── 3. Nutrition findings ─────────────────────────────────────────────────

    findings.extend(nutrition_flags(observations))

    # ── 4. Root-rot risk ─────────────────────────────────────────────────────

    rr_score = 0.0
    if profile:
        rr_score = root_rot_risk(history, profile, today)
        if rr_score >= 0.4:
            findings.append(DiagnosticFinding(
                flag="root_rot_risk",
                category="root_health",
                confidence=Confidence.LOW if rr_score < 0.8 else Confidence.MEDIUM,
                evidence=[
                    f"watering frequency significantly above profile interval "
                    f"(risk score: {rr_score:.1f})"
                ],
                recommendation=(
                    "Allow soil to dry more thoroughly between waterings. "
                    "Check roots: healthy roots are white/tan and firm; "
                    "rotted roots are brown/black and mushy. "
                    "If rot is found, trim affected roots and repot in fresh substrate."
                ),
                caution=(
                    "Root rot can only be confirmed by removing the plant from "
                    "the pot. This is disruptive — wait for other symptoms "
                    "(persistent drooping, musty smell) before un-potting."
                ),
            ))

    # ── 5. Derive overall status ──────────────────────────────────────────────

    _STATUS_FOR_CATEGORY = {
        "pest": "declining",
        "root_health": "needs-attention",
        "nutrition": "needs-attention",
        "environment": "needs-attention",
        "cultural": "needs-attention",
    }

    if observations.pests or observations.leaf_drop:
        overall = "declining"
    elif observations.yellowing and observations.drooping:
        overall = "declining"
    elif findings:
        worst = "needs-attention"
        for f in findings:
            if _STATUS_FOR_CATEGORY.get(f.category) == "declining":
                worst = "declining"
                break
        overall = worst
    else:
        overall = "healthy"

    # ── 6. Build summary notes ────────────────────────────────────────────────

    flag_names = [f.flag for f in findings]
    if not findings:
        notes = "No concerning findings. Continue routine care."
    else:
        notes = (
            f"Found {len(findings)} concern(s): {', '.join(flag_names)}. "
            "Address highest-confidence findings first; confirm before treating."
        )

    # Sort findings: HIGH confidence first, then by category
    _conf_rank = {Confidence.HIGH: 0, Confidence.MEDIUM: 1, Confidence.LOW: 2}
    findings.sort(key=lambda f: _conf_rank[f.confidence])

    return DiagnosticReport(
        specimen_id=specimen.id,
        date=today,
        overall_status=overall,
        findings=findings,
        root_rot_risk_score=rr_score,
        notes=notes,
    )
