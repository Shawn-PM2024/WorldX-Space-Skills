# media-transcribe-public

**中文** | [English](#english)

`media-transcribe-public` 是一个本地优先的音视频转写开源项目，同时内置 Codex skill。它把本地或 URL 音视频转成 Markdown 笔记，默认使用本机 `ffmpeg` + `whisper-cli`，并把远程转写、说话人模型和第三方笔记发布都设计为显式可选能力。

当前版本：`1.0.0`

## 功能

- 转写本地音频、视频文件或 HTTP(S) 媒体 URL。
- 默认使用本机 `whisper.cpp`，不需要 OpenAI API key。
- 对长文件自动压缩、切段、缓存，避免重复转写。
- 支持可选说话人区分：本地聚类、whisper stereo diarization、pyannote。
- 生成 Codex 可继续整理的 Markdown：标题、整理时间、核心观点占位、金句占位、清洗后全文和元信息。
- 根据 ASR segment 时间和文本 cue 做基础标点推断：句内停顿用逗号，完整句或问句才换行。
- 支持发布后端：本地 Markdown、Obsidian vault、Youdao 兼容后端、仅缓存不发布。

## 仓库结构

```text
media-transcribe-public/
├── README.md
├── LICENSE
├── PRIVACY.md
├── THIRD_PARTY_NOTICES.md
├── pyproject.toml
├── skill/
│   └── media-transcribe-public/
│       ├── SKILL.md
│       └── agents/openai.yaml
├── src/
│   └── media_transcribe_public/
│       ├── __init__.py
│       ├── __main__.py
│       └── cli.py
└── tests/
    ├── test_backends.py
    └── test_note_format.py
```

## 安装

从仓库安装 CLI：

```bash
git clone https://github.com/Shawn-PM2024/WorldX-Space-Skills.git
cd WorldX-Space-Skills/media-transcribe-public
python3 -m pip install -e ".[zh,diarization-cluster]"
```

安装内置 Codex skill：

```bash
mkdir -p ~/.codex/skills
cp -R skill/media-transcribe-public ~/.codex/skills/
```

开发环境可以额外安装测试依赖：

```bash
python3 -m pip install -e ".[zh,diarization-cluster,dev]"
```

## 本地依赖

默认本地转写需要这些系统工具在 `PATH` 上：

```bash
# macOS
brew install ffmpeg whisper-cpp
```

Linux 用户请通过发行版包管理器或源码安装 `ffmpeg` 和 `whisper.cpp`。Windows 用户需要安装 `ffmpeg.exe` 和 `whisper-cli.exe`，并加入 `PATH`。

下载 whisper.cpp GGML 模型：

```bash
mkdir -p ~/.cache/whisper-cpp
curl -L -o ~/.cache/whisper-cpp/ggml-small.bin \
  https://mirrors.mit.edu/macports/distfiles/whisper/ggml-small.bin
```

也可以用环境变量或参数指定模型：

```bash
export WHISPER_CPP_MODEL=/path/to/ggml-model.bin
media-transcribe-public input.mp3 --model-path /path/to/ggml-model.bin
```

## 快速开始

只保留缓存和 `note.md`：

```bash
media-transcribe-public input.mp3 \
  --language zh \
  --note-backend none \
  --no-polish
```

复制 Markdown 到本地目录：

```bash
media-transcribe-public input.mp3 \
  --title "Podcast Episode" \
  --language zh \
  --note-backend local \
  --output-dir ./notes \
  --no-polish
```

写入 Obsidian vault：

```bash
media-transcribe-public input.mp3 \
  --title "Interview Notes" \
  --language zh \
  --note-backend obsidian \
  --vault-path "$OBSIDIAN_VAULT" \
  --vault-folder "Transcripts" \
  --no-polish
```

写入 Youdao Note，要求本机已经配置 `youdaonote` CLI：

```bash
media-transcribe-public input.mp3 \
  --title "Podcast Notes" \
  --language zh \
  --note-backend youdao \
  --destination "YOUR_YOUDAO_PARENT_FOLDER_ID" \
  --no-polish
```

## 可选能力

OpenAI 转写会上传音频片段到 OpenAI：

```bash
export OPENAI_API_KEY="..."
media-transcribe-public input.mp3 \
  --backend openai \
  --model gpt-4o-mini-transcribe
```

本地聚类说话人区分需要数值计算依赖：

```bash
python3 -m pip install -e ".[diarization-cluster]"
media-transcribe-public input.mp3 \
  --diarization-backend local-cluster \
  --min-speakers 2 \
  --max-speakers 3
```

pyannote 说话人区分需要本地 Python 包和 Hugging Face 模型权限：

```bash
python3 -m pip install -e ".[diarization-pyannote]"
export PYANNOTE_AUTH_TOKEN="..."
media-transcribe-public input.mp3 \
  --diarization-backend pyannote \
  --min-speakers 2 \
  --max-speakers 4
```

## 输出格式

CLI 会先生成一份 Codex-ready Markdown。`--no-polish` 推荐用于 Codex 工作流，因为 `核心观点`、`金句` 和最终全文润色应由 Codex 基于完整转写内容完成。

```markdown
# {title}
整理时间：{YYYY-MM-DD}

## 核心观点
1. 未启用模型整理；请基于下方全文补充核心观点。

## 金句
1. 未启用模型整理；请基于下方全文补充金句。

## 清洗后全文
**说话人?**：...

## 元信息
- 媒体时长：...
```

## 隐私与安全

- 默认 `local-whisper-cpp` 模式不上传音频。
- `--backend openai` 会上传切分后的音频片段到 OpenAI。
- `--diarization-backend pyannote` 会使用 Hugging Face token 并可能下载模型。
- `--note-backend youdao` 会通过本机 `youdaonote` CLI 上传 Markdown 内容。
- 不要把 API key、token、`.env` 或笔记服务本地配置内容贴到聊天、日志或 issue 中。
- 详细说明见 [PRIVACY.md](PRIVACY.md) 和 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 测试

```bash
python3 -m pytest -q
python3 -m py_compile \
  src/media_transcribe_public/cli.py \
  src/media_transcribe_public/__init__.py \
  src/media_transcribe_public/__main__.py
```

验证内置 skill：

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py skill/media-transcribe-public
```

## 版本

当前版本：`1.0.0`

发布 tag：`media_transcribe_public-1.0.0`

---

## English

`media-transcribe-public` is a local-first open-source audio/video transcription project with a bundled Codex skill. It turns local files or HTTP(S) media URLs into Markdown notes. The default path uses local `ffmpeg` + `whisper-cli`; remote transcription, speaker models, and third-party note publishing are explicit opt-in features.

Current version: `1.0.0`

## Features

- Transcribe local audio/video files or HTTP(S) media URLs.
- Use local `whisper.cpp` by default, with no OpenAI API key required.
- Normalize, segment, and cache long media files to avoid repeated transcription.
- Optionally assign speaker labels through local clustering, whisper stereo diarization, or pyannote.
- Generate a Codex-ready Markdown note with title, timestamp, placeholders for core ideas and quotes, cleaned full text, and metadata.
- Infer basic punctuation from ASR segment timing and text cues: commas for intra-sentence pauses, line breaks only after complete sentences or questions.
- Publish to local Markdown, Obsidian vaults, an optional Youdao-compatible backend, or cache only.

## Repository Layout

```text
media-transcribe-public/
├── README.md
├── LICENSE
├── PRIVACY.md
├── THIRD_PARTY_NOTICES.md
├── pyproject.toml
├── skill/
│   └── media-transcribe-public/
│       ├── SKILL.md
│       └── agents/openai.yaml
├── src/
│   └── media_transcribe_public/
│       ├── __init__.py
│       ├── __main__.py
│       └── cli.py
└── tests/
    ├── test_backends.py
    └── test_note_format.py
```

## Install

Install the CLI from this repository:

```bash
git clone https://github.com/Shawn-PM2024/WorldX-Space-Skills.git
cd WorldX-Space-Skills/media-transcribe-public
python3 -m pip install -e ".[zh,diarization-cluster]"
```

Install the bundled Codex skill:

```bash
mkdir -p ~/.codex/skills
cp -R skill/media-transcribe-public ~/.codex/skills/
```

For development, include test dependencies:

```bash
python3 -m pip install -e ".[zh,diarization-cluster,dev]"
```

## Local Requirements

The default local transcription path needs these system tools on `PATH`:

```bash
# macOS
brew install ffmpeg whisper-cpp
```

Linux users can install `ffmpeg` and `whisper.cpp` through a package manager or from source. Windows users need `ffmpeg.exe` and `whisper-cli.exe` available on `PATH`.

Download a whisper.cpp GGML model:

```bash
mkdir -p ~/.cache/whisper-cpp
curl -L -o ~/.cache/whisper-cpp/ggml-small.bin \
  https://mirrors.mit.edu/macports/distfiles/whisper/ggml-small.bin
```

You can also select a model with an environment variable or CLI argument:

```bash
export WHISPER_CPP_MODEL=/path/to/ggml-model.bin
media-transcribe-public input.mp3 --model-path /path/to/ggml-model.bin
```

## Quick Start

Keep only cache artifacts and `note.md`:

```bash
media-transcribe-public input.mp3 \
  --language zh \
  --note-backend none \
  --no-polish
```

Copy Markdown to a local folder:

```bash
media-transcribe-public input.mp3 \
  --title "Podcast Episode" \
  --language zh \
  --note-backend local \
  --output-dir ./notes \
  --no-polish
```

Write to an Obsidian vault:

```bash
media-transcribe-public input.mp3 \
  --title "Interview Notes" \
  --language zh \
  --note-backend obsidian \
  --vault-path "$OBSIDIAN_VAULT" \
  --vault-folder "Transcripts" \
  --no-polish
```

Write to Youdao Note when the local `youdaonote` CLI is already configured:

```bash
media-transcribe-public input.mp3 \
  --title "Podcast Notes" \
  --language zh \
  --note-backend youdao \
  --destination "YOUR_YOUDAO_PARENT_FOLDER_ID" \
  --no-polish
```

## Optional Capabilities

OpenAI transcription uploads audio segments to OpenAI:

```bash
export OPENAI_API_KEY="..."
media-transcribe-public input.mp3 \
  --backend openai \
  --model gpt-4o-mini-transcribe
```

Local clustering diarization needs numerical Python dependencies:

```bash
python3 -m pip install -e ".[diarization-cluster]"
media-transcribe-public input.mp3 \
  --diarization-backend local-cluster \
  --min-speakers 2 \
  --max-speakers 3
```

pyannote diarization needs a local Python package and Hugging Face model access:

```bash
python3 -m pip install -e ".[diarization-pyannote]"
export PYANNOTE_AUTH_TOKEN="..."
media-transcribe-public input.mp3 \
  --diarization-backend pyannote \
  --min-speakers 2 \
  --max-speakers 4
```

## Output Format

The CLI first writes a Codex-ready Markdown draft. `--no-polish` is recommended for Codex workflows because Codex should fill `核心观点`, `金句`, and the final transcript cleanup after reading the full transcript.

```markdown
# {title}
整理时间：{YYYY-MM-DD}

## 核心观点
1. 未启用模型整理；请基于下方全文补充核心观点。

## 金句
1. 未启用模型整理；请基于下方全文补充金句。

## 清洗后全文
**说话人?**：...

## 元信息
- 媒体时长：...
```

## Privacy and Security

- The default `local-whisper-cpp` mode does not upload media.
- `--backend openai` uploads segmented audio to OpenAI.
- `--diarization-backend pyannote` uses a Hugging Face token and may download models.
- `--note-backend youdao` uploads Markdown through the local `youdaonote` CLI.
- Do not paste API keys, tokens, `.env` files, or local note-service config into chats, logs, or issues.
- See [PRIVACY.md](PRIVACY.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.

## Test

```bash
python3 -m pytest -q
python3 -m py_compile \
  src/media_transcribe_public/cli.py \
  src/media_transcribe_public/__init__.py \
  src/media_transcribe_public/__main__.py
```

Validate the bundled skill:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py skill/media-transcribe-public
```

## Version

Current version: `1.0.0`

Release tag: `media_transcribe_public-1.0.0`
