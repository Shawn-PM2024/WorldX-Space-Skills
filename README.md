# WorldX Space Skills

**中文** | [English](#english)

WorldX-Space 号主维护的公开 AI Skills 合集。每个 skill 都放在独立顶层目录中，可以单独安装、单独维护，也可以克隆整个仓库作为个人 Agent skill 库。

## Skills

| Skill | 用途 | 入口 |
|---|---|---|
| `kapuscinski-style-evaluator` | 面向中英文非虚构写作的编辑型评估 skill，用于判断文本是否接近卡普钦斯基式的观察和叙事方式，并给出具体练习建议；它是评估器，不是风格模仿生成器。 | [`SKILL.md`](./kapuscinski-style-evaluator/SKILL.md) |
| `media-transcribe-public` | 本地优先的音视频转写 skill，将音频/视频转成 Markdown 笔记，支持本机 whisper.cpp、可选说话人区分、Codex 整理、Obsidian/本地 Markdown/有道兼容后端。 | [`README.md`](./media-transcribe-public/README.md) / [`SKILL.md`](./media-transcribe-public/skill/media-transcribe-public/SKILL.md) |
| `practical-ppt` | 将 PPT 提纲、Markdown 草稿或结构化笔记转换为美观、可读、可编辑的 PowerPoint 演示文稿；采用 HTML 视觉源稿、原生 PPTX 重建和交付前 QA 流程。 | [`SKILL.md`](./practical-ppt/SKILL.md) |

## 安装

在 Codex、Claude Code、OpenClaw 或其他支持 `SKILL.md` 的 Agent 环境中，可以让 Agent 直接安装某个 skill 目录：

```text
安装这个 skill：
https://github.com/Shawn-PM2024/WorldX-Space-Skills/tree/main/kapuscinski-style-evaluator
```

```text
安装这个 skill：
https://github.com/Shawn-PM2024/WorldX-Space-Skills/tree/main/practical-ppt
```

`media-transcribe-public` 是一个开源 Python CLI 项目，并内置 Codex skill。安装项目和 skill 的推荐方式：

```bash
git clone https://github.com/Shawn-PM2024/WorldX-Space-Skills.git
cd WorldX-Space-Skills/media-transcribe-public
python3 -m pip install -e ".[zh,diarization-cluster]"
mkdir -p ~/.codex/skills
cp -R skill/media-transcribe-public ~/.codex/skills/
```

也可以克隆整个仓库，然后把需要的 skill 目录复制到本地 skills 目录：

```bash
git clone https://github.com/Shawn-PM2024/WorldX-Space-Skills.git
mkdir -p ~/.codex/skills
cp -R WorldX-Space-Skills/kapuscinski-style-evaluator ~/.codex/skills/
cp -R WorldX-Space-Skills/practical-ppt ~/.codex/skills/
cp -R WorldX-Space-Skills/media-transcribe-public/skill/media-transcribe-public ~/.codex/skills/
```

## 仓库结构

```text
WorldX-Space-Skills/
├── kapuscinski-style-evaluator/
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/
│   ├── docs/
│   └── references/
├── media-transcribe-public/
│   ├── README.md
│   ├── pyproject.toml
│   ├── skill/media-transcribe-public/
│   ├── src/media_transcribe_public/
│   └── tests/
└── practical-ppt/
    ├── SKILL.md
    ├── README.md
    ├── agents/
    ├── references/
    └── scripts/
```

## 说明

- `kapuscinski-style-evaluator` 只做写作评估和训练建议，不生成仿写长文。
- `media-transcribe-public` 默认本地运行，不捆绑 FFmpeg、whisper.cpp、模型文件或任何笔记服务凭据；OpenAI、pyannote、有道等能力都需要显式开启。
- `practical-ppt` 的 PPTX 审计和生成脚本需要 Python 与 Node.js 运行环境。
- 每个 skill 保留自己的 README、references、scripts、测试和可选 Agent 平台元数据。

---

## English

Public AI skills maintained by WorldX Space. Each skill lives in its own top-level directory, so it can be installed independently, maintained independently, or cloned as part of the full collection.

## Skills

| Skill | Purpose | Entry |
|---|---|---|
| `kapuscinski-style-evaluator` | An editorial evaluator for Chinese and English nonfiction prose. It judges whether a passage moves toward a Kapuscinski-like mode of observation and narration, then gives concrete practice suggestions. It is an evaluator, not a style-cloning generator. | [`SKILL.md`](./kapuscinski-style-evaluator/SKILL.md) |
| `media-transcribe-public` | A local-first audio/video transcription skill that turns media into Markdown notes with local whisper.cpp, optional speaker diarization, Codex editorial cleanup, and local Markdown, Obsidian, or optional Youdao-compatible publishing. | [`README.md`](./media-transcribe-public/README.md) / [`SKILL.md`](./media-transcribe-public/skill/media-transcribe-public/SKILL.md) |
| `practical-ppt` | Turns outlines, markdown drafts, or structured notes into polished, readable, editable PowerPoint decks through an HTML-first visual draft, native PPTX reconstruction, and pre-delivery QA. | [`SKILL.md`](./practical-ppt/SKILL.md) |

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

`media-transcribe-public` is an open Python CLI project with a bundled Codex skill. Recommended setup:

```bash
git clone https://github.com/Shawn-PM2024/WorldX-Space-Skills.git
cd WorldX-Space-Skills/media-transcribe-public
python3 -m pip install -e ".[zh,diarization-cluster]"
mkdir -p ~/.codex/skills
cp -R skill/media-transcribe-public ~/.codex/skills/
```

You can also clone the full repository and copy the desired skill directories into your local skills folder:

```bash
git clone https://github.com/Shawn-PM2024/WorldX-Space-Skills.git
mkdir -p ~/.codex/skills
cp -R WorldX-Space-Skills/kapuscinski-style-evaluator ~/.codex/skills/
cp -R WorldX-Space-Skills/practical-ppt ~/.codex/skills/
cp -R WorldX-Space-Skills/media-transcribe-public/skill/media-transcribe-public ~/.codex/skills/
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
├── media-transcribe-public/
│   ├── README.md
│   ├── pyproject.toml
│   ├── skill/media-transcribe-public/
│   ├── src/media_transcribe_public/
│   └── tests/
└── practical-ppt/
    ├── SKILL.md
    ├── README.md
    ├── agents/
    ├── references/
    └── scripts/
```

## Notes

- `kapuscinski-style-evaluator` provides writing evaluation and practice guidance only. It does not generate long-form imitation.
- `media-transcribe-public` runs locally by default and does not bundle FFmpeg, whisper.cpp, model files, or note-service credentials. OpenAI, pyannote, Youdao, and other external integrations must be enabled explicitly.
- `practical-ppt` expects Python and Node.js for its PPTX audit and generation scripts.
- Each skill keeps its own README, references, scripts, tests, and optional agent-platform metadata.
