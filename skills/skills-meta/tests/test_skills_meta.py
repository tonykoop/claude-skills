#!/usr/bin/env python3
"""Focused tests for review feedback on skills-meta.

Covers:
  1. `--mode single` is deterministic in duplicate-heavy installs and shows
     a multi-copy summary instead of silently picking records[0].
  2. `--mode sync` refuses to mutate a symlinked target without --force,
     and with --force unlinks the symlink (never rmtree through it) before
     laying down a fresh copy.
  3. Source directories that contain internal symlinks have their layout
     preserved through sync (no flattening).
  4. `fix-duplicates` unlinks symlink duplicates instead of rmtree'ing
     into whatever the link points at.

Run from anywhere:

    python skills/skills-meta/tests/test_skills_meta.py
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "skills-meta.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("skills_meta", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    # Register before exec so dataclass(cls) can resolve cls.__module__ —
    # Python 3.12 reads sys.modules during dataclass processing.
    sys.modules["skills_meta"] = module
    spec.loader.exec_module(module)
    return module


sm = _load_module()


def write_skill(path: Path, name: str, version: str | None, last_updated: str | None) -> None:
    path.mkdir(parents=True, exist_ok=True)
    fm_lines = ["---", f"name: {name}"]
    if version is not None:
        fm_lines.append(f"version: {version}")
    if last_updated is not None:
        fm_lines.append(f"last-updated: {last_updated}")
    fm_lines.append("description: fixture")
    fm_lines.append("---")
    body = "\n".join(fm_lines) + "\n\nbody\n"
    (path / "SKILL.md").write_text(body, encoding="utf-8")


def write_manifest(repo_root: Path, skills: dict[str, dict]) -> None:
    """Tiny manifest writer; YAML-compatible enough for safe_load."""
    lines = ["schema_version: 1", "skills:"]
    for name, entry in skills.items():
        lines.append(f"  {name}:")
        for key, value in entry.items():
            lines.append(f"    {key}: {value}")
    (repo_root / "manifest.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


class SingleModeDeterminismTests(unittest.TestCase):
    """A skill name appearing at four roots must produce stable output and
    surface every copy — silent records[0] picking was the review's
    complaint, so we exercise the actual rendered text."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="skills-meta-single-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

        self.repo = self.tmp / "repo"
        (self.repo / "skills").mkdir(parents=True)
        write_manifest(
            self.repo,
            {
                "duped": {
                    "canonical_version": "1.0.0",
                    "runtime": "shared",
                    "repo_path": "skills/duped",
                    "last_updated": "2026-05-01",
                    "status": "active",
                }
            },
        )
        # Four copies in declaration order that should be different from the
        # canonicalness ordering — repo path is canonical, then by version.
        write_skill(self.repo / "skills" / "duped", "duped", "1.0.0", "2026-05-01")
        # Other roots: an "old" Codex install (lower version), a "new" Claude
        # install (higher version), a Gemini install with no version.
        write_skill(self.tmp / "codex" / "duped", "duped", "0.9.0", "2026-04-01")
        write_skill(self.tmp / "claude" / "duped", "duped", "1.1.0", "2026-04-15")
        write_skill(self.tmp / "gemini" / "duped", "duped", None, None)

    def _run_single(self) -> str:
        os.chdir(self.repo)
        argv = [
            "skills-meta.py",
            "--mode",
            "single",
            "--skill",
            "duped",
            "--root",
            str(self.tmp / "codex"),
            "--root",
            str(self.tmp / "claude"),
            "--root",
            str(self.tmp / "gemini"),
        ]
        old_argv, sys.argv = sys.argv, argv
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                rc = sm.main()
        finally:
            sys.argv = old_argv
        self.assertEqual(rc, 0, msg=buf.getvalue())
        return buf.getvalue()

    def test_repo_path_wins_and_output_is_deterministic(self) -> None:
        first = self._run_single()
        second = self._run_single()
        self.assertEqual(
            first,
            second,
            msg="single-mode output drifted between runs; must be deterministic",
        )
        # The repo_path entry must win even though another copy has a higher
        # semver — manifest authority beats version.
        self.assertIn(
            f"path: {self.repo / 'skills' / 'duped' / 'SKILL.md'}",
            first,
            msg=first,
        )

    def test_other_copies_block_lists_all_remaining(self) -> None:
        out = self._run_single()
        self.assertIn("other copies: 3", out, msg=out)
        for path in (
            self.tmp / "codex" / "duped" / "SKILL.md",
            self.tmp / "claude" / "duped" / "SKILL.md",
            self.tmp / "gemini" / "duped" / "SKILL.md",
        ):
            self.assertIn(str(path), out, msg=out)


