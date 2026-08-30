from __future__ import annotations

import copy
import inspect
import json
import sys
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from yi_cosmos_evaluator import (
    UnsupportedCharacterError,
    ValidationError,
    load_character_data,
    prepare_evaluation,
    reduce_numerology,
    render_markdown,
    score_evaluation,
)


class EvaluatorTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture_path = SKILL_ROOT / "tests" / "fixtures.json"
        cls.fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))["anchors"]

    def fixture(self, label: str) -> dict:
        return copy.deepcopy(
            next(case for case in self.fixtures if case["label"] == label)
        )

    def complete(self, label: str) -> dict:
        case = self.fixture(label)
        prepared = prepare_evaluation(case["request"])
        prepared["judgments"] = case["judgments"]
        return prepared

    def test_required_name_is_validated(self) -> None:
        with self.assertRaisesRegex(ValidationError, "name"):
            prepare_evaluation({"object_type": "product"})

    def test_object_type_is_validated(self) -> None:
        with self.assertRaisesRegex(ValidationError, "object_type"):
            prepare_evaluation({"name": "测试", "object_type": "person"})

    def test_reduction_keeps_81_before_reducing_larger_totals(self) -> None:
        self.assertEqual(reduce_numerology(1), 1)
        self.assertEqual(reduce_numerology(81), 81)
        self.assertEqual(reduce_numerology(82), 2)
        self.assertEqual(reduce_numerology(160), 80)
        self.assertEqual(reduce_numerology(161), 81)

    def test_character_data_contains_current_and_traditional_strokes(self) -> None:
        data = load_character_data()
        self.assertIn(7, data["灵"]["strokes"])
        self.assertIn("靈", data["灵"]["traditional"])
        self.assertIn(24, data["靈"]["strokes"])
        self.assertIn("識", data["识"]["traditional"])
        self.assertIn(19, data["識"]["strokes"])
        self.assertIn("樞", data["枢"]["traditional"])
        self.assertIn(15, data["樞"]["strokes"])

    def test_prepare_exposes_character_and_hexagram_facts(self) -> None:
        prepared = prepare_evaluation(self.fixture("ling-shi")["request"])
        mechanical = prepared["mechanical"]
        self.assertEqual(mechanical["current"]["full_total"], 35)
        self.assertEqual(mechanical["traditional"]["full_total"], 81)
        self.assertEqual(mechanical["current"]["hexagram"]["upper_trigram"], "巽")
        self.assertEqual(mechanical["current"]["hexagram"]["lower_trigram"], "坎")
        self.assertEqual(mechanical["current"]["hexagram"]["moving_line"], 5)
        self.assertEqual(mechanical["traditional"]["hexagram"]["upper_trigram"], "坎")
        self.assertEqual(mechanical["traditional"]["hexagram"]["lower_trigram"], "离")
        self.assertEqual(mechanical["traditional"]["hexagram"]["moving_line"], 3)

    def test_distinctive_segment_drives_product_numerology_without_name_override(
        self,
    ) -> None:
        ling_shi = prepare_evaluation(self.fixture("ling-shi")["request"])
        ling_shu = prepare_evaluation(self.fixture("ling-shu")["request"])
        self.assertAlmostEqual(
            ling_shi["mechanical"]["numerology"]["score"], 55.16, places=2
        )
        self.assertAlmostEqual(
            ling_shu["mechanical"]["numerology"]["score"], 78.16, places=2
        )

    def test_unknown_symbol_requires_an_override(self) -> None:
        request = {
            "name": "灵🜁",
            "object_type": "brand",
            "scored_segment": "灵🜁",
        }
        with self.assertRaises(UnsupportedCharacterError):
            prepare_evaluation(request)

    def test_sourced_stroke_override_enables_missing_character(self) -> None:
        prepared = prepare_evaluation(
            {
                "name": "灵〇",
                "object_type": "brand",
                "industries": ["人工智能"],
                "stroke_overrides": {
                    "〇": {
                        "strokes": [1],
                        "source": "user-supplied dictionary record",
                    }
                },
            }
        )
        self.assertEqual(prepared["mechanical"]["current"]["strokes"], [7, 1])
        override_record = prepared["mechanical"]["character_analysis"][1]
        self.assertEqual(
            override_record["override_source"],
            "user-supplied dictionary record",
        )

    def test_latin_brand_omits_chinese_mechanical_dimensions(self) -> None:
        prepared = prepare_evaluation(
            {
                "name": "Aether",
                "object_type": "brand",
                "industries": ["人工智能"],
                "positioning": "国际化人工智能品牌",
            }
        )
        self.assertFalse(prepared["mechanical"]["applicable"])
        self.assertIn(
            "Chinese mechanical dimensions are unavailable",
            " ".join(prepared["evidence_gaps"]),
        )
        prepared["judgments"] = {
            "meaning_allusion": {
                "score": 82,
                "rationale": "International meaning is positive but culturally indirect.",
                "uncertainty": "medium",
                "evidence": [
                    {
                        "type": "model_judgment",
                        "claim": "The name has an international technology tone.",
                    }
                ],
            },
            "industry_positioning": {
                "score": 80,
                "rationale": "Suitable for an AI brand.",
                "uncertainty": "medium",
                "evidence": [
                    {
                        "type": "model_judgment",
                        "claim": "Industry fit is positive.",
                    }
                ],
            },
            "sound_form": {
                "score": 76,
                "rationale": "Pronunciation requires localization guidance.",
                "uncertainty": "medium",
                "evidence": [
                    {
                        "type": "model_judgment",
                        "claim": "Chinese pronunciation is not self-evident.",
                    }
                ],
            },
        }
        result = score_evaluation(prepared)
        keys = {item["key"] for item in result["dimensions"]}
        self.assertEqual(
            keys,
            {"meaning_allusion", "industry_positioning", "sound_form"},
        )
        self.assertEqual(result["confidence"], "低")

    def test_single_chinese_character_omits_hexagram_only(self) -> None:
        prepared = prepare_evaluation(
            {
                "name": "鼎",
                "object_type": "brand",
                "industries": ["大健康"],
            }
        )
        self.assertTrue(prepared["mechanical"]["applicable"])
        self.assertFalse(prepared["mechanical"]["hexagram_applicable"])
        self.assertIsNone(prepared["mechanical"]["current"]["hexagram"])

    def test_missing_judgments_fail_closed(self) -> None:
        prepared = prepare_evaluation(self.fixture("ling-shi")["request"])
        with self.assertRaisesRegex(ValidationError, "judgments"):
            score_evaluation(prepared)

    def test_incomplete_birth_data_never_creates_a_bazi_modifier(self) -> None:
        result = score_evaluation(self.complete("ling-shi"))
        modifier = result["modifiers"]["legal_representative_bazi"]
        self.assertFalse(modifier["applied"])
        self.assertEqual(modifier["value"], 0)
        self.assertIn("birth_date", " ".join(result["evidence_gaps"]))

    def test_context_modifier_bounds_are_enforced(self) -> None:
        completed = self.complete("ling-shi")
        completed["context_modifiers"] = {
            "establishment_timing": {
                "value": 4,
                "rationale": "outside the allowed range",
                "evidence": [{"type": "model_judgment", "claim": "invalid"}],
            }
        }
        with self.assertRaisesRegex(ValidationError, "establishment_timing"):
            score_evaluation(completed)

    def test_complete_context_modifiers_require_sources_and_apply(self) -> None:
        case = self.fixture("ling-shi")
        case["request"]["company"]["established_at"] = "09:30"
        case["request"]["legal_representative"].update(
            {
                "birth_date": "1980-01-02",
                "birth_time": "08:15",
                "calendar": "gregorian",
            }
        )
        completed = prepare_evaluation(case["request"])
        completed["judgments"] = case["judgments"]
        completed["context_modifiers"] = {
            "establishment_timing": {
                "value": 2,
                "rationale": "A sourced calendrical analysis reports modest support.",
                "evidence": [
                    {
                        "type": "model_judgment",
                        "claim": "This unsupported interpretation is insufficient.",
                    }
                ],
            },
            "legal_representative_bazi": {
                "value": 3,
                "rationale": "A sourced Four Pillars analysis reports strong support.",
                "evidence": [
                    {
                        "type": "traditional_rule",
                        "claim": "The supplied profile reports compatible favorable elements.",
                        "source": "test-profile.json",
                    }
                ],
            },
        }
        with self.assertRaisesRegex(ValidationError, "auditable"):
            score_evaluation(completed)
        completed["context_modifiers"]["establishment_timing"]["evidence"] = [
            {
                "type": "traditional_rule",
                "claim": "The supplied establishment profile reports modest support.",
                "source": "test-establishment-profile.json",
            }
        ]
        result = score_evaluation(completed)
        self.assertTrue(result["modifiers"]["establishment_timing"]["applied"])
        self.assertTrue(result["modifiers"]["legal_representative_bazi"]["applied"])
        self.assertEqual(result["score"], 77)

    def test_anchor_regressions_and_determinism(self) -> None:
        for case in self.fixtures:
            with self.subTest(case=case["label"]):
                completed = self.complete(case["label"])
                first = score_evaluation(completed)
                second = score_evaluation(copy.deepcopy(completed))
                self.assertEqual(first, second)
                self.assertGreaterEqual(first["score"], case["expected"]["minimum"])
                self.assertLessEqual(first["score"], case["expected"]["maximum"])
                self.assertEqual(first["score"], case["expected"]["target"])

    def test_score_recomputes_mechanical_facts_instead_of_trusting_input(self) -> None:
        clean = self.complete("ling-shi")
        tampered = copy.deepcopy(clean)
        tampered["mechanical"]["numerology"]["score"] = 100
        tampered["mechanical"]["parity_score"] = 100
        self.assertEqual(
            score_evaluation(clean)["score"],
            score_evaluation(tampered)["score"],
        )

    def test_markdown_report_has_required_sections(self) -> None:
        report = render_markdown(score_evaluation(self.complete("ling-shu")))
        for heading in (
            "# 易乾坤名称综合评估",
            "## 综合结论",
            "## 数据事实",
            "## 传统规则解释",
            "## 模型判断",
            "## 证据缺口",
            "## 使用边界",
        ):
            self.assertIn(heading, report)
        self.assertIn("《灵枢》为《黄帝内经》的组成部分", report)
        self.assertIn(
            "https://zh.wikisource.org/wiki/黃帝內經/靈樞",
            report,
        )

    def test_production_source_has_no_anchor_name_branches(self) -> None:
        import yi_cosmos_evaluator

        source = inspect.getsource(yi_cosmos_evaluator)
        self.assertNotIn("赫灵灵识", source)
        self.assertNotIn("赫灵灵枢", source)


if __name__ == "__main__":
    unittest.main()
