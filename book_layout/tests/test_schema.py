"""
Tests for book_layout.schema — serialization, field validation, slot filling.

All tests are offline and deterministic.  No real images or identifiable-
person data.

Refs: claude-skills#210
"""
import json
import sys
from pathlib import Path

import pytest

# Ensure package is importable when running pytest from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from book_layout.schema import (
    Book, BookFormat, Chapter, ImageSlot, Page, PageSize,
    SlotRole, TextBlock, TextRole,
)


# ── ImageSlot ─────────────────────────────────────────────────────────────────

class TestImageSlot:
    def test_create_unfilled(self):
        slot = ImageSlot(slot_id="hero-0", aspect_ratio=1.5, role=SlotRole.HERO)
        assert slot.filled is False
        assert slot.content_ref is None

    def test_fill_sets_state(self):
        slot = ImageSlot(slot_id="hero-0", aspect_ratio=1.5, role=SlotRole.HERO)
        slot.fill(content_ref=42)
        assert slot.filled is True
        assert slot.content_ref == 42

    def test_clear_resets_state(self):
        slot = ImageSlot(slot_id="hero-0", aspect_ratio=1.5, role=SlotRole.HERO)
        slot.fill(content_ref=7)
        slot.clear()
        assert slot.filled is False
        assert slot.content_ref is None

    def test_fill_negative_ref_raises(self):
        slot = ImageSlot(slot_id="hero-0", aspect_ratio=1.5, role=SlotRole.HERO)
        with pytest.raises(ValueError, match="content_ref must be >= 0"):
            slot.fill(content_ref=-1)

    def test_aspect_ratio_must_be_positive(self):
        with pytest.raises(Exception):
            ImageSlot(slot_id="bad", aspect_ratio=0.0, role=SlotRole.HERO)

    def test_role_enum_variants_accepted(self):
        for role in SlotRole:
            slot = ImageSlot(slot_id=f"s-{role}", aspect_ratio=1.0, role=role)
            assert slot.role == role

    def test_serialization_round_trip(self):
        slot = ImageSlot(slot_id="sup-1", aspect_ratio=0.75, role=SlotRole.SUPPORTING)
        slot.fill(content_ref=3)
        data = slot.model_dump()
        restored = ImageSlot(**data)
        assert restored.slot_id == slot.slot_id
        assert restored.aspect_ratio == slot.aspect_ratio
        assert restored.filled is True
        assert restored.content_ref == 3

    def test_json_round_trip(self):
        slot = ImageSlot(slot_id="col-0", aspect_ratio=1.2, role=SlotRole.COLLAGE_TILE)
        json_str = slot.model_dump_json()
        data = json.loads(json_str)
        restored = ImageSlot(**data)
        assert restored == slot


# ── TextBlock ─────────────────────────────────────────────────────────────────

class TestTextBlock:
    def test_create_empty(self):
        tb = TextBlock(block_id="cap-0", role=TextRole.CAPTION)
        assert tb.content is None

    def test_content_within_limit_ok(self):
        tb = TextBlock(block_id="cap-0", role=TextRole.CAPTION, max_chars=50, content="short")
        assert tb.content == "short"

    def test_content_exceeds_limit_raises(self):
        with pytest.raises(Exception):
            TextBlock(
                block_id="cap-0", role=TextRole.CAPTION,
                max_chars=5, content="way too long content"
            )

    def test_all_text_roles_accepted(self):
        for role in TextRole:
            tb = TextBlock(block_id=f"b-{role}", role=role)
            assert tb.role == role

    def test_serialization_round_trip(self):
        tb = TextBlock(block_id="hl-0", role=TextRole.HEADLINE, max_chars=80, content="Hello")
        data = tb.model_dump()
        restored = TextBlock(**data)
        assert restored.block_id == "hl-0"
        assert restored.content == "Hello"


# ── Page ──────────────────────────────────────────────────────────────────────

