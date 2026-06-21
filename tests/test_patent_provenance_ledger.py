"""Tests for provenance-ledger integration with patent-funnel dossiers (Story #417)."""

import json
import re
from pathlib import Path

SKILL_MD = Path(__file__).parent.parent / "plugins/maker/skills/file-a-patent/SKILL.md"
SCHEMA_MD = Path(__file__).parent.parent / "plugins/maker/skills/file-a-patent/references/provenance-ledger-schema.md"

REQUIRED_TOP_KEYS = {
    "dossier_id",
    "created_at",
    "ip_captures",
    "ip_disclosure_summaries",
    "quote_refs",
    "source_issues",
    "key_commits",
    "output_folder",
    "linked_patent_funnel_issue",
}

OUTPUT_FOLDER_PATTERN = re.compile(r"_invention-packets/")


def _parse_json_block(md_text: str) -> dict:
    match = re.search(r"```json\s*(\{.*?\})\s*```", md_text, re.DOTALL)
    assert match, "No JSON block found in schema"
    raw = match.group(1)
    raw = re.sub(r"<[^>]+>", "PLACEHOLDER", raw)
    return json.loads(raw)


def test_schema_file_exists():
    assert SCHEMA_MD.exists(), "provenance-ledger-schema.md must exist"


def test_schema_required_top_level_keys():
    text = SCHEMA_MD.read_text()
    data = _parse_json_block(text)
    missing = REQUIRED_TOP_KEYS - set(data.keys())
    assert not missing, f"PROVENANCE-LEDGER.json schema missing keys: {missing}"


def test_schema_ip_captures_is_list():
    text = SCHEMA_MD.read_text()
    data = _parse_json_block(text)
    assert isinstance(data["ip_captures"], list), "ip_captures must be a list"


def test_schema_ip_disclosure_summaries_is_list():
    text = SCHEMA_MD.read_text()
    data = _parse_json_block(text)
    assert isinstance(data["ip_disclosure_summaries"], list), "ip_disclosure_summaries must be a list"


def test_schema_quote_refs_is_list():
    text = SCHEMA_MD.read_text()
    data = _parse_json_block(text)
    assert isinstance(data["quote_refs"], list), "quote_refs must be a list"


def test_schema_output_folder_path_convention():
    text = SCHEMA_MD.read_text()
    assert "_invention-packets/" in text, "Schema must document the _invention-packets/<slug>/ write path"


def test_schema_documents_cross_link_not_duplicate():
    text = SCHEMA_MD.read_text()
    assert "cross-link" in text.lower() or "cross link" in text.lower() or "not duplicate" in text.lower() or "do not duplicate" in text.lower(), (
        "Schema must instruct to cross-link the patent-funnel dossier, not duplicate it"
    )


def test_schema_linked_patent_funnel_issue_nullable():
    text = SCHEMA_MD.read_text()
    assert "null" in text, "Schema must show linked_patent_funnel_issue can be null"


def test_schema_created_at_must_be_hard_provenance():
    text = SCHEMA_MD.read_text()
    assert "mtime" in text.lower() or "git commit" in text.lower() or "hard provenance" in text.lower(), (
        "Schema must specify that created_at comes from file mtime or git commit (hard provenance)"
    )


def test_schema_no_model_asserted_created_at():
    text = SCHEMA_MD.read_text()
    assert "not model" in text.lower() or "not a model" in text.lower() or "do not use a model" in text.lower() or "NOT model" in text, (
        "Schema must prohibit model-asserted timestamps for created_at"
    )


def test_schema_key_commits_is_list():
    text = SCHEMA_MD.read_text()
    data = _parse_json_block(text)
    assert isinstance(data["key_commits"], list), "key_commits must be a list"


def test_schema_source_issues_is_list():
    text = SCHEMA_MD.read_text()
    data = _parse_json_block(text)
    assert isinstance(data["source_issues"], list), "source_issues must be a list"


def test_skill_md_provenance_ledger_section_exists():
    text = SKILL_MD.read_text()
    assert "## Provenance Ledger" in text, "SKILL.md must have '## Provenance Ledger' section"


def test_skill_md_provenance_ledger_has_write_path():
    text = SKILL_MD.read_text()
    section_match = re.search(r"^## Provenance Ledger(.*?)^## ", text, re.DOTALL | re.MULTILINE)
    assert section_match, "Cannot find Provenance Ledger section"
    section = section_match.group(1)
    assert "_invention-packets/" in section, "Provenance Ledger section must show the write path"


def test_skill_md_no_duplicate_funnel_rule():
    text = SKILL_MD.read_text()
    assert "not duplicate" in text.lower() or "do not duplicate" in text.lower() or "cross-link" in text.lower(), (
        "SKILL.md must instruct to cross-link the patent-funnel dossier, not duplicate it"
    )


def test_skill_md_linked_patent_funnel_issue_mentioned():
    text = SKILL_MD.read_text()
    assert "linked_patent_funnel_issue" in text or "patent-funnel" in text, (
        "SKILL.md must reference the patent-funnel cross-link field"
    )


def test_skill_md_no_public_location_rule():
    text = SKILL_MD.read_text()
    section_match = re.search(r"^## Provenance Ledger(.*?)^## ", text, re.DOTALL | re.MULTILINE)
    assert section_match
    section = section_match.group(1)
    assert "public" in section.lower(), "Provenance Ledger section must prohibit writing to public locations"
