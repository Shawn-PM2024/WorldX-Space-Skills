---
name: practical-ppt
description: Use when the user needs to turn an outline, article, markdown draft, meeting notes, or structured business/technology content into a polished, readable, editable PPTX deck; also use when they ask for PPT style learning, HTML-to-PPT workflow, user-template adaptation, benchmark comparison, slide QA, or practical_ppt.
---

# Practical PPT

## Overview

Create high-quality practical PPT decks by turning expert presentation practice into an executable loop: read the source, choose a content/style route, plan proof objects, draw HTML as the visual source, rebuild the deck as editable native PowerPoint objects, run QA, repair, and only then deliver.

Default to a complete deck with a cover slide and an ending slide, even when the user only provides the body outline.

This skill is not a prompt for "make a pretty PPT". It is a workflow package. Keep the center short and use the surrounding files only when needed:

- [references/style-library.md](references/style-library.md): reusable style families and visual grammars.
- [references/proposal-proof-objects.md](references/proposal-proof-objects.md): executive proposal proof-object patterns.
- [references/qa-rubric.md](references/qa-rubric.md): blocking QA gate.
- [references/skill-principles.md](references/skill-principles.md): maintenance principles for evolving this skill.
- `scripts/`: deterministic audit, conversion, and QA helpers. Prefer calling them over re-implementing checks in prose.

## Trigger Discipline

Use this skill when the user wants a PPT/PPTX deliverable, a deck preview, a deck rebuild, a template/style adaptation, or a deck quality audit. Do not use it for ordinary long-form writing, single static images, generic web pages, or data analysis unless the end product is a presentation deck.

If the request is ambiguous, infer the closest deck task and state the assumption. Ask at most one short clarification before visual work when the missing answer materially changes the deck:

- strict outline or expanded content
- target audience and use occasion
- expected page count or time budget
- whether a supplied deck is source content, a style reference, or a benchmark

## Operating Contract

- Default deliverable: editable PPTX with native text, shapes, tables, charts, and lines.
- Default source of visual truth: HTML slides on a 16:9 canvas.
- Default content mode: `strict-outline` when the user supplies an outline and asks for conversion.
- Default required pages: cover and ending slide.
- Default readability floor: normal PPT text at least 12pt; HTML text at least 16px on a 1600x900 canvas.
- Default line spacing: at least single line spacing; prefer 1.15-1.35 for dense Chinese body copy.
- Default QA stance: any text overflow, overlap, illegible small text, broken style frame, unsupported claim, or non-editable core text is blocking until fixed or explicitly accepted by the user.
- Default repair path: revise HTML/spec first, then regenerate PPTX, then rerun checks.

## Execution Loop

Follow this loop. Do not skip the plan, style brief, or QA gates for non-trivial decks.

1. Confirm or infer content mode before visual work.

- `strict-outline`: use only the supplied outline and rewrite/compress it for slides.
- `expanded-content`: enrich the outline with reasonable framing, transitions, examples, and supporting material. When current facts, examples, or citations matter, use Codex's local/web search capability and keep source notes.
- If the user asks to convert a supplied outline directly, default to `strict-outline` and report that assumption.

2. Choose the style mode.

- `style-library`: no user template is supplied. Select a template type from [references/style-library.md](references/style-library.md), then adapt it to the deck's topic and audience.
- `参考用户模版` / `user-template`: the user supplies a PPTX/PDF/image/template deck as the style reference. Audit it before drawing any new slide, then adapt its visual grammar to the new topic.
- `benchmark-compare`: the user supplies another deck for the same or similar input and asks why it is better/worse. Audit both decks before rebuilding, then write a gap brief.
- If the user supplies a template-like PPTX and asks to use it as a reference, default to `user-template`.

For `user-template` mode:

- First run or manually perform a template audit: slide size, page count, color palette, fonts, title/body scale, recurring chrome, layout motifs, media style, diagram grammar, density, and what not to copy.
- Prefer the bundled audit helper when working with PPTX:

```bash
python3 scripts/audit_pptx_template.py reference-template.pptx --out template-audit
```

- Write a `template-style-brief.md` before creating the new deck. It must include: reusable grammar, adaptation for the new topic, content fit risks, and explicit non-copy rules.
- Do not paste the user's template content into the new deck unless it is also source content. Learn style, not content.
- Preserve editability. Recreate learned layouts with native PowerPoint text/shapes whenever possible.

For `benchmark-compare` mode:

- Run text QA and structure QA on both decks when files are available.
- Compare narrative spine, proof-object choice, layout rhythm, visual assets, text density, readability, and editability.
- Write `benchmark-gap-brief.md` before making a new version. Separate style gaps from story/proof-object gaps.
- Use [references/proposal-proof-objects.md](references/proposal-proof-objects.md) for executive, strategy, shareholder, financing, and joint-venture decks.

3. Build the slide plan.

- Convert the outline into a slide list with one claim or job per slide.
- Add `封面` and `结束页`.
- Mark each slide as narrative, data/table, diagram/process, product/solution, case, comparison, or transition.
- Choose one named proof object for each substantial slide before drawing: funnel, matrix, role swimlane, revenue stack, ownership donut, IP quadrant, timeline, checklist table, decision bridge, or another explicit object.
- Create a small style brief naming: topic, audience, selected reference grammar, deliberate modifications, and what must not be copied.
- Maintain a trace table: source outline item -> slide number -> treatment (`kept`, `merged`, `split`, `expanded`, or `omitted-with-reason`).
- Avoid more than 3 consecutive body slides with the same table/card/list layout. Vary the proof object shape so the contact sheet has visible rhythm.

