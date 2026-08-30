#!/usr/bin/env python3
"""Deterministic core for the Yi Cosmos commercial-name evaluation skill."""

from __future__ import annotations

import copy
import gzip
import json
from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = SKILL_ROOT / "references" / "data"
ALLOWED_OBJECT_TYPES = {"company", "brand", "product"}
JUDGMENT_KEYS = (
    "five_elements",
    "hexagram",
    "meaning_allusion",
    "industry_positioning",
    "sound_form",
    "brand_synergy",
)
EVIDENCE_TYPES = {
    "lexical_source",
    "classical_source",
    "traditional_rule",
    "model_judgment",
}
DIMENSION_CONFIG = {
    "commercial_numerology": {"label": "商业数理", "weight": 20.0},
    "yin_yang_five_elements": {"label": "阴阳五行", "weight": 15.0},
    "hexagram": {"label": "周易卦象", "weight": 15.0},
    "meaning_allusion": {"label": "字义与典故", "weight": 20.0},
    "industry_positioning": {"label": "行业与定位", "weight": 15.0},
    "sound_form": {"label": "音形与传播", "weight": 10.0},
    "brand_synergy": {"label": "母品牌协同", "weight": 5.0},
}


class ValidationError(ValueError):
    """Raised when an evaluation request or judgment is invalid."""


class UnsupportedCharacterError(ValidationError):
    """Raised when deterministic stroke data is unavailable."""


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _load_character_payload() -> dict:
    path = DATA_DIR / "unihan-17.0.0.json.gz"
    if not path.exists():
        raise RuntimeError(f"character data is missing: {path}")
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def load_character_data() -> dict[str, dict]:
    """Return the pinned Unihan character map."""
    return _load_character_payload()["characters"]


def character_data_metadata() -> dict:
    return copy.deepcopy(_load_character_payload()["metadata"])


@lru_cache(maxsize=1)
def _load_numerology() -> dict[int, dict]:
    configuration = _read_json(DATA_DIR / "numerology-81.json")
    result: dict[int, dict] = {}
    for group_name, group in configuration["groups"].items():
        for number in group["numbers"]:
            if number in result:
                raise RuntimeError(f"duplicate numerology number: {number}")
            result[number] = {
                "group": group_name,
                "label": group["label"],
                "score": float(group["score"]),
            }
    if set(result) != set(range(1, 82)):
        missing = sorted(set(range(1, 82)) - set(result))
        raise RuntimeError(f"numerology table is incomplete: {missing}")
    for raw_number, score in configuration.get("score_overrides", {}).items():
        result[int(raw_number)]["score"] = float(score)
    return result


@lru_cache(maxsize=1)
def _load_trigrams() -> dict[str, dict]:
    return _read_json(DATA_DIR / "trigrams.json")["modulo_mapping"]


@lru_cache(maxsize=1)
def _load_hexagrams() -> dict[str, dict]:
    return _read_json(DATA_DIR / "hexagrams.json")["mapping"]


def reduce_numerology(total: int) -> int:
    """Reduce a positive total into the configured 1..81 system."""
    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        raise ValidationError("numerology total must be a positive integer")
    while total > 81:
        total -= 80
    return total


def _numerology_fact(total: int) -> dict:
    number = reduce_numerology(total)
    entry = _load_numerology()[number]
    return {
        "total": total,
        "number": number,
        "grade": entry["label"],
        "group": entry["group"],
        "score": entry["score"],
    }


def _validate_string(value: Any, field: str, *, required: bool = True) -> str | None:
    if value is None and not required:
        return None
    if not isinstance(value, str) or value.strip() == "":
        raise ValidationError(f"{field} must be a non-empty string")
    return value.strip()


