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
- [references/evidence-led-editorial-workflow.md](references/evidence-led-editorial-workflow.md): field-report, conference-sharing, industry-analysis, and photo-evidence workflow.
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
- Default complex-deck gate: for visually consequential, evidence-heavy, or long-form decks, build 3-4 representative slides and obtain direction approval before full production unless the user explicitly asks for uninterrupted one-pass execution.
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
- Compare narrative spine, proof-object choice, layout rhythm, visual assets, media evidence, font system, text density, readability, and editability.
- Render or inspect a contact sheet for both decks. The comparison must mention cover/ending polish, section rhythm, repeated layout signatures, dark/light contrast pages, media/photo/screenshot usage, accent-color hierarchy, and page chrome consistency.
- Write `benchmark-gap-brief.md` before making a new version. Separate style gaps from story/proof-object gaps, and list concrete "keep/change/avoid" rules before rebuilding.
- Use [references/proposal-proof-objects.md](references/proposal-proof-objects.md) for executive, strategy, shareholder, financing, and joint-venture decks.

3. Build the slide plan.

- Convert the outline into a slide list with one claim or job per slide.
- Add `封面` and `结束页`.
- Mark each slide as narrative, data/table, diagram/process, product/solution, case, comparison, or transition.
- Choose one named proof object for each substantial slide before drawing: funnel, matrix, role swimlane, revenue stack, ownership donut, IP quadrant, timeline, checklist table, decision bridge, or another explicit object.
- Create a small style brief naming: topic, audience, selected reference grammar, deliberate modifications, and what must not be copied.
- For Chinese business decks, define the font policy before drawing. Prefer a Chinese UI font stack such as `PingFang SC`, `Microsoft YaHei`, `Noto Sans CJK SC`, or the supplied template's Chinese font. Do not default to Arial/Segoe UI for Chinese-heavy pages unless matching a user template.
- For review, report, product, case, or portfolio decks, define the media/evidence policy: which slides need product screenshots, photos, document snapshots, diagrams, logos supplied by the user, or native schematic stand-ins. A deck with only boxes and text should be treated as incomplete when visual evidence is available.
- For conference sharing, field reports, industry analysis, exhibition/event recaps, or decks built from user photos, read [references/evidence-led-editorial-workflow.md](references/evidence-led-editorial-workflow.md). Build an evidence map before drawing: source, provenance class, claim supported, orientation, reuse status, and target slide.
- Use this evidence priority: user-owned/local evidence first, authoritative external evidence second, generated or illustrative media only for concepts that cannot be shown faithfully. Label `现场证据`, `公开资料`, and `待确认` distinctly; never let layout imply that public material is a user-shot photo.
- Maintain a trace table: source outline item -> slide number -> treatment (`kept`, `merged`, `split`, `expanded`, or `omitted-with-reason`).
- Avoid more than 3 consecutive body slides with the same table/card/list layout. Vary the proof object shape so the contact sheet has visible rhythm.
- Assign every slide one rhythm role: `anchor` for decisive thesis/section pages, `dense` for comparison or structured evidence, and `breathing` for visual proof or transition. The sequence should vary intentionally instead of alternating layouts mechanically.
- Write a compact `deck-design-lock.md` before full production. It must lock canvas, palette, typography, icon policy, image hierarchy, page chrome, rhythm role per slide, and any source/template constraints. Re-check it before authoring each slide so a long deck does not drift after context compression.

4. Pass the representative sample gate when required.

- For complex, visually consequential, evidence-heavy, or long-form decks, build 3-4 representative slides first: normally a cover, a claim/narrative page, a dense diagram/comparison page, and an evidence/photo page.
- Render the sample as a contact sheet and inspect each sample slide at full size. Confirm typography, palette, density, image treatment, proof-object grammar, and editability.
- Present the sample and the recommended direction as one approval point. After approval, lock the accepted decisions in `deck-design-lock.md` and continue without repeated stylistic questions.
- Skip this gate only for narrow edits, simple short decks, strict template fills, or when the user explicitly requests uninterrupted one-pass production.

5. Draw the deck as a webpage.

- Use a 16:9 slide canvas by default: `.slide { width: 1600px; height: 900px; }`.
- Put each slide in one `.slide` element. Use semantic headings (`h1`, `h2`) and stable data attributes where useful.
- Keep all reusable theme values in CSS variables: background, text, accent, muted text, border, panel, grid, and chart colors.
- Set body/readable text at no less than 16px in HTML, which maps to roughly 12pt in PPT. Do not solve density problems by shrinking text below this threshold.
- Set paragraph and label line-height to at least `1.0`; prefer `1.15`-`1.35` for body text and dense Chinese paragraphs.
- Favor real layout systems: CSS grid, flex, SVG diagrams, tables, and chart libraries. Avoid decorative clutter that does not clarify the slide.
- Build reusable visual assets as native/vector grammar: dot grids, thin rules, badges, stage labels, dividers, rings, chevrons, ladders, funnels, and schematic icons. Do not rely on flat card grids for every slide.
- Make cover and ending slides feel intentional, not like body slides with larger text. Use restrained hero spacing, stable brand/project marks when supplied, a single decisive title block, and subtle motif geometry or media.
- Use accent colors as signals. In blue-white business decks, keep deep blue for primary hierarchy, cyan/light blue for structure, and a warm accent such as orange only for milestones, warnings, current-state markers, or key numbers.
- For evidence-led pages, let images prove what happened and let text explain what it means. Use one claim above the evidence, short captions on or beside it, and a restrained interpretation or caveat.
- Keep photo/evidence pages to at most 4 independent visual units by default. Match image orientation to the frame, avoid stretching, and change the layout or crop when the subject becomes too small or blurry. Do not reuse the same photo as evidence on multiple slides unless the second use reveals a different detail.
- Check the HTML in a browser before export. The webpage is the visual source of truth.

