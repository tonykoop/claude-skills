"""Tests for image_chapter_validator.py (image-gen-2 asset contract gate, #210)."""
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from image_chapter_validator import (
    validate_asset,
    validate_authority_artifact,
    validate_chapter,
    ALLOWED_KINDS,
    REVIEW_ORDER,
    main,
)

# --- helpers ------------------------------------------------------------------

def _asset(**overrides):
    """Return a fully valid asset sidecar."""
    base = {
        "asset_id": "flute-v2-cover",
        "kind": "cover",
        "prompt": "isometric technical illustration of a bamboo flute",
        "derivative": True,
        "non_dimensional": True,
        "source_provenance": "synthetic",
        "packet_ref": "abc1234",
        "caption": "Bamboo Flute v2 design study",
        "alt_text": "Isometric render of a bamboo flute",
        "review_state": "proof-reviewed",
    }
    base.update(overrides)
    return base


def _authority_artifact(**overrides):
    base = {"artifact_id": "params-csv", "kind": "parameter-csv", "packet_ref": "abc1234"}
    base.update(overrides)
    return base


def _chapter(**overrides):
    base = {
        "chapter_id": "flute-v2",
        "chapter_framing": "design-book",
        "packet_ref": "abc1234",
        "assets": [_asset()],
        "authority_artifacts": [_authority_artifact()],
    }
    base.update(overrides)
    return base


def _violations(result):
    return result["violations"]


def _violation_fields(result):
    return {v["field"] for v in result["violations"]}


# --- validate_asset -----------------------------------------------------------

class TestValidateAssetPass(unittest.TestCase):
    def test_fully_valid_asset_no_violations(self):
        self.assertEqual(validate_asset(_asset(), "abc1234"), [])

    def test_no_chapter_packet_ref_still_passes(self):
        self.assertEqual(validate_asset(_asset(), None), [])

    def test_all_allowed_kinds_pass(self):
        for kind in ALLOWED_KINDS:
            self.assertEqual(validate_asset(_asset(kind=kind), None), [],
                             msg=f"kind={kind!r} should pass")


class TestValidateAssetMissingFields(unittest.TestCase):
    def test_missing_asset_id(self):
        a = _asset()
        del a["asset_id"]
        v = validate_asset(a, None)
        fields = {x["field"] for x in v}
        self.assertIn("asset_id", fields)

    def test_missing_kind(self):
        a = _asset()
        del a["kind"]
        fields = {x["field"] for x in validate_asset(a, None)}
        self.assertIn("kind", fields)

    def test_missing_prompt(self):
        fields = {x["field"] for x in validate_asset(_asset(prompt=None), None)}
        self.assertIn("prompt", fields)

    def test_missing_caption(self):
        a = _asset()
        del a["caption"]
        fields = {x["field"] for x in validate_asset(a, None)}
        self.assertIn("caption", fields)

    def test_missing_alt_text(self):
        a = _asset()
        del a["alt_text"]
        fields = {x["field"] for x in validate_asset(a, None)}
        self.assertIn("alt_text", fields)

    def test_missing_source_provenance(self):
        a = _asset()
        del a["source_provenance"]
        fields = {x["field"] for x in validate_asset(a, None)}
        self.assertIn("source_provenance", fields)

    def test_missing_packet_ref(self):
        a = _asset()
        del a["packet_ref"]
        fields = {x["field"] for x in validate_asset(a, None)}
        self.assertIn("packet_ref", fields)

    def test_empty_asset_id_string(self):
        fields = {x["field"] for x in validate_asset(_asset(asset_id="   "), None)}
        self.assertIn("asset_id", fields)


class TestValidateAssetDerivative(unittest.TestCase):
    def test_derivative_false_violation(self):
        fields = {x["field"] for x in validate_asset(_asset(derivative=False), None)}
        self.assertIn("derivative", fields)

    def test_derivative_none_violation(self):
        fields = {x["field"] for x in validate_asset(_asset(derivative=None), None)}
        self.assertIn("derivative", fields)

    def test_derivative_string_violation(self):
        fields = {x["field"] for x in validate_asset(_asset(derivative="yes"), None)}
        self.assertIn("derivative", fields)


