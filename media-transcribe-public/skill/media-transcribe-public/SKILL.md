---
name: media-transcribe-public
description: Use when a user provides an audio or video file and wants a local-first Markdown transcript, Codex-ready summary draft, speaker-aware full text, or publishing to local files, Obsidian, or optional note backends.
---

# Media Transcribe Public

Use the packaged `media-transcribe-public` CLI for audio/video transcription workflows. Prefer local `whisper.cpp` and local Markdown output unless the user explicitly asks for a remote transcription backend or a third-party note backend.

## Workflow

1. Resolve the input media path or URL.
2. Run a dry-run before live transcription:

```bash
media-transcribe-public "/path/to/audio.mp3" --title "Note title" --dry-run
```

3. Run local transcription. Use `--no-polish` when Codex should fill the final editorial sections:

```bash
media-transcribe-public "/path/to/audio.mp3" \
  --title "Note title" \
  --language zh \
  --diarization-backend local-cluster \
  --min-speakers 2 \
  --max-speakers 3 \
  --note-backend local \
  --output-dir "./notes" \
  --no-polish
```

4. For Obsidian output:

```bash
media-transcribe-public "/path/to/audio.mp3" \
  --title "Note title" \
  --language zh \
  --note-backend obsidian \
  --vault-path "$OBSIDIAN_VAULT" \
  --vault-folder "Transcripts" \
  --no-polish
```

5. Read the generated `speaker_transcript.txt` and `note.md` from the returned `job_dir`. Codex should use its own capability to:
   - replace `## 核心观点` with 5-10 complete arguments;
   - replace `## 金句` with concise lines grounded in the transcript;
   - rewrite `## 清洗后全文` with better sentence breaks, punctuation, speaker-aware paragraphs, and simplified Chinese when the source is Chinese.
6. Save or publish the edited Markdown using the requested backend. Do not upload to OpenAI, Youdao, Notion, Feishu, or any other remote service unless the user explicitly chooses that backend.
7. Report the title, media duration, transcription backend, note backend, cache/job directory, local `note.md`, and any publish path or payload path.

## Backends

- `--note-backend local`: default local Markdown. With `--output-dir`, writes a copy outside the cache.
- `--note-backend obsidian`: writes Markdown into an Obsidian vault. Requires `--vault-path` or `OBSIDIAN_VAULT`; `--vault-folder` is optional.
- `--note-backend youdao`: optional compatibility backend. Requires the local `youdaonote` CLI and `--destination` with the parent folder ID.
- `--note-backend none`: only keep cache artifacts.

## Local Requirements

- `ffmpeg` and `ffprobe` on `PATH`.
- `whisper-cli` on `PATH` for the default `local-whisper-cpp` backend.
- A whisper.cpp GGML model at `~/.cache/whisper-cpp/ggml-small.bin`, `~/.cache/whisper-cpp/ggml-base.bin`, `WHISPER_CPP_MODEL`, or `--model-path`.
- Optional Chinese conversion: `opencc-python-reimplemented`.
- Optional local clustering diarization: `numpy`, `scipy`, `scikit-learn`.
- Optional pyannote diarization: `pyannote.audio` plus a Hugging Face token in `PYANNOTE_AUTH_TOKEN`, `HUGGINGFACE_TOKEN`, or `HF_TOKEN`.

## Output Format

The final note should remain Markdown:

```markdown
# {title}
整理时间：{YYYY-MM-DD}

## 核心观点
1. ...

## 金句
1. "..."

## 清洗后全文
**说话人A**：...
```

## Privacy Rules

- Default local transcription does not upload media.
- `--backend openai` uploads normalized media segments to OpenAI.
- `--note-backend youdao` uploads note Markdown through the local `youdaonote` CLI.
- Never print API keys, tokens, `.env` values, or note-service config file contents.
