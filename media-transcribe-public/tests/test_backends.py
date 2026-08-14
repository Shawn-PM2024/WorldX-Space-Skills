import argparse
from pathlib import Path
import subprocess

from media_transcribe_public import cli


def test_publish_local_uses_cache_when_no_output_dir(tmp_path: Path) -> None:
    note_path = tmp_path / "note.md"
    note_path.write_text("# Test\n", encoding="utf-8")

    result = cli.publish_local("Test", "# Test\n", None, note_path)

    assert result == {"backend": "local", "ok": True, "path": str(note_path)}


def test_publish_local_writes_unique_markdown(tmp_path: Path) -> None:
    existing = tmp_path / "Episode.md"
    existing.write_text("old", encoding="utf-8")

    result = cli.publish_local("Episode", "# Episode\n", str(tmp_path), tmp_path / "cache.md")

    assert result["backend"] == "local"
    assert result["ok"] is True
    assert Path(result["path"]).name == "Episode-2.md"
    assert Path(result["path"]).read_text(encoding="utf-8") == "# Episode\n"


def test_publish_obsidian_stays_inside_vault(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()

    result = cli.publish_obsidian(
        "Interview",
        "# Interview\n",
        vault_path=str(vault),
        vault_folder="Transcripts",
        meta={"duration": "1分钟", "source": "input.mp3"},
    )

    output = Path(result["path"])
    assert output.parent == vault / "Transcripts"
    text = output.read_text(encoding="utf-8")
    assert text.startswith("---\ntags:\n  - media-transcribe\n")
    assert "# Interview" in text


def test_legacy_skip_youdao_maps_to_none() -> None:
    args = argparse.Namespace(skip_youdao=True, note_backend="local", folder_id=None, destination=None)

    normalized = cli.normalize_legacy_args(args)

    assert normalized.note_backend == "none"


def test_legacy_folder_id_maps_to_youdao_destination() -> None:
    args = argparse.Namespace(
        skip_youdao=False,
        note_backend="youdao",
        folder_id="folder-123",
        destination=None,
    )

    normalized = cli.normalize_legacy_args(args)

    assert normalized.destination == "folder-123"


def test_default_cache_dir_respects_environment(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MEDIA_TRANSCRIBE_CACHE_DIR", str(tmp_path / "cache"))

    assert cli.default_cache_dir() == tmp_path / "cache"


def test_local_diarization_model_paths_are_configurable(monkeypatch, tmp_path: Path) -> None:
    segmentation = tmp_path / "segmentation.onnx"
    embedding = tmp_path / "embedding.onnx"
    monkeypatch.setenv("MEDIA_TRANSCRIBE_SEGMENTATION_MODEL", str(segmentation))
    monkeypatch.setenv("MEDIA_TRANSCRIBE_EMBEDDING_MODEL", str(embedding))

    assert cli.resolve_local_diarization_models() == (segmentation, embedding)


def test_resolve_transcribe_jobs_parallelizes_only_long_segmented_media() -> None:
    assert cli.resolve_transcribe_jobs("auto", segment_count=4, duration_seconds=7200, cpu_count=12) == 3
    assert cli.resolve_transcribe_jobs("auto", segment_count=4, duration_seconds=1200, cpu_count=12) == 1
    assert cli.resolve_transcribe_jobs("2", segment_count=4, duration_seconds=1200, cpu_count=12) == 2


def test_detects_whisper_metal_crash() -> None:
    crashed = subprocess.CalledProcessError(139, ["whisper-cli"], stderr="ggml_backend_metal failed")

    assert cli.is_whisper_gpu_failure(crashed) is True


def test_smooths_short_speaker_spike_between_same_speaker() -> None:
    diarization = [
        {"start": 0.0, "end": 5.0, "speaker": "speaker_0"},
        {"start": 5.0, "end": 5.35, "speaker": "speaker_1"},
        {"start": 5.35, "end": 10.0, "speaker": "speaker_0"},
    ]

    assert cli.smooth_diarization_segments(diarization) == [
        {"start": 0.0, "end": 10.0, "speaker": "speaker_0"}
    ]


def test_preserves_short_interjection_between_different_speakers() -> None:
    diarization = [
        {"start": 0.0, "end": 5.0, "speaker": "speaker_0"},
        {"start": 5.0, "end": 5.35, "speaker": "speaker_1"},
        {"start": 5.35, "end": 10.0, "speaker": "speaker_2"},
    ]

    assert cli.smooth_diarization_segments(diarization) == diarization


def test_local_cluster_cache_requires_current_engine_version() -> None:
    old_meta = {"diarization_backend": "local-cluster"}
    current_meta = {
        "diarization_backend": "local-cluster",
        "diarization_engine_version": cli.LOCAL_CLUSTER_ENGINE_VERSION,
    }

    assert cli.diarization_cache_is_compatible(old_meta, "local-cluster") is False
    assert cli.diarization_cache_is_compatible(current_meta, "local-cluster") is True


def test_reports_speaker_turn_fragmentation_rate() -> None:
    assigned = [
        {"start": 0.0, "end": 10.0, "speaker": "说话人A"},
        {"start": 10.0, "end": 20.0, "speaker": "说话人A"},
        {"start": 20.0, "end": 30.0, "speaker": "说话人B"},
        {"start": 30.0, "end": 40.0, "speaker": "说话人B"},
        {"start": 40.0, "end": 60.0, "speaker": "说话人A"},
    ]

    assert cli.speaker_turn_diagnostics(assigned, 60.0) == {
        "speaker_turns": 3,
        "speaker_count": 2,
        "speaker_turns_per_minute": 3.0,
    }
