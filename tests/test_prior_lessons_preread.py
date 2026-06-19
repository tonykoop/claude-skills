#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "maker"
    / "skills"
    / "idea-incubator"
    / "scripts"
    / "prior_lessons_preread.py"
)
STORE = (
    REPO_ROOT
    / "plugins"
    / "maker"
    / "skills"
    / "idea-incubator"
    / "references"
    / "institutional-knowledge.md"
)


def load_module():
    spec = importlib.util.spec_from_file_location("prior_lessons_preread", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["prior_lessons_preread"] = module
    spec.loader.exec_module(module)
    return module


pre = load_module()


STORE_TEXT = textwrap.dedent(
    """
    # Store

    ### Recovery captures keep their source issue open
    - **Context:** Promoting archive/legacy/recovery captures.
    - **Lesson:** Default to Refs not Closes.
    - **Applies-to:** promote, promote-batch, provenance
    - **Source:** seeded, 2026-06-16

    ### Run LFS prompts before any binary-asset repo scaffold
    - **Context:** Captures mentioning CAD/media/ZIPs.
    - **Lesson:** Decide LFS policy before the first commit.
    - **Applies-to:** promote, lfs, maker
    - **Source:** seeded, 2026-06-16

    ### Keep uncertain idea splits together
    - **Context:** Intake of an ambiguous dump.
    - **Lesson:** Keep candidates in one issue, mark the ambiguity.
    - **Applies-to:** intake, capture, general
    - **Source:** seeded, 2026-06-16
    """
).strip()


class ParseStoreTests(unittest.TestCase):
    def test_parses_entries_with_fields(self) -> None:
        lessons = pre.parse_store(STORE_TEXT)
        self.assertEqual(len(lessons), 3)
        first = lessons[0]
        self.assertEqual(first.title, "Recovery captures keep their source issue open")
        self.assertEqual(first.applies_to, ["promote", "promote-batch", "provenance"])
        self.assertTrue(first.lesson)

    def test_shipped_store_parses(self) -> None:
        lessons = pre.parse_store(STORE.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(lessons), 4)
        self.assertTrue(all(le.lesson for le in lessons))


class SelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lessons = pre.parse_store(STORE_TEXT)

    def test_ranks_by_tag_overlap(self) -> None:
        selected = pre.select_lessons(self.lessons, ["promote", "lfs"], limit=5)
        titles = [le.title for le in selected]
        # The LFS lesson overlaps both tags (promote + lfs) -> ranks first.
        self.assertEqual(titles[0], "Run LFS prompts before any binary-asset repo scaffold")

    def test_caps_to_limit(self) -> None:
        selected = pre.select_lessons(self.lessons, ["promote"], limit=1)
        self.assertEqual(len(selected), 1)

    def test_falls_back_to_general_when_no_overlap(self) -> None:
        selected = pre.select_lessons(self.lessons, ["yoga"], limit=5)
        self.assertEqual([le.title for le in selected], ["Keep uncertain idea splits together"])

    def test_empty_store_returns_empty(self) -> None:
        self.assertEqual(pre.select_lessons([], ["promote"], limit=5), [])


class DeriveTagsTests(unittest.TestCase):
    def test_derives_known_vocab_tags(self) -> None:
        tags = pre.derive_tags("This brainstorm covers firmware and electronics for a maker rig.")
        self.assertIn("firmware", tags)
        self.assertIn("electronics", tags)
        self.assertIn("maker", tags)
        self.assertNotIn("general", tags)


class RenderTests(unittest.TestCase):
    def test_empty_selection_renders_graceful_note(self) -> None:
        block = pre.render_block([], ["yoga"])
        self.assertIn("No prior lessons matched", block)
        self.assertIn("## Prior lessons to honor", block)

    def test_selection_renders_lessons_and_citation_instruction(self) -> None:
        lessons = pre.parse_store(STORE_TEXT)
        block = pre.render_block(lessons[:1], ["promote"])
        self.assertIn("applied lesson", block)
        self.assertIn("Default to Refs not Closes", block)


class LoadAndGracefulTests(unittest.TestCase):
    def test_missing_store_and_folder_degrade_gracefully(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            missing_store = Path(d) / "nope.md"
            missing_folder = Path(d) / "nofolder"
            lessons = pre.load_lessons(missing_store, missing_folder)
            self.assertEqual(lessons, [])
            block = pre.render_block(pre.select_lessons(lessons, ["promote"], 5), ["promote"])
            self.assertIn("No prior lessons matched", block)

    def test_includes_per_epic_folder_notes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            store = Path(d) / "store.md"
            store.write_text(STORE_TEXT, encoding="utf-8")
            folder = Path(d) / "ik"
            folder.mkdir()
            (folder / "epic-9-retro.md").write_text(
                "### Folder lesson\n- **Lesson:** from a per-epic note.\n"
                "- **Applies-to:** software\n- **Source:** epic #9 retro\n",
                encoding="utf-8",
            )
            lessons = pre.load_lessons(store, folder)
            self.assertTrue(any(le.title == "Folder lesson" for le in lessons))

    def test_main_runs_with_tags(self) -> None:
        rc = pre.main(["--tags", "promote", "--store", str(STORE), "--limit", "3"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
