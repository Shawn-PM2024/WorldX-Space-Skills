import importlib.util
import json
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class SkillPackageTests(unittest.TestCase):
    def test_entrypoint_stays_small_and_routes_to_resources(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertLessEqual(len(skill_text.splitlines()), 150)
        self.assertIn("references/derivation-method.md", skill_text)
        self.assertIn("references/gotchas.md", skill_text)
        self.assertIn("scripts/validate_output.py", skill_text)

    def test_eval_set_covers_load_forbidden_load_and_execution(self):
        eval_path = SKILL_ROOT / "evals" / "cases.json"
        cases = json.loads(eval_path.read_text(encoding="utf-8"))
        routing_expectations = {case["expected"] for case in cases["routing"]}

        self.assertEqual(routing_expectations, {"load", "do_not_load"})
        self.assertGreaterEqual(len(cases["execution"]), 3)

    def test_output_validator_accepts_traceable_output(self):
        validator = self._load_validator()
        markdown = """\
### 1. 首次启动流程正在截断核心价值

- 原始内容：
  - F1「5 名新用户中有 3 名在配网步骤中断。」
  - F2「完成绑定的用户中，87% 当天使用了核心功能。」
- 推导链：F1 与 F2 形成绑定前后的对比 → 阻塞集中在价值到达之前。
- 边界：样本只有 5 名新用户，不能估计总体流失率。
"""

        self.assertEqual(validator.validate_markdown(markdown), [])

    def test_output_validator_rejects_locator_only_evidence(self):
        validator = self._load_validator()
        markdown = """\
### 1. 首次启动流程正在截断核心价值

- 原始内容：
  - F1（12:08）
  - F2（第 4 页）
- 推导链：F1 + F2 → 结论。
- 边界：样本有限。
"""

        errors = validator.validate_markdown(markdown)
        self.assertTrue(any("定位信息" in error for error in errors), errors)

    @staticmethod
    def _load_validator():
        validator_path = SKILL_ROOT / "scripts" / "validate_output.py"
        spec = importlib.util.spec_from_file_location("validate_output", validator_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


if __name__ == "__main__":
    unittest.main()