class TestValidateAssetNonDimensional(unittest.TestCase):
    def test_non_dimensional_false_violation(self):
        fields = {x["field"] for x in validate_asset(_asset(non_dimensional=False), None)}
        self.assertIn("non_dimensional", fields)

    def test_non_dimensional_none_violation(self):
        fields = {x["field"] for x in validate_asset(_asset(non_dimensional=None), None)}
        self.assertIn("non_dimensional", fields)


class TestValidateAssetKind(unittest.TestCase):
    def test_unknown_kind_violation(self):
        fields = {x["field"] for x in validate_asset(_asset(kind="sketch"), None)}
        self.assertIn("kind", fields)

    def test_empty_kind_violation(self):
        fields = {x["field"] for x in validate_asset(_asset(kind=""), None)}
        self.assertIn("kind", fields)


class TestValidateAssetReviewState(unittest.TestCase):
    def test_unknown_review_state_violation(self):
        fields = {x["field"] for x in validate_asset(_asset(review_state="reviewed"), None)}
        self.assertIn("review_state", fields)

    def test_draft_passes_field_check(self):
        # 'draft' is a valid review_state value; it won't trigger a field-level
        # violation from validate_asset. The publishability check is in validate_chapter.
        violations = validate_asset(_asset(review_state="draft"), None)
        field_errors = [v for v in violations if v["field"] == "review_state"]
        self.assertEqual(field_errors, [], "draft is a valid state at the field level")

    def test_non_string_review_state_violation(self):
        fields = {x["field"] for x in validate_asset(_asset(review_state=1), None)}
        self.assertIn("review_state", fields)


class TestValidateAssetPacketRef(unittest.TestCase):
    def test_mismatched_packet_ref_violation(self):
        v = validate_asset(_asset(packet_ref="other"), "abc1234")
        fields = {x["field"] for x in v}
        self.assertIn("packet_ref", fields)

    def test_matching_packet_ref_passes(self):
        v = validate_asset(_asset(packet_ref="abc1234"), "abc1234")
        self.assertEqual([x for x in v if x["field"] == "packet_ref"], [])


# --- validate_authority_artifact ---------------------------------------------

class TestValidateAuthorityArtifact(unittest.TestCase):
    def test_valid_authority_artifact_no_violations(self):
        self.assertEqual(validate_authority_artifact(_authority_artifact()), [])

    def test_derivative_true_on_authority_is_violation(self):
        v = validate_authority_artifact(_authority_artifact(derivative=True))
        self.assertTrue(any(x["field"] == "derivative" for x in v))

    def test_missing_artifact_id_is_violation(self):
        a = _authority_artifact()
        del a["artifact_id"]
        v = validate_authority_artifact(a)
        self.assertTrue(any(x["field"] == "artifact_id" for x in v))

    def test_missing_packet_ref_is_violation(self):
        a = _authority_artifact()
        del a["packet_ref"]
        v = validate_authority_artifact(a)
        self.assertTrue(any(x["field"] == "packet_ref" for x in v))


# --- validate_chapter ---------------------------------------------------------

class TestValidateChapterPass(unittest.TestCase):
    def test_fully_valid_chapter_passes(self):
        result = validate_chapter(_chapter())
        self.assertEqual(result["decision"], "pass")
        self.assertTrue(result["publishable"])
        self.assertEqual(result["violations"], [])

    def test_chapter_counts(self):
        result = validate_chapter(_chapter())
        self.assertEqual(result["asset_count"], 1)
        self.assertEqual(result["authority_artifact_count"], 1)

    def test_chapter_id_preserved(self):
        result = validate_chapter(_chapter(chapter_id="my-chapter"))
        self.assertEqual(result["chapter_id"], "my-chapter")