def _validate_request(raw_request: dict) -> dict:
    if not isinstance(raw_request, dict):
        raise ValidationError("request must be an object")
    request = copy.deepcopy(raw_request)
    request["name"] = _validate_string(request.get("name"), "name")
    object_type = _validate_string(request.get("object_type"), "object_type")
    if object_type not in ALLOWED_OBJECT_TYPES:
        allowed = ", ".join(sorted(ALLOWED_OBJECT_TYPES))
        raise ValidationError(f"object_type must be one of: {allowed}")
    request["object_type"] = object_type

    scored_segment = request.get("scored_segment")
    if scored_segment is None:
        if object_type == "company" and any(
            marker in request["name"]
            for marker in ("有限公司", "有限责任公司", "股份有限公司", "（", "(")
        ):
            raise ValidationError(
                "scored_segment is required for a full company name; confirm the trade-name segment"
            )
        scored_segment = request["name"]
    request["scored_segment"] = _validate_string(scored_segment, "scored_segment")

    brand_prefix = request.get("brand_prefix")
    distinctive_segment = request.get("distinctive_segment")
    if brand_prefix is not None:
        brand_prefix = _validate_string(brand_prefix, "brand_prefix")
        if not request["scored_segment"].startswith(brand_prefix):
            raise ValidationError("brand_prefix must be a prefix of scored_segment")
        request["brand_prefix"] = brand_prefix
        derived = request["scored_segment"][len(brand_prefix) :]
        if distinctive_segment is None:
            distinctive_segment = derived
    if distinctive_segment is not None:
        distinctive_segment = _validate_string(
            distinctive_segment, "distinctive_segment"
        )
        if (
            brand_prefix
            and brand_prefix + distinctive_segment != request["scored_segment"]
        ):
            raise ValidationError(
                "brand_prefix plus distinctive_segment must equal scored_segment"
            )
        if distinctive_segment not in request["scored_segment"]:
            raise ValidationError(
                "distinctive_segment must be contained in scored_segment"
            )
        request["distinctive_segment"] = distinctive_segment
    else:
        request["distinctive_segment"] = request["scored_segment"]

    industries = request.get("industries", [])
    if industries is None:
        industries = []
    if not isinstance(industries, list) or any(
        not isinstance(item, str) or item.strip() == "" for item in industries
    ):
        raise ValidationError("industries must be an array of non-empty strings")
    request["industries"] = [item.strip() for item in industries]

    overrides = request.get("stroke_overrides", {})
    if not isinstance(overrides, dict):
        raise ValidationError("stroke_overrides must be an object")
    for character, override in overrides.items():
        if len(character) != 1 or not isinstance(override, dict):
            raise ValidationError(
                "each stroke_overrides entry must use one character and an object"
            )
        if (
            not isinstance(override.get("source"), str)
            or override["source"].strip() == ""
        ):
            raise ValidationError(f"stroke_overrides.{character}.source is required")
        strokes = override.get("strokes")
        if strokes is not None and (
            not isinstance(strokes, list)
            or not strokes
            or any(
                not isinstance(item, int) or isinstance(item, bool) or item <= 0
                for item in strokes
            )
        ):
            raise ValidationError(
                f"stroke_overrides.{character}.strokes must contain positive integers"
            )
    request["stroke_overrides"] = overrides
    return request


def _record_for(character: str, request: dict) -> dict:
    base = copy.deepcopy(load_character_data().get(character, {}))
    override = request.get("stroke_overrides", {}).get(character)
    if override:
        for key in (
            "strokes",
            "traditional",
            "simplified",
            "definition",
            "mandarin",
        ):
            if key in override:
                base[key] = copy.deepcopy(override[key])
        base["override_source"] = override["source"]
    if not base.get("strokes"):
        raise UnsupportedCharacterError(
            f"unsupported character {character!r}; provide stroke_overrides with a source"
        )
    base["strokes"] = sorted({int(value) for value in base["strokes"]})
    return base


def _analyze_characters(
    segment: str, request: dict
) -> tuple[list[dict], list[int], list[int], str]:
    analyses: list[dict] = []
    current_strokes: list[int] = []
    traditional_strokes: list[int] = []
    traditional_text: list[str] = []
    for character in segment:
        current_record = _record_for(character, request)
        variants = current_record.get("traditional") or [character]
        traditional_options: list[dict] = []
        for variant in variants:
            variant_record = _record_for(variant, request)
            traditional_options.append(
                {
                    "character": variant,
                    "strokes": variant_record["strokes"],
                    "definition": variant_record.get("definition"),
                    "mandarin": variant_record.get("mandarin"),
                    "override_source": variant_record.get("override_source"),
                }
            )
        traditional_options.sort(key=lambda item: ord(item["character"]))
        chosen = traditional_options[0]
        analyses.append(
            {
                "character": character,
                "current_strokes": current_record["strokes"],
                "definition": current_record.get("definition"),
                "mandarin": current_record.get("mandarin"),
                "traditional_variants": traditional_options,
                "override_source": current_record.get("override_source"),
            }
        )
        current_strokes.append(current_record["strokes"][0])
        traditional_text.append(chosen["character"])
        traditional_strokes.append(chosen["strokes"][0])
    return analyses, current_strokes, traditional_strokes, "".join(traditional_text)


