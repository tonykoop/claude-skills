"""
book_layout.templates
=====================
Reusable page-template definitions and a global registry.

Each template specifies prototype slot and text-block descriptors.
When the planner builds a Page it calls `template.make_slots(page_index)` and
`template.make_text_blocks(page_index)` to get fresh, page-scoped instances.

Built-in templates
------------------
full-bleed      1 full-bleed slot  + 1 caption block
grid-2x2        4 square slots     + 1 headline block
hero+caption    2 slots (hero + supporting) + 1 caption + 1 body block
collage         5 mixed-ratio slots + 1 title block
spread          3 slots (1 hero full-bleed + 2 supporting) + 1 headline + 1 caption

Custom templates can be registered with `register_template()`.

Refs: claude-skills#210
"""
from __future__ import annotations

from typing import Any, Dict, List

from .schema import ImageSlot, TextBlock, SlotRole, TextRole


# ── template class ────────────────────────────────────────────────────────────

class PageTemplate:
    """Prototype definition for a page layout.

    Slot and text-block prototypes are plain dicts; instances are created
    fresh for each page so the planner never shares mutable state.
    """

    def __init__(
        self,
        name: str,
        slot_prototypes: List[Dict[str, Any]],
        text_prototypes: List[Dict[str, Any]],
    ) -> None:
        self.name = name
        self._slot_protos = slot_prototypes
        self._text_protos = text_prototypes

    @property
    def slot_count(self) -> int:
        return len(self._slot_protos)

    @property
    def text_block_count(self) -> int:
        return len(self._text_protos)

    def make_slots(self, page_index: int = 0) -> List[ImageSlot]:
        """Return fresh ImageSlot instances scoped to `page_index`."""
        return [
            ImageSlot(
                slot_id=f"p{page_index}-{proto['slot_id']}",
                aspect_ratio=proto["aspect_ratio"],
                role=SlotRole(proto["role"]) if isinstance(proto["role"], str) else proto["role"],
            )
            for proto in self._slot_protos
        ]

    def make_text_blocks(self, page_index: int = 0) -> List[TextBlock]:
        """Return fresh TextBlock instances scoped to `page_index`."""
        return [
            TextBlock(
                block_id=f"p{page_index}-{proto['block_id']}",
                role=TextRole(proto["role"]) if isinstance(proto["role"], str) else proto["role"],
                max_chars=proto.get("max_chars", 500),
            )
            for proto in self._text_protos
        ]

    def __repr__(self) -> str:
        return (
            f"PageTemplate(name={self.name!r}, "
            f"slots={self.slot_count}, text_blocks={self.text_block_count})"
        )


# ── global registry ───────────────────────────────────────────────────────────

_REGISTRY: Dict[str, PageTemplate] = {}


def register_template(template: PageTemplate) -> PageTemplate:
    """Register a PageTemplate in the global registry and return it."""
    _REGISTRY[template.name] = template
    return template


def get_template(name: str) -> PageTemplate:
    """Look up a template by name; raises KeyError if not found."""
    if name not in _REGISTRY:
        raise KeyError(
            f"Unknown template '{name}'. "
            f"Available: {sorted(_REGISTRY.keys())}"
        )
    return _REGISTRY[name]


def list_templates() -> List[str]:
    """Return sorted list of all registered template names."""
    return sorted(_REGISTRY.keys())


# ── built-in template definitions ────────────────────────────────────────────

FULL_BLEED = register_template(PageTemplate(
    name="full-bleed",
    slot_prototypes=[
        {
            "slot_id": "fb-0",
            "aspect_ratio": 1.333,   # 4:3 landscape
            "role": SlotRole.FULL_BLEED,
        },
    ],
    text_prototypes=[
        {"block_id": "cap-0", "role": TextRole.CAPTION, "max_chars": 200},
    ],
))

GRID_2X2 = register_template(PageTemplate(
    name="grid-2x2",
    slot_prototypes=[
        {"slot_id": "g-0", "aspect_ratio": 1.0, "role": SlotRole.COLLAGE_TILE},
        {"slot_id": "g-1", "aspect_ratio": 1.0, "role": SlotRole.COLLAGE_TILE},
        {"slot_id": "g-2", "aspect_ratio": 1.0, "role": SlotRole.COLLAGE_TILE},
        {"slot_id": "g-3", "aspect_ratio": 1.0, "role": SlotRole.COLLAGE_TILE},
    ],
    text_prototypes=[
        {"block_id": "hl-0", "role": TextRole.HEADLINE, "max_chars": 80},
    ],
))

HERO_CAPTION = register_template(PageTemplate(
    name="hero+caption",
    slot_prototypes=[
        {"slot_id": "hero-0", "aspect_ratio": 1.5,  "role": SlotRole.HERO},
        {"slot_id": "sup-0",  "aspect_ratio": 1.0,  "role": SlotRole.SUPPORTING},
    ],
    text_prototypes=[
        {"block_id": "cap-0",  "role": TextRole.CAPTION, "max_chars": 300},
        {"block_id": "body-0", "role": TextRole.BODY,    "max_chars": 800},
    ],
))

COLLAGE = register_template(PageTemplate(
    name="collage",
    slot_prototypes=[
        {"slot_id": "col-0", "aspect_ratio": 1.2,  "role": SlotRole.COLLAGE_TILE},
        {"slot_id": "col-1", "aspect_ratio": 0.8,  "role": SlotRole.COLLAGE_TILE},
        {"slot_id": "col-2", "aspect_ratio": 1.0,  "role": SlotRole.COLLAGE_TILE},
        {"slot_id": "col-3", "aspect_ratio": 1.5,  "role": SlotRole.COLLAGE_TILE},
        {"slot_id": "col-4", "aspect_ratio": 0.75, "role": SlotRole.COLLAGE_TILE},
    ],
    text_prototypes=[
        {"block_id": "title-0", "role": TextRole.TITLE, "max_chars": 120},
    ],
))

SPREAD = register_template(PageTemplate(
    name="spread",
    slot_prototypes=[
        {"slot_id": "spread-hero",  "aspect_ratio": 2.0,   "role": SlotRole.FULL_BLEED},
        {"slot_id": "spread-sup-0", "aspect_ratio": 1.333, "role": SlotRole.SUPPORTING},
        {"slot_id": "spread-sup-1", "aspect_ratio": 1.333, "role": SlotRole.SUPPORTING},
    ],
    text_prototypes=[
        {"block_id": "hl-0",  "role": TextRole.HEADLINE, "max_chars": 100},
        {"block_id": "cap-0", "role": TextRole.CAPTION,  "max_chars": 300},
    ],
))
