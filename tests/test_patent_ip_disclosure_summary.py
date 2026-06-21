"""Tests for ip_disclosure_summary block schema (Story #415)."""

import json
import re
from pathlib import Path

SKILL_MD = Path(__file__).parent.parent / "plugins/maker/skills/file-a-patent/SKILL.md"
SCHEMA_MD = Path(__file__).parent.parent / "plugins/maker/skills/file-a-patent/references/ip-disclosure-summary-schema.md"
PACKET_SCHEMA_MD = Path(__file__).parent.parent / "plugins/maker/skills/file-a-patent/references/packet-schema.md"

REQUIRED_TOP_KEYS = {"technical_field", "invention_title", "problem_solved", "novel_elements", "technical_dependencies", "verbatim_inventor_quotes"}
REQUIRED_QUOTE_KEYS = {"text", "speaker", "source_doc", "captured_at"}

SECTION_MAPPINGS = {
    "technical_field": "Background",
    "problem_solved": "Background",
    "technical_dependencies": "Background",
    "novel_elements": "Detailed Description",
    "verbatim_inventor_quotes": "Specification",
}


def _parse_top_json_block(md_text: str) -> dict:
    match = re.search(r"```json\s*(\{.*?\})\s*```", md_text, re.DOTALL)
    assert match, "No JSON block found"
    raw = match.group(1)
    raw = re.sub(r"<[^>]+>", "PLACEHOLDER", raw)
    return json.loads(raw)


def test_schema_file_exists():
    assert SCHEMA_MD.exists(), "ip-disclosure-summary-schema.md must exist"


def test_schema_top_level_keys():
    text = SCHEMA_MD.read_text()
    data = _parse_top_json_block(text)
    block = data.get("ip_disclosure_summary", data)
    missing = REQUIRED_TOP_KEYS - set(block.keys())
    assert not missing, f"ip_disclosure_summary block missing keys: {missing}"


def test_novel_elements_is_list():
    text = SCHEMA_MD.read_text()
    data = _parse_top_json_block(text)
    block = data.get("ip_disclosure_summary", data)
    assert isinstance(block["novel_elements"], list), "novel_elements must be a list"


def test_technical_dependencies_is_list():
    text = SCHEMA_MD.read_text()
    data = _parse_top_json_block(text)
    block = data.get("ip_disclosure_summary", data)
    assert isinstance(block["technical_dependencies"], list), "technical_dependencies must be a list"


def test_verbatim_inventor_quotes_is_list():
    text = SCHEMA_MD.read_text()
    data = _parse_top_json_block(text)
    block = data.get("ip_disclosure_summary", data)
    assert isinstance(block["verbatim_inventor_quotes"], list), "verbatim_inventor_quotes must be a list"


def test_quote_object_has_required_keys():
    text = SCHEMA_MD.read_text()
    data = _parse_top_json_block(text)
    block = data.get("ip_disclosure_summary", data)
    quotes = block["verbatim_inventor_quotes"]
    assert len(quotes) >= 1, "Schema must include at least one example quote object"
    quote = quotes[0]
    missing = REQUIRED_QUOTE_KEYS - set(quote.keys())
    assert not missing, f"Quote object missing keys: {missing}"


def test_schema_documents_section_mapping():
    text = SCHEMA_MD.read_text()
    assert "Background" in text, "Schema must map fields to Background section"
    assert "Detailed Description" in text, "Schema must map fields to Detailed Description"
    assert "Specification" in text, "Schema must map fields to Specification"


def test_schema_documents_model_speaker_flag():
    text = SCHEMA_MD.read_text()
    assert '"model"' in text, "Schema must document speaker: 'model' flag for assisting-model quotes"
    assert "attorney" in text.lower(), "Schema must flag model quotes for attorney review"


def test_schema_cautions_against_patentability_assertion():
    text = SCHEMA_MD.read_text()
    assert "cautious" in text.lower() or "do not assert" in text.lower() or "attorney review" in text.lower(), (
        "Schema must caution against asserting patentability in novel_elements"
    )


def test_skill_md_ip_disclosure_summary_section_exists():
    text = SKILL_MD.read_text()
    assert "## IP Disclosure Summary" in text, "SKILL.md must have '## IP Disclosure Summary' section"


def test_skill_md_section_has_required_fields():
    text = SKILL_MD.read_text()
    section_match = re.search(r"## IP Disclosure Summary(.*?)## ", text, re.DOTALL)
    assert section_match, "Cannot find IP Disclosure Summary section"
    section = section_match.group(1)
    for key in REQUIRED_TOP_KEYS:
        assert key in section, f"SKILL.md IP Disclosure Summary must mention field '{key}'"


def test_skill_md_section_mentions_section_mapping():
    text = SKILL_MD.read_text()
    section_match = re.search(r"## IP Disclosure Summary(.*?)## ", text, re.DOTALL)
    section = section_match.group(1)
    assert "Background" in section, "Section mapping in SKILL.md must mention Background"
    assert "Detailed Description" in section, "Section mapping must mention Detailed Description"


def test_packet_schema_invention_summary_references_ip_disclosure():
    text = PACKET_SCHEMA_MD.read_text()
    assert "ip_disclosure_summary" in text, "packet-schema.md must reference ip_disclosure_summary"


def test_packet_schema_disclosure_timeline_references_ip_blocks():
    text = PACKET_SCHEMA_MD.read_text()
    assert "ip_capture" in text or "ip_disclosure_summary" in text, (
        "packet-schema.md DISCLOSURE-TIMELINE must reference ip_capture or ip_disclosure_summary"
    )
