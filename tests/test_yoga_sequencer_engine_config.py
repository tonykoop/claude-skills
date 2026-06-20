#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "plugins" / "maker" / "skills" / "yoga-sequencer"
SCRIPT = SKILL_ROOT / "scripts" / "engine_config.py"


def load_module():
    spec = importlib.util.spec_from_file_location("yoga_engine_config", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["yoga_engine_config"] = module
    spec.loader.exec_module(module)
    return module


engine_config = load_module()


def write_config(directory: Path, *, strictness: str, lufs: float = -14.0) -> Path:
    path = directory / f"config-{strictness}-{str(lufs).replace('.', '_')}.toml"
    path.write_text(
        textwrap.dedent(
            f"""
            current_phase = "test"
            syntax_strictness = "{strictness}"

            [audio_sync]
            lufs_target = {lufs}
            default_crossfade_seconds = 6.5

            [engine]
            allow_unknown_tokens_in_draft = true
            """
        ).strip(),
        encoding="utf-8",
    )
    return path


class YogaEngineConfigTests(unittest.TestCase):
    def test_loads_default_config_and_thesaurus(self) -> None:
        engine = engine_config.YogaEngineConfig.load(SKILL_ROOT)
        self.assertEqual(engine.current_phase, "draft")
        self.assertEqual(engine.syntax_strictness, "starter")
        self.assertEqual(engine.resolve("DD").label, "Downward Facing Dog")
        self.assertIn("DD", engine.tokens)
        self.assertAlmostEqual(engine.lufs_target, -14.0)

    def test_macro_expands_to_pose_and_breath_operator_tokens(self) -> None:
        engine = engine_config.YogaEngineConfig.load(SKILL_ROOT)
        tokens = engine.parse_line("Viny // 5B")
        self.assertEqual([token.raw for token in tokens], ["PL", ">", "CH", "+", "UD", ">", "DD", "//", "5B"])
        self.assertEqual(tokens[0].label, "Plank")
        self.assertEqual(tokens[-1].kind, "operator")

    def test_five_line_shorthand_program_parses_without_ambiguity(self) -> None:
        engine = engine_config.YogaEngineConfig.load(SKILL_ROOT)
        program = [
            "Viny = PL>CH+UD>DD",
            "DD // 5B",
            "RLH_r > CL_r // 5B > PT_r",
            "RLH_l > CL_l // 5B > PT_l",
            "FF > HL + FF > Viny",
        ]

        parsed = engine.parse_program(program)
        self.assertEqual([line.kind for line in parsed], ["macro_definition", "sequence", "sequence", "sequence", "sequence"])
        self.assertEqual(parsed[0].macro_name, "Viny")
        self.assertEqual([token.raw for token in parsed[-1].tokens], ["FF", ">", "HL", "+", "FF", ">", "PL", ">", "CH", "+", "UD", ">", "DD"])
        self.assertEqual({token.modifier for line in parsed for token in line.tokens if token.modifier}, {"_r", "_l"})
        self.assertFalse(any(token.draft for line in parsed for token in line.tokens))

    def test_tokenizer_rejects_unparsed_characters(self) -> None:
        engine = engine_config.YogaEngineConfig.load(SKILL_ROOT)
        with self.assertRaises(engine_config.ConfigError):
            engine.tokenize("DD @ CL")

    def test_protocol_reference_documents_starter_vocabulary_and_sample(self) -> None:
        doc = (SKILL_ROOT / "references" / "shorthand-protocol.md").read_text(encoding="utf-8")
        for token in ("DD", "HL", "FF", "RLH", "CL", "PT"):
            self.assertIn(f"`{token}`", doc)
        self.assertIn("Viny = PL>CH+UD>DD", doc)
        self.assertIn("Five-Line Starter Class", doc)

    def test_strictness_controls_unknown_token_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            draft_config = write_config(Path(tmp), strictness="draft")
            strict_config = write_config(Path(tmp), strictness="strict")

            draft = engine_config.YogaEngineConfig.load(SKILL_ROOT, config_path=draft_config)
            resolved = draft.resolve("NEW_r")
            self.assertTrue(resolved.draft)
            self.assertEqual(resolved.modifier, "_r")

            strict = engine_config.YogaEngineConfig.load(SKILL_ROOT, config_path=strict_config)
            with self.assertRaises(engine_config.UnknownPoseToken):
                strict.resolve("NEW_r")

    def test_audio_lufs_target_is_runtime_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = write_config(Path(tmp), strictness="starter", lufs=-16.5)
            engine = engine_config.YogaEngineConfig.load(SKILL_ROOT, config_path=config_path)
            self.assertEqual(
                engine.audio_sync_settings(),
                {"lufs_target": -16.5, "default_crossfade_seconds": 6.5},
            )


if __name__ == "__main__":
    unittest.main()