def _split_segments(segment: str, request: dict) -> tuple[str, str]:
    prefix = request.get("brand_prefix")
    distinctive = request.get("distinctive_segment")
    if prefix and distinctive:
        return prefix, distinctive
    split_at = (len(segment) + 1) // 2
    return segment[:split_at], segment[split_at:]


def _hexagram_fact(upper_segment: str, lower_segment: str, strokes: list[int]) -> dict:
    split_at = len(upper_segment)
    upper_sum = sum(strokes[:split_at])
    lower_sum = sum(strokes[split_at:])
    if not upper_segment or not lower_segment:
        raise ValidationError("hexagram segmentation requires two non-empty segments")
    upper_modulo = upper_sum % 8
    lower_modulo = lower_sum % 8
    trigrams = _load_trigrams()
    upper = trigrams[str(upper_modulo)]
    lower = trigrams[str(lower_modulo)]
    key = f"{upper['name']}/{lower['name']}"
    hexagram = _load_hexagrams()[key]
    moving_line = sum(strokes) % 6 or 6
    return {
        "upper_segment": upper_segment,
        "lower_segment": lower_segment,
        "upper_sum": upper_sum,
        "lower_sum": lower_sum,
        "upper_modulo": upper_modulo,
        "lower_modulo": lower_modulo,
        "upper_trigram": upper["name"],
        "upper_symbol": upper["symbol"],
        "lower_trigram": lower["name"],
        "lower_symbol": lower["symbol"],
        "hexagram_number": hexagram["number"],
        "hexagram_name": hexagram["name"],
        "moving_line": moving_line,
    }


def _parity_score(strokes: list[int]) -> dict:
    odd = sum(1 for value in strokes if value % 2)
    even = len(strokes) - odd
    if not strokes:
        raise ValidationError("cannot score parity without strokes")
    minority_ratio = min(odd, even) / len(strokes)
    if minority_ratio >= 0.5:
        score = 100.0
    elif minority_ratio >= 0.25:
        score = 75.0
    else:
        score = 40.0
    return {"odd": odd, "even": even, "score": score}


