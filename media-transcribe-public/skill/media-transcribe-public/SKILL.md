---
name: media-transcribe-public
description: Use when a user provides an audio or video file and wants local-first transcription into a Codex-ready Markdown note, speaker-aware draft text, or publishing to local files, Obsidian, or an explicitly selected note backend.
---

# Media Transcribe Public

Use the packaged `media-transcribe-public` CLI to turn audio/video into a Markdown transcript draft. Keep the default path local unless the user explicitly chooses OpenAI transcription or a remote note backend.

## Workflow

1. Resolve the input media path or URL.
2. Dry-run first:

```bash
media-transcribe-public "/path/to/audio.mp3" --title "Note title" --dry-run
```

3. Produce a Codex-ready draft. Use `--no-polish`; Codex should do the editorial pass:

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

4. For Obsidian:

```bash
media-transcribe-public "/path/to/audio.mp3" \
  --title "Note title" \
  --language zh \
  --note-backend obsidian \
  --vault-path "$OBSIDIAN_VAULT" \
  --vault-folder "Transcripts" \
  --no-polish
```

5. Read `speaker_transcript.txt`, `note.md`, `segments.json`, and `meta.json` from the returned `job_dir`.
6. Check `speaker_count`, `speaker_turns`, and `speaker_turns_per_minute` in `meta.json`. Treat more than 8 turns/minute as unreliable diarization that needs review.
7. Codex fills `核心观点`, `金句`, and final `清洗后全文`; the CLI handles deterministic media work and draft structure.
8. In `清洗后全文`, keep each speaker turn as exactly one paragraph. Retain sentence punctuation inside the turn, but start a new paragraph only when the speaker changes.
9. Publish only to the backend the user selected.

## Backend Rules

- Default: `--note-backend local`, or `none` if the user only wants cache artifacts.
- Obsidian: require `--vault-path` or `OBSIDIAN_VAULT`.
- Youdao: require configured `youdaonote` CLI and `--destination`.
- OpenAI transcription: require `--backend openai` and `OPENAI_API_KEY`.
- Never upload media or notes to remote services by implication.

## Runtime Rules

- Long segmented files use `--transcribe-jobs auto` by default, with at most three local whisper.cpp workers. Use `--transcribe-jobs 1` when memory is constrained.
- Keep `--gpu-preflight auto` unless the user explicitly disables it. If Metal is unstable, use `--whisper-no-gpu`; segment failures also retry on CPU automatically.
- `local-cluster` means sherpa-onnx neural diarization. It requires the `diarization-cluster` extra and configurable segmentation/embedding ONNX model paths; read the gotchas reference for setup.
- The persistent `job_dir/work` cache allows completed normalization, segmentation, and per-segment Whisper outputs to resume. Use `--force` only when stale results must be discarded.

## Editorial Contract

Codex should:

- replace `## 核心观点` with 5-10 transcript-grounded arguments;
- replace `## 金句` with concise lines grounded in the transcript;
- rewrite `## 清洗后全文` with speaker labels, natural paragraphing, punctuation cleanup, and simplified Chinese when appropriate;
- preserve one paragraph per speaker turn, including multiple complete sentences within that paragraph;
- keep the oral tone instead of turning the transcript into a generic article.

## Gotchas

Read [references/gotchas.md](references/gotchas.md) when the transcript is long, multi-speaker, cached, or intended for publication.

Minimum checks before reporting done:

- `note.md` exists and has no placeholder sections when final output is requested.
- `speaker_transcript.txt` exists for transcript review.
- remote backends were explicitly requested.
- secrets, `.env`, and local note-service config were not printed.

## Output Contract

```markdown
# {title}
整理时间：{YYYY-MM-DD}

## 核心观点
1. ...

## 金句
1. "..."

## 清洗后全文
**说话人A**：...

## 元信息
- 媒体时长：...
```
