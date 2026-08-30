# Methodology

## Status and boundary

This is a transparent synthesis of common Chinese commercial-naming practices. It is calibrated as a cultural model and makes no empirical claim that a name determines business outcomes.

The mechanical stage uses the bundled Unicode 17.0 Unihan extract. Unicode's `kTotalStrokes` and variant fields provide a reproducible glyph-data baseline, not a unique Kangxi naming-school count. See [UAX #38](https://www.unicode.org/reports/tr38/) and [data provenance](data/PROVENANCE.md).

## Input selection

Required fields are `name` and `object_type`.

For a company, the legal full name and the scored trade-name segment are different inputs. Show the proposed segmentation and obtain confirmation rather than silently removing a location, industry descriptor, or legal suffix.

For a product family, use:

- `brand_prefix`: the shared family prefix.
- `distinctive_segment`: the part that differentiates this product.
- `scored_segment`: their complete evaluated combination.

When no semantic segmentation is provided, split a multi-character Chinese segment into two balanced halves for hexagram derivation. A single-character segment has no upper/lower hexagram dimension.

## Character and stroke handling

For every Chinese character:

1. Preserve the market-facing form.
2. Resolve every Unihan traditional variant.
3. Display all stroke alternatives.
4. Use the first ordered variant and smallest stroke value only as the deterministic primary path; add ambiguity to sensitivity.
5. A sourced `stroke_overrides` entry wins and remains visible.

ASCII letters, numbers, spaces, and common brand punctuation are not assigned fictional Chinese strokes. For Latin-only names, omit commercial numerology, yin-yang/five-elements, and hexagram dimensions. For mixed names, calculate the mechanical stage only over Chinese ideographs and disclose the exclusion.

## Commercial numerology

Reduce totals into 1-81 by repeatedly subtracting 80 only while the total is greater than 81. Thus 81 remains 81, 82 becomes 2, and 161 becomes 81.

The model reads `data/numerology-81.json`. Values are model configuration:

- For each segment, current market glyphs contribute 60 percent and traditional variants 40 percent.
- When a distinct product segment exists, its blended number contributes 60 percent and the full name 40 percent.
- Without a distinct segment, the full name contributes 100 percent.

This structure measures both family continuity and the actual differentiating product term. Never change these weights during a comparison.

## Yin-yang and five elements

Stroke parity supplies 40 percent of the dimension:

- Equal odd/even count: 100.
- A one-to-three balance: 75.
- All odd or all even: 40.
- Current glyph parity contributes 60 percent and traditional parity 40 percent.

The evidence-backed `five_elements` judgment supplies the remaining 60 percent. Consider internal flow, character meaning or structure, industry attributes, and the user's intended positioning. Do not assign an element from an opaque online result alone.

## Hexagram derivation

For each current/traditional path:

- Upper trigram = first-segment stroke sum modulo 8.
- Lower trigram = second-segment stroke sum modulo 8.
- Mapping: `1乾, 2兑, 3离, 4震, 5巽, 6坎, 7艮, 0坤`.
- Moving line = full stroke sum modulo 6, with zero mapped to line 6.

Interpret the displayed main hexagram and moving-line context with [the rubric](scoring-rubric.md). For a simplified Chinese market-facing name, give current-glyph interpretation greater relevance while still discussing the traditional sensitivity. Do not turn one favorable phrase into an automatic high score.

## Optional people and timing modifiers

Legal-representative BaZi adjustment is bounded to `-4..4`. It requires gender, birth date, birth time, calendar system, birthplace, and an auditable Four Pillars calculation method or source. Missing time means no modifier.

Establishment timing adjustment is bounded to `-3..3`. It requires establishment date, exact time, location, and an auditable calendrical method or source. A date without a time receives no modifier.

Use `0` for neutral or missing context. Values of absolute 3 or 4 require unusually strong, specific evidence; ordinary compatibility belongs at plus or minus 1 or 2.

## Confidence and sensitivity

Confidence falls with missing context and medium/high-uncertainty judgments. Sensitivity expands when character variants or qualitative uncertainty could reasonably change the result. Do not hide either value when presenting an integer score.
