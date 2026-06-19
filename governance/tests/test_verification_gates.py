"""Tests for the automated verification gates (#257)."""
import sys
from pathlib import Path

import pytest

GOV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOV))

import verification_gates as vg  # noqa: E402


# --- sandbox execution gate (acceptance: catches runtime errors) ------------

def test_sandbox_passes_clean_code():
    res = vg.sandbox_exec_gate("x = 1 + 1\nassert x == 2\n")
    assert res.passed
    assert res.detail["returncode"] == 0


def test_sandbox_catches_runtime_exception():
    res = vg.sandbox_exec_gate("raise ValueError('boom')\n")
    assert not res.passed
    assert any("boom" in f or "ValueError" in f for f in res.findings)
    assert res.detail["returncode"] != 0


def test_sandbox_catches_syntax_error():
    res = vg.sandbox_exec_gate("def broken(:\n    pass\n")
    assert not res.passed


def test_sandbox_catches_timeout():
    res = vg.sandbox_exec_gate("while True:\n    pass\n", timeout_seconds=1.0)
    assert not res.passed
    assert "timed out" in res.summary


def test_sandbox_rejects_unknown_language():
    # default-deny: a language we can't run is a failure, never a silent pass.
    res = vg.sandbox_exec_gate("print('hi')", language="brainfuck")
    assert not res.passed


def test_sandbox_runs_bash():
    assert vg.sandbox_exec_gate("exit 0", language="bash").passed
    assert not vg.sandbox_exec_gate("exit 3", language="bash").passed


def test_sandbox_isolated_cwd_cannot_see_repo(tmp_path):
    # The script runs in a throwaway cwd, so a relative path into the repo fails.
    res = vg.sandbox_exec_gate("open('agent-roster.yaml').read()\n")
    assert not res.passed


# --- markdown / length gate (studio domain) ---------------------------------

