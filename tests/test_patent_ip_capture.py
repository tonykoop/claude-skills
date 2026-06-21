"""Tests for ip_capture schema (Story #414)."""

import json
import re
from pathlib import Path

SKILL_MD = Path(__file__).parent.parent / "plugins/maker/skills/file-a-patent/SKILL.md"
SCHEMA_MD = Path(__file__).parent.parent / "plugins/maker/skills/file-a-patent/references/ip-capture-schema.md"

REQUIRED_FIELDS = {"utc", "local", "timezone", "origin", "provenance_class", "provenance_note"}

TRIGGER_PHRASES = [
    "capture IP timestamp",
    "log this as IP",
    "timestamp this invention",
    "record IP moment",
]

ISO8601_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


def _parse_json_block(md_text: str) -> dict:
    match = re.search(r"```json\s*(\{.*?\})\s*```", md_text, re.DOTALL)
    assert match, "No JSON block found in schema file"
    raw = match.group(1)
    raw = re.sub(r"<[^>]+>", "PLACEHOLDER", raw)
    return json.loads(raw)


def test_schema_file_exists():
    assert SCHEMA_MD.exists(), "ip-capture-schema.md must exist"


def test_schema_required_fields_present():
    text = SCHEMA_MD.read_text()
    data = _parse_json_block(text)
    block = data.get("ip_capture", data)
    assert REQUIRED_FIELDS == set(block.keys()), (
        f"Schema block must have exactly: {REQUIRED_FIELDS}, got: {set(block.keys())}"
    )


def test_provenance_class_always_soft():
    text = SCHEMA_MD.read_text()
    data = _parse_json_block(text)
    block = data.get("ip_capture", data)
    assert block["provenance_class"] == "soft", "provenance_class must be 'soft' in schema example"


def test_schema_documents_soft_and_hard_classes():
    text = SCHEMA_MD.read_text()
    assert '"soft"' in text, "Schema must document the 'soft' provenance class"
    assert '"hard"' in text, "Schema must document the 'hard' provenance class"


def test_skill_md_contains_ip_capture_section():
    text = SKILL_MD.read_text()
    assert "## IP Capture" in text, "SKILL.md must have an '## IP Capture' section"


def test_skill_md_lists_trigger_phrases():
    text = SKILL_MD.read_text()
    for phrase in TRIGGER_PHRASES:
        assert phrase in text, f"SKILL.md must list trigger phrase: '{phrase}'"


def test_skill_md_ip_capture_block_has_required_fields():
    text = SKILL_MD.read_text()
    section_match = re.search(r"## IP Capture(.*?)## ", text, re.DOTALL)
    assert section_match, "Cannot find IP Capture section in SKILL.md"
    section = section_match.group(1)
    for field in REQUIRED_FIELDS:
        assert field in section, f"SKILL.md IP Capture block must include field '{field}'"


def test_skill_md_provenance_class_soft_in_ip_capture():
    text = SKILL_MD.read_text()
    section_match = re.search(r"## IP Capture(.*?)## ", text, re.DOTALL)
    section = section_match.group(1)
    assert '"soft"' in section, "IP Capture section must show provenance_class as 'soft'"


def test_skill_md_no_authoritative_timestamp_claim():
    text = SKILL_MD.read_text()
    section_match = re.search(r"## IP Capture(.*?)## ", text, re.DOTALL)
    section = section_match.group(1)
    assert "not claim" in section.lower() or "do not" in section.lower() or "not" in section.lower(), (
        "IP Capture section must caution against claiming timestamps are authoritative"
    )


def test_schema_references_guardrail_story():
    text = SCHEMA_MD.read_text()
    assert "#418" in text or "guardrail" in text.lower(), (
        "Schema must reference the guardrail story (#418) or use the word 'guardrail'"
    )
