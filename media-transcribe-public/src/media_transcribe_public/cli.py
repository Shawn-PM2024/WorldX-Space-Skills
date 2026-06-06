#!/usr/bin/env python3
"""Transcribe media and save a cleaned Markdown note with local-first backends."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import unquote, urlparse
from urllib.request import urlretrieve

DEFAULT_TRANSCRIBE_MODEL = "gpt-4o-mini-transcribe"
DEFAULT_POLISH_MODEL = "gpt-4.1-mini"
DEFAULT_DIARIZATION_MODEL = "pyannote/speaker-diarization-3.1"
DEFAULT_WHISPER_CPP_MODEL = Path.home() / ".cache/whisper-cpp/ggml-small.bin"
FALLBACK_WHISPER_CPP_MODEL = Path.home() / ".cache/whisper-cpp/ggml-base.bin"
MAX_SEGMENT_BYTES = 24 * 1024 * 1024
DEFAULT_SEGMENT_SECONDS = 20 * 60
BACKENDS = {"local-whisper-cpp", "openai"}
DIARIZATION_BACKENDS = {"none", "local-cluster", "pyannote", "whisper-stereo"}
NOTE_BACKENDS = {"none", "local", "obsidian", "youdao"}

AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".opus"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v"}


def default_cache_dir() -> Path:
    if os.getenv("MEDIA_TRANSCRIBE_CACHE_DIR"):
        return Path(os.environ["MEDIA_TRANSCRIBE_CACHE_DIR"]).expanduser()
    if sys.platform == "darwin":
        return Path.home() / "Library/Caches/media-transcribe-public"
    if os.name == "nt":
        base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        return Path(base).expanduser() / "media-transcribe-public" if base else Path.home() / ".cache/media-transcribe-public"
    return Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache")) / "media-transcribe-public"


def die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


def run(cmd: List[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def require_command(name: str) -> str:
    path = shutil.which(name)
    if not path:
        die(f"`{name}` is not installed or not on PATH")
    return path


def ensure_openai_key(dry_run: bool = False) -> None:
    if os.getenv("OPENAI_API_KEY"):
        return
    if dry_run:
        warn("OPENAI_API_KEY is not set; dry-run will not call OpenAI.")
        return
    die("OPENAI_API_KEY is not set. Export it in your shell before transcribing.")


def ensure_dependencies(note_backend: str, backend: str) -> None:
    require_command("ffmpeg")
    require_command("ffprobe")
    if backend == "local-whisper-cpp":
        require_command("whisper-cli")
    if note_backend == "youdao":
        require_command("youdaonote")
        try:
            run(["youdaonote", "check"], capture=True)
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or exc.stdout or "").strip()
            die(f"`youdaonote check` failed. {detail}")


def is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def download_url(url: str, work_dir: Path) -> Path:
    parsed = urlparse(url)
    name = unquote(Path(parsed.path).name) or "downloaded-media.mp3"
    if not Path(name).suffix:
        name += ".mp3"
    target = work_dir / name
    print(f"Downloading URL to {target}", file=sys.stderr)
    urlretrieve(url, target)
    return target


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ffprobe(path: Path) -> Dict[str, Any]:
    try:
        result = run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration,size,format_name",
                "-of",
                "json",
                str(path),
            ],
            capture=True,
        )
    except subprocess.CalledProcessError as exc:
        die(f"ffprobe failed for {path}: {(exc.stderr or '').strip()}")
    data = json.loads(result.stdout)
    fmt = data.get("format") or {}
    return {
        "duration": float(fmt.get("duration") or 0),
        "size": int(fmt.get("size") or path.stat().st_size),
        "format": fmt.get("format_name") or "",
    }


def format_duration(seconds: float) -> str:
    total = int(round(seconds))
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    if hours:
        return f"{hours}小时{minutes}分钟{secs}秒"
    if minutes:
        return f"{minutes}分钟{secs}秒"
    return f"{secs}秒"


def safe_title(value: str) -> str:
    title = re.sub(r"\s+", " ", value).strip()
    title = re.sub(r"[\\/:*?\"<>|]+", "-", title)
    return title[:180] or "media-transcribe"


def normalize_media(input_path: Path, work_dir: Path, *, channels: int = 1) -> Path:
    ext = input_path.suffix.lower()
    if ext not in AUDIO_EXTS and ext not in VIDEO_EXTS:
        die(f"Unsupported media format: {input_path.suffix}")
    output = work_dir / f"{input_path.stem}.normalized.mp3"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        str(channels),
        "-ar",
        "16000",
        "-b:a",
        "32k",
        str(output),
    ]
    print(f"Normalizing media to {output}", file=sys.stderr)
    try:
        run(cmd, capture=True)
    except subprocess.CalledProcessError as exc:
        die(f"ffmpeg normalization failed: {(exc.stderr or '').strip()}")
    return output


def segment_media(normalized_path: Path, work_dir: Path, segment_seconds: int) -> List[Path]:
    info = ffprobe(normalized_path)
    if info["size"] <= MAX_SEGMENT_BYTES and info["duration"] <= segment_seconds:
        return [normalized_path]
    pattern = work_dir / "segment_%03d.mp3"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(normalized_path),
        "-f",
        "segment",
        "-segment_time",
        str(segment_seconds),
        "-c",
        "copy",
        str(pattern),
    ]
    print(f"Segmenting media every {segment_seconds}s", file=sys.stderr)
    try:
        run(cmd, capture=True)
    except subprocess.CalledProcessError as exc:
        die(f"ffmpeg segmentation failed: {(exc.stderr or '').strip()}")
    segments = sorted(work_dir.glob("segment_*.mp3"))
    if not segments:
        die("ffmpeg did not produce any segments")
    oversized = [p for p in segments if p.stat().st_size > MAX_SEGMENT_BYTES]
    if oversized:
        names = ", ".join(p.name for p in oversized[:3])
        die(f"Segment still exceeds 24MB; reduce --segment-seconds. Oversized: {names}")
    return segments


def create_openai_client() -> Any:
    try:
        from openai import OpenAI
    except ImportError:
        die("openai SDK is not installed. Install it with `python3 -m pip install openai`.")
    return OpenAI()


def transcribe_segments(
    segments: List[Path],
    *,
    model: str,
    language: Optional[str],
    prompt: Optional[str],
) -> str:
    ensure_openai_key()
    client = create_openai_client()
    parts: List[str] = []
    for index, segment in enumerate(segments, start=1):
        print(f"Transcribing segment {index}/{len(segments)}: {segment.name}", file=sys.stderr)
        payload: Dict[str, Any] = {"model": model, "response_format": "text"}
        if language:
            payload["language"] = language
        if prompt:
            payload["prompt"] = prompt
        with segment.open("rb") as audio:
            result = client.audio.transcriptions.create(file=audio, **payload)
        text = getattr(result, "text", None)
        parts.append(text if isinstance(text, str) else str(result))
    return "\n\n".join(part.strip() for part in parts if part.strip())


def resolve_whisper_cpp_model(model_path: Optional[str]) -> Path:
    candidates = []
    if model_path:
        candidates.append(Path(model_path).expanduser())
    if os.getenv("WHISPER_CPP_MODEL"):
        candidates.append(Path(os.environ["WHISPER_CPP_MODEL"]).expanduser())
    candidates.append(DEFAULT_WHISPER_CPP_MODEL)
    candidates.append(FALLBACK_WHISPER_CPP_MODEL)

    for candidate in candidates:
        if candidate.exists() and candidate.stat().st_size > 0:
            return candidate
    die(
        "No whisper.cpp model found. Download one, for example: "
        f"`curl -L -o {DEFAULT_WHISPER_CPP_MODEL} "
        "https://mirrors.mit.edu/macports/distfiles/whisper/ggml-small.bin`"
    )


def transcribe_segments_whisper_cpp(
    segments: List[Path],
    *,
    model_path: Optional[str],
    language: Optional[str],
    threads: int,
    diarize: bool = False,
) -> tuple[str, List[Dict[str, Any]]]:
    model = resolve_whisper_cpp_model(model_path)
    parts: List[str] = []
    transcript_segments: List[Dict[str, Any]] = []
    offset_ms = 0
    for index, segment in enumerate(segments, start=1):
        out_base = segment.with_suffix("")
        txt_path = Path(str(out_base) + ".txt")
        json_path = Path(str(out_base) + ".json")
        if txt_path.exists():
            txt_path.unlink()
        if json_path.exists():
            json_path.unlink()
        lang = language or "auto"
        cmd = [
            "whisper-cli",
            "-m",
            str(model),
            "-f",
            str(segment),
            "-l",
            lang,
            "-t",
            str(threads),
            "-otxt",
            "-oj",
            "-ojf",
            "-of",
            str(out_base),
            "-np",
        ]
        if diarize:
            cmd.append("-di")
        print(
            f"Transcribing segment {index}/{len(segments)} locally with whisper.cpp: {segment.name}",
            file=sys.stderr,
        )
        try:
            completed = run(cmd, capture=True)
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or exc.stdout or "").strip()
            die(f"whisper.cpp transcription failed: {detail}")
        if txt_path.exists():
            text = txt_path.read_text(encoding="utf-8", errors="replace")
        else:
            text = completed.stdout
        parts.append(strip_timestamps(text))
        transcript_segments.extend(parse_whisper_json_segments(json_path, offset_ms=offset_ms))
        offset_ms += int(round(ffprobe(segment)["duration"] * 1000))
    return "\n\n".join(part.strip() for part in parts if part.strip()), transcript_segments


def parse_whisper_json_segments(json_path: Path, *, offset_ms: int = 0) -> List[Dict[str, Any]]:
    if not json_path.exists():
        return []
    try:
        data = json.loads(json_path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError) as exc:
        warn(f"Could not parse whisper.cpp JSON {json_path.name}: {exc}")
        return []
    segments = []
    for item in data.get("transcription", []):
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        offsets = item.get("offsets") or {}
        start_ms = int(offsets.get("from") or 0) + offset_ms
        end_ms = int(offsets.get("to") or start_ms) + offset_ms
        speaker = item.get("speaker")
        if speaker in ("", "?", None):
            speaker = None
        segments.append(
            {
                "start": start_ms / 1000,
                "end": max(end_ms, start_ms) / 1000,
                "text": strip_timestamps(text),
                "speaker": speaker,
            }
        )
    return segments


def strip_timestamps(text: str) -> str:
    text = re.sub(r"\[\d{1,2}:\d{2}(?::\d{2})?\]", "", text)
    text = re.sub(r"^\s*(?:\d{1,2}:)?\d{1,2}:\d{2}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def to_simplified(text: str) -> str:
    try:
        from opencc import OpenCC
    except ImportError:
        return text
    return OpenCC("t2s").convert(text)


def run_pyannote_diarization(
    audio_path: Path,
    *,
    model_name: str,
    min_speakers: Optional[int],
    max_speakers: Optional[int],
    rttm_path: Path,
) -> List[Dict[str, Any]]:
    token = (
        os.getenv("PYANNOTE_AUTH_TOKEN")
        or os.getenv("HUGGINGFACE_TOKEN")
        or os.getenv("HF_TOKEN")
    )
    if not token:
        warn("PYANNOTE_AUTH_TOKEN/HUGGINGFACE_TOKEN/HF_TOKEN is not set; skipping pyannote diarization.")
        return []
    try:
        from pyannote.audio import Pipeline
    except ImportError:
        warn("pyannote.audio is not installed; install it to use --diarization-backend pyannote.")
        return []

    print(f"Running local pyannote diarization with {model_name}", file=sys.stderr)
    try:
        pipeline = Pipeline.from_pretrained(model_name, use_auth_token=token)
        kwargs: Dict[str, Any] = {}
        if min_speakers:
            kwargs["min_speakers"] = min_speakers
        if max_speakers:
            kwargs["max_speakers"] = max_speakers
        diarization = pipeline(str(audio_path), **kwargs)
    except Exception as exc:  # pyannote raises several model/auth/runtime exceptions
        warn(f"pyannote diarization failed: {exc}")
        return []

    segments: List[Dict[str, Any]] = []
    with rttm_path.open("w", encoding="utf-8") as handle:
        diarization.write_rttm(handle)
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({"start": float(turn.start), "end": float(turn.end), "speaker": str(speaker)})
    return sorted(segments, key=lambda item: (item["start"], item["end"]))


def run_local_cluster_diarization(
    audio_path: Path,
    transcript_segments: List[Dict[str, Any]],
    *,
    work_dir: Path,
    min_speakers: Optional[int],
    max_speakers: Optional[int],
) -> List[Dict[str, Any]]:
    """Best-effort local speaker clustering from Whisper segment time ranges."""
    try:
        import numpy as np
        from scipy.fftpack import dct
        from scipy.io import wavfile
        from scipy.signal import spectrogram
        from sklearn.cluster import AgglomerativeClustering
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        warn(f"Local clustering dependencies are missing ({exc}); skipping diarization.")
        return []

    wav_path = work_dir / "diarization-analysis.wav"
    try:
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(audio_path),
                "-vn",
                "-ac",
                "1",
                "-ar",
                "16000",
                str(wav_path),
            ],
            capture=True,
        )
    except subprocess.CalledProcessError as exc:
        warn(f"Could not prepare audio for local clustering: {(exc.stderr or '').strip()}")
        return []

    sample_rate, samples = wavfile.read(str(wav_path))
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    samples = samples.astype("float32")
    peak = float(np.max(np.abs(samples)) or 1.0)
    samples = samples / peak

    def hz_to_mel(hz: float) -> float:
        return 2595.0 * np.log10(1.0 + hz / 700.0)

    def mel_to_hz(mel: np.ndarray) -> np.ndarray:
        return 700.0 * (10 ** (mel / 2595.0) - 1.0)

    def mel_filterbank(n_fft: int = 512, n_mels: int = 24) -> np.ndarray:
        mel_points = np.linspace(hz_to_mel(80), hz_to_mel(sample_rate / 2), n_mels + 2)
        hz_points = mel_to_hz(mel_points)
        bins = np.floor((n_fft + 1) * hz_points / sample_rate).astype(int)
        filters = np.zeros((n_mels, n_fft // 2 + 1), dtype="float32")
        for idx in range(1, n_mels + 1):
            left, center, right = bins[idx - 1], bins[idx], bins[idx + 1]
            if center <= left or right <= center:
                continue
            filters[idx - 1, left:center] = (np.arange(left, center) - left) / (center - left)
            filters[idx - 1, center:right] = (right - np.arange(center, right)) / (right - center)
        return filters

    filters = mel_filterbank()

    def feature_for(start: float, end: float) -> Optional[np.ndarray]:
        start_i = max(0, int(start * sample_rate))
        end_i = min(len(samples), int(end * sample_rate))
        if end_i - start_i < sample_rate // 2:
            return None
        clip = samples[start_i:end_i]
        freqs, _, spec = spectrogram(
            clip,
            fs=sample_rate,
            window="hann",
            nperseg=512,
            noverlap=256,
            nfft=512,
            mode="magnitude",
        )
        power = spec ** 2
        mel_energy = np.maximum(filters @ power, 1e-10)
        mfcc = dct(np.log(mel_energy), type=2, axis=0, norm="ortho")[:13]
        zcr = np.mean(np.abs(np.diff(np.signbit(clip))).astype("float32"))
        energy = np.log(np.mean(clip ** 2) + 1e-8)
        centroid = np.mean((freqs[:, None] * power).sum(axis=0) / (power.sum(axis=0) + 1e-8))
        return np.concatenate(
            [
                mfcc.mean(axis=1),
                mfcc.std(axis=1),
                np.array([zcr, energy, centroid / (sample_rate / 2)], dtype="float32"),
            ]
        )

    rows: List[Dict[str, Any]] = []
    features: List[Any] = []
    for segment in transcript_segments:
        text = str(segment.get("text") or "").strip()
        if not text:
            continue
        start = float(segment.get("start") or 0)
        end = float(segment.get("end") or start)
        feature = feature_for(start, end)
        if feature is None:
            continue
        rows.append({"start": start, "end": end, "text": text})
        features.append(feature)

    if len(rows) < 2:
        return []

    requested_min = min_speakers or 2
    requested_max = max_speakers or requested_min
    n_clusters = max(requested_min, min(requested_max, len(rows)))
    n_clusters = min(n_clusters, len(rows))
    if n_clusters < 2:
        return []

    matrix = StandardScaler().fit_transform(np.vstack(features))
    labels = AgglomerativeClustering(n_clusters=n_clusters).fit_predict(matrix)
    diarized = []
    for row, label in zip(rows, labels):
        diarized.append({"start": row["start"], "end": row["end"], "speaker": f"cluster_{int(label)}"})
    return diarized


def normalize_speaker_labels(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    mapping: Dict[str, str] = {}
    next_index = 0
    for segment in segments:
        speaker = segment.get("speaker")
        if not speaker:
            continue
        raw = str(speaker)
        if raw not in mapping:
            mapping[raw] = f"说话人{chr(ord('A') + next_index)}"
            next_index += 1
        segment["speaker"] = mapping[raw]
    return segments


def assign_speakers(
    transcript_segments: List[Dict[str, Any]],
    diarization_segments: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if not transcript_segments:
        return []
    if not diarization_segments:
        return normalize_speaker_labels([dict(segment) for segment in transcript_segments])

    assigned: List[Dict[str, Any]] = []
    for segment in transcript_segments:
        best_speaker = None
        best_overlap = 0.0
        start = float(segment.get("start") or 0)
        end = float(segment.get("end") or start)
        for diarized in diarization_segments:
            overlap = max(0.0, min(end, diarized["end"]) - max(start, diarized["start"]))
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = diarized["speaker"]
        item = dict(segment)
        if best_speaker:
            item["speaker"] = best_speaker
        assigned.append(item)
    return normalize_speaker_labels(assigned)


def speaker_transcript_from_segments(segments: List[Dict[str, Any]], fallback_text: str) -> str:
    if not segments:
        return punctuate_zh_text(fallback_text)

    paragraphs: List[str] = []
    current_speaker: Optional[str] = None
    current_segments: List[Dict[str, Any]] = []
    for segment in segments:
        text = str(segment.get("text") or "").strip()
        if not text:
            continue
        speaker = segment.get("speaker") or "说话人?"
        if current_speaker and speaker != current_speaker and current_segments:
            paragraphs.append(f"**{current_speaker}**：{punctuate_segment_group(current_segments)}")
            current_segments = []
        current_speaker = str(speaker)
        current_segments.append(dict(segment))
    if current_speaker and current_segments:
        paragraphs.append(f"**{current_speaker}**：{punctuate_segment_group(current_segments)}")
    return "\n\n".join(paragraphs).strip() or punctuate_zh_text(fallback_text)


def normalize_asr_spacing(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", text)
    text = re.sub(r"\s*([，。！？；：、,.!?;:])\s*", r"\1", text)
    return text.strip()


def split_on_existing_punctuation(text: str) -> List[str]:
    parts: List[str] = []
    current: List[str] = []
    for char in text:
        current.append(char)
        if char in "。！？!?；;":
            parts.append("".join(current).strip())
            current = []
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def is_question_clause(chunk: str, prev_text: str = "", next_text: str = "") -> bool:
    if prev_text and "你说的是" in prev_text and chunk.startswith("还是"):
        return True
    if "你说的是" in chunk and not next_text.startswith("还是"):
        return True
    question_patterns = (
        "吗",
        "呢",
        "是不是",
        "有没有",
        "为什么",
        "怎么",
        "什么",
        "哪里",
        "哪",
        "谁",
        "多少",
        "对吧",
        "是吧",
        "还是说",
    )
    return any(pattern in chunk for pattern in question_patterns)


def is_incomplete_clause(chunk: str) -> bool:
    incomplete_starts = (
        "像",
        "对我来说",
        "我觉得",
        "等会",
        "这个话",
        "这也是",
        "而如果",
        "如果",
        "因为",
        "所以",
    )
    incomplete_ends = (
        "的时候",
        "的话",
        "之后",
        "以前",
        "这",
    )
    return chunk.startswith(incomplete_starts) or chunk.endswith(incomplete_ends)


def sentence_mark(chunk: str, *, is_tail: bool = True, prev_text: str = "", next_text: str = "") -> str:
    if is_question_clause(chunk, prev_text=prev_text, next_text=next_text):
        return "？"
    if not is_tail or is_incomplete_clause(chunk):
        return "，"
    return "。"


def combine_punctuated_units(units: List[str]) -> str:
    lines: List[str] = []
    current = ""
    for unit in units:
        if not unit:
            continue
        current += unit
        if unit[-1] in "。！？!?；;":
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return "\n".join(lines)


def segment_mark(
    item: Dict[str, Any],
    prev_item: Optional[Dict[str, Any]],
    next_item: Optional[Dict[str, Any]],
) -> str:
    text = normalize_asr_spacing(to_simplified(str(item.get("text") or ""))).strip("，,。 ")
    prev_text = normalize_asr_spacing(to_simplified(str(prev_item.get("text") or ""))) if prev_item else ""
    next_text = normalize_asr_spacing(to_simplified(str(next_item.get("text") or ""))) if next_item else ""
    if is_question_clause(text, prev_text=prev_text, next_text=next_text):
        return "？"

    if next_item is None:
        return "。" if not is_incomplete_clause(text) else ""

    gap = max(0.0, float(next_item.get("start") or 0) - float(item.get("end") or 0))
    if gap >= 0.75:
        return "。"
    if next_text.startswith(("等会", "而如果", "这也是", "但后来")) and not is_incomplete_clause(text):
        return "。"
    if next_text.startswith(("还是", "第二", "第三")):
        return "，"
    if is_incomplete_clause(text):
        return "，"
    if len(text) >= 28 and gap >= 0.35:
        return "。"
    return "，"


def punctuate_segment_group(segments: List[Dict[str, Any]]) -> str:
    units: List[str] = []
    for index, item in enumerate(segments):
        text = normalize_asr_spacing(to_simplified(strip_timestamps(str(item.get("text") or "")))).strip("，,。 ")
        if not text:
            continue
        trailing = text[-1] if text[-1] in "。！？!?；;，," else ""
        body = text[:-1] if trailing else text
        if trailing:
            mark = "，" if trailing == "," else trailing
        else:
            prev_item = segments[index - 1] if index > 0 else None
            next_item = segments[index + 1] if index + 1 < len(segments) else None
            mark = segment_mark(item, prev_item, next_item)
        units.append(body + mark)
    return combine_punctuated_units(units)


def split_unpunctuated_clause(text: str, *, min_len: int = 8, max_len: int = 34) -> List[str]:
    strong_before = (
        "等会",
        "但是",
        "但",
        "不过",
        "所以",
        "因为",
        "如果",
        "其实",
        "我觉得",
        "对我来说",
        "就是说",
        "当然",
        "比如",
        "而且",
        "那么",
        "另外",
        "后来",
        "换句话说",
        "第一",
        "第二",
        "第三",
        "还是说",
        "还是",
        "这个",
        "这个话",
        "这也是",
        "那肯定",
    )
    soft_after = (
        "对吧",
        "是吧",
        "是不是",
        "有没有",
        "的时候",
        "的话",
        "之后",
        "以后",
    )

    compact = normalize_asr_spacing(text).strip("，,。 ")
    if not compact:
        return []

    chunks: List[str] = []
    start = 0
    i = 0
    while i < len(compact):
        current_len = i - start
        remaining = len(compact) - i
        should_break = False
        break_at = i

        for cue in strong_before:
            if compact.startswith(cue, i) and current_len >= min_len and remaining >= min_len:
                should_break = True
                break

        if not should_break:
            for cue in soft_after:
                cue_end = i + len(cue)
                if compact.startswith(cue, i) and cue_end - start >= min_len and len(compact) - cue_end >= min_len:
                    should_break = True
                    break_at = cue_end
                    break

        if not should_break and current_len >= max_len:
            should_break = True
            break_at = i

        if should_break:
            chunk = compact[start:break_at].strip("，,。 ")
            if chunk:
                chunks.append(chunk + sentence_mark(chunk, is_tail=False))
            start = break_at
            i = max(start, i)
        i += 1

    tail = compact[start:].strip("，,。 ")
    if tail:
        mark = "" if re.search(r"[。！？!?；;]$", tail) else sentence_mark(tail, is_tail=True)
        chunks.append(tail + mark)
    return chunks


def punctuate_zh_text(text: str) -> str:
    """Add sentence breaks and punctuation to Chinese ASR text."""
    text = to_simplified(strip_timestamps(text))
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    punctuated: List[str] = []

    for paragraph in paragraphs:
        sentences: List[str] = []
        lines = [line.strip() for line in re.split(r"\n+", paragraph) if line.strip()]
        for line in lines:
            normalized = normalize_asr_spacing(line)
            for part in split_on_existing_punctuation(normalized):
                trailing = part[-1] if part and part[-1] in "。！？!?；;" else ""
                body = part[:-1] if trailing else part
                if len(body) > 28 or not trailing:
                    sentences.append(combine_punctuated_units(split_unpunctuated_clause(body)))
                elif body:
                    sentences.append(body + trailing)
        if sentences:
            punctuated.append(combine_punctuated_units(sentences))

    return "\n\n".join(punctuated).strip()


def fallback_note(
    title: str,
    transcript: str,
    media_info: Dict[str, Any],
    *,
    cleaned_text: Optional[str] = None,
) -> str:
    cleaned = cleaned_text or punctuate_zh_text(transcript)
    today = datetime.now().strftime("%Y-%m-%d")
    return "\n".join(
        [
            f"# {title}",
            f"整理时间：{today}",
            "",
            "## 核心观点",
            "1. 未启用模型整理；请基于下方全文补充核心观点。",
            "",
            "## 金句",
            "1. 未启用模型整理；请基于下方全文补充金句。",
            "",
            "## 清洗后全文",
            cleaned,
            "",
            "## 元信息",
            f"- 媒体时长：{format_duration(media_info.get('duration', 0))}",
        ]
    )


def extract_response_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()
    if hasattr(response, "model_dump"):
        data = response.model_dump()
        texts: List[str] = []
        for item in data.get("output", []):
            for content in item.get("content", []):
                text = content.get("text")
                if text:
                    texts.append(text)
        if texts:
            return "\n".join(texts).strip()
    return str(response).strip()


def polish_note(title: str, transcript: str, media_info: Dict[str, Any], model: str) -> str:
    ensure_openai_key()
    client = create_openai_client()
    today = datetime.now().strftime("%Y-%m-%d")
    system = (
        "你是中文音频转写整理助手。输出必须是完整 Markdown，不要解释。"
        "轻清洗：去时间戳、去片尾歌或广告、统一简体、修正明显 ASR 错误，保留口语感。"
        "核心观点写 5-10 条完整论点；金句保留原文表达并加引号。"
    )
    user = f"""请把以下转写整理成指定格式。

