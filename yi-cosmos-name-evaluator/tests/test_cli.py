from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
CLI = SKILL_ROOT / "scripts" / "evaluate_name.py"
FIXTURES = json.loads(
    (SKILL_ROOT / "tests" / "fixtures.json").read_text(encoding="utf-8")
)["anchors"]


class CliTestCase(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(CLI), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_help(self) -> None:
        process = self.run_cli("--help")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("prepare", process.stdout)
        self.assertIn("score", process.stdout)

    def test_prepare_and_score_json(self) -> None:
        case = FIXTURES[0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request_path = root / "request.json"
            prepared_path = root / "prepared.json"
            completed_path = root / "completed.json"
            request_path.write_text(
                json.dumps(case["request"], ensure_ascii=False),
                encoding="utf-8",
            )
            prepared_process = self.run_cli(
                "prepare",
                "--input",
                str(request_path),
                "--output",
                str(prepared_path),
            )
            self.assertEqual(prepared_process.returncode, 0, prepared_process.stderr)
            prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
            prepared["judgments"] = case["judgments"]
            completed_path.write_text(
                json.dumps(prepared, ensure_ascii=False),
                encoding="utf-8",
            )
            score_process = self.run_cli(
                "score",
                "--input",
                str(completed_path),
                "--format",
                "json",
            )
            self.assertEqual(score_process.returncode, 0, score_process.stderr)
            result = json.loads(score_process.stdout)
            self.assertEqual(result["score"], case["expected"]["target"])

    def test_validation_error_uses_exit_code_two(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "bad.json"
            request_path.write_text(
                '{"object_type":"product"}',
                encoding="utf-8",
            )
            process = self.run_cli("prepare", "--input", str(request_path))
            self.assertEqual(process.returncode, 2)
            self.assertIn("name", process.stderr)
