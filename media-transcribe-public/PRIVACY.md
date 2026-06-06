# Privacy

`media-transcribe-public` is local-first by default, but some optional modes use remote services.

## Local Data

The CLI writes cache files containing transcript content and metadata:

- `transcript.txt`
- `segments.json`
- `diarization.json`
- `speaker_transcript.txt`
- `note.md`
- `meta.json`
- optional backend payloads such as `youdao_payload.json`

Default cache locations follow the operating system:

- macOS: `~/Library/Caches/media-transcribe-public`
- Linux: `${XDG_CACHE_HOME:-~/.cache}/media-transcribe-public`
- Windows: `%LOCALAPPDATA%\\media-transcribe-public` when available

Override with:

```bash
export MEDIA_TRANSCRIBE_CACHE_DIR=/path/to/cache
```

Delete the cache manually when transcripts should not remain on disk.

## Remote Services

- `--backend local-whisper-cpp` stays local.
- `--backend openai` uploads normalized media segments to OpenAI.
- `--diarization-backend pyannote` uses Hugging Face model access and may download model files.
- `--note-backend youdao` sends Markdown note content to Youdao through the local `youdaonote` CLI.
- `--note-backend obsidian` writes only to the local vault path.
- `--note-backend local` writes only to local disk.

## Secrets

Provide secrets through environment variables or service-specific local config files. Do not paste tokens into prompts, command logs, Markdown notes, or issue reports.

Recognized environment variables:

- `OPENAI_API_KEY`
- `PYANNOTE_AUTH_TOKEN`, `HUGGINGFACE_TOKEN`, or `HF_TOKEN`
- `OBSIDIAN_VAULT`
- `WHISPER_CPP_MODEL`
- `MEDIA_TRANSCRIBE_CACHE_DIR`
