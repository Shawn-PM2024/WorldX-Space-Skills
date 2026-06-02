# Kapuscinski Style Evaluator

**中文** | [English](#english)

一个面向中英文非虚构写作的编辑型评估 skill，用来判断一篇文本是否正在接近卡普希钦斯基式的观察与叙述方式，并给出可练习的修改方向。

这个 skill 不是仿写工具。它不会代替作者写出一篇“卡普希钦斯基风格”的文章，而是帮助作者看见：文本哪里已经接近这种写法，哪里仍然过于依赖解释、概念或抽象判断，以及下一步可以怎样训练。

## 它适合做什么

这个 skill 的输出应当像一封编辑点评，而不是评分表。

它重点关注：

- 文本如何进入场景
- 细节是否真正承重
- 叙述者如何面对人物、制度、事件和空间
- 意义是否从观察中生长出来，而不是以现成结论出现
- 作者下一步可以做哪些具体练习

它不会用一句话定义卡普希钦斯基的风格，而是通过分层阅读，判断一篇文本是否在观察、叙述和意义生成上靠近这种写法。

## 它不做什么

这个项目有意避免成为风格克隆工具。

它不应该：

- 整段或整篇改写成“卡普希钦斯基风格”
- 生成一篇仿佛由卡普希钦斯基写成的新文章
- 用分数简化文学判断
- 只因为题材涉及历史、权力、国家、边缘地带，就判断文本接近目标风格

在确实有助于理解差异时，它可以给出一小段极短的示例，但这个示例应当只用于说明写法差异，不能扩展成完整仿写。

## 适合的输入

第一版范围刻意保持收窄：

- 语种：中文和英文
- 长度：约 800-3000 字
- 体裁：非虚构 prose
- 最适合：报道、特稿、旅行写作、观察型随笔、反思性长文

如果输入是小说、诗、极短文本、纯社论或高度抽象的评论，skill 仍可给出有限点评，但应先说明文本只具备部分适配性。

## 输出会是什么样

一次完整回应通常包括：

1. 简短的整体判断
2. 自然的编辑式评论，说明文本在哪里接近或偏离目标写法
3. 一到三个贴合原文的练习建议

内部诊断层包括观察、叙述和意义生成，但它们通常只作为分析框架保留在后台。面向用户的输出应自然、灵活、有人文评论感，不应机械罗列成 checklist。

## 安装与使用

在 Codex、Claude Code、OpenClaw 或其他支持 `SKILL.md` 的 Agent 环境中，可以直接使用这个目录：

```text
https://github.com/Shawn-PM2024/WorldX-Space-Skills/tree/main/kapuscinski-style-evaluator
```

核心入口文件：

- [`SKILL.md`](./SKILL.md)

可选参考文件：

- [`references/craft-signals.md`](./references/craft-signals.md)
- [`references/response-patterns.md`](./references/response-patterns.md)
- [`references/debug-cases.md`](./references/debug-cases.md)
- [`references/corpus-inventory.yaml`](./references/corpus-inventory.yaml)
- [`docs/platform-notes.md`](./docs/platform-notes.md)

## 输入示例

```text
请作为写作教练阅读下面这篇文章。
我想知道它是否接近卡普希钦斯基式的观察与叙述方式。
请直接一点，但不要用打分方式。

标题：...
写作目的：...
正文：...
```

## 跨 Agent 兼容

这个 skill 的核心逻辑写在 `SKILL.md` 中，平台适配说明放在独立文档中，便于在不同 Agent 环境中复用。

当前目标环境包括：

- Codex
- Claude Code
- OpenClaw
- 其他可以读取 markdown skill 和参考文件的 Agent shell

平台说明见 [`docs/platform-notes.md`](./docs/platform-notes.md)。

## 目录结构

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

## 校验

在 Codex 环境中，可以运行：

```bash
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" /path/to/WorldX-Space-Skills/kapuscinski-style-evaluator
```

---

## English

A writing-coach skill for evaluating whether a Chinese or English nonfiction passage moves toward a Kapuscinski-like mode of observation and narration.

This skill is not an imitation tool. It does not write a new article "in Kapuscinski's style." Instead, it helps writers understand where a passage already moves closer to that manner, where it still relies too heavily on explanation or abstraction, and what concrete practice steps could move it further.

## What It Is For

The evaluator should respond like an editor's letter, not a scoring rubric.

It focuses on:

- how the passage enters a scene
- whether details carry real weight
- how the narrator relates to people, institutions, events, and space
- whether meaning grows out of observation rather than arriving as a ready-made conclusion
- what the writer can practice next

It does not reduce Kapuscinski's writing to a single formula. Instead, it uses layered reading to judge whether a text is moving closer to that mode of seeing and narrating.

## What It Does Not Do

This project intentionally avoids becoming a style-cloning tool.

It should not:

- rewrite full passages "in Kapuscinski's style"
- generate a new article as if written by Kapuscinski
- reduce literary judgment to a numeric score
- treat historical, political, or marginal subject matter alone as stylistic resemblance

It may provide a very short illustrative micro-example when that genuinely helps the user understand the difference on the page, but the example should stay brief and diagnostic.

## Best-Fit Inputs

Version 1 is intentionally narrow.

- Languages: Chinese and English
- Length: roughly 800-3000 words
- Form: nonfiction prose
- Strongest fit: reportage, feature writing, travel writing, observational essays, reflective long-form prose

Texts outside that range can still be discussed, but the skill should mark them as only partially suitable and avoid overconfident judgment.

## Expected Output

A substantial response usually includes:

1. a concise overall judgment
2. a natural editorial reading of where the passage moves closer to or further from the target manner
3. one to three practical exercises tailored to the passage

The internal diagnostic layers are observation, narration, and meaning-generation, but they normally stay in the background. The user-facing response should feel natural, flexible, and literary rather than checklist-like.

## Install And Use

In Codex, Claude Code, OpenClaw, or another agent environment that supports `SKILL.md`, use this skill directory:

```text
https://github.com/Shawn-PM2024/WorldX-Space-Skills/tree/main/kapuscinski-style-evaluator
```

Canonical entrypoint:

- [`SKILL.md`](./SKILL.md)

Optional references:

- [`references/craft-signals.md`](./references/craft-signals.md)
- [`references/response-patterns.md`](./references/response-patterns.md)
- [`references/debug-cases.md`](./references/debug-cases.md)
- [`references/corpus-inventory.yaml`](./references/corpus-inventory.yaml)
- [`docs/platform-notes.md`](./docs/platform-notes.md)

## Example Input

```text
Please read the following essay as a writing coach.
I want to know whether it moves toward a Kapuscinski-like mode of observation and narration.
Be direct, but do not use a score.

Title: ...
Purpose: ...
Text: ...
```

## Cross-Agent Compatibility

The core skill logic lives in `SKILL.md`; host-specific guidance lives in separate documentation so the skill can remain portable across agent environments.

Current target hosts include:

- Codex
- Claude Code
- OpenClaw
- other agent shells that can load a markdown skill and optional reference files

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

## Validation

In Codex-oriented environments, run:

```bash
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" /path/to/WorldX-Space-Skills/kapuscinski-style-evaluator
```
