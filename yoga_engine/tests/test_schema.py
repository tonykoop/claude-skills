"""Tests for yoga_engine.schema — data model correctness."""

import pytest
from yoga_engine.schema import (
    Pose, PoseFamily, Phase, PhaseBlock, PoseInstance, Sequence,
    ValidationIssue, ValidationReport, ArcReport, IssueSeverity, BreathOp,
)


# ---------------------------------------------------------------------------
# Pose
# ---------------------------------------------------------------------------


class TestPose:
    def test_valid_pose_creation(self):
        p = Pose(
            token="DD", name="Downward Dog",
            family=PoseFamily.TRANSITION, intensity=3,
            phase_roles=[Phase.WARMUP, Phase.BUILD],
        )
        assert p.token == "DD"
        assert p.intensity == 3
        assert PoseFamily.TRANSITION == p.family

    def test_intensity_out_of_range_low(self):
        with pytest.raises(ValueError, match="intensity must be 1–10"):
            Pose(token="XX", name="Bad", family=PoseFamily.SAVASANA,
                 intensity=0, phase_roles=[])

    def test_intensity_out_of_range_high(self):
        with pytest.raises(ValueError, match="intensity must be 1–10"):
            Pose(token="XX", name="Bad", family=PoseFamily.SAVASANA,
                 intensity=11, phase_roles=[])

    def test_intensity_boundary_values(self):
        p1 = Pose(token="A1", name="Min", family=PoseFamily.SAVASANA,
                  intensity=1, phase_roles=[])
        p2 = Pose(token="A2", name="Max", family=PoseFamily.ARM_BALANCE,
                  intensity=10, phase_roles=[])
        assert p1.intensity == 1
        assert p2.intensity == 10

    def test_repr(self):
        p = Pose(token="SV", name="Savasana", family=PoseFamily.SAVASANA,
                 intensity=1, phase_roles=[Phase.SAVASANA])
        assert "SV" in repr(p)
        assert "Savasana" in repr(p)


# ---------------------------------------------------------------------------
# PoseInstance
# ---------------------------------------------------------------------------


class TestPoseInstance:
    def _make_pose(self) -> Pose:
        return Pose(token="WR2", name="Warrior II",
                    family=PoseFamily.STANDING, intensity=6,
                    phase_roles=[Phase.BUILD])

    def test_display_name_no_side(self):
        inst = PoseInstance(pose=self._make_pose())
        assert inst.display_name == "Warrior II"

    def test_display_name_right(self):
        inst = PoseInstance(pose=self._make_pose(), side="r")
        assert inst.display_name == "Warrior II (R)"

    def test_display_name_left(self):
        inst = PoseInstance(pose=self._make_pose(), side="l")
        assert inst.display_name == "Warrior II (L)"

    def test_display_name_unknown_side(self):
        inst = PoseInstance(pose=self._make_pose(), side="z")
        assert inst.display_name == "Warrior II"  # unknown side omitted


# ---------------------------------------------------------------------------
# PhaseBlock
# ---------------------------------------------------------------------------


class TestPhaseBlock:
    def _make_block(self, intensities) -> PhaseBlock:
        block = PhaseBlock(label="BD", phase=Phase.BUILD)
        for i, iv in enumerate(intensities):
            p = Pose(token=f"P{i}", name=f"Pose{i}",
                     family=PoseFamily.STANDING, intensity=iv, phase_roles=[])
            block.poses.append(PoseInstance(pose=p))
        return block

    def test_max_intensity_empty(self):
        block = PhaseBlock(label="BD", phase=Phase.BUILD)
        assert block.max_intensity == 0

    def test_max_intensity(self):
        block = self._make_block([3, 6, 5])
        assert block.max_intensity == 6

    def test_avg_intensity(self):
        block = self._make_block([4, 6, 8])
        assert abs(block.avg_intensity - 6.0) < 0.001

    def test_avg_intensity_empty(self):
        block = PhaseBlock(label="BD", phase=Phase.BUILD)
        assert block.avg_intensity == 0.0


# ---------------------------------------------------------------------------
# Sequence
# ---------------------------------------------------------------------------


class TestSequence:
    def _make_seq(self) -> Sequence:
        seq = Sequence(title="Test", duration_minutes=60)
        warmup = PhaseBlock(label="WU", phase=Phase.WARMUP)
        warmup.poses.append(PoseInstance(
            pose=Pose(token="CC", name="Cat-Cow",
                      family=PoseFamily.SPINAL_MOBILITY, intensity=2,
                      phase_roles=[Phase.WARMUP])
        ))
        peak = PhaseBlock(label="PK", phase=Phase.PEAK)
        peak.poses.append(PoseInstance(
            pose=Pose(token="CM", name="Camel",
                      family=PoseFamily.BACKBEND, intensity=8,
                      phase_roles=[Phase.PEAK])
        ))
        seq.phases = [warmup, peak]
        return seq

    def test_all_poses_flat(self):
        seq = self._make_seq()
        all_p = seq.all_poses
        assert len(all_p) == 2

    def test_intensity_curve(self):
        seq = self._make_seq()
        assert seq.intensity_curve == [2, 8]

    def test_get_phase_found(self):
        seq = self._make_seq()
        block = seq.get_phase(Phase.WARMUP)
        assert block is not None
        assert block.label == "WU"

    def test_get_phase_not_found(self):
        seq = self._make_seq()
        assert seq.get_phase(Phase.COOLDOWN) is None


# ---------------------------------------------------------------------------
# ValidationReport
# ---------------------------------------------------------------------------


class TestValidationReport:
    def test_empty_report_is_safe(self):
        r = ValidationReport()
        assert r.is_safe
        assert r.errors == []
        assert r.warnings == []

    def test_error_makes_unsafe(self):
        r = ValidationReport(issues=[
            ValidationIssue(severity=IssueSeverity.ERROR,
                            code="TEST_ERR", message="boom")
        ])
        assert not r.is_safe

    def test_warning_stays_safe(self):
        r = ValidationReport(issues=[
            ValidationIssue(severity=IssueSeverity.WARNING,
                            code="TEST_WARN", message="heads up")
        ])
        assert r.is_safe

    def test_repr(self):
        r = ValidationReport()
        assert "errors=0" in repr(r)
        assert "safe=True" in repr(r)
