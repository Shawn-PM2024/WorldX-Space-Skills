# Media Transcribe Public Gotchas

Use these checks when the user expects a publishable transcript note, not just raw transcription artifacts.

## Draft Quality

- Do not publish `note.md` while `核心观点` or `金句` still says "未启用模型整理".
- Do not treat CLI punctuation as final. The CLI infers commas, periods, and questions from ASR segment timing and text cues; Codex should still fix obvious mistakes.
- Do not remove speaker labels when diarization is useful. If diarization is unreliable, say so and keep neutral labels such as `说话人?`.
- Do not insert sentence-level line breaks inside one speaker turn. Keep its sentences in one paragraph and use one blank line only when the speaker changes.
- Do not convert oral transcript into a polished essay unless the user asks for rewriting.

## Local Neural Diarization

- Install the `diarization-cluster` extra, which provides `numpy`, `scipy`, and `sherpa-onnx`.
- Provide a sherpa-onnx pyannote segmentation model and speaker embedding model through `MEDIA_TRANSCRIBE_DIARIZATION_DIR`, the two `MEDIA_TRANSCRIBE_*_MODEL` variables, or the matching CLI flags.
- When the speaker count is known, pass the same number to `--min-speakers` and `--max-speakers`.
- The CLI invalidates diarization caches created by the former MFCC clustering engine. It keeps the Whisper transcript reusable.
- Inspect `speaker_turns_per_minute` in `meta.json`. More than 8 turns/minute is a review signal, not a publishable result.

## Backend Safety

- Do not use `--backend openai` unless the user explicitly accepts remote transcription.
- Do not use `--note-backend youdao` unless the user explicitly selects Youdao and has configured the local CLI.
- Do not infer an Obsidian vault path. Use `--vault-path` or `OBSIDIAN_VAULT`.
- Do not print API keys, Hugging Face tokens, `.env`, or note-service config files.

## Cache and Reuse

- If the CLI says it used cached transcript or note artifacts, inspect `meta.json` before assuming the current flags generated them.
- Use `--force` when testing a change to transcription, punctuation, diarization, or note generation.
- Without `--force`, normalized media, chunks, and completed whisper.cpp segment outputs under `job_dir/work` are reusable after interruption.
- `--transcribe-jobs auto` uses parallel workers only for long, multi-segment inputs. Lower it when RAM is limited.
- Keep the GPU preflight enabled on macOS. Use `--whisper-no-gpu` when Metal remains unstable; failed GPU segments retry once on CPU.
- For smoke tests, use a short clipped sample instead of transcribing a full multi-hour file.

## Completion Criteria

- Report `job_dir`, `note_path`, selected transcription backend, selected note backend, and publish result.
- For final notes, verify the Markdown opens with `# {title}`, includes `整理时间`, and has completed `核心观点`, `金句`, and `清洗后全文`.
- For Obsidian output, confirm the Markdown file lands inside the vault, not next to it.
