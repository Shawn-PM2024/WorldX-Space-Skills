from __future__ import annotations

import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


class SkillPackageTestCase(unittest.TestCase):
    def test_required_skill_files_exist(self) -> None:
        required = (
            "SKILL.md",
            "agents/openai.yaml",
            "references/methodology.md",
            "references/scoring-rubric.md",
            "references/report-contract.md",
            "scripts/evaluate_name.py",
        )
        for relative_path in required:
            with self.subTest(path=relative_path):
                self.assertTrue((SKILL_ROOT / relative_path).is_file())

    def test_skill_frontmatter_and_routing(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: yi-cosmos-name-evaluator", text)
        self.assertIn("description: Use when", text)
        self.assertIn("scripts/evaluate_name.py", text)
        self.assertIn("references/scoring-rubric.md", text)
        self.assertNotIn("TODO", text)
        self.assertNotIn("TBD", text)


if __name__ == "__main__":
    unittest.main()