def _mechanical_analysis(request: dict) -> dict:
    original_segment = request["scored_segment"]
    available_characters = (
        load_character_data().keys() | request.get("stroke_overrides", {}).keys()
    )
    ignored_characters = [
        character
        for character in original_segment
        if character not in available_characters
    ]
    invalid_characters = [
        character
        for character in ignored_characters
        if not (character.isascii() and (character.isalnum() or character in " -_.&+"))
    ]
    if invalid_characters:
        raise UnsupportedCharacterError(
            f"unsupported character {invalid_characters[0]!r}; "
            "provide stroke_overrides with a source"
        )
    segment = "".join(
        character for character in original_segment if character in available_characters
    )
    if not segment:
        return {
            "applicable": False,
            "hexagram_applicable": False,
            "reason": "No Chinese ideographs with stroke data were found.",
            "ignored_characters": ignored_characters,
            "data_metadata": character_data_metadata(),
            "character_analysis": [],
            "current": None,
            "traditional": None,
            "numerology": None,
            "parity_score": None,
            "ambiguous_character_count": 0,
        }
    mechanical_request = copy.deepcopy(request)
    if segment != original_segment:
        mechanical_request["scored_segment"] = segment
        filtered_distinctive = "".join(
            character
            for character in request["distinctive_segment"]
            if character in available_characters
        )
        mechanical_request["distinctive_segment"] = filtered_distinctive or segment
        mechanical_request.pop("brand_prefix", None)
    analyses, current_strokes, traditional_strokes, traditional_text = (
        _analyze_characters(segment, mechanical_request)
    )
    upper_segment, lower_segment = _split_segments(segment, mechanical_request)
    traditional_upper = traditional_text[: len(upper_segment)]
    traditional_lower = traditional_text[len(upper_segment) :]
    distinctive_length = len(mechanical_request["distinctive_segment"])
    hexagram_applicable = bool(upper_segment and lower_segment)

    current_full = _numerology_fact(sum(current_strokes))
    traditional_full = _numerology_fact(sum(traditional_strokes))
    current_distinctive = _numerology_fact(sum(current_strokes[-distinctive_length:]))
    traditional_distinctive = _numerology_fact(
        sum(traditional_strokes[-distinctive_length:])
    )
    full_blend = current_full["score"] * 0.6 + traditional_full["score"] * 0.4
    distinctive_blend = (
        current_distinctive["score"] * 0.6 + traditional_distinctive["score"] * 0.4
    )
    uses_distinctive_weighting = mechanical_request["distinctive_segment"] != segment
    if uses_distinctive_weighting:
        numerology_score = full_blend * 0.4 + distinctive_blend * 0.6
    else:
        numerology_score = full_blend

    current_parity = _parity_score(current_strokes)
    traditional_parity = _parity_score(traditional_strokes)
    parity_score = current_parity["score"] * 0.6 + traditional_parity["score"] * 0.4
    ambiguous_count = sum(
        1
        for item in analyses
        if len(item["current_strokes"]) > 1
        or len(item["traditional_variants"]) > 1
        or any(len(option["strokes"]) > 1 for option in item["traditional_variants"])
    )

    return {
        "applicable": True,
        "hexagram_applicable": hexagram_applicable,
        "ignored_characters": ignored_characters,
        "data_metadata": character_data_metadata(),
        "character_analysis": analyses,
        "current": {
            "text": segment,
            "strokes": current_strokes,
            "full_total": sum(current_strokes),
            "distinctive_total": sum(current_strokes[-distinctive_length:]),
            "parity": current_parity,
            "hexagram": (
                _hexagram_fact(upper_segment, lower_segment, current_strokes)
                if hexagram_applicable
                else None
            ),
        },
        "traditional": {
            "text": traditional_text,
            "strokes": traditional_strokes,
            "full_total": sum(traditional_strokes),
            "distinctive_total": sum(traditional_strokes[-distinctive_length:]),
            "parity": traditional_parity,
            "hexagram": (
                _hexagram_fact(
                    traditional_upper,
                    traditional_lower,
                    traditional_strokes,
                )
                if hexagram_applicable
                else None
            ),
        },
        "numerology": {
            "score": round(numerology_score, 2),
            "uses_distinctive_weighting": uses_distinctive_weighting,
            "weights": {
                "full_name": 0.4 if uses_distinctive_weighting else 1.0,
                "distinctive_segment": 0.6 if uses_distinctive_weighting else 0.0,
                "current_glyph": 0.6,
                "traditional_variant": 0.4,
            },
            "current_full": current_full,
            "traditional_full": traditional_full,
            "current_distinctive": current_distinctive,
            "traditional_distinctive": traditional_distinctive,
        },
        "parity_score": round(parity_score, 2),
        "ambiguous_character_count": ambiguous_count,
    }


def _initial_evidence_gaps(request: dict, mechanical: dict) -> list[str]:
    gaps: list[str] = []
    if not mechanical["applicable"]:
        gaps.append(
            "Chinese mechanical dimensions are unavailable; "
            "numerology, yin-yang/five-elements, and hexagram dimensions are omitted"
        )
    elif not mechanical["hexagram_applicable"]:
        gaps.append(
            "The scored Chinese segment has fewer than two characters; "
            "the hexagram dimension is omitted"
        )
    if mechanical.get("ignored_characters"):
        gaps.append(
            "Non-Chinese market-facing characters were excluded from stroke calculations: "
            + "".join(mechanical["ignored_characters"])
        )
    if not request.get("industries"):
        gaps.append("industries is missing; industry-positioning judgment is omitted")
    company = request.get("company") or {}
    if company.get("established_on") and not company.get("established_at"):
        gaps.append(
            "company.established_at is missing; establishment timing modifier is omitted"
        )
    representative = request.get("legal_representative") or {}
    if representative:
        for field in ("birth_date", "birth_time"):
            if not representative.get(field):
                gaps.append(
                    f"legal_representative.{field} is missing; BaZi modifier is omitted"
                )
    return gaps


