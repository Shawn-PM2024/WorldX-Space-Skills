# Platform Notes

This skill is written to be portable across multiple agent environments.

The core design assumption is simple:

- `SKILL.md` is the primary operational document
- `references/` contains optional deepening material
- the skill should remain useful even when a host does not support Codex-native skill metadata

## 1. Codex

Codex is the primary reference environment for this repository.

Recommended usage:

- keep `SKILL.md` as the canonical English source
- keep `agents/openai.yaml` for UI-facing metadata when supported
- load `references/` only when the active task needs more detailed signals or response patterns

In Codex-style environments, the most natural invocation pattern is:

- explicit skill use, such as `$kapuscinski-style-evaluator`
- or repository-based loading where `SKILL.md` is treated as the entrypoint

## 2. Claude Code

Claude Code does not rely on Codex-specific metadata files in the same way.

Recommended adaptation:

- use `SKILL.md` as the main skill or prompt document
- treat `references/craft-signals.md` and `references/response-patterns.md` as optional supporting context
- ignore `agents/openai.yaml` if the host does not use it

When adapting to Claude Code, preserve:

- editorial commentary first
- no scoring
- no full-style imitation
- the three diagnostic layers as internal analysis, not rigid output headings

## 3. OpenClaw And Similar Agent Hosts

For OpenClaw or other agent shells, use the repository as a prompt package rather than assuming full Codex compatibility.

Recommended adaptation:

- keep `SKILL.md` as the host-facing instruction file
- map host-specific invocation syntax externally rather than rewriting the skill itself
- preserve repository-relative links where possible
- if the host cannot follow markdown links, provide the same files as manually loadable support documents

The important portability principle is:
the skill logic should stay stable even if the host-specific loading mechanism changes.

## 4. Portability Rules

To keep this skill adaptable across hosts:

- keep the core skill in plain English
- avoid relying on one vendor's hidden behaviors
- put host-specific guidance in separate docs instead of hard-wiring it into the core logic
- keep safety boundaries and output expectations in `SKILL.md`
- keep deeper examples and signal banks in `references/`

## 5. What Should Stay Stable Across All Hosts

No matter which agent runtime is used, preserve these behaviors:

- evaluate resemblance through textual behavior rather than topic similarity
- default to editorial commentary instead of structured scoring
- keep the three diagnostic layers available internally
- avoid full-paragraph imitation
- end substantial responses with practice suggestions

If a host requires extra wrapper prompts, add them outside the skill core whenever possible.
