# media-transcribe-public

Local-first audio/video transcription to Markdown. The default path uses local `ffmpeg` + `whisper-cli` and writes Markdown locally; remote transcription and third-party note publishing are opt-in.

## Features

- Transcribe audio/video files or HTTP(S) media URLs.
- Use local `whisper.cpp` by default, or OpenAI transcription when explicitly selected.
- Segment long media files before transcription.
- Optionally assign speaker labels with local clustering, whisper stereo diarization, or pyannote.
- Generate a Codex-ready Markdown note with transcript, speaker-aware draft text, metadata, and placeholders for editorial summary.
- Publish to `local`, `obsidian`, `youdao`, or `none`.

## Install

```bash
python3 -m pip install -e ".[zh,diarization-cluster,dev]"
```

Required system tools for local transcription:

```bash
# macOS
brew install ffmpeg whisper-cpp

# Linux: install ffmpeg and whisper.cpp using your distro/package manager or from source.
# Windows: install ffmpeg.exe and whisper-cli.exe, then add both to PATH.
```

Download a multilingual whisper.cpp GGML model:

```bash
mkdir -p ~/.cache/whisper-cpp
curl -L -o ~/.cache/whisper-cpp/ggml-small.bin \
  https://mirrors.mit.edu/macports/distfiles/whisper/ggml-small.bin
```

You can also set `WHISPER_CPP_MODEL=/path/to/ggml-model.bin` or pass `--model-path`.

## Quick Start

Write the generated Markdown note to the cache only:

```bash
media-transcribe-public input.mp3 --language zh --note-backend none --no-polish
```

Write a copy to a local folder:

```bash
media-transcribe-public input.mp3 \
  --title "Podcast Episode" \
  --language zh \
  --note-backend local \
  --output-dir ./notes \
  --no-polish
```

Write to Obsidian:

```bash
media-transcribe-public input.mp3 \
  --title "Interview Notes" \
  --language zh \
  --note-backend obsidian \
  --vault-path "$OBSIDIAN_VAULT" \
  --vault-folder "Transcripts" \
  --no-polish
```

Write to Youdao Note with an existing `youdaonote` CLI setup:

```bash
media-transcribe-public input.mp3 \
  --title "Podcast Notes" \
  --language zh \
  --note-backend youdao \
  --destination "YOUR_YOUDAO_PARENT_FOLDER_ID" \
  --no-polish
```

## Optional Backends

OpenAI transcription uploads audio segments to OpenAI:

```bash
export OPENAI_API_KEY="..."
media-transcribe-public input.mp3 --backend openai --model gpt-4o-mini-transcribe
```

pyannote diarization uses a local Python package and Hugging Face model access:

```bash
python3 -m pip install -e ".[diarization-pyannote]"
export PYANNOTE_AUTH_TOKEN="..."
media-transcribe-public input.mp3 --diarization-backend pyannote --min-speakers 2 --max-speakers 4
```

Local clustering diarization stays local but needs numerical Python packages:

```bash
python3 -m pip install -e ".[diarization-cluster]"
media-transcribe-public input.mp3 --diarization-backend local-cluster --min-speakers 2 --max-speakers 3
```

## Codex Skill

The project includes a Codex skill at:

```text
skill/media-transcribe-public/
```

Install or copy that folder into your Codex skills directory when you want Codex to use the packaged CLI as a reusable workflow.

## Notes

- The CLI does not bundle FFmpeg, whisper.cpp, GGML models, pyannote models, or any note-service credentials.
- `--no-polish` is recommended for Codex workflows because Codex should fill `核心观点`, `金句`, and final sentence formatting after reading `speaker_transcript.txt`.
- The old private skill's `--skip-youdao` and `--folder-id` flags are accepted for migration but are not documented as the primary interface.
