"""
Tests for book_layout.export — manifest generation, serialization round-trips,
physical page dimensions.

All tests offline and deterministic.  No real images.

Refs: claude-skills#210
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from book_layout.planner import ChapterSpec, TemplateRules, plan_book
from book_layout.schema import BookFormat, PageSize
from book_layout.export import (
    BookManifest, PageSizeConfig, SlotManifest,
    export_book, from_json, get_page_size_config, manifest_to_dict,
    manifest_to_json, to_json, PAGE_SIZE_CONFIGS,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_book(item_counts=(4, 8)):
    rules = TemplateRules(default_template="grid-2x2")
    specs = [ChapterSpec(title=f"Ch{i+1}", item_count=n)
             for i, n in enumerate(item_counts)]
    return plan_book(specs, book_title="Test Book",
                     book_format=BookFormat.PHOTO_BOOK, template_rules=rules)


# ── PageSizeConfig ────────────────────────────────────────────────────────────

class TestPageSizeConfig:
    def test_all_page_sizes_have_configs(self):
        for ps in PageSize:
            cfg = get_page_size_config(ps)
            assert isinstance(cfg, PageSizeConfig)
            assert cfg.width_mm > 0
            assert cfg.height_mm > 0

    def test_printable_area_smaller_than_page(self):
        cfg = get_page_size_config(PageSize.LETTER)
        assert cfg.printable_width_mm < cfg.width_mm
        assert cfg.printable_height_mm < cfg.height_mm

    def test_total_area_includes_bleed(self):
        cfg = PageSizeConfig(width_mm=210.0, height_mm=297.0, bleed_mm=3.0)
        assert cfg.total_width_mm == pytest.approx(216.0)
        assert cfg.total_height_mm == pytest.approx(303.0)

    def test_spread_is_twice_letter_width(self):
        letter = get_page_size_config(PageSize.LETTER)
        spread = get_page_size_config(PageSize.SPREAD)
        assert spread.width_mm == pytest.approx(letter.width_mm * 2)

    def test_custom_page_size_config(self):
        custom = PageSizeConfig(width_mm=150.0, height_mm=200.0, bleed_mm=5.0, margin_mm=15.0)
        assert custom.printable_width_mm == pytest.approx(120.0)
        assert custom.printable_height_mm == pytest.approx(170.0)


# ── export_book() ─────────────────────────────────────────────────────────────

class TestExportBook:
    def test_manifest_title_matches(self):
        book = _make_book()
        m = export_book(book)
        assert m.title == "Test Book"

    def test_manifest_format_matches(self):
        book = _make_book()
        m = export_book(book)
        assert m.book_format == "photo-book"

    def test_total_pages_correct(self):
        book = _make_book((4, 8))
        m = export_book(book)
        assert m.total_pages == book.total_pages

    def test_total_slots_correct(self):
        book = _make_book((4,))
        m = export_book(book)
        assert m.total_slots == book.total_slots

    def test_filled_slots_correct(self):
        book = _make_book((4,))
        m = export_book(book)
        assert m.filled_slots == book.filled_slots

    def test_chapter_count_correct(self):
        book = _make_book((4, 8))
        m = export_book(book)
        assert m.chapter_count == 2

    def test_page_manifests_count(self):
        book = _make_book((4, 8))
        m = export_book(book)
        assert len(m.page_manifests) == book.total_pages

    def test_all_slots_denormalised(self):
        book = _make_book((4, 8))
        m = export_book(book)
        assert len(m.all_slots) == book.total_slots

    def test_slot_manifests_have_geometry(self):
        book = _make_book((4,))
        m = export_book(book)
        for sm in m.all_slots:
            assert sm.approx_width_mm > 0
            assert sm.approx_height_mm > 0

    def test_slot_manifests_have_chapter_title(self):
        book = _make_book((4,))
        m = export_book(book)
        for sm in m.all_slots:
            assert sm.chapter_title != ""

    def test_fill_rate_calculation(self):
        book = _make_book((4,))   # 4 items / 4 slots = 100% fill
        m = export_book(book)
        assert m.fill_rate == pytest.approx(1.0)

    def test_underfull_fill_rate(self):
        # 5 items / 4-slot template = 5 filled, 3 unfilled (page 2 has 1 item, 3 slots)
        book = _make_book((5,))
        m = export_book(book)
        assert 0.0 < m.fill_rate < 1.0

    def test_unfilled_slots_property(self):
        book = _make_book((5,))
        m = export_book(book)
        assert m.unfilled_slots == m.total_slots - m.filled_slots

    def test_theme_defaults_to_format_match(self):
        book = _make_book()
        m = export_book(book)
        assert m.theme_name == "photo-album-warm"   # photo-book default

    def test_custom_page_size_config(self):
        book = _make_book()
        custom_cfg = PageSizeConfig(width_mm=200.0, height_mm=200.0)
        m = export_book(book, page_size_config=custom_cfg)
        # All slot approx widths should fit within printable area
        pw = custom_cfg.printable_width_mm
        for sm in m.all_slots:
            assert sm.approx_width_mm <= pw + 0.1   # small rounding allowed

    def test_page_manifest_fields(self):
        book = _make_book((4,))
        m = export_book(book)
        pm = m.page_manifests[0]
        assert pm.page_number == 1
        assert pm.slot_count > 0
        assert pm.template_name != ""

    def test_no_real_image_paths_in_manifest(self):
        book = _make_book((4,))
        m = export_book(book)
        mj = manifest_to_json(m)
        for forbidden in ["/home", "/tmp", "http://", ".jpg", ".png"]:
            assert forbidden not in mj


# ── JSON round-trip ───────────────────────────────────────────────────────────

class TestJsonRoundTrip:
    def test_to_json_produces_valid_json(self):
        book = _make_book()
        j = to_json(book)
        data = json.loads(j)
        assert data["title"] == "Test Book"

    def test_from_json_round_trip(self):
        book = _make_book((4, 8))
        j = to_json(book)
        restored = from_json(j)
        assert restored.title == book.title
        assert restored.total_pages == book.total_pages
        assert restored.total_slots == book.total_slots
        assert restored.filled_slots == book.filled_slots

    def test_from_json_preserves_chapter_structure(self):
        book = _make_book((4, 8))
        restored = from_json(to_json(book))
        assert len(restored.chapters) == 2
        assert restored.chapters[0].title == "Ch1"
        assert restored.chapters[1].title == "Ch2"

    def test_from_json_preserves_slot_fill_state(self):
        book = _make_book((4,))
        restored = from_json(to_json(book))
        for chapter in restored.chapters:
            for page in chapter.pages:
                for slot in page.image_slots:
                    if slot.content_ref is not None:
                        assert slot.filled is True

    def test_manifest_to_json_valid(self):
        book = _make_book()
        m = export_book(book)
        mj = manifest_to_json(m)
        data = json.loads(mj)
        assert data["title"] == "Test Book"
        assert "page_manifests" in data
        assert "all_slots" in data

    def test_manifest_to_dict(self):
        book = _make_book()
        m = export_book(book)
        d = manifest_to_dict(m)
        assert isinstance(d, dict)
        assert d["total_pages"] == book.total_pages
