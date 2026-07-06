# Changelog

All notable changes to Practical PPT are documented here.

## 1.0.5 - 2026-07-06

- Added a Blue-Orange Performance Review style family for Chinese semiannual/annual review and 述职 decks, including Chinese font policy, evidence-media treatment, cover/ending rhythm, and blue/cyan/orange hierarchy rules.
- Tightened benchmark comparison guidance so agents must inspect rendered contact sheets and compare media evidence, font system, cover/ending polish, accent hierarchy, and repeated layout signatures before rebuilding.
- Expanded QA blocking rules for Chinese business decks that fall back to Latin UI fonts, report decks with missing evidence media, and decks whose cover/ending pages lack intentional presentation rhythm.
- Enhanced `check_pptx_structure.py` to report font families and CJK text, and to optionally flag missing media evidence and Latin-font fallback with `--min-media-files` and `--warn-ascii-fonts-for-cjk`.

## 1.0.3 - 2026-06-19

- Refined the skill into a clearer agentic capability unit with trigger discipline, operating contract, execution loop, packaging rules, and failure-derived gotchas.
- Added maintainability principles for keeping the skill "center short, edges thick" while moving heavier judgment, QA, and deterministic work into references and scripts.
- Tightened the default QA stance around editable PPTX, outline traceability, proof-object planning, contact-sheet review, and repair-before-handoff behavior.
- Updated README versioning and repository installation instructions for the monorepo location.

## 1.0.2 - 2026-06-06

- Added benchmark comparison mode for auditing another deck generated from the same or similar input.
- Added executive proposal proof-object guidance for joint venture, shareholder, financing, board, and strategy decks.
- Added PPTX structure QA for slide density, proof-object variety, repeated layout signatures, and contact-sheet rhythm.
- Added an Executive Proposal System style family with native visual asset grammar.

## 1.0.1 - 2026-06-06

- Raised the default HTML QA minimum text size to 16px, matching the 12pt PPT readability floor.
- Added line-height QA for HTML slides with a default minimum of single spacing.
- Added final PPTX text QA for font sizes below 12pt, missing or below-single line spacing, estimated text overflow, out-of-bounds text boxes, and likely text box overlaps.
- Updated editable PPTX export to avoid auto-shrinking text below readability thresholds and to set at least single line spacing.
- Tightened the skill workflow and QA rubric so dense slides must be split, shortened, or relaid out instead of shrinking text.

## 1.0.0 - 2026-05-31

Initial public release.

- Added the Practical PPT workflow: outline intake, HTML-first visual drafting, editable PPTX export, and QA review.
- Added style-library mode for adapting reusable template type grammars to the deck topic.
- Added user-template mode for auditing a supplied PPTX style before generating a new deck.
- Added editable PPTX export from slide-spec JSON.
- Added HTML slide QA for overflow, out-of-bounds text, small text, and likely overlap issues.
- Added PPTX template audit helper for palette, fonts, shape grammar, text previews, and slide inventory.