def _good_script(words=200):
    # Wrap to short lines so the body itself doesn't trip the line-length check.
    per_line = 10
    lines = [" ".join(["word"] * per_line) for _ in range(words // per_line)]
    body = "\n".join(lines)
    return f"# Episode Title\n\nIntro paragraph.\n\n{body}\n"


def test_markdown_passes_well_formed_script():
    res = vg.markdown_length_gate(_good_script())
    assert res.passed
    assert res.domain == vg.DOMAIN_STUDIO


def test_markdown_flags_stub_too_short():
    res = vg.markdown_length_gate("# Title\n\ntoo short\n")
    assert not res.passed
    assert any("too short" in f for f in res.findings)


def test_markdown_flags_runaway_too_long():
    res = vg.markdown_length_gate(_good_script(words=3000), max_words=2500)
    assert not res.passed
    assert any("too long" in f for f in res.findings)


def test_markdown_flags_missing_heading():
    text = "Just prose " * 40
    res = vg.markdown_length_gate(text)
    assert not res.passed
    assert any("heading" in f for f in res.findings)


def test_markdown_flags_unterminated_code_fence():
    text = _good_script() + "\n```python\nprint(1)\n"
    res = vg.markdown_length_gate(text)
    assert not res.passed
    assert any("code fence" in f for f in res.findings)


def test_markdown_flags_overlong_line():
    text = "# Title\n\n" + ("x" * 200) + "\n" + " ".join(["w"] * 100)
    res = vg.markdown_length_gate(text, max_line_length=120)
    assert not res.passed
    assert any("chars >" in f for f in res.findings)


# --- URDF joint-limit gate (robotics domain) --------------------------------

GOOD_URDF = """
<robot name="leg">
  <link name="base"/>
  <link name="thigh"/>
  <link name="shin"/>
  <joint name="hip" type="revolute">
    <parent link="base"/><child link="thigh"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="2.0"/>
  </joint>
  <joint name="knee" type="prismatic">
    <parent link="thigh"/><child link="shin"/>
    <limit lower="0.0" upper="0.3" effort="80" velocity="1.0"/>
  </joint>
  <joint name="wheel" type="continuous">
    <parent link="shin"/><child link="base"/>
  </joint>
</robot>
"""


def test_urdf_passes_good_joints():
    res = vg.urdf_joint_limit_gate(GOOD_URDF)
    assert res.passed
    assert res.detail["actuated_joints"] == 2  # continuous joint is exempt


def test_urdf_flags_missing_limit():
    urdf = """
    <robot name="x">
      <joint name="hip" type="revolute">
        <parent link="a"/><child link="b"/>
      </joint>
    </robot>
    """
    res = vg.urdf_joint_limit_gate(urdf)
    assert not res.passed
    assert any("missing <limit>" in f for f in res.findings)


def test_urdf_flags_degenerate_range():
    urdf = """
    <robot name="x">
      <joint name="hip" type="revolute">
        <parent link="a"/><child link="b"/>
        <limit lower="1.0" upper="0.5" effort="10" velocity="1"/>
      </joint>
    </robot>
    """
    res = vg.urdf_joint_limit_gate(urdf)
    assert not res.passed
    assert any("lower" in f and "upper" in f for f in res.findings)


def test_urdf_flags_nonpositive_effort_velocity():
    urdf = """
    <robot name="x">
      <joint name="hip" type="revolute">
        <parent link="a"/><child link="b"/>
        <limit lower="-1" upper="1" effort="0" velocity="0"/>
      </joint>
    </robot>
    """
    res = vg.urdf_joint_limit_gate(urdf)
    assert not res.passed
    assert any("effort" in f for f in res.findings)
    assert any("velocity" in f for f in res.findings)


def test_urdf_flags_home_position_outside_limit():
    res = vg.urdf_joint_limit_gate(GOOD_URDF, home_positions={"hip": 3.0})
    assert not res.passed
    assert any("home position" in f for f in res.findings)


def test_urdf_home_position_inside_limit_passes():
    res = vg.urdf_joint_limit_gate(GOOD_URDF, home_positions={"hip": 0.5, "knee": 0.1})
    assert res.passed


def test_urdf_parse_error():
    res = vg.urdf_joint_limit_gate("<robot><not closed>")
    assert not res.passed
    assert any("parse error" in res.summary for _ in [0]) or any("XML" in f for f in res.findings)


# --- aggregation: gate results attach to the QA decision --------------------

def test_report_aggregates_and_attaches_to_qa_decision():
    results = [
        vg.sandbox_exec_gate("print('ok')"),
        vg.markdown_length_gate(_good_script()),
        vg.urdf_joint_limit_gate(GOOD_URDF),
    ]
    report = vg.run_gates(results)
    assert report.passed
    decision = report.as_qa_decision()
    assert decision["gates_passed"] is True
    assert decision["gate_count"] == 3
    assert decision["failed_gates"] == []
    assert len(decision["gates"]) == 3


def test_report_fails_when_any_gate_fails():
    results = [
        vg.sandbox_exec_gate("print('ok')"),
        vg.markdown_length_gate("# t\n\nstub\n"),  # too short
    ]
    report = vg.run_gates(results)
    assert not report.passed
    assert "markdown-length" in report.failed_gates
    assert report.as_qa_decision()["gates_passed"] is False


# --- CLI smoke --------------------------------------------------------------

def test_cli_sandbox_exit_codes(tmp_path):
    good = tmp_path / "good.py"
    good.write_text("print('hi')\n")
    assert vg.main(["sandbox", "--file", str(good)]) == 0

    bad = tmp_path / "bad.py"
    bad.write_text("raise SystemExit(2)\n")
    assert vg.main(["sandbox", "--file", str(bad)]) == 1


def test_cli_report_manifest(tmp_path, capsys):
    script = tmp_path / "s.md"
    script.write_text(_good_script())
    urdf = tmp_path / "leg.urdf"
    urdf.write_text(GOOD_URDF)
    manifest = tmp_path / "m.json"
    manifest.write_text(
        '{"artifacts": ['
        f'{{"gate": "markdown", "path": "{script}"}},'
        f'{{"gate": "urdf", "path": "{urdf}"}}'
        ']}'
    )
    assert vg.main(["report", "--manifest", str(manifest), "--json"]) == 0
    out = capsys.readouterr().out
    assert '"gates_passed": true' in out
