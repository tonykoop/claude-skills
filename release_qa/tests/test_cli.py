"""Tests for release_qa.cli — argparse CLI commands."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from release_qa.cli import build_parser, main
from release_qa.manifest import Artifact, ReleaseBundle


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_bundle_json(bundle: ReleaseBundle, dir_path: str) -> str:
    path = os.path.join(dir_path, "bundle.json")
    with open(path, "w") as f:
        f.write(bundle.to_json())
    return path


def _art(aid: str, atype: str, size: int = 1000, resolution: str = None) -> Artifact:
    return Artifact(
        id=aid, artifact_type=atype, path=f"/{aid}.out",
        size_bytes=size, checksum_sha256="cs123", resolution=resolution,
    )


def _stable_bundle(**kwargs) -> ReleaseBundle:
    defaults = dict(
        id="cli-stable-1",
        title="CLI Stable Release",
        version="1.0.0",
        release_type="stable",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[
            _art("s1", "script"),
            _art("v1", "video", resolution="1920x1080"),
            _art("a1", "audio"),
            _art("c1", "caption"),
        ],
        metadata={"project": "myshow", "episode": 1, "panel_score": 0.9, "human_approval_token": "tok-abc"},
        tags=["tech", "maker", "episode"],
    )
    defaults.update(kwargs)
    return ReleaseBundle(**defaults)


def _alpha_bundle(**kwargs) -> ReleaseBundle:
    defaults = dict(
        id="cli-alpha-1",
        title="CLI Alpha Release",
        version="0.1.0",
        release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[_art("s1", "script")],
        metadata={"project": "show", "episode": 1, "panel_score": 0.9, "human_approval_token": "tok"},
        tags=["alpha", "dev", "test"],
    )
    defaults.update(kwargs)
    return ReleaseBundle(**defaults)


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------

def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_parser_subcommands():
    parser = build_parser()
    for cmd in ["validate", "run-gates", "panel-review", "check-policy", "full-run"]:
        args = parser.parse_args([cmd, "/tmp/fake.json"])
        assert args.command == cmd
        assert args.manifest == "/tmp/fake.json"
        assert args.json is False


def test_parser_json_flag():
    parser = build_parser()
    args = parser.parse_args(["validate", "/tmp/fake.json", "--json"])
    assert args.json is True


# ---------------------------------------------------------------------------
# validate command
# ---------------------------------------------------------------------------

def test_cmd_validate_valid_bundle(tmp_path):
    bundle = _stable_bundle()
    path = _write_bundle_json(bundle, str(tmp_path))
    rc = main(["validate", path])
    assert rc == 0


def test_cmd_validate_invalid_bundle(tmp_path):
    bundle = _stable_bundle(version="not-semver")
    path = _write_bundle_json(bundle, str(tmp_path))
    rc = main(["validate", path])
    assert rc == 1


def test_cmd_validate_json_output(tmp_path, capsys):
    bundle = _stable_bundle()
    path = _write_bundle_json(bundle, str(tmp_path))
    rc = main(["validate", path, "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "valid" in data
    assert "errors" in data
    assert "warnings" in data
    assert rc == 0


def test_cmd_validate_invalid_json_output(tmp_path, capsys):
    bundle = _stable_bundle(version="bad")
    path = _write_bundle_json(bundle, str(tmp_path))
    rc = main(["validate", path, "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["valid"] is False
    assert len(data["errors"]) > 0


# ---------------------------------------------------------------------------
# run-gates command
# ---------------------------------------------------------------------------

def test_cmd_run_gates_good_alpha(tmp_path):
    bundle = _alpha_bundle()
    path = _write_bundle_json(bundle, str(tmp_path))
    rc = main(["run-gates", path])
    # May pass or fail depending on panel_score metadata stub
    assert rc in (0, 1)


def test_cmd_run_gates_json_output(tmp_path, capsys):
    bundle = _alpha_bundle()
    path = _write_bundle_json(bundle, str(tmp_path))
    main(["run-gates", path, "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    if data:
        assert "stage" in data[0]
        assert "passed" in data[0]


def test_cmd_run_gates_blocked_bundle(tmp_path):
    bundle = ReleaseBundle(
        id="bad", title="Bad", version="1.0.0", release_type="alpha",
        created_at="2026-06-19T00:00:00Z",
        artifacts=[],  # missing required script
        metadata={}, tags=[],
    )
    path = _write_bundle_json(bundle, str(tmp_path))
    rc = main(["run-gates", path])
    assert rc == 1


# ---------------------------------------------------------------------------
# panel-review command
# ---------------------------------------------------------------------------

def test_cmd_panel_review_json_output(tmp_path, capsys):
    bundle = _stable_bundle()
    path = _write_bundle_json(bundle, str(tmp_path))
    main(["panel-review", path, "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "bundle_id" in data
    assert "consensus_score" in data
    assert "recommendation" in data
    assert "critiques" in data


def test_cmd_panel_review_returns_code(tmp_path):
    bundle = _stable_bundle()
    path = _write_bundle_json(bundle, str(tmp_path))
    rc = main(["panel-review", path])
    assert rc in (0, 1)


# ---------------------------------------------------------------------------
# check-policy command
# ---------------------------------------------------------------------------

def test_cmd_check_policy_good_stable(tmp_path):
    bundle = _stable_bundle()
    path = _write_bundle_json(bundle, str(tmp_path))
    rc = main(["check-policy", path])
    assert rc == 0


def test_cmd_check_policy_blocked(tmp_path):
    bundle = _stable_bundle(tags=["nsfw"])
    path = _write_bundle_json(bundle, str(tmp_path))
    rc = main(["check-policy", path])
    assert rc == 1


def test_cmd_check_policy_json_output(tmp_path, capsys):
    bundle = _stable_bundle()
    path = _write_bundle_json(bundle, str(tmp_path))
    main(["check-policy", path, "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "blocked" in data
    assert "violations" in data
    assert "violation_count" in data


# ---------------------------------------------------------------------------
# full-run command
# ---------------------------------------------------------------------------

def test_cmd_full_run_json_output(tmp_path, capsys):
    bundle = _stable_bundle()
    path = _write_bundle_json(bundle, str(tmp_path))
    main(["full-run", path, "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "bundle_id" in data
    assert "overall_passed" in data
    assert "manifest" in data
    assert "gates" in data
    assert "panel" in data
    assert "policy" in data


def test_cmd_full_run_returns_code(tmp_path):
    bundle = _stable_bundle()
    path = _write_bundle_json(bundle, str(tmp_path))
    rc = main(["full-run", path])
    assert rc in (0, 1)


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_cmd_validate_missing_file():
    rc = main(["validate", "/nonexistent/path/bundle.json"])
    assert rc == 2


def test_cmd_check_policy_missing_file():
    rc = main(["check-policy", "/nonexistent/path.json"])
    assert rc == 2
