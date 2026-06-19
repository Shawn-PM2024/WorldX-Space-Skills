# Media Transcribe Public Gotchas

Use these checks when the user expects a publishable transcript note, not just raw transcription artifacts.

## Draft Quality

- Do not publish `note.md` while `核心观点` or `金句` still says "未启用模型整理".
- Do not treat CLI punctuation as final. The CLI infers commas, periods, and questions from ASR segment timing and text cues; Codex should still fix obvious mistakes.
- Do not remove speaker labels when diarization is useful. If diarization is unreliable, say so and keep neutral labels such as `说话人?`.
- Do not convert oral transcript into a polished essay unless the user asks for rewriting.

## Backend Safety

- Do not use `--backend openai` unless the user explicitly accepts remote transcription.
- Do not use `--note-backend youdao` unless the user explicitly selects Youdao and has configured the local CLI.
- Do not infer an Obsidian vault path. Use `--vault-path` or `OBSIDIAN_VAULT`.
- Do not print API keys, Hugging Face tokens, `.env`, or note-service config files.

## Cache and Reuse

- If the CLI says it used cached transcript or note artifacts, inspect `meta.json` before assuming the current flags generated them.
- Use `--force` when testing a change to transcription, punctuation, diarization, or note generation.
- For smoke tests, use a short clipped sample instead of transcribing a full multi-hour file.

## Completion Criteria

- Report `job_dir`, `note_path`, selected transcription backend, selected note backend, and publish result.
- For final notes, verify the Markdown opens with `# {title}`, includes `整理时间`, and has completed `核心观点`, `金句`, and `清洗后全文`.
- For Obsidian output, confirm the Markdown file lands inside the vault, not next to it.
