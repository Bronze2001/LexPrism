"""Offline checks for the packaged LexPrism Skill; no model, API, or MCP call."""

from __future__ import annotations

import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "lexprism"
SKILL_FILE = SKILL_DIR / "SKILL.md"
REFERENCE_DIR = SKILL_DIR / "references"
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+\.md)\)")


def packaged_references() -> dict[str, Path]:
    return {
        path.name: path
        for path in sorted(REFERENCE_DIR.glob("*.md"))
        if path.is_file()
    }


class SkillLoadingTests(unittest.TestCase):
    def test_skill_entry_and_packaged_references_are_readable(self):
        self.assertTrue(SKILL_FILE.is_file(), "Missing lexprism/SKILL.md")
        self.assertTrue(SKILL_FILE.read_text(encoding="utf-8").strip())
        self.assertGreaterEqual(len(packaged_references()), 1)
        for path in packaged_references().values():
            with self.subTest(reference=path.name):
                self.assertTrue(path.read_text(encoding="utf-8").strip())

    def test_skill_markdown_references_stay_inside_the_package(self):
        for source in [SKILL_FILE, *packaged_references().values()]:
            for target in LINK_PATTERN.findall(source.read_text(encoding="utf-8")):
                resolved = (source.parent / target).resolve()
                with self.subTest(source=source.name, target=target):
                    self.assertTrue(resolved.is_file(), f"Broken reference: {target}")
                    self.assertTrue(resolved.is_relative_to(SKILL_DIR.resolve()), f"External reference: {target}")

    def test_required_workflows_are_packaged(self):
        required = {
            "research.md",
            "drafting-review.md",
            "intake-and-samples.md",
            "translation-privacy.md",
        }
        self.assertTrue(required.issubset(packaged_references()))


if __name__ == "__main__":
    unittest.main()
