# Evidence-Led Editorial Deck Workflow

Read this reference for conference sharing, exhibition/event recaps, field reports, industry analysis, research trips, photo-led case studies, or any deck where user-owned images are part of the argument.

## Core Contract

Build the story and the evidence chain together:

1. State the slide's judgment.
2. Show the evidence that supports it.
3. Explain what the evidence means.
4. Mark uncertainty instead of hiding it in polished layout.

Photos prove that something was visible or happened. They do not automatically prove market scale, commercial success, technical superiority, or causality.

## Evidence Map

Create an evidence map before visual production. One row per usable asset:

| Field | Required decision |
|---|---|
| Asset | Stable local path, document reference, or source URL |
| Provenance | `现场证据`, `公开资料`, `用户提供`, `生成示意`, or `待确认` |
| Visible fact | What can be read or recognized directly |
| Supported claim | The narrow claim this asset can support |
| Limits | What must not be inferred from it |
| Orientation | Landscape, portrait, square, or detail crop |
| Quality | Native dimensions and whether enlargement remains readable |
| Reuse | Unused, used once, or deliberate second-use detail |
| Target slide | Planned slide number and visual role |

Use source priority in this order:

1. User-owned/local photos, screenshots, and documents.
2. Authoritative external sources with a visible citation or provenance label.
3. Generated/illustrative media for concepts, atmosphere, or transitions only.

Do not convert filename assumptions into facts. Inspect the visible content, especially signs, product labels, and company names.

## Narrative Pairing

For evidence-heavy chapters, prefer an argument/evidence pair:

- **Argument page**: one thesis, one framework or comparison, minimal media.
- **Evidence page**: photographs, screenshots, or document excerpts that test the thesis.

The pair may collapse into one slide when the evidence is singular and legible. Do not force a second page merely to follow the pattern.

Use captions to identify what is visible. Use body text to interpret why it matters. Keep caveats near the evidence they qualify.

## Design Lock

Before full production, create `deck-design-lock.md` with:

- canvas and safe margins
- palette and color roles
- title/body/caption font stacks
- icon and diagram policy
- image priority and provenance labels
- image-frame grammar for landscape, portrait, and detail crops
- page chrome and numbering
- slide list with `anchor`, `dense`, or `breathing` rhythm role
- per-slide proof object and layout strategy
- user-template or source-project constraints

The lock is a drift guard, not a large design essay. Re-check it before each slide and update it only when an approved change alters the system.

## Representative Sample Gate

For a complex or visually consequential deck, create 3-4 slides before the full build:

- cover or opening thesis
- claim/narrative page
- dense comparison, process, or diagram page
- evidence/photo page

Render a sample contact sheet and inspect each slide full size. The approval question should cover the whole visual system at once: tone, typography, density, proof objects, image treatment, and editability. Record accepted choices in the design lock and continue without repeatedly reopening settled decisions.

## Page Rhythm

- `anchor`: decisive thesis, chapter opening, or summary. Fewer objects, stronger hierarchy.
- `dense`: structured comparison, matrix, timeline, architecture, or multi-source argument.
- `breathing`: large evidence, quote, transition, or single visual proof.

Avoid long runs of the same role. An evidence-heavy chapter often works as `anchor -> dense -> breathing`, but the content decides the sequence.

## Photo Construction Rules

- Use at most 4 independent evidence units per page by default.
- Prefer 1-3 large, readable images over a dense gallery.
- Match portrait photos to portrait frames and landscape photos to wide frames.
- Crop to strengthen the subject, not to remove material context or signage needed for identification.
- If enlargement exposes blur, reduce the display size, use a detail crop only when it remains truthful, or choose another asset.
- Put labels inside the image only when contrast remains reliable; otherwise use a caption band beside or below it.
- Avoid dark overlays that obscure the product, document, or scene the audience needs to inspect.
- Generated images must not imitate documentary evidence. Keep them on conceptual pages and label them as illustrative when confusion is plausible.

## Existing Deck Updates

When a deck came from an HTML/SVG/spec project, modify that source and regenerate the PPTX. This preserves the deck's type system, notes, page order, and future editability. Direct PPTX surgery is appropriate for isolated changes only when no maintainable source exists.

Before an in-place replacement:

- identify the exact target deck
- preserve a timestamped backup
- render the changed pages before replacement
- verify the final file after replacement

## Visual QA

Review the full contact sheet for narrative and rhythm, then inspect every evidence page full size.

Check:

- each image supports the adjacent claim
- provenance labels are visible and truthful
- subjects, signs, and products remain recognizable
- no stretching, severe crop loss, or low-resolution enlargement
- no accidental image reuse
- captions are readable without competing with the image
- uncertainty is labeled rather than polished away
- the chapter moves from claim to evidence to interpretation
- cover, anchor pages, evidence pages, and closing pages belong to one visual system

Automated checks may catch missing media and font fallback, but they do not replace this review.
