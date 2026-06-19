# Practical PPT Skill Principles

Use these principles when maintaining this skill. They are implementation rules, not user-facing copy.

## 1. Treat the Skill as an Agent Capability Unit

Practical PPT should package a repeatable capability: route the request, inspect inputs, select style, build artifacts, run tools, repair issues, and hand off evidence. Avoid turning `SKILL.md` into a decorative prompt. Every instruction should change execution.

## 2. Center Short, Edges Thick

Keep `SKILL.md` focused on trigger conditions, the core loop, hard gates, and gotchas. Put heavier design systems, QA rubrics, proof-object libraries, examples, and deterministic checks into `references/` and `scripts/`.

## 3. Encode Taste as Constraints

Design quality improves when taste becomes executable constraints:

- use validated style families instead of free-form color prompts
- choose named proof objects before drawing slides
- forbid repeated card/list/table monotony
- keep editable native text and shapes as the default
- block small text, overflow, overlap, and weak contrast
- prefer real photos, screenshots, diagrams, and data over ornamental filler

## 4. Let Tools Handle Deterministic Work

The model should decide, synthesize, adapt, and repair. Scripts should audit PPTX templates, generate editable PPTX when possible, and detect text/layout/structure problems. When a script exists, call it rather than recreating the same check manually.

## 5. Use Real Failures as Gotchas

When a generation fails, do not only expand the happy path. Add a small gotcha, QA rule, helper script, eval case, or style-library refinement that prevents the same class of failure. Prefer a narrow fix over a longer generic rule.

## 6. Maintain the Skill Like Code

For each meaningful release:

- update `VERSION`, `CHANGELOG.md`, and README version text
- validate `SKILL.md` with the skill validator
- run script syntax checks
- sync the installed local skill if this repo is the source of truth
- tag the release in Git

## 7. User Sees Results, Not Internal Taxonomy

Use internal terms such as proof object, style family, and QA gate to guide the Agent. In final user-facing handoff, report the outcome plainly: files produced, editable status, checks run, fixes made, and any remaining assumptions.