class SyncRuntimeDriftReportingTests(unittest.TestCase):
    """Sync drift reports should make cross-runtime direction obvious. A
    Claude-owned source copied into a Codex install is otherwise easy to
    misread as ordinary local path drift."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="skills-meta-runtime-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "repo"
        write_skill(self.repo / "claude" / "skills" / "merge-review", "merge-review", "1.0.0", "2026-05-01")
        write_manifest(
            self.repo,
            {
                "merge-review": {
                    "canonical_version": "1.0.0",
                    "runtime": "claude",
                    "repo_path": "claude/skills/merge-review",
                    "last_updated": "2026-05-01",
                    "status": "active",
                }
            },
        )
        self.target_root = self.tmp / ".codex" / "skills"
        write_skill(self.target_root / "merge-review", "merge-review", "0.9.0", "2026-04-01")

    def _run_sync(self, *extra: str) -> tuple[int, str]:
        os.chdir(self.repo)
        argv = [
            "skills-meta.py",
            "--mode",
            "sync",
            "--target",
            str(self.target_root),
            "--skill",
            "merge-review",
            *extra,
        ]
        old_argv, sys.argv = sys.argv, argv
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                rc = sm.main()
        finally:
            sys.argv = old_argv
        return rc, buf.getvalue()

    def test_text_sync_plan_shows_claude_to_codex_drift(self) -> None:
        rc, out = self._run_sync()
        self.assertEqual(rc, 0, msg=out)
        self.assertIn("! drift", out, msg=out)
        self.assertIn("merge-review", out, msg=out)
        self.assertIn("[claude -> codex]", out, msg=out)
        self.assertIn("target has local changes", out, msg=out)
        self.assertIn("Drifted targets need --apply --force", out, msg=out)

    def test_json_sync_plan_includes_runtime_labels(self) -> None:
        rc, out = self._run_sync("--json")
        self.assertEqual(rc, 0, msg=out)
        plan = json.loads(out)["plan"]
        self.assertEqual(len(plan), 1, msg=out)
        self.assertEqual(plan[0]["state"], "drift", msg=out)
        self.assertEqual(plan[0]["source_runtime"], "claude", msg=out)
        self.assertEqual(plan[0]["target_runtime"], "codex", msg=out)


class RootDedupeTests(unittest.TestCase):
    """An explicit CLI root that points at a repo-local default should not
    double-scan the same skill tree under different path spellings."""

    def test_relative_default_and_absolute_cli_root_dedupe(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="skills-meta-roots-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        repo = tmp / "repo"
        (repo / "skills").mkdir(parents=True)

        old_cwd = Path.cwd()
        try:
            os.chdir(repo)
            specs = sm.dedupe_specs(
                [
                    sm.RootSpec(Path("skills"), "default"),
                    sm.RootSpec(repo / "skills", "cli"),
                ]
            )
        finally:
            os.chdir(old_cwd)

        self.assertEqual(len(specs), 1, msg=specs)
        self.assertEqual(specs[0].origin, "cli", msg=specs)


class SyncSymlinkSafetyTests(unittest.TestCase):
    """The destructive review concern: never rmtree through a symlink, never
    flatten source-side symlinks, and refuse symlinked targets without
    --force so a curated dev layout isn't replaced by accident."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="skills-meta-sym-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

        self.repo = self.tmp / "repo"
        (self.repo / "skills" / "linkable").mkdir(parents=True)
        write_skill(self.repo / "skills" / "linkable", "linkable", "1.0.0", "2026-05-01")
        write_manifest(
            self.repo,
            {
                "linkable": {
                    "canonical_version": "1.0.0",
                    "runtime": "shared",
                    "repo_path": "skills/linkable",
                    "last_updated": "2026-05-01",
                    "status": "active",
                }
            },
        )

        # Pretend ~/.codex/skills/linkable is a symlink into the repo — this
        # is exactly the layout someone using `ln -s` for live-edit would
        # have, and the layout the previous code would either crash on or
        # silently follow.
        self.target_root = self.tmp / "codex-install"
        self.target_root.mkdir()
        self.symlink_target = self.target_root / "linkable"
        os.symlink(self.repo / "skills" / "linkable", self.symlink_target)

        # Decoy file inside the repo; if anything follows the symlink and
        # rmtree's blindly, this file disappears.
        self.canary = self.repo / "skills" / "linkable" / "CANARY.md"
        self.canary.write_text("do not delete\n", encoding="utf-8")

    def _run_sync(self, *extra: str) -> tuple[int, str, str]:
        os.chdir(self.repo)
        argv = [
            "skills-meta.py",
            "--mode",
            "sync",
            "--target",
            str(self.target_root),
            "--skill",
            "linkable",
            *extra,
        ]
        old_argv, sys.argv = sys.argv, argv
        out, err = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(out):
                old_stderr, sys.stderr = sys.stderr, err
                try:
                    rc = sm.main()
                finally:
                    sys.stderr = old_stderr
        finally:
            sys.argv = old_argv
        return rc, out.getvalue(), err.getvalue()

    def test_dry_run_flags_symlinked_target(self) -> None:
        rc, out, _ = self._run_sync()
        self.assertEqual(rc, 0)
        # Plan should show in-sync (because the link points at the source)
        # and explicitly mention the symlink in the note.
        self.assertIn("symlinked to", out, msg=out)

    def test_apply_without_force_does_not_touch_symlink(self) -> None:
        rc, out, err = self._run_sync("--apply")
        self.assertEqual(rc, 0)
        self.assertTrue(
            self.symlink_target.is_symlink(),
            msg=f"symlinked target was mutated without --force: {out}{err}",
        )
        self.assertTrue(self.canary.exists(), msg="canary disappeared — rmtree followed the symlink")

    def test_apply_force_unlinks_then_copies_without_following(self) -> None:
        # First make the install drift so --force has work to do.
        # We rewrite the symlink into a new file so it points at *something*
        # but the content differs from source. This mirrors a developer
        # editing the install location after the symlink was set up.
        self.symlink_target.unlink()
        os.symlink(self.repo / "skills" / "linkable" / "CANARY.md", self.symlink_target)
        rc, out, err = self._run_sync("--apply", "--force")
        self.assertEqual(rc, 0, msg=out + err)
        self.assertFalse(
            self.symlink_target.is_symlink(),
            msg="--force should have replaced the symlink with a real copy",
        )
        self.assertTrue(
            (self.symlink_target / "SKILL.md").exists(),
            msg=f"sync did not lay down a fresh copy: {out}{err}",
        )
        self.assertTrue(
            self.canary.exists(),
            msg="--force followed the symlink and deleted source files",
        )


