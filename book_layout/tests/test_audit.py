"""
Tests for book_layout.audit — editorial quality rules, AuditFinding,
EditorialAuditResult.

All tests offline and deterministic.

Refs: claude-skills#210
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from book_layout.audit import (
    AuditFinding, EditorialAuditResult,
    CHAPTER_BALANCE_TOLERANCE, TEMPLATE_VARIETY_THRESHOLD,
    audit_book, audit_chapter,
)
from book_layout.planner import ChapterSpec, TemplateRules, plan_book, plan_chapter
from book_layout.schema import (
    Book, BookFormat, Chapter, ImageSlot, Page, PageSize,
    SlotRole, TextBlock, TextRole,
)
from book_layout.yearbook import (
    GateStatus, InstrumentChapterSpec, InstrumentContentSpec,
    YearbookConfig, build_yearbook,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_book(item_counts: tuple = (4, 8), fmt: BookFormat = BookFormat.PHOTO_BOOK) -> Book:
    rules = TemplateRules(default_template="hero+caption")
    specs = [ChapterSpec(title=f"Ch{i+1}", item_count=n)
             for i, n in enumerate(item_counts)]
    return plan_book(specs, book_format=fmt, template_rules=rules)


# ── EditorialAuditResult ──────────────────────────────────────────────────────

class TestEditorialAuditResult:
    def test_default_ok(self):
        r = EditorialAuditResult()
        assert r.ok is True

    def test_error_sets_ok_false(self):
        r = EditorialAuditResult()
        r.error("test-rule", "bad", "book")
        assert r.ok is False

    def test_warn_does_not_break_ok(self):
        r = EditorialAuditResult()
        r.warn("test-rule", "advisory", "book")
        assert r.ok is True

    def test_info_does_not_break_ok(self):
        r = EditorialAuditResult()
        r.info("test-rule", "fyi", "book")
        assert r.ok is True

    def test_finding_properties(self):
        r = EditorialAuditResult()
        r.error("r1", "msg", "ctx")
        r.warn("r2", "msg", "ctx")
        r.info("r3", "msg", "ctx")
        assert len(r.errors) == 1
        assert len(r.warnings) == 1
        assert len(r.infos) == 1

    def test_add_finding(self):
        r = EditorialAuditResult()
        r.add(AuditFinding("warn", "rule", "msg", "ctx"))
        assert len(r.findings) == 1

    def test_repr_shows_status(self):
        r = EditorialAuditResult()
        assert "PASS" in repr(r)
        r.error("r", "m", "c")
        assert "FAIL" in repr(r)


# ── audit_book() on clean book ────────────────────────────────────────────────

class TestAuditBookClean:
    def test_balanced_book_passes(self):
        book = _make_book((8, 8))   # perfectly balanced
        result = audit_book(book)
        balance_errors = [f for f in result.findings
                          if f.rule == "chapter-balance" and f.severity == "error"]
        assert balance_errors == []

    def test_ok_with_reasonable_book(self):
        book = _make_book((6, 8, 7))
        result = audit_book(book)
        assert result.ok   # warnings may exist but no errors

    def test_empty_book_returns_error(self):
        book = Book(title="T", book_format=BookFormat.PHOTO_BOOK)
        result = audit_book(book)
        assert not result.ok
        assert any(f.rule == "no-chapters" for f in result.findings)


# ── chapter-balance rule ──────────────────────────────────────────────────────

class TestChapterBalance:
    def test_severely_unbalanced_triggers_warning(self):
        """One 1-page chapter vs one 20-page chapter."""
        rules = TemplateRules(default_template="full-bleed")  # 1 slot/page
        book = plan_book(
            [ChapterSpec(title="Tiny", item_count=1),
             ChapterSpec(title="Huge", item_count=20)],
            template_rules=rules,
        )
        result = audit_book(book)
        balance_warns = [f for f in result.findings if f.rule == "chapter-balance"]
        assert len(balance_warns) > 0

    def test_single_chapter_no_balance_finding(self):
        book = _make_book((4,))
        result = audit_book(book)
        balance_findings = [f for f in result.findings if f.rule == "chapter-balance"]
        assert balance_findings == []


# ── template-variety rule ─────────────────────────────────────────────────────

class TestTemplateVariety:
    def test_all_same_template_long_chapter_triggers_warning(self):
        """A 10-page chapter all on 'full-bleed' should warn."""
        rules = TemplateRules(default_template="full-bleed")
        book = plan_book(
            [ChapterSpec(title="Mono", item_count=10)],
            template_rules=rules,
        )
        result = audit_book(book)
        variety_warns = [f for f in result.findings if f.rule == "template-variety"]
        assert len(variety_warns) > 0

    def test_short_chapter_no_variety_required(self):
        """2-page chapters are exempt from variety rule."""
        rules = TemplateRules(default_template="full-bleed")
        book = plan_book(
            [ChapterSpec(title="Short", item_count=2)],
            template_rules=rules,
        )
        result = audit_book(book)
        variety_warns = [f for f in result.findings if f.rule == "template-variety"]
        assert variety_warns == []


# ── hero-density rule ─────────────────────────────────────────────────────────

class TestHeroDensity:
    def test_hero_caption_template_has_hero_slots(self):
        """hero+caption template has SlotRole.HERO — should satisfy density (no warn)."""
        rules = TemplateRules(default_template="hero+caption")
        book = plan_book(
            [ChapterSpec(title="C", item_count=8)],
            template_rules=rules,
        )
        result = audit_book(book)
        # Only warn/error findings matter — an INFO "density OK" is expected and fine
        hero_warns = [f for f in result.warnings + result.errors if f.rule == "hero-density"]
        assert len(hero_warns) == 0   # hero+caption has hero slots → no warning

    def test_info_emitted_when_density_ok(self):
        rules = TemplateRules(default_template="hero+caption")
        book = plan_book([ChapterSpec(title="C", item_count=4)], template_rules=rules)
        result = audit_book(book)
        hero_infos = [f for f in result.infos if f.rule == "hero-density"]
        assert len(hero_infos) == 1


# ── caption-coverage rule ─────────────────────────────────────────────────────

class TestCaptionCoverage:
    def test_hero_caption_provides_captions(self):
        """hero+caption template adds caption text blocks."""
        rules = TemplateRules(default_template="hero+caption")
        book = plan_book([ChapterSpec(title="C", item_count=4)], template_rules=rules)
        result = audit_book(book)
        cap_warns = [f for f in result.findings if f.rule == "caption-coverage"]
        assert cap_warns == []

    def test_no_text_blocks_triggers_warning(self):
        """A page with no text blocks at all → caption coverage low."""
        slot = ImageSlot(slot_id="s", aspect_ratio=1.5, role=SlotRole.HERO)
        slot.fill(0)
        # page with NO text blocks
        page = Page(page_number=1, template_name="custom", image_slots=[slot], text_blocks=[])
        chapter = Chapter(title="C", pages=[page])
        book = Book(title="T", book_format=BookFormat.PHOTO_BOOK, chapters=[chapter])
        result = audit_book(book)
        cap_warns = [f for f in result.findings if f.rule == "caption-coverage"]
        assert len(cap_warns) > 0


# ── chapter-arc rule ──────────────────────────────────────────────────────────

class TestChapterArc:
    def test_yearbook_chapter_with_hero_and_caption_passes(self):
        rules = TemplateRules(default_template="hero+caption")
        book = plan_book(
            [ChapterSpec(title="Instrument X", item_count=6)],
            book_format=BookFormat.YEARBOOK,
            template_rules=rules,
        )
        result = audit_book(book)
        arc_warns = [f for f in result.findings if f.rule == "chapter-arc"]
        assert arc_warns == []

    def test_design_chapter_without_hero_warns(self):
        """collage-tile slots are not hero/full-bleed — should trigger arc warning."""
        rules = TemplateRules(default_template="grid-2x2")   # collage-tile only
        book = plan_book(
            [ChapterSpec(title="Gallery", item_count=8)],
            book_format=BookFormat.DESIGN_CHAPTER,
            template_rules=rules,
        )
        result = audit_book(book)
        arc_warns = [f for f in result.findings if f.rule == "chapter-arc"]
        assert len(arc_warns) > 0

    def test_cover_chapter_exempt_from_arc(self):
        """Chapters with 'cover' in the title skip the arc rule."""
        rules = TemplateRules(default_template="full-bleed")
        book = plan_book(
            [ChapterSpec(title="Cover", item_count=1)],
            book_format=BookFormat.YEARBOOK,
            template_rules=rules,
        )
        result = audit_book(book)
        arc_warns = [f for f in result.findings if f.rule == "chapter-arc"]
        assert arc_warns == []

    def test_photo_book_format_skips_arc_rule(self):
        """chapter-arc only fires for yearbook / design-chapter."""
        rules = TemplateRules(default_template="grid-2x2")
        book = plan_book(
            [ChapterSpec(title="Gallery", item_count=8)],
            book_format=BookFormat.PHOTO_BOOK,
            template_rules=rules,
        )
        result = audit_book(book)
        arc_warns = [f for f in result.findings if f.rule == "chapter-arc"]
        assert arc_warns == []


# ── minimum-pages rule ────────────────────────────────────────────────────────

class TestMinimumPages:
    def test_single_page_chapter_warns(self):
        rules = TemplateRules(default_template="full-bleed")
        book = plan_book(
            [ChapterSpec(title="Intro", item_count=1)],
            template_rules=rules,
        )
        result = audit_book(book)
        min_warns = [f for f in result.findings if f.rule == "minimum-pages"]
        assert len(min_warns) > 0

    def test_cover_chapter_exempt(self):
        rules = TemplateRules(default_template="full-bleed")
        book = plan_book(
            [ChapterSpec(title="Cover Page", item_count=1)],
            template_rules=rules,
        )
        result = audit_book(book)
        min_warns = [f for f in result.findings if f.rule == "minimum-pages"]
        assert min_warns == []   # "cover" in title → exempt

    def test_index_chapter_exempt(self):
        rules = TemplateRules(default_template="full-bleed")
        book = plan_book(
            [ChapterSpec(title="Index", item_count=1)],
            template_rules=rules,
        )
        result = audit_book(book)
        min_warns = [f for f in result.findings if f.rule == "minimum-pages"]
        assert min_warns == []


# ── audit_chapter() ───────────────────────────────────────────────────────────

class TestAuditChapter:
    def test_returns_list_of_findings(self):
        rules = TemplateRules(default_template="hero+caption")
        ch = plan_chapter(ChapterSpec(title="C", item_count=6), rules=rules)
        findings = audit_chapter(ch)
        assert isinstance(findings, list)

    def test_chapter_audit_uses_design_chapter_format(self):
        """audit_chapter wraps in BookFormat.DESIGN_CHAPTER — arc rule should fire."""
        rules = TemplateRules(default_template="grid-2x2")
        ch = plan_chapter(ChapterSpec(title="NoHero", item_count=8), rules=rules)
        findings = audit_chapter(ch)
        # grid-2x2 has collage-tile only → chapter-arc warn expected
        arc_warns = [f for f in findings if f.rule == "chapter-arc"]
        assert len(arc_warns) > 0


# ── integration: yearbook audit ───────────────────────────────────────────────

class TestYearbookAudit:
    def test_well_formed_yearbook_audit(self):
        book = build_yearbook([
            InstrumentChapterSpec(
                repo_name="handpan", display_name="Handpan",
                gate_status=GateStatus.PASSED,
                content=InstrumentContentSpec(
                    cover_items=1, build_gallery_items=6,
                    experiment_lab_items=3, detail_shot_items=4,
                ),
            ),
        ], config=YearbookConfig(include_index=False))
        result = audit_book(book)
        # No structural errors (warnings for template variety / hero density ok)
        assert result.ok