class TestValidateChapterPublishability(unittest.TestCase):
    def test_draft_asset_not_publishable(self):
        c = _chapter(assets=[_asset(review_state="draft")])
        result = validate_chapter(c)
        self.assertEqual(result["decision"], "fail")
        self.assertFalse(result["publishable"])
        # The review_state violation should mention proof-reviewed
        msgs = " ".join(v["message"] for v in result["violations"])
        self.assertIn("proof-reviewed", msgs)

    def test_privacy_reviewed_asset_not_publishable(self):
        c = _chapter(assets=[_asset(review_state="privacy-reviewed")])
        result = validate_chapter(c)
        self.assertFalse(result["publishable"])

    def test_proof_reviewed_is_publishable(self):
        c = _chapter(assets=[_asset(review_state="proof-reviewed")])
        result = validate_chapter(c)
        self.assertTrue(result["publishable"])

    def test_any_draft_asset_blocks_whole_chapter(self):
        c = _chapter(assets=[
            _asset(asset_id="a1", review_state="proof-reviewed"),
            _asset(asset_id="a2", review_state="draft"),
        ])
        result = validate_chapter(c)
        self.assertFalse(result["publishable"])


class TestValidateChapterPacketRef(unittest.TestCase):
    def test_missing_chapter_packet_ref_fails(self):
        c = _chapter()
        del c["packet_ref"]
        result = validate_chapter(c)
        self.assertEqual(result["decision"], "fail")
        fields = {v.get("field") for v in result["violations"]}
        self.assertIn("packet_ref", fields)

    def test_empty_packet_ref_fails(self):
        result = validate_chapter(_chapter(packet_ref=""))
        self.assertEqual(result["decision"], "fail")


class TestValidateChapterEdgeCases(unittest.TestCase):
    def test_no_assets_no_authority_artifacts_passes_with_valid_packet(self):
        result = validate_chapter({"chapter_id": "x", "packet_ref": "abc", "assets": []})
        self.assertEqual(result["decision"], "pass")
        self.assertTrue(result["publishable"])

    def test_non_dict_asset_entry_flagged(self):
        c = _chapter(assets=["not-a-dict"])
        result = validate_chapter(c)
        self.assertEqual(result["decision"], "fail")

    def test_authority_artifact_with_derivative_flagged(self):
        aa = _authority_artifact(derivative=True)
        result = validate_chapter(_chapter(authority_artifacts=[aa]))
        self.assertEqual(result["decision"], "fail")
        fields = {v.get("field") for v in result["violations"]}
        self.assertIn("derivative", fields)

    def test_multiple_violations_all_reported(self):
        bad_asset = _asset(derivative=False, non_dimensional=False, kind="sketch")
        result = validate_chapter(_chapter(assets=[bad_asset]))
        fields = {v["field"] for v in result["violations"]}
        self.assertGreaterEqual(len(fields), 3)


# --- CLI tests ----------------------------------------------------------------

class TestCLI(unittest.TestCase):
    def _run_cli(self, payload: dict, args=None):
        raw = json.dumps(payload)
        with patch("sys.stdin", io.StringIO(raw)):
            out = io.StringIO()
            with patch("sys.stdout", out):
                rc = main(args or [])
        return rc, out.getvalue()

    def test_valid_chapter_exits_0(self):
        rc, out = self._run_cli(_chapter())
        self.assertEqual(rc, 0)
        result = json.loads(out)
        self.assertEqual(result["decision"], "pass")

    def test_invalid_chapter_exits_1(self):
        c = _chapter(assets=[_asset(derivative=False)])
        rc, _ = self._run_cli(c)
        self.assertEqual(rc, 1)

    def test_bad_json_exits_2(self):
        with patch("sys.stdin", io.StringIO("not-json")):
            rc = main([])
        self.assertEqual(rc, 2)

    def test_non_dict_input_exits_2(self):
        with patch("sys.stdin", io.StringIO("[1, 2, 3]")):
            rc = main([])
        self.assertEqual(rc, 2)

    def test_require_publishable_flag_exits_1_on_draft(self):
        c = _chapter(assets=[_asset(review_state="draft")])
        rc, _ = self._run_cli(c, args=["--require-publishable"])
        self.assertEqual(rc, 1)

    def test_require_publishable_flag_passes_on_proof_reviewed(self):
        rc, _ = self._run_cli(_chapter(), args=["--require-publishable"])
        self.assertEqual(rc, 0)

    def test_output_is_valid_json(self):
        _, out = self._run_cli(_chapter())
        parsed = json.loads(out)
        self.assertIn("decision", parsed)
        self.assertIn("violations", parsed)
        self.assertIn("publishable", parsed)


if __name__ == "__main__":
    unittest.main()