4. Draw the deck as a webpage.

- Use a 16:9 slide canvas by default: `.slide { width: 1600px; height: 900px; }`.
- Put each slide in one `.slide` element. Use semantic headings (`h1`, `h2`) and stable data attributes where useful.
- Keep all reusable theme values in CSS variables: background, text, accent, muted text, border, panel, grid, and chart colors.
- Set body/readable text at no less than 16px in HTML, which maps to roughly 12pt in PPT. Do not solve density problems by shrinking text below this threshold.
- Set paragraph and label line-height to at least `1.0`; prefer `1.15`-`1.35` for body text and dense Chinese paragraphs.
- Favor real layout systems: CSS grid, flex, SVG diagrams, tables, and chart libraries. Avoid decorative clutter that does not clarify the slide.
- Build reusable visual assets as native/vector grammar: dot grids, thin rules, badges, stage labels, dividers, rings, chevrons, ladders, funnels, and schematic icons. Do not rely on flat card grids for every slide.
- Check the HTML in a browser before export. The webpage is the visual source of truth.

5. Build an editable PPTX.

- Default deliverable must use native editable PowerPoint text and shapes. Use a slide-spec JSON and the bundled editable export script when suitable:

```bash
node scripts/spec_to_editable_pptx.mjs deck-spec.json deck.pptx
```

- Use `scripts/html_to_pptx.mjs` only for preview, raster backup, or when the user explicitly accepts image-backed PPTX. Never present image-backed export as the primary editable deliverable.
- If a slide needs visual detail that the spec script cannot express, use the Presentations/artifact-tool workflow or pptxgenjs directly to create editable objects rather than embedding a screenshot.
- In editable exports, normal text must be at least 12pt and line spacing must be at least single. When content does not fit, split the slide, shorten copy, enlarge the container, or change the layout. Do not use PowerPoint auto-shrink as a final fix.

6. Run PPT checks and revise.

- Run `scripts/check_html_slides.mjs` on the HTML source before final export. The default minimum is 16px; do not lower it unless the user explicitly accepts smaller text.
- Run `scripts/check_pptx_text.py` on the final PPTX:

```bash
python3 scripts/check_pptx_text.py deck.pptx --output pptx-text-qa.json --fail-on-review
```

- Run structure QA on the final PPTX:

```bash
python3 scripts/check_pptx_structure.py deck.pptx --output pptx-structure-qa.json --fail-on-review
```

- Inspect a rendered contact sheet before delivery. Automated checks do not replace visual review.
- Verify editability: PPTX should contain real text runs and editable shapes for normal content. Screenshots may be used only for non-editable illustrative media, not core slide text.
- Use [references/qa-rubric.md](references/qa-rubric.md) as the blocking gate. Do not deliver if there are obvious overlap, overflow, style breakage, outline mismatch, or content-reasoning problems.
- Iterate the HTML first, then regenerate PPTX.

7. Package the handoff.

- Return the final PPTX path, HTML preview path, slide spec path, QA report paths, and mode assumptions.
- Mention whether the PPTX is editable and what content, if any, is intentionally image-backed.
- Keep unresolved assumptions short and concrete.

## Design Bar

The deck should match the reference set's practical quality: clear first-read hierarchy, coherent visual system, stable spacing, executive-readable density, and distinct slide rhythms. It should not look like a generic template with swapped text.

Every substantial slide needs:

- a slide-level claim or task
- a proof object: table, diagram, timeline, architecture, case, metric, quote, or structured comparison
- controlled density: readable at presentation size and scannable at contact-sheet size
- enough breathing room for native PPT rendering: text boxes should have vertical slack after line spacing is applied
- distinct visual rhythm: the proof object should be recognizable at thumbnail size, not just as a block of text

## Gotchas

These are failure-derived constraints. Treat them as higher priority than generic design instincts.

- Do not make the whole deck a sequence of card grids. If 3 body slides in a row share the same layout signature, redesign at least one slide.
- Do not copy a template literally. Use its grammar, then adapt colors, motifs, proof objects, and media treatment to the topic.
- Do not shrink text to solve overflow. Split, compress, or change the proof object.
- Do not let decorative images replace proof. Every substantial slide needs a claim and a proof object.
- Do not use full-slide screenshots as the primary PPTX export when the user expects editable slides.
- Do not trust automated checks alone. Contact-sheet inspection is mandatory because style drift and visual rhythm are partly human-judgment problems.
- Do not add unsourced facts in `strict-outline` mode. In `expanded-content` mode, keep source notes when facts matter.
- Do not expose source-template contents in a new deck unless those contents are also part of the user's input.

## Outputs

Return the final PPTX path, the HTML/source preview path if created, the slide-spec path when used, the HTML QA report path, the PPTX text QA report path, and the PPTX structure QA report path. Mention whether the deck used `strict-outline` or `expanded-content`, whether the PPTX is editable, and list any unresolved assumptions or missing source constraints.
