# media-transcribe-public

**中文** | [English](#english)

`media-transcribe-public` 是一个本地优先的音视频转写开源项目，同时内置 Codex skill。它把本地或 URL 音视频转成 Markdown 笔记，默认使用本机 `ffmpeg` + `whisper-cli`，并把远程转写、说话人模型和第三方笔记发布都设计为显式可选能力。

当前版本：`1.0.2`

## 功能

- 转写本地音频、视频文件或 HTTP(S) 媒体 URL。
- 默认使用本机 `whisper.cpp`，不需要 OpenAI API key。
- 对长文件自动压缩、切段、并行转写和逐段缓存；中断后可复用已经完成的片段。
- whisper.cpp 启动前检测 GPU/Metal，崩溃时自动回退 CPU；也可显式使用 `--whisper-no-gpu`。
- 支持可选说话人区分：本地 sherpa-onnx 神经聚类、whisper stereo diarization、pyannote。
- 生成 Codex 可继续整理的 Markdown：标题、整理时间、核心观点占位、金句占位、清洗后全文和元信息。
- 根据 ASR segment 时间和文本 cue 做基础标点推断；同一说话人的一次对话轮次保持为一个段落，仅在说话人变化时换段。
- 支持发布后端：本地 Markdown、Obsidian vault、Youdao 兼容后端、仅缓存不发布。

## 适合场景

- 播客、访谈、会议录音、课程录音、视频素材的长文本转写。
- 需要先得到完整转写，再由 Codex 生成核心观点、金句和整理后全文的工作流。
- 希望默认本地运行，只在明确选择时才使用 OpenAI、pyannote、Youdao 等外部服务的用户。
- 需要把输出落到 Obsidian vault 或本地 Markdown 文件夹的知识管理场景。

## 输入与输出

输入：

- 本地音频或视频文件。
- HTTP(S) 媒体 URL。
- 可选标题、语言、说话人数、模型路径、发布后端。

输出：

- `transcript.txt`：原始转写文本。
- `segments.json`：带时间戳的 ASR segments。
- `speaker_transcript.txt`：说话人感知的全文草稿。
- `note.md`：Codex-ready Markdown 笔记。
- 可选发布结果：本地 Markdown、Obsidian 文件或 Youdao note payload。

## 典型提示词

```text
使用 media-transcribe-public，把这个播客音频转写成 Markdown，先保存到本地 notes 目录，不要上传远程服务。
```

```text
使用 media-transcribe-public 转写这段访谈，区分 2-3 个说话人，输出到 Obsidian 的 Transcripts 文件夹。
```

## 常见失败

- 直接发布第一版 `note.md`：它通常还包含 `核心观点`、`金句` 占位符。
- 把 CLI 的断句当作最终文本：CLI 只做草稿标点，Codex 仍需要做最终整理。
- 默认启用远程服务：OpenAI、pyannote、Youdao 都必须由用户显式选择。
- 没有确认缓存：复测断句、模型或说话人逻辑时应使用 `--force` 或新缓存目录。
- 忽略 `meta.json` 的 `speaker_turns_per_minute`：高于 8 通常表示说话人标签过度碎片化，应先抽查再发布。

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
│       ├── agents/openai.yaml
│       └── references/gotchas.md
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

本地说话人区分使用 sherpa-onnx 的 pyannote segmentation 与 3D-Speaker embedding ONNX 模型。下面示例把模型放到一个显式目录，避免依赖操作系统默认缓存位置：

```bash
export MEDIA_TRANSCRIBE_DIARIZATION_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/media-transcribe-public/diarization"
mkdir -p "$MEDIA_TRANSCRIBE_DIARIZATION_DIR"
curl -L -o "$MEDIA_TRANSCRIBE_DIARIZATION_DIR/segmentation.tar.bz2" \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-segmentation-models/sherpa-onnx-pyannote-segmentation-3-0.tar.bz2
tar -xjf "$MEDIA_TRANSCRIBE_DIARIZATION_DIR/segmentation.tar.bz2" \
  -C "$MEDIA_TRANSCRIBE_DIARIZATION_DIR"
curl -L -o "$MEDIA_TRANSCRIBE_DIARIZATION_DIR/3dspeaker_speech_eres2net_base_sv_zh-cn_3dspeaker_16k.onnx" \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-recongition-models/3dspeaker_speech_eres2net_base_sv_zh-cn_3dspeaker_16k.onnx
```

也可以分别设置 `MEDIA_TRANSCRIBE_SEGMENTATION_MODEL`、`MEDIA_TRANSCRIBE_EMBEDDING_MODEL`，或传入 `--speaker-segmentation-model`、`--speaker-embedding-model`。

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

本地神经说话人区分需要 sherpa-onnx 依赖和上方两个模型：

```bash
python3 -m pip install -e ".[diarization-cluster]"
media-transcribe-public input.mp3 \
  --diarization-backend local-cluster \
  --min-speakers 2 \
  --max-speakers 3
```

超过 30 分钟且已切成多个片段时，`--transcribe-jobs auto` 会根据 CPU 数量使用最多 3 个并行任务。可用 `--transcribe-jobs 1` 强制串行；Metal 不稳定时可用 `--whisper-no-gpu`，默认 `--gpu-preflight auto` 也会自动回退。

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

当前版本：`1.0.2`

发布 tag：`media_transcribe_public-1.0.2`

---

## English

`media-transcribe-public` is a local-first open-source audio/video transcription project with a bundled Codex skill. It turns local files or HTTP(S) media URLs into Markdown notes. The default path uses local `ffmpeg` + `whisper-cli`; remote transcription, speaker models, and third-party note publishing are explicit opt-in features.

Current version: `1.0.2`

## Features

- Transcribe local audio/video files or HTTP(S) media URLs.
- Use local `whisper.cpp` by default, with no OpenAI API key required.
- Normalize, segment, transcribe in parallel, and cache long media per segment so interrupted runs can resume.
- Probe whisper.cpp GPU/Metal before a run and retry on CPU after backend crashes; `--whisper-no-gpu` is also available.
- Optionally assign speaker labels through local sherpa-onnx neural diarization, whisper stereo diarization, or pyannote.
- Generate a Codex-ready Markdown note with title, timestamp, placeholders for core ideas and quotes, cleaned full text, and metadata.
- Infer draft punctuation from ASR timing and text cues; keep each speaker turn in one paragraph and start a new paragraph only when the speaker changes.
- Publish to local Markdown, Obsidian vaults, an optional Youdao-compatible backend, or cache only.

## When to Use

- Podcasts, interviews, meeting recordings, lectures, and video sources that need long-form transcription.
- Workflows where Codex should read the full transcript before producing core ideas, quotes, and cleaned full text.
- Users who want local-first processing and only opt into OpenAI, pyannote, Youdao, or other external services explicitly.
- Knowledge-management workflows that save output into Obsidian vaults or local Markdown folders.

## Inputs and Outputs

Inputs:

- Local audio or video files.
- HTTP(S) media URLs.
- Optional title, language, speaker-count hints, model path, and publishing backend.

Outputs:

- `transcript.txt`: raw transcript text.
- `segments.json`: timestamped ASR segments.
- `speaker_transcript.txt`: speaker-aware full-text draft.
- `note.md`: Codex-ready Markdown note.
- Optional publish result: local Markdown, Obsidian file, or Youdao note payload.

## Typical Prompts

```text
Use media-transcribe-public to transcribe this podcast into Markdown, save it to my local notes folder, and do not upload to remote services.
```

```text
Use media-transcribe-public to transcribe this interview, separate 2-3 speakers, and write the output to my Obsidian Transcripts folder.
```

## Common Failure Modes

- Publishing the first `note.md` draft directly: it usually still contains placeholders for core ideas and quotes.
- Treating CLI punctuation as final copy: the CLI only drafts punctuation; Codex should still perform the final cleanup.
- Enabling remote services by default: OpenAI, pyannote, and Youdao must be selected explicitly.
- Ignoring cache reuse: use `--force` or a fresh cache directory when testing punctuation, model, or diarization changes.
- Ignoring `speaker_turns_per_minute` in `meta.json`: values above 8 usually indicate fragmented labels and require review before publishing.

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
│       ├── agents/openai.yaml
│       └── references/gotchas.md
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

Local diarization uses sherpa-onnx with pyannote segmentation and a 3D-Speaker embedding ONNX model. This example uses an explicit model directory instead of relying on an OS-specific cache path:

```bash
export MEDIA_TRANSCRIBE_DIARIZATION_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/media-transcribe-public/diarization"
mkdir -p "$MEDIA_TRANSCRIBE_DIARIZATION_DIR"
curl -L -o "$MEDIA_TRANSCRIBE_DIARIZATION_DIR/segmentation.tar.bz2" \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-segmentation-models/sherpa-onnx-pyannote-segmentation-3-0.tar.bz2
tar -xjf "$MEDIA_TRANSCRIBE_DIARIZATION_DIR/segmentation.tar.bz2" \
  -C "$MEDIA_TRANSCRIBE_DIARIZATION_DIR"
curl -L -o "$MEDIA_TRANSCRIBE_DIARIZATION_DIR/3dspeaker_speech_eres2net_base_sv_zh-cn_3dspeaker_16k.onnx" \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-recongition-models/3dspeaker_speech_eres2net_base_sv_zh-cn_3dspeaker_16k.onnx
```

Alternatively, set `MEDIA_TRANSCRIBE_SEGMENTATION_MODEL` and `MEDIA_TRANSCRIBE_EMBEDDING_MODEL`, or pass `--speaker-segmentation-model` and `--speaker-embedding-model`.

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

Local neural diarization needs the sherpa-onnx extra and the two models above:

```bash
python3 -m pip install -e ".[diarization-cluster]"
media-transcribe-public input.mp3 \
  --diarization-backend local-cluster \
  --min-speakers 2 \
  --max-speakers 3
```

For media longer than 30 minutes with multiple segments, `--transcribe-jobs auto` selects up to three workers from the available CPUs. Use `--transcribe-jobs 1` for serial execution. Use `--whisper-no-gpu` on unstable Metal systems; the default `--gpu-preflight auto` also falls back automatically.

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

Current version: `1.0.2`

Release tag: `media_transcribe_public-1.0.2`