标题：{title}
整理时间：{today}
媒体时长：{format_duration(media_info.get('duration', 0))}

必须使用这个结构：
# {title}
整理时间：{today}

## 核心观点
1. ...

## 金句
1. "..."

## 清洗后全文
...

转写原文：
{transcript}
"""
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    note = extract_response_text(response)
    if not note.startswith("# "):
        warn("Polish response did not start with a Markdown title; using fallback note.")
        return fallback_note(title, transcript, media_info)
    return note


def unique_markdown_path(directory: Path, title: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    base = safe_title(title)
    candidate = directory / f"{base}.md"
    index = 2
    while candidate.exists():
        candidate = directory / f"{base}-{index}.md"
        index += 1
    return candidate


def with_obsidian_frontmatter(markdown: str, meta: Dict[str, Any]) -> str:
    source = str(meta.get("source") or "").replace("\n", " ")
    created = datetime.now().isoformat(timespec="seconds")
    frontmatter = [
        "---",
        "tags:",
        "  - media-transcribe",
        f"created: {created}",
        f"duration: {json.dumps(meta.get('duration') or '', ensure_ascii=False)}",
        f"source: {json.dumps(source, ensure_ascii=False)}",
        "---",
        "",
    ]
    return "\n".join(frontmatter) + markdown


def publish_local(title: str, markdown: str, output_dir: Optional[str], fallback_path: Path) -> Dict[str, Any]:
    if not output_dir:
        return {"backend": "local", "ok": True, "path": str(fallback_path)}
    target = unique_markdown_path(Path(output_dir).expanduser(), title)
    target.write_text(markdown, encoding="utf-8")
    return {"backend": "local", "ok": True, "path": str(target)}


def publish_obsidian(
    title: str,
    markdown: str,
    *,
    vault_path: Optional[str],
    vault_folder: Optional[str],
    meta: Dict[str, Any],
) -> Dict[str, Any]:
    raw_vault = vault_path or os.getenv("OBSIDIAN_VAULT")
    if not raw_vault:
        die("Obsidian backend requires --vault-path or OBSIDIAN_VAULT.")
    vault = Path(raw_vault).expanduser()
    if not vault.exists() or not vault.is_dir():
        die(f"Obsidian vault path does not exist or is not a directory: {vault}")
    folder = (vault / vault_folder).resolve() if vault_folder else vault
    if vault.resolve() not in [folder, *folder.parents]:
        die("Obsidian destination must stay inside the vault.")
    target = unique_markdown_path(folder, title)
    target.write_text(with_obsidian_frontmatter(markdown, meta), encoding="utf-8")
    return {"backend": "obsidian", "ok": True, "path": str(target)}


def publish_youdao(title: str, markdown: str, folder_id: str, payload_path: Path) -> Dict[str, Any]:
    payload = {
        "title": title,
        "content": markdown,
        "parentId": folder_id,
    }
    payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    try:
        run(
            [
                "youdaonote",
                "call",
                "createNote",
                "--args",
                json.dumps(payload, ensure_ascii=False),
            ],
            capture=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        die(f"Youdao write failed: {detail}")
    return {"backend": "youdao", "ok": True, "external_id": None, "payload_path": str(payload_path)}


def publish_note(title: str, markdown: str, args: argparse.Namespace, job_dir: Path, meta: Dict[str, Any]) -> Dict[str, Any]:
    if args.note_backend == "none":
        return {"backend": "none", "ok": True, "path": str(job_dir / "note.md")}
    if args.note_backend == "local":
        return publish_local(title, markdown, args.output_dir, job_dir / "note.md")
    if args.note_backend == "obsidian":
        return publish_obsidian(
            title,
            markdown,
            vault_path=args.vault_path,
            vault_folder=args.vault_folder,
            meta=meta,
        )
    if args.note_backend == "youdao":
        folder_id = args.destination or args.folder_id
        if not folder_id:
            die("Youdao backend requires --destination or --folder-id with a parent folder ID.")
        return publish_youdao(title, markdown, folder_id, job_dir / "youdao_payload.json")
    die(f"Unsupported note backend: {args.note_backend}")


def validate_publish_target(args: argparse.Namespace) -> None:
    if args.note_backend == "obsidian":
        raw_vault = args.vault_path or os.getenv("OBSIDIAN_VAULT")
        if not raw_vault:
            die("Obsidian backend requires --vault-path or OBSIDIAN_VAULT.")
        vault = Path(raw_vault).expanduser()
        if not vault.exists() or not vault.is_dir():
            die(f"Obsidian vault path does not exist or is not a directory: {vault}")
    if args.note_backend == "youdao" and not (args.destination or args.folder_id):
        die("Youdao backend requires --destination or --folder-id with a parent folder ID.")


def load_cache(job_dir: Path) -> Dict[str, Optional[str]]:
    return {
        "transcript": (job_dir / "transcript.txt").read_text(encoding="utf-8")
        if (job_dir / "transcript.txt").exists()
        else None,
        "segments": (job_dir / "segments.json").read_text(encoding="utf-8")
        if (job_dir / "segments.json").exists()
        else None,
        "diarization": (job_dir / "diarization.json").read_text(encoding="utf-8")
        if (job_dir / "diarization.json").exists()
        else None,
        "note": (job_dir / "note.md").read_text(encoding="utf-8")
        if (job_dir / "note.md").exists()
        else None,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Local audio/video path or HTTP(S) URL")
    parser.add_argument("--backend", choices=sorted(BACKENDS), default="local-whisper-cpp")
    parser.add_argument("--title", help="Note title. Defaults to media filename.")
    parser.add_argument(
        "--note-backend",
        choices=sorted(NOTE_BACKENDS),
        default="local",
        help="Where to publish the generated Markdown note. Default: local cache note.md",
    )
    parser.add_argument("--destination", help="Generic backend destination, such as a Youdao parent folder ID")
    parser.add_argument("--output-dir", help="Directory for --note-backend local")
    parser.add_argument("--vault-path", help="Obsidian vault path for --note-backend obsidian")
    parser.add_argument("--vault-folder", help="Folder inside the Obsidian vault")
    parser.add_argument("--folder-id", help=argparse.SUPPRESS)
    parser.add_argument("--cache-dir", default=str(default_cache_dir()), help="Cache directory")
    parser.add_argument("--model", default=DEFAULT_TRANSCRIBE_MODEL, help="OpenAI transcription model")
    parser.add_argument("--model-path", help="Local whisper.cpp GGML model path")
    parser.add_argument("--polish-model", default=DEFAULT_POLISH_MODEL, help=argparse.SUPPRESS)
    parser.add_argument("--language", help="Optional transcription language hint, e.g. zh")
    parser.add_argument("--prompt", help="Optional transcription prompt")
    parser.add_argument("--threads", type=int, default=max((os.cpu_count() or 4) - 2, 2))
    parser.add_argument("--segment-seconds", type=int, default=DEFAULT_SEGMENT_SECONDS)
    parser.add_argument(
        "--diarization-backend",
        choices=sorted(DIARIZATION_BACKENDS),
        default="none",
        help="Local speaker diarization backend",
    )
    parser.add_argument("--diarization-model", default=DEFAULT_DIARIZATION_MODEL, help="pyannote diarization model")
    parser.add_argument("--min-speakers", type=int, help="Minimum speaker count hint for diarization")
    parser.add_argument("--max-speakers", type=int, help="Maximum speaker count hint for diarization")
    parser.add_argument("--force", action="store_true", help="Ignore cached transcript/note")
    parser.add_argument("--no-polish", action="store_true", help="Skip model cleanup and create a fallback note")
    parser.add_argument("--skip-youdao", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--dry-run", action="store_true", help="Validate dependencies and media plan without transcription or publishing")
    return parser.parse_args()


def normalize_legacy_args(args: argparse.Namespace) -> argparse.Namespace:
    if args.skip_youdao:
        args.note_backend = "none"
    if args.folder_id and not args.destination and args.note_backend == "youdao":
        args.destination = args.folder_id
    return args


def main() -> None:
    args = normalize_legacy_args(parse_args())
    ensure_dependencies(note_backend=args.note_backend, backend=args.backend)
    validate_publish_target(args)
    if args.dry_run:
        if args.backend == "openai":
            ensure_openai_key(dry_run=True)
        elif not args.model_path and not DEFAULT_WHISPER_CPP_MODEL.exists():
            warn(
                "Default whisper.cpp model is missing; live local transcription needs "
                "--model-path, WHISPER_CPP_MODEL, or a model at ~/.cache/whisper-cpp/."
            )
    cache_root = Path(args.cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="media-transcribe-") as tmp:
        work_dir = Path(tmp)
        input_path = download_url(args.input, work_dir) if is_url(args.input) else Path(args.input).expanduser()
        if not input_path.exists():
            die(f"Input file not found: {input_path}")
        input_path = input_path.resolve()
        title = safe_title(args.title or input_path.stem)
        file_hash = sha256_file(input_path)
        job_dir = cache_root / file_hash
        job_dir.mkdir(parents=True, exist_ok=True)

        media_info = ffprobe(input_path)
        meta = {
            "title": title,
            "source": str(input_path),
            "sha256": file_hash,
            "duration_seconds": media_info["duration"],
            "duration": format_duration(media_info["duration"]),
            "source_bytes": media_info["size"],
            "note_backend": args.note_backend,
            "destination": args.destination,
            "backend": args.backend,
            "diarization_backend": args.diarization_backend,
            "codex_format_required": True,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }

        cached = load_cache(job_dir)
        has_cached_transcript = bool(cached["transcript"] and not args.force)
        has_cached_note = bool(cached["note"] and not args.force and not args.no_polish)
        needs_transcription = args.dry_run or not has_cached_transcript
        can_polish = False
        needs_polish = (
            not args.dry_run
            and not args.no_polish
            and not has_cached_note
            and can_polish
        )

        if not args.dry_run and args.backend == "openai" and (needs_transcription or needs_polish):
            ensure_openai_key()

        segments: List[Path] = []
        normalized: Optional[Path] = None
        if needs_transcription:
            normalize_channels = 2 if args.diarization_backend == "whisper-stereo" else 1
            normalized = normalize_media(input_path, work_dir, channels=normalize_channels)
            segments = segment_media(normalized, work_dir, args.segment_seconds)
            meta["normalized_bytes"] = normalized.stat().st_size
            meta["normalized_channels"] = normalize_channels
            meta["segments"] = [
                {"path": str(segment), "bytes": segment.stat().st_size}
                for segment in segments
            ]
        else:
            meta["cache_used"] = True
            meta["segments"] = []
        (job_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

        if args.dry_run:
            print(json.dumps({"ok": True, "job_dir": str(job_dir), **meta}, indent=2, ensure_ascii=False))
            return

        if has_cached_transcript:
            print("Using cached transcript.", file=sys.stderr)
            transcript = cached["transcript"]
            transcript_segments = json.loads(cached["segments"]) if cached["segments"] else []
        else:
            transcript_segments: List[Dict[str, Any]] = []
            if args.backend == "openai":
                transcript = transcribe_segments(
                    segments,
                    model=args.model,
                    language=args.language,
                    prompt=args.prompt,
                )
            else:
                transcript, transcript_segments = transcribe_segments_whisper_cpp(
                    segments,
                    model_path=args.model_path,
                    language=args.language,
                    threads=args.threads,
                    diarize=args.diarization_backend == "whisper-stereo",
                )
            if not transcript.strip():
                die("Transcription returned empty text")
            (job_dir / "transcript.txt").write_text(transcript, encoding="utf-8")
            (job_dir / "segments.json").write_text(
                json.dumps(transcript_segments, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        diarization_segments: List[Dict[str, Any]] = []
        if cached["diarization"] and not args.force:
            diarization_segments = json.loads(cached["diarization"])
        elif args.diarization_backend == "pyannote":
            if normalized is None:
                normalized = normalize_media(input_path, work_dir, channels=1)
            diarization_segments = run_pyannote_diarization(
                normalized,
                model_name=args.diarization_model,
                min_speakers=args.min_speakers,
                max_speakers=args.max_speakers,
                rttm_path=job_dir / "diarization.rttm",
            )
            (job_dir / "diarization.json").write_text(
                json.dumps(diarization_segments, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        elif args.diarization_backend == "local-cluster":
            if normalized is None:
                normalized = normalize_media(input_path, work_dir, channels=1)
            diarization_segments = run_local_cluster_diarization(
                normalized,
                transcript_segments,
                work_dir=work_dir,
                min_speakers=args.min_speakers,
                max_speakers=args.max_speakers,
            )
            (job_dir / "diarization.json").write_text(
                json.dumps(diarization_segments, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        elif args.diarization_backend == "whisper-stereo":
            diarization_segments = [
                {"start": item["start"], "end": item["end"], "speaker": item["speaker"]}
                for item in transcript_segments
                if item.get("speaker")
            ]
            (job_dir / "diarization.json").write_text(
                json.dumps(diarization_segments, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        assigned_segments = assign_speakers(transcript_segments, diarization_segments)
        speaker_text = speaker_transcript_from_segments(assigned_segments, transcript)
        (job_dir / "speaker_transcript.txt").write_text(speaker_text, encoding="utf-8")

        if cached["note"] and not args.force and not args.no_polish:
            print("Using cached Markdown note.", file=sys.stderr)
            note = cached["note"]
        elif args.no_polish or not can_polish:
            if not args.no_polish and not can_polish:
                warn("Writing Codex-ready Markdown; core ideas and quotes should be filled by Codex.")
            note = fallback_note(title, transcript, media_info, cleaned_text=speaker_text)
            (job_dir / "note.md").write_text(note, encoding="utf-8")
        else:
            note = polish_note(title, transcript, media_info, args.polish_model)
            (job_dir / "note.md").write_text(note, encoding="utf-8")

        publish_result = publish_note(title, note, args, job_dir, meta)

        print(
            json.dumps(
                {
                    "ok": True,
                    "title": title,
                    "duration": format_duration(media_info["duration"]),
                    "backend": args.backend,
                    "diarization_backend": args.diarization_backend,
                    "note_backend": args.note_backend,
                    "speaker_segments": len(diarization_segments),
                    "codex_format_required": True,
                    "job_dir": str(job_dir),
                    "note_path": str(job_dir / "note.md"),
                    "publish_result": publish_result,
                },
                indent=2,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
