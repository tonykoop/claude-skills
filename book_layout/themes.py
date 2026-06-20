"""
book_layout.themes
==================
Design-theme metadata for books and chapters.

A Theme carries typographic and colour-palette *hints* as plain strings — not
CSS, not hex codes embedded in rendered output.  The hints are advisory
metadata for downstream renderers (human editors, image-gen-2 art-direction
prompts, print templates).  This module never renders anything.

Built-in themes
---------------
yearbook-classic        High-school yearbook: strong serif headlines, grid
                        layouts, black-and-white with spot colour.
photo-album-warm        Family-/friends album: warm neutral palette, generous
                        white space, humanist sans-serif captions.
design-chapter-technical  Instrument design-book: technical mono annotation,
                        ruled grids, dimensioned-drawing aesthetic.
minimal-editorial       Publisher-grade minimal layout: tight type scale,
                        flush-left, restrained palette.

Custom themes can be registered with `register_theme()`.

Refs: claude-skills#210 (#93, #100)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ColourPalette:
    """Advisory colour palette (plain names / roles — no hex codes here)."""
    background: str = "white"
    primary_text: str = "near-black"
    accent: str = "black"
    secondary_accent: str = "mid-grey"
    highlight: str = "warm-gold"

    def describe(self) -> str:
        return (
            f"bg={self.background}, text={self.primary_text}, "
            f"accent={self.accent}, highlight={self.highlight}"
        )


@dataclass
class Typography:
    """Advisory typography scale (font-family hints, not CSS)."""
    headline_family: str = "serif"
    body_family: str = "sans-serif"
    caption_family: str = "sans-serif"
    headline_weight: str = "bold"
    body_weight: str = "regular"
    base_size_hint: str = "11pt"

    def describe(self) -> str:
        return (
            f"headline={self.headline_family}/{self.headline_weight}, "
            f"body={self.body_family}/{self.body_weight}, "
            f"base={self.base_size_hint}"
        )


@dataclass
class SpreadGrammar:
    """Rules for how a 2-page spread should be structured."""
    dominant_position: str = "left"          # where the dominant visual goes
    caption_position: str = "bottom-right"
    gutter_hint: str = "narrow"              # narrow / medium / wide
    bleed_edges: List[str] = field(default_factory=lambda: ["outer", "top"])
    notes: str = ""


@dataclass
class Theme:
    """Design theme: typography + palette + spread grammar + metadata."""
    name: str
    description: str
    palette: ColourPalette = field(default_factory=ColourPalette)
    typography: Typography = field(default_factory=Typography)
    spread_grammar: SpreadGrammar = field(default_factory=SpreadGrammar)
    art_direction_hints: List[str] = field(default_factory=list)
    compatible_formats: List[str] = field(
        default_factory=lambda: ["yearbook", "photo-book", "design-chapter"]
    )

    def summarise(self) -> str:
        """One-line summary for art-direction prompts."""
        hints = "; ".join(self.art_direction_hints[:3])
        return f"[{self.name}] {self.description} | {self.palette.describe()} | {hints}"


# ── global registry ───────────────────────────────────────────────────────────

_THEME_REGISTRY: Dict[str, Theme] = {}


def register_theme(theme: Theme) -> Theme:
    _THEME_REGISTRY[theme.name] = theme
    return theme


def get_theme(name: str) -> Theme:
    if name not in _THEME_REGISTRY:
        raise KeyError(
            f"Unknown theme '{name}'. Available: {sorted(_THEME_REGISTRY.keys())}"
        )
    return _THEME_REGISTRY[name]


def list_themes() -> List[str]:
    return sorted(_THEME_REGISTRY.keys())


def get_theme_for_format(book_format: str) -> Theme:
    """Return the most appropriate default theme for a book format."""
    mapping = {
        "yearbook": "yearbook-classic",
        "photo-book": "photo-album-warm",
        "design-chapter": "design-chapter-technical",
    }
    return get_theme(mapping.get(book_format, "minimal-editorial"))


# ── built-in themes ───────────────────────────────────────────────────────────

YEARBOOK_CLASSIC = register_theme(Theme(
    name="yearbook-classic",
    description="High-school yearbook aesthetic with strong spreads and editorial discipline.",
    palette=ColourPalette(
        background="white",
        primary_text="near-black",
        accent="school-red",
        secondary_accent="mid-grey",
        highlight="gold",
    ),
    typography=Typography(
        headline_family="condensed-serif",
        body_family="humanist-sans",
        caption_family="humanist-sans",
        headline_weight="bold",
        body_weight="regular",
        base_size_hint="10pt",
    ),
    spread_grammar=SpreadGrammar(
        dominant_position="left",
        caption_position="bottom-right",
        gutter_hint="narrow",
        bleed_edges=["outer", "top"],
        notes="Dominant visual bleeds to outer edge; caption anchors bottom-right of right page.",
    ),
    art_direction_hints=[
        "Strong dominant visual earns its full-bleed placement",
        "Captions carry measurement data and context, not description",
        "Build-story arc: overview → process → detail → result",
        "Consistent type scale across all chapters in the series",
        "Spot colour used sparingly — only for school identity",
    ],
    compatible_formats=["yearbook"],
))

PHOTO_ALBUM_WARM = register_theme(Theme(
    name="photo-album-warm",
    description="Family/friends photo album: warm, generous, emotionally resonant layout.",
    palette=ColourPalette(
        background="warm-white",
        primary_text="charcoal",
        accent="terra-cotta",
        secondary_accent="sage",
        highlight="warm-gold",
    ),
    typography=Typography(
        headline_family="humanist-serif",
        body_family="humanist-sans",
        caption_family="italic-serif",
        headline_weight="light",
        body_weight="regular",
        base_size_hint="11pt",
    ),
    spread_grammar=SpreadGrammar(
        dominant_position="right",
        caption_position="bottom-left",
        gutter_hint="wide",
        bleed_edges=["top"],
        notes="Generous white space; spreads breathe. Caption in italic serif for warmth.",
    ),
    art_direction_hints=[
        "Warm, golden-hour colour grading throughout",
        "People and moments over landscapes",
        "Generous margins — never cramped",
        "Chronological within each era; emotional arc within each spread",
        "Captions: names, places, years — short and personal",
        "Cover: one iconic image, large; title in light humanist serif",
    ],
    compatible_formats=["photo-book"],
))

DESIGN_CHAPTER_TECHNICAL = register_theme(Theme(
    name="design-chapter-technical",
    description="Instrument design-book: technical annotation, dimensioned-drawing aesthetic.",
    palette=ColourPalette(
        background="off-white",
        primary_text="near-black",
        accent="engineering-blue",
        secondary_accent="mid-grey",
        highlight="amber",
    ),
    typography=Typography(
        headline_family="geometric-sans",
        body_family="technical-sans",
        caption_family="monospace",
        headline_weight="medium",
        body_weight="regular",
        base_size_hint="9pt",
    ),
    spread_grammar=SpreadGrammar(
        dominant_position="left",
        caption_position="right-column",
        gutter_hint="medium",
        bleed_edges=[],
        notes=(
            "Dimensioned drawings bleed right; annotation column on right page. "
            "Captions carry measurement data. No bleed on technical pages — "
            "margins preserve drawing legibility."
        ),
    ),
    art_direction_hints=[
        "3D isometric views use consistent viewpoint (30° elevation, front-left)",
        "Dimensioned drawings show critical tolerances only — no annotation clutter",
        "Build-section: process photos show tooling and fixturing, not just finished parts",
        "Experiment-lab section uses Wolfram-style parameter sweeps as hero visual",
        "Caption format: measurement ± tolerance (measured, commit SHA or test date)",
        "Colour used only for engineering annotation — blue for dimensions, amber for warnings",
    ],
    compatible_formats=["design-chapter"],
))

MINIMAL_EDITORIAL = register_theme(Theme(
    name="minimal-editorial",
    description="Publisher-grade minimal layout: tight type scale, restrained palette.",
    palette=ColourPalette(
        background="white",
        primary_text="black",
        accent="black",
        secondary_accent="light-grey",
        highlight="none",
    ),
    typography=Typography(
        headline_family="transitional-serif",
        body_family="transitional-serif",
        caption_family="grotesque-sans",
        headline_weight="regular",
        body_weight="regular",
        base_size_hint="10pt",
    ),
    spread_grammar=SpreadGrammar(
        dominant_position="left",
        caption_position="below",
        gutter_hint="medium",
        bleed_edges=[],
        notes="No bleed; strict column grid; images sized to column width or half-column.",
    ),
    art_direction_hints=[
        "Typography does the work — images support, not dominate",
        "Flush-left text; no justification",
        "Image captions in small-caps grotesque, set below image",
    ],
    compatible_formats=["yearbook", "photo-book", "design-chapter"],
))
