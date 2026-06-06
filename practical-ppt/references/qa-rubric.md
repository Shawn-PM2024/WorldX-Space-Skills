# Practical PPT QA Rubric

Run this rubric after the HTML deck exists and again after PPTX export.

## 1. Text Quality

Blocking issues:

- text overlaps other text, charts, images, page chrome, or slide edges
- any normal PPT text is below 12pt; in HTML this maps to a default minimum of 16px on a 1600x900 slide canvas
- font-size hierarchy is incoherent: body copy larger than headings, many unrelated sizes, or abrupt jumps without purpose
- line-height is below single spacing, missing on multi-line PPT text boxes, causes clipping, crops descenders, or makes Chinese paragraphs unreadable
- long Chinese/English words overflow buttons, labels, cards, tables, or diagram nodes
- text exceeds its card, table cell, diagram node, callout, or style frame after export to PPTX
- text has insufficient contrast against its actual background, including callouts, dark covers, pale cards, and transparent overlays

Checks:

- inspect screenshots/contact sheet at thumbnail and full size
- run `scripts/check_html_slides.mjs` with the default 16px minimum and at least `--min-line-height 1`
- run `scripts/check_pptx_text.py` on the final PPTX and treat any `review` result as blocking unless manually justified
- run `scripts/check_pptx_structure.py` on the final PPTX for proof-object variety, visual rhythm, and dense-slide review
- manually inspect text/background contrast because automated geometry checks may not catch white-on-white or low-contrast text
- manually review slides with dense tables, timelines, org charts, and multi-column text

## 2. Editability

Blocking issues:

- normal slide text is embedded only in screenshots or raster images
- titles, body copy, tables, and diagram labels cannot be selected and edited in PowerPoint
- the PPTX contains no meaningful text runs in `ppt/slides/slide*.xml`
- core diagrams are flattened into images when they could be native shapes, lines, and text

Checks:

- inspect the PPTX in PowerPoint/Keynote when available
- run an XML check: unzip the PPTX and confirm slide XML contains expected text
- run `scripts/check_pptx_text.py deck.pptx --fail-on-review` to catch font sizes below 12pt, missing or below-single line spacing, estimated text overflow, out-of-bounds text boxes, and likely text box overlaps
- treat image-backed PPTX as preview/backup only unless the user explicitly requested visual-only export

## 3. Style Integrity

Blocking issues:

- elements fall outside the slide canvas or are cropped by the PPT boundary
- repeated chrome changes position unexpectedly
- colors, shadows, border radii, icon styles, or diagram styles drift without chapter-level reason
- imported images are blurry, stretched, darkened excessively, or visually unrelated
- cover, section, body, and ending pages do not feel like the same deck
- most body slides use the same table/card/list grammar, making the deck fail the contact-sheet rhythm test
- substantial slides contain no recognizable proof object beyond text boxes
- in `user-template` mode, the output either copies the template content too literally or fails to preserve the template's visual grammar

Checks:

- compare contact sheet rhythm against the selected style family in `style-library.md`
- compare against the style brief: the deck should adapt reference grammar to the topic, not imitate a reference page literally
- in `user-template` mode, compare against `template-style-brief.md` and verify palette, typography scale, spacing, motif, density, and page rhythm were learned before generation
- verify each slide has stable margins and alignment
- confirm charts, tables, diagrams, and cards share a consistent grammar
- confirm each substantial slide has a named proof object and that no more than 3 consecutive body slides share the same layout signature

## 4. Outline Match

Blocking issues:

- required outline items are missing
- slide order changes the user's intended logic without explanation
- added content in `strict-outline` mode introduces unsupported claims
- `expanded-content` mode adds examples or facts without source notes when sources matter

Checks:

- maintain a slide-plan table: outline item -> slide number -> treatment
- state whether the final deck used `strict-outline` or `expanded-content`
- mark any merged, split, or reordered outline items

## 5. Content Reasonableness

Blocking issues:

- a slide has only decorative text and no useful claim, proof object, or decision value
- claims are stronger than the evidence shown
- data labels, units, dates, company names, or technical terms are inconsistent
- diagrams look plausible but do not explain a real relationship
- AI-generated filler replaces the user's actual point

Checks:

- each slide should answer: "What should the audience understand or decide after this page?"
- each proof object should support the slide claim directly
- for current or factual claims, keep source notes and avoid invented metrics

## QA Report Format

Use this concise format in the final QA note:

```markdown
## PPT QA
- Text: pass / issues found
- Editability: pass / issues found
- Style: pass / issues found
- Outline match: pass / issues found
- Content reasonableness: pass / issues found
- Fixes made: ...
- Remaining assumptions: ...
- HTML QA: report path + pass/review count
- PPTX text QA: report path + pass/review count
- PPTX structure QA: report path + pass/review count
```
