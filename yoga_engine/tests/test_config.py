"""Tests for yoga_engine.config — EngineConfig + PoseThesaurus (Story #374)."""

import json
import tempfile
from pathlib import Path

import pytest
from yoga_engine.config import (
    load_config, load_thesaurus,
    EngineConfig, AudioSyncConfig, ValidationConfig, ArcConfig,
    PoseThesaurus, ThesaurusEntry,
    get_config, get_thesaurus, reset_singletons,
)


# ---------------------------------------------------------------------------
# load_config — defaults
# ---------------------------------------------------------------------------


class TestLoadConfigDefaults:
    def test_returns_engine_config(self):
        cfg = load_config(Path("/nonexistent/config.toml"))
        assert isinstance(cfg, EngineConfig)

    def test_default_current_phase(self):
        cfg = load_config(Path("/nonexistent/config.toml"))
        assert cfg.current_phase == "warmup"

    def test_default_syntax_strictness(self):
        cfg = load_config(Path("/nonexistent/config.toml"))
        assert cfg.syntax_strictness == "strict"

    def test_default_lufs(self):
        cfg = load_config(Path("/nonexistent/config.toml"))
        assert cfg.audio_sync.lufs_target == -16.0

    def test_default_suppress_codes_empty(self):
        cfg = load_config(Path("/nonexistent/config.toml"))
        assert cfg.validation.suppress_codes == []

    def test_source_path_none_when_missing(self):
        cfg = load_config(Path("/nonexistent/config.toml"))
        assert cfg.source_path is None


# ---------------------------------------------------------------------------
# load_config — from bundled config.toml
# ---------------------------------------------------------------------------


class TestLoadBundledConfig:
    def test_bundled_config_loads(self):
        cfg = load_config()
        assert isinstance(cfg, EngineConfig)

    def test_bundled_current_phase(self):
        cfg = load_config()
        assert cfg.current_phase == "warmup"

    def test_bundled_strictness(self):
        cfg = load_config()
        assert cfg.syntax_strictness == "strict"

    def test_bundled_lufs_target(self):
        cfg = load_config()
        assert cfg.audio_sync.lufs_target == -16.0

    def test_bundled_source_path_set(self):
        cfg = load_config()
        assert cfg.source_path is not None

    def test_is_strict(self):
        cfg = load_config()
        assert cfg.is_strict()

    def test_is_not_debug(self):
        cfg = load_config()
        assert not cfg.is_debug()


# ---------------------------------------------------------------------------
# load_config — custom TOML
# ---------------------------------------------------------------------------


class TestLoadCustomConfig:
    def _write_toml(self, content: str) -> Path:
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False,
                                          mode="w") as fh:
            fh.write(content)
            return Path(fh.name)

    def test_custom_phase(self):
        path = self._write_toml('[engine]\ncurrent_phase = "peak"\n')
        cfg = load_config(path)
        assert cfg.current_phase == "peak"

    def test_custom_lufs(self):
        path = self._write_toml('[audio_sync]\nlufs_target = -14.0\n')
        cfg = load_config(path)
        assert cfg.audio_sync.lufs_target == -14.0

    def test_custom_lenient_strictness(self):
        path = self._write_toml('[engine]\nsyntax_strictness = "lenient"\n')
        cfg = load_config(path)
        assert not cfg.is_strict()

    def test_custom_debug_strictness(self):
        path = self._write_toml('[engine]\nsyntax_strictness = "debug"\n')
        cfg = load_config(path)
        assert cfg.is_strict()
        assert cfg.is_debug()

    def test_custom_suppress_codes(self):
        path = self._write_toml(
            '[validation]\nsuppress_codes = ["BILATERAL_MISSING_SIDE"]\n'
        )
        cfg = load_config(path)
        assert "BILATERAL_MISSING_SIDE" in cfg.validation.suppress_codes

    def test_custom_flat_stdev(self):
        path = self._write_toml('[arc]\nflat_stdev_threshold = 0.5\n')
        cfg = load_config(path)
        assert cfg.arc.flat_stdev_threshold == 0.5

    def test_crossfade_multipliers(self):
        path = self._write_toml(
            '[audio_sync]\n'
            'crossfade_slow_multiplier = 2.0\n'
            'crossfade_fast_multiplier = 0.25\n'
        )
        cfg = load_config(path)
        assert cfg.audio_sync.crossfade_slow_multiplier == 2.0
        assert cfg.audio_sync.crossfade_fast_multiplier == 0.25


# ---------------------------------------------------------------------------
# load_thesaurus — bundled JSON
# ---------------------------------------------------------------------------


