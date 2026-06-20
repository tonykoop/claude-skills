#!/usr/bin/env python3
"""Load yoga-sequencer shorthand engine config and pose thesaurus data."""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"//|[+>]|[A-Za-z][A-Za-z0-9]*(?:_(?:r|l|f|b|open|cl))?|[0-9]+B")
MODIFIER_RE = re.compile(r"^(?P<base>[A-Za-z][A-Za-z0-9]*)(?P<modifier>_(?:r|l|f|b|open|cl))?$")
BREATH_RE = re.compile(r"^[1-9][0-9]*B$")
VALID_STRICTNESS = {"draft", "starter", "strict"}


class ConfigError(ValueError):
    """Raised when the public engine config cannot be trusted."""


class UnknownPoseToken(ValueError):
    """Raised when strict parsing sees a token outside the thesaurus."""


@dataclass(frozen=True)
class ResolvedToken:
    raw: str
    kind: str
    base: str
    label: str
    modifier: str | None = None
    draft: bool = False


class YogaEngineConfig:
    def __init__(self, *, config: dict[str, Any], thesaurus: dict[str, Any]):
        self.config = config
        self.thesaurus = thesaurus
        strictness = self.syntax_strictness
        if strictness not in VALID_STRICTNESS:
            raise ConfigError(
                f"syntax_strictness must be one of {sorted(VALID_STRICTNESS)}, got {strictness!r}"
            )

    @classmethod
    def load(
        cls,
        skill_root: Path | None = None,
        *,
        config_path: Path | None = None,
        thesaurus_path: Path | None = None,
    ) -> "YogaEngineConfig":
        root = skill_root or Path(__file__).resolve().parents[1]
        config_file = config_path or root / "config.toml"
        thesaurus_file = thesaurus_path or root / "references" / "pose_thesaurus.json"

        with config_file.open("rb") as handle:
            config = tomllib.load(handle)
        with thesaurus_file.open("r", encoding="utf-8") as handle:
            thesaurus = json.load(handle)
        return cls(config=config, thesaurus=thesaurus)

    @property
    def current_phase(self) -> str:
        return str(self.config.get("current_phase", "draft"))

    @property
    def syntax_strictness(self) -> str:
        return str(self.config.get("syntax_strictness", "starter"))

    @property
    def lufs_target(self) -> float:
        audio = self.config.get("audio_sync", {})
        return float(audio.get("lufs_target", -14.0))

    @property
    def tokens(self) -> dict[str, dict[str, Any]]:
        return self.thesaurus.get("tokens", {})

    @property
    def operators(self) -> dict[str, str]:
        return self.thesaurus.get("operators", {})

    @property
    def modifiers(self) -> dict[str, str]:
        return self.thesaurus.get("modifiers", {})

    @property
    def macros(self) -> dict[str, dict[str, Any]]:
        return self.thesaurus.get("macros", {})

    def expand_macro(self, name: str) -> list[str]:
        macro = self.macros.get(name)
        if not macro:
            raise UnknownPoseToken(f"unknown macro {name!r}")
        expansion = macro.get("expands_to", [])
        if not isinstance(expansion, list) or not all(isinstance(item, str) for item in expansion):
            raise ConfigError(f"macro {name!r} must define expands_to as a list of strings")
        return expansion

    def tokenize(self, shorthand: str) -> list[str]:
        return TOKEN_RE.findall(shorthand)

    def resolve(self, raw: str) -> ResolvedToken:
        if raw in self.operators or BREATH_RE.match(raw):
            return ResolvedToken(raw=raw, kind="operator", base=raw, label=self.operators.get(raw, raw))
        if raw in self.macros:
            return ResolvedToken(raw=raw, kind="macro", base=raw, label=raw)

        match = MODIFIER_RE.match(raw)
        if not match:
            raise ConfigError(f"cannot parse shorthand token {raw!r}")
        base = match.group("base")
        modifier = match.group("modifier")
        pose = self.tokens.get(base)
        if pose:
            label = str(pose.get("canonical_name", base))
            return ResolvedToken(raw=raw, kind="pose", base=base, label=label, modifier=modifier)

        allow_draft = (
            self.syntax_strictness == "draft"
            and bool(self.config.get("engine", {}).get("allow_unknown_tokens_in_draft", True))
        )
        if allow_draft:
            return ResolvedToken(raw=raw, kind="pose", base=base, label=base, modifier=modifier, draft=True)
        raise UnknownPoseToken(
            f"unknown pose token {base!r}; add it to references/pose_thesaurus.json or use draft strictness"
        )

    def parse_line(self, shorthand: str) -> list[ResolvedToken]:
        resolved: list[ResolvedToken] = []
        for raw in self.tokenize(shorthand):
            token = self.resolve(raw)
            if token.kind == "macro":
                resolved.extend(self.resolve(part) for part in self.expand_macro(token.base))
            else:
                resolved.append(token)
        return resolved

    def audio_sync_settings(self) -> dict[str, float]:
        audio = self.config.get("audio_sync", {})
        return {
            "lufs_target": self.lufs_target,
            "default_crossfade_seconds": float(audio.get("default_crossfade_seconds", 8.0)),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect yoga-sequencer shorthand engine config.")
    parser.add_argument("line", nargs="?", help="Optional shorthand line to parse.")
    parser.add_argument("--skill-root", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a human summary.")
    args = parser.parse_args(argv)

    engine = YogaEngineConfig.load(args.skill_root)
    payload: dict[str, Any] = {
        "current_phase": engine.current_phase,
        "syntax_strictness": engine.syntax_strictness,
        "audio_sync": engine.audio_sync_settings(),
    }
    if args.line:
        payload["tokens"] = [token.__dict__ for token in engine.parse_line(args.line)]

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"phase={payload['current_phase']} strictness={payload['syntax_strictness']}")
        print(f"audio_sync={payload['audio_sync']}")
        if args.line:
            for token in payload["tokens"]:
                print(f"{token['raw']}: {token['kind']} -> {token['label']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
