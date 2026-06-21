"""Tests for verbatim-quote + source-doc capture into draft sections (Story #416)."""

import json
import re
from pathlib import Path

SKILL_MD = Path(__file__).parent.parent / "plugins/maker/skills/file-a-patent/SKILL.md"
AGENT_MD = Path(__file__).parent.parent / "plugins/maker/skills/file-a-patent/agents/quote-capture.md"
PACKET_SCHEMA_MD = Path(__file__).parent.parent / "plugins/maker/skills/file-a-patent/references/packet-schema.md"

REQUIRED_QUOTE_FIELDS = {"text", "speaker", "source_doc", "captured_at", "draft_section", "attorney_flag"}

TRIGGER_PHRASES = [
    "capture that quote",
    "record what I just said",
    "log this verbatim",
    "capture inventor quote",
    "quote capture",
]

SECTION_TARGETS = [
    "INVENTOR-QUESTIONNAIRE",
    "DISCLOSURE-TIMELINE",
    "INVENTION-SUMMARY",
    "NOVELTY-CANDIDATES",
    "RIGHTS-PROVENANCE",
]


def _parse_json_block(md_text: str) -> dict:
    match = re.search(r"```json\s*(\{.*?\})\s*```", md_text, re.DOTALL)
    assert match, "No JSON block found in agent file"
    raw = match.group(1)
    raw = re.sub(r"<[^>]+>", "PLACEHOLDER", raw)
    # attorney_flag value is boolean false — keep as-is
    return json.loads(raw)


def test_agent_file_exists():
    assert AGENT_MD.exists(), "agents/quote-capture.md must exist"


def test_agent_has_trigger_phrases():
    text = AGENT_MD.read_text()
    for phrase in TRIGGER_PHRASES:
        assert phrase in text, f"Agent must list trigger phrase: '{phrase}'"


def test_agent_quote_object_has_required_fields():
    text = AGENT_MD.read_text()
    data = _parse_json_block(text)
    block = data.get("verbatim_quote", data)
    missing = REQUIRED_QUOTE_FIELDS - set(block.keys())
    assert not missing, f"verbatim_quote object missing fields: {missing}"


def test_agent_attorney_flag_present():
    text = AGENT_MD.read_text()
    assert "attorney_flag" in text, "Agent must document attorney_flag field"


def test_agent_no_paraphrase_rule():
    text = AGENT_MD.read_text()
    assert "never paraphrase" in text.lower() or "no paraphrase" in text.lower() or "never paraphrasing" in text.lower(), (
        "Agent must state the no-paraphrase rule"
    )


def test_agent_model_speaker_flag():
    text = AGENT_MD.read_text()
    assert '"model"' in text, "Agent must document speaker: 'model' for assisting-model quotes"


def test_agent_model_attorney_flag_true():
    text = AGENT_MD.read_text()
    assert "attorney_flag: true" in text or "attorney_flag` to `true" in text or "attorney review" in text.lower(), (
        "Agent must flag model quotes with attorney_flag: true"
    )


def test_agent_routing_table_covers_sections():
    text = AGENT_MD.read_text()
    for section in SECTION_TARGETS:
        assert section in text, f"Agent routing table must reference section: {section}"


def test_agent_no_auto_include_model_quotes():
    text = AGENT_MD.read_text()
    assert "must not" in text.lower() or "must NOT" in text or "do not" in text.lower(), (
        "Agent must prohibit auto-including model quotes as inventor disclosure"
    )


def test_skill_md_verbatim_quote_capture_section():
    text = SKILL_MD.read_text()
    assert "## Verbatim Quote Capture" in text, "SKILL.md must have '## Verbatim Quote Capture' section"


def test_skill_md_no_paraphrase_rule():
    text = SKILL_MD.read_text()
    section_match = re.search(r"## Verbatim Quote Capture(.*?)## ", text, re.DOTALL)
    assert section_match, "Cannot find Verbatim Quote Capture section"
    section = section_match.group(1)
    assert "paraphrase" in section.lower(), "SKILL.md must address paraphrasing in the quote capture section"


def test_skill_md_references_agent():
    text = SKILL_MD.read_text()
    assert "agents/quote-capture.md" in text or "quote-capture" in text, (
        "SKILL.md must reference the quote-capture agent"
    )


def test_skill_md_attorney_flag_mentioned():
    text = SKILL_MD.read_text()
    assert "attorney_flag" in text or "attorney flag" in text.lower(), (
        "SKILL.md Verbatim Quote Capture section must mention attorney_flag"
    )


def test_packet_schema_inventor_questionnaire_has_quotes_section():
    text = PACKET_SCHEMA_MD.read_text()
    assert "Inventor Quotes" in text, "packet-schema.md INVENTOR-QUESTIONNAIRE must have an Inventor Quotes subsection"


def test_packet_schema_no_paraphrase_rule():
    text = PACKET_SCHEMA_MD.read_text()
    assert "paraphrase" in text.lower() or "verbatim" in text.lower(), (
        "packet-schema.md must prohibit paraphrasing of captured quotes"
    )


def test_packet_schema_disclosure_timeline_has_quote_guidance():
    text = PACKET_SCHEMA_MD.read_text()
    # Anchor section boundaries to lines that START with "## " (not inside code spans)
    timeline_match = re.search(r"^## DISCLOSURE-TIMELINE\.md(.*?)^## ", text, re.DOTALL | re.MULTILINE)
    assert timeline_match, "packet-schema.md must have DISCLOSURE-TIMELINE.md section"
    section = timeline_match.group(1)
    assert "quote" in section.lower() or "verbatim" in section.lower(), (
        "DISCLOSURE-TIMELINE section must reference quote capture"
    )