class TestLoadBundledThesaurus:
    def test_returns_thesaurus(self):
        th = load_thesaurus()
        assert isinstance(th, PoseThesaurus)

    def test_non_empty(self):
        th = load_thesaurus()
        assert len(th) > 0

    def test_dd_token_present(self):
        th = load_thesaurus()
        entry = th.lookup("DD")
        assert entry is not None
        assert entry.name == "Downward Dog"

    def test_sv_savasana(self):
        th = load_thesaurus()
        entry = th.lookup("SV")
        assert entry is not None
        assert entry.name == "Savasana"

    def test_all_tokens_list(self):
        th = load_thesaurus()
        tokens = th.all_tokens()
        assert "DD" in tokens
        assert "CM" in tokens
        assert "SV" in tokens

    def test_repr(self):
        th = load_thesaurus()
        assert "PoseThesaurus" in repr(th)


# ---------------------------------------------------------------------------
# PoseThesaurus.resolve — alias lookup
# ---------------------------------------------------------------------------


class TestThesaurusResolve:
    def test_resolve_by_token(self):
        th = load_thesaurus()
        assert th.resolve("DD") == "DD"

    def test_resolve_by_name(self):
        th = load_thesaurus()
        assert th.resolve("Downward Dog") == "DD"

    def test_resolve_by_alias(self):
        th = load_thesaurus()
        assert th.resolve("down-dog") == "DD"

    def test_resolve_by_sanskrit(self):
        th = load_thesaurus()
        # Camel = Ustrasana
        token = th.resolve("Ustrasana")
        assert token == "CM"

    def test_resolve_case_insensitive(self):
        th = load_thesaurus()
        assert th.resolve("DOWNWARD DOG") == "DD"
        assert th.resolve("downward dog") == "DD"

    def test_resolve_unknown_returns_none(self):
        th = load_thesaurus()
        assert th.resolve("flying unicorn") is None

    def test_resolve_savasana_alias_corpse(self):
        th = load_thesaurus()
        assert th.resolve("corpse") == "SV"

    def test_resolve_wheel(self):
        th = load_thesaurus()
        assert th.resolve("wheel") == "UB"


# ---------------------------------------------------------------------------
# ThesaurusEntry fields
# ---------------------------------------------------------------------------


class TestThesaurusEntry:
    def test_entry_has_intensity(self):
        th = load_thesaurus()
        cm = th.lookup("CM")
        assert cm.intensity == 8

    def test_entry_has_family(self):
        th = load_thesaurus()
        dd = th.lookup("DD")
        assert dd.family == "transition"

    def test_entry_has_sanskrit(self):
        th = load_thesaurus()
        sv = th.lookup("SV")
        assert sv.sanskrit == "Savasana"

    def test_entry_aliases_list(self):
        th = load_thesaurus()
        dd = th.lookup("DD")
        assert isinstance(dd.aliases, list)
        assert len(dd.aliases) > 0


# ---------------------------------------------------------------------------
# Custom thesaurus path
# ---------------------------------------------------------------------------


class TestCustomThesaurus:
    def test_missing_path_returns_empty(self):
        th = load_thesaurus(Path("/nonexistent/thesaurus.json"))
        assert len(th) == 0

    def test_custom_json(self):
        data = {
            "poses": [
                {"token": "XX", "name": "Test Pose", "sanskrit": "",
                 "aliases": ["test"], "family": "test", "intensity": 5}
            ]
        }
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as fh:
            json.dump(data, fh)
            path = Path(fh.name)
        th = load_thesaurus(path)
        assert len(th) == 1
        assert th.lookup("XX") is not None
        assert th.resolve("test") == "XX"


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------


class TestSingletons:
    def test_get_config_returns_engine_config(self):
        reset_singletons()
        cfg = get_config()
        assert isinstance(cfg, EngineConfig)

    def test_get_config_cached(self):
        reset_singletons()
        cfg1 = get_config()
        cfg2 = get_config()
        assert cfg1 is cfg2  # same object

    def test_get_thesaurus_returns_thesaurus(self):
        reset_singletons()
        th = get_thesaurus()
        assert isinstance(th, PoseThesaurus)

    def test_get_thesaurus_cached(self):
        reset_singletons()
        th1 = get_thesaurus()
        th2 = get_thesaurus()
        assert th1 is th2

    def test_reset_clears_cache(self):
        get_config()
        get_thesaurus()
        reset_singletons()
        # After reset, should re-load (objects may be equal but not identical)
        cfg = get_config()
        assert isinstance(cfg, EngineConfig)
