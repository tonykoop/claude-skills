"""Tests for the LLM-timestamp soft-provenance guardrail (Story #418)."""

import json
import re
from pathlib import Path

SKILL_MD = Path(__file__).parent.parent / "plugins/maker/skills/file-a-patent/SKILL.md"
EVALS_JSON = Path(__file__).parent.parent / "plugins/maker/skills/file-a-patent/evals/evals.json"

GUARDRAIL_KEYWORDS = [
    "LLM-asserted",
    "NOT reliable legal provenance",
    "provenance_class",
    "soft",
    "git commit",
]

REAL_PROVENANCE_KEYWORDS = [
    "clipping",
    "git commit",
    "filesystem",
]


def _get_hard_guardrails_section(text: str) -> str:
    match = re.search(r"^## Hard Guardrails(.*?)^## ", text, re.DOTALL | re.MULTILINE)
    assert match, "SKILL.md must have a '## Hard Guardrails' section"
    return match.group(1)


def test_skill_md_hard_guardrails_has_timestamp_rule():
    text = SKILL_MD.read_text()
    section = _get_hard_guardrails_section(text)
    assert "LLM" in section or "model-asserted" in section.lower() or "llm" in section.lower(), (
        "Hard Guardrails must address LLM-asserted timestamps"
    )


def test_skill_md_guardrail_says_not_reliable_provenance():
    text = SKILL_MD.read_text()
    section = _get_hard_guardrails_section(text)
    assert "NOT reliable" in section or "not reliable" in section.lower(), (
        "Guardrail must state timestamps are NOT reliable legal provenance"
    )


def test_skill_md_guardrail_labels_soft():
    text = SKILL_MD.read_text()
    section = _get_hard_guardrails_section(text)
    assert '"soft"' in section or "soft" in section.lower(), (
        "Guardrail must state model-asserted times are labeled provenance_class: 'soft'"
    )


def test_skill_md_guardrail_names_real_provenance_sources():
    text = SKILL_MD.read_text()
    section = _get_hard_guardrails_section(text)
    assert "git commit" in section.lower(), "Guardrail must name git commits as real provenance"
    assert "clipping" in section.lower() or "file" in section.lower(), (
        "Guardrail must name the clipping file date as real provenance"
    )


def test_skill_md_guardrail_covers_conception_window():
    text = SKILL_MD.read_text()
    section = _get_hard_guardrails_section(text)
    assert "conception" in section.lower() or "estimated_conception_window" in section, (
        "Guardrail must specifically address fabricated conception-window dates"
    )


def test_skill_md_guardrail_says_never_present_as_authoritative():
    text = SKILL_MD.read_text()
    section = _get_hard_guardrails_section(text)
    assert "never" in section.lower() or "not" in section.lower(), (
        "Guardrail must prohibit presenting model timestamps as authoritative"
    )


def test_evals_json_has_timestamp_guardrail_eval():
    data = json.loads(EVALS_JSON.read_text())
    evals = data["evals"]
    guardrail_evals = [e for e in evals if "timestamp" in e["name"] or "llm" in e["name"].lower()]
    assert len(guardrail_evals) >= 1, "evals.json must have at least one timestamp-guardrail eval"


def test_evals_json_guardrail_eval_structure():
    data = json.loads(EVALS_JSON.read_text())
    evals = data["evals"]
    guardrail_evals = [e for e in evals if "timestamp" in e["name"] or "llm" in e["name"].lower()]
    eval_entry = guardrail_evals[0]
    assert "prompt" in eval_entry, "Guardrail eval must have a prompt"
    assert "expected_output" in eval_entry, "Guardrail eval must have expected_output"
    assert "files" in eval_entry, "Guardrail eval must list relevant files"


def test_evals_json_guardrail_expected_output_refuses_model_timestamp():
    data = json.loads(EVALS_JSON.read_text())
    evals = data["evals"]
    guardrail_evals = [e for e in evals if "timestamp" in e["name"] or "llm" in e["name"].lower()]
    expected = guardrail_evals[0]["expected_output"].lower()
    assert "refuse" in expected or "does not" in expected or "does NOT" in guardrail_evals[0]["expected_output"], (
        "Guardrail eval expected output must describe refusing to use model timestamp as authoritative"
    )


def test_evals_json_guardrail_expected_output_names_real_provenance():
    data = json.loads(EVALS_JSON.read_text())
    evals = data["evals"]
    guardrail_evals = [e for e in evals if "timestamp" in e["name"] or "llm" in e["name"].lower()]
    expected = guardrail_evals[0]["expected_output"].lower()
    assert "git commit" in expected or "filesystem" in expected or "clipping" in expected, (
        "Guardrail eval must name real provenance sources (git commit, filesystem, clipping)"
    )


def test_evals_json_is_valid_json():
    text = EVALS_JSON.read_text()
    data = json.loads(text)
    assert "skill_name" in data
    assert "evals" in data
    assert isinstance(data["evals"], list)
    assert len(data["evals"]) >= 6, "evals.json should have at least 6 evals (5 existing + 1 guardrail)"


def test_evals_json_ids_are_unique():
    data = json.loads(EVALS_JSON.read_text())
    ids = [e["id"] for e in data["evals"]]
    assert len(ids) == len(set(ids)), f"Eval IDs must be unique, got: {ids}"