def prepare_evaluation(raw_request: dict) -> dict:
    """Validate a request and produce deterministic facts plus a judgment template."""
    request = _validate_request(raw_request)
    mechanical = _mechanical_analysis(request)
    return {
        "schema_version": "1.0",
        "stage": "prepared",
        "request": request,
        "mechanical": mechanical,
        "judgments": {key: None for key in JUDGMENT_KEYS},
        "evidence_gaps": _initial_evidence_gaps(request, mechanical),
    }


def _validate_evidence(evidence: Any, field: str) -> list[dict]:
    if not isinstance(evidence, list) or not evidence:
        raise ValidationError(f"{field}.evidence must be a non-empty array")
    validated: list[dict] = []
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            raise ValidationError(f"{field}.evidence[{index}] must be an object")
        evidence_type = item.get("type")
        if evidence_type not in EVIDENCE_TYPES:
            raise ValidationError(f"{field}.evidence[{index}].type is invalid")
        _validate_string(item.get("claim"), f"{field}.evidence[{index}].claim")
        if evidence_type != "model_judgment":
            _validate_string(item.get("source"), f"{field}.evidence[{index}].source")
        validated.append(copy.deepcopy(item))
    return validated


def _validate_judgment(value: Any, field: str) -> dict:
    if not isinstance(value, dict):
        raise ValidationError(f"judgments.{field} must be an object")
    score = value.get("score")
    if (
        not isinstance(score, (int, float))
        or isinstance(score, bool)
        or not 0 <= score <= 100
    ):
        raise ValidationError(f"judgments.{field}.score must be between 0 and 100")
    rationale = _validate_string(value.get("rationale"), f"judgments.{field}.rationale")
    uncertainty = value.get("uncertainty")
    if uncertainty not in {"low", "medium", "high"}:
        raise ValidationError(
            f"judgments.{field}.uncertainty must be low, medium, or high"
        )
    return {
        "score": float(score),
        "rationale": rationale,
        "uncertainty": uncertainty,
        "evidence": _validate_evidence(value.get("evidence"), f"judgments.{field}"),
    }


def _modifier(
    completed: dict,
    name: str,
    bound: int,
    prerequisites_met: bool,
    missing_reason: str,
) -> tuple[dict, str | None]:
    raw_modifier = (completed.get("context_modifiers") or {}).get(name)
    if raw_modifier is not None:
        if not isinstance(raw_modifier, dict):
            raise ValidationError(f"context_modifiers.{name} must be an object")
        value = raw_modifier.get("value")
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not -bound <= value <= bound
        ):
            raise ValidationError(
                f"context_modifiers.{name}.value must be between {-bound} and {bound}"
            )
        rationale = _validate_string(
            raw_modifier.get("rationale"),
            f"context_modifiers.{name}.rationale",
        )
        evidence = _validate_evidence(
            raw_modifier.get("evidence"), f"context_modifiers.{name}"
        )
        if value != 0 and not any(
            item["type"] != "model_judgment" and item.get("source") for item in evidence
        ):
            raise ValidationError(
                f"context_modifiers.{name} requires an auditable sourced calculation"
            )
        if not prerequisites_met and value != 0:
            raise ValidationError(
                f"context_modifiers.{name} cannot be applied because required source data is incomplete"
            )
        return {
            "applied": bool(prerequisites_met and value != 0),
            "value": float(value) if prerequisites_met else 0.0,
            "rationale": rationale if prerequisites_met else missing_reason,
            "evidence": evidence if prerequisites_met else [],
        }, None if prerequisites_met else missing_reason
    return {
        "applied": False,
        "value": 0.0,
        "rationale": missing_reason
        if not prerequisites_met
        else "No contextual modifier was supplied.",
        "evidence": [],
    }, missing_reason if not prerequisites_met else None


