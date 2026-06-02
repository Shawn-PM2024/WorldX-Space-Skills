# WorldX Space Skills

Public AI skills maintained by Shawn-PM2024.

This repository follows the multi-skill layout used by open skill collections such as `KKKKhazix/khazix-skills`: each skill lives in its own top-level directory and can be installed independently by pointing an agent to that directory.

## Skills

| Skill | Purpose | Entry |
|---|---|---|
| `kapuscinski-style-evaluator` | Evaluates Chinese or English nonfiction prose as an editorial writing coach, focusing on whether the draft moves toward a Kapuscinski-like mode of observation and narration without imitating the author. | [`SKILL.md`](./kapuscinski-style-evaluator/SKILL.md) |
| `practical-ppt` | Turns outlines, markdown drafts, or structured notes into polished, readable, editable PowerPoint decks with HTML-first design and QA checks. | [`SKILL.md`](./practical-ppt/SKILL.md) |

## Install

In Codex, Claude Code, OpenClaw, or another agent shell that supports `SKILL.md`, ask the agent to install one of these skill directories:

```text
Install this skill:
https://github.com/Shawn-PM2024/WorldX-Space-Skills/tree/main/kapuscinski-style-evaluator
```

```text
Install this skill:
https://github.com/Shawn-PM2024/WorldX-Space-Skills/tree/main/practical-ppt
```

You can also clone the repository and copy the desired directory into your local skills folder.

```bash
git clone https://github.com/Shawn-PM2024/WorldX-Space-Skills.git
mkdir -p ~/.codex/skills
cp -R WorldX-Space-Skills/kapuscinski-style-evaluator ~/.codex/skills/
cp -R WorldX-Space-Skills/practical-ppt ~/.codex/skills/
```

## Repository Layout

```text
WorldX-Space-Skills/
├── kapuscinski-style-evaluator/
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/
│   ├── docs/
│   └── references/
└── practical-ppt/
    ├── SKILL.md
    ├── README.md
    ├── agents/
    ├── references/
    └── scripts/
```

## Notes

- `kapuscinski-style-evaluator` is an evaluator and coaching skill, not a style-cloning generator.
- `practical-ppt` expects a Python and Node runtime for its PPTX audit and generation scripts.
- Each skill keeps its own README, references, scripts, and optional host metadata.