class SyncPreservesInternalSymlinksTests(unittest.TestCase):
    """copytree(symlinks=True) — verify a symlink inside the source survives
    as a symlink in the target, instead of being silently flattened."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="skills-meta-internal-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "repo"
        skill_dir = self.repo / "skills" / "linky"
        skill_dir.mkdir(parents=True)
        write_skill(skill_dir, "linky", "1.0.0", "2026-05-01")
        # bundled "shared" file, plus a symlink inside scripts/ pointing at it
        (skill_dir / "shared").write_text("shared bytes\n", encoding="utf-8")
        (skill_dir / "scripts").mkdir()
        os.symlink(Path("../shared"), skill_dir / "scripts" / "shared-link")
        write_manifest(
            self.repo,
            {
                "linky": {
                    "canonical_version": "1.0.0",
                    "runtime": "shared",
                    "repo_path": "skills/linky",
                    "last_updated": "2026-05-01",
                    "status": "active",
                }
            },
        )
        self.target_root = self.tmp / "install"
        self.target_root.mkdir()

    def test_internal_symlink_preserved(self) -> None:
        os.chdir(self.repo)
        argv = [
            "skills-meta.py",
            "--mode",
            "sync",
            "--target",
            str(self.target_root),
            "--skill",
            "linky",
            "--apply",
        ]
        old_argv, sys.argv = sys.argv, argv
        try:
            with redirect_stdout(io.StringIO()):
                rc = sm.main()
        finally:
            sys.argv = old_argv
        self.assertEqual(rc, 0)
        link = self.target_root / "linky" / "scripts" / "shared-link"
        self.assertTrue(
            link.is_symlink(),
            msg="internal source-side symlink was flattened by copytree",
        )


class FixDuplicatesUnlinksSymlinkTests(unittest.TestCase):
    """When a duplicate copy is itself a symlink, removal must unlink the
    link and never rmtree through it. Otherwise a 'cleanup' could destroy
    the directory the link points at — typically the user's source repo."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="skills-meta-dup-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.real = self.tmp / "real" / "shared-skill"
        self.real.mkdir(parents=True)
        write_skill(self.real, "shared-skill", "1.0.0", "2026-05-01")
        self.canary = self.real / "CANARY.md"
        self.canary.write_text("do not delete\n", encoding="utf-8")

        self.dup_dir = self.tmp / "install" / "shared-skill"
        self.dup_dir.parent.mkdir()
        os.symlink(self.real, self.dup_dir)

    def test_unlink_path_used_for_symlink_duplicate(self) -> None:
        # Build two SkillRecords pointing at the same name, one real, one
        # symlinked. The symlinked one is the "stale" copy we'd remove.
        real_record = sm.SkillRecord(
            name="shared-skill",
            path=self.real / "SKILL.md",
            root=self.real.parent,
            runtime="shared",
            version="1.0.0",
            last_updated="2026-05-01",
            description="fixture",
        )
        dup_record = sm.SkillRecord(
            name="shared-skill",
            path=self.dup_dir / "SKILL.md",
            root=self.dup_dir.parent,
            runtime="shared",
            version="1.0.0",
            last_updated="2026-05-01",
            description="fixture",
        )
        dup_record.duplicate_of = "shared-skill"
        groups = {"shared-skill": [real_record, dup_record]}

        # Force interactive y by piping yes through stdin, and pretend it's a TTY.
        old_stdin = sys.stdin
        sys.stdin = io.StringIO("y\n")
        sys.stdin.isatty = lambda: True  # type: ignore[attr-defined]
        try:
            with redirect_stdout(io.StringIO()):
                sm.apply_fix_duplicates(groups)
        finally:
            sys.stdin = old_stdin

        self.assertFalse(
            self.dup_dir.exists() or self.dup_dir.is_symlink(),
            msg="symlink duplicate should have been unlinked",
        )
        self.assertTrue(
            self.canary.exists(),
            msg="rmtree followed the symlink and deleted the real source",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
