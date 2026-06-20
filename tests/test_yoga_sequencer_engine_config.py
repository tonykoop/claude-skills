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
