# Qualitative scoring rubric

Complete each applicable judgment with:

```json
{
  "score": 82,
  "rationale": "One concise explanation tied to the rubric.",
  "uncertainty": "low",
  "evidence": [
    {
      "type": "model_judgment",
      "claim": "The name clearly signals a technical product."
    }
  ]
}
```

Allowed evidence types are `lexical_source`, `classical_source`, `traditional_rule`, and `model_judgment`. Every type except `model_judgment` requires `source`.

## Shared bands

| Score | Meaning |
|---:|---|
| 95-100 | Exceptional direct fit, strong positive evidence, no material conflict |
| 85-94 | Strong fit with only a minor limitation |
| 75-84 | Good and usable, with one clear caveat |
| 65-74 | More positive than negative but materially mixed |
| 50-64 | Neutral or highly ambiguous |
| 30-49 | Material conflict, adverse ambiguity, or weak fit |
| 0-29 | Strong conflict or serious naming risk |

Use the center of a band by default. Move toward a boundary only when the evidence distinguishes it. Repeated evaluations with the same evidence should use the same integer.

## Five elements

Evaluate internal element flow and compatibility with the supplied industries and positioning. A dual-industry name must support both unless the user states a priority. Treat unclear character-element attribution as uncertainty, not as a negative fact.

## Hexagram

Use only the prepared current/traditional trigram, hexagram, and moving-line facts. Score the overall pattern: favorable and coherent patterns are high; contradictory current/traditional paths are mixed; severe obstruction or mismatch is low. State which path drives the conclusion.

## Meaning and allusion

Assess literal meaning, compound meaning, cultural allusion, auspicious imagery, negative homophones, and misleading or sensitive associations. A claimed dictionary meaning or classical title requires a direct source. Original business interpretation is a `model_judgment`.

## Industry and positioning

Assess whether a customer can plausibly connect the name to every supplied industry, product function, audience, and desired brand trait. Do not award a high score for generic positivity without business relevance.

## Sound, form, and communication

Assess pronunciation, rhythm, repeated-character clarity, visual balance, memorability, likely misreading, typing, and spoken transmission. Trademark availability, domain availability, and search competition are outside this score unless separately researched.

## Parent-brand synergy

Assess family prefix continuity, distinctiveness of the product term, hierarchy clarity, and whether the candidate can stand alone without losing the parent association. Omit this judgment when no parent brand or family prefix exists.

## Uncertainty

- `low`: direct evidence and little interpretive variation.
- `medium`: one meaningful ambiguity or competing interpretation.
- `high`: sparse evidence, disputed character data, or a conclusion likely to change after clarification.

Never use uncertainty to manipulate the score; it changes confidence and sensitivity, not the qualitative judgment's direction.
