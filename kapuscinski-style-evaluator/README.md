# Kapuscinski Style Evaluator

A portable writing-coach skill for judging whether a Chinese or English nonfiction passage moves toward a Kapuscinski-like mode of observation and narration.

This repository is for editorial evaluation, not style cloning. It helps a writer see where a passage is already moving closer to that manner, where it still leans too heavily on explanation or abstraction, and what concrete practice steps could push it further.

## What This Skill Does

The evaluator is designed to produce an editor-like response rather than a rubric.

It focuses on:

- how a passage enters a scene
- whether details carry real weight
- how the narrator relates to people, institutions, and events
- whether meaning grows out of observation rather than arriving as a ready-made conclusion
- what the writer can practice next

It does not try to define Kapuscinski with a single formula. Instead, it uses a layered reading approach to judge whether a text is moving closer to that way of seeing and narrating.

## What It Does Not Do

This project is intentionally not a style-imitation tool.

It should not:

- rewrite full passages "in Kapuscinski's style"
- generate a new article as if written by Kapuscinski
- reduce literary judgment to a score
- treat subject matter alone as evidence of stylistic resemblance

It may provide a very short illustrative micro-example when that genuinely helps the user understand the difference on the page, but that example should stay brief and diagnostic.

## Best-Fit Inputs

Version 1 is intentionally narrow.

- Languages: Chinese and English
- Length: roughly 800-3000 words
- Form: nonfiction prose
- Strongest fit: reportage, feature writing, travel writing, observational essays, reflective long-form prose

Texts outside that range can still be discussed, but the skill should mark them as only partially suitable and avoid overconfident judgment.

## What The Output Should Feel Like

The response should read like a thoughtful editor's letter:

- interpretive rather than mechanical
- specific rather than slogan-like
- coaching-oriented rather than punitive
- literary in tone, but still practical

Substantial responses should usually include:

1. a concise overall judgment
2. a natural editorial commentary on where the text is closer to or further from the target manner
3. one to three practical exercises tailored to the passage

The internal diagnostic layers are observation, narration, and meaning-generation, but they normally stay in the background. The user-facing response should not read like a rigid checklist unless the user explicitly asks for that format.

## Install

Use this skill directory from the public collection:

```text
https://github.com/Shawn-PM2024/WorldX-Space-Skills/tree/main/kapuscinski-style-evaluator
```

## Quick Start

Use the canonical skill entrypoint:

- [`SKILL.md`](./SKILL.md)

Optional supporting files:

- [`references/craft-signals.md`](./references/craft-signals.md)
- [`references/response-patterns.md`](./references/response-patterns.md)
- [`references/debug-cases.md`](./references/debug-cases.md)
- [`references/corpus-inventory.yaml`](./references/corpus-inventory.yaml)
- [`docs/platform-notes.md`](./docs/platform-notes.md)

## Example Use

Typical user input can stay lightweight:

```text
Please read the following essay as a writing coach.
I want to know whether it moves toward a Kapuscinski-like mode of observation and narration.
Be direct but not harsh.

Title: ...
Purpose: ...
Text: ...
```

The evaluator should then respond with:

- an overall conclusion
- a natural editorial reading of the passage
- practical revision or practice suggestions
- optionally, a tiny illustrative micro-example if that would clarify the advice

## Cross-Agent Compatibility

The repository is written to stay usable across different agent environments.

Current target hosts include:

- Codex
- Claude Code
- OpenClaw
- similar agent shells that can load a markdown skill and optional references

The portability rule is simple: keep the core evaluative logic in `SKILL.md`, and move host-specific notes outside the core skill whenever possible.

See [`docs/platform-notes.md`](./docs/platform-notes.md) for environment-specific guidance.

## Repository Layout

```text
kapuscinski-style-evaluator/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── docs/
│   ├── SKILL.zh-CN.md
│   └── platform-notes.md
└── references/
    ├── corpus-inventory.yaml
    ├── craft-signals.md
    ├── debug-cases.md
    └── response-patterns.md
```

## Local Development Notes

This repository is meant to stay clean and GitHub-syncable.

Local-only material such as captured web text, scratch runs, and private notes should live outside the synced repository in a separate sibling workspace. On this machine, that directory is:

`/Users/xiao/Documents/codex/05-卡普希钦斯基skill.local/`

## Validation

In Codex-oriented environments, a fast local validation can be run with:

```bash
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" /path/to/WorldX-Space-Skills/kapuscinski-style-evaluator
```

## Status

This repository is a working, manually tested skill package. The most useful next steps are:

- more live evaluations on real nonfiction prose
- more cross-host response tuning
- more edge-case examples for short-form, highly abstract, or partially suitable inputs
