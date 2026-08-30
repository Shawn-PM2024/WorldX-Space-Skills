---
name: yi-cosmos-name-evaluator
description: Use when users ask to evaluate, compare, 测算, or 打分 company, brand, or product names with 易学、周易、商业取名、公司起名、81数理、五行、卦象、行业契合 or optional 法人八字 context.
---

# Yi Cosmos Name Evaluator

## Purpose

Produce a reproducible 0-100 cultural naming assessment with visible calculations, evidence, uncertainty, and actionable risks. Treat the result as a decision aid, never as scientific fact or a substitute for trademark, legal, market, or financial review.

## Workflow

1. Gather `name` and `object_type` (`company`, `brand`, or `product`). Ask for the actual `scored_segment` before evaluating a full legal company name. Capture industry, positioning, brand prefix, distinctive segment, parent brand, and optional timing or representative data when available.
2. Work in a temporary directory unless the user requests saved artifacts. From this skill directory run:

   ```bash
   python3 scripts/evaluate_name.py prepare --input request.json --output prepared.json
   ```

3. Read [references/scoring-rubric.md](references/scoring-rubric.md). Complete only applicable judgment slots. Every slot needs a score, rationale, uncertainty, and evidence; factual meanings or classical allusions require a source.
4. Run:

   ```bash
   python3 scripts/evaluate_name.py score --input completed.json --format markdown
   ```

5. Check the output against [references/report-contract.md](references/report-contract.md), then deliver the report. For calculation rules, ambiguous characters, segmentation, or optional context modifiers, read [references/methodology.md](references/methodology.md).

## Invariants

- Never invent birth data, establishment time, character variants, strokes, sources, or favorable elements.
- Keep source facts, traditional-rule interpretations, and model judgments separate.
- Use all stroke alternatives or a sourced override; never substitute a similar-looking character.
- Do not apply BaZi or establishment modifiers without complete enough raw data and an auditable calculation source or method.
- Omit inapplicable dimensions and retain the reported confidence and sensitivity interval.
- Do not alter weights, tables, or rubric bands for a desired name outcome.
- When comparing candidates, use identical inputs, segmentation rules, and evidence standards.