def _round_half_up(value: float) -> int:
    return int(Decimal(str(value)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _score_band(score: int) -> str:
    if score >= 90:
        return "卓越"
    if score >= 80:
        return "优秀"
    if score >= 70:
        return "良好"
    if score >= 60:
        return "中性"
    return "谨慎"


def score_evaluation(completed: dict) -> dict:
    """Validate qualitative judgments and return a deterministic final score."""
    if not isinstance(completed, dict) or completed.get("stage") != "prepared":
        raise ValidationError("score input must be prepared evaluation data")
    request = _validate_request(completed.get("request") or {})
    mechanical = _mechanical_analysis(request)
    raw_judgments = completed.get("judgments")
    if not isinstance(raw_judgments, dict):
        raise ValidationError("judgments must be an object")

    applicable = {
        "industry_positioning": bool(
            request.get("industries") or request.get("positioning")
        ),
        "brand_synergy": bool(
            request.get("parent_company")
            or request.get("parent_brand")
            or request.get("brand_prefix")
        ),
    }
    needed = {"meaning_allusion", "sound_form"}
    if mechanical.get("applicable"):
        needed.add("five_elements")
    if mechanical.get("hexagram_applicable"):
        needed.add("hexagram")
    if applicable["industry_positioning"]:
        needed.add("industry_positioning")
    if applicable["brand_synergy"]:
        needed.add("brand_synergy")
    judgments: dict[str, dict] = {}
    for key in sorted(needed):
        if raw_judgments.get(key) is None:
            raise ValidationError(f"judgments.{key} is required")
        judgments[key] = _validate_judgment(raw_judgments[key], key)

    dimension_scores: dict[str, float] = {
        "meaning_allusion": judgments["meaning_allusion"]["score"],
        "sound_form": judgments["sound_form"]["score"],
    }
    if mechanical.get("applicable"):
        dimension_scores["commercial_numerology"] = float(
            mechanical["numerology"]["score"]
        )
        dimension_scores["yin_yang_five_elements"] = round(
            float(mechanical["parity_score"]) * 0.4
            + judgments["five_elements"]["score"] * 0.6,
            4,
        )
    if mechanical.get("hexagram_applicable"):
        dimension_scores["hexagram"] = judgments["hexagram"]["score"]
    if applicable["industry_positioning"]:
        dimension_scores["industry_positioning"] = judgments["industry_positioning"][
            "score"
        ]
    if applicable["brand_synergy"]:
        dimension_scores["brand_synergy"] = judgments["brand_synergy"]["score"]

    available_weight = sum(DIMENSION_CONFIG[key]["weight"] for key in dimension_scores)
    dimensions: list[dict] = []
    base_score = 0.0
    for key in DIMENSION_CONFIG:
        if key not in dimension_scores:
            continue
        normalized_weight = DIMENSION_CONFIG[key]["weight"] / available_weight * 100
        contribution = dimension_scores[key] * normalized_weight / 100
        base_score += contribution
        dimensions.append(
            {
                "key": key,
                "label": DIMENSION_CONFIG[key]["label"],
                "score": round(dimension_scores[key], 2),
                "configured_weight": DIMENSION_CONFIG[key]["weight"],
                "normalized_weight": round(normalized_weight, 4),
                "contribution": round(contribution, 4),
            }
        )

    company = request.get("company") or {}
    representative = request.get("legal_representative") or {}
    establishment_complete = all(
        company.get(field) for field in ("established_on", "established_at", "location")
    )
    bazi_complete = all(
        representative.get(field)
        for field in (
            "gender",
            "birth_date",
            "birth_time",
            "birthplace",
            "calendar",
        )
    )
    establishment_modifier, establishment_gap = _modifier(
        completed,
        "establishment_timing",
        3,
        establishment_complete,
        "Complete company establishment date, time, and location are unavailable.",
    )
    bazi_modifier, bazi_gap = _modifier(
        completed,
        "legal_representative_bazi",
        4,
        bazi_complete,
        "Complete legal representative birth date, time, calendar, gender, and birthplace are unavailable.",
    )
    modifiers = {
        "establishment_timing": establishment_modifier,
        "legal_representative_bazi": bazi_modifier,
    }
    exact_score = max(
        0.0,
        min(
            100.0,
            base_score + establishment_modifier["value"] + bazi_modifier["value"],
        ),
    )
    rounded_score = _round_half_up(exact_score)

    evidence_gaps = _initial_evidence_gaps(request, mechanical)
    for gap in completed.get("evidence_gaps") or []:
        if isinstance(gap, str) and gap not in evidence_gaps:
            evidence_gaps.append(gap)
    if establishment_gap and not any(
        "establishment" in gap.lower() for gap in evidence_gaps
    ):
        evidence_gaps.append(establishment_gap)
    if bazi_gap and not any("bazi" in gap.lower() for gap in evidence_gaps):
        evidence_gaps.append(bazi_gap)
    uncertainties = [judgment["uncertainty"] for judgment in judgments.values()]
    confidence_points = 100 - min(30, len(evidence_gaps) * 5)
    if not mechanical.get("applicable"):
        confidence_points -= 20
    confidence_points -= uncertainties.count("medium") * 3
    confidence_points -= uncertainties.count("high") * 7
    if confidence_points >= 85:
        confidence = "高"
    elif confidence_points >= 65:
        confidence = "中"
    else:
        confidence = "低"
    sensitivity_margin = min(
        10,
        max(
            1,
            uncertainties.count("medium")
            + uncertainties.count("high") * 2
            + int(mechanical.get("ambiguous_character_count", 0)),
        ),
    )

    ranked = sorted(dimensions, key=lambda item: (-item["score"], item["key"]))
    strengths = [item["label"] for item in ranked[:2]]
    risks = [
        item["label"] for item in sorted(dimensions, key=lambda item: item["score"])[:2]
    ]
    suggestions = [
        f"优先复核{label}维度的低分原因，并比较候选名称。" for label in risks
    ]
    if evidence_gaps:
        suggestions.append("补齐证据缺口后重新评估，并比较分数及敏感性区间是否稳定。")

    return {
        "schema_version": "1.0",
        "stage": "scored",
        "name": request["name"],
        "scored_segment": request["scored_segment"],
        "object_type": request["object_type"],
        "score": rounded_score,
        "exact_score": round(exact_score, 4),
        "band": _score_band(rounded_score),
        "confidence": confidence,
        "confidence_points": confidence_points,
        "sensitivity_interval": {
            "minimum": max(0, rounded_score - sensitivity_margin),
            "maximum": min(100, rounded_score + sensitivity_margin),
        },
        "dimensions": dimensions,
        "modifiers": modifiers,
        "mechanical": copy.deepcopy(mechanical),
        "judgments": judgments,
        "evidence_gaps": evidence_gaps,
        "strengths": strengths,
        "risks": risks,
        "suggestions": suggestions,
        "disclaimer": "本结果属于可解释的传统文化命名模型，不构成经营、投资、法律或科学结论。",
    }


def _escape_markdown(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(result: dict) -> str:
    """Render a scored result as a stable Chinese Markdown report."""
    if not isinstance(result, dict) or result.get("stage") != "scored":
        raise ValidationError("render_markdown requires scored evaluation data")
    mechanical = result["mechanical"]
    evidence_groups: dict[str, list[dict]] = {
        "source_fact": [],
        "traditional_rule": [],
        "model_judgment": [],
    }
    for judgment in result["judgments"].values():
        for evidence in judgment["evidence"]:
            if evidence["type"] in {"lexical_source", "classical_source"}:
                evidence_groups["source_fact"].append(evidence)
            elif evidence["type"] == "traditional_rule":
                evidence_groups["traditional_rule"].append(evidence)
            else:
                evidence_groups["model_judgment"].append(evidence)
    lines = [
        "# 易乾坤名称综合评估",
        "",
        f"- 名称：{result['name']}",
        f"- 实际评分片段：{result['scored_segment']}",
        f"- 对象类型：{result['object_type']}",
        "",
        "## 综合结论",
        "",
        f"**{result['score']} 分｜{result['band']}｜置信度 {result['confidence']}**",
        "",
        f"敏感性区间：{result['sensitivity_interval']['minimum']}～{result['sensitivity_interval']['maximum']} 分。",
        "",
        "## 评分明细",
        "",
        "| 维度 | 原始分 | 归一化权重 | 加权贡献 |",
        "|---|---:|---:|---:|",
    ]
    for dimension in result["dimensions"]:
        lines.append(
            f"| {dimension['label']} | {dimension['score']:.2f} | "
            f"{dimension['normalized_weight']:.2f}% | "
            f"{dimension['contribution']:.2f} |"
        )
    lines.extend(["", "## 数据事实", ""])
    if mechanical["applicable"]:
        current = mechanical["current"]
        traditional = mechanical["traditional"]
        lines.extend(
            [
                f"- 当前字形：{current['text']}；笔画 {current['strokes']}；合计 {current['full_total']}。",
                f"- 传统字形：{traditional['text']}；笔画 {traditional['strokes']}；合计 {traditional['full_total']}。",
                f"- 字形数据版本：Unicode Unihan {mechanical['data_metadata']['unicode_version']}。",
            ]
        )
    else:
        lines.append("- 名称没有可用于中文笔画计算的汉字，机械维度未适用。")
    for evidence in evidence_groups["source_fact"]:
        lines.append(
            f"- {_escape_markdown(evidence['claim'])}"
            f"（来源：[{_escape_markdown(evidence['source'])}]"
            f"({evidence['source']})）。"
        )
    lines.extend(["", "## 传统规则解释", ""])
    if mechanical["applicable"]:
        current = mechanical["current"]
        traditional = mechanical["traditional"]
        numerology = mechanical["numerology"]
        lines.append(
            f"- 商业数理综合分：{numerology['score']:.2f}；"
            f"当前全名数 {numerology['current_full']['number']}，"
            f"传统全名数 {numerology['traditional_full']['number']}，"
            f"当前区别词数 {numerology['current_distinctive']['number']}，"
            f"传统区别词数 {numerology['traditional_distinctive']['number']}。"
        )
        if mechanical["hexagram_applicable"]:
            lines.extend(
                [
                    (
                        f"- 当前卦象：{current['hexagram']['upper_trigram']}上"
                        f"{current['hexagram']['lower_trigram']}下，"
                        f"第 {current['hexagram']['hexagram_number']} 卦"
                        f"《{current['hexagram']['hexagram_name']}》，"
                        f"动爻 {current['hexagram']['moving_line']}。"
                    ),
                    (
                        f"- 传统卦象：{traditional['hexagram']['upper_trigram']}上"
                        f"{traditional['hexagram']['lower_trigram']}下，"
                        f"第 {traditional['hexagram']['hexagram_number']} 卦"
                        f"《{traditional['hexagram']['hexagram_name']}》，"
                        f"动爻 {traditional['hexagram']['moving_line']}。"
                    ),
                ]
            )
        else:
            lines.append("- 单字评分片段无法分出上下卦，卦象维度未适用。")
    else:
        lines.append("- 中文数理、阴阳五行和卦象规则均未适用。")
    for evidence in evidence_groups["traditional_rule"]:
        lines.append(
            f"- {_escape_markdown(evidence['claim'])}"
            f"（规则来源：[{_escape_markdown(evidence['source'])}]"
            f"({evidence['source']})）。"
        )
    lines.extend(["", "## 模型判断", ""])
    labels = {
        "five_elements": "五行适配",
        "hexagram": "卦象综合",
        "meaning_allusion": "字义与典故",
        "industry_positioning": "行业与定位",
        "sound_form": "音形传播",
        "brand_synergy": "母品牌协同",
    }
    for key, judgment in result["judgments"].items():
        lines.append(
            f"- **{labels[key]} {judgment['score']:.0f} 分：** "
            f"{_escape_markdown(judgment['rationale'])}"
        )
    for evidence in evidence_groups["model_judgment"]:
        lines.append(f"- 判断依据：{_escape_markdown(evidence['claim'])}")
    lines.extend(["", "## 可选修正", ""])
    for key, modifier in result["modifiers"].items():
        status = "已应用" if modifier["applied"] else "未应用"
        lines.append(
            f"- {key}：{status}，{modifier['value']:+.1f}；"
            f"{_escape_markdown(modifier['rationale'])}"
        )
        for evidence in modifier["evidence"]:
            if evidence.get("source"):
                lines.append(
                    f"  - 依据：{_escape_markdown(evidence['claim'])}"
                    f"（[{_escape_markdown(evidence['source'])}]"
                    f"({evidence['source']}))"
                )
            else:
                lines.append(f"  - 依据：{_escape_markdown(evidence['claim'])}")
    lines.extend(
        [
            "",
            "## 优势与风险",
            "",
            f"- 优势维度：{'、'.join(result['strengths'])}。",
            f"- 优先复核：{'、'.join(result['risks'])}。",
            "",
            "## 建议",
            "",
        ]
    )
    lines.extend(f"- {suggestion}" for suggestion in result["suggestions"])
    lines.extend(["", "## 证据缺口", ""])
    if result["evidence_gaps"]:
        lines.extend(f"- {_escape_markdown(gap)}" for gap in result["evidence_gaps"])
    else:
        lines.append("- 无已识别的关键证据缺口。")
    lines.extend(
        [
            "",
            "## 使用边界",
            "",
            result["disclaimer"],
            "",
        ]
    )
    return "\n".join(lines)
