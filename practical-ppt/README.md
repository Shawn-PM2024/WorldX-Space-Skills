# Practical PPT

Practical PPT 是一个 Codex skill，用于将 PPT 提纲、Markdown 草稿或结构化笔记转换为美观、可读、可编辑的 PowerPoint 演示文稿。

当前版本：`1.0.3`

English version: [English](#english)

## 中文

### 功能

- 默认生成完整 PPT，包括封面页和结束页。
- 先绘制 HTML 页面作为视觉源稿，再重建为可编辑的原生 PowerPoint 文本和图形对象。
- 以 Agent 工作流方式执行：路由输入、规划 proof object、生成 HTML/PPTX、运行 QA、修复问题，再交付。
- 支持两种样式模式：
  - `style-library`：从内置样式库选择模板类型，并根据主题和受众改造。
  - `user-template`：先审计用户提供的模板 PPT，再学习其视觉语法并适配到新主题。
- 支持 `benchmark-compare`：对比另一个 PPT 输出，先分析叙事、样式、proof object、可读性和可编辑性差距，再重建。
- 交付前执行 QA，包括文字溢出、重叠、越界、小字号、样式一致性、提纲匹配和内容合理性。

### 仓库结构

```text
.
├── SKILL.md
├── VERSION
├── agents/
│   └── openai.yaml
├── references/
│   ├── proposal-proof-objects.md
│   ├── qa-rubric.md
│   ├── skill-principles.md
│   └── style-library.md
└── scripts/
    ├── audit_pptx_template.py
    ├── check_html_slides.mjs
    ├── check_pptx_structure.py
    ├── check_pptx_text.py
    ├── html_to_pptx.mjs
    └── spec_to_editable_pptx.mjs
```

### 安装

克隆本仓库到 Codex skills 目录：

```bash
mkdir -p ~/.codex/skills
git clone --depth 1 https://github.com/Shawn-PM2024/WorldX-Space-Skills.git ~/.codex/skills/worldx-space-skills
ln -sfn ~/.codex/skills/worldx-space-skills/practical-ppt ~/.codex/skills/practical-ppt
```

之后在 Codex 中要求使用 `practical-ppt` 将提纲转换为 PPT。

### 运行环境

- Python 3.10 或更高版本，用于 PPTX 模板审计。
- Node.js 18 或更高版本。
- 脚本需要可解析以下 Node 包：
  - `pptxgenjs`
  - `playwright`

在 Codex 桌面环境中，这些包通常可通过内置 runtime 获得。如果 Node 无法解析依赖，可以通过 `NODE_PATH` 指向对应 runtime 的 `node_modules` 目录。

### 常用命令

审计用户提供的 PPTX 模板：

```bash
python3 scripts/audit_pptx_template.py reference-template.pptx --out template-audit
```

从 slide spec 生成可编辑 PPTX：

```bash
node scripts/spec_to_editable_pptx.mjs deck-spec.json deck.pptx
```

导出前检查 HTML slides：

```bash
node scripts/check_html_slides.mjs deck.html --output qa-report.json --min-text-px 16
```

检查最终 PPTX 的文字可读性：

```bash
python3 scripts/check_pptx_text.py deck.pptx --output pptx-text-qa.json --fail-on-review
```

检查最终 PPTX 的结构与视觉节奏：

```bash
python3 scripts/check_pptx_structure.py deck.pptx --output pptx-structure-qa.json --fail-on-review
```

仅在明确接受非完全可编辑备份时，生成图片型 PPTX：

```bash
node scripts/html_to_pptx.mjs deck.html deck-raster-backup.pptx
```

### 质量标准

默认交付物必须可编辑。普通页面文字和核心图示应使用 PPTX 原生文本、形状和线条，而不是整页截图。图片型导出仅用于预览、备份，或用户明确接受非完全可编辑的场景。

交付前应完成：

- HTML slide QA，没有阻塞性布局问题。
- PPTX text QA，没有 12pt 以下字号、缺失/低于单倍行距、估算溢出、越界或疑似重叠问题。
- PPTX structure QA，没有过密页面、连续重复版式、缺少 proof object 的正文页。
- 缩略图总览人工检查。
- PPTX 可编辑性检查，确认存在真实文本节点和可编辑图形。
- 根据 `references/qa-rubric.md` 做样式和内容审查。

### 版本管理

本仓库使用语义化版本。当前发布版本为 `1.0.3`。

版本说明见 [CHANGELOG.md](CHANGELOG.md)。

## English

Practical PPT is a Codex skill for creating polished, readable, editable PowerPoint decks from outlines, markdown drafts, and structured notes.

Current version: `1.0.3`

### What It Does

- Creates a complete deck by default, including a cover slide and an ending slide.
- Designs the deck as HTML first, then rebuilds it as editable native PowerPoint text and shape objects.
- Runs as an agentic workflow: route the input, plan proof objects, generate HTML/PPTX, run QA, repair issues, and then hand off evidence.
- Supports two style modes:
  - `style-library`: select and adapt a reusable template type from the local style library.
  - `user-template`: audit a supplied template deck first, then adapt its visual grammar to the new topic.
- Supports `benchmark-compare`: compare another deck output first, then rebuild based on narrative, style, proof-object, readability, and editability gaps.
- Runs QA before delivery, including text overflow, overlap, out-of-bounds elements, small text, style consistency, outline matching, and content reasonableness.

### Repository Layout

```text
.
├── SKILL.md
├── VERSION
├── agents/
│   └── openai.yaml
├── references/
│   ├── proposal-proof-objects.md
│   ├── qa-rubric.md
│   ├── skill-principles.md
│   └── style-library.md
└── scripts/
    ├── audit_pptx_template.py
    ├── check_html_slides.mjs
    ├── check_pptx_structure.py
    ├── check_pptx_text.py
    ├── html_to_pptx.mjs
    └── spec_to_editable_pptx.mjs
```

### Install

Clone this repository into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone --depth 1 https://github.com/Shawn-PM2024/WorldX-Space-Skills.git ~/.codex/skills/worldx-space-skills
ln -sfn ~/.codex/skills/worldx-space-skills/practical-ppt ~/.codex/skills/practical-ppt
```

Then ask Codex to use `practical-ppt` when converting an outline into a deck.

### Runtime Requirements

- Python 3.10 or newer for PPTX template auditing.
- Node.js 18 or newer.
- Node packages available to the scripts:
  - `pptxgenjs`
  - `playwright`

In Codex desktop environments, these packages may already be available through the bundled runtime. If Node cannot resolve them, run scripts with `NODE_PATH` pointing to the runtime `node_modules` directory.

### Main Commands

Audit a supplied PPTX template:

```bash
python3 scripts/audit_pptx_template.py reference-template.pptx --out template-audit
```

Build an editable PPTX from a slide spec:

```bash
node scripts/spec_to_editable_pptx.mjs deck-spec.json deck.pptx
```

Check HTML slides before export:

```bash
node scripts/check_html_slides.mjs deck.html --output qa-report.json --min-text-px 16
```

Check final PPTX text readability:

```bash
python3 scripts/check_pptx_text.py deck.pptx --output pptx-text-qa.json --fail-on-review
```

Check final PPTX structure and visual rhythm:

```bash
python3 scripts/check_pptx_structure.py deck.pptx --output pptx-structure-qa.json --fail-on-review
```

Create an image-backed PPTX only when explicitly acceptable:

```bash
node scripts/html_to_pptx.mjs deck.html deck-raster-backup.pptx
```

### Quality Bar

The default deliverable should be editable. Normal slide text and core diagrams should be native PPTX text, shapes, and lines rather than full-slide screenshots. Raster export is reserved for preview, backup, or explicitly accepted non-editable use.

Before delivery, Practical PPT expects:

- HTML slide QA with no blocking layout issues.
- PPTX text QA with no text below 12pt, missing or below-single line spacing, estimated overflow, out-of-bounds text, or likely overlaps.
- PPTX structure QA with no over-dense slides, repeated layout runs, or body slides without proof objects.
- Visual contact sheet inspection.
- PPTX editability check for real text runs and editable shapes.
- A style/content review against `references/qa-rubric.md`.

### Versioning

This repository uses semantic versioning. The current release is `1.0.3`.

See [CHANGELOG.md](CHANGELOG.md) for release notes.