6. Build an editable PPTX.

- Default deliverable must use native editable PowerPoint text and shapes. Use a slide-spec JSON and the bundled editable export script when suitable:

```bash
node scripts/spec_to_editable_pptx.mjs deck-spec.json deck.pptx
```

- Use `scripts/html_to_pptx.mjs` only for preview, raster backup, or when the user explicitly accepts image-backed PPTX. Never present image-backed export as the primary editable deliverable.
- If a slide needs visual detail that the spec script cannot express, use the Presentations/artifact-tool workflow or pptxgenjs directly to create editable objects rather than embedding a screenshot.
- In editable exports, normal text must be at least 12pt and line spacing must be at least single. When content does not fit, split the slide, shorten copy, enlarge the container, or change the layout. Do not use PowerPoint auto-shrink as a final fix.

7. Run PPT checks and revise.

- Run `scripts/check_html_slides.mjs` on the HTML source before final export. The default minimum is 16px; do not lower it unless the user explicitly accepts smaller text.
- Run `scripts/check_pptx_text.py` on the final PPTX:

```bash
python3 scripts/check_pptx_text.py deck.pptx --output pptx-text-qa.json --fail-on-review
```

- Run structure QA on the final PPTX:

```bash
python3 scripts/check_pptx_structure.py deck.pptx --output pptx-structure-qa.json --fail-on-review
```

- For Chinese review/report decks where visual evidence matters, add the richer structure checks:

```bash
python3 scripts/check_pptx_structure.py deck.pptx --output pptx-structure-qa.json --min-media-files 1 --warn-ascii-fonts-for-cjk --fail-on-review
```

- Inspect a rendered contact sheet before delivery. Automated checks do not replace visual review.
- Inspect every representative slide and every photo/evidence slide at full size. Check subject recognition, blur after scaling, crop loss, aspect-ratio distortion, duplicate use, caption readability, and provenance labeling.
- Verify editability: PPTX should contain real text runs and editable shapes for normal content. Screenshots may be used only for non-editable illustrative media, not core slide text.
- Verify package integrity, slide count, and speaker-note count when notes are part of the deliverable. If the office-rendered PDF substitutes fonts or loses CJK text, deliver a clearly labeled visual-fidelity preview made from verified slide renders instead of presenting the broken PDF as authoritative.
- Use [references/qa-rubric.md](references/qa-rubric.md) as the blocking gate. Do not deliver if there are obvious overlap, overflow, style breakage, outline mismatch, or content-reasoning problems.
- Iterate the HTML first, then regenerate PPTX.

8. Package the handoff.

- Return the final PPTX path, HTML preview path, slide spec path, QA report paths, and mode assumptions.
- Mention whether the PPTX is editable and what content, if any, is intentionally image-backed.
- Keep unresolved assumptions short and concrete.

## Existing Deck Updates

- Before editing an existing PPTX, inspect whether its HTML, SVG, slide spec, or generator project still exists. When it does, edit the source project and regenerate the deck so typography, notes, layout logic, and future edits stay coherent.
- Use direct PPTX object edits only when the source project is unavailable or the requested change is genuinely local.
- When replacing an existing user file in place, keep a timestamped rollback copy unless the user explicitly declines a backup.

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
- Do not ship Chinese-heavy decks with default Latin UI fonts when the output is meant to look locally polished.
- Do not make review/report decks entirely text-and-shape based when the content naturally has proof photos, screenshots, documents, product images, or user-supplied visual evidence.
- Do not mix user-shot photos, public-source images, generated visuals, and unverified claims without visible provenance distinctions.
- Do not put more than 4 independent evidence units on a photo page by default; split the page or enlarge the strongest evidence.
- Do not proceed from a representative sample to a complex full deck until the sample direction is approved, unless the user explicitly chose uninterrupted one-pass production.
- Do not patch a source-generated deck only at the PPTX layer when the source project is available and the change belongs in that source.
- Do not copy a template literally. Use its grammar, then adapt colors, motifs, proof objects, and media treatment to the topic.
- Do not shrink text to solve overflow. Split, compress, or change the proof object.
- Do not let decorative images replace proof. Every substantial slide needs a claim and a proof object.
- Do not use full-slide screenshots as the primary PPTX export when the user expects editable slides.
- Do not trust automated checks alone. Contact-sheet inspection is mandatory because style drift and visual rhythm are partly human-judgment problems.
- Do not add unsourced facts in `strict-outline` mode. In `expanded-content` mode, keep source notes when facts matter.
- Do not expose source-template contents in a new deck unless those contents are also part of the user's input.

## Outputs

Return the final PPTX path, the HTML/source preview path if created, the slide-spec path when used, the HTML QA report path, the PPTX text QA report path, and the PPTX structure QA report path. Mention whether the deck used `strict-outline` or `expanded-content`, whether the PPTX is editable, and list any unresolved assumptions or missing source constraints.
