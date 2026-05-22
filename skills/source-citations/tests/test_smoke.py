#!/usr/bin/env python3
"""Round-trip smoke tests for source-citations.

No external deps. Run from anywhere:

    python3 skills/source-citations/tests/test_smoke.py

What this guards:
  * `build_registry.py` produces stable, unique keys from the bundled TSV
    (the full library) and a tiny fixture TSV (controlled inputs).
  * `gen_sources.py check` passes on a valid `.citations.yaml` and FAILS
    on the two failure modes that matter (unknown key, blank `why`).
  * `gen_sources.py gen` writes a SOURCES.md whose content exactly matches
    an expected snippet from the fixture inputs.
  * `gen_techniques.py audit` reports the seed status counts the SKILL.md
    promises (0 confirmed, 2 unconfirmed).
  * `gen_techniques.py site` strips inline YAML comments from scalars
    (regression guard for the `platform: web  # ...` bug fixed in 0.1.0).
"""
from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL_DIR / "scripts"
REFS = SKILL_DIR / "references"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(SCRIPTS))
import build_registry  # type: ignore
import gen_sources     # type: ignore
import gen_techniques  # type: ignore


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True, cwd=str(SKILL_DIR),
    )


class TestBuildRegistry(unittest.TestCase):
    def test_full_library_201_unique(self):
        # The shipped library.tsv must produce exactly the entry count the
        # SKILL.md and CHANGELOG promise (201), with no duplicate keys.
        rows = build_registry.load(REFS / "library.tsv")
        entries = build_registry.build(rows)
        keys = [e["key"] for e in entries]
        self.assertEqual(len(entries), 201)
        self.assertEqual(len(keys), len(set(keys)))
        # Spot-check a stable key that real repos already cite.
        self.assertIn("demakein", set(keys))

    def test_mini_fixture(self):
        rows = build_registry.load(FIXTURES / "mini-library.tsv")
        entries = build_registry.build(rows)
        keys = {e["key"] for e in entries}
        self.assertEqual(keys, {"demakein", "openwind", "audacity"})


class TestGenSources(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="source-citations-test-"))
        shutil.copy(FIXTURES / "sample-citations.yaml", self.tmp / ".citations.yaml")
        self.registry = gen_sources.load_registry(REFS / "registry.yaml")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _capture(self, fn, *args):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = fn(*args)
        return rc, buf.getvalue()

    def test_check_passes_on_valid_citations(self):
        rc, _ = self._capture(gen_sources.cmd_check, self.tmp, self.registry)
        self.assertEqual(rc, 0)

    def test_check_fails_on_unknown_key(self):
        (self.tmp / ".citations.yaml").write_text(
            "instrument: X\nrepo: x\ncites:\n  - key: not-a-real-key\n    why: nope\n",
            encoding="utf-8",
        )
        rc, out = self._capture(gen_sources.cmd_check, self.tmp, self.registry)
        self.assertEqual(rc, 1)
        self.assertIn("unknown key", out)

    def test_check_fails_on_blank_why(self):
        # The integrity rule that distinguishes this skill from a bibtex dump:
        # no rationale, no citation.
        (self.tmp / ".citations.yaml").write_text(
            "instrument: X\nrepo: x\ncites:\n  - key: demakein\n    why:\n",
            encoding="utf-8",
        )
        rc, out = self._capture(gen_sources.cmd_check, self.tmp, self.registry)
        self.assertEqual(rc, 1)
        self.assertIn("no 'why'", out)

    def test_gen_writes_sources_md(self):
        rc, _ = self._capture(gen_sources.cmd_gen, self.tmp, self.registry)
        self.assertEqual(rc, 0)
        body = (self.tmp / "SOURCES.md").read_text(encoding="utf-8")
        self.assertIn("# Sources & References — Sample Flute", body)
        self.assertIn("[Demakein](https://github.com/pfh/demakein)", body)
        self.assertIn("Generated the bore profile", body)
        self.assertIn("2 sources cited", body)


class TestGenTechniques(unittest.TestCase):
    def setUp(self):
        self.reg = gen_techniques.load_registry(REFS / "techniques.yaml")

    def test_audit_counts(self):
        confirmed = [k for k, e in self.reg.items() if e.get("status") == "confirmed"]
        seeds = [k for k, e in self.reg.items() if e.get("status") == "unconfirmed"]
        self.assertEqual(len(confirmed), 0)
        self.assertEqual(len(seeds), 2)

    def test_inline_comments_stripped(self):
        # Regression guard for the 0.1.0 fix: the Schama seed declares
        # `platform: web  # youtube | maker-tok | ...`. The scalar parser
        # must drop the inline comment.
        self.assertEqual(self.reg["schama-layered-relief"]["platform"], "web")

    def test_site_render_omits_comment_text(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".qmd", delete=False) as f:
            qmd = Path(f.name)
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                gen_techniques.cmd_site(qmd, self.reg)
            body = qmd.read_text(encoding="utf-8")
            self.assertIn("Gabriel Schama", body)
            # The comment text must not leak into the rendered link label.
            self.assertNotIn("# youtube", body)
            self.assertNotIn("maker-tok", body)
        finally:
            qmd.unlink(missing_ok=True)


class TestCliSmoke(unittest.TestCase):
    """Tickle the actual command-line entry points so a refactor that
    breaks argparse wiring is caught even when the in-process tests pass."""

    def test_build_registry_cli(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "registry.yaml"
            r = _run("build_registry.py", str(FIXTURES / "mini-library.tsv"), "--out", str(out))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(out.exists())
            self.assertTrue(out.with_suffix(".json").exists())

    def test_gen_techniques_audit_cli(self):
        r = _run("gen_techniques.py", "audit")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("confirmed: 0", r.stdout)
        self.assertIn("unconfirmed: 2", r.stdout)


if __name__ == "__main__":
    unittest.main()