class TestPage:
    def _make_page(self, n_slots: int = 2) -> Page:
        slots = [
            ImageSlot(slot_id=f"s-{i}", aspect_ratio=1.5, role=SlotRole.HERO)
            for i in range(n_slots)
        ]
        return Page(page_number=1, template_name="hero+caption", image_slots=slots)

    def test_slot_count(self):
        page = self._make_page(3)
        assert page.slot_count == 3

    def test_filled_slot_count(self):
        page = self._make_page(3)
        page.image_slots[0].fill(0)
        page.image_slots[2].fill(2)
        assert page.filled_slot_count == 2
        assert page.unfilled_slot_count == 1

    def test_page_number_must_be_positive(self):
        with pytest.raises(Exception):
            Page(page_number=0, template_name="full-bleed")

    def test_serialization_round_trip(self):
        page = self._make_page(2)
        page.image_slots[0].fill(0)
        data = page.model_dump()
        restored = Page(**data)
        assert restored.page_number == 1
        assert restored.image_slots[0].filled is True


# ── Chapter ───────────────────────────────────────────────────────────────────

class TestChapter:
    def _make_chapter(self, n_pages: int = 2) -> Chapter:
        pages = []
        for i in range(n_pages):
            slot = ImageSlot(slot_id=f"p{i}-s0", aspect_ratio=1.5, role=SlotRole.HERO)
            slot.fill(0)
            pages.append(Page(page_number=i + 1, template_name="full-bleed", image_slots=[slot]))
        return Chapter(title="Test Chapter", theme="test", pages=pages)

    def test_page_count(self):
        ch = self._make_chapter(3)
        assert ch.page_count == 3

    def test_total_and_filled_slots(self):
        ch = self._make_chapter(2)
        assert ch.total_slots == 2
        assert ch.filled_slots == 2
        assert ch.unfilled_slots == 0

    def test_serialization_round_trip(self):
        ch = self._make_chapter(2)
        data = ch.model_dump()
        restored = Chapter(**data)
        assert restored.title == "Test Chapter"
        assert restored.page_count == 2


# ── Book ──────────────────────────────────────────────────────────────────────

class TestBook:
    def _make_book(self) -> Book:
        slot = ImageSlot(slot_id="p1-s0", aspect_ratio=1.5, role=SlotRole.HERO)
        slot.fill(0)
        page = Page(page_number=1, template_name="full-bleed", image_slots=[slot])
        chapter = Chapter(title="Ch 1", pages=[page])
        return Book(
            title="My Book",
            book_format=BookFormat.PHOTO_BOOK,
            page_size=PageSize.LETTER,
            chapters=[chapter],
        )

    def test_total_pages(self):
        book = self._make_book()
        assert book.total_pages == 1

    def test_total_and_filled_slots(self):
        book = self._make_book()
        assert book.total_slots == 1
        assert book.filled_slots == 1

    def test_all_formats_accepted(self):
        for fmt in BookFormat:
            book = Book(title="T", book_format=fmt)
            assert book.book_format == fmt

    def test_all_page_sizes_accepted(self):
        for ps in PageSize:
            book = Book(title="T", book_format=BookFormat.YEARBOOK, page_size=ps)
            assert book.page_size == ps

    def test_full_json_round_trip(self):
        book = self._make_book()
        json_str = book.model_dump_json()
        data = json.loads(json_str)
        restored = Book(**data)
        assert restored.title == "My Book"
        assert restored.book_format == BookFormat.PHOTO_BOOK
        assert restored.total_pages == 1
        assert restored.chapters[0].pages[0].image_slots[0].filled is True

    def test_no_real_image_data_in_serialization(self):
        """Privacy check: serialized Book must not contain file paths or URLs."""
        book = self._make_book()
        json_str = book.model_dump_json()
        # These strings would indicate a real-image reference leaked in
        assert "/home" not in json_str
        assert "/tmp" not in json_str
        assert "http" not in json_str
        assert ".jpg" not in json_str
        assert ".png" not in json_str
