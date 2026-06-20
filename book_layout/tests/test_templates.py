"""
Tests for book_layout.templates — template registry, slot/text instantiation,
custom registration.

All tests are offline and deterministic.

Refs: claude-skills#210
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from book_layout.templates import (
    COLLAGE, FULL_BLEED, GRID_2X2, HERO_CAPTION, SPREAD,
    PageTemplate, get_template, list_templates, register_template,
)
from book_layout.schema import SlotRole, TextRole


BUILTIN_TEMPLATES = ["collage", "full-bleed", "grid-2x2", "hero+caption", "spread"]


# ── registry ──────────────────────────────────────────────────────────────────

class TestRegistry:
    def test_list_templates_contains_builtins(self):
        available = list_templates()
        for name in BUILTIN_TEMPLATES:
            assert name in available, f"Missing built-in template: {name}"

    def test_get_known_template(self):
        for name in BUILTIN_TEMPLATES:
            tmpl = get_template(name)
            assert tmpl.name == name

    def test_get_unknown_raises_key_error(self):
        with pytest.raises(KeyError, match="Unknown template"):
            get_template("does-not-exist")

    def test_register_custom(self):
        custom = PageTemplate(
            name="custom-test-xyzzy",
            slot_prototypes=[
                {"slot_id": "c-0", "aspect_ratio": 1.0, "role": SlotRole.ACCENT},
            ],
            text_prototypes=[],
        )
        register_template(custom)
        assert "custom-test-xyzzy" in list_templates()
        assert get_template("custom-test-xyzzy") is custom


# ── built-in template slot counts ────────────────────────────────────────────

class TestBuiltinSlotCounts:
    @pytest.mark.parametrize("name,expected_slots", [
        ("full-bleed", 1),
        ("grid-2x2", 4),
        ("hero+caption", 2),
        ("collage", 5),
        ("spread", 3),
    ])
    def test_slot_count(self, name, expected_slots):
        tmpl = get_template(name)
        assert tmpl.slot_count == expected_slots

    @pytest.mark.parametrize("name,expected_texts", [
        ("full-bleed", 1),
        ("grid-2x2", 1),
        ("hero+caption", 2),
        ("collage", 1),
        ("spread", 2),
    ])
    def test_text_block_count(self, name, expected_texts):
        tmpl = get_template(name)
        assert tmpl.text_block_count == expected_texts


# ── make_slots ────────────────────────────────────────────────────────────────

class TestMakeSlots:
    def test_slots_not_filled(self):
        """Fresh slots must always start unfilled."""
        for name in BUILTIN_TEMPLATES:
            slots = get_template(name).make_slots(page_index=1)
            for slot in slots:
                assert not slot.filled, f"{name}: slot {slot.slot_id} should be unfilled"

    def test_slot_ids_are_scoped_to_page(self):
        """Slot IDs must embed the page_index so pages don't share IDs."""
        tmpl = get_template("full-bleed")
        slots_p1 = tmpl.make_slots(page_index=1)
        slots_p2 = tmpl.make_slots(page_index=2)
        assert slots_p1[0].slot_id != slots_p2[0].slot_id
        assert "p1-" in slots_p1[0].slot_id
        assert "p2-" in slots_p2[0].slot_id

    def test_aspect_ratios_positive(self):
        for name in BUILTIN_TEMPLATES:
            for slot in get_template(name).make_slots():
                assert slot.aspect_ratio > 0

    def test_full_bleed_role(self):
        slots = FULL_BLEED.make_slots()
        assert slots[0].role == SlotRole.FULL_BLEED

    def test_grid_2x2_all_collage_tiles(self):
        slots = GRID_2X2.make_slots()
        assert all(s.role == SlotRole.COLLAGE_TILE for s in slots)

    def test_hero_caption_first_slot_is_hero(self):
        slots = HERO_CAPTION.make_slots()
        assert slots[0].role == SlotRole.HERO

    def test_collage_has_five_tiles(self):
        slots = COLLAGE.make_slots()
        assert len(slots) == 5
        assert all(s.role == SlotRole.COLLAGE_TILE for s in slots)

    def test_spread_first_slot_is_full_bleed(self):
        slots = SPREAD.make_slots()
        assert slots[0].role == SlotRole.FULL_BLEED
        assert all(s.role == SlotRole.SUPPORTING for s in slots[1:])

    def test_make_slots_returns_independent_instances(self):
        """Two make_slots() calls must return distinct objects (no shared state)."""
        tmpl = get_template("hero+caption")
        s1 = tmpl.make_slots(page_index=1)
        s2 = tmpl.make_slots(page_index=1)
        s1[0].fill(0)
        assert not s2[0].filled, "Slots from separate make_slots() calls must be independent"


# ── make_text_blocks ──────────────────────────────────────────────────────────

class TestMakeTextBlocks:
    def test_block_ids_scoped_to_page(self):
        tmpl = get_template("hero+caption")
        tb1 = tmpl.make_text_blocks(page_index=1)
        tb2 = tmpl.make_text_blocks(page_index=5)
        assert "p1-" in tb1[0].block_id
        assert "p5-" in tb2[0].block_id

    def test_hero_caption_has_caption_and_body(self):
        texts = HERO_CAPTION.make_text_blocks()
        roles = {tb.role for tb in texts}
        assert TextRole.CAPTION in roles
        assert TextRole.BODY in roles

    def test_collage_has_title(self):
        texts = COLLAGE.make_text_blocks()
        assert any(tb.role == TextRole.TITLE for tb in texts)

    def test_max_chars_positive(self):
        for name in BUILTIN_TEMPLATES:
            for tb in get_template(name).make_text_blocks():
                assert tb.max_chars > 0

    def test_text_blocks_content_is_none_on_creation(self):
        for name in BUILTIN_TEMPLATES:
            for tb in get_template(name).make_text_blocks():
                assert tb.content is None
